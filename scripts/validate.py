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
REQUIRED_REFS = ["references/questions.md", "references/rewrite-guide.md", "references/cases.md"]
REQUIRED_SECTIONS = ["## SOP", "## Working without Jev", "## Reporting"]

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
    for step in range(1, 8):
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
        for marker in ["## Core rule", "## Rewrite procedure", "Kiterlin", "MIT"]:
            check(marker in guide_text, f"rewrite guide missing: {marker}")

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
