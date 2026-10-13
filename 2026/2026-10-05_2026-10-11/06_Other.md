# 方向报告 06｜Other：数据谱系、评测与 AI 工程基础设施

**周期：** 2026-10-05—2026-10-11

## 技术判断

这些项目通常不直接提出新的模型架构，但决定模型研发能否从一次实验变成可重复、可上线、可追责的工程系统。共通问题是**数据和代码版本如何关联、评测是否可复现、模型线上为何退化、跨服务故障如何定位**。本报告列出的是有长期工程价值的技术入口，不等同于本周官方 Trending 排名。

## 10 个项目精读

### 1. [MLflow](https://github.com/mlflow/mlflow) — 把训练实验变成有谱系的记录

**技术分析**

训练结果通常由代码、参数、数据切分、环境和随机种子共同决定；只存一个最终分数或模型文件，无法解释结果为什么变化。MLflow Tracking 将参数、指标、运行信息和工件绑定到 run，再通过实验组织不同对照，模型注册能力则将训练产物与版本、阶段和部署生命周期连接。技术关键不在“画曲线”，而是**同一个模型工件能否反查对应的代码、数据和配置**。若数据路径指向可变文件、日志异步失败或模型别名被覆盖，实验看似被记录，实际仍不可复现。对 LLM 系统还需记录提示模板、检索索引版本、评测器模型和推理参数，否则分数变化无法归因。阅读时应看 Tracking API 怎样写入 backend store、artifact store 如何保存文件，以及 Model Registry 如何管理版本转换；项目本身不能保证团队记录了完整元数据。

**项目结构图**

```mermaid
flowchart TD
  A[训练/评测代码] --> B[MLflow Client API]
  B --> C[Tracking Server]
  C --> D[Backend Store：参数/指标/run]
  C --> E[Artifact Store：模型/文件]
  D --> F[Experiment 对照]
  E --> G[Model Registry 版本]
  F --> H[可复现性审查]
  G --> I[部署/回滚]
```

**如何读懂本项目：** 先跑最小 Tracking 示例，追踪 start_run、log_param/log_metric、log_artifact 的调用；再定位 backend store 与 artifact store 的职责边界，最后检查 registry 版本如何关联原始 run。

### 2. [Weights & Biases](https://github.com/wandb/wandb) — 分布式训练的实验可观测层

**技术分析**

分布式训练中，单个 worker 的日志可能不完整，指标还会涉及同步、聚合和 step 对齐；将日志写在本地文件也难以跨实验对比。W&B SDK 通过 run 生命周期组织配置、指标、系统信息和 artifacts，并将本地训练过程与可视化/协作平台连接。关键分析点是指标在何时、由哪个进程、以怎样的 step 定义被记录；若多个 worker 写入相同指标或 step 不一致，曲线可能误导判断。Artifacts 能提供数据和模型版本引用，但不自动冻结外部数据源、依赖版本或随机状态。使用时还要考虑离线模式、断网缓冲、日志上传失败和敏感输入泄露。对 LLM/Agent 实验而言，建议将模型版本、prompt、数据切分、judge 配置和运行成本一并记录，再用固定任务集比较。平台可提高可见性，却不能替代严谨的实验设计或隐私治理。

**项目结构图**

```mermaid
flowchart LR
  A[Trainer/Workers] --> B[wandb.init / Run Context]
  B --> C[Config + Metrics + System Stats]
  C --> D[本地缓冲/离线日志]
  D --> E[同步/上传]
  E --> F[云端 Run 与图表]
  B --> G[Artifact 引用与版本]
  G --> H[跨实验比较/模型溯源]
```

**如何读懂本项目：** 从 run 初始化和 log 接口入手，找到 step、summary 与 history 的差别；再查看 artifact 版本引用、离线/在线同步和多进程日志示例，验证网络断开时数据如何恢复。

### 3. [Evidently](https://github.com/evidentlyai/evidently) — 将数据漂移转化为监控证据

**技术分析**

线上模型可能在代码未变的情况下退化，因为用户群、输入格式或环境分布发生变化。Evidently 提供数据质量、分布差异和模型表现报告，用参考数据与当前数据对照，形成可查看的统计信号。这里最重要的是区分**输入分布变化、标签/目标关系变化和业务指标下降**：检测到特征漂移并不能证明模型已经变差；没有漂移也不意味着目标关系稳定。漂移统计还依赖特征类型、样本量、阈值和参考窗口，类别不平衡或样本少时容易出现噪声告警。项目适合将诊断步骤标准化，但告警阈值仍需结合业务代价校准，并与真实标签到达后的模型表现交叉验证。阅读时追踪数据 schema、metric 计算和报告生成，确认每个图表代表的统计假设，避免把可视化报告当成因果结论。

