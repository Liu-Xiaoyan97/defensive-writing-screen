# Jev request shapes and judgment contract

## Question set v4

`controls.json` is the single machine-readable source for the four active questions, six gate controls, thresholds and semantic challenge cases. Read it rather than reconstructing prompts from examples. v4 preserves the four observable questions from v3. It retires `scope_tail` from default routing after failures on neutral and positive controls; it does not claim the tail classifier is repaired. `repeated_scope` and `repeated_fact` also remain agent-side only. Report the active question revision with every run.

The four dimensions detect observable wording, not defective writing:

| dimension | observable construction |
|---|---|
| claim_negation | Negation of a claim, capability or coverage. Necessary limits can route high. |
| negative_contrast | Explicit not-X-but-Y or equivalent contrasts. Meaningful contrasts stay. |
| vague_hedge | Weakening language without a named source of uncertainty. |
| concessive_hedge | Concession framing that subordinates a result or pre-frames a limitation. |

English and Chinese markers are included in the canonical questions, but the gate controls are English. An English pass is not Chinese calibration. For another language, prepare a separately identified matched-language variant and control set before the audit.

## State

One paragraph per request; include local context so backward references can be resolved. Do not insert a proposed rewrite, desired verdict or invented evidence.

```json
{
  "paragraph": {"text": "<exact unit text>", "location": "<line range>"},
  "genre": "academic paper, English",
  "context": "<nearby conditions needed to interpret this unit; unknown if absent>",
  "rules": "Preserve facts, metric direction, mathematical conditions, intervention scope, and necessary uncertainty."
}
```

For controls use this same shape, `location: control battery`, and `context: Only facts stated in this paragraph are supplied.` Send all four canonical questions in the same call. Parse the returned JSON string and retain raw responses. Record requested model alias separately from any resolved model returned; absent metadata means unknown, not an inferred fixed version.

## Control gate and failure handling

Run every row in `controls.json.controls`, one request per row. All four positives must score >=0.65 on their designated dimension; each of the two neutrals must score <=0.20 on all active dimensions. Preserve every value, not just maxima. Do not change controls, labels, thresholds or prompts during an audit. Retry a transport failure once, not a low/high score.

A completed failing gate blocks draft Jev calls and triggers `agent-only diagnostic review`. A persistent service error triggers the same mode with a different reason. No caller also permits that mode. Continue the complete agent review with null draft probabilities and the appropriate `untriaged_*` state. This is not a successful Jev pipeline.

`validation_controls` is a separate frozen regression set: run it only after freezing a candidate revision. It is not included among prompt examples, not a basis for adjusting the current audit, and not a substitute for a larger independent labelled set. Once inspected it is a regression set, not a perpetually unseen test. Report failures; do not silently omit them.

Read `semantic_challenges` to check the agent rules: protected facts can be reframed, necessary backward references stay, incomplete context does not license deletion, and independent spans need independent records. These expected decisions are not classifier-negative labels. Necessary scope may have high observable scores.

## Focused span question

For deterministic candidates and proposed deletions in Jev mode, issue this separately. Supply the full paragraph plus known facts and the antecedent of any reference. Do not declare evidence complete when it is not.

```json
{
  "state": {
    "text": "<exact paragraph and necessary context>",
    "span": "<exact substring>",
    "evidence": "<known facts and necessary restrictions; unknown when unavailable>"
  },
  "questions": {
    "removal_preserves": {
      "type": "noul",
      "instructions": "If `span` is removed from `text`, does the remaining text still accurately convey all facts and necessary restrictions in `evidence`?",
      "criteria": {
        "true": "Removal preserves every known fact, scope condition, and methodological limit in evidence",
        "false": "Removal loses a fact, scope condition, methodological limit, safety rule, or operational requirement"
      }
    }
  }
}
```

A high value is only a deletion candidate. Low values veto deletion, not equivalent restructuring. Agent-only suggestions carry no Jev validation. Do not assign zero to a missing focused judgment.

## Protection classes (P1–P6)

