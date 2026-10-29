# 验收记录
实际执行 python -m unittest discover -s tests：9项通过。
覆盖明确答案、冲突、资料外问题、相似改写、上下文追问、一次读取失败恢复、预算耗尽、30改45、伪造引用拒绝。
记录 runs/mock-clear.jsonl：检索→读取→结束（3步）。
记录 runs/mock-conflict.jsonl：检索→读取D01→读取D02→补查范围/优先级→追问（5步）。
两条均为离线模拟器运行，不证明真实模型决策有效。
未进行真实模型验收；真实模型行为仍需按 README 命令执行并人工检查引用支持、冲突查证与动作调整。

## 健壮性补验
新增5组测试，总计14项通过（python -m unittest discover -s tests -v）。
修复：非对象模型输出导致崩溃、非法JSON直接终止、空引用集合类型错误、工具参数缺少类型约束、Mock冲突字段为空。
非法JSON和结构错误会作为失败观察反馈下一轮，计入执行上限；网络/模型调用异常仍明确返回model_error。
持续工具失败测试返回tool_error；冲突日志已重新生成，含sources与resolved=false。
本次未读取.env或调用真实模型。当前CLI尚未自动加载.env，真实模型验证前需补充该入口或显式设置环境变量。


## Real model acceptance
Model: deepseek-flash; 8/8 passed. Measured runtime: 62.57 seconds.
Cases: clear, conflict, outside, paraphrase, context, transient tool failure, changed document, execution budget.
Evidence: runs/real-summary.json and runs/remote-*.jsonl. Original failed run retained in runs/real-summary-first.json.


## Core evidence enhancement: actual remote validation
Model: deepseek-flash. Result: 10/10. Suite wall time: 90.31 seconds (API waiting included; editing time excluded).
Added explicit supersession resolution, mandatory supplementary search for declared conflicts, resolution evidence checks, persistent tool failure, retained evidence on incomplete termination.
Observed resolved path: finish rejected at step 6; invalid JSON at step 7; model performed supplementary search at step 8 and ended with supported resolution at step 9. Unresolved conflict path: search, read D01, read D02, supplementary search, clarify. Persistent read failure: tool_error.
Remaining: model may omit conflict detection; semantic entailment is not guaranteed by exact-quote validation. GitHub publication pending.


Optimization results: 17/20 repeated acceptance expectations met; targeted audit 5/5, clear paraphrase 2/2. Suite runtime 297.46 seconds. See docs/optimization-report.md for failures and HTTP 402 blocking further calls. No mock fallback used.

固定验收与对照准备：详情见docs/comparison-progress.md。本轮真实模型HTTP 402；预算终止未完成验收。36项审查开关对照已准备、未执行。明确材料提交与缺失材料条件分开验收，资料均为合成测试，不代表真实企业政策。


## 接口恢复后的最终真实对照结果
固定规范未修改，运行状态completed，36项全部执行，无模型接口错误。
审查开启：18/18符合必要条件；关闭：16/18。差异均为材料提交起算依据不足时关闭审查返回answered。
完整实验墙钟348.078秒；开启平均任务耗时11.463秒，关闭7.841秒。
服务端报告Token：开启95758，关闭65224；请求数分别89与68。未推算金额。
预算单独补验通过；文档ID、部门范围、干扰文档、明确替代关系和材料明确/缺失均已真实验证。
结果：runs/comparison-20261028T154247157942Z/report.md；原始summary.json、36条trace和manual_review.csv保留。
结论仅限本批必要条件检查；人工语义审核清单未冒充已审核，小样本不足以推断生产准确率。正式CLI继续默认开启审查。
