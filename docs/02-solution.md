# 02 实现方案与取舍

Python 3.11+标准库原生实现，无第三方Agent框架。选择原生实现便于直接审查模型选择动作和工具反馈，降低环境依赖；代价是自行维护格式校验、状态和日志。

## 调用流程

CLI加载本地.env（进程环境变量优先）→读取问题与可选历史→真实模型输出action/arguments/reason_summary→执行工具→将观察加入状态→模型调整动作或结束。

可选动作：search_documents、read_passage、finish。程序提供执行骨架，查询词、片段选择、补查、重试和结束由模型决定。工具失败原样作为观察交回模型，自动重试不充当ReAct证据。

检索采用字符二元组、制度术语和文档ID加权；命中摘要只定位资料，回答引用必须读取原文。小规模合成库无需向量数据库；缺点是长文与大规模召回能力有限。

结束前先校验字段、已读原文和声明冲突。声明冲突后必须补查；未解决冲突不得以answered结束；解决冲突需resolution_citations。随后用同一真实模型服务的一次独立请求审查语义支持和遗漏冲突，拒绝意见交回Agent。它不是独立人工审核，也不是多Agent系统。

默认8个决策步骤；每步最多一次额外审查，总请求上限2×max_steps。预算耗尽返回budget_exceeded并保留已读证据。网络异常返回model_error及安全的HTTP状态，不写密钥或响应正文。复杂替代关系场景显式配置更高预算。

## 模块

- enterprise_qa/core.py：工具、模型接入、循环及基础校验。
- enterprise_qa/evidence.py：声明冲突的证据约束。
- enterprise_qa/audit.py：语义审查规则与响应检查。
- enterprise_qa/config.py、cli.py：配置、输入和运行入口。
- tests/run_evidence.py：真实模型规范验收。
- tests/verify_evidence.py：保存证据的一致性检查，不模拟模型效果。

## 状态与日志

answered、needs_clarification、insufficient_evidence、tool_error、model_error、budget_exceeded；配置错误由CLI返回configuration_error。Trace记录步骤、参数、观察、简要依据和最终结果，不要求内部思维过程。CLI退出码与运行步骤见README。

## 实际改进

首次模型名无效及HTTP 402均如实保留。修复非法结构导致崩溃、冲突字段遗漏、补查约束、解决依据缺失；增加术语/编号匹配和结束前审查。36项开关对照中开启18/18、关闭16/18满足必要条件，同时审查增加延迟和用量。见[03-evaluation.md](03-evaluation.md)，不将小样本结果宣称为生产准确率。
