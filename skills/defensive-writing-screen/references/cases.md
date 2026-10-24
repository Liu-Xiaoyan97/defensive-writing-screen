# Labeled smoke tests

Observed on `jev-latest` through Pi `jev_evaluate`, 2026-02, Chinese and English. These are **smoke tests, not a calibration set**: they show what the questions do, and where they fail. Rerun them after changing questions, model, or threshold.

## Cases

| id | language | text | expected agent decision |
|---|---|---|---|
| `weak_modesty` | zh | 本文仅在两个数据集上做了初步尝试，只能提供有限参考。 | rewrite; keep "two datasets" |
| `causal_boundary` | zh | 观察性分析发现 X 与 Y 相关。本研究不能据此识别 X 对 Y 的因果效应。 | keep; the causal limit carries method meaning |
| `safety_rule` | zh | 设备通电时不得进行校准，否则可能发生电击。 | keep; safety prohibition |
| `clean_scope` | zh | 本文在两个数据集上评估该方法。 | keep; no defensive wording |
| `strong_defense` | zh | 本文并不声称解决所有语言建模问题，也无意证明该方法总是最优。我们只提供一个初步方案，仍有很大提升空间。 | rewrite both sentences |

## Observed triage

| case | self | preemptive | hedging | span removal_preserves |
|---|---:|---:|---:|---:|
| `weak_modesty` | 0.336 | 0.223 | 0.271 | 0.691 |
| `causal_boundary` | 0.038 | 0.044 | 0.060 | 0.737 |
| `safety_rule` | 0.001 | 0.004 | 0.014 | 0.371 |
| `clean_scope` | 0.006 | 0.019 | 0.093 | — |
| `strong_defense` | 0.753 | 0.804 | 0.357 | — |

## What the numbers mean

- **The broad questions miss mild Chinese modesty.** `weak_modesty` peaks at 0.336 and would not reach a 0.65 gate. Without the focused span question it is silently skipped. This is why the SOP adds a deterministic candidate search plus a focused request.
- **The focused question does not separate removable from necessary wording by itself.** `weak_modesty` (removable) scores 0.691, and `causal_boundary` (must keep) scores 0.737. Ordering is uninformative here; only the agent's reading separates them. Never delete on probability alone.
- **The focused question does reject safety prohibitions.** `safety_rule` scores 0.371, so a gate on 0.65 avoids sending obvious prohibitions to review. It is a cheap filter, not a truth test.
- **Strong, explicit defense is detected easily.** `strong_defense` reaches 0.75-0.80 on the broad questions.
- **Collapsing dimensions loses signal.** Asking one combined question ("is this mainly uninformative self-deprecation?") on a shortened defensive sentence returned 0.340, versus 0.75-0.80 when the dimensions were separate. Keep the questions separate.
- **Richer context can cause timeouts.** Requests with long rule or evidence strings timed out at 10 s; the same judgments succeeded with a short, flat state. Keep state small and retry once.
- **Batching paragraphs degrades attribution.** Sending five paper paragraphs with `paragraphs[i].text` paths returned uniformly low values, while the same paragraphs judged one per request with `paragraph.text` produced higher and better-separated values. One paragraph per request is the default until measured otherwise.

## Real-document dry run

Thirteen prose paragraphs from a scaling-law experiments section (Chinese, numbers and sampling scope present) were screened one per request. Highest `triage_probability` was **0.169**; no unit reached 0.65, so the run produced no candidates and no edits.

Interpretation: the section is written without obvious defensive framing, or the questions under-detect that genre. A single run cannot distinguish the two. Before relying on a clean result, sample below-threshold units and add genre-specific labeled cases.

## Using this file

1. Reproduce the table with the current model and question wording.
2. Add cases from the target project, including necessary-limitation cases that must never be rewritten.
3. Set the routing threshold from the observed trade-off; store the resulting confusion counts here.
4. Keep the expected agent decision, not only the probability: probabilities alone do not define correct behavior.
