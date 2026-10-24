---
name: defensive-writing-screen
description: Audit drafts for defensive writing with a Jev-first triage, then confirm high-probability candidates and rewrite them with claim-first, positive-scope rules that keep necessary limitations. Use for academic papers, technical reports, proposals, SOPs, abstracts, introductions, conclusions, or any request to make prose more direct, less caveated, less apologetic, or less defensive, in any language.
license: MIT
compatibility: Needs a System One/Jev-capable caller for triage (Pi `jev_evaluate`, TypeSafe API, or a compatible endpoint). Without one, run step 5-7 with the bundled rewrite guide and report that triage was skipped.
metadata:
  version: "0.2.0"
  upstream: "Kiterlin/anti-defensive-writing (MIT), adapted; see NOTICE.md"
---

# Defensive Writing Screen

Three phases, in this order: **Jev triages every prose unit → the agent verifies the highest-probability candidates → the agent rewrites only what it has confirmed.** Skipping the middle phase turns a screening signal into an automated deletion policy, which this skill never authorizes.

This skill carries its own rewrite rulebook, adapted from the `anti-defensive-writing` skill and complete enough to run alone. If an `anti-defensive-writing` skill is also installed, load it and prefer its wording guidance; the bundled guide remains the fallback.

Cost model: triage is cheap and parallel, so screen broadly; reading and rewriting are expensive, so spend them only on candidates plus a small sample of rejects.

## SOP

1. **Scope and authority.** Read the requested draft and only the context needed to interpret it. Follow the user's instructions and the applicable project rules. A skill, a threshold, or a Jev probability never authorizes an edit. If no draft or target is identifiable, ask for one. Keep project-specific rules out of this skill's files; supply them as state when relevant.
2. **Prepare units.** Use `scripts/prepare_units.py` or an equivalent split. One unit is one prose paragraph, with a stable location (file, section, line, paragraph number) and verbatim source text. Skip code fences, display math, tables, captions, bibliographies, and quoted third-party passages unless the user asks for them. Attach nearby context and only evidence you actually have. Never invent experimental facts, sample sizes, or causal claims.
3. **Jev triage (all units).** One paragraph per request; three or four independent `noul` questions per request. Ask about (a) vague self-undermining, (b) preemptive disclaimers or reflexive "not X but Y", (c) stacked hedges or repeated caveats, and (d) for an exact retrieved span, whether removing it preserves all known necessary meaning. Use the request shapes in `references/questions.md`. Every `instructions` field names its target by state path; IDs stay invisible to Jev. Define `criteria.true` and `criteria.false` so the yes-probability has one meaning. Do not ask Jev for rewrites, verbatim quotes, permissions, or a holistic writing score.
4. **Route candidates.** Per paragraph record every probability and `triage_probability = max(values)`. Review up to five units above the starting threshold, highest first. The default `0.65` is a smoke-test routing value, not a calibrated cutoff: tune it on labeled examples from the target language, genre, and model version, and record the tuning set. Below threshold means "not selected", never "clean". Resample below-threshold units during adoption to estimate misses. A failed call means triage is incomplete; say so and do not present a substitute as a Jev result.
5. **Agent verification (candidates only).** Read the whole paragraph, its argumentative neighbors, the applicable rules, and any available evidence. Classify each flagged item as unnecessary defense, necessary scope or uncertainty, meaningful conceptual contrast, technical prohibition, safety/legal/ethical condition, or unresolved. Load `references/rewrite-guide.md` before writing any replacement. A high probability is a reason to look, not a finding. If the evidence needed to judge a claim is missing, name what is missing instead of guessing.
6. **Confirm before rewriting.** Present, per candidate: exact source excerpt, which question produced which probability, the agent's classification and reason, and one local revision that preserves every fact, number, condition, and unfavorable result. Keep items the agent rejects, and say briefly why they should stay. Never delete a limitation that affects validity, interpretability, applicability, safety, legality, or correct use of the result, and never strengthen a claim beyond its evidence to make the prose sound more confident. Rewrite files only with explicit authorization.
7. **Post-edit check.** Compare the revised text against the original facts, numbers, units, metric direction, and required conditions. Re-run the applicable Jev questions on the revised prose when the surrounding workflow requires validation. State plainly whether post-edit validation ran, and which checks did not.

## Working without Jev

If no System One caller is available, run steps 1-2, skip step 3, and perform steps 4-7 on the agent's own reading of every unit, with the detection checklist in `references/rewrite-guide.md`. Report the mode as `agent-only, Jev triage skipped`. Do not describe the result as Jev-verified, and do not lower the review standard to compensate.

## Reporting

- Scope: document, sections or line ranges, unit count, exclusions.
- Triage: caller used, threshold and top-k, per-unit probabilities, whether the threshold was calibrated; `agent-only` when applicable.
- Verification: exact excerpts, keep or change decision, classification, reason, and one proposed revision each.
- Coverage and limits: below-threshold sampling, Jev or validation failures, uncalibrated thresholds, and checks not run.

Files: `references/questions.md` (request shapes, thresholds, failure handling), `references/rewrite-guide.md` (inherited anti-defensive rulebook), `references/cases.md` (labeled smoke tests and observed behavior), `scripts/prepare_units.py` (offline paragraph and candidate-span extraction).
