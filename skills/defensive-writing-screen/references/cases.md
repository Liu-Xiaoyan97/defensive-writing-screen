# Control battery, labeled cases, and calibration records

All values were produced by `jev-latest` through Pi `jev_evaluate` with one paragraph per request. They are routing observations, not ground truth, and they expire when the model, the wording, or the language changes. Rerun the battery after any of those changes. Repeat runs on identical input varied by up to 0.03, so treat a value near the threshold as a coin flip rather than a stable estimate.

This file records detector behaviour only: control sentences, question-level numbers, and aggregate screening statistics. It must not carry project content, document identity, domain vocabulary, or draft-specific excerpts. Project cases belong in the project that uses the skill, supplied as state at run time.

## Control battery (question set v3)

Run these seven before screening a document. The battery passes when each positive control reaches its designated dimension at or above 0.65 and neither negative control exceeds 0.20 on any dimension.

Values in this table were re-measured for v3 on one served model, whose endpoint reported `StartLux-Decision-v1.1-4B-AutoThink`; an earlier v2 table recorded `jev-latest` and differed within the documented 0.03 repeat-run spread. Record the model with any rerun.

| id | text | designated dimension | v3 value | expected agent decision |
|---|---|---|---:|---|
| `pos_do_not_claim` | We do not claim that these cases are representative of all settings. | `claim_negation` | 0.991 | rewrite to positive scope |
| `pos_not_x_but_y` | This paper is not intended to provide a comprehensive account of the phenomenon, but rather to examine one specific mechanism. | `negative_contrast` | 0.844 | rewrite to a single claim |
| `pos_although_limited` | While the sample is limited and cannot capture every variation, it still offers useful insights. | `concessive_hedge` | 0.988 | rewrite; keep the sample description |
| `pos_stacked_hedge` | This may potentially suggest that X could possibly be associated with Y. | `vague_hedge` | 0.977 | reduce to one warranted qualifier |
| `pos_scope_tail` | The intervention lowers the measured error by 4.5 points under this setup. | `scope_tail` | 0.968 | rewrite; name the condition or drop the tail |
| `neg_neutral_setup` | We analyze four cases over the same period. | all | 0.066 max | keep |
| `neg_neutral_result` | Under the same conditions the two estimates are 49.47% and 46.08%. | all | 0.145 max | keep |

The positive controls are the canonical defensive patterns listed in `references/rewrite-guide.md`; they carry no project content and no field-specific nouns, so the same battery applies to any academic or professional draft. Designated dimensions follow the construction each control uses: a concessive sentence routes on `concessive_hedge`, not on `claim_negation`.

### Chinese controls (bilingual markers)

English-only marker lists underperform on Chinese: the mild-modesty control scored 0.377 on the hedge dimension, below the gate, and 0.991 once Chinese markers were named in the same question. Run this block when the target document is Chinese.

| id | text | designated dimension | bilingual value | expected agent decision |
|---|---|---|---:|---|
| `zh_weak_modesty` | 本文仅在两个案例上做了初步尝试，只能提供有限参考。 | `vague_hedge` | 0.921 | rewrite; keep "two cases" |
| `zh_strong_defense` | 本文并不声称解决该领域的全部问题，也无意证明该方法总是最优。我们只提供一个初步方案，仍有很大提升空间。 | `claim_negation` | 0.995 | rewrite both sentences |
| `zh_causal_boundary` | 观察性分析发现 X 与 Y 相关。本研究不能据此识别 X 对 Y 的因果效应。 | `claim_negation` | 0.995 | keep; the causal limit carries method meaning |
| `zh_safety_rule` | 设备通电时不得进行校准，否则可能发生电击。 | none | 0.195 | keep; a prohibition is not routed for rewriting |
| `zh_clean_scope` | 本文在两个案例上评估该方法。 | all | 0.074 | keep |

### Concessive controls

| id | text | value on its strongest dimension | expected agent decision |
|---|---|---:|---|
| `concessive_soften` | 虽然样本规模有限，但该方法在三个案例上均给出一致结论。 | 0.991 (`concessive_hedge`) | rewrite; lead with the result |
| `gap_first` | 结果在部分指标上更优，但在另外两项指标上低于对照。 | 0.662 (`concessive_hedge`) | rewrite; state both sides without the concession frame |
| `necessary_limit` | 观察性分析发现 X 与 Y 相关。本研究不能据此识别 X 对 Y 的因果效应。 | 0.995 (`claim_negation`) | keep; the negation carries method meaning |
| `conditional_baseline` | 若仅采用单一取值，结论只能按一种方式汇总。 | 0.307 (`vague_hedge`) | keep; defines the problem the design addresses |
| `neutral` | 本文在两个案例上评估该方法。 | 0.074 (`vague_hedge`) | keep |

The `vague_hedge` question excludes explicit prohibitions and conditions that name the case they govern. Before that exclusion, the causal-limit control scored 0.706 on `vague_hedge` and the prohibition control 0.272, so both entered the review queue for nothing; after it they score 0.391 and 0.195 while the mild-modesty control stays at 0.921.

### Repetition controls (agent-side only)

| id | text | `repeated_fact` | expected agent decision |
|---|---|---:|---|
| `repeat_constructed` | 样本规模有限，说明样本规模不足，因此结论仅限本组案例，本组案例之外不作推断。 | 0.384 | rewrite; deliberate repetition |
| `repeat_neutral` | 本文在两个案例上评估该方法，报告其准确率与耗时。 | 0.343 | keep |

