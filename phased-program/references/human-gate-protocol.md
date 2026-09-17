# Human Gate Protocol

The human sponsor's gates are load-bearing. Three mechanisms make them real: ruling presentations with depth, frozen artifacts only the human can version, and a decision log where rulings are recorded verbatim and remain supersedable.

## Presenting rulings

Every open question that needs a human decision gets, in prose (not a bare option list):

1. **Background** — what happened, with the primary evidence inline. Don't make the human cross-reference.
2. **Options** — each with pros, cons, and *forward impact* (what future work each choice enables, blocks, or defers).
3. **A recommendation** — commit to one and say why. The human can overrule; never present a menu without a position.
4. **Door label** — one-way or two-way. Two-way doors can be decided fast and revisited; say so explicitly ("this is a two-way door — we can revisit if it turns out meaningless").

Detail level: err toward *more detail and fewer abbreviated abstractions*. Summaries hide exactly the hair-splitting distinctions the human's judgment is for. When a ruling is important enough, walk the cases one at a time with the verbatim records on the table.

A legitimate verdict on an under-evidenced question is **open-pending-data**: leave the entry `[OPEN]`, and write the data-collection plan into the next phase's spec as a cheap piggyback deliverable (each later worker's stack is a free experiment venue) with the boundary stated — "you're adding data, not deciding." Close the entry when the draws arrive, with a pointer from the old entry.

## Supersedable rulings — the most important property

Record verdicts verbatim in an append-only decision log (dated entries, `[OPEN]`/`[LEANING]`/`[DECIDED]` tags; resolving an old entry means *re-tagging* it with a pointer to the new one, never editing history). Crucially: **a human re-reviewing their own past ruling is a feature.** The single best design decision of the reference program came from the sponsor saying "my earlier approvals may have been too fast/handwavy" and re-reviewing five cases against the primary records. Make that cheap:

- Keep the primary artifacts (verbatim corpora, preserved DB volumes, per-case rationales) so a re-review can *reason in context* rather than from memory.
- When a new ruling supersedes an old one, the log says so explicitly and keeps both.
- Never treat a past `[DECIDED]` as a wall — treat it as the current best answer.
- **Negative results get the same durability as positive ones**: a measured "don't ship" keeps its named config in the run ledger (retired, never deleted), and the recorded ruling names the exact run-ids it rests on — "any future change starts from these N ledger lines and re-measures." This makes an old "no" cheap to revisit deliberately and impossible to re-litigate accidentally.

## Gate amendments and entry obligations

A gate is a checklist, not a vibe — failing it means the phase isn't done, not that the gate was too strict. When an item genuinely cannot be met in its phase (a wall-clock clause, a quality target the current architecture can't reach), don't waive it and don't fudge it:

- **Amend the gate doc deliberately** and convert the item into a **named entry obligation of a specific later phase**, recording the exact evidence (ledger lines, failing case names, numbers) as the baseline that phase must beat.
- Every later kickoff spec carries an **"Entry baseline (inherited obligations)"** section restating those numbers verbatim.
- The PR that carries an amendment says so explicitly — "approving this PR ratifies the gate amendment" — so the human's merge *is* the ratification.
- If a spec can foresee the unsatisfiable clause, it proposes the split interpretation up front, flagged for the human's close-out ratification, with the build designed to be identical under either reading.

## The deferral ledger

Distinct from door-labeling and from the gotcha ledger: a standing **deferral ledger** for deliberately-accepted risks/shortcuts, each entry made *the day the deferral happens*, with four columns: (1) why it's acceptable under the current posture, (2) what lockdown/hardening looks like, (3) the **trigger condition** that makes fixing it mandatory, (4) where it was decided. Rules:

- Nothing on the list is a bug; everything is a scheduled obligation.
- Reviewed at every circle-back and before any exposure change (deployment beyond the current operator).
- Entries close only by structural fix plus a decision-log entry — struck through, never deleted (closed entries teach the closure pattern).
- Derive the pre-exposure/deploy-day checklist from it; later phases can pull deliverables straight off it.

## Frozen artifacts and ratification

Declare the load-bearing interfaces frozen by name and version (API contracts, schemas, grammar, DB invariants like append-only triggers). Rules:

- Workers may **propose** a change (implemented as optional/additive, no-op when absent, byte-identical default behavior — proven by evidence) and document it as a *proposed vN+1* in their report.
- Only the human **ratifies** the version bump; only after ratification does the frozen doc get edited.
- Weakening a safety invariant (a trigger, a guard) is never routine — it is a STOP even to propose casually.

## Mid-phase human gates: the sanctioned checkpoint

When a phase contains a genuine human decision in the middle (approving a generated proposal, choosing between built alternatives), design the stop explicitly in the spec, or it will look like a stall:

- The worker ends its run-segment **cleanly**: everything committed, environment left up, and a **checkpoint report** containing the decision artifact verbatim, its supporting statement, receipts so far, and exactly what happens on each verdict (approve / amend / reject).
- This is the ONE sanctioned turn-end mid-phase — distinguishable from a stall because it ends with a completed report, not an idle wait. The worker does not poll for a reply.
- The orchestrator relays to the human with the full ruling format above (including anything the worker plans to add beyond the literal artifact — surface every delta the human is implicitly approving).
- Resume the worker via SendMessage with the verdict, restated context, and the post-verdict sequencing. Close the gate explicitly: "there are no further sanctioned stops; your next turn-end is the final report."
- **A rejection is a receipt, not a failure** — the worker records it, proposes the next iteration, and checkpoints again.

## What stays human-only (never route around)

- Version bumps to frozen artifacts; any weakening of safety invariants.
- `git push` (see environment-contract.md) and PR merges.
- Approval of generated policy/content changes that a gate exists to review.
- Scope changes and one-way-door decisions.
