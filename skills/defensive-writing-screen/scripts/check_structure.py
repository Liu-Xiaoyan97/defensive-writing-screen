#!/usr/bin/env python3
"""Check a draft for the sections a paper normally carries.

Reads headings only: Markdown ATX headings, or LaTeX \\section and
\\subsection plus the abstract environment. Reports which canonical roles are
present, which are absent, and which section the document ends on. Absence is a
fact about the file, not a verdict: a supplement, an extended abstract, or a
letter legitimately lacks most roles. The agent decides.

Usage:
    python3 check_structure.py draft.md
    python3 check_structure.py draft.tex --json
    cat draft.md | python3 check_structure.py -

Output: a JSON object with roles, missing, last_role, and flags.
Exit code 0 when headings were found, 1 when none were.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Section-level titles only: a subsection such as "Model composition" or
# "Recurrent evaluation" must not be read as the document's method or results
# section. Patterns are anchored at the start of the title, after any numbering.
ROLES = [
    ("abstract", r"^abstract\b"),
    ("introduction", r"^introduction\b"),
    ("related", r"^(?:related (?:work|research|literature)|background|prior work)\b"),
    ("method", r"^(?:methods?|methodology|approach|proposed (?:method|approach|model))\b"),
    ("experiments", r"^(?:experiments?|experimental (?:setup|results)|evaluation|results|empirical (?:study|evaluation))\b"),
    ("conclusion", r"^(?:conclusions?|concluding remarks|summary|conclusions? and (?:outlook|future work)|discussion and conclusions?)\b"),
    ("limitations", r"^(?:limitations?|threats? to validity)\b"),
]
NUMBERING = re.compile(r"^(?:\d+(?:\.\d+)*\.?\s*|[ivx]+\.\s*|[A-Z]\.\s*)")

TEX_HEADING = re.compile(r"\\section\*?\{([^{}]*)\}")
MD_HEADING = re.compile(r"^#{1,2}\s+(.*\S)\s*$")


def classify(title: str) -> list[str]:
    lowered = NUMBERING.sub("", title.strip().lower())
    found = []
    for role, pattern in ROLES:
        if re.search(pattern, lowered):
            found.append(role)
    return found


def headings(path: str | None, text: str) -> list[tuple[int, str]]:
    out: list[tuple[int, str]] = []
    for number, line in enumerate(text.splitlines(), start=1):
        if path and path.endswith((".tex", ".ltx")):
            if "\\begin{abstract}" in line:
                out.append((number, "Abstract"))
                continue
            match = TEX_HEADING.search(line)
            if match:
                out.append((number, match.group(1)))
        else:
            match = MD_HEADING.match(line)
            if match:
                out.append((number, match.group(1)))
    return out


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", nargs="?", default="-")
    parser.add_argument("--json", action="store_true", help="emit JSON only")
    args = parser.parse_args(argv)

    if args.source == "-":
        text = sys.stdin.read()
        path = None
    else:
        path = args.source
        text = Path(path).read_text(encoding="utf-8")

    found = []
    sequence: list[tuple[int, str, str]] = []
    all_headings = headings(path, text)
    for number, title in all_headings:
        roles = classify(title) or [""]
        for role in roles:
            if role and role not in found:
                found.append(role)
            sequence.append((number, title, role))

    if not all_headings:
        print("no headings found", file=sys.stderr)
        return 1

    order = [role for _, _, role in sequence if role]
    last_role = order[-1] if order else "none"
    missing = [role for role, _ in ROLES if role not in found]
    flags = []
    if "conclusion" not in found:
        flags.append("missing_conclusion")
    if last_role == "limitations" and "conclusion" not in found:
        flags.append("ends_on_limitations")
    if "limitations" not in found:
        flags.append("missing_limitations")
    if "related" not in found:
        flags.append("related_work_absent_or_folded")
    if len(found) < 3:
        flags.append("sparse_structure")

    result = {
        "source": path or "stdin",
        "heading_count": len(sequence),
        "roles": [role for role, _ in ROLES if role in found],
        "missing": missing,
        "last_role": last_role,
        "flags": flags,
        "sequence": [{"line": number, "title": title, "role": role} for number, title, role in sequence],
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=1))
    else:
        print(f"source {result['source']} | headings {len(sequence)} | roles {', '.join(result['roles']) or 'none'}")
        print(f"missing: {', '.join(missing) or 'none'} | last: {last_role}")
        for flag in flags:
            print(f"  flag: {flag}")
        for item in result["sequence"]:
            role = item["role"] or "-"
            print(f"  {item['line']:>4}  {role:<12} {item['title']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
