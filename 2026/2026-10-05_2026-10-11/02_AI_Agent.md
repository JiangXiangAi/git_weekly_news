# 子报告 02｜AI Agent

周期：2026-10-05—2026-10-11；整理日期：2026-10-13。

## 结论先行
本期公开趋势材料中，Agent 方向信号最强：skills、记忆、上下文管理、代码审查、自然语言 E2E 测试和软件逆向理解多次出现。共同趋势是把模型能力嵌入可恢复、可检查、可组合的工作流。

## 10 个重点项目

1. [morluto/rea](https://github.com/morluto/rea) — 用 Agent 理解软件行为，从 Web 应用到原生二进制。第三方周趋势摘要将其列为显著热门。入门：在自有测试样例上评估重建准确率和安全边界。
2. [mattpocock/skills](https://github.com/mattpocock/skills) — 可复用工程技能包。入门：追踪 skill 的输入、步骤、验收条件和失败处理。第三方周报有提及。
3. [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem) — 跨会话持久记忆。入门：检查记忆筛选、检索质量、隐私与删除机制。第三方趋势摘要有提及。
4. [michael-denyer/pstack-claude](https://github.com/michael-denyer/pstack-claude) — 多种编码 Agent 的结构化工作流适配。入门：比较宿主能力差异与可移植性。
5. [tester-army/e2e](https://github.com/tester-army/e2e) — 自然语言/Agent 驱动的端到端测试。入门：测量误报、漏报和 flaky rate。第三方周趋势摘要有提及。
6. [alibaba/open-code-review](https://github.com/alibaba/open-code-review) — 确定性规则结合 LLM 的代码审查。入门：比较规则检查与模型评论的可复现性。
7. [earthtojake/text-to-cad](https://github.com/earthtojake/text-to-cad) — 为 Agent 增加 CAD 能力。入门：检查几何约束、可制造性和输出文件校验。第三方 Agent 趋势页有提及。
8. [mvschwarz/openrig](https://github.com/mvschwarz/openrig) — 多 Agent 团队协作与共享上下文。入门：研究任务分配、冲突处理、成本和复核。第三方趋势页有提及。
9. [openai/openai-agents-python](https://github.com/openai/openai-agents-python) — Agent SDK，涵盖工具、handoff 和 tracing。入门：从单工具 Agent 开始，加入超时与恢复。
10. [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph) — 有状态的 Agent 工作流编排。入门：构建带 checkpoint、人类审批和重试的状态图。

## 核心观察
- 记忆不是简单追加历史：重点是何时保存、如何检索和如何纠正错误记忆。
- 测试与审查为任务提供了可检查的成功条件。
- 多 Agent 会增加通信、协调和 token 成本，必须以基准测试证明收益。
- 工具白名单、最小权限、沙箱、审批和审计日志应作为基础设计。

## 未来检验点
逐周观察 skills/memory/testing/review 类项目是否持续出现；用固定任务测量恢复率、工具调用成功率、人工介入、成本与完成时间。此处是趋势推断，不是对整个市场已完成转向的断言。