---
name: adversarial-review
description: Run a robust adversarial review — a fresh-context subagent charged to BREAK the work (not confirm it), hunting 3–6 named failure classes with evidence and a verdict — then triage with judgment, not deference - adjudicate each finding, quietly fix what is truly wrong and leaves the effort's north star untouched, and present north-star changes and genuine judgment calls in numbered-rec-alts format. STANDING RULE - run this unprompted on EVERY new feature or non-trivial change when it reaches "ready" (tests green, about to hand the user the push command), no exceptions for "small". Also use whenever the user says "adversarial review", "have an agent review this/your work", or wants a spec/design/plan attacked before building.
---

# Adversarial Review

A fresh-context reviewer tries to break the work; findings get triaged so the user only hears about what actually needs their judgment. Extracted from the `phased-program` skill's verifier layer — inside a phased program that skill's verification playbook layers this method with program scaffolding; standalone, this is the whole loop.

## When it runs

- **Standing rule (unprompted):** when a feature reaches "ready" — tests green, about to hand the user the push command — that moment IS the trigger. Launch the reviewer *before* presenting the branch; the review is part of "ready", not an optional extra. No exceptions for "small": the review that proved this rule ran on a feature that already had passing tests and a smoke check, and still surfaced two findings that would have broken production.
- **On request:** any time the user asks for an adversarial review of code, a plan, a spec, or your own work.

## Two modes, same charter

- **Design review** — attack a spec/plan *before anything is built*: wrong invariants, hidden data-visibility holes, missing failure modes, and especially **claims about existing code that aren't true** (the reviewer must read the code the spec cites, not trust the citation). This is where the highest-value catches happen — a blocker here costs a spec edit instead of a rebuilt feature. Prefer this mode whenever a plan exists and building hasn't started.
- **Code review** — attack the built change: the diff, the tests, and the running behavior.

## Designing the reviewer

Launch a subagent (Agent tool, fresh context). The design rules, each load-bearing:

- **Fresh context.** The reviewer must not share the builder's assumptions — it reads the code and system cold. Reviewing your own work in-context and calling it adversarial is theater; the whole value is the un-shared assumption.
- **Adversarial charter.** Its job is to *break the claims, not confirm them*. Prompt it with the specific attacks: "try to write directly, bypassing the draft queue", "prove the budget ceiling does NOT bind", "try to make deploy-before-migrate brick login".
- **3–6 named failure classes, specific to this change.** Generic "review this" reviewers find style nits. Name the hunts: privilege escape, invariant leak between features, silent no-op, spec divergence (built thing ≠ agreed design), weakened tests/pins, "does mainline behavior change AT ALL when the new feature exists".
- **Live probes over code reading** wherever the system can run: snapshot state, fire an adversarial payload, diff bytes. A re-runnable zero-diff table beats any amount of source inspection.
- **Evidence, not vibes.** Every finding names its proof — file:line, a failing command, a DB row, a diff. Number findings F1..Fn, severity-rank each (**BLOCKER / MAJOR / MINOR / NIT**), and label each **CONFIRMED** (reproduced/demonstrated) vs **PLAUSIBLE** (reasoned but not reproduced).
- **Verdict required.** The report ends with a verdict: **safe to push** (design mode: **safe to build**) or **fixes required**, with the gating findings named.

## Triage — judgment against the reviewer

The reviewer is a **finder, not a judge**. The classic failure mode after an adversarial review is deference — "you said it's wrong, okay, I'll fix it" — which merely relocates blind trust from the builder to the reviewer. Adjudicate every finding on its merits before touching anything: is it actually wrong (a PLAUSIBLE label is a hypothesis, not evidence — confirm it yourself before acting on it), and does the proposed fix serve the effort's north star? **Rejecting findings is a healthy, expected outcome** — a tough reviewer is *supposed* to over-generate, and sometimes the "flaw" it found is the design working as intended.

The boundary for what gets fixed without asking is not size, severity, or relatedness — it is the **north star**: the agreed intent, invariants, and design of the effort. A fix moves the north star when it changes *what* the thing is supposed to do — reverses an agreed design decision, weakens an invariant, redefines what success means — rather than *how* the code achieves the agreed thing.

1. **Fix freely, quietly:** anything genuinely wrong whose fix leaves the north star untouched. Opportunistic cleanups the reviewer surfaced along the way are welcome even when unrelated to the change under review — scope creep in service of the same intent is fine. Land fixes as separate review-named conventional commits, then **re-verify** — a finding fixed without re-verification is half-fixed; re-run the exact probe or test that demonstrated the finding, not just the suite (in design mode, re-check the spec edit against the finding's evidence). The user doesn't need the play-by-play — report in one line: "review found F1–F5; F1–F4 fixed and re-verified."
2. **Never auto-fix a north-star change.** Anything that would move the north star — plus any genuine judgment call (more than one defensible answer) and any divergence between the build and the agreed design — goes to the user via the `numbered-rec-alts` skill, one numbered item per call, Rec + Alt each; wait for verdicts before proceeding. If you're unsure whether a fix touches the north star, that uncertainty is itself the signal — present it.
3. **Nothing is silently dropped.** Every finding ends fixed, presented, or explicitly rejected on the record with the reason. A **fixes-required verdict always reaches the user** even when every gating fix was quietly applied.

Only after triage completes — fixes re-verified, judgment calls ruled on — is the change "ready" and the push command handed over.