A deliberate repetition scores 0.384 against 0.343 for neutral prose, so neither question separates the class. A milder redundant pair timed out on four attempts and stays unmeasured. Repetition is therefore not a routing dimension; step 6 assigns it to the agent.

### Conditional controls

| id | text | `vague_hedge` | expected agent decision |
|---|---|---:|---|
| `conditional_vague` | 若只保留最终结论而不附原始记录，复核时难以追溯每个判断的依据。 | 0.706 | rewrite the closing clause; keep the conditional |
| `conditional_vague_strong` | 若只保留最终结论而不附原始记录，复核时几乎无法追溯任何判断的依据。 | 0.437 | rewrite the closing clause; keep the conditional |
| `conditional_precise` | 该流程统一采用固定模板，无法在单个环节内根据材料调整格式。 | 0.030 | keep; the constraint names its object |

The same class spans 0.030-0.706 across constructed instances, and the stronger wording scores lower than the milder one. Conditional vagueness therefore does not separate reliably at any single threshold; treat the distinction as an agent judgment and reach such units through the deterministic candidate search.

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

## Labeled cases (question set v1)

Reworded to remove field-specific nouns. The expected decisions still define correct behaviour; the v1 probabilities are no longer routing values.

| id | text | expected agent decision |
|---|---|---|
| `weak_modesty` | 本文仅在两个案例上做了初步尝试，只能提供有限参考。 | rewrite; keep "two cases" |
| `causal_boundary` | 观察性分析发现 X 与 Y 相关。本研究不能据此识别 X 对 Y 的因果效应。 | keep; the causal limit carries method meaning |
| `safety_rule` | 设备通电时不得进行校准，否则可能发生电击。 | keep; safety prohibition |
| `clean_scope` | 本文在两个案例上评估该方法。 | keep; no defensive wording |
| `strong_defense` | 本文并不声称解决该领域的全部问题，也无意证明该方法总是最优。我们只提供一个初步方案，仍有很大提升空间。 | rewrite both sentences |

The v1 run on the earlier phrasing returned 0.34 for `weak_modesty` and 0.75-0.80 for `strong_defense`. Only the second would have cleared a 0.65 gate, which is why the Chinese battery exists.

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

### Tail controls (question set v3)

| id | text | `scope_tail` | expected agent decision |
|---|---|---:|---|
| `pos_scope_tail` | The intervention lowers the measured error by 4.5 points under this setup. | 0.968 | rewrite; name the condition or drop the tail |
| `tail_setting` | The comparison supports the benefit of the additional term under the current training setup. | 0.809 | rewrite; the tail points at conditions already described |
| `tail_positions` | The check confirms agreement at the measured positions. | 0.979 | rewrite; name the coverage the check actually reached |
| `tail_named_budget` | The intervention lowers the measured error by 4.5 points at the 2B-step budget. | 0.008 | keep; the qualifier names its condition |
| `tail_named_protocol` | The check confirms that the two paths agree within 1e-5 at every readout record. | 0.014 | keep; the qualifier names the coverage |
| `tail_named_scope` | The intervention measures the contribution of the full path, not its components. | 0.068 | keep; removal would drop what the intervention covered |
| `tail_impl` | Both subsystems use the same scan in the current implementation. | 0.213 | keep as scope; the value exceeds the 0.20 control bound, so an implementation qualifier needs an agent decision rather than automatic routing |

Two of the positives were added after the first control set, because a single phrase can be matched by a keyword rule while the deictic pattern is the class being detected. `tail_impl` is recorded rather than repaired: pushing it under 0.20 by naming more exclusions would also pull down `tail_setting`, which shares its wording.

### Narrative cases (agent-side only)

No question in the set detects narrative placement, so these cases carry no routing
value. They fix the expected action so two readers can compare records.

| id | text | expected action | boundary that applies |
|---|---|---|---|
| `n1_defeat_buried` | The estimate is 0.7 points below the baseline while using 12% of its steps. | N1 restate; lead with the token share | may not become a match |
| `n1_stated_plainly` | Using 12% of its steps, the estimate comes within 0.7 points of the baseline. | keep | already in the stronger order |
| `n2_overreach` | The method outperforms the baselines on the tasks we measured and on others. | N2 narrow to the measured tasks | may not delete the measured comparisons |
| `n2_scoped` | The method outperforms the baselines on the four measured tasks. | keep | the claim matches the evidence |
| `n3_duplicate_fact` | The same setup sentence appears in a related-work subsection and again in the setup subsection. | N3 relocate; keep the setup subsection | must name the section that keeps it |
| `n3_kept_where_needed` | A control condition appears once, immediately before the comparison it governs. | keep | the fact is already where the reader needs it |

## What the numbers mean

- **Sufficiency wording compresses the scale.** v1 scored the canonical defensive sentences at 0.15-0.45, below the gate it shipped with, and returned no candidate on a draft that contained several. A low v1 score is not evidence about a document.
- **Observable wording restores separation.** v2 scores positives at 0.83-0.99 and neutral prose at 0.002-0.017, so 0.65 is usable and the ranking carries information.
- **Different constructions need different dimensions.** A `rather than` contrast is invisible to the hedge question, and "could hardly" is invisible to the contrast question. Keep the dimensions separate; a combined question returned 0.340 where separate questions returned 0.75-0.80 on the same sentence.
- **Low `removal_preserves` does not veto a rewrite.** A span that carries a fact scores low on the removal question because removal would lose that fact. Restructuring keeps the fact while removing the softening frame; check the rewrite against the original instead of deleting the span.
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
