"""Offline behavior and contract regression tests; no semantic accuracy claim."""
import contextlib
import hashlib
import importlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT/'skills'/'defensive-writing-screen'
SCRIPTS = SKILL/'scripts'
sys.path.insert(0, str(SCRIPTS))
import handoff
import split_sentences
import run_screen
import verify_findings
import merge_verdicts
import verify_candidate_scan


def unit(i, text=None):
    text = text or f'The measurement in setting {i} is reported here.'
    return dict(id=f'draft_p{i}', start=i+1, end=i+1, text=text, source_text=text,
                source_sha256=handoff.digest(text), line_basis='LF')


def score(u, value=0.1, ok=True):
    return dict(id=u['id'],ok=ok,triage=value,triage_dim='claim_negation',
                claim_negation=value,negative_contrast=0.01,vague_hedge=0.01,
                concessive_hedge=0.01,text_sha256=handoff.digest(u['text']))


def fixture():
    u=unit(0,'We humbly present measurements from two settings.')
    f=dict(id='f1',unit=u['id'],quote=u['text'],span='humbly',issue_present=True,
           issue_reason='Unnecessary authorial humility.',context_evidence='The stated scope is two settings.',
           action='rewrite',deletes_sentence=False,proposal='We present measurements from two settings.',
           facts_preserved=True,strength_preserved=True,issue_removed=True,
           preservation_reason='The scope and measurement claim are unchanged.')
    return u,f


class PreparationTests(unittest.TestCase):
    def prepare(self,text,*args):
        p=subprocess.run([sys.executable,str(SCRIPTS/'prepare_units.py'),'-',*args],
                         input=text,text=True,capture_output=True)
        self.assertEqual(p.returncode,0,p.stderr)
        return [json.loads(l) for l in p.stdout.splitlines()]

    def test_raw_snapshots_and_lf_lines(self):
        text='First sentence across\n two lines.\n\n\fNext page stays on LF line four.\n'
        rows=self.prepare(text)
        self.assertEqual(rows[1]['start'],4)
        self.assertEqual(rows[0]['source_text'],'First sentence across\n two lines.')
        self.assertTrue(all(r['source_sha256']==handoff.digest(text) for r in rows))

    def test_candidates_are_substrings(self):
        text='本文并不声称解决所有问题，也无意证明该方法总是最优。\n\n设备通电时不得进行校准。\n'
        rows=self.prepare(text,'--candidates','--min-chars','8')
        self.assertEqual(len(rows),2)
        self.assertTrue(all(c in r['text'] for r in rows for c in r['candidates']))
        rows=self.prepare('Within the memory, the states do not by themselves provide history.','--candidates')
        self.assertIn('not by themselves',rows[0]['candidates'])

    def test_latex_body_caption_and_raw_source(self):
        text=('\\documentclass{article}\n\\begin{document}\n\\section{Setup}\n\\label{sec:x}\n'
              'The test measures both conditions.\n\\begin{equation}\nP=1\n\\end{equation}\n'
              '\\begin{table}\n\\begin{tabular}{lr}\nrow & 1 \\\\\n\\end{tabular}\n'
              '\\caption{Two conditions are measured.}\n\\end{table}\n'
              'The measured scope remains fixed.\n\\end{document}\n')
        rows=self.prepare(text,'--format','latex')
        joined=' '.join(r['text'] for r in rows)
        self.assertIn('Two conditions are measured.',joined)
        self.assertIn('The measured scope remains fixed.',joined)
        self.assertNotIn('P=1',joined)
        self.assertNotIn('row & 1',joined)
        for r in rows:
            self.assertEqual(r['source_text'],'\n'.join(text.split('\n')[r['start']-1:r['end']]))

    def test_structure_smoke(self):
        p=subprocess.run([sys.executable,str(SCRIPTS/'check_structure.py'),'-'],
                         input='# Abstract\n\nText.\n\n# Limitations\n\nText.\n',text=True,capture_output=True)
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertIn('missing_conclusion',p.stdout)
        self.assertIn('ends_on_limitations',p.stdout)