**项目结构图**

```mermaid
flowchart TD
  A[参考数据/基线] --> C[Dataset/Column Mapping]
  B[当前线上样本] --> C
  C --> D[数据质量指标]
  C --> E[分布漂移指标]
  F[延迟到达的真实标签] --> G[模型质量指标]
  D --> H[Report / Test Results]
  E --> H
  G --> H
  H --> I[阈值校准/告警/调查]
```

**如何读懂本项目：** 找一个数据漂移报告，追踪 column mapping、statistical test 与阈值选择；对同一数据分别改变样本量、参考窗口和类别比例，观察告警敏感性，再验证其与模型真实错误率是否一致。

### 4. [Ragas](https://github.com/explodinggradients/ragas) — 拆解 RAG 系统的检索与生成错误

**技术分析**

检索增强生成系统出错可能来自检索没找到证据、上下文排序不合理、模型忽略证据，或答案虽相关却包含无依据结论。Ragas 将 RAG 质量拆成若干评估维度，例如检索上下文相关性、答案与问题的相关性，以及答案对提供上下文的忠实程度。**这些维度测量的是不同失效模式，不能合并成一个分数就判断系统可靠**。部分指标依赖 LLM 作为 judge，因而会受 judge 模型、提示、温度与参考答案质量影响；分数与人工标注也可能存在系统性偏差。评估设计应保存问题、检索片段、最终答案、模型版本和评审提示，并抽样与人工标注对照，测量一致性及对答案微小改写的敏感性。对于企业 RAG，还需单独测引用正确率、关键事实遗漏和权限泄露，通用指标并不覆盖全部业务风险。

**项目结构图**

```mermaid
flowchart TD
  A[问题 + 检索结果 + 答案] --> B[Sample / Dataset Adapter]
  B --> C[Metric Selection]
  C --> D[Context Relevance]
  C --> E[Faithfulness]
  C --> F[Answer Relevance]
  D --> G[LLM Judge / Embedding / Rules]
  E --> G
  F --> G
  G --> H[分项得分与样本级解释]
  H --> I[与人工标注比对/改进检索链]
```

**如何读懂本项目：** 先读指标定义和最小 evaluation 示例，再跟踪每项 metric 对输入字段的要求、judge prompt 与解析逻辑；用有意构造的检索失败、无关上下文和幻觉答案验证指标是否能区分问题来源。

### 5. [DeepEval](https://github.com/confident-ai/deepeval) — 将 LLM 语义回归纳入测试流程

**技术分析**

传统单元测试能精确验证函数返回值，却不容易检查生成内容是否忠实、是否完成任务或是否泄露不该输出的信息。DeepEval 将测试样例、指标和模型调用组织成类似测试框架的接口，使 LLM 应用可以在改 prompt、模型、检索逻辑或工具之后执行回归评测。其主要风险是测试结果依赖 judge：指标阈值、判分模型和评估提示发生变化时，CI 可能对同一输出得出不同结论。可靠做法是把语义测试与确定性断言分层；格式、权限和函数副作用应由普通代码测试验证，模糊的质量维度才使用模型评审。小型测试集容易过拟合当前 prompt，也可能漏掉长尾输入，因此应从生产失败、人工反馈和对抗样例持续扩充。阅读重点是 test case schema、metric 判分过程、阈值判断和 CI 集成，评估其误报率与漏报率，而不是只看测试绿灯。

**项目结构图**

```mermaid
flowchart TD
  A[应用输出/检索轨迹] --> B[Test Case]
  B --> C[确定性断言]
  B --> D[LLM-based Metrics]
  D --> E[Judge 模型与评分解释]
  C --> F[Pass/Fail 聚合]
  E --> F
  F --> G[本地测试/CI Gate]
  G -->|失败| H[样例保存与问题归因]
  H --> B
```

**如何读懂本项目：** 从最小测试定义追踪指标类和 judge 调用，再核对阈值如何转成 pass/fail；为同一应用构造确定性规则测试和语义评分测试，比较两者边界。

