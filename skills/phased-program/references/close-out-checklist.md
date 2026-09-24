# Close-Out Checklist

The fixed sequence from "worker reports done" to "phase merged and cleaned up." Order matters: verification before presentation, rulings before merge, docs before push.

## 1. Spot-verify personally
Full checklist in verification-playbook.md. Nothing reaches the human unverified.

## 2. Present rulings
Every needs-a-ruling question with options / pros-cons / forward impact / recommendation / door label (human-gate-protocol.md). Present informational findings separately, labeled "no action needed." Wait for verdicts — rulings can change what the docs commit says.

## 3. Execute verdicts
Whatever the rulings require: config changes, doc edits, dataset relabels. If a verdict requires worker-side work, resume the worker; otherwise do it on the phase branch.

## 4. Merge the worker branch
- Merge into the phase branch (often fast-forward when the phase branch only held the spec).
- **Union-resolve shared append-only files** (run ledgers) if parallel workers appended; then validate the merged file line-by-line.
- Re-run the full suite on the merged phase branch.

## 5. Docs commit
- Decision-log entries: one per ruling, dated, verdict verbatim with rationale, `[DECIDED]` tag; re-tag any now-resolved `[OPEN]` entries with pointers.
- Roadmap/gate doc: the gate-closed line with date and evidence pointers.
- Update the handoff doc and long-term memory.

## 6. Human pushes
Hand the exact command (`git push -u origin <branch>`). Never attempt it yourself; never embed it in a compound command (environment-contract.md).

## 7. PR
`gh pr create` with this body shape:

```markdown
## What this is
[1–2 paragraphs: the phase, what gate it closes, the governing principle
if one shaped it.]

## Gate <N> evidence
| Checklist item | Evidence |
|---|---|
| [each gate item] | [SHAs, ledger run-ids, zero-diff tables, live-probe
results, test counts — the same grounded-claims standard as everywhere] |

## Rulings executed in this PR
1..n. Each verdict with who ruled, what, and the recorded rationale.

## Notes for review
- Anything the human should know post-merge: volumes to keep, queues to
  review, informational findings, spend actual vs expected.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```


If this PR carries a gate amendment (an item converted to a later phase's entry obligation — see human-gate-protocol.md), the body says so explicitly: "approving this PR ratifies the gate amendment," with the baseline evidence the receiving phase must beat.

## 8. After the human merges
- [ ] Sync main; confirm the merge commit.
- [ ] Remove agent worktrees (`git worktree remove`), delete merged local branches.
- [ ] Re-run the full suite on merged main.
- [ ] Update the handoff doc (state, next actions) and long-term memory (the arc entry).
- [ ] Confirm environment state: phase containers gone, volumes on the KEEP list preserved, ports ledger updated (which ports freed, which volumes still pin names).
- [ ] Tell the human the close-out state plainly, then what's next.

## 8b. Deploy tail (when a production/permanent stack consumes this repo)

Merge is not done; *live* is done. If the program's output runs somewhere permanent, every phase that changes shipped behavior ends with a deploy, executed per that stack's own runbook (a separate skill/doc owned by the stack, not by this program — read it before touching anything). The generic shape, each item evidence-producing:

- [ ] Backup first, verify the artifacts exist before proceeding.
- [ ] Build the deployable at the exact merged SHA from a clean tree; tag with the SHA.
- [ ] Retag/roll the stack per its runbook; run migrations (additive-only) before expecting health checks to pass.
- [ ] Live verification: health/ready endpoints, the stack's contract-check script, cleanup of any probe artifacts it leaves.
- [ ] Execute the live config change the phase was FOR (feature flips, versioned config bumps) — with whatever audit mechanism the stack uses (pre-change epochs, change log), so the change is attributable.
- [ ] Record the old→new tag in the stack's runbook with date, PR, migrations delta, verification results, and any client-facing breakage (e.g. "clients must re-authenticate" vs "no schema changes, clients unaffected").
- [ ] Tell the human what is now live and what to watch (the metric that will show whether the change works).

## 9. Program close-out (after the last gate)

When the final gate closes, write the **standing operations handoff** as a committed doc (not a chat message, not the session handoff): one paragraph of what shipped; remaining operational tasks in natural adoption order, each with its evidence pointer; the KEEP/REMOVABLE resource lists and the resurrection recipe; the **standing invariants that must not drift** (sacred stack, frozen-artifact versions, any governing principle's preconditions); deferred-not-designed enhancements; and a key-evidence-locations table. The final PR states explicitly what the program hands to production. Without this doc, a finished program strands its operational knowledge in the orchestrator's memory and a hundred decision-log entries.
