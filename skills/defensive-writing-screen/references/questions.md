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
  "genre": "academic paper, Chinese, experimental section",
  "context": "validation loss, lower is better; only facts supplied by the user",
  "rules": "<optional: applicable project or user rules>"
}
```

Keep state flat and short when asking about one span. Do not include the intended rewrite, a prejudged label, or invented evidence; each biases the judgment.

## Broad triage questions

Ask all of these in one request for the paragraph. Keep `instructions` free of question IDs, which Jev cannot see.

```json
{
  "self": {
    "type": "noul",
    "instructions": "Does `paragraph.text` contain vague self-deprecation or an apology-like appraisal that adds no concrete fact or necessary scope?",
    "criteria": {
      "true": "The wording undermines the work without conveying a checkable fact, constraint, or scope",
      "false": "No such wording, or the wording states a specific necessary constraint"
    }
  },
  "preemptive": {
    "type": "noul",
    "instructions": "Does `paragraph.text` preempt an imagined objection with an unnecessary disclaimer or a reflexive negative contrast?",
    "criteria": {
      "true": "The disclaimer or contrast adds no evidence, necessary scope, or useful distinction",
      "false": "No such framing, or a real restriction or distinction is expressed"
    }
  },
  "hedging": {
    "type": "noul",
    "instructions": "Does `paragraph.text` stack hedges, duplicate caveats, or repeat limitations beyond what the evidence requires?",
    "criteria": {
      "true": "Uncertainty is repeated or inflated without adding precision",
      "false": "Uncertainty and limitations are proportionate to the evidence and stated once"
    }
  }
}
```

## Focused span question

Use only when a deterministic search (`scripts/prepare_units.py --candidates`) or the user supplies an exact substring. Ambiguous Chinese wording can score low on broad questions, so this focused request is the recall backstop.

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
      "instructions": "If `span` is removed from `text`, does the remaining text still convey all facts and necessary restrictions in `evidence`?",
      "criteria": {
        "true": "Every known fact and necessary restriction survives the removal",
        "false": "Removal loses a fact, scope condition, methodological limit, safety rule, or operational requirement"
      }
    }
  }
}
```

A high `true` means the span is a deletion *candidate*. The agent still decides, because `evidence` may be incomplete.

## Routing

- `triage_probability = max(all noul values)` per paragraph; sort descending.
- Start at `0.65`, review at most five units, then tune on labeled data.
- Two questions measure different things: `self` scores weak; `removal_preserves` scores near 0.7 for both removable and necessary wording in some Chinese cases. Treat a `removal_preserves >= 0.65` as "look here", and require agent verification of every candidate.
- When `removal_preserves` is high but `evidence` is thin, collect the missing facts before rewriting.
- Never convert a probability into a deletion without agent evidence. A probability near 0.5 means the model splits yes and no, not that the wording is half-defensive.

## Batching and cost

- Batch the broad questions for one paragraph in a single call: they run in parallel and cost little.
- Do not batch different paragraphs until a measured run shows no recall loss and no target confusion. Path-based references (`paragraphs[2].text`) are the failure point.
- One retry on timeout; report the unit as untriaged if it still fails.
- Record model name and version with results. Default `jev-evaluate` runs used `jev-latest`; behavior changes across versions.
- CJK accuracy is lower than English. Calibrate separately and keep the human verification step.

## Calibration

Build a labeled set of 30-60 paragraphs per genre and language, covering: clearly defensive, clearly necessary limitation, safety or legal prohibition, technical condition, and neutral prose. Record `triage_probability`, agent decision, and final outcome. Choose the threshold from the observed trade-off between misses and review volume, and keep the set in `references/cases.md` style so it can be rerun after model or question changes.
