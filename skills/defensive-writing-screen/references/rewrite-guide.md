# Anti-defensive rewrite guide

Adapted from the `anti-defensive-writing` skill (Kiterlin, MIT, commit `f516147d017a3fe43ae99192cb89d8261b0c8679`); the commit, file hash, and license are recorded in `NOTICE.md`. The reference is provenance and attribution only. This file is the operative rulebook for this skill and is complete on its own: nothing in it requires the upstream skill to be installed, read, or consulted.

## Core rule

Advance the claim. State what is true, what the text argues, what the evidence shows, or what the method does. Do not spend sentences on what the text does not claim, does not prove, does not cover, or does not attempt. Write as an author explaining an argument, not as an author negotiating with an imagined critic.

## Preferred patterns

- "This paper examines..." / "This study shows..." / "The analysis focuses on..."
- "The evidence indicates..." / "The results suggest..."
- "This design allows..." / "In this setting, X shapes Y by..."
- "The central contribution is..."
- 本文研究…… / 本研究表明…… / 本文重点分析…… / 证据表明…… / 结果提示……

## Submission checks

- Remove self-criticism that adds no information.
- Narrow claims that exceed the evidence; withdraw claims the evidence does not support.
- Remove repeated limitation statements from abstracts, introductions, and conclusions; keep the ones the claim cannot survive without.
- Confirm the contribution stays visible in the abstract, introduction, results, and conclusion.
- When simulating reviewers, separate demonstrated problems, items needing verification, and optional extra experiments. Fix what affects the conclusion or its interpretation; do not convert every imagined objection into a limitation.

## Main argument

Identify the paper's main contribution: a new capability, a mechanism, lower cost, or better scalability. Organize the abstract, introduction, experiments, and conclusion around it, keep supporting contributions, and cut unrelated setup. If a reader finishes the abstract without knowing the contribution, the structure is the problem, not the phrasing.

## Writing principles

- Lead with the claim; the first sentence carries the point, not a caveat.
- Use positive scope: say what the text examines, explains, tests, compares, or contributes.
- Strengthen with evidence, not apology.
- One paragraph, one job. Do not mix argument, caveat, apology, exception, and clarification.
- Use contrast only when the contrast is part of the argument.

## Technical plans and SOPs

For Chinese technical plans, procedures, reports, and presentations, remove redundancy and admonitory tone while keeping technical meaning, applicability conditions, prohibitions, and operational purpose. State the operation, parameters, prerequisites, and result directly. Replace vague prerequisites such as "在条件允许时" with the concrete condition the draft supports ("标定前提：……"); keep "仅在……时" and "若欲……需要……" or rewrite them equivalently, never as unconditional actions. Drop admonitions such as "切记" while keeping real prohibitions and technical conclusions. Simplify "进行……的测量" to "测量……"; use "标定", "解耦", "淬灭", or "钳定" only when they name the actual operation. Do not change an operation to make the text sound more specialized.

## What must survive

Keep a limitation when omitting it would change the validity of the claim, the interpretation of the evidence, the scope of application, the research design, a safety or legal requirement, or the reader's ability to use the result correctly. A qualifier that names the budget, precision, protocol, implementation, or version under test is such a limitation, and so is one that reports what an intervention covered. State such a limitation once, calmly, in the place where it belongs: methods, results, discussion, limitations, or the exact sentence that depends on it. Do not scatter it through abstracts, contribution lists, topic sentences, or conclusions.

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
3. Keep the strength of a warranted qualifier. A rewrite may not turn "could hardly" into "difficult", "cannot" into "may not always", or "no prior report" into "few reports". Weakening a supported claim is as wrong as inflating it. Replace stacked hedging without strengthening the evidence. "This may potentially suggest that X could influence Y" may become "These observations suggest that X may influence Y". Keep association distinct from causation and preserve warranted uncertainty. Name its source when known.
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
- redundant "however", "nevertheless", "although" transitions;
- genuinely empty retreating tails, distinguished from useful references to conditions already stated;
- a result demoted behind a retreat while a stronger fact sits in the main clause;
- a claim wider than the evidence, or a fact stated in two sections.

## Discouraged patterns

"This paper does not claim..."; "We do not attempt to..."; "This is not to say that..."; "This should not be taken to mean..."; "The goal is not X but Y"; "Rather than arguing X, this paper argues Y"; "Although this study has limitations..."; "Of course, this does not fully capture..."; "It is worth noting that..."; "To be clear...". Keep any of them only when the sentence carries accuracy that would otherwise be lost.

## Retreating tails

A genuinely empty tail adds rhetorical retreat without necessary scope or uncertainty. A backward reference is not automatically such a tail. Read the whole paragraph and neighboring context: "under this setup" may refer accurately to several conditions just established. Keep a useful reference instead of repeating the setup in every sentence. Do not replace a multi-condition scope with just one selected condition. With missing or ambiguous context, retain the qualifier or ask for clarification; absence of an antecedent in an isolated sentence does not justify deletion. Sentence-initial conditions are not appended tails.

- A qualifier that names its condition stays: "at the 2B-step budget", "with
  0-shot evaluation", "within 1e-5", "in the current implementation".
