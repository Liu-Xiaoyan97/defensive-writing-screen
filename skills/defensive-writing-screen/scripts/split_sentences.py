#!/usr/bin/env python3
"""Split screening units into sentences so Jev can score finer than a paragraph.

Random sampling existed only because review attention was assumed expensive. When Jev
calls are free, recall should come from deterministic granularity instead of luck.

Usage:
    python3 split_sentences.py units.jsonl > sentences.jsonl

Input fields: id, start, end, text.
Output fields: id (parent_sN), parent, start, end, text (one sentence).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

BOUNDARY = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9(\[\"\u2018\u201c])")
MIN_CHARS = 30


def sentences(text: str) -> list[str]:
    parts = [part.strip() for part in BOUNDARY.split(text)]
    merged: list[str] = []
    for part in parts:
        if merged and len(part) < MIN_CHARS:
            merged[-1] = f"{merged[-1]} {part}"
        else:
            merged.append(part)
    return [part for part in merged if part]


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("units", nargs="?", default="-")
    args = parser.parse_args(argv)

    rows = read_jsonl(Path(args.units)) if args.units != "-" else [
        json.loads(line) for line in sys.stdin if line.strip()]
    emitted = 0
    for row in rows:
        for index, sentence in enumerate(sentences(row["text"])):
            print(json.dumps({"id": f"{row['id']}_s{index}", "parent": row["id"],
                              "start": row.get("start"), "end": row.get("end"),
                              "text": sentence}, ensure_ascii=False))
            emitted += 1
    print(f"{emitted} sentence(s) from {len(rows)} unit(s)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
