#!/usr/bin/env python3
"""Make this clone the single source of truth: symlink each skill into ~/.claude/skills and turn
on the disclosure hooks. Re-runnable. An existing real directory is moved aside, never deleted."""
import os
import subprocess
import sys
import time
from pathlib import Path

repo = Path(__file__).resolve().parent
dest = Path(os.environ.get("CLAUDE_SKILLS_DIR", Path.home() / ".claude/skills"))
dest.mkdir(parents=True, exist_ok=True)
if dest.resolve() == repo or repo in dest.resolve().parents:
    sys.exit(f"{dest} is inside this clone; linking would move the skills out of the repo. Nothing done.")

for skill_md in sorted(repo.glob("*/SKILL.md")):
    source = skill_md.parent
    target = dest / source.name
    if target.is_symlink():
        target.unlink()
    elif target.exists():
        aside = dest.parent / f"skills-replaced-{time.strftime('%Y%m%d_%H%M%S')}-{os.getpid()}"
        aside.mkdir(exist_ok=True)
        target.rename(aside / source.name)
        print(f"moved existing {source.name} to {aside}/")
    target.symlink_to(source)
    print(f"linked {source.name}")

subprocess.check_call(["git", "-C", str(repo), "config", "core.hooksPath", ".githooks"])
print("hooks on (core.hooksPath=.githooks)")
denylist = Path(os.environ.get("OSS_DENYLIST", Path.home() / ".config/oss-publish/denylist.txt"))
if not denylist.is_file():
    print(f"WARNING: no denylist at {denylist}; commits will be refused until you create one (see README).")
