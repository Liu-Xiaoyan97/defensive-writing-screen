#!/usr/bin/env python3
"""Aggregate review records without counting KEEP/optional as detection errors.

--verdicts accepts flat checked findings (unit/id/disposition) or legacy unit rows
(id/verdict/findings). Unreported screen units are not_reviewed, never clean.
Optional labels: {id: unit_id, issue_present: true|false|null}. Metrics are unit-level
and only cover reviewed, explicitly labelled units; no overall recall is inferred.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path
from handoff import read_rows

DIMENSIONS = {'claim_negation': ('claim_negation','neg'),
              'negative_contrast': ('negative_contrast','con'),
              'vague_hedge': ('vague_hedge','hedge'),
              'concessive_hedge': ('concessive_hedge','conc'),
              'effort_assurance': ('effort_assurance','effort'),
              'attribution_hedge': ('attribution_hedge','attrib'),
              'completeness_assurance': ('completeness_assurance','complete'),
              'omission_value_judgment': ('omission_value_judgment','omit')}
# Specialized dimensions drive the confidence tier. They cover fewer defect families than the
# generic ones, so a low tier must never discard a candidate; it only routes to agent review.
GENERIC = ('claim_negation','negative_contrast','vague_hedge','concessive_hedge')
SPECIALIZED = ('effort_assurance','attribution_hedge',
               'completeness_assurance','omission_value_judgment')
TIERS = (('high',0.6),('medium',0.2),('low',0.0))


def confidence_tier(row):
    """Return (tier, score) from the specialized dimensions.

    A record produced before the specialized dimensions existed carries none of them. That is a
    missing tier, not a failed unit: return (None, None) and let the caller fall back to the
    generic routing threshold so older screens stay readable.
    """
    values = [probability(row, DIMENSIONS[name]) for name in SPECIALIZED]
    present = [v for v in values if v is not None]
    if not present:
        return None, None
    score = max(present)
    for name, floor in TIERS:
        if score >= floor:
            return name, score
    return 'low', score
UNRUN_STATES = ('untriaged_error','untriaged_no_caller','untriaged_control_failed')
DISPOSITIONS = ('confirmed','partial','optional','keep','unresolved')


def probability(row, keys):
    for key in keys:
        if key in row:
            value = row[key]
            if value is None or value == '':
                return None
            if type(value) not in (int,float) or not math.isfinite(value) or not 0 <= value <= 1:
                raise ValueError(f"{row['id']}: invalid probability {key}")
            return value
    return None


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--screen', required=True, type=Path)
    parser.add_argument('--verdicts', required=True, type=Path)
    parser.add_argument('--labels', type=Path)
    parser.add_argument('--reviewed-units', type=Path,
                        help='JSON array of unit ids actually inspected, including units with no findings')
    parser.add_argument('--threshold', type=float, default=0.65)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args(argv)
    if not 0 <= args.threshold <= 1:
        raise SystemExit('threshold must be in [0,1]')
    screen = {r['id']:r for r in read_rows(args.screen)}
    labels = {r['id']:r for r in read_rows(args.labels)} if args.labels else {}
    grouped = defaultdict(list)
    review_ids = json.loads(args.reviewed_units.read_text()) if args.reviewed_units else []
    if not isinstance(review_ids, list) or any(not isinstance(uid, str) for uid in review_ids):
        raise SystemExit('reviewed-units must be a JSON array of ids')
    if len(set(review_ids)) != len(review_ids) or set(review_ids)-set(screen):
        raise SystemExit('duplicate or unknown reviewed unit')
    reviewed = set(review_ids)
    for r in read_rows(args.verdicts):
        uid = r.get('unit', r['id'])
        if uid not in screen:
            raise SystemExit(f'unknown review unit: {uid}')
        reviewed.add(uid)
        items = [r] if 'unit' in r else r.get('findings', [])
        for f in items:
            if f.get('disposition') not in DISPOSITIONS:
                raise SystemExit(f"{f.get('id')}: missing/invalid disposition")
            if f.get('record_valid') is False and f['disposition'] != 'unresolved':
                raise SystemExit('invalid record cannot count as a finding')
            grouped[uid].append(f)
    if set(labels)-set(screen):
        raise SystemExit('labels contain unknown units')
    for label in labels.values():
        if label.get('issue_present') is not None and type(label['issue_present']) is not bool:
            raise SystemExit('label issue_present must be boolean or null')
    totals = Counter()
    routes = untriaged = positive_routes = tp = fp = fn = tn = 0
    tiers = Counter()
    table = [['id','screen_state','triage','tier','tier_score','review_state','confirmed','partial','optional','keep','unresolved']]
    spans = [['unit','id','disposition','span','proposal','reason']]
    for uid, r in screen.items():
        values = [probability(r, keys) for keys in DIMENSIONS.values()]
        generic = [probability(r, DIMENSIONS[name]) for name in GENERIC]
        complete = all(v is not None for v in generic) and r.get('ok', True) is not False
        state = r.get('screen_state') or ('scored' if complete else 'untriaged_error')
        if state in UNRUN_STATES:
            complete = False
        if not complete and state not in UNRUN_STATES:
            state = 'untriaged_error'
        score = max(generic) if complete else None
        routed = score is not None and score >= args.threshold
        tier, tier_score = confidence_tier(r) if complete else (None, None)
        tiers[tier] += 1
        routes += routed
        untriaged += not complete
        c = Counter(f['disposition'] for f in grouped[uid])
        totals.update(c)
        predicted = bool(c['confirmed']+c['partial'])
        positive_routes += routed and predicted
        truth = labels.get(uid, {}).get('issue_present')
        if uid in reviewed and truth is not None and not c['unresolved']:
            tp += predicted and truth
            fp += predicted and not truth
            fn += not predicted and truth
            tn += not predicted and not truth
        table.append([uid,state,'null' if score is None else score,
                      'reviewed' if uid in reviewed else 'not_reviewed',*[c[d] for d in DISPOSITIONS]])
        for f in grouped[uid]:
            spans.append([uid,f.get('id',''),f['disposition'],f.get('span',''),f.get('proposal',''),
                          f.get('issue_reason', f.get('reason',''))])
    for path, data in [(args.out,table),(args.out.with_suffix('.findings.tsv'),spans)]:
        with path.open('w',encoding='utf-8',newline='') as handle:
            csv.writer(handle,delimiter='\t').writerows(data)
    print(f'units {len(screen)} | reviewed {len(reviewed)} | routed {routes} | untriaged {untriaged}',file=sys.stderr)
    print('span counts '+json.dumps({d:totals[d] for d in DISPOSITIONS}),file=sys.stderr)
    print(f'agent positive yield among scored routes {positive_routes}/{routes} (not precision)',file=sys.stderr)
    if labels:
        print(f'independently labelled reviewed units: TP {tp} FP {fp} FN {fn} TN {tn}',file=sys.stderr)
        print(f'labelled-unit precision {tp}/{tp+fp}; recall on labelled reviewed units {tp}/{tp+fn}',file=sys.stderr)
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
