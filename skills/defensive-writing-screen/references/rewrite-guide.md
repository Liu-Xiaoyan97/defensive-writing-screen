# Anti-defensive rewrite guide

Adapted from `anti-defensive-writing` by Kiterlin (MIT, commit `f516147d017a3fe43ae99192cb89d8261b0c8679`). Attribution and the upstream hash remain in `NOTICE.md`. This bundled guide is complete on its own. No other skill is loaded, consulted or required.

## Core rule

Explain the work directly and accurately. Remove unnecessary authorial apology, uncheckable effort assurances and empty defenses against hypothetical criticism. A disclaimer about authorial intent can be empty when it adds no reader-relevant distinction. Preserve every fact, uncertainty, limitation and inference boundary that helps the reader understand the work.

Detect a communicative problem, not a grammatical pattern. Negation, concession and repetition can be useful. A shorter positive version is not evidence that the source was defensive. Information preservation is necessary, not sufficient, for confirming a defect.

## Main argument

Make the contribution identifiable and connect claims to their evidence. Supporting contributions and unfavorable results remain. Do not impose a triumphant narrative on uncertain or negative evidence. Missing explanation of the contribution is a structural issue, not automatically a defensive phrase.

## Writing principles

- Prefer direct statements where they preserve the same meaning.
- Begin with a condition when the result depends on it. Claim-first is not mandatory.
- State the scope positively or negatively according to clarity, not a ban on negation.
- Keep contrasts that distinguish methods, metrics, mechanisms or outcomes.
- Let evidence determine strength. Do not strengthen or weaken a claim for tone.
- Distinguish scientific criticism from authorial self-justification.

## Technical plans and SOPs

Preserve prerequisites, prohibitions, applicability, tolerances and operational purpose. “Only when”, “must not” and “cannot be used” may be critical safety information. Replace a vague prerequisite only with a condition already established in the source; never invent one. Removing admonitory tone or simplifying nominalizations is usually optional style, not a defensive-writing hit. Keep precise technical terminology rather than making the wording sound more specialized.

## Preferred patterns

Use “The analysis examines…”, “The evidence suggests…”, “The test covers…” or “The method does not establish…” as appropriate. None is privileged over a necessary negative statement. In Chinese, “本文研究……”, “结果提示……” and “本次测试不能确定……” are all legitimate when they match the evidence.

## Submission checks

Separate demonstrated defects, evidence gaps and optional presentation changes. Do not label every plausible reviewer question a manuscript failure. Check source quotations, scope, attribution and modal degree before recommending edits. Keep limitations wherever an independently read claim requires them, including abstracts and conclusions.

## What must survive

Preserve numbers, units, metric directions, comparison objects, effect degree, modal strength, causal status, mathematical assumptions, tested conditions, intervention scope, safety/legal/ethical restrictions and unfavorable results. A meaningful interpretation may add no new number and still be necessary. A backward reference can efficiently retain a previously specified scope.

Do not remove a restriction just because its facts also appear elsewhere. The question is whether the reader at this location would lose an inference boundary. Repetition across independently read sections can be useful.

## Classify before editing

First classify the function: result, scope, methodological limitation, attribution, useful contrast, evidence qualification, navigation, ordinary presentation, or unnecessary rhetorical defense. A protected fact and an empty apology may occupy different spans of one sentence.

