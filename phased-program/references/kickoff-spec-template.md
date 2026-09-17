# Kickoff Spec Template

One spec per phase, numbered and committed to the repo (e.g. `docs/<program>/9N-phaseN-kickoff-prompt.md`) on a fresh branch from main, **before the worker exists**. Header line: "operational artifact, not design" — the design lives in the corpus docs; the spec tells one worker exactly what to build and under what rules. A worker with a complete spec runs autonomously for hours; every omission becomes a stall or a wrong guess.

If a governing principle or recent human ruling shapes the phase, state it **at the top, in full** — the spine paragraph. Don't make the worker reconstruct intent from citations.

## Skeleton

```markdown
# Phase N Kickoff Prompt (operational artifact, not design)

[1–2 paragraphs: where this phase sits in the program, what prior phases
provide, what gate it closes. If a principle/ruling governs the phase,
summarize it here in full.]

---

## Mission
Build Phase N per [exact doc citations — roadmap section, design docs,
reference implementations the worker should study].

## Entry baseline (inherited obligations)
[If a prior gate was amended and handed this phase a named entry obligation:
restate the obligation and its exact baseline evidence (ledger lines, failing
case names, numbers) verbatim. This phase must beat those numbers.]

## Deliverables
1..K. Numbered, each self-contained: WHAT to build, the non-negotiable
properties (e.g. "zero direct writes, proven by grep + live tamper probe"),
and WHY when the reason constrains the design. Name the reference
implementation to imitate where one exists.

## [Phase-specific protocol sections as needed]
e.g. a Human Gate Protocol if the phase contains a mid-phase human decision
(see human-gate-protocol.md), data-sourcing instructions, migration rules.

## Gate (the checklist that closes this phase)
- One bullet per deliverable with its EVIDENCE form (ledger lines, zero-diff
  tables, live probes — never "it works").
- Standing items: full test suite green (state the floor number), lint/hooks
  per commit, deterministic unit tier (external calls mocked in unit tests).
- A built-artifact pass: the deliverables work from the built container/
  package against a seeded environment, not just from the dev checkout.

## Operational rules
- Isolated stack: names, ports (from the ports ledger), volumes.
  What is SACRED and untouchable.
- LLM/API spend: expected $X / flag $Y / hard tripwire $Z (stop, commit
  clean, report). Estimate before every recorded batch — AND put the
  estimate in a commit message (a committed estimate is a receipt the
  actuals get judged against); iterate on mocks.
- Fixes discovered while gathering evidence are committed separately from
  the evidence-gathering work and labeled by discovery channel
  (found-by-soak, found-by-verifier) so the history attributes them.
- Frozen artifacts (list them with versions). Changing one = STOP,
  human-only. Additive-only migrations, written as if real data exists.
- Secrets: copy from the main checkout; never print/log/commit.
- Commit discipline: phase-shaped commits, no pushes, resumable from
  git alone. Stage explicitly (never `git add -A`).
- NEVER end your turn to wait for anything [except sanctioned checkpoints,
  if any] — no notification will come; poll bounded cycles in-turn.

## Working agreements
- Grounded progress claims — ledger and DB, not enthusiasm.
- Fresh-context verifier subagents after milestones (a), (b), (c) — name
  each verifier's target failure classes explicitly.
- Stop conditions: gate met, spend tripwire, frozen-artifact temptation,
  genuine human-only blocker → commit clean, document, stop.

## Final report
Self-assessment per gate item WITH EVIDENCE; open questions split
needs-a-ruling vs informational; total spend accounting.
```

## Notes

- **Gate ≠ deliverables list.** The gate states the *evidence* that will be accepted. Writing it forces you to decide, before the build, what proof looks like.
- **Name the traps.** If a prior phase hit a subtle trap (a shared config that serves two consumers, a column that triggers must cover), write it into the spec of any phase that goes near it.
- **Contract surfaces:** if a deliverable touches a frozen artifact's surface, spec it as an optional/additive no-op-when-absent change, documented in the report as a *proposed* version bump — the human ratifies versions, workers never edit the frozen doc.
- **Parallel workers:** if two workers run concurrently, each spec names the other's stack/ports/worktree as untouchable, and declares which shared append-only files (run ledgers) will conflict at merge — expected, handled at close-out, append normally. Two parallel workers may share one phase branch and one PR when their gates close together; commit both specs together.
- **Unsatisfiable gate clauses:** if a gate clause cannot be honestly satisfied by a worker run (wall-clock, human-scale usage), don't hide it — the spec proposes the split interpretation, flags it for the human's close-out ratification, and designs the build to be identical under either reading.
- **Split on data dependencies:** construction that doesn't consume an artifact runs in parallel with the run producing it; the consumer phase waits for its input to exist.
