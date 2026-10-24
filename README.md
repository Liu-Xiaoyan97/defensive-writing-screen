# Defensive Writing Screen

An agent skill that finds defensive writing cheaply and rewrites it carefully.

Most writing skills ask a model to read a whole draft and comment on it. That is
expensive and tends to produce either generic advice or over-deletion. This skill
splits the work: a TypeSafe/Jev System One model scores every prose paragraph with
a few narrow yes/no questions, the agent reads only the paragraphs that score high,
and rewriting follows the bundled anti-defensive rulebook, which protects evidence,
scope, and necessary limitations.

The skill is self-contained. It carries its own rewrite rules (adapted from
[`anti-defensive-writing`](https://github.com/Kiterlin/anti-defensive-writing), MIT)
so an agent that installs only this package still has the full editing capability.

## How it runs

```text
draft
  └─ prepare_units.py          split into prose paragraphs, line ranges, candidate spans
       └─ Jev triage          3 broad noul questions per paragraph (+ 1 focused span question)
            └─ routing         max probability per paragraph, top-k above a threshold
                 └─ agent     read candidate in context, classify, decide keep or change
                      └─ rewrite guide   claim-first, positive scope, keep real limits
                           └─ report       excerpt, reason, one local revision
```

Jev never rewrites, never locates quotes, and never grants permission. A high
probability means "read this", not "delete this".

## Install

### 1. As an agent skill (any skills-compatible agent)

The skill is the directory `skills/defensive-writing-screen/`. Copy it into a skills
location your agent reads:

```sh
# user-level (Pi, Codex, other agents reading ~/.agents/skills)
mkdir -p ~/.agents/skills
cp -R skills/defensive-writing-screen ~/.agents/skills/

# or project-level
mkdir -p .agents/skills
cp -R skills/defensive-writing-screen .agents/skills/
```

Claude Code uses `~/.claude/skills/` or `.claude/skills/` instead. Keep the
`references/` and `scripts/` subdirectories: the skill resolves them relative to its
own directory, and `references/rewrite-guide.md` is what supplies the rewriting
capability.

From a git URL:

```sh
git clone https://github.com/<you>/defensive-writing-screen.git
cp -R defensive-writing-screen/skills/defensive-writing-screen ~/.agents/skills/
```

With the installer, which reads this checkout when run from the repository root and
otherwise downloads a pinned tarball:

```sh
sh install.sh                                   # -> ~/.agents/skills
sh install.sh --dest .agents/skills             # project-level
sh install.sh --repo <you>/defensive-writing-screen --ref v0.2.0 --force
```

With the skills CLI (layout follows the `skills/<name>/SKILL.md` convention; confirm
with the CLI's own output):

```sh
npx skills add <you>/defensive-writing-screen@defensive-writing-screen
```

### 2. As a Pi package

```sh
pi install git:github.com/<you>/defensive-writing-screen@v0.2.0
# or from a local checkout
pi install ./defensive-writing-screen
```

`package.json` declares `pi.skills: ["./skills"]`, so the skill appears alongside
other Pi resources. Run `/reload` in an existing session, then invoke it explicitly
with `/skill:defensive-writing-screen`.

## Requirements

- A System One caller for triage: Pi's `jev_evaluate` tool, the TypeSafe HTTP API
  (`/v1/systemone`), or a compatible local endpoint such as a StartLux-Decision
  server that accepts `state` + typed `questions`.
- Python 3.8+ only if you use `scripts/prepare_units.py`. It is stdlib-only and
  optional: the agent can split paragraphs itself.
- No Jev? The skill still runs in `agent-only` mode using the bundled rewrite
  guide, and must report that triage was skipped.

## Use

Ask for an audit and name the scope:

```text
Use defensive-writing-screen on sections 4.2-4.3 of paper.md. Screen first, show me
candidates with probabilities, then propose edits without writing to the file.
```

The agent then:

1. emits units with `scripts/prepare_units.py --candidates`;
2. asks the three broad questions per paragraph and, for each retrieved span, the
   focused removal question;
3. ranks by `max(probability)` and reviews the top candidates above the threshold;
4. verifies each one against the surrounding argument and known evidence;
5. proposes one local revision per confirmed item, or explains why it stays.

Default reporting: source excerpt, probabilities, agent classification, proposed
revision. Nothing is written to disk unless you authorize it.

## Calibration

The shipped `0.65` routing threshold is a smoke-test value, not a calibrated cutoff.
Run `references/cases.md`, add labeled paragraphs from your language and genre, and
pick the threshold from the observed miss/review trade-off. Chinese and other CJK
inputs are accepted by Jev but score lower than English, so calibrate separately and
keep the agent verification step. Record the model version with any tuning result.

## Design notes

- **Screening before rewriting.** Paragraph-level questions are cheap and parallel;
  rewriting is not. Triage buys attention where it matters.
- **One paragraph per request.** Batched paragraphs blurred target attribution in
  testing; the SOP keeps them separate until a measured run shows otherwise.
- **Two question families.** Broad questions catch explicit defense; a focused
  "would removal preserve all known meaning?" question catches mild Chinese modesty
  that broad questions miss. Neither one alone is sufficient.
- **Necessary limits are protected.** Causal boundaries, safety prohibitions,
  technical prerequisites, and unfavorable results stay, even when they read as
  negative phrasing.
- **Rewriting capability is bundled.** `references/rewrite-guide.md` reproduces the
  operational content of `anti-defensive-writing` needed to revise prose, with
  attribution in `NOTICE.md`.

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
│   ├── rewrite-guide.md    inherited anti-defensive rulebook
│   └── cases.md            labeled smoke tests and observed failures
└── scripts/
    └── prepare_units.py    offline paragraph and candidate-span extraction
```

## License

MIT. The rewrite guide is adapted from `anti-defensive-writing` by Kiterlin (MIT);
see `NOTICE.md` for the upstream commit, file hash, and scope of the adaptation.