For every asserted defense, name the exact span, explain its unnecessary function and cite contextual evidence. Before deciding that none exists in a selected unit, actively scan all of its sentences and headings for effort/rigor/responsibility assurances, apologies, author-intent or value disclaimers, non-claims, anticipated-reader rebuttals, reasons for omitting experiments, model scales, baselines or repeated prior results, explanations discounting unfavorable outcomes, and repeated caveats. Search semantically, including question-and-answer responses and claims about what is needed, useful, beneficial, in scope or worth repeating. In FAQ/Q&A clusters, compare generic purpose/genre disclaimers across neighboring answers. Repeated “this is not a benchmarking paper” or “all we need to show” wording may function as an empty rebuttal when the same scope or burden has already been explained; do not assume this from the phrase alone. Preserve repeated answers that distinguish separate comparison objects, design rationales, scopes or evidence limits. When an answer says there is “no benefit” in repeating prior negative results, verify those results cover the same population or system, conditions, research question, comparison and inference; results from a related but narrower setting do not establish that an evaluation at the queried scope has no value. When “all we need to show” narrows the burden, verify that existence is actually the theorem or predeclared research objective instead of treating the asserted burden as its own justification. For a non-claim immediately followed by the same positive result, compare proposition, direction and degree against evidence already stated; preserve distinct subgroup uncertainty and scope. Markers are retrieval cues, not a complete checklist. Record the candidate before checking whether it has a legitimate reader function; safe rewrite availability is a separate later test. Keep a separate per-unit candidate ledger with exact spans, possible defensive functions, decisions and concrete KEEP rationales. In Pass B, each `decision_reason` must state the exact candidate proposition/function, the local evidence proposition or reader function offered in its favor, whether they match on the relevant object/conditions/comparison/question/inference, and whether unnecessary authorial evaluation remains after protected content is preserved. A KEEP rationale that names only a related fact or plausible design reason is incomplete. Record `candidate_scan: none` only after inspecting the complete unit and context. The ledger audits discovery and is not a positive label. For omitted-work rationales, test separately whether the wording dismisses a reasonable scope question and whether it supplies a concrete design reason; lack of evidence alone does not establish defensive function. For a broad evaluation such as “no benefit,” “does not contradict,” “necessary,” or “scope creep,” write down the exact proposition and the proposition supported by nearby facts or cited work. Compare population/system, conditions, comparison, question, and inference. A citation on the same topic or a relevant fact does not by itself establish that the evidence answers the exact claim; equally, a direct match plus a separate stated aim can support a real scope boundary. A non-claim immediately followed by the direct result it denies is a candidate only when it adds no distinct inferential boundary. When a qualifier follows subgroup estimates, preserve differences in precision, significance, and group scope; do not collapse an overall estimate into a subgroup claim. A disclaimer about not framing prior work or limitations negatively is a candidate when the substantive analysis follows and the disclaimer adds no method, evidence, or scope. Do not infer the author's actual motives or emotions. Judge the wording's role in the argument.

For an explanation of an unfavorable or mixed result, separate observed directions from the proposed interpretation and the evidence that links them. A specific interpretation can be scientifically useful even when the defensive-writing review cannot independently verify it. Missing support is an evidence-alignment question, not a defensive-writing hit by itself. Do not upgrade, downgrade, delete, or relabel the interpretation under this screen. Mark the evidence relation unresolved when needed, while preserving the original modality.

Do not conflate evidence alignment with defensive writing. An unsupported causal explanation may need separate qualification or evidence review, but it is not defensive solely because support is missing. Do not use a defensive-writing rewrite to change a categorical attribution into a possibility, or otherwise change its modality. Preserve the original claim and report the evidence concern separately; when the evidence cannot be assessed, mark the issue unresolved.

For each retained candidate, name the specific fact, method, scope, attribution, comparison, audit purpose or inference boundary it preserves. “Necessary caveat” without that explanation is not a completed KEEP test. Required AI-use and responsibility disclosures remain protected unless a separate empty rhetorical span is established.

Then independently classify the repair. A real issue remains established even when no safe rewrite is found; that case is partial or unresolved, not an absent issue.
- confirmed: issue established, repaired, source anchored and all meaning preserved;
- partial: issue established but repair unsafe or ineffective;
- optional: safe presentation improvement without a defensive problem;
- keep: no change required;
- unresolved: missing context, ambiguous source or unverified meaning.

## Rewrite procedure

