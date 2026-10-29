# 真实模型审查开关对照报告

运行状态：completed；模型：deepseek-flash。
规范SHA256：32ca0f5b81df9fbfb4d62ba6403576547cd58ec73657eb4e98fae2661b42d818

自动检查仅验证预设必要条件，不等于人工语义审核。

| 审查 | 已执行 | 满足必要条件 | 模型错误 | 调用数 | 报告Token | 累计耗时(秒) |
|---|---:|---:|---:|---:|---:|---:|
| 开启 | 18 | 18 | 0 | 89 | 95758 | 206.328 |
| 关闭 | 18 | 16 | 0 | 68 | 65224 | 141.137 |

| 场景/轮次 | 开启审查 | 关闭审查 |
|---|---|---|
| clear/1 | 通过 / answered | 通过 / answered |
| materials_missing/1 | 通过 / insufficient_evidence | 需复核 / answered |
| materials_explicit/1 | 通过 / answered | 通过 / answered |
| conflict/1 | 通过 / needs_clarification | 通过 / needs_clarification |
| resolved/1 | 通过 / answered | 通过 / answered |
| scoped/1 | 通过 / answered | 通过 / answered |
| noise/1 | 通过 / answered | 通过 / answered |
| document_id/1 | 通过 / answered | 通过 / answered |
| budget/1 | 通过 / budget_exceeded | 通过 / budget_exceeded |
| clear/2 | 通过 / answered | 通过 / answered |
| materials_missing/2 | 通过 / insufficient_evidence | 需复核 / answered |
| materials_explicit/2 | 通过 / answered | 通过 / answered |
| conflict/2 | 通过 / needs_clarification | 通过 / needs_clarification |
| resolved/2 | 通过 / answered | 通过 / answered |
| scoped/2 | 通过 / answered | 通过 / answered |
| noise/2 | 通过 / answered | 通过 / answered |
| document_id/2 | 通过 / answered | 通过 / answered |
| budget/2 | 通过 / budget_exceeded | 通过 / budget_exceeded |

已完成且无模型错误的成对样本：18；仅开启审查符合必要条件：2；仅关闭审查符合必要条件：0。
开启审查的平均每次任务耗时：11.463秒；平均报告Token：5319.9。
关闭审查的平均每次任务耗时：7.841秒；平均报告Token：3623.6。

## 未通过及未执行

- materials_missing 轮次1 审查False：unexpected status；状态answered。
- materials_missing 轮次2 审查False：unexpected status；状态answered。
未执行：0项。

## 解释边界

同一服务模型的随机波动、请求顺序和缓存会影响结果。只有两轮，不能据此推断生产准确率或统计显著性。需人工检查答案支持、遗漏条件、冲突及过度拒答。审查开关对照只用于实验，正式CLI仍默认开启。
