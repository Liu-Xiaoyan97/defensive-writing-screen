#!/usr/bin/env python3
"""Validate discovery records, NOT review performance or semantic correctness."""
import argparse
from collections import Counter
import json
from pathlib import Path
import re

CATEGORIES = {'assurance', 'intent_apology', 'nonclaim_rebuttal', 'omitted_work',
              'adverse_result', 'repeated_caveat'}


def normalize(text):
    return re.sub(r'\s+', ' ', text).strip() if isinstance(text, str) else ''


def validate(units, records, selected_ids=None, discovery=False, findings=None):
    errors = []
    ids = [u['id'] for u in units]
    by_id = {u['id']: u for u in units}
    selected = ids if selected_ids is None else selected_ids
    if len(ids) != len(set(ids)):
        errors.append('duplicate source unit IDs')
    if len(selected) != len(set(selected)) or set(selected) - set(ids):
        errors.append('invalid selected IDs')
    seen = []
    candidates = 0
    for index, row in enumerate(records):
        if not isinstance(row, dict):
            errors.append(f'{index}: record must be an object')
            continue
        uid = row.get('unit')
        if not isinstance(uid, str):
            errors.append(f'{index}: unit must be a string')
            continue
        seen.append(uid)
        if uid not in by_id:
            errors.append(f'{uid}: unknown unit')
        cs = row.get('candidates')
        if not isinstance(cs, list):
            errors.append(f'{uid}: candidates must be an array')
            continue
        expected = 'candidates' if cs else 'none'
        if row.get('candidate_scan') != expected:
            errors.append(f'{uid}: candidate_scan conflicts with candidates')
        spans = []
        for c in cs:
            candidates += 1
            if not isinstance(c, dict):
                errors.append(f'{uid}: candidate must be an object')
                continue
            for key in ('span', 'category', 'possible_defensive_function'):
                if not isinstance(c.get(key), str) or not c[key].strip():
                    errors.append(f'{uid}: missing candidate {key}')
            if c.get('category') not in CATEGORIES:
                errors.append(f'{uid}: invalid candidate category')
            if discovery:
                if 'decision' in c or 'decision_reason' in c:
                    errors.append(f'{uid}: discovery record must not contain adjudication fields')
            else:
                for key in ('decision', 'decision_reason'):
                    if not isinstance(c.get(key), str) or not c[key].strip():
                        errors.append(f'{uid}: missing candidate {key}')
                if c.get('decision') not in ('issue', 'keep', 'unresolved'):
                    errors.append(f'{uid}: invalid candidate decision')
            span = c.get('span')
            if isinstance(span, str):
                spans.append(span)
                if not span.strip() or normalize(span) not in normalize(by_id.get(uid, {}).get('text', '')):
                    errors.append(f'{uid}: span not in source unit')
        if len(spans) != len(set(spans)):
            errors.append(f'{uid}: duplicate candidate span')
    duplicates = [uid for uid, count in Counter(seen).items() if count > 1]
    missing = sorted(set(selected) - set(seen))
    extra = sorted(set(seen) - set(selected))
    if duplicates:
        errors.append('duplicate scan units: ' + ', '.join(duplicates))
    if missing:
        errors.append('missing selected units: ' + ', '.join(missing))
    if extra:
        errors.append('unexpected scan units: ' + ', '.join(extra))
    linked_finding_count = None
    if findings is not None:
        if discovery:
            errors.append('finding linkage is available only for adjudication records')
        else:
            issue_candidates = [(row.get('unit'), normalize(c.get('span', '')))
                                for row in records if isinstance(row, dict)
                                for c in row.get('candidates', [])
                                if isinstance(c, dict) and c.get('decision') == 'issue']
            positive_findings = [(f.get('unit'), normalize(f.get('span', '')))
                                 for f in findings if isinstance(f, dict)
                                 and f.get('issue_present') is True]
            linked_finding_count = len(positive_findings)
            for unit, span in issue_candidates:
                if not any(funit == unit and fspan and span and
                           (span in fspan or fspan in span)
                           for funit, fspan in positive_findings):
                    errors.append(f'{unit}: issue candidate has no matching positive finding: {span[:80]}')
            for unit, span in positive_findings:
                if not any(cunit == unit and cspan and span and
                           (span in cspan or cspan in span)
                           for cunit, cspan in issue_candidates):
                    errors.append(f'{unit}: positive finding has no matching issue candidate: {span[:80]}')
    return dict(record_valid=not errors, selected_count=len(selected), scan_count=len(records),
                candidate_count=candidates, linked_finding_count=linked_finding_count,
                errors=errors, semantic_correctness='not_verified',
                actual_reading='not_verified')


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--units', type=Path, required=True)
    p.add_argument('--scan', type=Path, required=True)
    p.add_argument('--selected-ids', type=Path)
    p.add_argument('--discovery', action='store_true', help='validate a candidate-only ledger with no verdict fields')
    p.add_argument('--findings', type=Path, help='optionally verify bidirectional issue-candidate/finding linkage')
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    selected = json.loads(args.selected_ids.read_text()) if args.selected_ids else None
    if selected is not None and (not isinstance(selected, list) or any(not isinstance(i, str) for i in selected)):
        p.error('--selected-ids must contain a JSON array of string IDs')
    findings = read_jsonl(args.findings) if args.findings else None
    result = validate(read_jsonl(args.units), read_jsonl(args.scan), selected,
                      discovery=args.discovery, findings=findings)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    return 0 if result['record_valid'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