1. Read the full paragraph and relevant neighbors. Resolve references before editing.
2. Establish the problem without looking for a convenient rewrite first.
3. Mark protected information separately from unnecessary rhetoric.
4. Propose the smallest repair that removes the actual problem.
5. Check facts, strength and issue removal independently. Record a reason for each.
6. If the repair merely swaps although/but for punctuation, ask whether any separate defect existed. Normally this is optional presentation.
7. Keep an unresolved condition. Do not invent conditions, mechanisms or results to make a fluent replacement.
8. Verify the original quotation against the source. Failed anchors block accepted edits.
9. Whole-sentence deletion, even inside a larger rewrite, requires the focused check and complete known evidence. A high deletion score is not a diagnosis.

## Detection checklist

Investigate, but do not automatically condemn:
- authorial apology unrelated to the measured result;
- an assurance of effort or rigor that supplies no method or evidence;
- a disclaimer repeating the same locally available scope without a reader function;
- a retreat explicitly intended only to sound less confident;
- a broad disclaimer about authorial intent when it precedes substantive analysis;
- a non-claim immediately followed by the direct result it denies, if it adds no distinct boundary;
- a broad claim that an omitted experiment has "no benefit" when it supplies no design rationale and dismisses a reasonable scope question. Keep prior results and the actual study scope; do not infer that every omitted experiment needs to be run;
- authorial effort or rigor assurance even when nearby method details are present; assess whether the assurance adds evidence beyond those details;
- a defense of a poor result, testing whether its wording goes beyond an evidence-supported interpretation; if the problem is real but no equivalent repair is supportable, retain the claim and disposition it partial or unresolved rather than strengthening or weakening it;
- a justification for an unfavorable result that exceeds the evidence. Assess the unsupported attribution separately and do not change its modality under this skill.

Exclude as defects unless there is an independent problem:
- actual tradeoffs and ranked comparisons;
- limits of causal identification, statistical power or external validity;
- contribution attribution and evaluation scope;
- audit history and disclosure of selection procedures;
- ordinary “it should be noted” lead-ins;
- duplicated words, sentence merging and changes of emphasis.

## Discouraged patterns

There is no blacklist of “although”, “however”, “only”, “not”, “rather than” or “we do not claim”. These are retrieval hints. A sentence that cannot establish clinical safety or a theorem outside its assumptions must say so. An apology that supplies no such restriction may be removed. Read context to tell the difference.

## Retreating tails

A tail is empty only when it adds rhetorical withdrawal without necessary uncertainty, scope or navigation. “Under these conditions” can refer to several conditions already specified; preserve that reference. A missing antecedent requires more context, not deletion. Do not replace a multi-condition scope with one selected budget. Conditions at the beginning of a sentence are not appended retreats.

## Narrative placement

N1 restates emphasis, N2 narrows an unsupported claim, N3 relocates material. N1 and N3 are often optional presentation and never detection hits merely because they improve flow. N2 is evidence alignment; keep it distinct from defensive rhetoric. Every relocation names a destination. Do not describe a deficit as a match or choose a favorable metric to hide an unfavorable one.

## Protection before rewriting

P1 protects results and directions, P2 mathematical conditions, P3 measurement/reproduction conditions, P4 intervention scope, P5 design premises, P6 comparison semantics. Protection concerns meaning, but does not prove that alternative framing is needed. A separate unnecessary apology beside a result can be repaired without changing the result. Record independent spans rather than labelling the entire paragraph defective.

Keep the same modal strength and degree. “Could hardly” must not become either “difficult” or an absolute “cannot”. “May”, “suggests”, “some”, “partly”, “only” and “not necessarily” can carry information. Stacked hedges are not permission to silently upgrade evidence. If an equivalent repair is unavailable, KEEP.

## Document structure

S1 missing conclusion, S2 ending on limitations, S3 missing necessary scope, S4 absent/folded related work, S5 distant evidence and S6 redundant implementation detail are observations. Genre, venue and reader function determine whether a change is warranted. A required final limitations section is not a defect. Related work can motivate the current design. Do not impose one experiment order or move a restriction away from the claim that needs it.

