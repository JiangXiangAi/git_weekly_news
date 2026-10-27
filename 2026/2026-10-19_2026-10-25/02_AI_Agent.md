# 方向报告 02｜AI Agent：配置优先级、状态隔离与恢复正确性

**统计周期：** 2026-10-19—2026-10-25（自然周，周一至周日）　**整理日期：** 2026-10-27  
**选题口径：** 本周原创事件 + 代表项目技术精读。Top 10 为技术关注清单，不是未经快照校验的 GitHub Trending 名次；没有同口径周初周末 Star 数据，不给虚构增量。

## 一、整体结论

本周 Agent 系统有一项比增加工具更值得警惕的正确性修复：LangGraph 发现显式指定的递归上限，若数值恰好等于默认值，可能被配置合并逻辑错误丢弃。2026 年 10 月 24 日修复后的 1.2.17 通过带类型的默认值标记区分「没有显式配置」与「显式要求该值」。这直接关系到长任务停止条件和无意的循环执行。

跨项目判断是运行时治理正在从「允许什么工具」延伸到「谁的配置优先、状态如何传递、何时必须停机」。LangGraph 的主张可由 PR 和 release 验证，但没有本周跨 Agent 框架的统一成功率基准；记忆、编排、检查和工程产物依然按各自证据评估。

## 二、本周焦点

**事件一｜2026-10-23 至 24，LangGraph PR #9417 与 1.2.17。** [原始修复 PR](https://github.com/langchain-ai/langgraph/pull/9417) 记录 `merge_configs` 将与默认值相等的显式 `recursion_limit` 当作未设置，从而留下更高的已绑定限制；提交把隐式默认值改为私有 `int` 子类标记，保证经过 copy、deepcopy、pickle 后仍能正确区分显式值。官方 [1.2.17 release](https://github.com/langchain-ai/langgraph/releases/tag/1.2.17) 于 10 月 24 日包含该修复。机制影响是降低 Agent 意外超限执行的风险。**边界：** 这是配置合并语义修复，不等于全链路费用上限或外部工具副作用已受控。

