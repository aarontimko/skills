# AGENTS.md

Each `skills/<name>/SKILL.md` is one skill; the [README](README.md) table is the catalog.
`.claude-plugin/` makes the repo both a Claude Code plugin and its own marketplace. There is no
build. Cloned into `~/.claude/skills/`, the repo loads in place, so an edit here is an edit to
the live skill.

## Golden path

```sh
git config core.hooksPath .githooks                       # enable the disclosure checks
python3 -m unittest discover -s tests                     # what CI runs
claude plugin validate .                                  # manifest check
git diff --cached | python3 scripts/disclosure.py check   # what pre-commit runs
```

Commits and pushes are checked; see README "Keeping a live, public skills directory clean".
The checks fail closed, and the denylist they read lives outside the repo. Changes reach
`main` through a squash-merged pull request from the maintainer.

## Rules for changing a skill

- Keep every lesson generic. Real numbers and dates are welcome; private project names, people,
  hosts and ids from other repositories are not. Worked examples that cite another repo's
  internals belong in a private companion skill on your machine, not here.
- Skills reference each other by directory name; keep names stable. A new skill is a new
  `skills/<name>/` directory plus a README table row; the manifests need no change.
- Replacing or retiring a skill: delete its directory, remove its README row, and add a
  dated `CHANGELOG.md` entry saying what replaced it and why.
- The maintainer's name appears only in `NOTICE`'s copyright line; the checks exempt
  exactly that line.
- Scripts and hooks are Python 3, stdlib only.

### Skill entry points

Read the `SKILL.md` of the skill you are working on. Where a skill has a `references/`
directory, its `SKILL.md` ends with a table saying which file to read for which task.

### Disclosure checks

`scripts/disclosure.py` holds both checks and `tests/test_disclosure.py` pins their behavior;
change them together, and update the README section and `docs/disclosure-hooks.md` (the
design, the evasions and the limits; read it before changing a check) in the same commit.
