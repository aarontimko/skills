---
name: numbered-rec-alts
description: Present recommendations as a numbered list where every item has a short topic phrase, a brief description, a Rec (the recommended solution and why), and an Alt (a tangible alternative that wins under different circumstances or goals). Use this whenever the user asks for recommendations, judgment calls, "what would you do", how to handle review findings, options for a decision, or invokes /numbered-rec-alts — and also when YOU need to surface non-mechanical decisions to the user mid-task (e.g. after a code review turned up judgment calls rather than clear bugs).
---

# Numbered Rec/Alts

A format for presenting recommendations so the user can rule on each item fast — by number, without re-reading walls of prose. Use your best judgment on the substance; the format is fixed.

## The format

For each item:

```
N - Topic in a short phrase

1–3 sentences describing the topic or issue. Go longer only when the issue
genuinely needs the depth — don't pad, don't truncate a real subtlety.

Rec: your recommended solution in a few sentences, and why you would do it
this way — the reasoning is part of the Rec, not optional.

Alt: a tangible, concrete alternate possibility that would be good under
other circumstances or for different goals. Name the circumstance or goal
that would make the Alt win.
```

Repeat for each item. Plain numbered items (`1 -`, `2 -`, ...), ordered most-important first.

## Rules that make it work

- **The Alt must be real.** A strawman Alt ("Alt: do nothing") wastes the slot. It should be something you'd genuinely reach for if the goals were different — and say *which* goal-difference flips the choice. If no honest Alt exists, say so in the Alt line ("Alt: none worth taking — X is strictly better here because...") rather than inventing one.
- **Items are independent rulings.** Each number should be decidable on its own. If two issues can only be decided together, make them one item.
- **Take a position.** The Rec is a commitment, not a menu. "It depends" belongs in the Alt's circumstance-naming, not in the Rec.
- **Close by inviting verdicts by number**, e.g.: *"Reply like `1 rec, 2 alt, 3 skip` — or push back on any of them."* Then execute exactly the verdicts given.

## Example item

```
2 - Token refresh window is hardcoded

The 30-day sliding window for refresh tokens is a literal in two places
(auth.py and the migration default). They can drift silently if one is
edited without the other.

Rec: hoist it to a single REFRESH_WINDOW_DAYS setting read by both, with
the migration default generated from it. It's a 10-line change and removes
the drift class entirely.

Alt: leave it hardcoded but add a unit test asserting the two values match.
Cheaper now, and fine if this service is feature-frozen — but it turns a
config change into a two-file edit forever.
```
