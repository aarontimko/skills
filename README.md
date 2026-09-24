# skills

Agent skills for running AI-built software with the rigor of a real engineering program:
phased checkpoints, adversarial review, and decisions presented as recommendations with
alternatives. These are the skills I use day to day for AI-native coding, published as I
work, so I can point people at what has held up.

## Who it is for

- You build software with a coding agent and want the agent to plan, review and escalate
  the way a careful engineer would, not just type faster.
- You want to read how someone else structures long agent-driven builds, and copy the
  parts that fit.
- You use Claude Code, Codex, Cursor, or another agent that reads `SKILL.md` files.

## Who it is not for

- You want a maintained framework with a roadmap and a support promise. This is one
  person's working set, and a skill here can be replaced when I find a better approach.
- You want to contribute skills. Fork it instead; see below.

## What it does

| Skill | What it does |
|---|---|
| [`phased-program`](skills/phased-program/SKILL.md) | Run a large build as gated phases: spec first, workers in isolated worktrees, adversarial verification, a human who rules and pushes. Scales down to a single-session change. |
| [`adversarial-review`](skills/adversarial-review/SKILL.md) | A fresh-context reviewer charged to break the work, then triage with judgment: fix what is plainly wrong, escalate what is a real decision. |
| [`numbered-rec-alts`](skills/numbered-rec-alts/SKILL.md) | Present decisions as a numbered list, each with a recommendation and a tangible alternative. |

Some skills call others by name (`phased-program` uses `adversarial-review` and
`numbered-rec-alts`), so install the whole set.

## Install

**Claude Code, as a plugin** (skills are invoked as `/skills:<name>`, and trigger on their
own when a task matches):

```
/plugin marketplace add aarontimko/skills
/plugin install skills@aarontimko
```

**Codex, Cursor and other agents** that read `SKILL.md`, via the
[skills CLI](https://github.com/vercel-labs/skills):

```sh
npx skills add aarontimko/skills
```

**To adapt your own copy**, fork the repository and clone the fork straight into your
Claude Code skills directory. It loads in place as a skills-directory plugin, so the
working tree is the live skill: an edit made while using a skill is already a change you
can commit.

```sh
git clone https://github.com/<you>/skills.git ~/.claude/skills/skills
git -C ~/.claude/skills/skills config core.hooksPath .githooks
```

## Keeping a live, public skills directory clean

When the directory your agent writes lessons into is a public repository, anything written
into a skill can ship. The `core.hooksPath` line above turns on three checks:

- **pre-commit** and **commit-msg**, deterministic: the added lines of the staged diff, then
  the commit message, are checked against a private denylist
  (`~/.config/oss-publish/denylist.txt`, one term per line, never committed; a gitignored
  `z_ignore/oss-denylist.txt` adds repository-local terms) plus built-in patterns for real
  email addresses, home paths and credentials. No denylist, no commit.
- **pre-push**, deterministic then probabilistic: the full outgoing log (patches, commit
  messages, author headers, tag messages) goes through the same check, then a tool-less
  `claude -p` reads it as a stranger trying to learn who wrote it and where they work. It
  must answer `VERDICT: PASS`. It fails closed; `SKIP_LLM_REVIEW=1 git push` is the
  deliberate override.

If you fork this, create your own denylist before your first commit:

```bash
mkdir -p ~/.config/oss-publish
printf '%s\n' 'your surname' 'your employer' > ~/.config/oss-publish/denylist.txt
```

The pre-push review needs the `claude` CLI. Without it, push with `SKIP_LLM_REVIEW=1` and read
the outgoing log yourself.

Keep one denylist per machine. On a work machine it carries the employer's name, internal
project names and hostnames, which is what stops a lesson learned at work from arriving in
public with the project's name still on it. The tests for these checks run with
`python3 -m unittest discover -s tests`.

## Status

This is a living set, not a versioned product. There are no releases: `main` is the
current version, and a plugin install follows it. When a skill is replaced or retired,
`CHANGELOG.md` says what replaced it and why, and the git history keeps the old text.

## Contributing, security, issues

This is personal publishing, so pull requests are not accepted. Fork it and make it yours;
that is what the Apache-2.0 license is for. Bug reports about the scripts and hooks, and
feedback on the skills, are welcome as issues. Security problems go through private
reporting, never a public issue: see [SECURITY.md](SECURITY.md). More in
[CONTRIBUTING.md](CONTRIBUTING.md).

## License

Apache-2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE); a redistributed copy keeps the
NOTICE file.
