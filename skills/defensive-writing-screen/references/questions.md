# Jev request shapes

Every request is one `state` plus independent questions. Use Pi `jev_evaluate`, the TypeSafe `/v1/systemone` API, or any compatible System One caller. Probabilities are routing signals, never editing permission.

## State

One paragraph per request during adoption and whenever ambiguity is high:

```json
{
  "paragraph": {
    "text": "<exact paragraph, verbatim>",
    "location": "section 4.3"
  },
  "genre": "academic paper, English, methods section",
  "context": "reported metric direction and units; only facts supplied by the user",
  "rules": "<optional: applicable project or user rules>"
}
```

Keep state flat and short when asking about one span. Do not include the intended rewrite, a prejudged label, or invented evidence; each biases the judgment.

`jev_evaluate` returns a JSON string; parse it before reading values. Batched calls occasionally time out at higher concurrency: retry the unit, and report it as untriaged if the retry fails.

## Question set v3 (calibrated)

Version 3 keeps the four v2 questions and adds `scope_tail`, which routes a closing qualifier that withdraws a result without naming the condition that limits it. The extended battery passes: positives 0.844-0.991 on their designated dimensions, neutral controls at or below 0.145, and named-condition controls at or below 0.068.

Ask all five in one request for the paragraph. Each maps to a row of the detection checklist in `references/rewrite-guide.md`. Each asks what the text **contains**, not whether the text **deserves** to contain it.

Marker lists are language-specific and must be translated for the document at hand. The Chinese markers below were added after a batch of English-only anchors scored a mild Chinese modesty sentence at 0.375 and the same sentence reached 0.991 once Chinese markers were named.

```json
{
  "claim_negation": {
    "type": "noul",
    "instructions": "Does `paragraph.text` contain a sentence or clause stating a negation of a claim, that is, saying what the method, paper, model, or result does not do, does not claim, does not prove, does not provide, or does not include? Markers: do not claim, not intended to, should not be taken to mean; 并不声称、无意、不意味着、不应被理解为、不代表、不涉及、不能据此.",
    "criteria": {
      "true": "At least one sentence or clause explicitly negates a claim or capability",
      "false": "No sentence or clause explicitly negates a claim or capability"
    }
  },
  "negative_contrast": {
    "type": "noul",
    "instructions": "Does `paragraph.text` contain a 'not X but Y', 'rather than', 'instead of', or 'as opposed to' contrast used to redirect an expected reading? Markers: 并非…而是、不是…而是、与其说…不如说.",
    "criteria": {
      "true": "At least one such contrast construction is present",
      "false": "No such contrast construction is present"
    }
  },
  "vague_hedge": {
    "type": "noul",
    "instructions": "Does `paragraph.text` contain a vague weakening word or phrase that lowers the force of a statement without naming the source of uncertainty? Markers: could hardly, may potentially, to some extent, it should be noted, of course; 仅、只能、初步、难以、尚不能、仍有提升空间、在一定程度上、或许. Do not count an explicit prohibition or a required restriction, such as 不得、must not、cannot be used, or a condition that names the specific case it governs.",
    "criteria": {
      "true": "At least one such vague weakening expression is present and it is not a prohibition or a condition that names its case",
      "false": "No such weakening expression, or the negative wording is a prohibition or a named condition"
    }
  },
  "concessive_hedge": {
    "type": "noul",
    "instructions": "Does `paragraph.text` use a concessive construction that softens a claim or pre-frames a limitation instead of stating the result directly? Markers: although, while, however; 虽然、尽管、但、然而、仍.",
    "criteria": {
      "true": "At least one concessive construction softens a claim or pre-frames a limitation",
      "false": "No concessive construction is used to soften a claim"
    }
  },
  "scope_tail": {
    "type": "noul",
    "instructions": "Does `paragraph.text` append a qualifier to an already completed statement of a result, method, or check that retreats from it by pointing at the document's own conditions with a deictic word (markers: under this setup, under this setting, under the current training setup, in this setup, at the measured positions, at this stage, for now) instead of naming the condition, bound, or range? Do not count a qualifier that names its condition, such as a budget, a precision, a range, or an evaluation protocol. Do not count a qualifier that identifies which implementation, version, or configuration the statement describes, and do not count a prohibition or a stated failure mode.",
    "criteria": {
      "true": "At least one such retreating qualifier is present and it names no condition, bound, range, implementation, or version",
      "false": "No such qualifier, or the qualifier names its condition, implementation, or version"
    }
  },
  "repeated_scope": {
    "type": "noul",
    "instructions": "Agent-side only; do not route on this value. Does `paragraph.text` state a scope limit, condition, or caveat twice, where the second statement adds no new restriction?",
    "criteria": {
      "true": "A limit or caveat is stated twice within the unit",
      "false": "Each limit or caveat is stated once, or none is stated"
    }
  }
}
```