Protection attaches to meaning at span level, not to exact wording or an entire paragraph. A revision is allowed only if every protected fact survives. Meaning-preserving reframing and deletion are different operations.

| id | protected content |
|---|---|
| P1 | Measured results, metric directions, uncertainties and unfavorable outcomes, whether numbers are local or clearly referenced. |
| P2 | Mathematical/proof assumptions, bounds, floors and identity cases. |
| P3 | Measurement/reproduction conditions, protocol, corpus, budget, precision, configuration or version. |
| P4 | What an intervention or check covered, varied, held fixed or failed to isolate. |
| P5 | Design premise, meaningful baseline or reason a component exists. |
| P6 | Objects and semantics of a ranked comparison, including sign and magnitude where given. |

A direction-only comparison is not automatically R1. Do not add redundant numbers just to make it eligible for protection. Conversely, preserve an unfavorable comparison while considering a less apologetic sentence frame. Resolve scope references through context before calling them empty. Unknown context yields keep/unresolved, never a manufactured condition.

## Verdict categories

Every read unit has one summary verdict (`keep`, `rewrite`, `narrative`, `mixed`, or `unresolved`) and zero or more independent span findings. One unit may carry several R rules on different spans, including combinations of rewrites and keeps. Each finding needs an ID, exact span, rule/action, reason, protection classes, proposal and disposition (`confirmed`, `optional`, `keep`, `unresolved`). Count findings and units separately.

### Disposition test

| disposition | test |
|---|---|
| `confirmed` | The bundled guide lists the construction as a rewrite rule, every fact and condition survives the revision, and the current wording weakens a supported claim, a supported unfavorable result, or the reader's access to the result through framing rather than content. |
| `optional` | The text is not defensive; the change is presentation only: restating a condition the paragraph already makes clear, importing numbers that already appear in a table, merging or splitting sentences, reordering material. |
| `keep` | The span carries a protection class, a functional contrast, a resolved reference, or a result whose framing does not need to change. |
| `unresolved` | The evidence or context needed to decide is missing. |

A concession whose favorable and unfavorable facts both survive is `confirmed`: the facts are protected, the frame is not. Treating such a case as `optional` understates a real finding, and a run reporting zero confirmed findings while routing concession units needs that discrepancy explained rather than left as a total.

## Review scope and cost accounting

Choose one scope before reading and report it with the result.

| scope | reads | when |
|---|---|---|
| `screened` | All routed units, all focused candidates, the 0.45-0.65 band when small, plus a stratified sample of the rest: everything when 20 or fewer, otherwise at least 20 spread across the document. The response carries routed rows and a sample summary; the full table goes to an artifact. | Default when Jev passed the gate and the goal is triage. |
| `full` | Every unit. | Publication acceptance, exhaustive requests, or any agent-only run. |

In `screened` mode, count misses found in the sampled unread population and report `misses/sample`, never a recall claim. Unsampled units are reported as unread, not as clean. A Jev-first run that also reads every unit cannot save agent work by construction, so report scope before discussing cost.

Record measured cost facts: review scope, units read, units sampled, units unread, Jev requests with retries and failures, and agent turns or tokens when the caller exposes them.

Record only risk-bearing results. The response carries: the gate table, every finding with its span, one line per routed unit, one aggregate line per sampling group, structure observations, and cost facts. A read unit with no finding contributes only to the aggregate count; a finding at any score is recorded. This keeps the audit trail where it matters and drops the row-per-unit ledger that dominated cost.

Recording dominates cost in measured runs: a screened run that read 34 of 118 units still produced more agent output than an agent-only full read, because the response inlined a 119-row probability table. Put the full table in a file artifact, keep one row per routed unit plus one aggregate line for the sample in the response, and treat the response length as a cost to report rather than proof of thoroughness. Do not claim that Jev-first review is cheaper than agent-only review without a measured comparison on the same draft. Quality and cost are separate results; a cheaper run that misses a confirmed finding is not a better run.