## Metrics, experiments, unfavorable results

Report benefits and drawbacks together when that comparison answers the research question. “Sensitivity rises but specificity falls” is a useful result, not defense. An insignificant contrast does not establish equivalence. More conditions do not replace repeated random seeds. A possible explanation of a poor outcome must remain a hypothesis unless the evidence identifies it. For mixed metrics, inspect whether the proposed mechanism explains the direction difference and whether the text states the evidential limit; do not require the interpretation to be treated as fact. Neither deleting that hypothesis wholesale nor changing its connector necessarily repairs an unsupported attribution.

## Chinese-specific habits

“仅”, “初步”, “可能”, “尚不能” and “在一定程度上” may state actual scope or evidence strength. “我们对此深感抱歉” may instead be unnecessary authorial posture. Do not decide from the word alone. Simplifications such as “进行测量” to “测量” are optional style. Preserve real prohibitions such as “不得” and requirements such as “仅在……时”.

## English-specific habits

Meaningful “not X but Y” contrasts, literature qualifications such as “to our knowledge”, and actual “although” tradeoffs stay. Removing a metadiscursive lead-in is normally optional. Compare the complete original and revision, including quantifiers and hypothetical status, rather than counting hedges.

## Examples

**Candidate:** “We therefore do not claim that the within-group relationship is absent. It is present and weak.” When the same local context already reports the relationship and its strength, the denial adds no distinct boundary. “The within-group relationship is weak but present” retains direction and degree. If the non-claim instead limits a different analysis or population, keep it.

**Candidate:** “We are not framing these limitations negatively; rather, they show how the design constrains interpretation.” The intent disclaimer adds no information about the limitations. “These limitations show how the design constrains interpretation” preserves the analysis. Keep descriptions of the limitations, their consequences and mitigation.

**Keep for this screen; assess evidence separately:** “The regression is a normalization artifact rather than a failure of initialization.” Whether the causal attribution is supported is not itself a defensive-writing decision. Do not rewrite it as “may be consistent with” unless the author separately authorizes an evidence-alignment edit.

**Keep:** “We report the full search path so readers can check whether selection depended on searching until something worked.” This names an audit purpose and the disclosed procedure. Anticipating a concern is not automatically an empty disclaimer.

**Contextual candidate:** “There is no benefit in repeating established negative results.” If this answers a reasonable question about why a relevant experiment is omitted, but gives no design reason, retain the reported prior result and state the scope studied. Do not infer that every omitted experiment should be repeated.

**Keep:** “The change raises sensitivity but reduces specificity.” Both directions are results. A semicolon is optional.

**Keep:** “We evaluate an existing algorithm; we do not introduce a new one.” This attributes the contribution.

**Keep:** “The interval is wide and cannot rule out an important difference.” This calibrates uncertainty.

**Unresolved:** “The effect holds under that setup.” Read the antecedent before judging scope.

**Optional:** “It should be noted that the tests use different units.” The unit distinction must remain; shortening the lead-in is not a defensive hit.

**Defensive candidate:** “We humbly present measurements from two settings.” If “humbly” only evaluates authorial posture, “We present measurements from two settings” removes it without changing scope.

**Defensive candidate with protected content:** “We apologize for not offering a grand result. The experiment measured two conditions.” The apology may be unnecessary; the measured scope stays. A whole-sentence deletion still needs the focused check.

**Unsafe repair:** Replacing “may reflect several causes” with “reflects the cause” changes both uncertainty and multiplicity. Reject it regardless of fluency.

Examples are synthetic and supply no missing facts to a manuscript. Context can change a decision.

## Before returning a revision

Ask separately: Is the issue real? Does this repair remove it? Are all facts and uncertainty preserved? Is the quote verified against the current source? Are required deletion checks complete? If any required answer is unknown, do not present the edit as confirmed. Keep partial, optional, KEEP and unresolved out of the confirmed count.
