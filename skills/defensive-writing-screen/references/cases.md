# Control battery, semantic cases, and calibration boundaries

This file must not carry project content, document identity, domain-specific excerpts or document-level findings. Keep runtime reports outside the skill. Values below are historical observations, not current guarantees.

## Control battery v4

The canonical questions and control texts live only in `controls.json`. Run every row of `controls` (four positives, two neutrals: six total) using the four listed active dimensions. Positive designated scores must be >=0.65, and every neutral dimension <=0.20. Report all values. No prompt, label or threshold changes inside an audit. A failed gate switches to an explicitly marked agent-only diagnostic review with null probabilities.

The old seventh control tested `scope_tail`. That dimension is retired from default routing, not silently passed or assigned zero. Its original isolated sentence is retained in `semantic_challenges` as keep/unresolved without an antecedent. The four other questions and six remaining gate controls retain their wording. This is an explicit change in scope and interpretation, not evidence that the old five-question detector now works.

`validation_controls` provides separate frozen texts. Inspect their results only after freezing a revision, report failures, and do not tune the current audit to them. Once inspected, call them regression cases, not unseen validation. A larger independently labelled set is still required before general accuracy claims.

## Semantic challenge cases

Read every `semantic_challenges` entry before reviewing the document. These test agent reasoning, not Jev routing. A necessary contrast or limitation may legitimately score high on an observable dimension.

The current cases cover:
- A reference to conditions already specified: retain the reference, rather than repeating the complete setup.
- A reference to a clearly stated test range: preserve coverage, not an unlimited claim.
- An isolated deictic qualifier with missing context: keep/unresolved, never assume it is meaningless.
- An explicitly rhetorical retreat: remove the retreat while retaining the result.
- A protected unfavorable result in a concessive frame: optional equivalent reframing, not deletion.
- A direction-only comparison: keep without requiring duplicated table values.
- A useful explanation of an aggregate: keep unless unsupported or genuinely redundant.
- Two independent problem spans within one paragraph: record both.
- A review-to-research transition: legitimate positioning, not an automatic structure defect.

These cases replace prior rules that treated all deictic tails, direction-only comparisons or arithmetic interpretations as rewrite targets. Do not import those old labels into the current run.

## Historical classifier observations

### v3 tail failure

One earlier served endpoint reported `StartLux-Decision-v1.1-4B-AutoThink`; later requests used `jev-latest` without a resolved fixed version. Values are not interchangeable across those endpoints.

A later rerun of seven five-dimensional controls returned:

| control | original scope_tail | one positional clarification |
|---|---:|---:|
| Sentence-initial condition with two numeric estimates | 0.709782 (negative gate failed) | 0.016584 |
| Finished result followed by “under this setup” | 0.985961 | 0.303647 (positive gate failed) |

All service calls returned normally. Both complete gates failed, so no document screening followed. v4 moves tail interpretation to the agent rather than lowering a threshold or repeatedly adjusting the question. No current full-document precision/recall follows from these control measurements.

### Earlier v1/v2 and language observations

- Broad sufficiency questions scored several defensive controls below their own 0.65 route threshold. Observable questions improved separation in those historical runs.
- English-only markers missed mild Chinese self-undermining wording; bilingual markers improved one observed case. This does not validate all Chinese genres.
- Repetition questions scored a deliberately repeated statement about 0.38 versus 0.34 for neutral prose. Repetition remains an agent task.
- A low deletion-preservation score can correctly identify that a span carries a fact. It does not veto an equivalent rewrite that preserves the fact.
- Multi-paragraph requests can confuse target attribution. Prefer one unit per call.

## Concurrency and handoff size

Units were screened at four, eight and twelve pool workers on the same draft and question set against a four-slot endpoint. Results were identical in routing and wall time stayed between 55 and 58 seconds, which is the service limit rather than a client bottleneck. On a sixty-four-slot endpoint the same work finishes in seconds, so the pool size must track the served limit and be recorded with every measurement. Record retries as well: the service returned intermittent 502s under load.

The handoff packet for that draft contained 8 high-risk units and 6 sampled units in 71 lines. The agent judged the packet instead of the document, so its reading shrank to the routed units while the machine record stayed in the script output.

## Script path versus tool path

The same environment was measured twice: once through per-unit agent tool calls and once through `scripts/run_screen.py` with concurrency four. Both used the same questions, controls and thresholds.

| path | calls | wall time | resolved model | routed units at 0.65 |
|---|---|---:|---|---:|
| individual tool calls | 131 | minutes, interleaved with agent turns | not returned | 8 |
| script, thread pool, concurrency four | 119 triage calls | about 57 s | StartLux-Decision-v1.1-4B-AutoThink | 8 |
| script, process pool claiming units | 119 triage calls | about 55 s | StartLux-Decision-v1.1-4B-AutoThink | 8 |

Routing agreed on the same eight units. Individual values differed by up to about 0.04, so the two paths are not interchangeable within one measurement and a run must name the path it used. The script also returns the resolved model identifier, which the tool path did not expose. A resumed run retried only the single failed unit and finished in seconds.

## Coverage instead of sampling

Sampling was introduced when review attention was assumed expensive. On a 20-paper corpus the random 12-unit probe covered about 28 percent of units and recovered no consistent recall, while deterministic surfaces did: every unit at or above 0.35, every candidate-span unit, and sentence-level hits together covered 17 of the 18 findings a full agent read produced as valid, at about 35 percent of units read. Sentence-level screening alone raised one document from 11 routed units to 17.

The lesson is that recall should come from a score floor and finer granularity, not from drawing a sample. Keep a small probe only to estimate bias.

## Review-scope measurements

Two aggregate runs on the same English draft compared the cost of the two review scopes. Only aggregate workload is recorded here; no document identity, section names or excerpts.

| run | routing | agent reading | Jev requests | agent turns | agent output tokens |
|---|---|---|---:|---:|---:|
| Jev-first, every unit read | four active dimensions, gate passed | 119 of 119 units | 131 | 38 | about 46k |
| agent-only skill, no Jev | none | whole draft, no unit ledger | 0 | 12 | about 12k |

The Jev-first run that also read every unit cost roughly 3.7 times the agent output tokens of the agent-only run. That is a property of full reading, not evidence about the classifier: the same Jev requests would have supported a `screened` run that read 9 routed units, 6 candidate spans and a 20-unit sample. Do not reuse this table as a quality result; it measures workload only, and both runs used a single model.

For a fair cost comparison, hold the draft, model and requirement fixed and vary only the scope. Record units read, units unread, Jev requests and failures, and the misses found in the sampled population. A cheaper run that misses a confirmed finding is a recall failure, not an efficiency gain.

## What the numbers mean

Probabilities prioritize inspection, not edit permission. A passing six-control gate is a small smoke test, not a generalization result. Missing calls are null, never zero. Full reading remains mandatory even when no unit routes. Distinguish model alias from a resolved immutable version, and retain question revision, state shape and raw responses.

For calibration beyond this smoke test, use independently labelled material across language, genre and problem class. Include ordinary neutral prose, necessary uncertainty, safety prohibitions, factual comparisons, resolved contextual references and genuinely empty retreat. Keep tuning and evaluation sets separate; after a set has influenced prompt design, do not call it unseen evidence. Report actual routed-unit precision and per-span disagreements without treating either agent as ground truth.