Dimension coverage, defined by these questions alone:

| dimension | catches | checklist rows |
|---|---|---|
| `claim_negation` | "We do not claim", "This paper does not attempt", "This is not to say", "This should not be taken to mean"; 并不声称、不意味着 | unnecessary disclaimers; repeated statements of what the text does not claim |
| `negative_contrast` | "not X but Y", "rather than", "instead of", "the goal is not X but Y"; 并非…而是 | unnecessary "not X but Y" structures; reflexive contrast |
| `vague_hedge` | "could hardly", "may potentially", "to some extent", "it is worth noting"; 仅、只能、初步、难以 | excessive hedging; apologetic framing |
| `concessive_hedge` | "although", "while", "however"; 虽然、尽管、但、然而、仍 | caveats in high-impact positions; limitation-first topic sentences |
| `scope_tail` | "under this setup", "at the measured positions", "for now"; 在该设置下、在当前实现中 | retreating tails; a result withdrawn by a deictic qualifier that names no condition |
| `repeated_scope` | the same caveat twice, caveat restating the previous sentence | repeated caveats; redundant clarification |

`repeated_scope` and a stricter `repeated_fact` variant were measured on a genuine restatement and did not separate it: 0.29 and 0.36, against 0.38 for a constructed redundant control and 0.34 for neutral prose. Paraphrase-level repetition therefore stays outside the routable classes and is assigned to the agent-side check in step 6. Do not lower the threshold to force it through; a threshold below the neutral baseline routes everything.

## Deprecated question set v1

Do not use. It asked whether the wording "adds no evidence, necessary scope, or useful distinction". Measured on the canonical positive controls, v1 returned 0.145-0.446, that is, below the 0.65 gate it was paired with. On an unidentified English academic draft it then returned no candidate at all (maximum 0.251), while v2 on the same draft returned 13 candidates, 5 of which the agent confirmed. Sufficiency questions are answered conservatively for academic prose, which compresses the scale instead of ranking it.

If a legacy run exists, do not salvage it with a lowered threshold. Re-screen with v2 and report the earlier run as invalid for lack of a passing battery.

## Focused span question

Use for every span returned by `scripts/prepare_units.py --candidates`, independently of the paragraph score. This is the recall backstop: an implementation contrast that scored 0.017 under v1 and 0.99 under v2 also needed this question to establish that removal preserved meaning.

```json
{
  "state": {
    "text": "<exact paragraph>",
    "span": "<verbatim substring of text>",
    "evidence": "<known facts and restrictions; say 'unknown' if none>"
  },
  "questions": {
    "removal_preserves": {
      "type": "noul",
      "instructions": "If `span` is removed from `text`, does the remaining text still accurately convey all facts and necessary restrictions in `evidence`?",
      "criteria": {
        "true": "Removal preserves every known fact, scope condition, and methodological limit in `evidence`",
        "false": "Removal loses a fact, scope condition, methodological limit, safety rule, or operational requirement"
      }
    }
  }
}
```

A high `true` means the span is a deletion *candidate*. A low value means the span carries something, so the options are keep or restructure, not delete. The agent still decides, because `evidence` may be incomplete. Observed span values: 0.93 for a contrast clause that repeats a fact stated elsewhere, 0.72 for a vague weakening clause, 0.70 for a disclaimer whose content belongs in a setup section, 0.66 for a summary sentence restating earlier content, 0.60 for a duplicated scope reminder, and 0.39 for a harmless restatement that the agent kept. The question orders removable spans above harmless ones but does not separate removable from necessary wording on its own, so it never authorizes deletion.

## Protection classes (P1-P6)

These are not verdict categories. They are the classes a span belongs to when removing
or restating it would change what a reader can verify, reproduce, or interpret. Apply
the test before any rewrite: a routed unit that belongs to one of them stays, and the
record names the class next to the keep category.

| id | class | test |
|---|---|---|
| P1 | Measured result | Would removal change a number, its sign, its direction, or the comparison it belongs to? Unfavorable results and metric direction belong here. |
| P2 | Mathematical or proof condition | Would removal drop a bound, a floor, an identity case, an assumption, or the scope within which a proof holds? |
| P3 | Measurement or reproduction condition | Would removal drop the corpus, tokenizer, budget, context length, precision, protocol, implementation path, or configuration that a reader needs to reproduce or interpret the number? |
| P4 | Scope of an intervention or check | Would removal drop what was varied, what was held fixed, what the check covered, or what it did not isolate? |
| P5 | Design premise or motivation | Would removal drop the reason a component exists, the problem it answers, or the baseline the design is measured against? |
| P6 | Comparison semantics | Would removal turn a ranked comparison into a spread, or change a per-item difference into a summary that hides it? |

