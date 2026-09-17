# Worker Prompt Template

The prompt is a **pointer to the spec**, not a copy of it. Structure: FIRST ACTIONS (a read-list) → CRITICAL BOUNDARIES → SEQUENCING → REPORTING. Launch with the Agent tool, `isolation: "worktree"`, `run_in_background: true`, `model: "opus"` (construction runs on Opus 5; reviewers and verifiers stay on Fable — see the model split under Roles in SKILL.md). One phase = one worker; parallel phases = separate workers launched in the same message.

```text
You are the Phase N worker for <program>. You work ONLY inside your assigned
worktree (a checkout at branch <phase-branch>, commit <sha>). Your entire
mission, deliverables, gate checklist, operational rules, and reporting
format are in ONE authoritative spec file. Follow it exactly.

FIRST ACTIONS (in order, before any code):
1. Read <path-to-spec> — this is your complete mission spec. Everything
   below is a boundary reminder, not a substitute.
2..k. Read <the design docs the spec cites; recent decision-log entries;
   the governing principle if one exists>.
k+1. Study the reference implementations: <named prior modules the new
   work should imitate>.
k+2. Copy .env / creds from the main checkout at <path>. NEVER print, log,
   or commit their contents.
k+3. <Toolchain setup: sync deps, install pre-commit hooks.> Run the test
   suite once to confirm your baseline is <N> green before you write anything.

CRITICAL BOUNDARIES (violations are unrecoverable):
- The shared/production stack is SACRED: <ports, container names, DB,
  users>. Never touch any of it. Your isolated stack: <names, ports,
  own new volume>. <Other live workers' stacks/worktrees, if any> are
  not yours — never touch them.
- Frozen artifacts — any change is a STOP/human-only blocker: <list with
  versions>. If your design needs one modified, your design is wrong.
- NO `git push`, ever. NO `git add -A` — stage files explicitly.
  Phase-shaped commits, resumable from git alone.
- Test/eval identities are <pattern, e.g. *@test.local> on your isolated
  stack only — never real user data.
- Spend: expected <$X>, flag if projected ><$Y>, hard tripwire <$Z>
  (stop, commit clean, report). Estimate before every recorded batch;
  iterate with mocks and single smoke runs first.
- NEVER end your turn to wait for anything — no notification will ever
  come; poll bounded cycles in-turn (container readiness, migrations,
  eval runs — all polled in-turn). [If the spec defines a sanctioned
  human-gate checkpoint, name it here as the ONE exception and describe
  the checkpoint-report shape.]

SEQUENCING (the spec has full detail):
1..n. The build order, one line each. Put protective fixes FIRST (anything
   that guards the rest of the build). Name where fresh-context verifier
   subagents run and what each one hunts.
Final: built-artifact pass, final verifier, teardown your stack (stop+rm
   containers; LEAVE the volume), final report.

REPORTING:
- Progress claims must be grounded: ledger lines, DB rows, test counts,
  git SHAs — not enthusiasm.
- Your final message per segment = the report. [Checkpoint-report shape
  if applicable.] Final report: gate self-assessment with evidence per
  item; open questions split needs-a-ruling vs informational; total
  spend accounting.
```

## Launch-time judgment

- **Baseline check belongs in FIRST ACTIONS.** A worker that starts from a red suite wastes its whole run attributing failures.
- **"Never stand by" needs teeth and history.** State that prior workers stalled this way if true — concrete precedent lands harder than an abstract rule.
- **Protective fixes first** in sequencing: if the phase includes a fix that makes failures louder (e.g. a budget-ceiling fix), build it before the code it protects.
- **Verifiers are named in the prompt** so the worker budgets for them instead of treating them as optional polish.
- **Stay inside the permission allowlist.** Routine invocations must use the pre-approved command shapes (test runner, task-runner targets — see environment-contract.md); an ad-hoc entry point blocks on an interactive prompt no one is watching.
- **Resuming:** the same agent can be resumed later via SendMessage with its agent id — used for both stall recovery and delivering human-gate verdicts. Write prompts assuming resumption is possible; require commits frequent enough that any stop is resumable from git alone.
