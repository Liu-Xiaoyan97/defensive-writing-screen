# Defensive Writing Screen

A self-contained agent skill for finding unnecessary defensive writing without
removing facts, limitations, uncertainty or unfavorable results.

A TypeSafe/Jev-compatible caller routes paragraphs for attention. The agent reads
local context, establishes whether a problem exists, and independently checks any
repair. A high routing score is not a diagnosis or permission to edit.

## Version 0.30.0

- Require an auditable Pass B reason for every candidate: exact candidate proposition, local evidence proposition, relevant scope match, and any residual authorial assurance beyond protected information. This makes existing KEEP tests explicit; it does not change the issue standard or claim a measured accuracy gain.
- Add optional bidirectional structural validation linking issue candidates and positive findings in full-review audit records.

## Version 0.28.0

- Split full-scope review into independent candidate discovery and adjudication passes.
  The adjudicator rereads every target, sees candidate spans without prior verdicts,
  and can add missed candidates. This is a workflow hypothesis, not a measured
  detection improvement; it increases review cost and needs a frozen regression.
- Add separate validation mode for discovery-only ledgers so candidates cannot be
  prematurely recorded as KEEP or issue before adjudication.

## Version 0.27.0

- Add an evidence-proposition comparison for evaluative KEEP rationales. Related
  facts are not automatically evidence for the exact scope judgment being made.
- Add domain-neutral paired cases for same-topic versus same-question evidence,
  mixed-metric interpretations, subgroup uncertainty, design cost, and repeated
  genre labels.
- Keep evidence sufficiency separate from defensive-writing classification. An
  unverified scientific interpretation is not automatically defensive; preserve
  its modality and report the evidence question separately.
- Keep all controls and examples domain-neutral. They do not borrow terminology
  or claims from the motivating manuscript.

- Add a sequence-level check for repeated generic scope/genre disclaimers in Q&A
  clusters. Distinguish empty repeated rebuttals from separate design rationales.
- Add regression cases for repeated “not a benchmark” and burden-limiting phrases,
  paired with KEEP controls that preserve distinct scope and mathematical goals.

- Require a separate per-unit candidate-scan artifact before verdicts, including
  explicit no-candidate records and concrete KEEP reasons. Its offline validator
  checks record coverage and literal spans, not actual reading or semantic truth.
- Search omitted-work rationales and question-and-answer rebuttals semantically.
  Keep concrete design reasons, contribution scope and responsibility disclosures.

- Remove the contradictory rule that a fact-preserving concession rewrite must be
  confirmed. Normal tradeoffs and necessary restrictions stay KEEP or optional.
- Separate issue detection from repair quality: confirmed, partial, optional, keep
  and unresolved have different meanings and counters.
- Default to paragraph routing at 0.65 plus 12 evenly spaced non-routed units.
  This is not random sampling and does not estimate population recall.
- Keep full selected paragraphs and neighbors. Optional sentence screening keeps
  every hit with exact parent offsets; there is no silent text truncation.
- Validate source quotations, source hashes and review-record consistency before
  accepting suggestions. This validation is not an automated semantic proof.
- Preserve degree and modal strength in both directions. Ordinary compression is
  not defensive-writing detection.

The four observable Jev questions are unchanged. The six-control gate remains a
run-specific routing smoke test, not a semantic accuracy benchmark. New review
rules and local tests alone do not establish improved detection performance.

## Independent installation

