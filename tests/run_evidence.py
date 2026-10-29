"""Generate submission evidence with real models; never use Mock."""
import argparse
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from enterprise_qa.config import load_env
from enterprise_qa.core import Agent, RemoteModel, Tools

CASES=[
 ('normal','clear','data/clear.json','报销期限多久？',[],None,None,10,['answered'],'30'),
 ('normal','paraphrase','data/clear.json','报销的期限是多少天？',[],None,None,10,['answered'],'30'),
 ('insufficient','conflict','data/conflict.json','报销期限多久？',[],None,None,12,['needs_clarification'],None),
 ('insufficient','outside','data/clear.json','明天天气怎样？',[],None,None,10,['insufficient_evidence'],None),
 ('insufficient','context','data/clear.json','那试用期员工呢？',[{'role':'user','content':'报销期限多久？'}],None,None,10,['insufficient_evidence','needs_clarification'],None),
 ('failure','transient','data/clear.json','报销期限多久？',[],'read_passage',None,10,['answered'],'30'),
 ('failure','persistent','data/clear.json','报销期限多久？',[],None,'read_passage',10,['tool_error'],None),
 ('normal','changed','data/changed.json','报销期限多久？',[],None,None,10,['answered'],'45'),
 ('normal','resolved','data/resolved.json','现行报销期限多久？',[],None,None,14,['answered'],'15'),
 ('failure','budget','data/clear.json','报销期限多久？',[],None,None,1,['budget_exceeded'],None)]

def main():
    p=argparse.ArgumentParser(); p.add_argument('--output'); a=p.parse_args()
    load_env(); root=Path(a.output or 'examples/evidence-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
    root.mkdir(parents=True,exist_ok=False)
    report={'mode':'remote','model':None,'cases':[],'status':'running','not_run':[]}
    start=time.monotonic()
    def save():
        report['elapsed_seconds']=round(time.monotonic()-start,3)
        (root/'results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Evidence:',root,flush=True); save()
    for index,(group,name,data,q,history,first,always,budget,expected,text) in enumerate(CASES):
        folder=root/group/name; folder.mkdir(parents=True)
        model=RemoteModel(); report['model']=model.name
        raw=Path(data).read_bytes(); (folder/'documents.json').write_bytes(raw)
        inp={'question':q,'history':history,'data_source':data,'data_sha256':hashlib.sha256(raw).hexdigest(),'fail_first':first,'fail_always':always,'max_steps':budget,'audit_enabled':True,'mode':'remote','model':model.name,'expected_statuses':expected,'expected_text':text}
        (folder/'input.json').write_text(json.dumps(inp,ensure_ascii=False,indent=2),encoding='utf-8')
        r=Agent(model,Tools(str(folder/'documents.json'),first,always),budget,str(folder/'trace.jsonl'),'remote').run(q,history)
        (folder/'output.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
        events=[json.loads(x) for x in (folder/'trace.jsonl').read_text(encoding='utf-8').splitlines()]
        checks={'expected_status':r['status'] in expected,'expected_text':text is None or text in r['answer'],'real_model':r['mode']=='remote' and r['model_calls']>0}
        if r['status']=='answered': checks['has_citations']=bool(r['citations'])
        if name=='conflict':
            checks['two_sources']={'D01','D02'}<={c['document_id'] for c in r['citations']}
            checks['unresolved']=any(c.get('resolved') is False for c in r['conflicts'])
            checks['question']=bool(r['follow_up_question'])
        if name in ['transient','persistent']: checks['tool_failure_observed']=any(e.get('observation',{}).get('error')=='TIMEOUT' for e in events)
        if name=='resolved': checks['resolution_source']=any(c['document_id']=='D03' for c in r['citations'])
        row={'case':name,'group':group,'path':str(folder.relative_to(root)).replace('\\','/'),'checks':checks,'passed':all(checks.values())}
        (folder/'checks.json').write_text(json.dumps(row,ensure_ascii=False,indent=2),encoding='utf-8')
        report['cases'].append(row); print(name,r['status'],'PASS' if row['passed'] else 'REVIEW',flush=True)
        if r['status']=='model_error':
            report['status']='blocked'; report['not_run']=[c[1] for c in CASES[index+1:]]; save(); return 2
        save()
    report['status']='completed'; save()
    return 0 if all(c['passed'] for c in report['cases']) else 1
if __name__=='__main__': raise SystemExit(main())
