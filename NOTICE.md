# Notice

This package contains an adaptation of a third-party skill. The upstream license is
reproduced in `LICENSE`; the statement below records what came from where.

## Upstream

- Project: `anti-defensive-writing`
- Repository: https://github.com/Kiterlin/anti-defensive-writing
- Commit read: `f516147d017a3fe43ae99192cb89d8261b0c8679`
- Upstream file: `skill/anti-defensive-writing/SKILL.md`
- SHA-256 of that file as vendored in the source project:
  `287e3d05aeabf6409fa53b74a124ee0d897338009be2c04d3e38c352ca74a3c1`
- License: MIT, Copyright (c) 2026 Kiterlin

## What was adapted

`skills/defensive-writing-screen/references/rewrite-guide.md` is a condensed,
reorganized restatement of the operational content of the upstream skill: the core
claim-first rule, the rule that necessary limitations survive, the classify-then-
rewrite procedure, the detection checklist, the discouraged-pattern list, the
handling of metrics and unfavorable results, the Chinese and English phrasing
habits, and illustrative pairs of defensive and direct sentences. Wording was
rewritten for brevity and grouped for lookup; the operational rules were not
relaxed. Examples of phrasing were kept as phrasing only, with no added facts.

## What is original to this package

- The Jev triage design: paragraph-level `noul` questions, the focused
  removal-preservation question, the routing rule, and the agent-verification step.
- `skills/defensive-writing-screen/references/questions.md` and `cases.md`.
- `skills/defensive-writing-screen/scripts/prepare_units.py`.
- The package layout, `package.json`, `README.md`, and `install.sh`.

## What was not taken

No upstream installer, script, image, or test suite is bundled. No upstream
repository is vendored. The upstream `SKILL.md` is not reproduced verbatim; the
adaptation is the condensed guide only.

## Compatibility note

If an `anti-defensive-writing` skill is installed alongside this one, the skill
instructs the agent to prefer the installed skill for rewrite wording and to treat
the bundled guide as a fallback. The two are intended to agree; where they differ,
the installed upstream skill is authoritative for rewriting.
