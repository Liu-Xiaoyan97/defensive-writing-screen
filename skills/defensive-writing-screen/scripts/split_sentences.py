#!/usr/bin/env python3
"""Optional sentence triage with exact parent offsets and full local context.

Sentence splitting is a heuristic, not a grammatical or semantic classifier.
Run triage on this file only when paragraph screening needs finer inspection.
Usage: python3 split_sentences.py units.jsonl > sentences.jsonl
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path

from handoff import read_rows, unit_snapshot

BOUNDARY = re.compile(r'(?<=[.!?。！？])\s+(?=[A-Z0-9(\["\u2018\u201c\u4e00-\u9fff])')


def sentence_spans(text):
    """Return exact slices; do not drop short sentences or normalize their words."""
    boundaries = [0] + [m.end() for m in BOUNDARY.finditer(text)] + [len(text)]
    for left, right in zip(boundaries, boundaries[1:]):
        while left < right and text[left].isspace():
            left += 1
        while right > left and text[right-1].isspace():
            right -= 1
        if left < right:
            yield left, right, text[left:right]


def sentences(text):
    return [part for _, _, part in sentence_spans(text)]


def split_units(rows):
    if len({r['id'] for r in rows}) != len(rows):
        raise ValueError('duplicate unit ids')
    for i, row in enumerate(rows):
        neighbors = [unit_snapshot(rows[j]) for j in (i-1, i+1) if 0 <= j < len(rows)]
        for n, (start, end, text) in enumerate(sentence_spans(row['text'])):
            yield {'id': f"{row['id']}_s{n}", 'parent': row['id'],
                   'start': row.get('start'), 'end': row.get('end'),
                   'line_range_kind': 'parent_unit', 'char_start': start, 'char_end': end,
                   'text': text, 'context': {'parent': unit_snapshot(row), 'neighbors': neighbors}}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('units', nargs='?', default='-')
    args = parser.parse_args(argv)
    rows = read_rows(Path(args.units)) if args.units != '-' else [json.loads(l) for l in sys.stdin if l.strip()]
    emitted = 0
    for row in split_units(rows):
        print(json.dumps(row, ensure_ascii=False))
        emitted += 1
    print(f'{emitted} sentence(s) from {len(rows)} unit(s); exact offsets, full context', file=sys.stderr)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
