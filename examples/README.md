# 验收证据入口

本目录包含真实模型生成的输入、实际输出及原始Trace，按正常、资料不足、工具失败三组组织。无Mock替代。

模型：deepseek-flash；本轮耗时：135.594秒；状态：completed。

| 验收项 | 输入 | 实际输出 | 原始Trace | 可读步骤 | 检查结果 |
|---|---|---|---|---|---|
| 明确答案 | [输入](evidence-20261029T031505879381Z/normal/clear/input.json) | [输出](evidence-20261029T031505879381Z/normal/clear/output.json) | [Trace](evidence-20261029T031505879381Z/normal/clear/trace.jsonl) | [步骤](evidence-20261029T031505879381Z/normal/clear/path.md) | [检查](evidence-20261029T031505879381Z/normal/clear/checks.json) |
| 改写后的相似问题 | [输入](evidence-20261029T031505879381Z/normal/paraphrase/input.json) | [输出](evidence-20261029T031505879381Z/normal/paraphrase/output.json) | [Trace](evidence-20261029T031505879381Z/normal/paraphrase/trace.jsonl) | [步骤](evidence-20261029T031505879381Z/normal/paraphrase/path.md) | [检查](evidence-20261029T031505879381Z/normal/paraphrase/checks.json) |
| 文档冲突 | [输入](evidence-20261029T031505879381Z/insufficient/conflict/input.json) | [输出](evidence-20261029T031505879381Z/insufficient/conflict/output.json) | [Trace](evidence-20261029T031505879381Z/insufficient/conflict/trace.jsonl) | [步骤](evidence-20261029T031505879381Z/insufficient/conflict/path.md) | [检查](evidence-20261029T031505879381Z/insufficient/conflict/checks.json) |
| 资料外问题 | [输入](evidence-20261029T031505879381Z/insufficient/outside/input.json) | [输出](evidence-20261029T031505879381Z/insufficient/outside/output.json) | [Trace](evidence-20261029T031505879381Z/insufficient/outside/trace.jsonl) | [步骤](evidence-20261029T031505879381Z/insufficient/outside/path.md) | [检查](evidence-20261029T031505879381Z/insufficient/outside/checks.json) |
| 上下文追问 | [输入](evidence-20261029T031505879381Z/insufficient/context/input.json) | [输出](evidence-20261029T031505879381Z/insufficient/context/output.json) | [Trace](evidence-20261029T031505879381Z/insufficient/context/trace.jsonl) | [步骤](evidence-20261029T031505879381Z/insufficient/context/path.md) | [检查](evidence-20261029T031505879381Z/insufficient/context/checks.json) |
| 工具失败后恢复 | [输入](evidence-20261029T031505879381Z/failure/transient/input.json) | [输出](evidence-20261029T031505879381Z/failure/transient/output.json) | [Trace](evidence-20261029T031505879381Z/failure/transient/trace.jsonl) | [步骤](evidence-20261029T031505879381Z/failure/transient/path.md) | [检查](evidence-20261029T031505879381Z/failure/transient/checks.json) |
| 持续工具失败 | [输入](evidence-20261029T031505879381Z/failure/persistent/input.json) | [输出](evidence-20261029T031505879381Z/failure/persistent/output.json) | [Trace](evidence-20261029T031505879381Z/failure/persistent/trace.jsonl) | [步骤](evidence-20261029T031505879381Z/failure/persistent/path.md) | [检查](evidence-20261029T031505879381Z/failure/persistent/checks.json) |
| 文档30天改45天 | [输入](evidence-20261029T031505879381Z/normal/changed/input.json) | [输出](evidence-20261029T031505879381Z/normal/changed/output.json) | [Trace](evidence-20261029T031505879381Z/normal/changed/trace.jsonl) | [步骤](evidence-20261029T031505879381Z/normal/changed/path.md) | [检查](evidence-20261029T031505879381Z/normal/changed/checks.json) |
| 明确替代关系解决冲突 | [输入](evidence-20261029T031505879381Z/normal/resolved/input.json) | [输出](evidence-20261029T031505879381Z/normal/resolved/output.json) | [Trace](evidence-20261029T031505879381Z/normal/resolved/trace.jsonl) | [步骤](evidence-20261029T031505879381Z/normal/resolved/path.md) | [检查](evidence-20261029T031505879381Z/normal/resolved/checks.json) |
| 达到步数上限 | [输入](evidence-20261029T031505879381Z/failure/budget/input.json) | [输出](evidence-20261029T031505879381Z/failure/budget/output.json) | [Trace](evidence-20261029T031505879381Z/failure/budget/trace.jsonl) | [步骤](evidence-20261029T031505879381Z/failure/budget/path.md) | [检查](evidence-20261029T031505879381Z/failure/budget/checks.json) |

每例同时提供documents.json原始资料快照及history.json对话历史。path.md从Trace摘录，原始Trace为事实来源。

[本轮测试结果](evidence-20261029T031505879381Z/results.json) · [完整性检查](evidence-20261029T031505879381Z/integrity.json)

## 重新执行

在仓库根目录PowerShell运行：
```powershell
$env:QA_MODEL = "deepseek-flash"
python tests/run_evidence.py
python tests/verify_evidence.py examples/evidence-20261029T031505879381Z
```

第一条测试命令调用真实模型，创建新的时间戳目录，不覆盖本轮证据；接口错误会停止，结果不保证逐字一致。第二条只检查已保存证据，不模拟模型，也不产生新的模型决策。密钥、地址通过本地.env配置。

## 两条核心动态路径

- insufficient/conflict：检索 → 读取D01 → 读取D02 → 补查适用范围/替代依据 → 列出冲突并追问。
- failure/transient：检索 → 原文读取超时 → 模型再次选择读取 → 获得原文 → 回答。
- normal/resolved：明确替代关系下，引用D03及D02回答15天；没有按日期擅自选取。

## 复核边界

引用原文匹配、文档哈希、模式、步数和输出一致性由程序检查；语义复核说明见docs/03-evaluation.md。AI复核不冒充个人或独立人工审核。
