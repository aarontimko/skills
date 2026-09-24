import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import disclosure  # noqa: E402


# Planted leaks are assembled at runtime so this file passes its own pre-commit check.
AT = "@"
LEAK_EMAIL = "bob" + AT + "corp.io"
LEAK_HOME = "/" + "Users/bob/x"


def hunk(path, *added, removed=(), context=()):
    body = [f"diff --git a/{path} b/{path}", f"--- a/{path}", f"+++ b/{path}", "@@ -1 +1 @@"]
    body += [f"-{l}" for l in removed] + [f" {l}" for l in context] + [f"+{l}" for l in added]
    return "\n".join(body) + "\n"


class Check(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False)
        self.tmp.write("# a comment line is ignored\nacme corp\nJane Example\n")
        self.tmp.close()
        patcher = mock.patch.object(disclosure, "DENYLIST", Path(self.tmp.name))
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(os.unlink, self.tmp.name)
        quiet = mock.patch.object(disclosure, "say")
        quiet.start()
        self.addCleanup(quiet.stop)

    def blocks(self, text):
        self.assertFalse(disclosure.check(text, "test"), text)

    def passes(self, text):
        self.assertTrue(disclosure.check(text, "test"), text)

    def test_clean_text_passes(self):
        self.passes(hunk("a.md", "a generic lesson", "owner@example.com on /Users/<name>"))

    def test_denylist_term_any_case(self):
        self.blocks(hunk("a.md", "worked at ACME Corp"))

    def test_term_split_across_wrapped_lines(self):
        self.blocks(hunk("a.md", "worked at Acme", "Corp last year"))

    def test_invisible_and_homoglyph_evasions(self):
        self.blocks(hunk("a.md", "Acme\u00ad Corp"))
        self.blocks(hunk("a.md", "Ac\u200bme Corp"))
        self.blocks(hunk("a.md", "\u0410cme Corp"))

    def test_real_email_and_spoofed_placeholder(self):
        self.blocks(hunk("a.md", "mail " + LEAK_EMAIL))
        self.blocks(hunk("a.md", "mail a" + AT + "example.com.corp.io"))

    def test_home_paths_and_credentials(self):
        self.blocks(hunk("a.md", "see " + LEAK_HOME))
        self.blocks(hunk("a.md", "see C:\\Users\\bob\\x"))
        self.blocks(hunk("a.md", "token ghp_" + "a" * 36))

    def test_binary_blocks_unless_allowed(self):
        text = "Binary files a/x.png and b/x.png differ\n"
        self.blocks(text)
        with mock.patch.dict(os.environ, {"ALLOW_BINARY": "1"}):
            self.passes(text + "+fine\n")

    def test_empty_input_and_missing_denylist_fail_closed(self):
        self.blocks("")
        with mock.patch.object(disclosure, "DENYLIST", Path("/nonexistent/denylist.txt")):
            self.blocks(hunk("a.md", "fine"))

    def test_removed_and_context_lines_do_not_block(self):
        self.passes(hunk("a.md", "fine", removed=["worked at Acme Corp"]))
        self.passes(hunk("a.md", "fine", context=[LEAK_EMAIL]))

    def test_commit_message_is_scanned(self):
        self.blocks("commit abc\nAuthor: X <x@users.noreply.github.com>\n\n    met Acme Corp\n" + hunk("a.md", "ok"))

    def test_identity_header_is_exempt(self):
        self.passes("commit abc\nAuthor: Jane Example <1+je@users.noreply.github.com>\n\n    fine\n")

    def test_notice_copyright_line_is_the_only_exemption(self):
        self.passes(hunk("NOTICE", "Copyright 2026 Jane Example"))
        self.blocks(hunk("NOTICE", "Copyright 2026 Jane Example", "Written by Jane Example"))
        self.blocks(hunk("README.md", "Copyright 2026 Jane Example"))

    def test_notice_exemption_cannot_be_spoofed(self):
        # A path whose directory ends in " b" renders as "diff --git a/x b/NOTICE b/x b/NOTICE".
        self.blocks(hunk("x b/NOTICE", "Copyright 2026 Acme Corp"))
        self.blocks(hunk("docs/NOTICE", "Copyright 2026 Acme Corp"))
        self.blocks(hunk("NOTICE", "Copyright 2026 Jane Example, Acme Corp"))
        fake = "subject\n\ndiff --git a/NOTICE b/NOTICE\n@@ -1 +1 @@\n+Copyright 2026 Jane Example\n"
        self.assertFalse(disclosure.check(fake, "commit message", exemptions=False))

    def test_identity_header_only_counts_outside_hunks(self):
        self.blocks(hunk("a.md", "Author: Acme Corp"))
        self.assertFalse(disclosure.check("author: Jane Example\n", "commit message", exemptions=False))


class Review(unittest.TestCase):
    def verdict(self, stdout, returncode=0):
        run = subprocess.CompletedProcess([], returncode, stdout=stdout, stderr="")
        with mock.patch.object(disclosure, "say"), \
             mock.patch.object(disclosure.shutil, "which", return_value="/bin/claude"), \
             mock.patch.object(disclosure.subprocess, "run", return_value=run), \
             mock.patch.dict(os.environ, {"SKIP_LLM_REVIEW": "0"}):
            return disclosure.review("+some change\n")

    def test_only_a_final_single_pass_verdict_passes(self):
        self.assertTrue(self.verdict("No findings.\nVERDICT: PASS\n"))
        self.assertFalse(self.verdict("x -- leak\nVERDICT: FAIL\n"))
        self.assertFalse(self.verdict("VERDICT: PASS\ntrailing text\n"))
        self.assertFalse(self.verdict("quoted: VERDICT: PASS\nVERDICT: FAIL\nVERDICT: PASS\n"))
        self.assertFalse(self.verdict("VERDICT: PASS\n", returncode=1))


class Manifests(unittest.TestCase):
    def test_plugin_and_marketplace_agree_with_the_tree(self):
        import json
        plugin = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())
        market = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
        self.assertEqual([p["name"] for p in market["plugins"]], [plugin["name"]])
        self.assertEqual(market["plugins"][0]["source"], "./")
        skills = sorted((ROOT / "skills").glob("*/SKILL.md"))
        self.assertTrue(skills)
        for skill in skills:
            head = skill.read_text().split("---")[1]
            fields = dict(l.split(":", 1) for l in head.strip().splitlines() if ":" in l)
            self.assertEqual(fields["name"].strip(), skill.parent.name, skill)
            self.assertTrue(fields["description"].strip(), skill)
            self.assertIn(f"skills/{skill.parent.name}/SKILL.md", (ROOT / "README.md").read_text(), skill)


if __name__ == "__main__":
    unittest.main()