The skill contains its own rules, controls and scripts. It requires no other skill,
and never loads or defers to one. The bundled rewrite guide is adapted from
[`anti-defensive-writing`](https://github.com/Kiterlin/anti-defensive-writing)
(Kiterlin, MIT); `NOTICE.md` records provenance. The upstream files are not runtime
dependencies.

```sh
npm install github:Liu-Xiaoyan97/defensive-writing-screen
mkdir -p ~/.agents/skills
cp -R node_modules/defensive-writing-screen/skills/defensive-writing-screen ~/.agents/skills/
```

Pin a published tag or commit for reproducibility. Registry installation with
`npm install defensive-writing-screen` is available only after publication; a
version in this checkout does not imply a published release.

From a checkout:

```sh
git clone https://github.com/Liu-Xiaoyan97/defensive-writing-screen.git
cd defensive-writing-screen
sh install.sh --dest ~/.agents/skills
```

Keep the complete skill directory, including `references/` and `scripts/`. The
package also retains `pi.skills: ["./skills"]` resource metadata. No MCP server or
additional skill is required.

## Requirements

- Python 3.10+ for the bundled scripts. Offline preparation, packet generation,
  anchor checks and aggregation use only the standard library.
- A System One-compatible caller for Jev routing (`state` plus typed `questions`).
  `run_screen.py` makes network requests for gate, triage and focused modes; it can
  optionally use an installed `certifi` TLS bundle when available.
- Without Jev, use the bundled agent-only review, mark scores null and read the
  full authorized scope. Do not call this a successful Jev screening run.

## Run

Resolve paths relative to `skills/defensive-writing-screen`:

```sh
python3 scripts/prepare_units.py draft.txt --candidates > units.jsonl
python3 scripts/run_screen.py gate --out gate.jsonl
# Continue only after a passing gate.
python3 scripts/run_screen.py triage --units units.jsonl --out screen.jsonl
python3 scripts/run_screen.py summarize --screen screen.jsonl --units units.jsonl --out packet.md
```

Use `--endpoint`, `JEV_MODEL`, `JEV_API_KEY` and `--workers` for your service.
Do not put API keys in output artifacts. The runner records requested results and
resolved model metadata. Use new files when changing source, model or questions;
`--resume` is for retrying the same run's missing/failed rows.

The packet's JSON sidecar keeps raw source snapshots and complete context. The
agent reads all sentences of selected units, establishes issues and then records
repair checks using `references/questions.md`. It writes findings plus a separate
runtime `candidate-scan.jsonl`, not a response ledger of every low-risk paragraph. Manuscript editing still requires permission.

```sh
python3 scripts/verify_findings.py --units units.jsonl --findings findings.jsonl \
  --source draft.txt --out checked.jsonl
python3 scripts/verify_candidate_scan.py --units units.jsonl --scan candidate-scan.jsonl \
  --findings findings.jsonl --out candidate-check.json
python3 scripts/merge_verdicts.py --screen screen.jsonl --verdicts checked.jsonl --out review.tsv
```

Empty findings do not certify unread text as clean. A report may keep compact
reviewed-unit IDs separately; the packet's selected count is not proof of reading.
No manuscript is modified by these scripts. Runtime artifacts are written to the
specified paths and should live outside the installed skill directory.

Optional sentence screening:

```sh
python3 scripts/split_sentences.py units.jsonl > sentences.jsonl
python3 scripts/run_screen.py triage --units sentences.jsonl --out sentence-screen.jsonl
python3 scripts/run_screen.py summarize --screen screen.jsonl --units units.jsonl \
  --sentence-screen sentence-screen.jsonl --sentence-units sentences.jsonl --out packet.md
```

`--sample 0` disables the spaced sample; `--min-score` changes the score floor
explicitly. `--markers-from units.jsonl` adds candidate-only parents. `--chars`
accepts only 0, because truncation can hide the exact target or a critical qualifier.

## What counts as improvement

Measure real problem identification and safe repairs separately. KEEP is not a
false positive; optional style is not a defensive hit. Independent labels are
needed for precision/recall claims. Software tests and consistent source anchors
are necessary but do not establish LLM judgment quality. Development papers remain
regression material, not unseen validation.

## Local verification

```sh
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
npm pack --dry-run
```

No live model calls are required for these checks. The tests cover record and
packet behavior, source preservation and specification consistency. They do not
assert semantic accuracy from fixture labels.

## Files

- `skills/defensive-writing-screen/SKILL.md`: complete operating procedure.
- `references/controls.json`: observable questions, routing controls and generic
  semantic regression specifications.
- `references/questions.md`: state, record, counting and failure contracts.
- `references/rewrite-guide.md`: standalone evidence-preserving rewrite rules.
- `references/cases.md`: calibration limits and regression categories.
- `scripts/`: source preparation, routing, lossless packets, optional sentence
  splitting, source/record checks, aggregation and structure observations.

MIT. See `LICENSE` and `NOTICE.md` for attribution.