- A qualifier whose removal would drop the fact of what was tested stays: "the
  contribution of the full path, not its components" reports the scope of the
  intervention, and a rewrite keeps it.
- Apply the same semantic test to method statements. Grammatical completeness without a qualifier does not establish that its scope or uncertainty can be removed.
- Optional explicit restatement of an already clear condition is a style choice, not a confirmed defensive-writing defect.
- Do not use this rule to remove a result. The tail goes; the number, the metric
  direction, and the unfavorable outcome stay, in the place where the result is
  discussed.

## Narrative placement

Three moves carry the same facts into a stronger position. None of them is a style
repair, and none may change a number, a unit, a direction, or a condition.

- **Restate.** When a sentence puts its own result behind a retreat while a stronger
  fact it already reports sits in the main clause, swap them. "The estimate is 0.7
  points below the baseline while using 12% of its steps" becomes "Using 12% of its
  steps, the estimate comes within 0.7 points of the baseline". It never becomes "the
  estimate matches the baseline".
- **Narrow.** When a claim covers more than the evidence, limit it to what was measured. An interpretation of reported numbers may help explain a comparison or aggregate; do not remove it solely because it adds no new number or condition. Remove only unsupported or genuinely redundant interpretation. Narrowing never hides an unfavorable result or stops a supported comparison merely to improve tone.
- **Relocate.** When a fact interrupts its unit or appears in more than one section,
  keep one statement where the reader needs it and name the location that keeps it.
  Relocating never deletes the fact.

The test is the same for all three: after the move, every number, metric direction,
condition, and unfavorable result is still present, and the sentence that carries the
result is the one a reader meets first. A unit that fails the test keeps its verdict.

## Protection before rewriting

Protect six classes of meaning: P1 results and directions, P2 mathematical/proof conditions, P3 measurement/reproduction conditions, P4 intervention/check scope, P5 design premises, P6 comparison semantics. A high probability never permits their removal. Protection does not freeze the exact words: a concession or apologetic frame may be restated if all favorable and unfavorable facts, uncertainty, objects and conditions survive.

Judge independent spans, not whole paragraphs. A clear direction-only comparison remains meaningful when its numbers are in a table; missing repeated numbers do not make it defensive or require a longer replacement. Conversely, the presence of a protected result does not shield a separate empty disclaimer. Record multiple findings within one paragraph rather than stopping after its first rewrite rule. Separate deletion from equivalent restructuring and confirmed defects from optional style choices.

## Document structure

A paper normally carries an abstract, an introduction, related work, a method,
experiments, a conclusion, and a limitations statement. Related work may fold into the
introduction, and limitations may sit inside a discussion. A draft that ends on its
limitations section leaves the reader with a withdrawal instead of the takeaway, and a
draft with no closing section at all leaves the reader without a statement of what was
solved, proposed, and shown. Both are structural findings, reported once at the document
level. Absence is not automatically a defect: a supplement, appendix, extended abstract,
letter, or proposal carries a different set, and the report says which roles the genre
does not require.

Placement is also structural, but there is no mandatory experiment order. Move evidence only when its distance from a claim creates a concrete reading problem. Related work may legitimately end by positioning the current study or motivating its design. Distinguish such transitions from redundant implementation instructions. Report optional reorganizations separately and name where any moved facts remain.

## Metrics, experiments, unfavorable results

- When a metric is unfavorable, state the condition, metric, and number, then the tradeoff. Do not turn one weaker metric into a verdict on the whole method, and do not switch evaluation criteria to avoid the result. "Accuracy falls from 90% to 89% while latency falls from 100 ms to 60 ms" stays a two-sided statement.
- Each experiment should answer at least one of: does the method work, what explains the gain, can alternatives be ruled out, when does it apply. When a supporting experiment is missing, name the specific claim that loses support instead of writing "the experiments are insufficient".
- Keep results that affect the central conclusion. Report them where the conclusion is discussed, not only in a limitations section.
- Do not attribute an effect to one component without the corresponding intervention test, and do not describe a local observation as a general defect.

## Chinese-specific habits

Check habitual modesty: "仅仅做了初步尝试", "只能提供有限参考", "仍有很大提升空间". Replace with what was done: "本文在两个案例上评估该方法". Keep "初步", "可能", and "提示" when the evidence warrants them; do not add "显著" or "全面领先" to sound stronger. Remove admonitory tone ("切记") while keeping real prohibitions and technical conclusions. Keep necessary conditions such as "仅在……时" or "若欲……需要……" and rewrite them equivalently; never drop them to sound decisive.

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

Context-dependent: "The comparison supports the benefit of the additional term under this setup."
Keep when the setup has already been specified and limits the conclusion. If the antecedent is unclear, ask or clarify from available evidence; do not delete the qualifier merely because it is deictic.

Examples show phrasing only. They never supply facts to a draft that lacks them.

## Before returning a revision

Remove any sentence that exists mainly to preempt an imagined objection. Confirm that no number, unit, condition, metric direction, prohibition, or unfavorable result changed. Confirm the paragraph still has one job and opens with its point.
