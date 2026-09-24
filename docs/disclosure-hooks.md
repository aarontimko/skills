# Disclosure hooks: how a live skills directory stays safe to publish

An agent that learns from its work writes lessons into its skills. When the skills directory
is also a public repository, every lesson is one `git push` from the internet, and a lesson
learned on a private project tends to carry that project's names with it. Asking the agent to
be careful is not a control. These hooks are.

## The design in one paragraph

Two checks of different kinds, and each fails closed. A deterministic check matches every
added line against a private denylist and a set of built-in patterns. It is fast, exact and
blind to meaning. A probabilistic check hands the whole outgoing log to a tool-less
`claude -p` that reads it as a stranger trying to learn who wrote it and where they work. It
catches what no list names, such as a lesson that describes a private product without naming
it. Neither one alone is enough, so a push must pass both.

## Setup

The README's install section turns the hooks on with `git config core.hooksPath .githooks`
and shows how to create the denylist at `~/.config/oss-publish/denylist.txt`. `OSS_DENYLIST`
points the check at another file, and a gitignored `z_ignore/oss-denylist.txt` adds terms for
one repository.

## Where each check runs

| Hook | Input | Deterministic | Stranger review |
|---|---|---|---|
| pre-commit | added lines of the staged diff | yes | no |
| commit-msg | the commit message | yes | no |
| pre-push | full log of commits not yet on that remote, with patches, headers and merge diffs; annotated tag objects | yes | yes |

The review runs only at push time because it is slow and costs a model call. Commits stay
cheap, and nothing leaves the machine without it.

## Failing closed

Every path that is not an explicit pass is a failure:

- No denylist file, or an empty one, blocks every check. An empty list would pass everything.
- Empty input blocks. A bug that feeds the check nothing must not read as clean.
- The review passes only when its last line is exactly `VERDICT: PASS` and it is the only
  verdict line, so quoted text in the diff cannot supply one. A timeout, a missing `claude`
  CLI or a non-zero exit blocks.
- Binary files block, because neither check can read them. `ALLOW_BINARY=1` overrides after
  you look yourself.
- `SKIP_LLM_REVIEW=1` skips only the review, and says so loudly.

## Evasions it is built to catch

- **Look-alike and invisible characters.** Text is NFKC-normalized and format characters
  such as zero-width spaces and soft hyphens are stripped before matching. A word that mixes
  scripts, such as Latin with one Cyrillic letter, is flagged on its own.
- **A term split across a line wrap.** Lines are also matched joined together.
- **Text that only a merge introduces, or that only a tag carries.** Pre-push reads merge
  diffs and annotated tag objects, which a plain log skips.
- **Exemption spoofing.** The one deliberate name in the repository, the copyright line in
  `NOTICE`, is exempt only when the diff header is exactly the root `NOTICE` and the line ends
  at the name. Author, committer and tagger headers in the log are the only other exemption.
  Commit messages get no exemptions, so a pasted fake diff cannot claim one.

Removed lines are never checked: deleting a leak must not be blocked.

## What it cannot do

- It cannot take anything back. Once pushed, text is public. The checks are only useful
  before the push.
- The denylist only knows what you put in it. Keep one per machine; on a work machine it
  holds the employer's and internal project names.
- The review is a model reading text. It is a second pair of eyes, not proof.
- `git commit --no-verify` and `git push --no-verify` skip every hook. The hooks guard
  against accidents and an agent's habits, not against someone who means to leak.

## Reading the code

Everything is Python standard library: `scripts/disclosure.py` holds both checks and the
review's instructions, and `.githooks/` holds three thin callers. The tests in `tests/` plant
the character, line-wrap and exemption evasions above and confirm each is blocked. The merge
and tag paths are covered by the pre-push hook's code, not by a test.
