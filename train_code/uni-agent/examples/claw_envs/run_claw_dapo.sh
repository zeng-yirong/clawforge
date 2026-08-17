#!/usr/bin/env bash
set -euxo pipefail

# Native claw WORKPLACE + CLI training launcher for verl async agent-loop PPO.
#
# This script follows the shape of run_dapo.sh, but uses:
#   - uni_agent.datasets.claw_native.ClawNativeDataset
#   - examples/claw_envs/agent_config.yaml
#   - local_native execution, no Docker sandbox
#   - per-sample verify_workplace.py reward
#
# Override paths/knobs with environment variables before running.

npu-smi info || true

# ================= 1. Repository and dependency setup =================
VERL_DIR=${VERL_DIR:-/opt/huawei/dataset/zyr_yuyin/youshen/verl-v070}
UNI_AGENT_DIR=${UNI_AGENT_DIR:-/opt/huawei/dataset/zyr_yuyin/youshen/uni-agent}
INSTALL_DEPS=${INSTALL_DEPS:-1}

export PYTHONPATH="${UNI_AGENT_DIR}:${VERL_DIR}:${PYTHONPATH:-}"

if [ "$INSTALL_DEPS" = "1" ]; then
    python3 -m pip install --upgrade pip
    python3 -m pip install -e "$VERL_DIR"
    # uni-agent is loaded through PYTHONPATH because this repo's pyproject may
    # not be installable in all training images.
    python3 -m pip install \
        loguru \
        pydantic \
        pyyaml \
        orjson \
        swe-rex \
        pexpect \
        datasets \
        deepdiff \
        sympy \
        html2text \
        requests \
        beautifulsoup4 \
        json_repair
fi

# Optional Ascend/vLLM environment hooks. Keep these outside the default path
# because different server images usually preinstall them differently.
if [ -n "${ASCEND_ENV_SH:-}" ]; then
    # shellcheck disable=SC1090
    source "$ASCEND_ENV_SH"
fi
if [ -n "${ATB_ENV_SH:-}" ]; then
    # shellcheck disable=SC1090
    source "$ATB_ENV_SH"
fi

# ================= 2. claw native data configuration =================
CLAW_TASKS_DIR=${CLAW_TASKS_DIR:-$UNI_AGENT_DIR/claw_envs/claw_chains/example_tasks}
CLAW_TOOL_DOCS_DIR=${CLAW_TOOL_DOCS_DIR:-$UNI_AGENT_DIR/claw_envs/claw_chains/claw_tool_env_docs}
CLAW_AGENT_CONFIG=${CLAW_AGENT_CONFIG:-$UNI_AGENT_DIR/examples/claw_envs/agent_config.yaml}
CLAW_FORMAT=${CLAW_FORMAT:-without_skill}
CLAW_INCLUDE_CLI=${CLAW_INCLUDE_CLI:-true}
CLAW_RESTRICT_WORKSPACE=${CLAW_RESTRICT_WORKSPACE:-true}
CLAW_RESTRICT_BASH=${CLAW_RESTRICT_BASH:-true}

TRAIN_FILES=${TRAIN_FILES:-$CLAW_TASKS_DIR}
VAL_FILES=${VAL_FILES:-$TRAIN_FILES}

for required_path in \
    "$VERL_DIR/verl/trainer/main_ppo.py" \
    "$UNI_AGENT_DIR/uni_agent/datasets/claw_native.py" \
    "$CLAW_AGENT_CONFIG" \
    "$CLAW_TOOL_DOCS_DIR" \
    "$TRAIN_FILES" \
    "$VAL_FILES"
do
    if [ ! -e "$required_path" ]; then
        echo "Required path does not exist: $required_path" >&2
        exit 1
    fi
done

# ================= 3. Training hyperparameters =================
MODEL_PATH=${MODEL_PATH:-/opt/huawei/dataset/zyr_yuyin/models/Qwen3-32B}
PROJECT_NAME=${PROJECT_NAME:-claw_envs}
EXPERIMENT_NAME=${EXPERIMENT_NAME:-qwen3_32b_claw_native}
DEFAULT_LOCAL_DIR=${DEFAULT_LOCAL_DIR:-$MODEL_PATH/claw_native_runs}
ROLLOUT_DATA_DIR=${ROLLOUT_DATA_DIR:-$DEFAULT_LOCAL_DIR/rollout_data/$EXPERIMENT_NAME}

