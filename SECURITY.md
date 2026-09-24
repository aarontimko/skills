# Security policy

## Supported versions

There are no releases. `main` is the only supported version; a fix lands there.

## Reporting a vulnerability

Use GitHub private vulnerability reporting on this repository: the **Security** tab, then
the **Report a vulnerability** button. That opens a private advisory only the maintainer
can see.

Do not open a public issue or a discussion for a security problem. A public report is a
disclosure.

If private reporting is unavailable to you, open an issue titled
"security contact request" with no other content. The maintainer will open a private
advisory and invite you to it.

## What to include

- What the problem is, in one or two sentences.
- The commit SHA you were using.
- Your OS and Python version.
- Steps to reproduce, or a proof of concept.
- What an attacker gets out of it, and what they need first.

## Response

- Acknowledgement within 7 days.
- For a confirmed report, a fix or a decision not to fix within 30 days of the
  acknowledgement.
- You are credited in the advisory unless you ask not to be.

## Threat model

What the repository runs, so you can judge whether something is in scope:

- **The skills** are Markdown instructions an agent reads. They run nothing by themselves;
  what an agent does with them happens under that agent's own permissions.
- **The git hooks** (`.githooks/`, enabled only by `git config core.hooksPath .githooks`)
  run `scripts/disclosure.py` with Python's standard library. They read the staged diff or
  the outgoing log, the commit message, and the denylist files named in the README. They
  make no repository changes (Python may write a `__pycache__` folder).
- **The pre-push hook reaches the network** by running the `claude` CLI, which sends the
  outgoing log to Anthropic's API under your own Claude login. `SKIP_LLM_REVIEW=1` turns
  that call off for one push. Nothing else here makes a network call.

A way to get a leak past the checks without the documented overrides (`SKIP_LLM_REVIEW`,
`ALLOW_BINARY`, `git commit --no-verify`) is in scope. Out of scope: anything that needs an
attacker to already have arbitrary code execution as your user, and the behavior of the
agents that read the skills.
