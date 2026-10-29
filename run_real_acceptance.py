"""Real-model acceptance runner. No offline fallback."""
import json
import os
import time
import argparse
from datetime import datetime, timezone
from pathlib import Path
from enterprise_qa.config import load_env
from enterprise_qa.core import Agent, RemoteModel, Tools

def main():
    load_env()
    parser=argparse.ArgumentParser()
    parser.add_argument('--repeat',type=int,default=1)
    options=parser.parse_args()
    if options.repeat<1: parser.error('repeat must be positive')
    output=Path('runs') / ('real-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
    output.mkdir(parents=True)
    print('Run directory:',output,flush=True)
    cases=[
        ('resolved','data/resolved.json','现行报销期限多久？',None,None,12,'answered'),
        ('persistent_failure','data/clear.json','报销期限多久？',None,None,8,'tool_error'),
        ('clear','data/clear.json','报销期限多久？',None,None,8,'answered'),
        ('conflict','data/conflict.json','报销期限多久？',None,None,8,'needs_clarification'),
        ('outside','data/clear.json','明天天气怎样？',None,None,8,'insufficient_evidence'),
        ('paraphrase','data/clear.json','报销材料最迟多少天内提交？',None,None,8,'answered'),
        ('context','data/clear.json','那试用期员工呢？',[{'role':'user','content':'报销期限多久？'}],None,8,'insufficient_evidence'),
        ('failure','data/clear.json','报销期限多久？',None,'read_passage',8,'answered'),
        ('changed','data/changed.json','报销期限多久？',None,None,8,'answered'),
        ('budget','data/clear.json','报销期限多久？',None,None,1,'budget_exceeded')]
    cases=cases*options.repeat
    summary=[]
    started=time.time()
    for index,(name,data,q,h,f,b,expected) in enumerate(cases):
        r=Agent(RemoteModel(),Tools(data,f, 'read_passage' if name=='persistent_failure' else None),b,str(output / f'{index:02d}-{name}.jsonl'),'remote').run(q,h)
        passed=r['status']==expected
        if name in ('clear','changed','paraphrase'): passed=passed and ('45' if name=='changed' else '30') in r['answer'] and bool(r['citations'])
        if name=='conflict': passed=passed and len(r['citations'])>=2 and bool(r['conflicts'])
        if name=='resolved':
            passed=passed and '15' in r['answer'] and any(c.get('document_id')=='D03' for c in r['citations']) and any(c.get('resolved') is True for c in r['conflicts'])
        summary.append({'case':name,'passed':passed,'expected':expected,'result':r})
        print(name,r['status'],'PASS' if passed else 'REVIEW',flush=True)
    (output / 'summary.json').write_text(json.dumps({'model':os.environ['QA_MODEL'],'elapsed_seconds':round(time.time()-started,2),'cases':summary},ensure_ascii=False,indent=2),encoding='utf-8')
    raise SystemExit(0 if all(c['passed'] for c in summary) else 1)

if __name__=='__main__': main()