class PacketTests(unittest.TestCase):
    def test_spaced_sample_endpoints_and_small_population(self):
        self.assertEqual(handoff.spaced_sample(list(range(20)),3),[0,9,19])
        self.assertEqual(handoff.spaced_sample([1,2],12),[1,2])
        self.assertEqual(handoff.spaced_sample([1,2],0),[])
        self.assertEqual(handoff.spaced_sample([1,2,3],1),[2])

    def test_sampling_excludes_all_routes(self):
        us=[unit(i) for i in range(20)]
        rs=[score(u,0.9 if i in (0,7) else 0.1) for i,u in enumerate(us)]
        packet=handoff.build_packet(us,rs,sample=3,marker_ids={us[12]['id']})
        self.assertEqual(packet['selected_count'],6)
        self.assertTrue(set(packet['sample_ids']).isdisjoint({us[i]['id'] for i in (0,7,12)}))
        self.assertEqual(len({p['unit']['id'] for p in packet['items']}),6)

    def test_full_text_neighbors_and_all_sentence_hits(self):
        long='A long context provides evidence. '*70+'A short apology follows. We apologize.'
        us=[unit(0),unit(1,long),unit(2)]
        sentences=list(split_sentences.split_units(us))
        target=[s for s in sentences if s['parent']==us[1]['id']][-2:]
        ss=[score(s,0.9 if s['id'] in {t['id'] for t in target} else 0.1) for s in sentences]
        rs=[score(u,0.9 if i==1 else 0.1) for i,u in enumerate(us)]
        packet=handoff.build_packet(us,rs,sample=0,sentence_rows=ss,sentence_units=sentences)
        item=packet['items'][0]
        self.assertEqual(item['unit']['text'],long)
        self.assertEqual(len(item['sentence_hits']),2)
        self.assertEqual([n['id'] for n in item['neighbors']],['draft_p0','draft_p2'])
        self.assertEqual(packet['context_only_count'],2)
        self.assertIn(long,handoff.render(packet))
        self.assertTrue(all(t['char_start']>1200 for t in target))
        for s in sentences:
            parent=next(u for u in us if u['id']==s['parent'])
            self.assertEqual(parent['text'][s['char_start']:s['char_end']],s['text'])
            self.assertIn('parent',s['context'])

    def test_failed_calls_select_for_inspection(self):
        us=[unit(0),unit(1)]
        rs=[score(us[0],None,False),score(us[1])]
        packet=handoff.build_packet(us,rs,sample=0)
        self.assertEqual(packet['failed_ids'],['draft_p0'])
        self.assertEqual(packet['items'][0]['reasons'],['untriaged_error'])
        sentences=list(split_sentences.split_units(us))
        ss=[score(s,None,False) for s in sentences]
        packet=handoff.build_packet(us,[score(u) for u in us],sample=0,sentence_rows=ss,sentence_units=sentences)
        self.assertEqual(packet['selected_count'],2)
        self.assertEqual(len(packet['sentence_failed_ids']),2)

    def test_stale_unknown_and_missing_sentence_evidence_rejected(self):
        u=unit(0); r=score(u)
        with self.assertRaises(ValueError):
            handoff.build_packet([u],[dict(r,text_sha256='wrong')])
        with self.assertRaises(ValueError):
            handoff.build_packet([u],[r],sentence_rows=[])
        with self.assertRaises(ValueError):
            handoff.build_packet([u],[r],marker_ids={'unknown'})
        with self.assertRaises(ValueError):
            handoff.build_packet([u,u],[r,r])
        s=list(split_sentences.split_units([u]))[0]
        with self.assertRaises(ValueError):
            handoff.build_packet([u],[r],sentence_rows=[score(s,0.9)],sentence_units=[dict(s,text='changed')])

    def test_cli_defaults_and_no_truncation(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp); us=[unit(i) for i in range(20)]
            (p/'units').write_text(''.join(json.dumps(u)+'\n' for u in us))
            (p/'scores').write_text(''.join(json.dumps(score(u))+'\n' for u in us))
            cmd=[sys.executable,str(SCRIPTS/'run_screen.py'),'summarize','--units',str(p/'units'),
                 '--screen',str(p/'scores'),'--out',str(p/'packet.md')]
            proc=subprocess.run(cmd,text=True,capture_output=True)
            self.assertEqual(proc.returncode,0,proc.stderr)
            packet=json.loads((p/'packet.json').read_text())
            self.assertEqual(len(packet['sample_ids']),12)
            self.assertEqual(packet['threshold'],0.65)
            proc=subprocess.run(cmd+['--chars','1200'],text=True,capture_output=True)
            self.assertNotEqual(proc.returncode,0)
            self.assertIn('truncation',proc.stderr)


