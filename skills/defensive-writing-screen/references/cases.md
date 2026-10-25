# Control battery and review regression boundaries

This file must not carry project content, document identity, domain-specific excerpts or document-level findings. Runtime reports stay outside the skill. The cases in `controls.json` are generic synthetic examples. They do not establish deployment accuracy.

## Control battery

The four observable questions, six routing controls and thresholds are unchanged from v4. Four construction positives must reach 0.65 on the designated dimension; two neutral negatives must stay <=0.20 on every dimension. A failed gate blocks document triage and requires explicitly reported agent-only review. Missing values stay null.

A necessary scope statement can be a construction positive. This gate says whether the caller recognizes the specified wording, not whether the wording is defective. Semantic hard negatives must not be relabelled as routing negatives to force a desirable score.

`validation_controls` are frozen regression cases. Once inspected or used to change a rule, they are not unseen validation. Do not tune a live audit to pass them.

## Review2 changes

The previous semantic cases gave the same ordinary benefit/drawback comparison both KEEP/optional and confirmed labels. That contradiction is removed. The single protected-comparison case now stays KEEP/optional. A distinct effort-assurance example tests actual rhetorical defense.

The old rule “a fact-preserving concession rewrite is confirmed” is withdrawn. Two independent tests now apply:
1. There is an unnecessary rhetorical defense beyond facts and necessary restrictions.
2. The repair removes it while preserving facts, modal strength and degree.

A failed second test is partial, not confirmed. Merely swapping a connector or splitting sentences is optional when no independent defect exists. Correct KEEP decisions are never included in the false-positive denominator.

## Revision 0.29.0 review protocol

The r12 full review found that candidate discovery alone did not ensure precise KEEP decisions, and an issue candidate was present in the adjudication ledger but absent from the findings list. Revision 0.29.0 makes the existing proposition/evidence KEEP test explicit in every Pass B reason and adds optional bidirectional candidate/finding linkage validation. It does not change the issue threshold, categories, or protected-content rules. This is a testable process hypothesis, not a measured accuracy improvement. Compare exact source/rules/model, parent-adjudicated issues, false alarms, missed labels, accepted repairs, cost and review consistency before claiming benefit.

## Revision 0.28.0 review protocol

The r11 full review met coverage but regressed in parent-adjudicated findings relative to r9. Several candidates were found and then given a plausible KEEP rationale; a later retry also differed from the first review on an anchored finding. The 0.28.0 workflow separates discovery from adjudication for full reviews. Pass A lists candidate spans without verdicts. Pass B uses a separate reviewer context, rereads every target, evaluates the candidates, and may add missed candidates. This aims to reduce anchoring and discovery/adjudication interference. It is a testable workflow hypothesis, not a measured improvement. Keep source, rules, model and labels frozen; compare yield, KEEP quality, cost and review variance before claiming benefit.

## Revision 0.27.0 decision checks

The 0.26.0 development replay found that several misses were not candidate-discovery failures: the reviewer found the wording but treated a related nearby fact as sufficient KEEP support. Others involved interpretations of mixed metrics, subgroup uncertainty, or assigned responsibility. The added cases in `controls.json` require the reviewer to compare the candidate's proposition with the evidence proposition, while retaining paired hard negatives for real subgroup boundaries, mixed-result interpretation, matched prior evidence, and concrete design costs.

These cases do not turn historical misses into automatic positives. A candidate still needs a demonstrable defensive function. If the source cannot establish the relation between evidence and interpretation, keep the original modal force and record the evidence question separately. A benchmark-alignment label is not a semantic verdict.

## Required semantic regression classes

Read `semantic_challenges` and `hard_negatives` in the canonical JSON. They cover:
- resolved references to tested conditions and coverage;
- an unknown antecedent that must not be deleted;
- an explicit rhetorical retreat or effort assurance;
- protected unfavorable results and meaningful tradeoffs;
- comparisons with numbers located elsewhere;
- useful interpretations, contribution attribution and method definitions;
- multiple independent rhetorical spans in a paragraph;
- necessary causal, statistical and safety boundaries;
- degree/modal preservation in both directions;
- ordinary compression and metadiscourse, excluded from detection.

