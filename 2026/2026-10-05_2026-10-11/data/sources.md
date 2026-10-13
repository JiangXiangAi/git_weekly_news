# 数据来源与统计口径

报告周期：2026-10-05—2026-10-11。整理日期：2026-10-13。

## 本周事件与项目原始来源

1. [OpenAI/math 官方 README](https://github.com/openai/math/blob/main/README.md) — 发布时与修订后的目录规模、结果家族、模型生成流程和形式化覆盖说明。
2. [OpenAI/math 结果概览](https://github.com/openai/math/blob/main/overview.tex) — 代表性数学主张与结果家族索引。报告以“仓库列出/项目方声称”表述，不替代独立数学审查。
3. [OpenAI/math 修订历史](https://github.com/openai/math/blob/main/history.md) — 2026-10-07 的 3 篇撤回、14 篇修订和相关引用更新。
4. [llama.cpp 官方 Releases](https://github.com/ggml-org/llama.cpp/releases)、[vLLM 官方 Releases](https://github.com/vllm-project/vllm/releases)、[Ollama 官方 Releases](https://github.com/ollama/ollama/releases) — 本地推理和模型服务运行时的版本记录。
5. [Local Model Watch 运行时版本追踪](https://localmodelwatch.tsuchitsuchi.com/en/engines-en/) — 作为版本日期的辅助索引；版本事实仍链接到各项目官方 Releases。
6. [Week 41 开源 AI 追踪](https://olud.ai/reports/2026-w41.html) — 第三方聚合的周内增长和项目线索；其 Star 数据不是 GitHub 官方质量排名。
7. [GitHubTrending.today — AI Agents topic](https://githubtrending.today/topic/ai-agents/) — Agent 主题的日/周榜采样线索；不能等同于完整官方 Trending。
8. [REA 官方仓库](https://github.com/morluto/rea) — Agent 辅助软件行为探索和逆向理解的项目说明。
9. [claude-mem 官方仓库](https://github.com/thedotmack/claude-mem) 与 [text-to-cad 官方仓库](https://github.com/earthtojake/text-to-cad) — 跨会话记忆和可编辑工程产物相关入口。
10. [CARLA 官方提交记录](https://github.com/carla-simulator/carla/commits/ue58-dev)、[LiDAR 随机种子提交](https://github.com/carla-simulator/carla/commit/6549ebd)、[鱼眼镜头修复](https://github.com/carla-simulator/carla/commit/8d7635c)、[LiDAR 优化](https://github.com/carla-simulator/carla/commit/a7e2bf8) — 2026-10-08 至 10-09 的仿真传感器与渲染维护活动。
11. [LeRobot 官方 PR 列表](https://github.com/huggingface/lerobot/pulls)、[归一化统计 dtype/shape](https://github.com/huggingface/lerobot/pull/4846)、[时序值校验](https://github.com/huggingface/lerobot/pull/4847)、[数据集版本兼容](https://github.com/huggingface/lerobot/pull/4852) — 机器人数据管线维护活动；PR 存在不等于已经合并或证明策略性能提升。
12. [NVIDIA/OpenShell 官方仓库](https://github.com/NVIDIA/OpenShell) — Agent sandbox、声明式 YAML policy 与文件/网络/凭证访问控制的项目说明。
13. [DeepSeek DeepGEMM-Ascend](https://github.com/deepseek-ai/DeepGEMM-Ascend) — Ascend NPU 上 GEMM、MQA logits 与 MegaMoE 内核实现。官方 README 将 initial release 标为 2026-09-30，因此报告把它作为本周受关注的基础设施信号，而不是本周首次发布。
14. [TechRadar — DeepSeek and Huawei open-source AI tools（2026-10-07）](https://www.techradar.com/pro/huawei-and-deepseek-release-open-source-ai-tools-in-a-bid-to-lower-nvidia-exposure-but-will-programmers-make-the-switch) — 本周公开报道，只作事件背景，不能替代官方实现或基准。
15. [Nemati AI — GitHub Trending: Week of Oct 04–Oct 11, 2026](https://nemati.ai/en/blog/github-trending-week-of-oct-04-oct-11-2026)、[AI Beyond — GitHub AI Weekly Issue 09](https://00011000.com/en/news/github-ai-weekly-2026-w41)、[Tommy Zhang — GitHub Trending Weekly Digest](https://www.tommyz.blog/blog/github-trending-weekly-2026-10-05-to-2026-10-10)、[GitTrend Week 41](https://gittrend.io/weekly/2026-W41) — 第三方趋势摘要，统计窗口和采样方法可能不同，不合并其 Star 数。

## 统计与证据口径

- 第三方趋势页面只作为发现线索，不冒充 GitHub 官方完整周榜；项目事实优先回到官方仓库、release、PR、commit、论文或文档。
- Star 数据来自第三方时必须标明口径；不同来源时区、采样时间和周期不一致时，不把增量直接比较。
- 本仓库为首期归档，没有自有历史快照，不报告虚构的排名升降或周环比。
- 方向报告中的项目可以是长期技术入口，不代表每个项目都是本周新发布或上榜。
- Star、下载量和媒体关注度不等于质量。报告优先分析可复现性、维护状态、许可、失效边界及独立证据。
- 自动驾驶/机器人区分离线数据集、闭环仿真、封闭场地和真实世界验证；数学区分模型生成主张、同行审查、独立复现、形式化证明与内核检查。
- OpenAI/math 的目录规模、算力流程和结果摘要来自项目方公开说明；具体数学主张仍需领域专家独立审查。

## 下一期改进

1. 固定周初/周末采集时间和时区。
2. 保存 Trending 列表及采集时间，记录原始 JSON/CSV。
3. 对固定项目池记录同口径 Star 快照，只有同口径时才计算周期新增。
4. 为项目记录方向、仓库 URL、版本/commit、发布事件日期、证据等级和上榜状态。
5. 本周焦点优先依据有日期的 release、commit、PR、研究材料或基准；无强信号时坦诚说明证据稀疏。
6. 关键术语直接链接到 Google 技术解释并添加 Markdown title 中文提示；技术事实仍链接原始资料，避免只凭搜索摘要下结论。