A high Jev probability never overrides a protection class. The two measured failures that
created this section are representatives of the class: a metric-semantics sentence about
what an activated count does and does not measure routed at 0.946, and an unfavorable
per-task comparison routed at 0.897. Both stay.

## Structural findings (S1-S4)

Document-level, from `scripts/check_structure.py`. They are reported next to the unit
record, never as a unit verdict, and each states whether the genre requires the role.

| id | finding | note |
|---|---|---|
| S1 | No conclusion-like section | A paper's closing section should restate what was solved, proposed, and shown. |
| S2 | Document ends on limitations | The last section a reader meets is a withdrawal rather than the takeaway. |
| S3 | No limitations statement | Required when the draft makes claims whose scope is not bounded in the sections themselves. |
| S4 | Related work absent or folded into the introduction | Often legitimate; report where the prior-work discussion sits. |

A supplement, appendix, extended abstract, letter, or proposal carries a different set.
Say which absences the genre allows instead of reporting them as defects.

## Verdict categories

Every unit gets one verdict. A rewrite cites one rule and may carry narrative actions, recorded together as `R6+N3`; a narrative action on its own cites one action id; a keep cites one category, plus its protection class when the unit was routed, as in `K5+P3`. Each list is closed so that two readers can compare their records.

Rewrite rules:

| id | rule |
|---|---|
| R1 | A difficulty word or vague qualifier with no stated bound, range, degree, or governing condition. |
| R2 | A concessive frame that puts the limitation and the conclusion in one sentence, so the conclusion only appears after a turn. |
| R3 | An explicit statement of what the work does not claim, prove, or address, carrying no method, data, or scope information. |
| R4 | A not-A-but-B contrast used to pre-empt a misreading, where the contrast carries no argument or distinction. |
| R5 | The same limit, scope, or fact stated twice in one unit about the same object, the second occurrence adding nothing. A sentence that transfers a bound to a new object adds information and is K5, not R5. |
| R6 | A closing qualifier that retreats from a completed statement by pointing at the document's own conditions with a deictic word, without naming the condition, bound, or range that limits it. The qualifier goes; the actual condition replaces it when the paragraph supports one. A qualifier that names its condition, precision, protocol, implementation, or version is K4 or K5, and a qualifier whose removal would drop the fact of what the statement covered is K5, not R6. |

Keep categories:

| id | category |
|---|---|
| K1 | Definition, notation, formula, or symbol explanation. |
| K2 | Reported number, metric direction, per-item difference, or analysis setup. |
| K3 | Conditional baseline describing the object that the design improves on. |
| K4 | Constraint naming its object and its failure mode or bound. |
| K5 | Causal limit, safety prohibition, scope of application, methodological premise. |
| K6 | Contrast that distinguishes mechanisms, notation, or settings. |
| K7 | Caption, table lead-in, reference list, or section roadmap. |

A keep record carries the category and, in one short clause, what makes the unit
that category. Without that clause the record shows a label, not a judgment.

## Narrative actions (agent-side, not routed)

No question in the set detects these. They are judgments about framing and placement,
not about observable wording, so like the repetition check they are found by reading
every unit. Every action keeps each fact, number, metric direction, condition, and
prohibition; an action that would remove one is not available and the unit stays.

| id | action | entry condition | what may change |
|---|---|---|---|
| N1 | RESTATE | A unit demotes its own result behind a retreat or a subordinate clause while a stronger fact it already reports sits in the main clause, or the reverse. | Clause order and emphasis. Same numbers, same direction, same comparison. |
| N2 | NARROW | A claim covers more than the unit's evidence: a range wider than what was measured, a population wider than what was sampled, or a comparison the unit does not support. | The claim shrinks to the measured scope. The numbers it already reports stay. |
| N3 | RELOCATE | A fact, control condition, or caveat sits where it interrupts the unit's job, or the same fact is stated in more than one section. | The fact moves or is consolidated, exactly one statement remains, and the receiving location is named in the record. |

Boundaries:

- N1 may not convert a deficit into a match. "The estimate is 0.7 points below the
  baseline while using 12% of its steps" may become "Using 12% of its steps, the
  estimate comes within 0.7 points of the baseline", never "the estimate matches the
  baseline".
