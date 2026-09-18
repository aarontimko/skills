# Recovery Playbook

Failure modes designed for in advance stop being failures. Four areas: worker stalls, context loss (compaction), evidence preservation, and the gotcha ledger.

## Worker stalls

The dominant failure mode of long-running background workers is **ending their turn to "wait"** — for a container, a long eval, a notification that will never come. In the reference program, three separate workers stalled exactly this way despite warnings.

**Prevention:** every worker prompt carries the never-stand-by rule with teeth ("no notification will come; poll bounded cycles in-turn") and, if true, the precedent ("N prior workers stalled on exactly this"). Long waits are legitimate — *in-turn polling* through them is the requirement. Tell workers the expected duration is normal: "roughly 5–6 hours of in-turn polling is expected and correct."

**Recovery recipe (in order):**
1. **Verify ground truth externally first** — worktree `git log`, running processes, containers, DB rows. Distinguish "stalled while healthy" (most common) from "stalled because broken."
2. **Resume via SendMessage** to the worker's agent id with (a) the actual current state you verified, so it doesn't re-derive or re-do work, (b) explicit orders to continue with in-turn polling, (c) the remaining sequencing.
3. Don't arm elaborate watchers that can't themselves resume the worker. The notification-on-stop plus SendMessage-resume loop is the mechanism that works.

**Distinguish stalls from sanctioned checkpoints** (see human-gate-protocol.md): a checkpoint ends with a completed report and a decision request; a stall ends with "standing by" / "waiting for". Only the latter gets the recovery recipe.

## Compaction and context loss

Long programs outlive context windows. The three-layer memory model:

- **The repo** remembers what was decided: decision log, specs, receipts, PR trail. If it matters beyond the session, it's committed.
- **The handoff doc** (session scratchpad or repo) remembers what's in flight. It is THE authoritative next-actions document, rewritten before each anticipated compaction and **updated at every state change** — launches, gate closures, rulings, merges. Contents: current state (SHAs, test counts, what's clean/running), governing principles for in-flight work, complete outlines for the next specs, pending human-side items, playbook reminders, a ports/resources ledger, immediate next actions.
- **Long-term memory** remembers how you work: the sponsor's preferences, spend posture, environment rules, glossaries.

Post-compaction protocol: read the handoff first, verify its claims against the repo (`git log`, `git status`, suite run), then execute its next actions. The handoff says what to do; the repo proves where you are.

## Evidence preservation

- **Preserve, never destroy, provenance.** Phase DB volumes survive stack teardown (stop+rm containers, leave volumes). In the reference program, resurrected volumes settled three disputes summaries had gotten wrong — including one that reversed a dataset's ground-truth note.
- **Resurrection recipe:** temp container of the same DB image mounting the volume read-only, default creds, throwaway port; stop+rm the container after; never rm the volume.
- **Prefer exporting** the relevant rows as committed artifacts when downstream work needs them durably (committed JSONL beats a volume that requires resurrection).
- Keep a KEEP/REMOVABLE volume list in the handoff doc; deletion is the human's action, on their schedule.

## The gotcha ledger

Every operational mistake gets written down once — in the handoff doc and in the next specs that could hit it — and never repeated. Seed entries from the reference program (several are environment-general):

- **Never `git add -A` with agent worktrees present** — it stages them as embedded-repo gitlinks. Stage explicitly; gitignore the worktrees dir.
- **Shared append-only files (run ledgers) conflict at merge by design** — union-resolve, then validate line-by-line. Say so in specs so workers append normally.
- **Re-install commit hooks after venv resyncs** ("pre-commit not found" → reinstall, retry).
- **Introspect JSON/DB shapes before writing extraction scripts** — schemas drift from memory.
- **zsh treats `===` specially** — avoid it in inline shell (even in echo separators).
- **A shared config key can serve two consumers** — before swapping a model/role/flag, grep for every consumer; split the role instead of editing the shared one (a registry-role swap nearly hit both the intended consumer and one with an opposite verdict).
- **Watch for silently-disarming safety rails** (a budget ceiling that no-ops when pricing data is missing) — make them loud, and test the disarm path.
