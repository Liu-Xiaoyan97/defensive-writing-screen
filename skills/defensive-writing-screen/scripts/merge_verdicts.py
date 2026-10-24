#!/usr/bin/env python3
"""Merge a Jev screen, agent verdicts, and optional independent labels.

The screen supplies probabilities and routing state; the agent supplies one
verdict per unit plus independent span findings; the labels file supplies an
external comparison when one exists. Null probabilities stay null: a missing or
failed judgment is untriaged, never 0 and never "not_selected".

Usage:
    python3 merge_verdicts.py --screen screen.jsonl --verdicts verdicts.jsonl \
        [--labels labels.jsonl] [--threshold 0.65] --out table.tsv

Input fields (one JSON object per line):

  screen    {"id": "...", "line": 12, "claim_negation": 0.1, "negative_contrast": 0.2,
             "vague_hedge": 0.7, "concessive_hedge": 0.3}
            Legacy short keys (neg, con, hedge, conc) are accepted. Missing or null
            dimensions are treated as null, so the unit cannot be routed on its score.
            "untriaged_error"/"untriaged_no_caller"/"untriaged_control_failed" in
            "screen_state" marks a unit that was not scored.
  verdicts  {"id": "...", "verdict": "keep"|"rewrite"|"narrative"|"mixed"|"unresolved",
             "findings": [{"id": "...", "span": "...", "rule": "R2",
                           "disposition": "confirmed"|"optional"|"keep"|"unresolved"}]}
            A unit without findings may still carry "span"/"rule" for one finding.
  labels    {"id": "...", "verdict": "rewrite"|"keep"}

Output: TSV of per-unit routing plus a findings TSV written next to --out.
Summary counts go to stderr. Exit code 1 on malformed input or unit mismatch.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

DIMENSIONS = {
    "claim_negation": ("claim_negation", "neg"),
    "negative_contrast": ("negative_contrast", "con"),
    "vague_hedge": ("vague_hedge", "hedge"),
    "concessive_hedge": ("concessive_hedge", "conc"),
}
UNRUN_STATES = ("untriaged_error", "untriaged_no_caller", "untriaged_control_failed")


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


def probability(row: dict, keys: tuple[str, ...]) -> float | None:
    for key in keys:
        if key in row:
            value = row[key]
            if value is None or value == "":
                return None
            try:
                return float(value)
            except (TypeError, ValueError):
                raise SystemExit(f"{row.get('id')}: non-numeric {key}={value!r}")
    return None


def findings_for(verdict: dict) -> list[dict]:
    items = verdict.get("findings")
    if items:
        return [dict(item, unit=verdict["id"]) for item in items]
    if verdict.get("span") or verdict.get("rule"):
        return [{**verdict, "unit": verdict["id"]}]
    return []


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
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
        print(f"unit mismatch: {len(missing_screen)} verdicts without a screen row, "
              f"{len(missing_verdict)} screen rows without a verdict", file=sys.stderr)
        for unit in (missing_screen + missing_verdict)[:10]:
            print(f"  {unit}", file=sys.stderr)
        return 1

    header = ["id", "line", *DIMENSIONS, "triage", "triage_dim", "screen_state",
              "verdict", "finding_count", "label", "agree"]
    lines = ["\t".join(header)]
    finding_lines = ["\t".join(["unit", "finding", "rule", "span", "disposition",
                                "protection", "proposal", "reason"])]
    routed = untriaged = confirmed_in_routed = 0
    agree = comparable = 0
    rewrite_labeled = rewrite_found = 0
    finding_count = confirmed_total = optional_total = 0

    for unit, row in screen.items():
        values = {name: probability(row, keys) for name, keys in DIMENSIONS.items()}
        scored = [v for v in values.values() if v is not None]
        dim = max((k for k, v in values.items() if v is not None),
                  key=lambda k: values[k], default="")
        triage = values[dim] if dim else None
        state = row.get("screen_state") or ("scored" if dim else "untriaged_error")
        is_routed = state not in UNRUN_STATES and triage is not None and triage >= args.threshold
        routed += is_routed
        untriaged += not scored or state in UNRUN_STATES

        verdict = verdicts[unit]
        action = verdict.get("verdict", "")
        findings = findings_for(verdict)
        finding_count += len(findings)
        confirmed = [f for f in findings if (f.get("disposition") or "") == "confirmed"]
        optional = [f for f in findings if (f.get("disposition") or "") == "optional"]
        confirmed_total += len(confirmed)
        optional_total += len(optional)
        if is_routed and (confirmed or action == "rewrite"):
            confirmed_in_routed += 1

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
            str(row.get("line", row.get("start", ""))),
            *(("null" if values[d] is None else f"{values[d]:.3f}") for d in DIMENSIONS),
            "null" if triage is None else f"{triage:.3f}",
            dim,
            state,
            action,
            str(len(findings)),
            label,
            match,
        ]))
        for f in findings:
            finding_lines.append("\t".join(str(f.get(key, "")) for key in
                                           ("unit", "id", "rule", "span", "disposition",
                                            "protection", "proposal", "reason")))

    args.out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    args.out.with_suffix(".findings.tsv").write_text("\n".join(finding_lines) + "\n", encoding="utf-8")
    print(f"units {len(screen)} | routed {routed} | untriaged {untriaged} | "
          f"findings {finding_count} (confirmed {confirmed_total}, optional {optional_total})",
          file=sys.stderr)
    if routed:
        print(f"routing precision {confirmed_in_routed}/{routed}", file=sys.stderr)
    else:
        print("routing precision not computable: no scored routed unit", file=sys.stderr)
    if labels:
        print(f"agreement {agree}/{comparable} | recall on labelled rewrites "
              f"{rewrite_found}/{rewrite_labeled}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