class RecordTests(unittest.TestCase):
    def test_confirmed_and_no_live_source(self):
        u,f=fixture()
        self.assertEqual(verify_findings.verify(f,u,u['source_text'])['disposition'],'confirmed')
        self.assertEqual(verify_findings.verify(f,u)['disposition'],'unresolved')

    def test_fact_preservation_is_not_sufficient(self):
        u,f=fixture()
        f.update(issue_present=False,issue_removed=False)
        self.assertEqual(verify_findings.verify(f,u,u['source_text'])['disposition'],'optional')
        f['disposition']='confirmed'
        self.assertFalse(verify_findings.verify(f,u,u['source_text'])['record_valid'])

    def test_partial_if_repair_does_not_fix_or_changes_strength(self):
        u,f=fixture()
        for key in ['facts_preserved','strength_preserved','issue_removed']:
            for value in [False,None]:
                result=verify_findings.verify(dict(f,**{key:value}),u,u['source_text'])
                self.assertEqual(result['disposition'],'partial')

    def test_keep_not_false_positive(self):
        u,f=fixture()
        f.update(issue_present=False,action='keep',proposal='KEEP',issue_removed=None)
        self.assertEqual(verify_findings.verify(f,u,u['source_text'])['disposition'],'keep')

    def test_deletion_and_disguised_deletion_need_gate(self):
        u,f=fixture()
        for action, proposal in [('delete',''),('rewrite',f['proposal'])]:
            row=dict(f,action=action,proposal=proposal,deletes_sentence=True)
            self.assertEqual(verify_findings.verify(row,u,u['source_text'])['disposition'],'partial')
            row.update(removal_preserves=0.9,evidence_complete=True)
            self.assertEqual(verify_findings.verify(row,u,u['source_text'])['disposition'],'confirmed')
            row['evidence_complete']=False
            self.assertEqual(verify_findings.verify(row,u,u['source_text'])['disposition'],'partial')

    def test_missing_word_stale_source_and_malformed_fields(self):
        u,f=fixture()
        for row,src in [(dict(f,quote=f['quote'].replace('two ','')),u['source_text']),
                        (f,u['source_text']+' Changed.'),
                        (dict(f,quote=None),u['source_text']),
                        (dict(f,issue_reason=''),u['source_text']),
                        (dict(f,strength_preserved='true'),u['source_text'])]:
            result=verify_findings.verify(row,u,src)
            self.assertFalse(result['record_valid'])
            self.assertEqual(result['disposition'],'unresolved')

    def test_only_whitespace_reflow_is_allowed(self):
        u,f=fixture(); source=f['quote'].replace('present ','present\n')
        u.update(source_text=source,source_sha256=handoff.digest(source),end=2)
        self.assertEqual(verify_findings.verify(f,u,source)['disposition'],'confirmed')
        u['source_text']=source+' '+source
        self.assertFalse(verify_findings.verify(f,u)['record_valid'])