**事件二｜2026-10-23 至 24，LangGraph SDK / RemoteGraph 参数语义维护。** 官方 [SDK 0.4.9](https://github.com/langchain-ai/langgraph/releases) 在 10 月 23 日引入线程 priority 配置；同一 1.2.17 release 修复 `RemoteGraph.stream(subgraphs=True)` 的调用方 namespace 保留问题，见 [PR #9401](https://github.com/langchain-ai/langgraph/pull/9401)。这些都是运行时状态与优先级可预期性的维护，不是模型推理算法突破。

## 三、Top 10 项目技术分析

每项结构图描述所列项目自身模块/工件/数据或控制流，统一为纵向 Mermaid。项目持续跟踪不等于每个项目均在本周发生重大版本更新；如无周内原始事件，技术分析以官方公开实现与可验证的架构判断为主。

### 1. [OpenAI Agents SDK](https://github.com/openai/openai-agents-python) — 工具调用、交接与追踪

**技术分析**

**OpenAI Agents SDK 的运行循环把模型输出、工具调用、角色交接和追踪拆为可观察的阶段，但不代替权限判断。**

当 Agent 需要调用多个工具或将任务交给专门角色时，业务代码容易演变成难以调试的 prompt 分支。Agents SDK 将 Agent、Runner、工具 schema、handoff、guardrail 和 tracing 组织成相对统一的执行抽象。典型运行过程不是一次模型调用，而是模型生成动作、执行器验证并调用工具、工具结果回到上下文，再决定继续、交接或结束。这个循环让调用路径可观测，但并不意味着模型输出天然可信：参数仍需验证，工具权限需要最小化，循环也必须有预算与终止条件。 [Tracing](https://www.google.com/search?q=Tracing%20%E6%8A%80%E6%9C%AF%E5%8E%9F%E7%90%86%20%E8%A7%A3%E9%87%8A "Tracing：将模型调用、工具执行、延迟和异常串成调用链") 的价值在于把模型调用、工具执行和交接连接起来，帮助定位失败发生在哪一阶段；它不能代替业务级正确性测试。关键判断在于特别区分模型“建议调用工具”与宿主代码“实际执行工具”的边界，并检查异常和 guardrail 是否在每条路径都生效。评估应同时看任务成功率、工具参数正确率、无效循环、人工介入和总成本。

机制依据见 [OpenAI Agents SDK 官方仓库及项目文档](https://github.com/openai/openai-agents-python)；其中关于性能、安全或泛化的评价，除非另附独立实验，否则仅属于系统分析推断。

**项目结构图**

```mermaid
%%{init: {"flowchart": {"useMaxWidth": true, "nodeSpacing": 20, "rankSpacing": 24, "curve": "linear"}, "themeVariables": {"fontSize": "12px"}}}%%
flowchart TD
  A[用户任务 / Context] --> B[Runner]
  B --> C[Agent Model Call]
  C --> D{最终答复 / Tool Call / Handoff}
  D -->|Tool Call| E[Schema 与权限校验]
  E --> F[Tool Executor]
  F --> G[Tool Result]
  G --> B
  D -->|Handoff| H[目标 Agent]
  H --> B
  D -->|Final| I[输出]
  J[Guardrails / Tracing] --- B
```

*图注：依据 [OpenAI Agents SDK 官方仓库](https://github.com/openai/openai-agents-python) 的公开接口与实现整理；此图是项目机制示意而非逐文件证明，未公开的实现细节待源码核验。*

**技术判断与边界：** 该 SDK 的关键价值是把模型循环、工具执行、交接和追踪放在可观测的执行框架中；但实际正确性仍依赖宿主程序的 schema、权限、终止条件和业务验证，不应把 tracing 当作结果正确的证明。

### 2. [LangGraph](https://github.com/langchain-ai/langgraph) — 显式状态图与可恢复执行

**技术分析**

**LangGraph 采用显式状态图、checkpoint 与恢复边界，使长期 Agent 执行能够区分完成节点和待运行节点。**

长任务会出现分支、循环、暂停等待用户、人工审批和进程崩溃恢复等需求。把这些状态隐含在长 prompt 或普通函数调用中，往往难以重放和审计。LangGraph 用状态、节点和条件边表达执行图，并通过 checkpoint/interrupt 等机制保存状态和建立暂停点。其工程价值是让工作流结构显式化：可以观察当前节点、状态如何变化、在哪个条件下进入下一步。持久化并不自动保证“恰好执行一次”；恢复后若某个节点已调用外部 API、但结果未写入 checkpoint，重放可能再次执行副作用。因此幂等键、事务边界、状态版本和外部操作记录仍需应用设计。图也可能因状态不断增长或分支组合而变复杂。结果比较必须测试中断后恢复、重复提交、节点失败和状态 schema 变更，而不只是演示一次成功路径。关键证据是工作流能否在失败点重建一致状态。

与本周 [LangGraph PR #9417](https://github.com/langchain-ai/langgraph/pull/9417) 相连，默认值和显式配置的区别属于控制平面安全边界；这不是模型能力提升。

机制依据见 [LangGraph 官方仓库及项目文档](https://github.com/langchain-ai/langgraph)；其中关于性能、安全或泛化的评价，除非另附独立实验，否则仅属于系统分析推断。

**项目结构图**

```mermaid
%%{init: {"flowchart": {"useMaxWidth": true, "nodeSpacing": 20, "rankSpacing": 24, "curve": "linear"}, "themeVariables": {"fontSize": "12px"}}}%%
flowchart TD
  A[初始 State] --> B[Node A]
  B --> C{Conditional Edge}
  C -->|继续| D[Node B]
  C -->|需审批| E[Interrupt / Human]
  E --> F[Checkpoint]
  F --> D
  D --> G{结束条件}
  G -->|未完成| B
  G -->|完成| H[Final State]
  I[Persistence Layer] --- F
```

*图注：依据 [LangGraph 官方仓库](https://github.com/langchain-ai/langgraph) 的公开接口与实现整理；此图是项目机制示意而非逐文件证明，未公开的实现细节待源码核验。*

**技术判断与边界：** 显式状态图和 checkpoint 使暂停、人工审批与失败恢复更可建模；代价是状态 schema 和版本迁移需要维护，且 checkpoint 不能自动回滚已经发生的外部副作用。

### 3. [mattpocock/skills](https://github.com/mattpocock/skills) — 将操作知识封装成可发现的技能

**技术分析**

**mattpocock/skills 把任务操作知识构造成可发现的技能工件，关键取舍是版本一致性与技能可信来源。**

Agent 的执行质量经常受制于团队经验是否以稳定形式传递：复杂指令可能散落在 prompt、文档和个人习惯里，随着模型或工具变化很难回归。[Skill](https://www.google.com/search?q=Skill%20%E6%8A%80%E6%9C%AF%E5%8E%9F%E7%90%86%20%E8%A7%A3%E9%87%8A "Skill：可复用任务指引/资源包，本身不是安全沙箱")s 这类目录化机制将任务指引、资源引用和执行约定封装为可发现的能力单元，让 Agent 在相关任务出现时加载适用说明。它的技术价值在于把程序性知识从一次性上下文转成可版本管理的资产，但“技能”本身不是可执行沙箱，也不保证模型每次遵守。技能内容可能过期、相互冲突或诱导模型越权，因此需要清晰的触发条件、输入前提、依赖资源和失败处理。若技能只包含自然语言说明，执行结果仍依赖模型解释；若包含脚本或工具，权限边界和供应链风险就更加重要。应以固定任务集回归测试技能的触发率、完成率和错误动作，并检查版本变化是否改变行为。技能复用的真正收益要用任务质量和维护成本衡量，而不是目录数量。

机制依据见 [mattpocock/skills 官方仓库及项目文档](https://github.com/mattpocock/skills)；其中关于性能、安全或泛化的评价，除非另附独立实验，否则仅属于系统分析推断。

**项目结构图**

```mermaid
%%{init: {"flowchart": {"useMaxWidth": true, "nodeSpacing": 20, "rankSpacing": 24, "curve": "linear"}, "themeVariables": {"fontSize": "12px"}}}%%
flowchart TD
  A[用户任务] --> B[技能发现 / 匹配]
  B --> C[技能元数据与触发条件]
  C --> D[加载说明 / 资源]
  D --> E[模型规划]
  E --> F[工具或脚本执行]
  F --> G[结果验证]
  G --> H[完成 / 错误反馈]
  H -.经验回归测试.-> C
```

*图注：依据 [mattpocock/skills 官方仓库](https://github.com/mattpocock/skills) 的公开接口与实现整理；此图是项目机制示意而非逐文件证明，未公开的实现细节待源码核验。*

**技术判断与边界：** Skills 把重复工程经验变成可发现模块，能减少提示词复制；它不等于可靠的插件沙箱，技能内容可能过期或冲突，任何脚本与外部工具都仍应由执行层限制权限。

### 4. [claude-mem](https://github.com/thedotmack/claude-mem) — 跨会话记忆与上下文压缩

**技术分析**

**claude-mem 通过会话摘要和持久化检索连接短期上下文与长期状态，同时引入记忆污染风险。**

长期任务不能无限携带完整对话：上下文窗口有限，历史内容也混有重复信息、过期事实和偶发错误。claude-mem 代表一种[记忆](https://www.google.com/search?q=%E8%AE%B0%E5%BF%86%20%E6%8A%80%E6%9C%AF%E5%8E%9F%E7%90%86%20%E8%A7%A3%E9%87%8A "Agent 记忆：选择性保留历史信息供后续检索，可能过期或错误")管线：从交互中提取观察，整理或压缩后存储，再根据后续任务检索相关信息并注入上下文。这个过程的难点不是简单“记得更多”，而是决定什么值得保存、如何标注时间和来源、何时失效，以及检索结果如何影响模型。压缩会丢失细节，检索会遗漏关键事实，错误记忆则可能在多个会话中反复影响决策。对涉及隐私或机密的环境，还必须明确保存范围、删除策略和本地/远端存储边界。评估应使用长期任务测试，测量召回关键事实的比例、过期记忆误用率、上下文 token 节省量和最终任务质量；仅展示能回忆某条事实不足以证明记忆机制可靠。

机制依据见 [claude-mem 官方仓库及项目文档](https://github.com/thedotmack/claude-mem)；其中关于性能、安全或泛化的评价，除非另附独立实验，否则仅属于系统分析推断。

**项目结构图**

```mermaid
%%{init: {"flowchart": {"useMaxWidth": true, "nodeSpacing": 20, "rankSpacing": 24, "curve": "linear"}, "themeVariables": {"fontSize": "12px"}}}%%
flowchart TD
  A[会话 / 工具观察] --> B[提取与清洗]
  B --> C[摘要 / 结构化记忆]
  C --> D[存储与索引]
  E[新任务] --> F[检索查询]
  D --> F
  F --> G[相关性排序 / 时效过滤]
  G --> H[上下文注入]
  H --> I[Agent 决策]
  J[删除 / 过期 / 隐私策略] --- D
```

*图注：依据 [claude-mem 官方仓库](https://github.com/thedotmack/claude-mem) 的公开接口与实现整理；此图是项目机制示意而非逐文件证明，未公开的实现细节待源码核验。*

**技术判断与边界：** 跨会话记忆能减少重复解释并保存长期任务线索，但摘要与检索可能引入错误、过期或敏感内容；质量关键在写入标准、来源/时间戳、冲突消解和遗忘机制，而不只是检索命中率。

### 5. [tester-army/e2e](https://github.com/tester-army/e2e) — Agent 驱动的端到端测试

**技术分析**

**tester-army/e2e 将浏览器交互后的可观察页面与测试断言反馈给 Agent，使结果可被证据链约束。**

传统 UI 自动化依赖脆弱的选择器与固定等待；页面稍有改版就可能失败。 Agent 驱动测试试图把“用户目标”转成浏览器动作，并利用页面观测、断言、截图或轨迹来判断是否完成。其难点在于将自然语言目标变成可验证条件：如果只让模型判断页面“看起来对”，测试可能把错误状态误判为通过；如果等待和重试策略不明确，偶发网络延迟会造成 flaky tests。浏览器操作还涉及登录态、测试数据和外部副作用，必须在隔离环境运行。工程上要把模型的探索能力与确定性断言分开，关键业务结果应由 DOM 状态、API 响应或数据库状态验证，而不是只靠模型自评。评估应在同一组测试任务上重复运行多次，报告成功率、误报/漏报、平均执行时间、成本和 flaky rate。Agent 可以降低编写脚本的门槛，但不会自动消除测试设计问题。

机制依据见 [tester-army/e2e 官方仓库及项目文档](https://github.com/tester-army/e2e)；其中关于性能、安全或泛化的评价，除非另附独立实验，否则仅属于系统分析推断。

**项目结构图**

```mermaid
%%{init: {"flowchart": {"useMaxWidth": true, "nodeSpacing": 20, "rankSpacing": 24, "curve": "linear"}, "themeVariables": {"fontSize": "12px"}}}%%
flowchart TD
  A[自然语言测试目标] --> B[测试计划]
  B --> C[浏览器观察]
  C --> D[动作选择]
  D --> E[Browser Action]
  E --> F[页面状态 / 网络结果]
  F --> G[断言与证据采集]
  G -->|未达目标| C
  G -->|通过 / 失败| H[报告 / Trace / Screenshot]
```

*图注：依据 [tester-army/e2e 官方仓库](https://github.com/tester-army/e2e) 的公开接口与实现整理；此图是项目机制示意而非逐文件证明，未公开的实现细节待源码核验。*

**技术判断与边界：** Agent 驱动的端到端测试有机会降低编写脆弱 UI 脚本的成本，但自然语言动作并不天然确定；实际价值需要重复运行稳定性、明确断言和失败 trace 支持，不能以成功截图替代 flaky rate。

### 6. [Alibaba Open Code Review](https://github.com/alibaba/open-code-review) — 模型审查与 CI 的结合

**技术分析**

**Alibaba Open Code Review 把模型建议放入代码变更审查环节，但审查模型并不天然具有真实性保证。**

代码审查要理解变更语义、调用上下文和潜在回归，纯静态规则容易漏掉语义问题，纯模型评论则可能产生误报、泛泛建议或定位错误。Open Code Review 代表将 [diff](https://www.google.com/search?q=diff%20%E6%8A%80%E6%9C%AF%E5%8E%9F%E7%90%86%20%E8%A7%A3%E9%87%8A "Diff：代码变更集合，审查系统据此识别潜在问题") 处理、规则/模型分析、评论定位与持续集成流程结合的路线。关键工程问题是如何把模型输出约束成可操作的评论：需要把问题映射到具体文件和行，过滤重复意见，处理模型无法确定的情况，并避免将敏感代码无控制地发送到外部服务。模型提出的风险不是已证实 bug，因此审查系统需要可追踪的证据和人工反馈。评价不应只数评论条数，而要用人工标注的历史 PR 测 precision、recall、误报严重程度、开发者采纳率和额外审查时间。若只优化评论数量，系统可能以噪声换取表面覆盖。在机制层面重点看 diff 如何分块、上下文如何补齐、评论如何回写以及 CI 失败条件是什么。

机制依据见 [Alibaba Open Code Review 官方仓库及项目文档](https://github.com/alibaba/open-code-review)；其中关于性能、安全或泛化的评价，除非另附独立实验，否则仅属于系统分析推断。

**项目结构图**

```mermaid
%%{init: {"flowchart": {"useMaxWidth": true, "nodeSpacing": 20, "rankSpacing": 24, "curve": "linear"}, "themeVariables": {"fontSize": "12px"}}}%%
flowchart TD
  A[PR / Diff] --> B[Diff 解析与上下文补齐]
  B --> C[规则检查]
  B --> D[模型分析]
  C --> E[结果归一化]
  D --> E
  E --> F[去重 / 置信与位置校验]
  F --> G[PR 行级评论]
  G --> H[人工反馈 / CI 状态]
  H -.回归数据.-> D
```

*图注：依据 [Alibaba Open Code Review 官方仓库](https://github.com/alibaba/open-code-review) 的公开接口与实现整理；此图是项目机制示意而非逐文件证明，未公开的实现细节待源码核验。*

**技术判断与边界：** 模型辅助代码审查可以发现规则式 lint 难以覆盖的上下文问题，但误报、重复评论和漏检会消耗审查者注意力；项目质量需在历史 PR 盲测上以真实缺陷标注验证，而不是按生成评论数量判断。

### 7. [morluto/rea](https://github.com/morluto/rea) — 通过交互轨迹理解既有软件

**技术分析**

**REA 将应用交互观测和二进制分析组织为证据链，而不能据有限行为轨迹保证原程序被完整复原。**

既有软件常缺少文档，或者源码复杂到无法快速判断真实行为。让 Agent 通过操作界面探索软件，可以获得动作、[状态](https://www.google.com/search?q=%E7%8A%B6%E6%80%81%20%E6%8A%80%E6%9C%AF%E5%8E%9F%E7%90%86%20%E8%A7%A3%E9%87%8A "状态：描述当前任务/环境的信息，是恢复和决策的依据")变化和界面反馈组成的行为证据，再据此归纳流程。这条路线将 Agent 从“执行已知步骤”扩展到“探索并建立软件行为模型”，潜在用途包括迁移、测试生成和理解遗留系统。但探索轨迹不等于完整规格：界面状态可能隐藏后台行为，随机探索也可能遗漏罕见分支，模型还可能将相关性误判为因果。若软件具有删除、付款或发送等副作用，探索必须在获授权的测试环境中进行。技术评估应明确状态覆盖、动作覆盖、重复运行一致性和模型生成的行为描述是否经独立验证。阅读项目时应查清它记录哪些观测、如何表示状态、何时选择下一动作，以及最终产物是操作脚本、结构模型还是自然语言总结。演示一个应用不能证明可泛化理解任意软件。

机制依据见 [morluto/rea 官方仓库及项目文档](https://github.com/morluto/rea)；其中关于性能、安全或泛化的评价，除非另附独立实验，否则仅属于系统分析推断。

**项目结构图**

```mermaid
%%{init: {"flowchart": {"useMaxWidth": true, "nodeSpacing": 20, "rankSpacing": 24, "curve": "linear"}, "themeVariables": {"fontSize": "12px"}}}%%
flowchart TD
  A[目标软件 / 测试环境] --> B[界面与状态观察]
  B --> C[状态 / 动作轨迹]
  C --> D[探索策略]
  D --> E[下一步交互]
  E --> A
  C --> F[行为归纳 / 软件模型]
  F --> G[人工或自动验证]
```

*图注：依据 [morluto/rea 官方仓库](https://github.com/morluto/rea) 的公开接口与实现整理；此图是项目机制示意而非逐文件证明，未公开的实现细节待源码核验。*

**技术判断与边界：** 通过交互轨迹理解软件，可把“试着操作”变成可回放证据；但探索轨迹覆盖不到的状态和权限路径仍会遗漏，自动形成的描述应能被实际动作记录支持，不能当作完整逆向结果。

### 8. [text-to-cad](https://github.com/earthtojake/text-to-cad) — 从自然语言到可编辑几何模型

**技术分析**

**text-to-cad 的关键输出是可修改的几何工件，约束冲突和生成几何可制造性比语言流畅度更重要。**

自然语言生成图像可以接受视觉近似，但 [CAD](https://www.google.com/search?q=CAD%20%E6%8A%80%E6%9C%AF%E5%8E%9F%E7%90%86%20%E8%A7%A3%E9%87%8A "CAD：计算机辅助设计，几何输出需满足尺寸与拓扑约束") 输出需要尺寸、拓扑和几何约束可编辑，不能只看渲染图是否像目标。 text-to-cad 的路线是把文字需求转成 CAD 生成过程，并由几何后端创建模型。关键技术边界在于语言描述往往缺少精确尺寸、约束或制造条件，系统必须推断缺失参数或请求用户补充；即使生成成功，也需要几何内核验证实体是否有效、尺寸是否一致、面是否自交。文本模型擅长补全意图，却不天然保证几何约束满足，因此应将生成与验证分离。该类工具可能降低概念建模的起步成本，但距离工程设计还差公差、材料、装配、可制造性和版本管理。评估应使用明确的尺寸约束和参考模型，比较几何有效率、尺寸误差、可编辑性和后续人工修改时间。仅展示几个视觉上相似的模型，不足以证明其适用于生产 CAD。

机制依据见 [text-to-cad 官方仓库及项目文档](https://github.com/earthtojake/text-to-cad)；其中关于性能、安全或泛化的评价，除非另附独立实验，否则仅属于系统分析推断。

**项目结构图**

```mermaid
%%{init: {"flowchart": {"useMaxWidth": true, "nodeSpacing": 20, "rankSpacing": 24, "curve": "linear"}, "themeVariables": {"fontSize": "12px"}}}%%
flowchart TD
  A[文本需求] --> B[参数 / 约束提取]
  B --> C[CAD 中间表示或脚本]
  C --> D[几何内核执行]
  D --> E[实体有效性检查]
  E -->|有效| F[STEP / STL 等输出]
  E -->|失败| G[错误反馈 / 参数修订]
  G --> C
  F --> H[尺寸与可制造性检查]
```

*图注：依据 [text-to-cad 官方仓库](https://github.com/earthtojake/text-to-cad) 的公开接口与实现整理；此图是项目机制示意而非逐文件证明，未公开的实现细节待源码核验。*

**技术判断与边界：** 文本转 CAD 的技术门槛在于把语言约束转成几何内核能够接受的实体和参数；渲染图相似不表示尺寸、拓扑、装配和制造约束有效，必须由几何检查与领域规则验证。

### 9. [openrig](https://github.com/mvschwarz/openrig) — 多 Agent 分工与协调

**技术分析**

**openrig 将多 Agent 任务、会话和角色依赖组织为可恢复编排，正确性仍取决于共享状态隔离。**

[多 Agent](https://www.google.com/search?q=%E5%A4%9A%20Agent%20%E6%8A%80%E6%9C%AF%E5%8E%9F%E7%90%86%20%E8%A7%A3%E9%87%8A "多 Agent：多个模型执行单元协作，收益需与协调和通信成本对照") 系统假设复杂任务可以拆分为若干子任务，由不同角色并行或串行完成。但分工本身会带来协调成本：共享状态可能过期，多个角色可能重复工作，输出之间可能冲突，最后还需要合并与验证。openrig 可作为研究多角色协作工作流的入口；实现层面需要以当前仓库实际实现为准，确认角色定义、任务分配、消息传递和结果合并机制，不要仅根据项目名称推断其内部架构。多 Agent 是否优于单 Agent，取决于任务是否可分解、角色间依赖是否低、通信成本和模型调用成本是否可控。若子任务高度耦合，增加 Agent 可能只增加 token 消耗和错误面。评估必须使用相同任务集与预算，对照单 Agent、顺序协作和并行协作，记录成功率、总延迟、token 成本、冲突率和人工修复量。没有这样的对照，就只能说系统支持协作流程，不能声称协作提高了质量。

机制依据见 [openrig 官方仓库及项目文档](https://github.com/mvschwarz/openrig)；其中关于性能、安全或泛化的评价，除非另附独立实验，否则仅属于系统分析推断。

**项目结构图**

```mermaid
%%{init: {"flowchart": {"useMaxWidth": true, "nodeSpacing": 20, "rankSpacing": 24, "curve": "linear"}, "themeVariables": {"fontSize": "12px"}}}%%
flowchart TD
  A[主任务] --> B[任务分解 / Coordinator]
  B --> C[Agent A]
  B --> D[Agent B]
  B --> E[Agent C]
  C --> F[共享任务状态 / 消息]
  D --> F
  E --> F
  F --> G[结果合并 / 冲突处理]
  G --> H[验证与最终输出]
```

*图注：依据 [openrig 官方仓库](https://github.com/mvschwarz/openrig) 的公开接口与实现整理；此图是项目机制示意而非逐文件证明，未公开的实现细节待源码核验。*

**技术判断与边界：** 多 Agent 分工可能提升并行性和角色专长，但共享状态、消息交换、冲突合并与重复工作会增加成本；是否优于单 Agent 必须用相同任务、模型预算、工具权限和成功标准进行对照。

### 10. [pstack-claude](https://github.com/michael-denyer/pstack-claude) — 将编码任务拆成阶段化流程

**技术分析**

**pstack-claude 将编码活动拆成有阶段契约的流程，只有外部可执行测试才能防止错误逐级传递。**

单轮“帮我实现功能”指令容易跳过需求澄清、代码定位、测试、复核和交付说明，尤其在代码库较大时，模型可能过早开始修改。阶段化编码[工作流](https://www.google.com/search?q=%E5%B7%A5%E4%BD%9C%E6%B5%81%20%E6%8A%80%E6%9C%AF%E5%8E%9F%E7%90%86%20%E8%A7%A3%E9%87%8A "工作流：把模型调用、工具、验证和恢复组成明确执行链")把任务拆成多个状态，每阶段明确输入、输出和完成条件，并在阶段之间传递必要上下文。这种设计能让过程更可观察，也方便在某一阶段失败后重新执行；但如果阶段交接只传自然语言摘要，关键约束可能在压缩中丢失，阶段过多也会增加 token 成本和等待时间。真正有效的流程应把可验证工件作为阶段边界，例如修改计划、测试结果、diff、静态检查和最终摘要，而不是依赖模型自述“已完成”。 应比较阶段化流程与单轮提示在同一 bugfix 或功能任务集上的通过率、回归缺陷、人工干预和成本，并记录测试是否真实执行。阶段化只是组织机制，不是正确性证明。

机制依据见 [pstack-claude 官方仓库及项目文档](https://github.com/michael-denyer/pstack-claude)；其中关于性能、安全或泛化的评价，除非另附独立实验，否则仅属于系统分析推断。

**项目结构图**

```mermaid
%%{init: {"flowchart": {"useMaxWidth": true, "nodeSpacing": 20, "rankSpacing": 24, "curve": "linear"}, "themeVariables": {"fontSize": "12px"}}}%%
flowchart TD
  A[任务 / 代码库] --> B[需求澄清]
  B --> C[代码探索与计划]
  C --> D[实现阶段]
  D --> E[测试与静态检查]
  E -->|失败| F[定位与修复]
  F --> D
  E -->|通过| G[Diff 复核]
  G --> H[交付摘要 / 已知限制]
  I[阶段状态与上下文] --- B
  I --- C
  I --- D
  I --- E
```

*图注：依据 [pstack-claude 官方仓库](https://github.com/michael-denyer/pstack-claude) 的公开接口与实现整理；此图是项目机制示意而非逐文件证明，未公开的实现细节待源码核验。*

**技术判断与边界：** 阶段化编码流程能显式安排需求澄清、实现、测试和审查，但流程步骤本身不保证产出正确；若阶段完成条件只检查文本而没有可执行测试和工件，流程容易沦为形式化的 prompt 模板。
