"""Render measured comparison and a manual evidence review checklist."""
import argparse
import csv
import json
from pathlib import Path

def main():
    p=argparse.ArgumentParser(); p.add_argument('run_dir'); a=p.parse_args()
    root=Path(a.run_dir); s=json.loads((root/'summary.json').read_text(encoding='utf-8'))
    lines=['# 真实模型审查开关对照报告','',f"运行状态：{s['status']}；模型：{s['model']}。",f"规范SHA256：{s['benchmark_sha256']}",'','自动检查仅验证预设必要条件，不等于人工语义审核。','', '| 审查 | 已执行 | 满足必要条件 | 模型错误 | 调用数 | 报告Token | 累计耗时(秒) |','|---|---:|---:|---:|---:|---:|---:|']
    for key,label in [('audit_on','开启'),('audit_off','关闭')]:
        m=s.get(key)
        if m: lines.append(f"| {label} | {m['runs']} | {m['passed']} | {m['model_errors']} | {m['model_calls']} | {m['reported_tokens']} | {m['total_seconds']} |")
    grouped={}
    for r in s['cases']: grouped.setdefault((r['repeat'],r['case']),{})[r['audit_enabled']]=r
    lines+=['','| 场景/轮次 | 开启审查 | 关闭审查 |','|---|---|---|']
    for (repeat,case),pair in grouped.items():
        def cell(v):
            if v is None: return '未执行'
            if v['result']['status']=='model_error': return '接口/模型失败'
            return ('通过' if v['passed'] else '需复核')+' / '+v['result']['status']
        lines.append(f'| {case}/{repeat+1} | {cell(pair.get(True))} | {cell(pair.get(False))} |')
    paired=[pair for pair in grouped.values() if True in pair and False in pair and all(row['result']['status']!='model_error' for row in pair.values())]
    improved=sum(pair[True]['passed'] and not pair[False]['passed'] for pair in paired)
    regressed=sum(pair[False]['passed'] and not pair[True]['passed'] for pair in paired)
    lines += ['',f'已完成且无模型错误的成对样本：{len(paired)}；仅开启审查符合必要条件：{improved}；仅关闭审查符合必要条件：{regressed}。']
    for audit,label in [(True,'开启'),(False,'关闭')]:
        rows=[row for row in s['cases'] if row['audit_enabled']==audit and row['result']['status']!='model_error']
        if rows:
            avg_seconds=sum(row['result']['elapsed_seconds'] for row in rows)/len(rows)
            avg_tokens=sum(row['result']['usage'].get('total_tokens',0) for row in rows)/len(rows)
            lines.append(f'{label}审查的平均每次任务耗时：{avg_seconds:.3f}秒；平均报告Token：{avg_tokens:.1f}。')
    lines+=['','## 未通过及未执行','']
    for r in s['cases']:
        if not r['passed']: lines.append(f"- {r['case']} 轮次{r['repeat']+1} 审查{r['audit_enabled']}：{'; '.join(r['issues'])}；状态{r['result']['status']}。")
    lines.append(f"未执行：{len(s['not_run'])}项。")
    lines+=['','## 解释边界','','同一服务模型的随机波动、请求顺序和缓存会影响结果。只有两轮，不能据此推断生产准确率或统计显著性。需人工检查答案支持、遗漏条件、冲突及过度拒答。审查开关对照只用于实验，正式CLI仍默认开启。']
    (root/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    with (root/'manual_review.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f); w.writerow(['case','repeat','audit_enabled','status','answer','citations','gaps','conflicts','claims_supported','conflicts_handled','over_refusal','reviewer_notes'])
        for r in s['cases']:
            q=r['result']; w.writerow([r['case'],r['repeat']+1,r['audit_enabled'],q['status'],q['answer'],json.dumps(q['citations'],ensure_ascii=False),json.dumps(q['gaps'],ensure_ascii=False),json.dumps(q['conflicts'],ensure_ascii=False),'','','',''])
    print(root/'report.md')

if __name__=='__main__': main()