| id | rewrite rule |
|---|---|
| R1 | Vague weakening with no evidential role; not a clear comparison merely lacking repeated numbers. |
| R2 | Concession or self-undermining emphasis that can be restated while preserving both favorable and unfavorable facts. |
| R3 | Empty disclaimer carrying no method, evidence or necessary scope. |
| R4 | Empty contrast carrying no conceptual distinction or argument. |
| R5 | Redundant fact/limit with no new restriction, navigation or inferential role. |
| R6 | Genuinely empty retreat after a complete statement: no necessary uncertainty, scope or useful contextual reference would be lost. |

R6 does not fire merely on `under these conditions`, `in this setup`, or a reference to tested locations. If an antecedent establishes scope, retain the concise reference or offer equivalent wording as optional style. Do not replace a multi-condition setup by only its budget. Sentence-initial conditions are not appended retreating tails. Missing context is uncertainty, not evidence that a qualifier is meaningless.

Keep categories: K1 definition/notation; K2 reported result; K3 conditional baseline; K4 constraint; K5 necessary scope; K6 meaningful contrast; K7 caption/roadmap/reference. A keep needs a concrete reason, not just a category label.

## Narrative actions

| id | action | boundary |
|---|---|---|
| N1 | Restate emphasis | Preserve both sides, rank, numbers and uncertainty; a deficit never becomes a match. |
| N2 | Narrow an unsupported claim | Retain supported interpretations. Arithmetic explanation is not defective just because its inputs are already reported. |
| N3 | Relocate/consolidate | Name the receiving location and preserve every necessary fact and condition. |

Do not interpret an unfavorable result as a global defect. Do not remove an interpretation that helps explain a reported aggregate merely to avoid discussing gaps. When no better evidence-preserving framing exists, keep the text. Optional improvements are not confirmed defects.

## Structural findings (S1–S6)

| id | observation | decision boundary |
|---|---|---|
| S1 | No conclusion-like section | Check genre/venue and existing closing paragraphs. |
| S2 | Ends on limitations | Report the ordering; not automatically wrong or a reason to suppress limitations. |
| S3 | No necessary scope statement | Scope may already be stated with each claim. |
| S4 | Related work absent/folded | Integration with the introduction can be legitimate. |
| S5 | Evidence distant from its claim | Propose moving it only if a concrete reading problem is shown. |
| S6 | Redundant implementation detail in a review | Legitimate research positioning or a transition to the present work can stay. |

These are document-level observations, not additional span defects. Mechanism evidence need not have one mandatory section order. Never delete accurate conditions to make a section end on a stronger note.

## Tail calibration history

v3 used five routing dimensions. A subsequent rerun returned 0.709782 for a neutral sentence-initial condition on `scope_tail` (negative ceiling 0.20). A single positional-prompt revision reduced that negative to 0.016584 but reduced the old positive from 0.985961 to 0.303647 (positive floor 0.65). Calls succeeded; classification failed. No draft probabilities were produced by that blocked run.

These observations motivate retiring the dimension, not declaring a lower threshold valid. The old isolated tail positive lacks its antecedent; under current agent rules it is keep/unresolved until context establishes whether the qualifier matters. This is an explicit semantic change, not a relabelled success for the v3 classifier. Other dimensions and their neutral controls remain unchanged.

## Routing and records

- Maximum of exactly the four active probabilities; review all >=0.65 plus focused candidates and then every remaining unit. No top-five cap.
- Missing or failed calls remain null and untriaged. A valid below-threshold score is `not_selected`, never `clean`.
- The merge script accepts canonical or legacy short keys, preserves findings, and distinguishes incomplete screening from low scores.
- Routing precision is confirmed rewrite units among actually routed units, divided by routed units. It is not all rewrites divided by routed units. Report span counts separately.
- Agreement and recall require an independently produced label set with matched units and scope. Do not call another agent's opinion ground truth.
- Gate validity is run-specific; one tiny passing set does not establish general accuracy, multilingual performance, or cost savings.