Cases can include both protected information and an unnecessary rhetorical fragment. An entire paragraph must not be protected or condemned because of one phrase.

## Offline regression checks

Repository tests check source snapshots and LF anchors, nontruncating packets, all sentence hits with exact parent offsets, complete contextual delivery, deterministic sampling without route overlap, failed-call visibility, duplicate IDs and stale hashes. They also check two-stage record consistency, deletion gates, KEEP/optional isolation, and contradictory duplicate semantic labels.

These are software and specification checks. They do not prove that an LLM will follow the specification, nor that a supplied semantic assertion is true. `verify_findings.py` verifies source anchors and declarations, not entailment. A passing unit test is not a measured improvement in writing judgment.

## Historical observations

`scope_tail` was retired after a neutral sentence-initial condition scored 0.709782 above its 0.20 ceiling. A positional clarification reduced that negative to 0.016584 but also reduced the old positive from 0.985961 to 0.303647, below the 0.65 floor. Both gates failed. The isolated tail lacked context; do not revive it by lowering the threshold.

Earlier observable questions separated some construction controls better than sufficiency questions. This supported observable routing, not semantic defect classification. English controls did not establish general Chinese performance. Repetition likewise remained an agent judgment.

A historical script/tool comparison routed the same eight units out of 119, with score differences of about 0.04. A separate four-slot endpoint test did not become faster with eight or twelve workers. These are endpoint-specific observations. Record current actual workers, retries, model and elapsed time rather than assuming linear speedup.

## Sampling and optional finer screening

The default is paragraph routing plus 12 evenly spaced non-routed units. The old implementation also used interval selection, not random sampling. The new sampler includes endpoints when possible and avoids already-selected units. This is a document-order miss check, not a probability sample or population recall estimator.

Full sentence screening is optional. Finer units can expose a problem hidden by paragraph aggregation, but their benefit is not assumed. Every sentence carries its parent and neighbors, and the packet keeps all hits. Whole units are never cut to a character budget. Measure the extra confirmed issues, safe repairs and reading cost before claiming that the finer pass helps.

## What the numbers mean

- Routing score: priority for inspection, not a defect label or editing permission.
- Packet coverage: selected/delivered units, not verified reading or recall.
- Agent positive yield: issue assertions among routed units, not independently verified precision.
- Confirmed: a contextual issue with an accepted repair; partial: an issue with no accepted repair.
- KEEP and optional: separate decisions, not positive alarms. Unresolved remains unknown.
- Recall: requires independently labelled issues in a defined reviewed population. A few sampled misses cannot estimate full-document recall.
- Blind evaluation: remove identities, versions, scores and tool-specific headers. A randomized label alone does not make a packet anonymous.

Keep development, regression and unseen evaluation sets distinct. Freeze source, skill, model and decision rules when comparing versions. A single judge's disagreement across runs does not establish a noise interval or statistical significance. Report software checks, observed benchmark results and untested claims separately.

## Revision 0.30.0 posture-versus-scope test

Revision 0.30.0 adds one rule to the decision boundary: a protected fact does not exempt an attached authorial posture. It was derived from a development-set experiment, not from the papers in question.

The experiment used a sentence-level screening task with a paper-level split, labels produced by blind annotation and then audited by an independent reviewer, and three repeated runs per rule version aggregated by unanimous vote. Two labels were missed by every run because the local text contained a number and a citation respectively, and both were used to retain the whole sentence. The added rule separates the factual part from the posture part and forbids the number, citation, scope limit or meaningful concession from exempting the posture. With that rule the training split reached full recall and a unanimous-vote F1 of 0.900; the untouched validation split reached 0.700.

The same validation split also showed the cost: four false positives survived unanimous voting and three of them were factual statements with a hedged qualifier that the new rule treated as posture. A later attempt to distinguish scope from posture by an abstract criterion, without any example, lowered training F1 to 0.800 and was discarded. Treat the rule as a candidate improvement with a known failure mode, not as a measured gain. Re-measure on data that never informed the rule before claiming benefit.
