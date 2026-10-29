# 企业知识问答 Agent

帮助员工查询合成制度，使用真实模型动态检索、读取与查证；输出答案、原文引用、资料缺口和状态。原生Python CLI，无第三方框架依赖。

## 评审入口

1. [需求与成功标准](docs/01-requirements.md)
2. [流程、动态决策与技术取舍](docs/02-solution.md)
3. [预期、实际结果、失败与限制](docs/03-evaluation.md)
4. [AI辅助与个人贡献](docs/04-ai-usage.md)
5. [复盘与下一步](docs/05-retrospective.md)
6. [输入、实际输出、Trace及验收结果](examples/README.md)

本轮10例真实模型证据覆盖六类必验及文档替换、替代关系、预算上限；证据完整性校验通过。36项审查开关对照中开启18/18、关闭16/18符合必要条件。均不是独立人工签核或生产准确率保证。

## 环境与安装

Python 3.11+；实测3.12.10。仅标准库，requirements.txt声明无第三方依赖。仓库根目录PowerShell：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --no-index -r requirements.txt
Copy-Item .env.example .env
```

仅首次配置时复制.env.example，已有.env请保留。在.env中填写：

```text
QA_API_KEY=本地密钥
QA_BASE_URL=https://你的兼容服务地址/v1
QA_MODEL=服务实际支持的模型名
```

接口须兼容Chat Completions并支持JSON object输出；已实测deepseek-flash。密钥不提交，接口须由使用者信任；真实运行会发送问题、历史及相关合成资料。.env自动加载，进程环境变量优先，不展开变量。

## 运行

```powershell
.\.venv\Scripts\python.exe -m enterprise_qa.cli --mode remote --question "报销期限多久？"
.\.venv\Scripts\python.exe -m enterprise_qa.cli --mode remote --data data/conflict.json --question "报销期限多久？"
.\.venv\Scripts\python.exe -m enterprise_qa.cli --mode remote --data data/resolved.json --question "现行报销期限多久？" --max-steps 14
.\.venv\Scripts\python.exe -m enterprise_qa.cli --mode remote --history data/history.json --question "那试用期员工呢？"
.\.venv\Scripts\python.exe -m enterprise_qa.cli --mode remote --question "报销期限多久？" --fail-first read_passage
```

真实模式默认开启语义审查；未指定--trace时自动保存时间戳日志并返回trace_path。状态及退出码：0回答/需澄清，2资料不足，3预算耗尽，4工具失败，5模型失败，6配置错误。非零不一定代表程序崩溃，应查看status。默认8步，每步最多附加一次审查请求；复杂场景可显式提高上限。

## 可执行验收

```powershell
# 10例真实模型测试，写入新的examples时间戳目录；会产生服务调用费用
.\.venv\Scripts\python.exe tests/run_evidence.py
# 核对已提交证据的哈希、引用、输出一致性和步数；不调用模型
.\.venv\Scripts\python.exe tests/verify_evidence.py examples/evidence-20261029T031505879381Z
# 9场景审查开关各2轮，固定36项真实对照
.\.venv\Scripts\python.exe run_real_comparison.py --repeat 2
# 使用上条打印的目录生成对照报告与人工复核表
python report_comparison.py runs/comparison-20261028T154247157942Z
```

验收期望事先固定；实际输出与Trace保留，不伪造通过记录。真实接口异常不回退Mock。历史HTTP 402与歧义问法结果见评估和runs记录。

## 离线入口

```powershell
.\.venv\Scripts\python.exe -m enterprise_qa.cli --mode mock --question "报销期限多久？"
```

Mock是确定性规则模拟，仅验证流程，不证明真实模型决策效果。后续提交验收使用真实模型。tests/test_acceptance.py和test_robustness.py为早期离线回归，不能替代上述真实验收，后续功能变化未按当前约束重跑这些旧测试。

## 目录

- enterprise_qa/：模型、工具、循环、证据审查与CLI；保留原生包布局，不另造src副本。
- tests/：真实验收入口、证据一致性检查及历史回归。
- examples/：按正常、资料不足、工具失败三组组织的输入、实际输出、资料快照、Trace与测试结果。
- data/：合成资料、固定验收规则。
- docs/：五份交付文档及历史用时/限制记录。
- runs/：开发与改进实验记录；examples为规范评审入口。

## 已知限制与提交状态

语义审查与问答使用同一模型服务，可能共同漏检；未召回的证据无法充分审查。原文匹配不代表语义必然支持。仅为本地小规模合成库，无真实文档解析、权限、部署或生产Runtime，这些不是题目必需项。

完整开发墙钟未计时，不倒填；测试实测耗时见docs/time_log.md。个人修改、独立人工复核与投入需本人确认，AI不代签。题号3，目标仓库已确定；评审权限及远程提交仍待完成，当前不宣称已推送。

题号：**3**。目标GitHub仓库：[Nicco-zxw/RAGAgent-xiaoyin](https://github.com/Nicco-zxw/RAGAgent-xiaoyin)。主要由AI辅助实现；个人复核任务见[任务清单](docs/personal-review-tasks.md)，目前待本人完成。

