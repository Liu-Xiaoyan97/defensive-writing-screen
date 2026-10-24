# Control battery, labeled cases, and calibration records

All values were produced by `jev-latest` through Pi `jev_evaluate` with one paragraph per request. They are routing observations, not ground truth, and they expire when the model, the wording, or the language changes. Rerun the battery after any of those changes. Repeat runs on identical input varied by up to 0.03, so treat a value near the threshold as a coin flip rather than a stable estimate.

This file records detector behaviour only: control sentences, question-level numbers, and aggregate screening statistics. It must not carry project content, document identity, domain vocabulary, or draft-specific excerpts. Project cases belong in the project that uses the skill, supplied as state at run time.

## Control battery (question set v2)

Run these six before screening a document. The battery passes when each positive control reaches its designated dimension at or above 0.65 and neither negative control exceeds 0.20 on any dimension.

| id | text | designated dimension | v2 value | expected agent decision |
|---|---|---|---:|---|
| `pos_do_not_claim` | We do not claim that these cases are representative of all contexts. | `claim_negation` | 0.991 | rewrite to positive scope |
| `pos_not_x_but_y` | This paper is not intended to provide a comprehensive theory of platform governance, but rather to examine one specific mechanism. | `negative_contrast` | 0.919 | rewrite to a single claim |
| `pos_although_limited` | While the sample is limited and cannot capture every variation, it still offers useful insights. | `claim_negation` | 0.832 | rewrite; keep the sample description |
| `pos_stacked_hedge` | This may potentially suggest that X could possibly be associated with Y. | `vague_hedge` | 0.995 | reduce to one warranted qualifier |
| `neg_neutral_setup` | We train four models on the same corpus for 10B tokens. | all | 0.002 / 0.001 / 0.004 | keep |
| `neg_neutral_result` | Under the same conditions the two averages are 49.47% and 46.08%. | all | 0.002 / 0.002 / 0.017 | keep |

The positive controls are the canonical defensive patterns listed in `references/rewrite-guide.md`; they carry no project content. The battery runs entirely from files in this skill.

The same six controls under the deprecated v1 sufficiency wording:

| id | v1 dimension | v1 value |
|---|---|---:|
| `pos_do_not_claim` | preemptive | 0.446 |
| `pos_not_x_but_y` | preemptive | 0.233 |
| `pos_although_limited` | preemptive | 0.310 |
| `pos_stacked_hedge` | hedging | 0.732 |
| `neg_neutral_setup` | preemptive | 0.005 |
| `neg_neutral_result` | preemptive | 0.003 |

Three of the four canonical positives sit below 0.65 under v1, which is why a v1 threshold cannot be used as written. That measurement is the basis of the v0.3.0 change.

## Labeled cases from the Chinese smoke test (v1 questions)

Measured before the v2 calibration. Kept because the agent decisions still define correct behaviour; the probabilities need re-measurement under v2 before they are used for routing.

| id | text | expected agent decision |
|---|---|---|
| `weak_modesty` | 本文仅在两个数据集上做了初步尝试，只能提供有限参考。 | rewrite; keep "two datasets" |
| `causal_boundary` | 观察性分析发现 X 与 Y 相关。本研究不能据此识别 X 对 Y 的因果效应。 | keep; the causal limit carries method meaning |
| `safety_rule` | 设备通电时不得进行校准，否则可能发生电击。 | keep; safety prohibition |
| `clean_scope` | 本文在两个数据集上评估该方法。 | keep; no defensive wording |
| `strong_defense` | 本文并不声称解决所有语言模型问题，也无意证明该方法总是最优。我们只提供一个初步方案，仍有很大提升空间。 | rewrite both sentences |

| case | self | preemptive | hedging | span removal_preserves |
|---|---:|---:|---:|---:|
| `weak_modesty` | 0.336 | 0.223 | 0.271 | 0.691 |
| `causal_boundary` | 0.038 | 0.044 | 0.060 | 0.737 |
| `safety_rule` | 0.001 | 0.004 | 0.014 | 0.371 |
| `clean_scope` | 0.006 | 0.019 | 0.093 | — |
| `strong_defense` | 0.753 | 0.804 | 0.357 | — |

Under v2, `weak_modesty` and `strong_defense` are expected to move on `claim_negation`, and `causal_boundary` and `safety_rule` are expected to stay high on `claim_negation` while remaining correct to keep. Re-measure before using either number.

## Calibration screening (v1 to v2)

Two question sets were compared on the same English academic draft, with display math, tables, and bibliographies excluded. The draft is unidentified on purpose and only aggregate detector behaviour is recorded: no excerpts, section names, figures, domain terms, or counts that would identify it.

| run | question set | maximum | median | candidates at 0.65 | confirmed after review |
|---|---|---:|---:|---:|---:|
| A | v1 sufficiency | 0.251 | 0.043 | 0 | none reached review |
| B | v2 observable | 0.99 | 0.014 | 13 | 5 |

The 13 candidates of run B fell into five decision classes:

| class | count | agent decision |
|---|---:|---|
| contrast clause repeating a fact stated elsewhere | 1 | change |
| disclaimer whose content belongs in a setup or definition section | 1 | change |
| vague weakening clause naming no source of uncertainty | 1 | change |
| duplicated limit or restated summary | 2 | change |
| necessary conceptual contrast or necessary scope | 8 | keep |

Confirmed share: 5 of 13, about 38%. Every reject was necessary contrast or necessary scope, which is the class the rewrite guide protects.

Three further candidates were below 0.65 on every dimension and were reached only through a retrieved span. Their span values were 0.66, 0.60, and 0.39; the agent changed the first two and kept the third.

## What the numbers mean

- **Sufficiency wording compresses the scale.** v1 scored the canonical defensive sentences at 0.15-0.45, below the gate it shipped with, and returned no candidate on a draft that contained several. A low v1 score is not evidence about a document.
- **Observable wording restores separation.** v2 scores positives at 0.83-0.99 and neutral prose at 0.002-0.017, so 0.65 is usable and the ranking carries information.
- **Different constructions need different dimensions.** A `rather than` contrast is invisible to the hedge question, and "could hardly" is invisible to the contrast question. Keep the dimensions separate; a combined question returned 0.340 where separate questions returned 0.75-0.80 on the same sentence.
- **The focused span question is still required.** In run B, two of the five confirmed changes were below 0.65 on every dimension and were reached only through a retrieved span.
- **Candidate precision is low and must be reported.** Most candidates in an academic draft are necessary contrast or necessary scope; reporting only the candidate count overstates the problem by a factor of two to three.
- **Keep the model fixed while calibrating.** Numbers move across versions; record the version with every table.
- **Richer context can cause timeouts.** Requests with long rule or evidence strings timed out at 10 s; the same judgments succeeded with a short, flat state. Keep state small and retry once.
- **Batching paragraphs degrades attribution.** Sending five paragraphs with `paragraphs[i].text` paths returned uniformly low values, while the same paragraphs judged one per request with `paragraph.text` produced higher and better-separated values.

## Using this file

1. Reproduce the battery table with the current model and question wording; a failing battery blocks the screen.
2. Record `triage_probability`, `removal_preserves`, agent decision, and final outcome, so the threshold can be chosen from observed misses and review volume.
3. Keep the expected agent decision, not only the probability: probabilities alone do not define correct behaviour.
4. Add project-specific cases in the project, not here. This file stays generic so that it can be reused and compared across projects.
