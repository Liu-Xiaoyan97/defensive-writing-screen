#!/usr/bin/env python3
"""Merge a Jev screen, an agent verdict file, and optional independent labels.

Makes the per-unit record reproducible instead of narrated: the screen supplies
probabilities and routing state, the agent supplies one verdict per unit, and an
independent label file supplies the cross-check.

Usage:
    python3 merge_verdicts.py --screen screen.jsonl --verdicts verdicts.jsonl \
        [--labels labels.jsonl] [--threshold 0.65] --out table.tsv

Inputs (one JSON object per line):
    screen    {"id": "...", "line": 12, "neg": 0.1, "con": 0.2,
               "hedge": 0.7, "conc": 0.3, "tail": 0.1}
    verdicts  {"id": "...", "verdict": "rewrite"|"keep",
               "category": "...", "span": "...", "reason": "..."}
    labels    {"id": "...", "verdict": "rewrite"|"keep"}

Output: a TSV with triage, screen_state, verdict, category, span, label, agree.
Summary counts go to stderr. Exit code 1 on malformed input or missing units.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

DIMENSIONS = ("neg", "con", "hedge", "conc", "tail")


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise SystemExit(f"{path}:{number}: {exc}") from exc
    return rows


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--screen", required=True, type=Path)
    parser.add_argument("--verdicts", required=True, type=Path)
    parser.add_argument("--labels", type=Path)
    parser.add_argument("--threshold", type=float, default=0.65)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)

    screen = {row["id"]: row for row in read_jsonl(args.screen)}
    verdicts = {row["id"]: row for row in read_jsonl(args.verdicts)}
    labels = {row["id"]: row for row in read_jsonl(args.labels)} if args.labels else {}

    missing_screen = [i for i in verdicts if i not in screen]
    missing_verdict = [i for i in screen if i not in verdicts]
    if missing_screen or missing_verdict:
        print(
            f"unit mismatch: {len(missing_screen)} verdicts without a screen row, "
            f"{len(missing_verdict)} screen rows without a verdict",
            file=sys.stderr,
        )
        for unit in (missing_screen + missing_verdict)[:10]:
            print(f"  {unit}", file=sys.stderr)
        return 1

    header = ["id", "line", *DIMENSIONS, "triage", "triage_dim", "screen_state",
              "verdict", "category", "basis", "rule", "span", "reason", "label", "agree"]
    lines = ["\t".join(header)]
    routed = rewritten = agree = comparable = 0
    rewrite_labeled = rewrite_found = 0

    for unit, row in screen.items():
        values = {dim: float(row.get(dim, 0.0)) for dim in DIMENSIONS}
        dim = max(values, key=values.get)
        triage = values[dim]
        is_routed = triage >= args.threshold
        routed += is_routed
        verdict = verdicts[unit]
        action = verdict["verdict"]
        rewritten += action == "rewrite"
        label = labels.get(unit, {}).get("verdict", "")
        match = "" if not label else ("Y" if label == action else "N")
        if label:
            comparable += 1
            agree += match == "Y"
            if label == "rewrite":
                rewrite_labeled += 1
                rewrite_found += action == "rewrite"
        lines.append("\t".join([
            unit,
            str(row.get("line", "")),
            *(f"{values[d]:.3f}" for d in DIMENSIONS),
            f"{triage:.3f}",
            dim,
            "routed" if is_routed else "not_selected",
            action,
            str(verdict.get("category", "")),
            str(verdict.get("basis", "")),
            str(verdict.get("rule", "")),
            str(verdict.get("span", "")),
            str(verdict.get("reason", "")),
            label,
            match,
        ]))

    args.out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"units {len(screen)} | routed {routed} | rewrites {rewritten}", file=sys.stderr)
    if labels:
        print(
            f"agreement {agree}/{comparable} | recall on labelled rewrites "
            f"{rewrite_found}/{rewrite_labeled} | routing precision "
            f"{rewritten}/{routed}" if routed else "agreement",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
