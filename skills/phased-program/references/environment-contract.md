# Environment Contract (opinionated defaults)

These are deliberate, opinionated choices, not neutral options. They're what make long-running parallel workers, A/B stacks, and multi-day programs safe and cheap for any service-shaped project (API, UI, CLI backend). A program can opt out of a piece, but that should be a rarity with a stated reason. Set all of this up on day one and record it in the handoff doc.

## 1. The sacred shared stack

One long-running stack (local or deployed) is the *real* one — real data, real users, the thing the program eventually serves. Declare it SACRED by name: its ports, containers, DB, volumes, and any real user identities. **No worker ever touches it.** Adoption of finished work onto it is a deliberate, human-scheduled act (an env change, an image deploy), never a side effect of a phase build.

## 2. Per-phase isolated stacks + a ports ledger

Every phase (and every parallel worker) gets its own docker-compose stack: own DB container with its **own new volume**, own service port(s), seeded with synthetic/persona data — never real users. Test identities follow a recognizable pattern (e.g. `*@test.local`).

Keep a **ports ledger** in the handoff doc: which ports are sacred, which are burned (volumes still pin their names even after containers are gone), which are next-free. Parallel workers each get their own row, and each worker's spec names the *other* worker's resources as untouchable.

Teardown = stop + rm **containers only**. Volumes are evidence (see recovery-playbook.md); they appear on a KEEP/REMOVABLE list, and deletion is the human's action. This also enables A/B forensics later — a preserved volume is a queryable snapshot of what a phase actually did.

**Two isolation traps that reached a sacred stack in the field (both must be designed out, not remembered):**
- *Compose project-name collision:* docker compose derives its project (and default container names) from the directory basename — a fresh-clone test whose clone dir shares the repo's name will silently adopt the sacred stack's containers and **recreate them with the clone's config**. Fix structurally: set explicit, project-derived `container_name`/`name` in compose files, and make fresh-clone instructions use a distinct directory name.
- *Hardcoded sacred ports in tooling:* any fixture loader, smoke script, or probe with a baked-in default port (the sacred API port) will aim at whoever owns that port — usually the sacred stack — the moment someone runs it outside its intended stack. Fix structurally: tooling targets `$API_PORT`/stack-scoped env, never a literal sacred port.

## 3. The push hook

A global hook blocks agent-initiated `git push`. This is a **feature, by design**: every branch crosses the network by the human's hand, which makes the human gate physical rather than procedural. Working agreement:

- Hand the human the exact push command; never retry, never bypass, never bury a push inside a compound command (`&&` chains) where the hook fires and aborts the rest.
- The same posture generalizes: any hook-blocked operation (force-removals, volume deletion, prunes) is a *communication* to hand the action to the human, not an obstacle to engineer around.

## 4. Secrets

`.env` / creds live in the main checkout. Workers copy them into their worktrees as a FIRST ACTION and **never print, log, or commit** their contents. Secrets never appear in specs, reports, ledgers, or PR bodies.

## 5. Branch/PR topology

- One phase = one branch (`feat/<program>-phaseN`) cut from main, carrying the spec as its first commit.
- Workers build on worktree branches; merged into the phase branch at close-out; the phase branch is PR'd to main; the human merges.
- Gitignore the agent-worktrees directory. Never `git add -A` while worktrees exist.

## 6. Spend posture

Three numbers per phase — **expected / flag / hard tripwire** (e.g. $10 / $15 / $25) — where the tripwire is a stop-loss, not a budget. Estimate before every recorded eval/LLM batch **and put the estimate in a commit message** (a committed estimate is a receipt the actuals get judged against); iterate on mocks and single smoke runs; report actuals per phase. Calibrate to the phase *type*: well-mocked construction phases cost cents to ~$1; research/eval-heavy phases (sweeps, judged tiers, baselining) run single-digit dollars — set their tripwires accordingly, or the stop-loss trips falsely and teaches everyone to ignore it.

## 7. Permission allowlist

Day one, alongside the ports ledger: commit a permission allowlist covering the command shapes workers will live in (test runner, task-runner targets, docker compose forms) and write specs so routine invocations use *exactly* those shapes. An autonomous worker that shells out through ad-hoc entry points (`python random_script.py`) will block on an interactive prompt no one is watching — a stall class as real as never-stand-by. Funnel new tooling into allowlisted patterns (e.g. `just` targets) rather than widening the allowlist per script.

## 8. Quality floor — the test-floor ratchet

A dense, deterministic unit suite is a **firm precondition** for autonomous work (see day-zero setup in SKILL.md), not a nice-to-have — it is the self-correction loop workers run inside between check-ins. Mechanics:

- Every phase spec states the suite floor as a NUMBER ("full suite green, floor 612"), and the floor **only ratchets upward** — each phase's new tests raise the next phase's floor (reference program: 612 → 680 → 720 → 759 across four phases). Growth is fine; shrinkage is never: a "simplification" that deletes or loosens tests to stay green is a finding, updated pins must be deliberate and named in their commit message, and verifiers hunt weakened pins as a named failure class.
- Per-commit hooks (lint/format/fast-tests) installed in every worktree, so every worker commit is self-gating and a regression surfaces at the commit that caused it.
- Unit tier deterministic: external LLM/API calls mocked or oracled; live calls confined to integration/R&D tiers. Determinism is what keeps the floor checkable in seconds — that speed is what makes hours of worker autonomy and one-command orchestrator spot-verification affordable.
- **State the canonical suite command in the spec** (exact pytest/task-runner invocation): a partial glob that silently misses test files makes the orchestrator's spot-check disagree with the worker's honest count.
- A **built-artifact pass** per phase: the phase's deliverables demonstrated from the built container/package against a seeded environment — not just the dev checkout.
- Additive-only DB migrations, written as if real data already lives in the tables.
