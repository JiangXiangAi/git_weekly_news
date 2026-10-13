# 数据来源与统计口径

报告周期：2026-10-05—2026-10-11。整理日期：2026-10-13。

## 本期查阅来源

1. [Nemati AI — GitHub Trending: Week of Oct 04–Oct 11, 2026](https://nemati.ai/en/blog/github-trending-week-of-oct-04-oct-11-2026) — 第三方趋势汇总，提供部分项目与 Star 线索。
2. [GitHubTrending.today — LLM topic](https://githubtrending.today/topic/llm/) — 主题分类和采样信息；页面说明周榜解析存在缺失，不视为完整周榜。
3. [GitHubTrending.today — AI Agents topic](https://githubtrending.today/topic/ai-agents/) — Agent 主题仓库与部分日/周增量。
4. [AI Beyond — GitHub AI Weekly Issue 09](https://00011000.com/en/news/github-ai-weekly-2026-w41) — ISO 第 41 周 AI 项目摘要。
5. [Tommy Zhang — GitHub Trending Weekly Digest, Oct 5–10, 2026](https://www.tommyz.blog/blog/github-trending-weekly-2026-10-05-to-2026-10-10) — 对 skills、软件逆向、记忆和上下文的分析。
6. [GitHub AI Trend Radar](https://radar.metabiz.ai/) — 可作为未来跨日快照辅助来源。
7. [OpenAI/math 官方仓库](https://github.com/openai/math) — 数学手稿、证明工件、结果目录和项目方对生成流程的说明。
8. [OpenAI/math 结果概览](https://github.com/openai/math/blob/main/overview.tex) — 结果家族与代表性数学主张的索引；本报告以“仓库声称/列出”表述，未替代独立数学审查。
9. [OpenAI/math 修订历史](https://github.com/openai/math/blob/main/history.md) — 手稿修订、撤回和更正记录。
10. [OpenAI/math README](https://github.com/openai/math/blob/main/README.md) — 目录规模、生成流程、形式化覆盖情况和项目方声明。

## 口径与限制

- 第三方趋势页面是发现线索，不能冒充 GitHub 官方完整周榜；项目事实应回到官方仓库核实。
- 各来源时区、采样时间和窗口不同；总 Star 与周增量只有在同口径时间点下才可比较。
- 本仓库为首期归档，没有自有历史快照，不报告虚构的排名升降或周环比。
- 自动驾驶、具身智能和 AI 数学报告中的部分项目是长期研究/工程入口，不代表它们本周上榜。
- Star 不等于质量。综合考察维护状态、许可、可复现性、实际使用证据与研究意义。
- 自动驾驶/机器人区分离线、仿真、封闭场地和真实世界验证；数学区分模型生成的主张、同行审查、独立复现与形式化证明。
- OpenAI/math 中的数量、算力流程和结果摘要来自项目方自己的公开说明；具体数学结论需由领域专家独立检查，不能只凭 README 认定为已确立定理。

## 下一期改进

1. 固定采集时间。
2. 保存 Trending 名单与采集时刻。
3. 对固定仓库池记录周期起止 Star；同口径才计算新增。
4. 为项目记录方向、仓库 URL、类型、总 Star、周期增量、来源时间、证据等级和上榜状态。
5. 保存原始 CSV/JSON，确保报告中的数字可追溯。
6. 将术语沉淀到仓库根目录的 glossary/，报告引用既有词条而不是每周复制定义。
