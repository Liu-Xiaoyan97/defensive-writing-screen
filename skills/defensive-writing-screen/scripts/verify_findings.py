#!/usr/bin/env python3
"""Validate evidence anchors and the two-stage review record, without a model call.

This checks a record, NOT the truth of an agent's semantic judgments. Agent-supplied
facts/strength/repair checks are explicit assertions, not an automatic entailment test.
Usage: verify_findings.py --units units.jsonl --findings findings.jsonl --out checked.jsonl
       [--source draft.txt]
Each finding: id, unit, quote, span, issue_present (true/false/null), issue_reason,
context_evidence, action (rewrite/delete/keep), proposal, facts_preserved,
strength_preserved, issue_removed (true/false/null), preservation_reason.
For delete also: removal_preserves, evidence_complete. The source must be checked
live for an executable suggestion; without --source the snapshot can be audited,
but the effective disposition is unresolved (provisional_disposition is retained).
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import re
import sys
from pathlib import Path

from handoff import read_rows


def normalized(text):
    # Only reflow whitespace: never remove words, numbers, punctuation or hyphens.
    return re.sub(r'\s+', ' ', text).strip() if isinstance(text, str) else ''


def has_text(value):
    return isinstance(value, str) and bool(value.strip()) and value.strip().lower() not in {'unknown', 'none', 'n/a'}


def decide(row):
    issue = row.get('issue_present')
    action = row.get('action')
    safe = row.get('facts_preserved') is True and row.get('strength_preserved') is True
    if issue is None:
        return 'unresolved'
    if issue is False:
        if action == 'keep':
            return 'keep'
        return 'optional' if safe else 'unresolved'
    repaired = row.get('issue_removed') is True
    if not safe or not repaired or action == 'keep':
        return 'partial'
    if action == 'delete' or row.get('deletes_sentence') is True:
        score = row.get('removal_preserves')
        if not (type(score) in (int, float) and math.isfinite(score) and 0.65 <= score <= 1
                and row.get('evidence_complete') is True):
            return 'partial'
    return 'confirmed'


def verify(row, unit, source=None):
    errors = []
    for key in ('issue_present', 'facts_preserved', 'strength_preserved', 'issue_removed'):
        if key not in row or (row[key] is not None and type(row[key]) is not bool):
            errors.append(f'{key} must be an explicit boolean or null')
    if type(row.get('deletes_sentence')) is not bool:
        errors.append('deletes_sentence must be explicit, including deletions inside a rewrite')
    if row.get('action') not in ('rewrite', 'delete', 'keep'):
        errors.append('action must be rewrite/delete/keep')
    for key in ('id', 'unit', 'quote', 'span', 'issue_reason', 'context_evidence'):
        if not has_text(row.get(key)):
            errors.append(f'missing {key}')
    quote, span = normalized(row.get('quote', '')), normalized(row.get('span', ''))
    raw = unit.get('source_text')
    if not isinstance(raw, str) or not raw:
        errors.append('missing raw source snapshot; regenerate units')
    elif not quote or normalized(raw).count(quote) != 1:
        errors.append('quote must occur exactly once in raw source (whitespace reflow only)')
    if not span or span not in quote:
        errors.append('span must be inside the quoted source')
    if row.get('action') == 'rewrite':
        if not has_text(row.get('proposal')) or normalized(row['proposal']) == quote:
            errors.append('rewrite requires a changed proposal')
    if row.get('action') == 'delete' and row.get('proposal') not in ('', None):
        errors.append('delete requires an empty proposal')
    if row.get('action') == 'keep' and row.get('proposal') not in ('KEEP', '', None):
        errors.append('keep may not carry a replacement')
    if row.get('action') != 'keep' and not has_text(row.get('preservation_reason')):
        errors.append('missing preservation_reason')
    if (row.get('action') == 'delete' or row.get('deletes_sentence') is True) and row.get('issue_present') is not True:
        errors.append('deletion is restricted to independently established defensive spans')

    source_status = 'snapshot_only'
    if source is not None:
        start, end = unit.get('start'), unit.get('end')
        sha = hashlib.sha256(source.encode('utf-8')).hexdigest()
        if unit.get('source_sha256') != sha:
            errors.append('source hash changed or missing')
        lines = source.split('\n')
        if type(start) is not int or type(end) is not int or not 1 <= start <= end <= len(lines):
            errors.append('invalid LF source line range')
        elif '\n'.join(lines[start-1:end]) != raw:
            errors.append('source snapshot differs from the live line range')
        source_status = 'live_checked' if not errors else 'invalid'
    provisional = decide(row) if not errors else 'unresolved'
    if row.get('disposition') is not None and row['disposition'] != provisional:
        errors.append(f"declared disposition {row['disposition']!r} conflicts with {provisional!r}")
    effective = provisional if not errors and source_status == 'live_checked' else 'unresolved'
    return {**row, 'provisional_disposition': provisional, 'disposition': effective,
            'record_valid': not errors, 'anchor_status': source_status,
            'semantic_checks': 'agent_assertions_not_automated_proof',
            'errors': errors}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--units', type=Path, required=True)
    parser.add_argument('--findings', type=Path, required=True)
    parser.add_argument('--source', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(argv)
    units = {u['id']: u for u in read_rows(args.units)}
    rows = read_rows(args.findings)
    source = args.source.read_bytes().decode('utf-8') if args.source else None
    results = []
    for row in rows:
        if row.get('unit') not in units:
            results.append({**row, 'record_valid': False, 'disposition': 'unresolved',
                            'errors': ['unknown unit']})
        else:
            results.append(verify(row, units[row['unit']], source))
    args.out.write_text(''.join(json.dumps(r, ensure_ascii=False)+'\n' for r in results), encoding='utf-8')
    counts = {k:sum(r['disposition']==k for r in results) for k in ('confirmed','partial','optional','keep','unresolved')}
    print(json.dumps(counts), file=sys.stderr)
    return 0 if all(r['record_valid'] for r in results) else 1


if __name__ == '__main__':
    raise SystemExit(main())
