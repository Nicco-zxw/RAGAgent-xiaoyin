"""Frozen real-model audit on/off comparison. Never falls back to Mock."""
import argparse
import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from enterprise_qa.config import load_env
from enterprise_qa.core import Agent, RemoteModel, Tools

def check(case, result):
    issues=[]
    if result['status'] not in case['statuses']: issues.append('unexpected status')
    for text in case.get('required_text',[]):
        if text not in result['answer']: issues.append('missing expected answer text: '+text)
    sources={c['document_id'] for c in result['citations']}
    if not set(case.get('required_sources',[])).issubset(sources): issues.append('missing required sources')
    if case.get('require_gaps') and not result['gaps']: issues.append('missing gaps')
    if case.get('unresolved_conflict') and not any(c.get('resolved') is False for c in result['conflicts']): issues.append('missing unresolved conflict')
    if case.get('resolved_conflict') and not any(c.get('resolved') is True for c in result['conflicts']): issues.append('missing resolved conflict')
    return issues

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--repeat',type=int,default=2)
    parser.add_argument('--case',action='append',dest='selected')
    parser.add_argument('--audit',choices=['both','on','off'],default='both')
    parser.add_argument('--prepare-only',action='store_true',help='Save manifest without any model requests; not a test pass')
    args=parser.parse_args()
    if args.repeat<1: parser.error('repeat must be positive')
    load_env()
    raw=Path('data/benchmark_v1.json').read_bytes()
    spec=json.loads(raw.decode('utf-8'))
    known={c['id'] for c in spec['cases']}
    if args.selected and not set(args.selected)<=known: parser.error('unknown case')
    cases=[c for c in spec['cases'] if not args.selected or c['id'] in args.selected]
    out=Path('runs')/('comparison-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')); out.mkdir(parents=True)
    (out/'benchmark.json').write_bytes(raw)
    report={'status':'running','model':os.environ.get('QA_MODEL'),'benchmark_sha256':hashlib.sha256(raw).hexdigest(),'requested_repeat':args.repeat,'cases':[],'not_run':[]}
    started=time.monotonic()
    modes=[True,False] if args.audit=='both' else [args.audit=='on']
    jobs=[(repeat,c,audit) for repeat in range(args.repeat) for c in cases for audit in (modes if repeat%2==0 else modes[::-1])]
    def save():
        report['elapsed_seconds']=round(time.monotonic()-started,3)
        for audit in modes:
            rows=[r for r in report['cases'] if r['audit_enabled']==audit]
            report['audit_on' if audit else 'audit_off']={'runs':len(rows),'passed':sum(r['passed'] for r in rows),'model_errors':sum(r['result']['status']=='model_error' for r in rows),'model_calls':sum(r['result']['model_calls'] for r in rows),'reported_tokens':sum(r['result']['usage'].get('total_tokens',0) for r in rows),'total_seconds':round(sum(r['result']['elapsed_seconds'] for r in rows),3)}
        (out/'summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Output:',out,flush=True)
    if args.prepare_only:
        report['status']='prepared_not_executed'
        report['not_run']=[{'repeat':rep,'case':c['id'],'audit_enabled':a} for rep,c,a in jobs]
        save(); return 0
    save()
    for index,(repeat,case,audit) in enumerate(jobs):
        trace=out/f'{index:03d}-{case["id"]}-audit-{audit}.jsonl'
        r=Agent(RemoteModel(),Tools(case['data']),case['max_steps'],str(trace),'remote',audit_enabled=audit).run(case['question'])
        issues=check(case,r)
        events=[json.loads(line) for line in trace.read_text(encoding='utf-8').splitlines()]
        retrieved={hit['document_id'] for event in events if event.get('action')=='search_documents' and event['observation']['ok'] for hit in event['observation']['data']}
        relevant=set(case.get('required_sources',[]))
        recall=len(relevant & retrieved)/len(relevant) if relevant else None
        report['cases'].append({'case':case['id'],'repeat':repeat,'audit_enabled':audit,'passed':not issues,'issues':issues,'retrieval_recall':recall,'result':r})
        print(case['id'],'audit',audit,r['status'],'PASS' if not issues else 'REVIEW',flush=True)
        if r['status']=='model_error':
            report['status']='blocked'
            report['not_run']=[{'repeat':rep,'case':c['id'],'audit_enabled':a} for rep,c,a in jobs[index+1:]]
            save(); return 2
        save()
    report['status']='completed'; save()
    return 0 if all(r['passed'] for r in report['cases']) else 1

if __name__=='__main__': raise SystemExit(main())