ADV_ESTIMATOR=${ADV_ESTIMATOR:-grpo}
USE_KL_IN_REWARD=${USE_KL_IN_REWARD:-False}
KL_COEF=${KL_COEF:-0.0}
USE_KL_LOSS=${USE_KL_LOSS:-False}
KL_LOSS_COEF=${KL_LOSS_COEF:-0.0}
CLIP_RATIO_LOW=${CLIP_RATIO_LOW:-0.2}
CLIP_RATIO_HIGH=${CLIP_RATIO_HIGH:-0.28}

MAX_TURNS=${MAX_TURNS:-50}
MAX_PROMPT_LENGTH=${MAX_PROMPT_LENGTH:-4096}
MAX_RESPONSE_LENGTH=${MAX_RESPONSE_LENGTH:-8192}
ACTOR_LR=${ACTOR_LR:-1e-6}
TRAIN_BATCH_SIZE=${TRAIN_BATCH_SIZE:-128}
PPO_MINI_BATCH_SIZE=${PPO_MINI_BATCH_SIZE:-32}
N_RESP_PER_PROMPT=${N_RESP_PER_PROMPT:-16}
N_RESP_PER_PROMPT_VAL=${N_RESP_PER_PROMPT_VAL:-16}
INFER_TP=${INFER_TP:-4}
TRAIN_SP=${TRAIN_SP:-4}
OFFLOAD=${OFFLOAD:-True}

ACTOR_MAX_TOKEN_LEN_PER_GPU=${ACTOR_MAX_TOKEN_LEN_PER_GPU:-$(( (MAX_PROMPT_LENGTH + MAX_RESPONSE_LENGTH) * 1 ))}
LOG_PROB_MAX_TOKEN_LEN_PER_GPU=${LOG_PROB_MAX_TOKEN_LEN_PER_GPU:-$(( ACTOR_MAX_TOKEN_LEN_PER_GPU * 4 ))}

# ================= 4. Ray / NPU runtime environment =================
export HCCL_CONNECT_TIMEOUT=${HCCL_CONNECT_TIMEOUT:-5400}
export USE_OPTIMIZED_MODEL=${USE_OPTIMIZED_MODEL:-0}
export VLLM_USE_V1=${VLLM_USE_V1:-1}
export HCCL_BUFFSIZE=${HCCL_BUFFSIZE:-300}
export TASK_QUEUE_ENABLE=${TASK_QUEUE_ENABLE:-1}
export COMBINED_ENABLE=${COMBINED_ENABLE:-1}
export PYTORCH_NPU_ALLOC_CONF=${PYTORCH_NPU_ALLOC_CONF:-garbage_collection_threshold:0.85}
export MULTI_STREAM_MEMORY_REUSE=${MULTI_STREAM_MEMORY_REUSE:-1}
export TOKENIZERS_PARALLELISM=${TOKENIZERS_PARALLELISM:-false}
export HYDRA_FULL_ERROR=${HYDRA_FULL_ERROR:-1}
export RAY_DEDUP_LOGS=${RAY_DEDUP_LOGS:-0}
export VLLM_ASCEND_ENABLE_NZ=${VLLM_ASCEND_ENABLE_NZ:-0}
export CLOSE_MATMUL_K_SHIFT=${CLOSE_MATMUL_K_SHIFT:-1}
export ATB_MATMUL_SHUFFLE_K_ENABLE=${ATB_MATMUL_SHUFFLE_K_ENABLE:-0}
export HCCL_DETERMINISTIC=${HCCL_DETERMINISTIC:-true}
export VLLM_ENABLE_V1_MULTIPROCESSING=${VLLM_ENABLE_V1_MULTIPROCESSING:-0}
export HCCL_ASYNC_ERROR_HANDLING=${HCCL_ASYNC_ERROR_HANDLING:-0}

ulimit -n 65536
RAY_TMPDIR=${RAY_TMPDIR:-/cache/ray_tmp}
mkdir -p "$RAY_TMPDIR"
export TMPDIR="$RAY_TMPDIR"

NNODES=${NNODES:-${VC_WORKER_NUM:-1}}
NPUS_PER_NODE=${NPUS_PER_NODE:-${MA_NUM_GPUS:-8}}

if [ -n "${VC_WORKER_HOSTS:-}" ]; then
    MASTER_HOST=$(echo "$VC_WORKER_HOSTS" | cut -d',' -f1)
    MASTER_ADDR=$(getent hosts "$MASTER_HOST" | awk '{print $1; exit}' || true)
    MASTER_ADDR=${MASTER_ADDR:-$MASTER_HOST}
