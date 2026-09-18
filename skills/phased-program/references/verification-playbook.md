# Verification Playbook

Two layers: **your own spot-verification** (the orchestrator, before anything reaches the human) and **fresh-context verifier subagents** (adversarial, during the worker's build). Neither substitutes for the other.

## Layer 1 — Orchestrator spot-verification

Run before presenting any worker report to the human. The standard is *personally reproduced*, not *plausibly reported*:

- [ ] **Worktree state:** `git status` clean; `git log` shows phase-shaped commits; commit count and tip SHA match the report.
- [ ] **Test suite:** run it yourself in the worker's worktree. The number must match the report exactly.
- [ ] **Frozen artifacts:** `git diff main -- <each frozen file>` yourself. Zero-diff means zero-diff. For DB-level invariants (triggers, guard functions), dump from the live DB and diff — don't trust the migration files alone.
- [ ] **Ledger/evidence lines:** grep for every run-id the report cites; validate append-only files parse line-by-line (a tiny JSON round-trip script).
- [ ] **Live state claims:** if the report says "teardown done" — `docker ps`. If it says "row exists" — query it. If it says "volume preserved" — `docker volume ls`.
- [ ] **Key artifacts read in full:** the receipts file, the report's own evidence tables. You are looking for the claim that *almost* matches reality.

When a claim fails verification, that's a finding, not a catastrophe: fix or have the worker fix it, and record the class of error in the gotcha ledger.

## Layer 2 — Fresh-context verifier subagents

The verifier *method* — charter, failure classes, evidence standards, verdict, triage — lives in the sibling `adversarial-review` skill. Read it when designing a verifier; it is the single source of truth for how a verifier is built and how findings are triaged.

Program-specific rules on top of the method:

- **Spawned by the worker** (write it into the spec) at named milestones, so the worker budgets for verifiers instead of treating them as optional polish.
- **Triage routing inside a program:** workers never present to the human and never wait — a worker-spawned verifier's judgment calls go into the worker's report as needs-a-ruling items; the orchestrator presents them at the rulings step (numbered-rec-alts format) and returns verdicts to the worker.
- **Standard milestones:** (a) after the riskiest new component (write-discipline, budgets); (b) after anything touching cross-cutting invariants (triggers, migrations, shared state); (c) before the final report (receipts complete and *reproducible* — can a stranger re-run the scoring?).

## Grounded-claims standard (applies to everyone)

A progress claim is grounded when it names its evidence: a ledger line, a DB row, a git SHA, a test count, a diff table. "Consolidation works now" is not a claim; "16 consolidations, all human-gated drafts, 15 approved 1 rejected-respected, decision rows append-only (tamper-probed)" is. Enforce this in worker prompts, verifier charters, your own reports to the human, and PR bodies.

## Score-hygiene rules learned the hard way

- **Correct summaries against primary sources.** A dataset note claimed a text casualty that volume-recovered originals disproved. When a ruling depends on what a text said — read the text.
- **Metrics can be right for the wrong reason.** A verdict-match rate that *rises* can mean the system got worse (agreeable) — decide per metric whether it's a target or telemetry, and say so in the spec.
- **Expected values in eval datasets need class labels** (e.g. hard/soft, or domain-meaningful verdict classes) and, where honest, `acceptable_verdicts` sets — binary expectations force false regressions on judgment calls.

## Protect the measuring stick (circle-backs)

Datasets and contracts are foundations under load: schedule **circle-backs** in the roadmap where each is formally re-analyzed against everything learned since — not continuously, not never. A circle-back is the *only* sanctioned path to editing golden ground truth:

- Every change justified in writing, committed separately from implementation or scoring-rule changes.
- Never made to flatter a config — reject flattering alternatives on the record.
- "Zero changes needed" is a legitimate outcome, but it must be argued and recorded, not skipped.

## Measure before you target

- **Before/after baseline pairs:** any phase that restructures state under a frozen behavior contract is gated on baselines recorded on identical data — PRE on the old code/schema, migrate, POST on the new. Decide in advance what "unchanged" means (bit-identical deterministic spine; symmetric noise on judged layers — a real bug depresses scores *systematically*, noise scatters symmetrically).
- **Targets after baselines:** set numeric gate targets only after the entry baseline is measured — numbers chosen in ignorance are theater.
- **Null arms first:** measure the do-nothing/gate-only arm before the full system, so every component's contribution is attributed rather than assumed.

## Verifying stochastic and time-shaped claims

- When the system under test has probabilistic components, **run the identical configuration at least twice and diff at decision grain** — variance is the property a single run silently assumes away. Name the flutter cases and judge their *direction*: conservative flutter can be acceptable where liberal flutter is not.
- When a gate contains a **wall-clock clause**, ask what the elapsed time is supposed to evidence. If the inputs are synthetic anyway, redesign it as **named-hypothesis scenarios expressed as pure configs** — a reviewer diffs two scenarios by diffing two config files; have a verifier grep the driver for scenario-name conditionals (the anti-pattern is behavior hiding in the harness). Parameterize the horizon so a year-scale run is the same config with different numbers.
