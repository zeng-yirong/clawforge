# Nanoclaw GRPO Recipe

这个 recipe 把 `vllm_nanoclaw_runtime` 的目录型 agent 任务接进 VERL GRPO，多轮 rollout 仍走 VERL 的 `tool_agent`，奖励函数在最终 workspace 上调用 `verify_workplace.py`。

## 数据目录

`data.train_files` / `data.val_files` 仍然传 Nanoclaw 的 `base_tasks` 目录：

```text
base_tasks/
  tasks/
    data_000001/
      env_builder.py
    prompts/
      data_000001.md
  scripts/                  # 或兼容旧 typo: scrips/
    data_000001/
      verify_workplace.py
```

发现规则和 `vllm_nanoclaw_runtime.tasks` 对齐：

- 任务目录默认匹配 `tasks/data_*`，可用 `+data.nanoclaw_task_glob=...` 改。
- 每个任务必须有 `env_builder.py`。
- prompt 查找顺序是 `tasks/prompts/{task_id}.md`、`tasks/{task_id}/prompt.md`、`tasks/{task_id}/task.md`。
- verifier 查找顺序是 `scripts/{task_id}/verify_workplace.py`、`scripts/{task_id}.py`、`scripts/verify_workplace.py`，同时兼容 `scrips/`。

## 运行方式

Nanoclaw 现在作为最新版 VERL 主仓库中的独立包 `nanoclaw_recipe` 提供，不依赖官方
`recipe` 子模块。最直接的训练入口是：

```bash
bash nanoclaw_recipe/train_half_turn.sh
```

也可以在最新版 VERL 根目录给其他 PPO/GRPO 入口追加这些覆盖项：

```bash
data.train_files=[/path/to/base_tasks] \
data.val_files=[/path/to/base_tasks_val] \
data.prompt_key=prompt \
data.return_raw_chat=True \
data.custom_cls.path=pkg://nanoclaw_recipe.nanoclaw \
data.custom_cls.name=CustomRLHFDataset \
data.tool_config_path=nanoclaw_recipe/nanoclaw_tool_config.yaml \
+data.nanoclaw_task_glob=data_* \
+data.nanoclaw_temp_root=/tmp/verl_nanoclaw_workspaces \
+data.nanoclaw_cleanup_workspaces=True \
+data.nanoclaw_verifier_timeout=300 \
reward.custom_reward_function.path=pkg://nanoclaw_recipe.nanoclaw \
reward.custom_reward_function.name=compute_score \
+reward.custom_reward_function.reward_kwargs.cleanup_workspaces=True \
+reward.custom_reward_function.reward_kwargs.verifier_timeout=300 \
+reward.custom_reward_function.reward_kwargs.reward_score_mode=ratio \
actor_rollout_ref.rollout.multi_turn.enable=True \
actor_rollout_ref.rollout.multi_turn.format=qwen3_coder \
actor_rollout_ref.rollout.multi_turn.tool_config_path=nanoclaw_recipe/nanoclaw_tool_config.yaml
```

如果希望关闭 final answer 硬门槛，但仍鼓励模型主动结束并输出最终回答，可以设置：

```bash
NANOCLAW_REQUIRE_FINAL_ANSWER=False \
NANOCLAW_FINAL_ANSWER_BONUS_ENABLE=True \
NANOCLAW_FINAL_ANSWER_BONUS_SCORE=0.05 \
bash nanoclaw_recipe/train_half_turn.sh
```

只有 rollout 以 `completed_no_tool_call` 正常结束且最后一条 assistant 消息非空时才会获得 bonus。最终奖励为
`verifier reward + final answer bonus - behavior penalties`；未开启时默认 bonus 为 `0`，不改变原有行为。

如果你的数据集没有单独验证集，可以先临时让 `data.val_files` 指向同一个目录。

## 生命周期

一次 rollout 的流程是：

1. `CustomRLHFDataset` 只发现任务并生成 prompt，不提前创建 workspace。
2. 模型第一次调用 workspace tool 时，`NanoclawWorkspaceTool` 为该 rollout 创建独立临时目录。
3. tool 在 `workspace_after` 里运行 `env_builder.py`，之后所有读写工具都限制在这个目录内。
4. rollout 结束后，`compute_score` 在最终 `workspace_after` 上运行 `verify_workplace.py`。
5. 默认评分后删除整个临时目录；调试时可加 `+reward.custom_reward_function.reward_kwargs.keep_failed_workspaces=True`。

