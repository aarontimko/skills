---
name: phased-program
description: Orchestrate an autonomous build as gated phases - Claude as orchestrator, subagent workers in isolated worktrees/stacks, human gates with evidence. Use for multi-phase programs (platform/API/UI/CLI over days/weeks, one branch/PR per phase) AND for single-session mini-phases that keep the same rigor at smaller scale (spec, adversarial review, worker, human gate, one PR). Right-size the scale, never the rigor. Not for trivial edits that need no spec or review.
---

# Phased Program Orchestration

Run a large build as a sequence of gated phases: a versioned design corpus, one kickoff spec per phase, background workers in isolated worktrees with isolated runtime stacks, adversarial verification, and a human sponsor who rules on open questions, pushes branches, and merges PRs. Proven on a 9-phase platform build that ran across multiple compactions at roughly $0.20–$0.90 actual LLM spend for well-mocked construction phases and $4–8 for research/eval-heavy phases; later programs on the same platform have run $5–10 per phase as LLM-judged eval and live-model calibration became routine — calibrate spend expectations to the phase *type*, not one program-wide norm, and set the tripwire as a stop-loss above the expected number, not as a budget.

## Mini-phase mode (single-session programs)

The method scales DOWN. A well-scoped change (one feature, one contract bump, one prompt-ecology change) runs the full loop in a single session: spec → adversarial design review → human rulings → worker build → adversarial code review → orchestrator-applied fixes → one branch, one PR → deploy tail. What gets dropped is the program scaffolding (no roadmap doc, no per-phase G0, no separate handoff doc — long-term memory serves as the handoff), never the rigor: the spec still exists before the worker, the reviews still run adversarially, the human still rules and still pushes. If you're declining to use this skill because the task fits in one session, that's the wrong reason — decline only when the task needs no spec and no review at all.

## Program setup (day zero, before Phase 1)

- Commit the **design corpus** and a **roadmap doc containing every phase's gate checklist, written in advance**. Gates change only by deliberately editing that doc (see gate amendments in `references/human-gate-protocol.md`). Include a sequencing-rationale section and scheduled **circle-backs** (see verification-playbook).
- Close a **G0 gate**: the human reviews and version-stamps the frozen artifacts everything downstream will be written against, *before* datasets and specs are written against them.
- **Phase-0 safeguard rule:** if existing behavior actively violates a target invariant, rule on disabling it immediately rather than letting it do damage until its phase arrives — the cheapest migration is the one with the least lost data.
- Sequence so the **measurement instrument is Phase 1** — nothing judgment-bearing gets built before the thing that measures judgment, and the dataset outlives any implementation.
- **FIRM PRECONDITION — a dense, deterministic unit-test baseline before any autonomous work.** This is the substrate the whole method stands on: workers confirm the baseline green before writing a line, commit hooks run the fast tier on every commit, the orchestrator spot-verifies any claim with one command, and regressions surface at the commit that caused them instead of at phase close. If the target codebase doesn't have this, **building/densifying the suite IS the first phase** — do not launch autonomous workers onto a thin suite; without the floor, "autonomous worker" means unreviewed drift. The floor then ratchets (see quality floor in `references/environment-contract.md`).
- Set up the environment contract (`references/environment-contract.md`), including the permission allowlist workers will live inside.

## Roles

- **Orchestrator (you, the main session):** writes specs, launches and babysits workers, personally verifies claims, presents rulings to the human, executes verdicts, merges, writes docs, maintains the handoff doc and memory. Never builds a phase yourself; never lets a worker talk to the human directly. Carve-out proven in practice: post-review fixes that clear the `adversarial-review` skill's triage (genuinely wrong, north star untouched) are applied by the orchestrator directly in the worker's worktree as separate review-named conventional commits when small — relaunching a worker for a 3-file fix wastes more than it protects; a sprawling fix goes back to a worker. Who types the fix is economics; whether it may be fixed without a human ruling is the north-star test, and that lives in the adversarial-review skill.
- **Workers (background subagents, isolation: worktree):** build exactly one phase from one spec, in their own git worktree and their own runtime stack. Report with evidence, not enthusiasm.
- **Verifiers (fresh-context subagents):** adversarial, milestone-triggered, hunting named failure classes. They try to break the worker's claims, not confirm them.
- **Model split (preferred token balance, adopted 2026-09-02 on lastcall):** construction workers run on Opus 5 (`model: "opus"` on the Agent call) — a frozen spec, a dense test floor, the pre-commit hook, and a verifier behind them make the worker the most scaffolded role, so it needs the least judgment per token. Everything judgment-shaped stays on Fable 5.1: orchestrator, design and code reviewers, verifiers, triage, diagnosis. The instrument for whether the split holds is the verifier finding count per phase (lastcall Phase 4 baseline on Fable workers: 8 + 6 findings, none blocking); if Opus-built phases push that up or produce blockers, move construction back to Fable.
- **Human sponsor:** rules on open questions (presented with options/pros-cons/forward-impact), ratifies version bumps to frozen artifacts, pushes branches, merges PRs. The gates are load-bearing — design them in, don't route around them.

## The per-phase loop

