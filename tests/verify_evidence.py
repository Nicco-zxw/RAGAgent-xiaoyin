"""Check saved evidence integrity and render actual tool paths; no model simulation."""
import argparse
import hashlib
import json
from pathlib import Path

def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def main():
    p=argparse.ArgumentParser(); p.add_argument('root'); a=p.parse_args(); root=Path(a.root)
    summary=read(root/'results.json'); rows=[]
    for item in summary['cases']:
        d=root/item['path']; inp=read(d/'input.json'); out=read(d/'output.json')
        events=[json.loads(x) for x in (d/'trace.jsonl').read_text(encoding='utf-8').splitlines()]
        checks={}
        checks['documents_hash']=hashlib.sha256((d/'documents.json').read_bytes()).hexdigest()==inp['data_sha256']==events[0]['data_sha256']
        checks['real_trace']=events[0]['mode']==out['mode']==inp['mode']=='remote' and events[0]['model']==inp['model']
        checks['final_matches']=events[-1]['event']=='final' and events[-1]['result']==out
        actions=[e for e in events if 'action' in e]
        checks['within_budget']=len(actions)<=inp['max_steps'] and out['steps']==len(actions)
        seen=[]
        docs=read(d/'documents.json')
        corpus={(x['document_id'],p['passage_id'],x['version_date']):p['text'] for x in docs for p in x['passages']}
        for e in actions:
            if e['action']=='read_passage' and e['observation']['ok']:
                passage=e['observation']['data']; seen.append(passage)
        citations=list(out['citations'])
        for conflict in out['conflicts']: citations+=conflict.get('resolution_citations',[])
        checks['exact_read_citations']=all(isinstance(c.get('quote'),str) and bool(c['quote']) and c['quote'] in corpus.get((c['document_id'],c['passage_id'],c['version_date']),'') and any(all(c.get(k)==r.get(k) for k in ['document_id','passage_id','version_date']) and c['quote'] in r['quote'] for r in seen) for c in citations)
        text=['# 实际执行路径','',f"输入：{inp['question']}",f"对话历史：{json.dumps(inp['history'],ensure_ascii=False)}",f"模型：{inp['model']}；最终状态：{out['status']}",'','下列内容由原始Trace直接摘录，不是预设决策日志。','']
        for index,e in enumerate(actions):
            following=actions[index+1]['action'] if index+1<len(actions) else '结束：'+out['status']
            text += [f"## 步骤 {e['step']}：{e['action']}",'', '参数：'+json.dumps(e['arguments'],ensure_ascii=False),'', '返回：'+json.dumps(e['observation'],ensure_ascii=False),'','简要依据：'+str(e.get('reason_summary','')),'','后续动作：'+following,'']
        (d/'path.md').write_text('\n'.join(text),encoding='utf-8')
        rows.append({'case':item['case'],'integrity_checks':checks,'integrity_passed':all(checks.values()),'behavior_passed':item['passed']})
    result={'source_status':summary['status'],'cases':rows,'integrity_passed':bool(rows) and all(r['integrity_passed'] for r in rows),'boundary':'Checks saved real artifacts, not semantic correctness or new model decisions.'}
    (root/'integrity.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if result['integrity_passed'] else 1
if __name__=='__main__': raise SystemExit(main())