### 6. [OpenTelemetry Python](https://github.com/open-telemetry/opentelemetry-python) — 跨模型与工具调用的可观测标准

**技术分析**

一个 Agent 请求可能串联 API 网关、模型服务、向量库、数据库、浏览器和业务工具。若每个服务只写本地日志，很难重建一次请求的总延迟、重试与错误传播。OpenTelemetry 用 trace、span、context propagation 和 metrics 建立跨服务的观测模型：上游 span 的上下文被传给下游，多个 span 形成调用树，并记录时长、状态和属性。关键点是上下文传播必须贯穿异步任务、线程和网络边界，否则链路会断开；而采样策略可能导致低频故障未被记录。可观测并不等于安全：prompt、用户标识或工具返回内容若被直接写入 span，可能带来隐私风险。应把诊断需要与数据最小化结合，过滤敏感属性，并将 trace 与业务任务 ID 关联。阅读时区分 API、SDK 和 exporter 的责任，确认 instrumentation 是否真正覆盖所有调用路径。

**项目结构图**

```mermaid
flowchart LR
  A[应用代码/Instrumentor] --> B[Tracer / Meter API]
  B --> C[Span 与 Context]
  C --> D[跨进程传播注入/提取]
  D --> E[下游模型/数据库/工具]
  C --> F[Processor / Sampling]
  F --> G[Exporter]
  G --> H[Collector / Backend]
  H --> I[Trace 查询与延迟归因]
```

**如何读懂本项目：** 从 tracer provider、instrumentation 和 exporter 示例入手，检查 span context 如何注入 HTTP 请求及从下游恢复；用异步调用和错误重试测试链路连续性，并确认敏感字段过滤在 exporter 前发生。

### 7. [DVC](https://github.com/iterative/dvc) — 用内容寻址和流水线描述数据版本

**技术分析**

Git 适合追踪文本源代码，却不适合把大型数据集、视频和模型权重直接存进仓库。DVC 将工件内容与轻量元数据关联，配合远端存储和 pipeline 描述数据生成/模型训练步骤，使代码版本与数据版本可以共同回溯。关键机制是依赖与输出关系：当输入或命令发生变化时，流水线可以判断哪些阶段需要重跑。但这依赖元数据准确、命令环境可复现以及远端工件仍可取回；只保存数据指针而丢失对应对象，并不能复现训练。随机数据增强、外部 API 和未锁定包版本也可能让相同 pipeline 得到不同结果。因此，数据版本控制应同时记录原始来源、处理代码、schema、校验和、许可和敏感数据访问边界。阅读时重点关注 .dvc 元数据、remote/cache、pipeline stage 与依赖检测，不要把“Git 提交可回滚”误当成整条数据链已被冻结。

**项目结构图**

```mermaid
flowchart TD
  A[原始数据/远端工件] --> B[.dvc 元数据与校验]
  B --> C[本地缓存/Remote Storage]
  D[代码版本/Git] --> E[dvc.yaml Pipeline]
  C --> E
  E --> F[预处理阶段]
  F --> G[训练/评测阶段]
  G --> H[模型/报告工件]
  H --> I[可追溯版本与复现]
```

**如何读懂本项目：** 从一个 .dvc 文件看哈希与输出路径，再追踪 dvc.yaml 的 stage、依赖和缓存命中；将输入数据或处理代码改动一次，观察哪些阶段被重新执行。

### 8. [Great Expectations](https://github.com/great-expectations/great_expectations) — 把数据质量要求变成可执行契约

**技术分析**

模型训练前后的数据错误常以“模型性能变差”出现：字段类型变化、关键列空值、枚举值突然新增或业务约束被破坏，都可能污染输入。Great Expectations 允许将数据假设表达为 expectations，并在批数据或数据管道上执行验证，生成结果和文档。与单纯统计摘要不同，数据契约明确表达“什么情况被认为不合格”；但契约本身必须覆盖真实风险，若规则过宽就会漏检，若过严则会在合法分布变化时频繁阻塞任务。规则也不能无条件要求生产分布固定——合法的季节变化可能是预期的，异常变化是否需要拦截取决于用途。要把硬性约束（类型、唯一键、非空字段）与统计告警（分布、范围）分开管理，并给每条规则配异常样例与负责人。阅读重点是 expectation 定义、validator 执行、批次/数据资产配置和验证结果如何被 CI 或调度系统消费。

