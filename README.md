# Defensive Writing Screen

An agent skill that finds defensive writing cheaply and rewrites it carefully.

Most writing skills ask a model to read a whole draft and comment on it. That is
expensive and tends to produce either generic advice or over-deletion. This skill
splits the work: a TypeSafe/Jev System One model scores every prose paragraph with
a few narrow yes/no questions, the agent reads only the paragraphs that score high,
and rewriting follows the bundled anti-defensive rulebook, which protects evidence,
scope, and necessary limitations.

The skill is self-contained. It carries its own rewrite rules (adapted from
[`anti-defensive-writing`](https://github.com/Kiterlin/anti-defensive-writing), MIT,
attribution only) together with its own screening questions and control battery, so
an agent that installs only this package has the full capability. It requires no
other skill and never defers to one.

## How it runs

```text
draft
  └─ prepare_units.py          split into prose paragraphs, line ranges, candidate spans
       └─ control battery      4 positive + 2 negative controls; a failing battery blocks the screen
            └─ Jev triage     observable noul questions per paragraph (+ focused span question)
                 └─ routing   max probability per paragraph, top-k above threshold
                      └─ agent     read every unit, classify, record rewrite or keep
                           └─ rewrite guide   claim-first, positive scope, keep real limits
                                └─ report       excerpt, reason, one local revision
```

Jev never rewrites, never locates quotes, and never grants permission. A high
probability means "read this", not "delete this".

## Install

### 1. From npm

```sh
npm install defensive-writing-screen
```

The package ships the skill directory, its references, and its two helper scripts.
Point your agent at `node_modules/defensive-writing-screen/skills/defensive-writing-screen/`,
or copy that directory into a skills location your agent reads:

```sh
mkdir -p ~/.agents/skills
cp -R node_modules/defensive-writing-screen/skills/defensive-writing-screen ~/.agents/skills/
```

Claude Code reads `~/.claude/skills/` or `.claude/skills/` instead. Keep the
`references/` and `scripts/` subdirectories: the skill resolves them relative to its
own directory, and `references/rewrite-guide.md` supplies the rewriting rules.

### 2. As a Pi package

```sh
pi install npm:defensive-writing-screen
# or pin a version
pi install npm:defensive-writing-screen@0.6.0
# or from git or a local checkout
pi install git:github.com/Liu-Xiaoyan97/defensive-writing-screen
pi install ./defensive-writing-screen
```

`package.json` declares `pi.skills: ["./skills"]`, so the skill appears alongside
other Pi resources. Run `/reload` in an existing session, then invoke it with
`/skill:defensive-writing-screen`.

### 3. From a checkout

```sh
git clone https://github.com/Liu-Xiaoyan97/defensive-writing-screen.git
cp -R defensive-writing-screen/skills/defensive-writing-screen ~/.agents/skills/
```

The installer reads the current checkout when run from the repository root and
otherwise downloads a tarball:

```sh
sh install.sh                                   # -> ~/.agents/skills
sh install.sh --dest .agents/skills             # project-level
```

The layout follows the `skills/<name>/SKILL.md` convention used by `npx skills`:

```sh
npx skills add Liu-Xiaoyan97/defensive-writing-screen
```

## Requirements

No other skill and no MCP server is required. The skill is a self-contained
directory: its rulebook, question set, control battery, and scripts are all local,
and `scripts/validate.py` fails if the text reintroduces a dependency on another
installed skill.

- A System One caller for triage: Pi's `jev_evaluate` tool, the TypeSafe HTTP API
  (`/v1/systemone`), or a compatible local endpoint such as a StartLux-Decision
  server that accepts `state` + typed `questions`.
- Python 3.8+ only for the two helper scripts. Both are stdlib-only, make no
  network calls, and are optional: the agent can split paragraphs and merge the
  per-unit record itself.
- No Jev? The skill still runs in `agent-only` mode using the bundled rewrite
  guide, and must report that triage was skipped.

## Use

Ask for an audit and name the scope:

```text
Use defensive-writing-screen on sections 4.2-4.3 of draft.md. Screen first, show me
candidates with probabilities, then propose edits without writing to the file.
```

The agent then:

1. emits units with `scripts/prepare_units.py --candidates`;
2. asks the three broad questions per paragraph and, for each retrieved span, the
   focused removal question;
3. ranks by `max(probability)` and reviews the top candidates above the threshold;
4. verifies each one against the surrounding argument and known evidence, and
   records a verdict for every unit, including those the screen did not route;
5. proposes one local revision per confirmed item, or explains why it stays.

Default reporting: source excerpt, probabilities, agent classification, proposed
revision. Nothing is written to disk unless you authorize it.

## Calibration

Version 0.3.0 replaces the original sufficiency questions with observable ones and
adds a control battery that runs before any document is screened. The change came
from a measured failure: the original questions scored the canonical defensive
sentences at 0.15-0.45, below the 0.65 gate they were shipped with, and an English
academic draft of several hundred units returned no candidate at all. The observable set scores the
same positives at 0.90-0.99 and neutral prose at 0.001-0.024; on that draft it
returned 13 candidates, of which 5 survived review.

The shipped `0.65` threshold is valid only for the current question set, language,
and model version. Rerun `references/cases.md` before screening a new genre, and
report the six battery values with any result. A failing battery invalidates the
run; it does not make the document clean. Chinese and other CJK inputs are accepted
by Jev but score lower than English, so calibrate separately and keep the agent
verification step. Record the model version with any tuning result.

Calibration data is deliberately decoupled from any project. The skill holds
control sentences from the upstream defensive-writing patterns plus aggregate
screening statistics: no draft content, document identity, domain vocabulary, or
excerpts. Project cases live in the project and reach the skill only as run-time
state, so the same battery can be compared across projects.

## Design notes

- **Screening before rewriting.** Paragraph-level questions are cheap and parallel;
  rewriting is not. Triage buys attention where it matters.
- **A battery before a screen.** A probability scale without known positive and
  negative controls cannot distinguish a clean draft from an insensitive question.
- **Observable wording over sufficiency wording.** Asking whether wording "adds
  evidence" is answered conservatively on academic prose and flattens the ranking;
  asking what the text contains keeps the scale usable.
- **One paragraph per request.** Batched paragraphs blurred target attribution in
  testing; the SOP keeps them separate until a measured run shows otherwise.
- **Two question families.** Observable dimensions catch explicit defense; a focused
  "would removal preserve all known meaning?" question catches mild Chinese modesty
  and restated caveats that the dimensions miss. Neither one alone is sufficient.
- **Necessary limits are protected.** Causal boundaries, safety prohibitions,
  technical prerequisites, mathematical conditions, unfavorable results, and
  conceptual contrasts that carry the argument stay, even when they read as negative
  phrasing. In the measured run, eight of thirteen candidates were such contrasts.
- **No skill dependencies.** Every capability lives inside this directory:
  screening questions, the control battery, the rewrite rulebook, and the unit
  splitter. The skill neither loads nor defers to `anti-defensive-writing` or any
  other installed skill; attribution in `NOTICE.md` is provenance, not a runtime
  link. Install it alone, or delete the upstream skill, and behaviour is unchanged.

## Files

```text
package.json
README.md
LICENSE
NOTICE.md
skills/defensive-writing-screen/
├── SKILL.md
├── references/
│   ├── questions.md        request shapes, routing, calibration
│   ├── rewrite-guide.md    bundled rewrite rulebook (self-sufficient)
│   └── cases.md            labeled smoke tests and observed failures
└── scripts/
    ├── prepare_units.py    offline paragraph and candidate-span extraction
    └── merge_verdicts.py   join screen, verdicts, and labels; print agreement
```

## License

MIT. The rewrite guide is adapted from `anti-defensive-writing` by Kiterlin (MIT).
`NOTICE.md` records the upstream commit, file hash, scope of the adaptation, and the
fact that the upstream skill is not a runtime dependency.
