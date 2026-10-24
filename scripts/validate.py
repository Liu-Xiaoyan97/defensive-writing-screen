#!/usr/bin/env python3
"""Repository checks for defensive-writing-screen.

Stdlib only. Verifies the skill layout, frontmatter, referenced files,
package manifest, script behaviour, and that the rewrite guide is present and
non-trivial. Exit code 1 on failure.

Usage:
    python3 scripts/validate.py
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = ROOT / "skills" / "defensive-writing-screen"
SKILL_MD = SKILL_DIR / "SKILL.md"
REQUIRED_REFS = ["references/questions.md", "references/rewrite-guide.md", "references/cases.md", "references/controls.json"]
REQUIRED_SECTIONS = ["## SOP", "## Working without Jev", "## Reporting"]
# Capabilities the skill must supply itself; each must appear as a section in the
# bundled rulebook so no installed skill is needed to rewrite prose.
GUIDE_CAPABILITIES = [
    "## Core rule",
    "## Main argument",
    "## Writing principles",
    "## Technical plans and SOPs",
    "## Preferred patterns",
    "## Submission checks",
    "## What must survive",
    "## Classify before editing",
    "## Rewrite procedure",
    "## Detection checklist",
    "## Discouraged patterns",
    "## Retreating tails",
    "## Narrative placement",
    "## Protection before rewriting",
    "## Document structure",
    "## Metrics, experiments, unfavorable results",
    "## Chinese-specific habits",
    "## English-specific habits",
    "## Examples",
    "## Before returning a revision",
]
# Phrases that would make the skill depend on another installed skill.
DEPENDENCY_MARKERS = [
    "prefer its wording",
    "remains the fallback",
    "load it and prefer",
    "if an `anti-defensive-writing` skill is also installed",
    "requires the `anti-defensive-writing` skill",
]

failures: list[str] = []


def check(condition: bool, message: str) -> None:
    if not condition:
        failures.append(message)


def parse_frontmatter(text: str) -> dict[str, str]:
    check(text.startswith("---\n"), "SKILL.md must start with YAML frontmatter")
    parts = text.split("---\n", 2)
    check(len(parts) >= 3, "SKILL.md frontmatter must be closed")
    fields: dict[str, str] = {}
    for line in parts[1].splitlines():
        match = re.match(r"^([a-zA-Z-]+):\s*(.*)$", line)
        if match:
            fields[match.group(1)] = match.group(2).strip().strip('"')
    return fields


def main() -> int:
    text = SKILL_MD.read_text(encoding="utf-8")
    fields = parse_frontmatter(text)

    check(fields.get("name") == "defensive-writing-screen", "frontmatter name must match the directory")
    description = fields.get("description", "")
    check(10 < len(description) <= 1024, "frontmatter description length must be 11-1024 chars")
    check("Jev" in description, "description should state the Jev triage")
    check(fields.get("license") == "MIT", "frontmatter license must be MIT")
    check("version" in text, "metadata.version should be recorded")
    check(
        "Calibration records in this skill stay generic" in text,
        "SKILL.md must state that calibration records stay free of project content",
    )

    cases = SKILL_DIR / "references" / "cases.md"
    if cases.is_file():
        cases_text = cases.read_text(encoding="utf-8")
        check(
            "must not carry project content" in cases_text,
            "cases.md must keep the decoupling rule",
        )
        for marker in ["Control battery", "What the numbers mean"]:
            check(marker in cases_text, f"cases.md missing section: {marker}")

    for section in REQUIRED_SECTIONS:
        check(section in text, f"SKILL.md missing section: {section}")
    unknown=set(text.split("active_dimensions")) and None
    questions_text = (SKILL_DIR / "references" / "questions.md").read_text(encoding="utf-8")
    for marker in ["| R6 |", "Tail calibration history", "Protection classes"]:
        check(marker in questions_text, f"questions.md missing marker: {marker}")
    check("scope_tail" in text, "SKILL.md must state that scope_tail is retired")
    check("retired" in text, "SKILL.md must state that scope_tail is retired")
    for marker in ["null", "untriaged_control_failed", "agent-only"]:
        check(marker in text, f"SKILL.md missing failure-state marker: {marker}")
    for marker in ["P1", "P2", "P3", "P4", "P5", "P6"]:
        check(marker in questions_text, f"questions.md missing protection class: {marker}")
    # Review scope and disposition contract: the cost claim must stay measurable.
    for marker in ["## Review scope and cost accounting", "### Disposition test", "screened", "full"]:
        check(marker in questions_text, f"questions.md missing scope/disposition contract: {marker}")
    for marker in ["`confirmed`", "`optional`", "misses/sample"]:
        check(marker in questions_text, f"questions.md missing disposition or sampling rule: {marker}")
    for marker in ["screened", "full", "Review scope"]:
        check(marker in text, f"SKILL.md missing review-scope marker: {marker}")
    check("cannot save agent work by construction" in text,
          "SKILL.md must state that Jev-first review with full reading cannot save agent work")
    check("artifact" in text, "SKILL.md must route the full per-unit table to an artifact instead of the response")
    check("Report only what carries risk" in text,
          "SKILL.md must state that only risk-bearing results are recorded")
    check("no finding get no individual record" in text,
          "SKILL.md must exempt low-risk read units from individual records")
    check("aggregate line" in questions_text,
          "questions.md must define the aggregate record for read units without findings")
    check("a finding at any score is recorded" in questions_text,
          "questions.md must forbid suppressing a finding because its score is low")
    check("Recording dominates cost" in questions_text,
          "questions.md must record that response size, not only reading, drives agent cost")
    check("cannot save agent work by construction" in questions_text,
          "questions.md must repeat the cost caveat so it survives a partial read")
    for marker in ["N1", "N2", "N3"]:
        check(marker in questions_text, f"questions.md missing narrative action: {marker}")
    for marker in ["R1", "R2", "R3", "R4", "R5", "R6", "K1", "K7", "S1", "S6"]:
        check(marker in questions_text, f"questions.md missing verdict/structural id: {marker}")

    # Canonical questions and controls: single source of truth, fixed counts and ids.
    controls_path = SKILL_DIR / "references" / "controls.json"
    check(controls_path.is_file(), "controls.json missing")
    if controls_path.is_file():
        controls = json.loads(controls_path.read_text(encoding="utf-8"))
        questions = controls.get("questions", {})
        check(set(questions) == {"claim_negation", "negative_contrast", "vague_hedge", "concessive_hedge"},
              f"active question set must contain exactly four dimensions, got {sorted(questions)}")
        check(controls.get("active_dimensions") == list(questions),
              "active_dimensions must match the question keys in order")
        check("scope_tail" not in questions, "scope_tail must not be an active Jev dimension in v4")
        check("scope_tail" not in controls.get("active_dimensions", []),
              "scope_tail must not be listed as active")
        rows = controls.get("controls", [])
        positives = [r for r in rows if r["id"].startswith("pos_")]
        negatives = [r for r in rows if r["id"].startswith("neg_")]
        check(len(positives) == 4, f"control gate must list four positive controls, got {len(positives)}")
        check(len(negatives) == 2, f"control gate must list two negative controls, got {len(negatives)}")
        check(controls.get("thresholds") == {"positive_min": 0.65, "negative_max": 0.20},
              "control thresholds must be positive_min 0.65 and negative_max 0.20")
        for row in rows:
            check(row.get("designated_dimension") in {*questions, "all"},
                  f"control {row['id']} names an inactive dimension")
            check(bool(row.get("text")), f"control {row['id']} has no text")
        challenge_ids = {row["id"] for row in controls.get("semantic_challenges", [])}
        check(len(challenge_ids) >= 8, "semantic challenges must cover the calibrated decision classes")
        for required in ["resolved_reference", "unknown_reference", "protected_reframe",
                         "direction_without_number", "multiple_spans",
                         "concessive_confirmed", "optional_explicit_scope", "sampled_unread"]:
            check(required in challenge_ids, f"semantic challenges missing {required}")
        validation = controls.get("validation_controls", [])
        check(len(validation) >= 6, "validation_controls must provide at least six frozen texts")
        gate_texts = {row["text"] for row in rows}
        check(not ({row["text"] for row in validation} & gate_texts),
              "validation_controls must not reuse gate control texts")
        for row in validation:
            check(row.get("designated_dimension") in {*questions, "all"},
                  f"validation control {row['id']} names an inactive dimension")
    for marker in ["P1", "P2", "P3", "P4", "P5", "P6"]:
        check(marker in questions_text, f"questions.md missing protection class: {marker}")
    # Review scope and disposition contract: the cost claim must stay measurable.
    for marker in ["## Review scope and cost accounting", "### Disposition test", "screened", "full"]:
        check(marker in questions_text, f"questions.md missing scope/disposition contract: {marker}")
    for marker in ["`confirmed`", "`optional`", "misses/sample"]:
        check(marker in questions_text, f"questions.md missing disposition or sampling rule: {marker}")
    for marker in ["screened", "full", "Review scope"]:
        check(marker in text, f"SKILL.md missing review-scope marker: {marker}")
    check("cannot save agent work by construction" in text,
          "SKILL.md must state that Jev-first review with full reading cannot save agent work")
    check("artifact" in text, "SKILL.md must route the full per-unit table to an artifact instead of the response")
    check("Report only what carries risk" in text,
          "SKILL.md must state that only risk-bearing results are recorded")
    check("no finding get no individual record" in text,
          "SKILL.md must exempt low-risk read units from individual records")
    check("aggregate line" in questions_text,
          "questions.md must define the aggregate record for read units without findings")
    check("a finding at any score is recorded" in questions_text,
          "questions.md must forbid suppressing a finding because its score is low")
    check("Recording dominates cost" in questions_text,
          "questions.md must record that response size, not only reading, drives agent cost")
    check("cannot save agent work by construction" in questions_text,
          "questions.md must repeat the cost caveat so it survives a partial read")
    for marker in ["S1", "S2", "S3", "S4", "S5", "S6"]:
        check(marker in questions_text, f"questions.md missing structural finding: {marker}")
        check(marker in text, f"SKILL.md missing structural finding: {marker}")
    for marker in ["N1", "N2", "N3"]:
        check(marker in questions_text, f"questions.md missing narrative action id: {marker}")
        check(marker in text, f"SKILL.md missing narrative action id: {marker}")
    check(
        "requires no other skill" in text,
        "SKILL.md must state that the skill requires no other skill",
    )
    for step in range(1, 9):
        check(f"{step}. **" in text, f"SOP step {step} missing")

    for rel in REQUIRED_REFS:
        path = SKILL_DIR / rel
        check(path.is_file(), f"missing referenced file: {rel}")
        if path.is_file():
            check(path.stat().st_size > 500, f"referenced file too small to be useful: {rel}")
            # The skill must mention each reference so an agent can find it.
            check(rel.split("/")[-1] in text, f"SKILL.md does not point at {rel}")

    guide = SKILL_DIR / "references" / "rewrite-guide.md"
    if guide.is_file():
        guide_text = guide.read_text(encoding="utf-8")
        for marker in GUIDE_CAPABILITIES:
            check(marker in guide_text, f"rewrite guide missing capability: {marker}")
        check("Kiterlin" in guide_text, "rewrite guide must keep upstream attribution")
        check("MIT" in guide_text, "rewrite guide must keep the upstream license note")
        check(
            "complete on its own" in guide_text,
            "rewrite guide must state that it is self-sufficient",
        )

    # Independence: no skill file may instruct the agent to load or defer to another skill.
    scanned = [SKILL_MD] + [SKILL_DIR / rel for rel in REQUIRED_REFS]
    for path in scanned:
        if not path.is_file():
            continue
        body = path.read_text(encoding="utf-8")
        for marker in DEPENDENCY_MARKERS:
            check(
                marker not in body,
                f"{path.name} reintroduces a skill dependency: {marker!r}",
            )

    manifest = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
    check(manifest.get("name") == "defensive-writing-screen", "package.json name mismatch")
    check("pi-package" in manifest.get("keywords", []), "package.json needs the pi-package keyword")
    for declared in manifest.get("pi", {}).get("skills", []):
        check((ROOT / declared).is_dir(), f"pi.skills path does not exist: {declared}")
    for entry in manifest.get("files", []):
        check((ROOT / entry).exists(), f"package.json files entry missing: {entry}")
    check((ROOT / "LICENSE").is_file(), "LICENSE missing")
    notice = ROOT / "NOTICE.md"
    check(notice.is_file(), "NOTICE.md missing")
    if notice.is_file():
        notice_text = notice.read_text(encoding="utf-8")
        check("f516147" in notice_text, "NOTICE.md must record the upstream commit")
        check("MIT" in notice_text, "NOTICE.md must record the upstream license")

    runner = SKILL_DIR / "scripts" / "run_screen.py"
    check(runner.is_file(), "run_screen.py missing")
    if runner.is_file():
        result = subprocess.run([sys.executable, str(runner), "--help"], capture_output=True, text=True)
        check(result.returncode == 0, f"run_screen --help failed: {result.stderr.strip()}")
        runner_text = runner.read_text(encoding="utf-8")
        for marker in ("/v1/systemone", "--resume", "resolved_model", "mp.Pool", "imap_unordered",
                       "maxtasksperchild", "os.fsync", "summarize"):
            check(marker in runner_text, f"run_screen.py missing: {marker}")
            check(marker in runner_text, f"run_screen.py missing: {marker}")
        check("JEV_CONCURRENCY" in runner_text, "run_screen.py must expose the concurrency setting")
        check("claim units from a shared queue" in questions_text or "claim units" in questions_text,
              "questions.md must describe pool workers claiming units")
        check("flushed" in questions_text, "questions.md must state that finished rows are flushed")
        check("## Handoff packet" in questions_text, "questions.md must define the handoff packet")
        check("writes findings, not a ledger" in questions_text,
              "questions.md must state that the agent writes findings, not a ledger")
        check("do not write a per-unit ledger" in text,
              "SKILL.md must forbid the per-unit ledger in the response")
        check("run_screen.py" in text, "SKILL.md must point at run_screen.py")
        check("Script-mode and tool-mode values are not interchangeable" in text,
              "SKILL.md must warn that script and tool paths are not interchangeable")

    merge = SKILL_DIR / "scripts" / "merge_verdicts.py"
    check(merge.is_file(), "merge_verdicts.py missing")
    if merge.is_file():
        result = subprocess.run([sys.executable, str(merge), "--help"], capture_output=True, text=True)
        check(result.returncode == 0, f"merge_verdicts --help failed: {result.stderr.strip()}")

    structure = SKILL_DIR / "scripts" / "check_structure.py"
    check(structure.is_file(), "check_structure.py missing")
    if structure.is_file():
        sample = "# Abstract\n\nText.\n\n# Introduction\n\nText.\n\n# Limitations\n\nText.\n"
        result = subprocess.run([sys.executable, str(structure), "-"], input=sample,
                                capture_output=True, text=True)
        check(result.returncode == 0, f"check_structure failed: {result.stderr.strip()}")
        check("missing_conclusion" in result.stdout, "check_structure should flag a missing conclusion")
        check("ends_on_limitations" in result.stdout, "check_structure should flag a limitations ending")

    script = SKILL_DIR / "scripts" / "prepare_units.py"
    check(script.is_file(), "prepare_units.py missing")
    if script.is_file():
        sample = "本文并不声称解决所有问题，也无意证明该方法总是最优。\n\n设备通电时不得进行校准。\n"
        result = subprocess.run(
            [sys.executable, str(script), "-", "--candidates", "--min-chars", "8"],
            input=sample,
            capture_output=True,
            text=True,
        )
        check(result.returncode == 0, f"prepare_units failed: {result.stderr.strip()}")
        lines = [line for line in result.stdout.splitlines() if line.strip()]
        check(len(lines) == 2, f"prepare_units should emit 2 units, got {len(lines)}")
        for line in lines:
            unit = json.loads(line)
            for key in ("id", "start", "end", "paragraph", "text", "candidates"):
                check(key in unit, f"unit missing key: {key}")
            for span in unit.get("candidates", []):
                check(span in unit["text"], "candidate span must be a verbatim substring")

        phrase = "Within recurrent memory, the states do not by themselves provide history."
        result = subprocess.run([sys.executable, str(script), "-", "--format", "text", "--candidates"],
                                input=phrase + "\n", capture_output=True, text=True)
        check(result.returncode == 0, "prepare_units --format text failed")
        spans = json.loads(result.stdout.splitlines()[0]).get("candidates", []) if result.stdout.strip() else []
        check("not by themselves" in spans,
              f"candidate extraction must keep a complete fixed phrase, got {spans}")

        tex = ("\\documentclass{article}\n\\begin{document}\n"
               "\\section{Experiments}\n\\label{sec:exp}\n"
               "At a 1B-token budget the model reaches 63.2.\n\\begin{equation}\nP=1\n\\end{equation}\n"
               "\\begin{table}\n\\begin{tabular}{lr}\nrow & 1 \\\\\n\\end{tabular}\n\\caption{A caption.}\n\\end{table}\n"
               "The check covers all layers at the measured tolerance.\n\\end{document}\n")
        result = subprocess.run([sys.executable, str(script), "-", "--format", "latex"],
                                input=tex, capture_output=True, text=True)
        check(result.returncode == 0, f"prepare_units latex mode failed: {result.stderr.strip()}")
        tex_units = [json.loads(line) for line in result.stdout.splitlines() if line.strip()]
        joined = " ".join(u["text"] for u in tex_units)
        check("At a 1B-token budget" in joined, "latex mode must keep body prose")
        check("The check covers all layers" in joined, "latex mode must keep prose after a table")
        check("P=1" not in joined, "latex mode must drop display math")
        check("row & 1" not in joined, "latex mode must drop table cells")
        check("\\label" not in joined and "\\section" not in joined, "latex mode must drop layout commands")
        check(all(u.get("source_text") for u in tex_units), "latex mode must record source_text")

    # merge_verdicts: null stays untriaged, findings survive, precision is unit-based.
    merge_script = SKILL_DIR / "scripts" / "merge_verdicts.py"
    if merge_script.is_file():
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            (tmp_path / "screen.jsonl").write_text(
                json.dumps({"id": "u1", "line": 1, "claim_negation": None, "negative_contrast": None,
                            "vague_hedge": None, "concessive_hedge": None,
                            "screen_state": "untriaged_control_failed"}) + "\n" +
                json.dumps({"id": "u2", "line": 2, "claim_negation": 0.9, "negative_contrast": 0.1,
                            "vague_hedge": 0.2, "concessive_hedge": 0.1}) + "\n",
                encoding="utf-8")
            (tmp_path / "verdicts.jsonl").write_text(
                json.dumps({"id": "u1", "verdict": "rewrite",
                            "findings": [{"id": "f1", "rule": "R3", "disposition": "confirmed"}]}) + "\n" +
                json.dumps({"id": "u2", "verdict": "rewrite",
                            "findings": [{"id": "f2", "rule": "R2", "disposition": "confirmed"}]}) + "\n",
                encoding="utf-8")
            result = subprocess.run([sys.executable, str(merge_script),
                                     "--screen", str(tmp_path / "screen.jsonl"),
                                     "--verdicts", str(tmp_path / "verdicts.jsonl"),
                                     "--out", str(tmp_path / "table.tsv")],
                                    capture_output=True, text=True)
            check(result.returncode == 0, f"merge_verdicts failed on null probabilities: {result.stderr.strip()}")
            table = (tmp_path / "table.tsv").read_text(encoding="utf-8")
            check("untriaged_control_failed" in table, "merge must keep the untriaged state")
            check("\tnull\t" in table or "null" in table, "merge must print null, not 0, for unrun dimensions")
            findings = (tmp_path / "table.findings.tsv").read_text(encoding="utf-8")
            check("f1" in findings, "merge must preserve span findings")
            check("routing precision 1/1" in result.stderr,
                  f"routing precision must count confirmed rewrites among routed units only: {result.stderr.strip()}")
            check("untriaged 1" in result.stderr, "an untriaged unit must not count as routed")

    if failures:
        print("FAILED")
        for item in failures:
            print(f"  - {item}")
        return 1

    print(f"OK: {SKILL_MD.relative_to(ROOT)}")
    print(f"  references: {len(REQUIRED_REFS)} files")
    print(f"  manifest: {manifest['name']} {manifest.get('version')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
