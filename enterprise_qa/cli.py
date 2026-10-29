import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from .core import Agent, MockModel, RemoteModel, Tools
from .config import load_env

def main():
    p=argparse.ArgumentParser(description='企业知识问答 Agent')
    p.add_argument('--mode',choices=['mock','remote'],default='mock')
    p.add_argument('--data',default='data/clear.json')
    p.add_argument('--question',required=True)
    p.add_argument('--history')
    p.add_argument('--max-steps',type=int,default=8)
    p.add_argument('--trace')
    p.add_argument('--fail-first',choices=['search_documents','read_passage'])
    p.add_argument('--fail-always',choices=['search_documents','read_passage'])
    a=p.parse_args()
    if a.max_steps<1: p.error('--max-steps 必须大于0')
    try:
        load_env()
        if a.mode == 'remote' and not a.trace:
            a.trace = str(Path('runs') / ('cli-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')) / 'trace.jsonl')
        model=MockModel() if a.mode=='mock' else RemoteModel()
        history=json.loads(Path(a.history).read_text(encoding='utf-8-sig')) if a.history else []
        result=Agent(model,Tools(a.data,a.fail_first,a.fail_always),a.max_steps,a.trace,a.mode).run(a.question,history)
        if a.trace: result['trace_path'] = a.trace
    except (OSError,ValueError,KeyError) as e:
        result={'status':'configuration_error','error':type(e).__name__,'message':'请检查文件和 QA_MODEL、QA_API_KEY、QA_BASE_URL 配置。'}
    if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return {'answered':0,'needs_clarification':0,'insufficient_evidence':2,'budget_exceeded':3,'tool_error':4,'model_error':5,'configuration_error':6}.get(result['status'],1)

if __name__=='__main__': raise SystemExit(main())


