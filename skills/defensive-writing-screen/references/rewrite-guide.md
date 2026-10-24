# Anti-defensive rewrite guide

Adapted from the `anti-defensive-writing` skill (Kiterlin, MIT, commit `f516147d017a3fe43ae99192cb89d8261b0c8679`); see `NOTICE.md`. Use it after a candidate has been verified, and keep everything the original rules protect: evidence, scope, uncertainty, prohibitions, and unfavorable results.

## Core rule

Advance the claim. State what is true, what the text argues, what the evidence shows, or what the method does. Do not spend sentences on what the text does not claim, does not prove, does not cover, or does not attempt. Write as an author explaining an argument, not as an author negotiating with an imagined critic.

## What must survive

Keep a limitation when omitting it would change the validity of the claim, the interpretation of the evidence, the scope of application, the research design, a safety or legal requirement, or the reader's ability to use the result correctly. State such a limitation once, calmly, in the place where it belongs: methods, results, discussion, limitations, or the exact sentence that depends on it. Do not scatter it through abstracts, contribution lists, topic sentences, or conclusions.

## Classify before editing

Label each flagged item as one of:

- unnecessary disclaimer;
- necessary scope condition;
- real methodological limitation;
- useful conceptual contrast;
- evidence-based qualification;
- redundant clarification.

Only the first and last are routine deletion or compression targets. The middle four are rewritten for precision, not removed.

## Rewrite procedure

1. Name the job the sentence does. If it adds no evidence, scope, logic, precision, or reader guidance, delete it.
2. Convert defensive limitation into positive scope. "We do not claim these cases are representative" becomes "The analysis covers three institutional settings from 2015 to 2023", and only when those facts exist in the draft.
3. Replace stacked hedging with precision. "This may potentially suggest that X could influence Y" becomes "X influences Y in these cases". If uncertainty is real, name its source: "The design does not estimate population-level effects".
4. Keep contrast only when the contrast is part of the argument. Drop reflexive "not X but Y", "rather than", "to be clear", "it should be noted that".
5. Rebuild the paragraph around one job: claim first, then support, then any necessary limit. Remove repeated caveats, apology-like framing, and detours that exist only to fend off a hypothetical objection.
6. Strengthen with evidence, not apology. If a claim feels too broad, narrow it, sharpen the concept, or point to the evidence; do not bolt on a protective clause.
7. Do not manufacture facts to make a sentence land. Data, settings, mechanisms, causal links, and advantages must already be in the draft or the supplied evidence.

## Detection checklist

- unnecessary disclaimer or preemptive rebuttal;
- repeated statements of what the text does not claim;
- stacked hedges, or hedges on results the evidence already supports;
- caveats in high-impact positions: abstract, contribution list, topic sentence, conclusion;
- paragraph opening with a limitation before stating its point;
- negative framing where positive scope is available;
- self-undermining contribution statements ("only a preliminary attempt", "of limited reference value");
- reflexive "not X but Y";
- redundant "however", "nevertheless", "although" transitions.

## Discouraged patterns

"This paper does not claim..."; "We do not attempt to..."; "This is not to say that..."; "This should not be taken to mean..."; "The goal is not X but Y"; "Rather than arguing X, this paper argues Y"; "Although this study has limitations..."; "Of course, this does not fully capture..."; "It is worth noting that..."; "To be clear...". Keep any of them only when the sentence carries accuracy that would otherwise be lost.

## Metrics, experiments, unfavorable results

- When a metric is unfavorable, state the condition, metric, and number, then the tradeoff. Do not turn one weaker metric into a verdict on the whole method, and do not switch evaluation criteria to avoid the result. "Accuracy falls from 90% to 89%, and latency from 100 ms to 60 ms" stays a two-sided statement.
- Each experiment should answer at least one of: does the method work, what explains the gain, can alternatives be ruled out, when does it apply. When a supporting experiment is missing, name the specific claim that loses support instead of writing "the experiments are insufficient".
- Keep results that affect the central conclusion. Report them where the conclusion is discussed, not only in a limitations section.
- Do not attribute a gain to a module without the corresponding ablation, and do not describe a local observation as a general defect of the method.

## Chinese-specific habits

Check habitual modesty: "仅仅做了初步尝试", "只能提供有限参考", "仍有很大提升空间". Replace with what was done: "本文在两个数据集上评估该方法". Keep "初步", "可能", and "提示" when the evidence warrants them; do not add "显著" or "全面领先" to sound stronger. Remove admonitory tone ("切记") while keeping real prohibitions and technical conclusions. Keep necessary conditions such as "仅在……时" or "若欲……需要……" and rewrite them equivalently; never drop them to sound decisive.

## English-specific habits

Remove stacked modals ("may potentially suggest", "could possibly be associated with"). Keep a single modal or explicit uncertainty when warranted. An association stays an association. Do not delete "may", "suggests", or "under these conditions" mechanically; decide from the evidence.

## Examples

Defensive: "We do not claim that these cases are representative of all contexts."
Direct: "The cases show how the mechanism operates across three institutional settings." (only if the draft establishes three settings)

Defensive: "This paper is not intended to provide a comprehensive theory, but rather to examine one mechanism."
Direct: "This paper examines one mechanism through which platform governance reshapes participation."

Defensive: "This does not mean that policy design alone determines implementation outcomes."
Direct: "Implementation outcomes depend on how policy design interacts with administrative capacity."

Defensive: "While the sample is limited and cannot capture every variation, it still offers useful insights."
Direct: "The sample covers the variation relevant to the study's question." (only if the draft supports that claim)

Defensive: "We are not arguing that this model is superior in every situation."
Direct: "The model is most useful when the task requires interpretable comparisons across cases."

Examples show phrasing only. They never supply facts to a draft that lacks them.

## Before returning a revision

Remove any sentence that exists mainly to preempt an imagined objection. Confirm that no number, unit, condition, metric direction, prohibition, or unfavorable result changed. Confirm the paragraph still has one job and opens with its point.