1. **Spec first.** Write the complete kickoff spec (`references/kickoff-spec-template.md`) on a fresh branch from main and commit it before any worker exists. The spec is the authoritative interface; the worker prompt is a pointer to it. Split phases along *data* dependencies (a consumer phase waits for the artifact-producing run; independent construction runs in parallel); two parallel workers may share one phase branch and one PR when their gates close together. If the spec touches personal or work-sensitive data, it lives in a gitignored private directory (e.g. `z_ignore/`) with rulings recorded in its header; the *committed* record is a separate sanitized, dated design-provenance doc written at docs-commit time — counts, types, and ids in committed evidence, never the real content.
2. **Adversarially review the spec, then present rulings — BEFORE any worker exists.** Run the sibling `adversarial-review` skill in design-review mode against the spec — that skill owns the method and the rationale. Fold findings, present every open question to the human (options / pros-cons / forward impact / recommendation / door label), and freeze the rulings into the spec. Post-build rulings (step 6) then cover only what the build *surfaced*, not the design.
3. **Launch** the worker: Agent tool, `isolation: "worktree"`, `run_in_background: true`, prompt from `references/worker-prompt-template.md` (FIRST-ACTIONS read-list → CRITICAL BOUNDARIES → sequencing → reporting).
4. **Babysit.** Expect stalls and recover them (`references/recovery-playbook.md`). If the phase contains a genuine mid-phase human decision, design a **sanctioned checkpoint** into the spec so a clean stop is distinguishable from a stall (`references/human-gate-protocol.md`).
5. **Spot-verify personally** before anything reaches the human: run the suite yourself, diff frozen artifacts yourself, query the DB yourself (`references/verification-playbook.md`). Trust nothing you didn't verify.
6. **Present rulings** — every open question the *build* surfaced (design rulings were frozen in step 2), with options, pros/cons, forward impact, and a recommendation. Label each decision one-way or two-way door.
7. **Execute verdicts, merge** the worker branch into the phase branch, validate shared append-only files (ledgers) after merge.
8. **Docs commit:** decision-log entries for every ruling (verbatim, supersedable), gate-closed line in the roadmap, and the sanitized design-provenance doc if the spec is private (step 1).
9. **Human pushes** (see `references/environment-contract.md` — the push hook is deliberate). Hand them the exact command.
10. **PR** with a gate-evidence table (`references/close-out-checklist.md`). Human merges.
11. **Sync + cleanup + deploy tail:** pull main, remove worktrees, delete branches, re-run the suite on merged main, update the handoff doc and long-term memory. If a production/permanent stack consumes this repo, the phase is NOT closed at merge — run the deploy tail (close-out-checklist.md §Deploy tail): the production runbook's upgrade procedure, live verification, and any live config change the phase was for.

## Principles (each expanded in references/)

1. **The spec is the interface** — complete, versioned, committed; workers run autonomously against it for hours.
2. **Orchestrator holds the relationship; workers hold the keyboard** — your context is spent on cross-phase memory, verification, and the human, not on building.
3. **Trust nothing you didn't verify** — grounded claims (ledger lines, DB rows, SHAs, test counts) + personal spot-checks + adversarial verifiers.
4. **Human gates are load-bearing** — frozen artifacts only the human can version-bump; rulings presented with depth; decisions recorded verbatim and *supersedable* (a log that permits "I ruled too fast" beats one that treats rulings as final).
5. **Reason hard rulings from primary sources** — verbatim records and preserved evidence, not summaries of them. Preserve evidence volumes; never destroy provenance.
6. **Design the failure modes in advance** — never-stand-by rule, sanctioned checkpoints, stall-recovery recipe, a gotcha ledger where every mistake is written down once and never repeated.
7. **Cheap iterations, hard tripwires** — expected/flag/stop spend numbers per phase; mock everything until the recorded run.
8. **Survive your own context loss** — a living handoff doc updated at every state change; the repo remembers what was decided, the handoff remembers what's in flight, memory remembers how you work.
9. **Label your doors, ledger your deferrals** — two-way doors deferred cheaply with a paper trail; one-way doors get the full ruling treatment; deliberately-accepted risks go in a standing **deferral ledger** with named trigger conditions (human-gate-protocol.md).
10. **Gates fail honestly** — an unmet gate item is never waived or fudged; it becomes a deliberately-amended gate plus a **named entry obligation** of a later phase, with the exact evidence as the baseline that phase must beat.
11. **Measure before you target** — before/after baseline pairs on identical data for structural changes; numeric gate targets set only after the entry baseline exists; null arms measured first so contributions are attributed.

## Environment (opinionated defaults — see references/environment-contract.md)

Per-phase isolated docker stacks with a ports ledger, a sacred untouchable shared/production stack, volumes preserved as evidence, a hook that blocks agent-initiated `git push` so every branch crosses the network by human hand, and creds copied-never-committed. A program can opt out, but these defaults are what make long-running parallel workers and A/B stacks safe and cheap.

## References

| File | When to read |
|---|---|
| `references/kickoff-spec-template.md` | Writing a phase spec |
| `references/worker-prompt-template.md` | Launching a worker |
| `references/verification-playbook.md` | Spot-verifying; designing verifiers |
| `references/human-gate-protocol.md` | Presenting rulings; frozen artifacts; mid-phase gates |
| `references/recovery-playbook.md` | Worker stalls; compaction; evidence preservation; gotchas |
| `references/close-out-checklist.md` | Phase close-out through PR |
| `references/environment-contract.md` | Setting up stacks/ports/hooks on day one |
