"""Summarize saved real-model runs without additional model calls."""
import json
from pathlib import Path

def summarize(root):
    paths=list(Path(root).glob('*.jsonl')); audits=[]; final=[]
    for path in paths:
        rows=[json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()]
        audits += [r for r in rows if r.get('event')=='audit']
        final += [r['result'] for r in rows if r.get('event')=='final']
    return {'traces':len(paths),'audit_calls_with_valid_response':len(audits),'audit_rejections':sum(not a['review']['approved'] for a in audits),'model_calls':sum(r.get('model_calls',0) for r in final),'reported_tokens':sum(r.get('usage',{}).get('total_tokens',0) for r in final),'completed_results':len(final)}

if __name__=='__main__':
    import sys
    print(json.dumps(summarize(sys.argv[1]),ensure_ascii=False,indent=2))
