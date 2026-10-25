"""Record validation tests, not model-level semantic accuracy tests."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'skills' / 'defensive-writing-screen' / 'scripts'))
from verify_candidate_scan import validate


class CandidateScanTests(unittest.TestCase):
    def setUp(self):
        self.units = [{'id':'p0','text':'We do not invent a new algorithm.'},
                      {'id':'p1','text':'Three conditions were measured.'}]
        self.candidate = dict(span='We do not invent a new algorithm.', category='nonclaim_rebuttal',
                              possible_defensive_function='Denial of a contribution.', decision='keep',
                              decision_reason='Attributes novelty rather than inventing an algorithm.')
        self.records = [dict(unit='p0',candidate_scan='candidates',candidates=[self.candidate]),
                        dict(unit='p1',candidate_scan='none',candidates=[])]

    def test_full_scan_and_not_semantic_proof(self):
        r=validate(self.units,self.records)
        self.assertTrue(r['record_valid'])
        self.assertEqual(r['semantic_correctness'],'not_verified')
        self.assertEqual(r['actual_reading'],'not_verified')
        self.assertEqual(r['candidate_count'],1)

    def test_discovery_ledger_is_separate_from_adjudication(self):
        candidate={k:v for k,v in self.candidate.items() if k not in ('decision','decision_reason')}
        records=[dict(unit='p0',candidate_scan='candidates',candidates=[candidate]),
                 dict(unit='p1',candidate_scan='none',candidates=[])]
        self.assertTrue(validate(self.units,records,discovery=True)['record_valid'])
        self.assertFalse(validate(self.units,records)['record_valid'])
        judged=[dict(unit='p0',candidate_scan='candidates',candidates=[self.candidate]),
                dict(unit='p1',candidate_scan='none',candidates=[])]
        self.assertFalse(validate(self.units,judged,discovery=True)['record_valid'])

    def test_missing_or_duplicate_units_fail(self):
        self.assertFalse(validate(self.units,self.records[:1])['record_valid'])
        self.assertFalse(validate(self.units,self.records+[self.records[0]])['record_valid'])

    def test_screened_scope_is_explicit(self):
        self.assertTrue(validate(self.units,self.records[:1],['p0'])['record_valid'])
        self.assertFalse(validate(self.units,self.records,['p0'])['record_valid'])
        self.assertFalse(validate(self.units,self.records,[])['record_valid'])

    def test_none_cannot_hide_candidates(self):
        self.records[0]['candidate_scan']='none'
        self.assertFalse(validate(self.units,self.records)['record_valid'])

    def test_literal_span_and_required_reason(self):
        self.candidate['span']='Not in the source'
        self.assertFalse(validate(self.units,self.records)['record_valid'])
        self.candidate['span']=self.units[0]['text']
        self.candidate['decision_reason']=''
        self.assertFalse(validate(self.units,self.records)['record_valid'])

    def test_category_decision_and_duplicate_candidate(self):
        self.candidate['decision']='confirmed'
        self.assertFalse(validate(self.units,self.records)['record_valid'])
        self.candidate['decision']='keep'
        self.candidate['category']='unknown'
        self.assertFalse(validate(self.units,self.records)['record_valid'])
        self.candidate['category']='nonclaim_rebuttal'
        self.records[0]['candidates'].append(self.candidate.copy())
        self.assertFalse(validate(self.units,self.records)['record_valid'])

    def test_malformed_records_do_not_count_as_scanned(self):
        for records in ([None], [{'unit':[]}], [{'unit':'p0','candidates':None}]):
            self.assertFalse(validate(self.units,records)['record_valid'])

    def test_issue_candidate_and_positive_finding_link_both_ways(self):
        issue = dict(self.candidate, decision='issue', decision_reason='Exact issue rationale.')
        records=[dict(unit='p0',candidate_scan='candidates',candidates=[issue]),
                 dict(unit='p1',candidate_scan='none',candidates=[])]
        finding=dict(unit='p0',span='We do not invent a new algorithm.',issue_present=True)
        result=validate(self.units,records,findings=[finding])
        self.assertTrue(result['record_valid'],result['errors'])
        self.assertEqual(result['linked_finding_count'],1)

    def test_missing_positive_finding_link_fails(self):
        issue = dict(self.candidate, decision='issue', decision_reason='Exact issue rationale.')
        records=[dict(unit='p0',candidate_scan='candidates',candidates=[issue]),
                 dict(unit='p1',candidate_scan='none',candidates=[])]
        result=validate(self.units,records,findings=[])
        self.assertFalse(result['record_valid'])
        self.assertIn('issue candidate has no matching positive finding',result['errors'][0])

    def test_untracked_positive_finding_fails(self):
        records=[dict(unit='p0',candidate_scan='candidates',candidates=[self.candidate]),
                 dict(unit='p1',candidate_scan='none',candidates=[])]
        finding=dict(unit='p0',span='We do not invent a new algorithm.',issue_present=True)
        result=validate(self.units,records,findings=[finding])
        self.assertFalse(result['record_valid'])
        self.assertTrue(any('positive finding has no matching issue candidate' in e for e in result['errors']))

    def test_malformed_issue_span_with_linkage_fails_cleanly(self):
        malformed=dict(self.candidate,span=7,decision='issue',decision_reason='Bad span.')
        records=[dict(unit='p0',candidate_scan='candidates',candidates=[malformed]),
                 dict(unit='p1',candidate_scan='none',candidates=[])]
        result=validate(self.units,records,findings=[])
        self.assertFalse(result['record_valid'])


if __name__=='__main__':
    unittest.main()