**项目结构图**

```mermaid
flowchart TD
  A[数据源/Batch] --> B[Datasource 与 Batch Definition]
  B --> C[Expectation Suite]
  C --> D[Validator 执行]
  B --> D
  D --> E[Validation Results]
  E --> F[Data Docs/报告]
  E --> G{质量门禁}
  G -->|通过| H[下游训练/推理]
  G -->|失败| I[隔离/告警/修复]
```

**如何读懂本项目：** 找一个 expectation suite 追踪配置、validator 与结果对象，再确认失败是否实际阻断下游流程；用空值、类型变化和合法分布漂移分别测试规则的有效性。

### 9. [BentoML](https://github.com/bentoml/BentoML) — 将模型依赖封装为可部署服务

**技术分析**

训练脚本通常隐藏着模型权重、预处理依赖、系统库和启动参数；若只将模型文件交付给部署团队，同一模型可能在不同环境表现不一致。BentoML 将服务逻辑、模型引用、依赖和运行配置组织成可打包的服务单元，便于生成容器并在统一接口下处理请求。对生成式模型而言，除了模型加载，还要考虑并发队列、流式返回、超时、显存管理和健康检查；封装并不能自动解决这些运行时问题。打包成功仅证明部署工件构建完成，不证明吞吐、延迟、弹性或安全边界满足生产要求。应核验模型权重是否按版本固定、预处理代码是否一起打包、环境变量和密钥如何注入，以及新版本失败如何回滚。阅读时沿 service 定义、model artifact、build 和 serve 路径追踪，从本地运行到容器部署比较实际依赖是否一致。

**项目结构图**

```mermaid
flowchart TD
  A[服务定义/推理函数] --> B[Bento 配置与依赖]
  C[模型权重/模型引用] --> D[Artifact 打包]
  B --> D
  D --> E[Bento 工件]
  E --> F[容器镜像/部署]
  F --> G[API Server]
  G --> H[预处理/模型推理/后处理]
  H --> I[响应/指标/日志]
  I --> J[版本回滚与健康检查]
```

**如何读懂本项目：** 从 service API 与模型加载开始，跟踪 build 如何收集依赖、模型文件和配置；再检查 serve 的请求处理、健康检查和容器化示例，验证同一工件在开发与部署环境的差异。

### 10. [Ray](https://github.com/ray-project/ray) — 用 task、actor 和资源调度扩展 Python 工作负载

**技术分析**

数据处理、超参数搜索、分布式推理和训练会遇到进程管理、资源分配、任务失败和跨节点数据传输问题。Ray 将计算表达为 task（无状态远程函数）和 actor（持有状态的工作单元），由调度层将其映射到可用 CPU/GPU 与节点。这个抽象降低编写分布式程序的门槛，但不消除分布式系统本身的代价：小任务可能被调度和序列化开销吞噬，actor 可能成为瓶颈，数据倾斜会造成部分节点过载，故障恢复还取决于任务是否可重试及副作用是否幂等。对象引用把生产者和消费者关联起来，若传输大型对象或不必要复制，内存和网络都可能成为瓶颈。评测应对照单机实现，记录任务粒度、对象大小、并发、吞吐和尾延迟，而非只比较节点数。阅读时区分 Ray Core 与上层训练/数据组件，避免把所有能力都归因于底层调度器。

**项目结构图**

```mermaid
flowchart TD
  A[Driver 程序] --> B[Task 提交 / Actor 创建]
  B --> C[调度器与资源管理]
  C --> D[Node Worker]
  D --> E[Object Store / ObjectRef]
  E --> F[下游 Task/Actor]
  D --> G[结果/异常]
  G --> A
  H[节点故障/重试策略] --> C
```

**如何读懂本项目：** 从 remote function 和 actor 示例读起，追踪 ObjectRef、资源声明和调度行为；比较本地函数与远程 task 的序列化成本，再用人为抛异常的任务观察重试和状态恢复边界。

## 方法论沉淀

基础设施是否真正提高研发质量，应从**可追溯性、复现成功率、故障定位时间、线上回归检出率与数据安全边界**来衡量。仪表盘数量或“接入了监控”不是效果证据。术语见[研究证据与评测词典](../../glossary/evaluation.md "解释基准、复现、消融、证据等级和趋势统计的可比条件")、[Agent 词典](../../glossary/agent.md "解释 tracing、工具执行、权限和幂等性")。
