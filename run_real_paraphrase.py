from pathlib import Path
import json,time
from datetime import datetime, timezone
from enterprise_qa.config import load_env
from enterprise_qa.core import RemoteModel,Agent,Tools
load_env()
out=Path('runs')/('paraphrase-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')); out.mkdir(parents=True)
start=time.monotonic(); results=[]
for i in range(2):
    r=Agent(RemoteModel(),Tools('data/clear.json'),8,str(out/f'{i}.jsonl'),'remote').run('报销的期限是多少天？')
    results.append({'passed':r['status']=='answered' and '30' in r['answer'],'result':r})
    print(i,results[-1]['passed'],flush=True)
(out/'summary.json').write_text(json.dumps({'cases':results,'elapsed_seconds':round(time.monotonic()-start,2)},ensure_ascii=False,indent=2),encoding='utf-8')
print(out)