- N1 may not replace a ranked comparison with a spread that hides its direction.
  Reporting that a value falls inside a distribution is a restatement only when the
  distribution is also compared, not when it replaces the comparison.
- N2 may not drop an unfavorable number, and may not narrow a claim past the evidence
  in order to avoid a comparison the unit already makes.
- N3 may not lose a fact. The receiving location must exist in the draft and must be
  named, and the record must say which section keeps it.
- None of the three may change a metric direction, a unit, a condition, a prohibition,
  or the identity of the objects being compared.

A narrative action is not a reward for a weak result. When the unit's evidence does not
support any framing that reads better, the verdict is keep with a K category.

## Tail calibration (question set v3)

Measured on constructed controls, one paragraph per request. The positive appends a deictic qualifier to a finished result; the negatives name the condition instead.

| id | text | `scope_tail` | expected agent decision |
|---|---|---:|---|
| `pos_scope_tail` | The intervention lowers the measured error by 4.5 points under this setup. | 0.968 | rewrite; name the condition or drop the tail |
| `tail_named_budget` | The intervention lowers the measured error by 4.5 points at the 2B-step budget. | 0.008 | keep; the qualifier names its condition |
| `tail_named_protocol` | The check confirms that the two paths agree within 1e-5 at every readout record. | 0.014 | keep; the qualifier names the coverage |
| `tail_named_scope` | The intervention measures the contribution of the full path, not its components. | 0.068 | keep; removal would drop what the intervention covered |
| `tail_impl` | Both subsystems use the same scan in the current implementation. | 0.213 | keep as scope, but the value sits above the 0.20 control bound, so implementation qualifiers need an agent decision |

The class is narrow on purpose. A second measured positive, "The comparison supports the benefit of the additional term under the current training setup", scored 0.809, and "The check confirms agreement at the measured positions" scored 0.979, so the question reads the deictic pattern rather than one fixed phrase. Values move with the model version; re-measure before relying on the gate.

## Routing

- `triage_probability = max(claim_negation, negative_contrast, vague_hedge, concessive_hedge, scope_tail)` per paragraph; sort descending. Keep `repeated_scope` and `removal_preserves` as separate columns.
- Review up to five units at or above `0.65`, plus every unit with a candidate span at `removal_preserves >= 0.65`.
- `0.65` is valid for v3 because the battery separates: positive controls 0.844-0.991, negative controls at or below 0.145, and named-condition tail controls at or below 0.068. It is not transferable to another question set, language, or model version without rerunning the battery.
- Language anchors move recall by large margins. English-only markers left a mild Chinese modesty sentence at 0.375; naming Chinese markers moved the same sentence to 0.991. Run the battery in the document's language before trusting either number.
- Candidate precision is low by design. In the calibration screening, 5 of 13 candidates were confirmed; every reject was a notation distinction, a mechanism contrast, a setup fact, or a necessary scope statement. Report both counts. In a method-heavy draft, conditional baselines ("if only a single value were used", 若仅采用) account for most rejects; they describe the problem class and stay.
- Never convert a probability into a deletion without agent evidence. A probability near 0.5 means the model splits yes and no, not that the wording is half-defensive.
- Keep this file free of project content. Control sentences are the generic defensive patterns bundled in `references/cases.md`; screening statistics are aggregates without document identity, domain vocabulary, or draft excerpts. Project cases stay in the project and arrive as state at run time.

## Batching and cost

- Batch the five questions for one paragraph in a single call: they run in parallel and cost little. Long CJK units can exceed a 10 s request timeout on a four- or five-question call; split such a unit into two calls rather than dropping it.
- Do not batch different paragraphs until a measured run shows no recall loss and no target confusion. Path-based references (`paragraphs[2].text`) are the failure point.
- One retry on timeout; report the unit as untriaged if it still fails.
- Record model name and version with results. Default `jev-evaluate` runs used `jev-latest`; behavior changes across versions.
- CJK is slower and scores lower than English on English-only wording. Name CJK markers in the `instructions`, calibrate separately, expect request timeouts on long units, and keep the human verification step.

## Calibration

Run the six controls in `references/cases.md` before screening a document. Then build a labeled set of 30-60 paragraphs per genre and language, covering: clearly defensive, necessary limitation, safety or legal prohibition, technical condition, conceptual contrast, and neutral prose. Record `triage_probability`, `removal_preserves`, agent decision, and final outcome. Choose the threshold from the observed trade-off between misses and review volume, and keep the set in `references/cases.md` style so it can be rerun after model or question changes.
