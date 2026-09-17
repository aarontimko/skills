# AGENTS.md

Three Claude Code skills, published as a plain directory tree: each top-level directory with a
`SKILL.md` is one skill. There is no build. The working tree is meant to be symlinked into
`~/.claude/skills/`, so an edit here is an edit to the live skill.

## Golden path

```sh
python3 install.py                     # symlink skills into ~/.claude/skills, enable hooks
git diff --cached | python3 scripts/disclosure.py check    # what pre-commit runs
git log -p -m origin/main.. | python3 scripts/disclosure.py review   # what pre-push adds
```

Commits run the deterministic disclosure check; pushes add a `claude -p` stranger-review and
fail closed. `SKIP_LLM_REVIEW=1` is the deliberate override. The private denylist lives outside
the repo at `~/.config/oss-publish/denylist.txt` and is never committed.

## Rules for changing a skill

- Keep every lesson generic. Real numbers and dates are welcome; private project names, people,
  hosts, ids from other repositories are not. Worked examples that cite another repo's
  internals belong in a private companion skill on your machine, not here.
- `phased-program` calls `adversarial-review` and `numbered-rec-alts` by name; keep those names
  stable.
- Scripts and hooks are Python 3, stdlib only.

### Skill entry points

Read the `SKILL.md` of the skill you are working on; `phased-program/references/` holds its
per-task runbooks, indexed in a table at the bottom of `phased-program/SKILL.md`.

### Disclosure gates

`scripts/disclosure.py` is both gates; read it before changing what the hooks check. Change the
README section "Editing on a machine that pushes here" in the same commit.
