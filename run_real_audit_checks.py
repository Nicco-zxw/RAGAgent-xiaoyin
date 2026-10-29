"""Targeted live reviewer checks, including deliberately incorrect candidates."""
import json
import time
from pathlib import Path
from datetime import datetime, timezone
from enterprise_qa.core import RemoteModel, Tools, Agent
from enterprise_qa.config import load_env
from enterprise_qa.audit import review

def main():
    load_env(); started=time.monotonic()
    out=Path('runs')/('audit-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')); out.mkdir(parents=True)
    model=RemoteModel(); tools=Tools('data/scoped.json')
    evidence=[tools.execute('read_passage',{'document_id':d,'passage_id':'P01'})['data'] for d in ['S01','S02']]
    cases=[('overgeneralization','所有员工报销期限为30天。',False),('scoped','销售部员工报销期限为30天，研发部员工为15天。',True),('wrong_number','销售部员工报销期限为15天。',False)]
    records=[]
    for name,answer,expected in cases:
        candidate={'status':'answered','answer':answer,'citations':evidence,'conflicts':[]}
        result=review(model,'销售部和研发部员工报销期限分别多久？',[],candidate,evidence,[])
        records.append({'case':name,'expected':expected,'review':result,'passed':result['approved']==expected})
        print(name,records[-1]['passed'],flush=True)
    ct=Tools('data/conflict.json'); ev=[ct.execute('read_passage',{'document_id':d,'passage_id':'P01'})['data'] for d in ['D01','D02']]
    r=review(model,'报销期限多久？',[],{'status':'answered','answer':'报销期限为15天。','citations':[ev[1]],'conflicts':[]},ev,[])
    records.append({'case':'omitted_conflict','review':r,'passed':not r['approved']}); print('omitted_conflict',not r['approved'],flush=True)
    r=Agent(model,tools,12,str(out/'scoped.jsonl'),'remote').run('销售部员工报销期限多久？')
    records.append({'case':'scoped_agent','result':r,'passed':r['status']=='answered' and '30' in r['answer'] and not any(c.get('resolved') is False for c in r['conflicts'])})
    (out/'summary.json').write_text(json.dumps({'cases':records,'elapsed_seconds':round(time.monotonic()-started,2),'calls':model.calls,'usage':model.usage},ensure_ascii=False,indent=2),encoding='utf-8')
    print('Output',out,flush=True)
    raise SystemExit(0 if all(c['passed'] for c in records) else 1)
if __name__=='__main__': main()