class RoutingAndCountingTests(unittest.TestCase):
    def test_bad_model_values_are_failed_not_zero(self):
        q=run_screen.load_controls()['questions']
        item={'id':'u','state':run_screen.state_for('A control.')}
        for bad in [None,{},dict.fromkeys(q,float('nan')),dict.fromkeys(q,True),dict.fromkeys(q,1.2)]:
            r=run_screen.build_row(item,bad,'model',1,None,q,'triage')
            self.assertFalse(r['ok'])
            self.assertIsNone(r['triage'])

    def test_gate_matches_ids_in_reverse_completion_order(self):
        specs=run_screen.load_controls()
        results=[]
        for c in specs['controls']:
            r=dict(id=c['id'],ok=True,resolved_model='mock',error=None)
            r.update({name:0.95 if name==c['designated_dimension'] else 0.01 for name in specs['questions']})
            results.append(r)
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(run_screen,'run',return_value=results[::-1]), contextlib.redirect_stderr(io.StringIO()):
            path=Path(tmp)/'gate.jsonl'
            self.assertEqual(run_screen.main(['gate','--out',str(path)]),0)
            ordered=[json.loads(l)['id'] for l in path.read_text().splitlines()]
            self.assertEqual(ordered,[c['id'] for c in specs['controls']])

    def test_separate_counts_unreviewed_and_null(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp); us=[unit(i) for i in range(4)]
            scores=[score(u,0.9) for u in us]
            scores[0].update(ok=False,screen_state='untriaged_control_failed')
            (p/'scores').write_text(''.join(json.dumps(s)+'\n' for s in scores))
            reviews=[dict(id='f1',unit=us[0]['id'],disposition='confirmed'),
                     dict(id='f2',unit=us[1]['id'],disposition='optional'),
                     dict(id='f3',unit=us[2]['id'],disposition='keep')]
            (p/'reviews').write_text(''.join(json.dumps(r)+'\n' for r in reviews))
            output=io.StringIO()
            with contextlib.redirect_stderr(output):
                self.assertEqual(merge_verdicts.main(['--screen',str(p/'scores'),'--verdicts',str(p/'reviews'),'--out',str(p/'table.tsv')]),0)
            self.assertIn('not_reviewed',(p/'table.tsv').read_text())
            self.assertIn('untriaged_control_failed',(p/'table.tsv').read_text())
            self.assertIn('null',(p/'table.tsv').read_text())
            self.assertIn('positive yield among scored routes 0/3',output.getvalue())
            self.assertNotIn('routing precision',output.getvalue())
            self.assertIn('"keep": 1',output.getvalue())
            self.assertIn('"optional": 1',output.getvalue())

    def test_independent_label_metrics_only_on_reviewed_units(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);us=[unit(i) for i in range(3)]
            (p/'s').write_text(''.join(json.dumps(score(u,0.9))+'\n' for u in us))
            (p/'v').write_text(json.dumps(dict(id='f1',unit=us[0]['id'],disposition='confirmed'))+'\n')
            (p/'r').write_text(json.dumps([us[1]['id']]))
            (p/'l').write_text(''.join(json.dumps(dict(id=u['id'],issue_present=True))+'\n' for u in us))
            output=io.StringIO()
            with contextlib.redirect_stderr(output):
                merge_verdicts.main(['--screen',str(p/'s'),'--verdicts',str(p/'v'),'--labels',str(p/'l'),
                                     '--reviewed-units',str(p/'r'),'--out',str(p/'o')])
            self.assertIn('TP 1 FP 0 FN 1 TN 0',output.getvalue())



class EndpointDiscoveryTests(unittest.TestCase):
    """The screen must resolve its endpoint without importing any Pi package."""

    def test_no_pi_import_in_scripts(self):
        import pathlib
        root = pathlib.Path(__file__).resolve().parent.parent
        for path in (root/'skills'/'defensive-writing-screen'/'scripts').glob('*.py'):
            body = path.read_text()
            for bad in ('import pi_jev', 'from pi_jev', 'pi-jev', 'jev_eval', 'jev-eval'):
                self.assertNotIn(bad, body, f'{path.name} references {bad}')

    def test_discovery_prefers_explicit_env(self):
        import importlib, os, sys
        sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent.parent
                              /'skills'/'defensive-writing-screen'/'scripts'))
        mod = importlib.import_module('run_screen')
        old = {k: os.environ.get(k) for k in ('JEV_ENDPOINT','PI_JEV_BASE_URL')}
        try:
            os.environ['PI_JEV_BASE_URL'] = 'http://a.test'
            os.environ.pop('JEV_ENDPOINT', None)
            self.assertTrue(mod.discover_endpoint()[0].startswith('http://a.test'))
            os.environ['JEV_ENDPOINT'] = 'http://b.test/v1/systemone'
            self.assertEqual(mod.discover_endpoint()[0], 'http://b.test/v1/systemone')
        finally:
            for k, v in old.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v
