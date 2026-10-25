#!/usr/bin/env python3
"""Offline package/specification checks plus regression tests. No live model calls."""
from __future__ import annotations
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'skills'/'defensive-writing-screen'
DEPENDENCY_MARKERS=['prefer its wording','remains the fallback','load it and prefer',
                    'if an `anti-defensive-writing` skill is also installed',
                    'requires the `anti-defensive-writing` skill']
GUIDE_SECTIONS=['Core rule','Main argument','Writing principles','Technical plans and SOPs',
                'Preferred patterns','Submission checks','What must survive','Classify before editing',
                'Rewrite procedure','Detection checklist','Discouraged patterns','Retreating tails',
                'Narrative placement','Protection before rewriting','Document structure',
                'Metrics, experiments, unfavorable results','Chinese-specific habits',
                'English-specific habits','Examples','Before returning a revision']


def main():
    failures=[]
    def check(ok,message):
        if not ok: failures.append(message)
    text=(SKILL/'SKILL.md').read_text()
    manifest=json.loads((ROOT/'package.json').read_text())
    check(text.startswith('---\n'),'missing skill frontmatter')
    check('name: defensive-writing-screen' in text,'skill name mismatch')
    check(f'version: "{manifest["version"]}"' in text,'manifest/skill version mismatch')
    check('requires no other skill' in text,'independence contract missing')
    check('Calibration records in this skill stay generic' in text,'project separation missing')
    check('Information preservation is necessary, not sufficient' in text,'two-stage boundary missing')
    check('keep the modal strength and degree' in text,'modal/degree protection missing')
    check('two independent passes' in text,'full-review pass separation missing')
    for name in ['SOP','Working without Jev','Reporting']:
        check(f'## {name}' in text,f'missing section {name}')
    for i in range(1,9):
        check(f'{i}. **' in text,f'missing SOP step {i}')
    for name in ['questions.md','controls.json','rewrite-guide.md','cases.md']:
        path=SKILL/'references'/name
        check(path.is_file() and path.stat().st_size>500,f'missing/empty {name}')
        check(name in text,f'undiscoverable reference {name}')
    for name in ['prepare_units.py','run_screen.py','handoff.py','split_sentences.py',
                 'verify_findings.py','verify_candidate_scan.py','merge_verdicts.py','check_structure.py']:
        check((SKILL/'scripts'/name).is_file(),f'missing script {name}')
    for path in SKILL.rglob('*'):
        if path.suffix not in {'.md','.json','.py'}: continue
        body=path.read_text()
        for bad in DEPENDENCY_MARKERS:
            check(bad not in body,f'{path.name}: external skill dependency {bad}')
        for bad in ['a concession whose facts all survive is therefore confirmed',
                    'A concession whose favorable and unfavorable facts both survive is `confirmed`']:
            check(bad not in body,f'{path.name}: withdrawn concession rule')
        check(not re.search(r'\bCoral\b|paper\.md|AGENTS\.md|/Users/',body,re.I),
              f'{path.name}: project-specific/runtime content in generic package')
    guide=(SKILL/'references'/'rewrite-guide.md').read_text()
    for name in GUIDE_SECTIONS:
        check(f'## {name}' in guide,f'guide lost capability {name}')
    check('complete on its own' in guide and 'Kiterlin' in guide and 'MIT' in guide,'standalone attribution missing')
    check('must not carry project content' in (SKILL/'references'/'cases.md').read_text(),'case separation missing')
    controls=json.loads((SKILL/'references'/'controls.json').read_text())
    check(controls['thresholds']=={'positive_min':0.65,'negative_max':0.2},'routing thresholds changed')
    check(set(controls['questions'])=={'claim_negation','negative_contrast','vague_hedge','concessive_hedge'},'routing dimensions changed')
    check(len(controls['controls'])==6,'gate control count changed')
    check(controls['revision']==manifest['version'],'review contract/package version mismatch')
    questions=(SKILL/'references'/'questions.md').read_text()
    check('candidate-discovery.jsonl' in questions and 'Pass B' in questions,
          'two-pass candidate workflow missing')
    cases={row['id'] for row in controls['semantic_challenges']}
    check({'direct_result_plus_nonclaim','intent_disclaimer_before_analysis',
           'unsupported_causal_explanation','auditable_method_rationale',
           'poor_result_causal_defense','effort_claim_with_details',
           'qa_omitted_work_dismissal','scope_label_as_answer',
           'omitted_work_design_reason','ai_disclosure_responsibility',
           'q_and_a_repeated_genre_rebuttal','q_and_a_distinct_design_reason',
           'all_we_need_burden_rebuttal','all_we_need_distinct_theorem_goal',
           'q_and_a_repeated_no_benefit_scope_gap','q_and_a_no_benefit_same_scope_rationale',
           'q_and_a_all_we_need_unjustified_burden',
           'nonclaim_same_result_after_evidence','nonclaim_distinct_subgroup_uncertainty'} <= cases,
          'missing review regression boundaries')
    hard={row['id'] for row in controls['hard_negatives']}
    check('causal_attribution_not_tone' in hard,'missing causal-modality protection')
    for entry in manifest['files']:
        check(bool(list(ROOT.glob(entry))),f'missing package entry {entry}')
    for entry in manifest.get('pi',{}).get('skills',[]):
        check((ROOT/entry).is_dir(),f'invalid resource path {entry}')
    notice=(ROOT/'NOTICE.md').read_text()
    check('f516147' in notice and 'MIT' in notice,'upstream attribution changed')
    check((ROOT/'LICENSE').is_file(),'LICENSE missing')
    if failures:
        print('\n'.join(['FAILED']+failures))
        return 1
    result=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(ROOT/'tests'),'-v'],cwd=ROOT)
    if result.returncode:
        return result.returncode
    print(f'OK: package {manifest["version"]}; layout, independence, contracts and offline tests')
    print('Live classifier calibration and manuscript detection quality are NOT verified by this command.')
    return 0


if __name__=='__main__':
    raise SystemExit(main())