这个设计是为了避免 `rollout.n > 1` 时多个采样共享同一个 workspace。workspace 不能在 dataset 阶段创建，因为同一条数据会被复制成多条 rollout 轨迹。

## 长度配置

多轮历史确实会继续喂回 vLLM：`tool_agent_loop.py` 会把 assistant 输出和 tool observation 都追加到 `agent_data.prompt_ids`，下一轮 generation 会带着完整历史。

- `data.max_prompt_length` / `actor_rollout_ref.rollout.prompt_length` 主要约束初始 prompt，也就是 system + user task + tool schema。
- `data.max_response_length` / `actor_rollout_ref.rollout.response_length` 才是多轮 trajectory 的主要预算，里面包含 assistant token 和 tool observation token。
- 如果 `max_response_length=24k`、初始 prompt 约 `2k`，vLLM 的 `max_model_len` 和 `max_num_batched_tokens` 至少要覆盖约 `26k` 以上，再加 tool schema 和安全余量。
- 为了避免 tool observation 把 response 预算吃光，建议继续设置较小的 `actor_rollout_ref.rollout.multi_turn.max_tool_response_length`，例如 `1024` 或 `2048`。

## 奖励

默认从 `workspace_after/workplace_score.json` 读取：

- `total_score` 或 `score`
- `max_score`
- `passed`
- `details[*].max_score` 可用于推导总 `max_score`

`reward_score_mode=ratio` 时优先返回 `score / max_score`；没有 `max_score` 时回退到原始 `score` 或 `passed`。

## 与训练 Agent 同构的纯批量推理

`nanoclaw_recipe.inference` 是 rollout-only 推理入口。它不维护另一套 Agent runner，而是直接复用训练链路：

```text
CustomRLHFDataset
  -> VERL standalone LLMServerManager/vLLM
  -> VERL AgentLoopManager
  -> tool_agent / ToolAgentLoop
  -> NanoclawWorkspaceTool
```

因此任务发现、初始 prompt、Qwen3-Coder 工具格式、多轮 token 拼接、response mask、工具执行和 workspace 创建都与训练相同。该入口是纯 rollout：不创建 `RewardLoopManager`，不调用 `compute_score`，不执行任务自带 verifier，也不请求任何 verifier API。推理结果可以交给后续 benchmark 使用任意验证方法独立评分。

即使某条 trajectory 一次工具都没有调用，输出阶段也会只运行 `env_builder.py` 补建一个未修改的 `workspace_after`，确保每条 rollout 都有统一的最终 workspace。这个过程不会运行 verifier。

0710 的多 checkpoint 配套脚本是：

```bash
bash /path/to/contextBenchmark/v14/0710/inference.sh
```

该脚本不是仅包含推理命令的简化入口。它会在每个 ModelArts 节点执行训练脚本同款的 GCC、CANN、torch-npu、vLLM/vLLM-Ascend、Triton-Ascend、VERL 和 Python 依赖安装，配置 NPU/HCCL/Ray 环境，然后启动纯 rollout Ray 集群。所有常用参数都集中在脚本顶部。若镜像已经预装完全相同的环境，可显式设置 `SETUP_ENVIRONMENT=0` 跳过重复安装。

多个 checkpoint 直接填写脚本顶部的 Bash 数组：

```bash
MODEL_PATHS=(
    /shared/checkpoints/global_step_100/actor/huggingface
    /shared/checkpoints/global_step_200/actor/huggingface
    /shared/checkpoints/global_step_300/actor/huggingface
)

# 可选。留空时会自动提取 global_step_100、global_step_200、global_step_300。
MODEL_NAMES=(
    # step100
    # step200
    # step300
)

OUTPUT_ROOT=/shared/benchmark_rollouts
```

模型会串行加载并推理；同一个模型内部仍使用所有 rollout NPU 并发。每个模型结束后，脚本会等待 Ray 可用 NPU 恢复到总卡数，再加载下一个 checkpoint，避免前一个模型的 actor/placement group 尚未释放。输出结构为：

```text
OUTPUT_ROOT/
  global_step_100/
    step_1/
      data_x_sample_0/
      data_y_sample_0/
  global_step_200/
    step_1/
      data_x_sample_0/
      data_y_sample_0/
```

模型目录下面只写 `step_1/data_x_sample_y/` 样本目录，不再生成 `results.jsonl`、`summary.json`、`dataproto/`、`models.tsv`、`run_status.tsv` 或 `_SUCCESS/_FAILED`。如果该模型的 `step_1/` 已存在，脚本默认停止，避免混入旧结果；设置 `OVERWRITE_OUTPUT=True` 会删除该模型旧目录后重跑。默认遇到某个模型失败立即停止；设置 `CONTINUE_ON_MODEL_ERROR=1` 可继续测试后续 checkpoint。

