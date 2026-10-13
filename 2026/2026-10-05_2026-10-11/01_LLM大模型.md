# 子报告 01｜LLM 与大模型

周期：2026-10-05—2026-10-11；整理日期：2026-10-13。

## 结论先行
本周值得关注的不只是模型本身，也包括推理、接入、成本控制与部署工程。第三方周趋势材料提及 LiteLLM；主题趋势页也列出 AirLLM、Microsoft BitNet 等项目，但采样时刻和榜单规则不同，不能据此拼接官方 Top 10 周榜。以下为研究与工程跟踪名单，并非严格周榜排名。

## 10 个跟踪项目

1. [BerriAI/litellm](https://github.com/BerriAI/litellm) — 统一模型网关、路由、成本与日志。入门：接入两种模型，测试限流、fallback、观测和密钥管理。本周趋势线索：有。
2. [microsoft/BitNet](https://github.com/microsoft/BitNet) — 低比特 LLM 推理框架。入门：研究量化方式、支持硬件和质量/速度权衡。本周趋势线索：第三方主题页提及。
3. [lyogavin/airllm](https://github.com/lyogavin/airllm) — 面向有限显存环境的模型推理。入门：记录峰值显存、首 token 延迟和总吞吐。本周趋势线索：第三方主题页提及。
4. [vllm-project/vllm](https://github.com/vllm-project/vllm) — 高吞吐 LLM 推理与服务。入门：理解 continuous batching 与 KV cache。
5. [huggingface/text-generation-inference](https://github.com/huggingface/text-generation-inference) — 模型部署服务。入门：比较部署、监控与硬件支持，并检查维护状态。
6. [ggml-org/llama.cpp](https://github.com/ggml-org/llama.cpp) — 本地与边缘推理。入门：量化格式、CPU/GPU 后端与模型兼容性。
7. [ollama/ollama](https://github.com/ollama/ollama) — 本地模型运行工具。入门：模型打包、API 和本地服务安全。
8. [huggingface/transformers](https://github.com/huggingface/transformers) — 模型加载、训练和推理生态。入门：tokenizer、generation config 与小型实验。
9. [sgl-project/sglang](https://github.com/sgl-project/sglang) — LLM 服务与结构化生成运行时。入门：比较请求调度、吞吐与延迟。
10. [openai/openai-python](https://github.com/openai/openai-python) — Python API SDK。入门：流式输出、重试、错误处理和结构化输出。

## 推荐实验
固定模型、硬件、量化精度、上下文长度和 batch size，对比吞吐、首 token 延迟、峰值显存与输出质量。模型网关实验加入限流、fallback、日志脱敏和成本统计。

## 数据缺口
本期没有可用的统一周初/周末 Star 快照，故不提供估算的总 Star、周新增或精确排名。上述项目混合趋势线索与长期基础设施，不代表全部在本周上榜。