# AGENTS.md

Each top-level directory with a `SKILL.md` is one Claude Code skill; the [README](README.md)
table is the catalog. There is no build. The working tree is meant to be symlinked into
`~/.claude/skills/`, so an edit here is an edit to the live skill.

## Golden path

```sh
python3 install.py                                        # symlink skills, enable hooks
git diff --cached | python3 scripts/disclosure.py check   # what pre-commit runs
```

Commits and pushes are gated; see README "Editing on a machine that pushes here". The gates
fail closed, and the denylist they read lives outside the repo.

## Rules for changing a skill

- Keep every lesson generic. Real numbers and dates are welcome; private project names, people,
  hosts and ids from other repositories are not. Worked examples that cite another repo's
  internals belong in a private companion skill on your machine, not here.
- Skills reference each other by directory name; keep names stable.
- Scripts and hooks are Python 3, stdlib only.

### Skill entry points

Read the `SKILL.md` of the skill you are working on. Where a skill has a `references/`
directory, its `SKILL.md` ends with a table saying which file to read for which task.

### Disclosure gates

`scripts/disclosure.py` is both gates; read it before changing what the hooks check, and update
the README gate section in the same commit.