也可以从作业环境变量传入换行分隔的列表：

```bash
MODEL_PATH_LIST=$'/shared/ckpts/global_step_100/actor/huggingface\n/shared/ckpts/global_step_200/actor/huggingface' \
MODEL_NAME_LIST=$'step100\nstep200' \
OUTPUT_ROOT=/shared/benchmark_rollouts \
bash /path/to/contextBenchmark/v14/0710/inference.sh
```

默认拓扑是 1 台 8-NPU 节点：

```text
rank 0: 8 NPU rollout，INFER_TP=4，共 2 个 vLLM replica
```

因此默认只需申请 1 台 8 卡机器。最低可以使用 4 卡，并把 `NPUS_PER_NODE=4`、`INFER_TP=4`，此时只有 1 个 rollout replica：

```bash
INFER_NNODES=1 \
NPUS_PER_NODE=4 \
INFER_TP=4 \
bash /path/to/contextBenchmark/v14/0710/inference.sh
```

只运行单个模型时仍兼容原来的 `MODEL_PATH` 环境变量：

```bash
MODEL_PATH=/path/to/merged_hf_checkpoint \
BASE_TASKS=/path/to/exported_new_data \
OUTPUT_ROOT=/shared/path/nanoclaw_inference \
N_RESP_PER_PROMPT=1 \
PROMPT_BATCH_SIZE=16 \
AGENT_NUM_WORKERS=32 \
INFER_TP=4 \
bash /path/to/contextBenchmark/v14/0710/inference.sh
```

首次运行建议先限制少量 task，并把输出写到临时目录：

```bash
NANOCLAW_TASK_IDS=data_000001,data_000002 \
OUTPUT_ROOT=/shared/path/nanoclaw_inference_smoke \
PROMPT_BATCH_SIZE=2 \
N_RESP_PER_PROMPT=1 \
bash /path/to/contextBenchmark/v14/0710/inference.sh
```

`MODEL_PATH` 必须是 vLLM 能直接加载的 Hugging Face 模型目录；如果训练产物是 VERL/FSDP 分片 checkpoint，需要先按 VERL model merger 流程导出合并模型。

多 rollout 节点时，同一份脚本需要由 ModelArts 在所有节点执行；脚本使用 `VC_TASK_INDEX` 自动区分 Ray head 和 worker。例如使用 2 台 8 卡 rollout 节点：

```bash
INFER_NNODES=2 \
NPUS_PER_NODE=8 \
INFER_TP=4 \
bash /path/to/contextBenchmark/v14/0710/inference.sh
```

输出目录包含：

```text
OUTPUT_ROOT/
  MODEL_NAME/
    step_1/
      data_x_sample_0/
        workspace_before/
        workspace_after/
        conversation_history.json
        trajectory.json
        tool_events.jsonl
```

- `workspace_after/` 是模型完成操作后的最终工作区，供后续 benchmark 验证。
- `workspace_before/` 是同一个任务的初始工作区，可用于 diff。
- `conversation_history.json` 保存完整对话、final answer、termination reason 和 turn/tool 统计。
- `trajectory.json` 保存 rollout 摘要、对话事件和 workspace 元信息。
- `tool_events.jsonl` 仅在发生工具调用时生成，保存逐次工具参数和 observation。

所有 dataloader batch 都使用 `rollout_step=1`，但 dataset sample index 在全数据集内唯一，因此会统一落入同一个 `step_1/`，不会因为 batch 切分产生 `step_2/step_3`，也不会造成样本目录冲突。

因为不再保存 DataProto，脚本默认 `CALCULATE_LOG_PROBS=False`，避免计算和传输不会落盘的 rollout log-prob。

性能主要由三组参数控制：

- `INFER_TP`：每个 vLLM replica 使用的 NPU 数；
- `PROMPT_BATCH_SIZE`：每批不同任务数；
- `AGENT_NUM_WORKERS`：并发 Agent loop worker 数。

总 NPU 数能被 `INFER_TP` 整除时会自动启动多个 vLLM replica，例如单机 8 NPU、`INFER_TP=4` 会启动 2 个 replica。Agent 使用 sticky session，同一条多轮 trajectory 会固定路由到同一个 replica；不同 trajectory 由全局 least-loaded 调度并发执行。
