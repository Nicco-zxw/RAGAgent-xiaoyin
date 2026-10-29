# 实际用时与未完成项
本轮通过工具执行回执记录的命令运行耗时合计约6秒（不含模型生成、文件编辑准备及技能阅读时间）。
未在开始时设置完整墙钟计时，因此不能可靠给出端到端实际用时；不以预估冒充实测。

已完成：本地CLI、文档工具、远程模型适配器、Mock、执行预算、原文引用校验、9项测试、两条Mock运行日志及运行文档。
未完成：真实模型运行与动态决策效果验收（未配置/调用外部模型）；GitHub发布及最终提交SHA（用户当前要求本地搭建，且未提供目标远程仓库与题号）。
未纳入范围：界面、部署、多Agent、生产Runtime、企业权限与大规模检索。
实现取舍：使用标准库和unittest替代Pydantic/pytest，降低环境依赖；结构验证为手工校验，语义正确性依赖后续真实模型验收。

健壮性补验：新增5组回归测试，总计14项通过。修复模型输出及工具参数异常处理，补齐结构化冲突。实际完整墙钟未记录；不填写推测用时。真实模型和.env自动加载仍待后续处理。

Real-model acceptance suite measured runtime: 62.57 seconds (includes API waiting; excludes editing and interrupted run). 8/8 cases passed. Model: deepseek-flash. Real-model validation and .env loading are now implemented. GitHub publication remains pending.


## Core evidence enhancement: actual remote validation
Model: deepseek-flash. Result: 10/10. Suite wall time: 90.31 seconds (API waiting included; editing time excluded).
Added explicit supersession resolution, mandatory supplementary search for declared conflicts, resolution evidence checks, persistent tool failure, retained evidence on incomplete termination.
Observed resolved path: finish rejected at step 6; invalid JSON at step 7; model performed supplementary search at step 8 and ended with supported resolution at step 9. Unresolved conflict path: search, read D01, read D02, supplementary search, clarify. Persistent read failure: tool_error.
Remaining: model may omit conflict detection; semantic entailment is not guaranteed by exact-quote validation. GitHub publication pending.


Optimization results: 17/20 repeated acceptance expectations met; targeted audit 5/5, clear paraphrase 2/2. Suite runtime 297.46 seconds. See docs/optimization-report.md for failures and HTTP 402 blocking further calls. No mock fallback used.

本轮预算补验真实请求elapsed_seconds=0.454，HTTP 402，未完成业务验收；完整开发墙钟未计时。对照准备清单36项均未执行。见docs/comparison-progress.md。


## 接口恢复后的最终真实对照结果
固定规范未修改，运行状态completed，36项全部执行，无模型接口错误。
审查开启：18/18符合必要条件；关闭：16/18。差异均为材料提交起算依据不足时关闭审查返回answered。
完整实验墙钟348.078秒；开启平均任务耗时11.463秒，关闭7.841秒。
服务端报告Token：开启95758，关闭65224；请求数分别89与68。未推算金额。
预算单独补验通过；文档ID、部门范围、干扰文档、明确替代关系和材料明确/缺失均已真实验证。
结果：runs/comparison-20261028T154247157942Z/report.md；原始summary.json、36条trace和manual_review.csv保留。
结论仅限本批必要条件检查；人工语义审核清单未冒充已审核，小样本不足以推断生产准确率。正式CLI继续默认开启审查。

2026-10-29规范证据补验：当前实现真实模型10/10符合预期，完整性检查10/10通过；测试墙钟135.594秒，含API等待，不含文档整理。证据存于examples/evidence-20261029T031505879381Z，索引examples/README.md；复核边界见docs/03-evaluation.md。完整开发墙钟仍未可靠记录。
