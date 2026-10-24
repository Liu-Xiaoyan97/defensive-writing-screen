# Jev request shapes

Every request is one `state` plus independent questions. Use Pi `jev_evaluate`, the TypeSafe `/v1/systemone` API, or any compatible System One caller. Probabilities are routing signals, never editing permission.

## State

One paragraph per request during adoption and whenever ambiguity is high:

```json
{
  "paragraph": {
    "text": "<exact paragraph, verbatim>",
    "location": "section 4.3, line 784"
  },
  "genre": "academic paper, English, methods section",
  "context": "reported metric direction and units; only facts supplied by the user",
  "rules": "<optional: applicable project or user rules>"
}
```

Keep state flat and short when asking about one span. Do not include the intended rewrite, a prejudged label, or invented evidence; each biases the judgment.

`jev_evaluate` returns a JSON string; parse it before reading values. Batched calls occasionally time out at higher concurrency: retry the unit, and report it as untriaged if the retry fails.

## Question set v2 (calibrated)

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
  "repeated_scope": {
    "type": "noul",
    "instructions": "Does `paragraph.text` state a scope limit, condition, or caveat twice, where the second statement adds no new restriction?",
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
| `repeated_scope` | the same caveat twice, caveat restating the previous sentence | repeated caveats; redundant clarification |

Low recall is expected on `repeated_scope` for paraphrase-level repetition: it scored 0.60-0.68 on real academic text where the repeated content was a prior obligation restated with new wording. Treat it as a soft signal and rely on `removal_preserves` for those units.

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

A high `true` means the span is a deletion *candidate*. The agent still decides, because `evidence` may be incomplete. Observed span values: 0.93 for a contrast clause that repeats a fact stated elsewhere, 0.72 for a vague weakening clause, 0.70 for a disclaimer whose content belongs in a setup section, 0.66 for a summary sentence restating earlier content, 0.60 for a duplicated scope reminder, and 0.39 for a harmless restatement that the agent kept. The question orders removable spans above harmless ones but does not separate removable from necessary wording on its own, so it never authorizes deletion.

## Routing

- `triage_probability = max(claim_negation, negative_contrast, vague_hedge, concessive_hedge)` per paragraph; sort descending. Keep `repeated_scope` and `removal_preserves` as separate columns.
- Review up to five units at or above `0.65`, plus every unit with a candidate span at `removal_preserves >= 0.65`.
- `0.65` is valid for v2 because the battery separates: positive controls 0.83-0.99, negative controls 0.002-0.017. It is not transferable to another question set, language, or model version without rerunning the battery.
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
