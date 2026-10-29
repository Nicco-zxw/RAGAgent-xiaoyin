# 03 测试、实际结果与限制

## 本轮真实验收

评审入口：[examples/README.md](../examples/README.md)。2026-10-29重新调用deepseek-flash，使用当前实现生成10例实际证据，10/10符合预设必要条件，总墙钟135.594秒（包括API等待，不包括整理文档）。

[测试汇总](../examples/evidence-20261029T031505879381Z/results.json)；[完整性校验](../examples/evidence-20261029T031505879381Z/integrity.json)；[运行环境与代码哈希](../examples/evidence-20261029T031505879381Z/environment.json)。每例提供input.json、documents.json、output.json、trace.jsonl、path.md、checks.json。三个资料组均包含真实输入、输出与工具记录。

| 验收项 | 预期 | 实际结果及证据 |
|---|---|---|
| 明确答案 | 依据D01回答30天 | answered，引用D01/P01，[记录](../examples/evidence-20261029T031505879381Z/normal/clear/path.md) |
| 相似改写 | 同义问题仍回答30天 | answered，引用同一原文，[记录](../examples/evidence-20261029T031505879381Z/normal/paraphrase/path.md) |
| 文档冲突 | 30/15不擅自择一，补查并追问 | needs_clarification，引用双方，补查后仍缺适用依据，[记录](../examples/evidence-20261029T031505879381Z/insufficient/conflict/path.md) |
| 资料外问题 | 不用常识回答天气 | insufficient_evidence，无制度结论，[记录](../examples/evidence-20261029T031505879381Z/insufficient/outside/path.md) |
| 上下文追问 | 根据历史理解试用期报销，但不假定适用 | insufficient_evidence，缺试用期适用范围，[输入与历史](../examples/evidence-20261029T031505879381Z/insufficient/context/input.json)、[记录](../examples/evidence-20261029T031505879381Z/insufficient/context/path.md) |
| 工具一次失败 | 将超时观察交给模型，由模型选择恢复 | 首次读取超时，再次读取成功，answered，[记录](../examples/evidence-20261029T031505879381Z/failure/transient/path.md) |
| 工具持续失败 | 无原文时明确失败、不伪造引用 | tool_error，[记录](../examples/evidence-20261029T031505879381Z/failure/persistent/path.md) |
| 文档内容替换 | 30改45应改变答案 | answered 45天，引用更新原文，[记录](../examples/evidence-20261029T031505879381Z/normal/changed/path.md) |
| 明确替代关系 | 读取依据后才解决冲突 | 引用D03及D02回答15天，resolved=true，[记录](../examples/evidence-20261029T031505879381Z/normal/resolved/path.md) |
| 执行上限 | 不能将预算耗尽当成功 | max_steps=1，budget_exceeded，[记录](../examples/evidence-20261029T031505879381Z/failure/budget/path.md) |

## 动态决策及修改结果

至少两条实际路径：冲突用例中模型选择补充检索；读取超时用例中模型观察失败后选择再次读取。path.md逐步包含参数、返回、简要依据和后续动作，均从原始Trace摘录，不是预先写好的路径。

文档干预形成三个对照：clear→changed，期限30变45且答案随之变化；clear→conflict，新增15天规则后动作变为查证与追问；conflict→resolved，新增明确替代条款后读取并引用D03，才回答15天。这些是合成制度，不能用于推断真实企业政策。

## 引用与语义复核

程序核对全部10例：资料快照哈希与Trace一致；均为remote模式；output与Trace最终结果一致；未超执行步数；所有最终引用及解决冲突引用都来自本次实际读取且与资料原文匹配。检查结果全部通过。空引用的资料外/失败场景不据此证明语义正确。

本轮由AI辅助逐条查看输出、原文快照和关键路径：30/45/15天结论有对应条款；冲突列出双方且未擅自选择；试用期没有凭常识认定适用；超时结果没有伪造原文。资料外回答中的“知识库没有天气资料”仅在本合成快照范围内成立，不能扩大到任意企业完整知识库。

上述AI复核不是个人签核。提交者后续确认已完成答案引用、冲突处理与执行记录的个人复核，见04-ai-usage.md；未另附逐例人工批注，不把AI审查改记为个人操作。

## 改进实验与失败保留

历史真实审查开关对照：[报告](../runs/comparison-20261028T154247157942Z/report.md)。固定36项全部执行；开启18/18、关闭16/18符合必要条件；两次差异为缺起算依据时关闭审查返回answered。平均耗时11.463秒/7.841秒，服务端报告Token总计95758/65224。两轮小样本，不能声称生产准确率或统计显著提升。

历史HTTP 402、旧有歧义问法失败记录仍在runs/及旧评估文档，不删除或改成通过。本轮无接口错误、无Mock回退。高分改进证据为同义/编号检索、冲突补查、明确替代依据及真实审查反馈，而非框架名称。

## 执行步骤

仓库根目录PowerShell：

```powershell
$env:QA_MODEL = "deepseek-flash"
python tests/run_evidence.py
python tests/verify_evidence.py examples/evidence-20261029T031505879381Z
```

环境Python 3.11+，仅标准库；QA_API_KEY、QA_BASE_URL、QA_MODEL读取本地.env。第一条会产生新的真实调用及独立目录，结果可能波动。第二条是保存证据的完整性检查，不是Mock、也不是新的模型效果测试。

## 已知限制与未完成

模型与同模型审查均可能漏检；未召回的矛盾不一定被发现；程序引用匹配不能保证语义充分。提交者已自述完成最终结果复核，具体范围见04-ai-usage.md。完整开发墙钟未记录，不倒填；本轮测试时间有实测。题号已确认为3，目标仓库为Nicco-zxw/RAGAgent-xiaoyin；已推送codex/submission分支，个人复核范围已确认；评审访问权限仍待确认。


