# skills

Agent skills for [Claude Code](https://claude.com/claude-code), written from real programs and
kept generic enough to use anywhere.

| Skill | What it does |
|---|---|
| [`phased-program`](phased-program/SKILL.md) | Run a large build as gated phases: spec first, workers in isolated worktrees, adversarial verification, a human who rules and pushes. Scales down to a single-session change. |
| [`adversarial-review`](adversarial-review/SKILL.md) | A fresh-context reviewer charged to break the work, then triage with judgment: fix what is plainly wrong, escalate what is a real decision. |
| [`numbered-rec-alts`](numbered-rec-alts/SKILL.md) | Present decisions as a numbered list, each with a recommendation and a tangible alternative. |

`phased-program` calls the other two, so install all three.

## Install

```sh
git clone https://github.com/aarontimko/skills.git
cd skills && python3 install.py
```

`install.py` symlinks each skill into `~/.claude/skills/`, so the clone is the only copy:
`git pull` updates the skills, and an edit made while using a skill is already a change in
this working tree. To just try one, copy its directory into `~/.claude/skills/` instead.

## Editing on a machine that pushes here

Because the live skill directory is a public repository, anything written into a skill can
ship. `install.py` turns on two gates:

- **pre-commit**, deterministic: the staged diff is checked against a private denylist
  (`~/.config/oss-publish/denylist.txt`, one term per line, never committed) plus built-in
  patterns for real email addresses, home paths and credentials. No denylist, no commit.
- **pre-push**, deterministic then probabilistic: the full outgoing log (patches, commit
  messages, author headers) goes through the same check, then a tool-less `claude -p` reads it
  as a stranger trying to learn who wrote it and where they work. It must answer
  `VERDICT: PASS`. It fails closed; `SKIP_LLM_REVIEW=1 git push` is the loud override.

Each machine keeps its own denylist. On a work machine it carries the employer's name,
internal project names and hostnames, which is what stops a lesson learned at work from
arriving here with the project's name still on it.

## License

Apache-2.0.