else
    MASTER_ADDR=${MASTER_ADDR:-127.0.0.1}
fi

CURRENT_IP=${MA_CURRENT_IP:-$(hostname -I 2>/dev/null | awk '{print $1}' || true)}
CURRENT_IP=${CURRENT_IP:-127.0.0.1}

SOCKET_IFNAME=${GLOO_SOCKET_IFNAME:-${HCCL_SOCKET_IFNAME:-}}
if [ -n "$SOCKET_IFNAME" ]; then
    export HCCL_SOCKET_IFNAME="$SOCKET_IFNAME"
    export GLOO_SOCKET_IFNAME="$SOCKET_IFNAME"
    export TP_SOCKET_IFNAME="$SOCKET_IFNAME"
fi

echo "Cleaning up old Ray processes..."
ray stop --force || true
sleep 5
rm -rf "$RAY_TMPDIR"/*
pkill -9 -f raylet || true
pkill -9 -f plasma_store || true
pkill -9 -f gcs_server || true

# ================= 5. Training command =================
run_training() {
    cd "$VERL_DIR"

    python3 -m verl.trainer.main_ppo \
        algorithm.adv_estimator="$ADV_ESTIMATOR" \
        algorithm.use_kl_in_reward="$USE_KL_IN_REWARD" \
        algorithm.kl_ctrl.kl_coef="$KL_COEF" \
        algorithm.save_turn_level_entropy=True \
        data.custom_cls.path=pkg://uni_agent.datasets.claw_native \
        data.custom_cls.name=ClawNativeDataset \
        data.train_files="$TRAIN_FILES" \
        data.val_files="$VAL_FILES" \
        data.prompt_key=prompt \
        data.allow_missing_prompt_key=False \
        data.return_raw_chat=True \
        data.need_tools_kwargs=True \
        data.shuffle=True \
        data.train_batch_size="$TRAIN_BATCH_SIZE" \
        data.max_prompt_length="$MAX_PROMPT_LENGTH" \
        data.max_response_length="$MAX_RESPONSE_LENGTH" \
        data.filter_overlong_prompts=False \
        data.truncation=error \
        ++data.claw_repo_root="$UNI_AGENT_DIR" \
        ++data.claw_include_cli="$CLAW_INCLUDE_CLI" \
        ++data.claw_restrict_workspace="$CLAW_RESTRICT_WORKSPACE" \
        ++data.claw_restrict_bash="$CLAW_RESTRICT_BASH" \
        ++data.claw_format="$CLAW_FORMAT" \
        ++data.claw_tool_docs_dir="$CLAW_TOOL_DOCS_DIR" \
        actor_rollout_ref.model.path="$MODEL_PATH" \
        actor_rollout_ref.model.use_remove_padding=True \
        actor_rollout_ref.model.enable_gradient_checkpointing=True \
        actor_rollout_ref.actor.use_kl_loss="$USE_KL_LOSS" \
        actor_rollout_ref.actor.kl_loss_coef="$KL_LOSS_COEF" \
        actor_rollout_ref.actor.clip_ratio_low="$CLIP_RATIO_LOW" \
        actor_rollout_ref.actor.clip_ratio_high="$CLIP_RATIO_HIGH" \
        actor_rollout_ref.actor.clip_ratio_c=10.0 \
        actor_rollout_ref.actor.optim.lr="$ACTOR_LR" \
        actor_rollout_ref.actor.use_dynamic_bsz=True \
        actor_rollout_ref.actor.ppo_mini_batch_size="$PPO_MINI_BATCH_SIZE" \
        actor_rollout_ref.actor.ppo_max_token_len_per_gpu="$ACTOR_MAX_TOKEN_LEN_PER_GPU" \
        actor_rollout_ref.actor.ulysses_sequence_parallel_size="$TRAIN_SP" \
        actor_rollout_ref.actor.fsdp_config.param_offload="$OFFLOAD" \
        actor_rollout_ref.actor.fsdp_config.optimizer_offload="$OFFLOAD" \
        actor_rollout_ref.actor.use_torch_compile=False \
        actor_rollout_ref.ref.use_torch_compile=False \
        actor_rollout_ref.ref.log_prob_max_token_len_per_gpu="$LOG_PROB_MAX_TOKEN_LEN_PER_GPU" \
        actor_rollout_ref.rollout.name=vllm \
        actor_rollout_ref.rollout.mode=async \
        actor_rollout_ref.rollout.tensor_model_parallel_size="$INFER_TP" \
        actor_rollout_ref.rollout.multi_turn.enable=True \
        actor_rollout_ref.rollout.multi_turn.max_user_turns="$MAX_TURNS" \
        actor_rollout_ref.rollout.multi_turn.max_assistant_turns="$MAX_TURNS" \
        actor_rollout_ref.rollout.multi_turn.max_tool_turns_per_step=5 \
        actor_rollout_ref.rollout.agent.default_agent_loop=swe_agent \
        actor_rollout_ref.rollout.agent.agent_loop_config_path="$CLAW_AGENT_CONFIG" \
        actor_rollout_ref.rollout.gpu_memory_utilization=0.8 \
        actor_rollout_ref.rollout.n="$N_RESP_PER_PROMPT" \
        actor_rollout_ref.rollout.calculate_log_probs=True \
        actor_rollout_ref.rollout.val_kwargs.top_p=0.6 \
        actor_rollout_ref.rollout.val_kwargs.temperature=1.0 \
        actor_rollout_ref.rollout.val_kwargs.n="$N_RESP_PER_PROMPT_VAL" \
        +actor_rollout_ref.model.override_config.attention_dropout=0 \
        actor_rollout_ref.actor.entropy_from_logits_with_chunking=True \
        trainer.logger="['console']" \
        trainer.project_name="$PROJECT_NAME" \
        trainer.experiment_name="$EXPERIMENT_NAME" \
        trainer.n_gpus_per_node="$NPUS_PER_NODE" \
        trainer.val_before_train=False \
        trainer.log_val_generations=100 \
        trainer.nnodes="$NNODES" \
        trainer.device=npu \
        trainer.resume_mode=auto \
        actor_rollout_ref.actor.fsdp_config.forward_prefetch=True \
        actor_rollout_ref.ref.fsdp_config.forward_prefetch=True \
        ++actor_rollout_ref.actor.entropy_from_logits_with_chunking=True \
        ++actor_rollout_ref.ref.entropy_from_logits_with_chunking=True \
        trainer.save_freq="${SAVE_FREQ:-100}" \
        trainer.save_local_metrics=True \
        trainer.default_local_dir="$DEFAULT_LOCAL_DIR" \
        trainer.rollout_data_dir="$ROLLOUT_DATA_DIR" \
        trainer.test_freq="${TEST_FREQ:-5}" \
        trainer.total_epochs="${TOTAL_EPOCHS:-1}"
}

# ================= 6. Ray cluster startup =================
if [ "$MASTER_ADDR" = "$CURRENT_IP" ] || [ "$MASTER_ADDR" = "127.0.0.1" ]; then
    echo "Starting Ray HEAD node on $CURRENT_IP..."
    ray start --head --port 6344 --dashboard-host=0.0.0.0 --dashboard-port=8260 --resources='{"NPU": '"$NPUS_PER_NODE"'}'

    while true; do
        ray_status_output=$(ray status || true)
        npu_count=$(echo "$ray_status_output" | grep -oP '(?<=/)\d+\.\d+(?=\s*NPU)' | head -n 1 || true)
        if [ -z "$npu_count" ]; then
            npu_count=0
        fi
        npu_count_int=$(echo "$npu_count" | awk '{print int($1)}')
        ready_nodes=$(( npu_count_int / NPUS_PER_NODE ))

        if [ "$ready_nodes" -ge "$NNODES" ]; then
            echo "Ray cluster is ready with $ready_nodes node(s). Starting claw training..."
            run_training
            break
        fi
        echo "Waiting for Ray to allocate $NNODES node(s). Current: $ready_nodes. Retrying in 5s..."
        sleep 5
    done
else
    RANDOM_DELAY=$((RANDOM % 10 + 1))
    echo "Worker waiting $RANDOM_DELAY seconds before joining Ray head $MASTER_ADDR..."
    sleep "$RANDOM_DELAY"

    while true; do
        ray start --address="$MASTER_ADDR:6344" --resources='{"NPU": '"$NPUS_PER_NODE"'}' --node-ip-address="$CURRENT_IP" || true
        if ray status; then
            echo "Connected to Ray cluster."
            break
        fi
        echo "Failed to connect to Ray cluster. Retrying in 5 seconds..."
        sleep 5
    done

    echo "Worker is ready and waiting for jobs."
    sleep infinity
fi
