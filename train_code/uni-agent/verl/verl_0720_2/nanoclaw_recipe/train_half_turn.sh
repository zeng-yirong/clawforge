#!/bin/bash
# Qwen3.5-27B Nanoclaw 多轮 GRPO 训练脚本 — VERL 0720 unified engine 兼容版
#
# 关键修改：
#   1) 入口改为 python3 -m verl.trainer.main_ppo，不再使用 recipe.grpo_mindspeed_mm.main_ppo；
#   2) 不再使用 MM_CONFIG_FILE / MindSpeed-MM YAML；
#   3) 显式 text-only：data.return_multi_modal_inputs=False；
#   4) 数据输入改为 Nanoclaw base_tasks 目录，不再使用 Retool parquet/json；
#   5) 修正 HCCL 多机默认：端口范围 + HCCL_BUFFSIZE=32，降低 HcclAllreduce socket/资源压力；
#   6) 默认 val n=1、log_val_generations=10，先验证训练稳定性；
#   7) 支持通过 ACTOR_STRATEGY=fsdp2 FSDP_SIZE=16 切到官方新版 NPU FSDP2/FSDP16 形状。

set -x

npu-smi info || true
pip install --upgrade pip
pip uninstall -y moxing-framework || true

# ================= 路径配置 =================
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
WORK_DIR=${WORK_DIR:-$(cd "${SCRIPT_DIR}/.." && pwd)}
INSTALL_DIR=${INSTALL_DIR:-/home/ma-user}
BKGS=${BKGS:-/opt/huawei/dataset/zyr_yuyin/bkgs}
chmod 755 "${INSTALL_DIR}"

# Nanoclaw recipe 已随 WORK_DIR 提供：nanoclaw_recipe。

GCC_INSTALL_PREFIX=${GCC_INSTALL_PREFIX:-/home/ma-user/gcc-11.3.0}
COMPILED_GCC_ARCHIVE_PATH=${COMPILED_GCC_ARCHIVE_PATH:-/opt/huawei/dataset/zyr_yuyin/bkgs/gcc-11.3.0-compiled-aarch64.tar.gz}

echo "--> 正在从缓存恢复 GCC 11.3.0..."
tar -xzf "${COMPILED_GCC_ARCHIVE_PATH}" -C /home/ma-user/
export PATH=${GCC_INSTALL_PREFIX}/bin:${PATH}
export LD_LIBRARY_PATH=${GCC_INSTALL_PREFIX}/lib64:${GCC_INSTALL_PREFIX}/lib:${LD_LIBRARY_PATH:-}
export CC=${GCC_INSTALL_PREFIX}/bin/gcc
export CXX=${GCC_INSTALL_PREFIX}/bin/g++
echo "--> 验证 GCC 版本:"
gcc --version

cd "${BKGS}"
cp jemalloc-5.3.0.tar.bz2 "${INSTALL_DIR}"

VLLM_LATEST_PKGS=${VLLM_LATEST_PKGS:-/opt/huawei/dataset/zyr_yuyin/lyf/verl-05-12/verl_new_26_05_09/pkgs}
rm -rf "${INSTALL_DIR}/vllm" "${INSTALL_DIR}/vllm-ascend"
cp -r "${VLLM_LATEST_PKGS}/vllm" "${INSTALL_DIR}"
cp -r "${VLLM_LATEST_PKGS}/vllm-ascend" "${INSTALL_DIR}"

CANN_BKGS=${CANN_BKGS:-/opt/huawei/dataset/zyr_yuyin/bkgs/cann_0527}
cp "${CANN_BKGS}/Ascend-cann-toolkit_9.0.0_linux-aarch64.run" "${INSTALL_DIR}"
cp "${CANN_BKGS}/Ascend-cann-910b-ops_9.0.0_linux-aarch64.run" "${INSTALL_DIR}"
cp "${CANN_BKGS}/Ascend-cann-nnal_9.0.0_linux-aarch64.run" "${INSTALL_DIR}"

echo "################"
echo "## set verl env"
echo "################"

cd "${INSTALL_DIR}"

chmod +x Ascend-cann-toolkit_9.0.0_linux-aarch64.run
bash Ascend-cann-toolkit_9.0.0_linux-aarch64.run --install --quiet
source "${INSTALL_DIR}/Ascend/ascend-toolkit/set_env.sh"

chmod +x Ascend-cann-910b-ops_9.0.0_linux-aarch64.run
bash Ascend-cann-910b-ops_9.0.0_linux-aarch64.run --install --quiet

chmod +x Ascend-cann-nnal_9.0.0_linux-aarch64.run
bash Ascend-cann-nnal_9.0.0_linux-aarch64.run --install --quiet
source "${INSTALL_DIR}/Ascend/nnal/atb/set_env.sh"

export ASCEND_HOME_PATH=${ASCEND_TOOLKIT_HOME}
export LD_LIBRARY_PATH=/usr/local/Ascend/driver/lib64:/usr/local/Ascend/driver/lib64/common:${LD_LIBRARY_PATH:-}
echo "LD_LIBRARY_PATH=${LD_LIBRARY_PATH}"

pip3 install torch==2.9.0
pip3 install pyyaml setuptools
pip3 install torch-npu==2.9.0
pip3 install torchvision==0.24.0 torchaudio==2.9.0

ASCEND_TOOLKIT_PYTHON_PATH=/home/ma-user/Ascend/ascend-toolkit/latest/python/site-packages
export PYTHONPATH=${PYTHONPATH:-}:${INSTALL_DIR}:${ASCEND_TOOLKIT_PYTHON_PATH}
pip install pybind11==2.13.6

cd "${INSTALL_DIR}/vllm"
VLLM_TARGET_DEVICE=empty pip install .

cd "${INSTALL_DIR}/vllm-ascend"
pip install -e .
export VLLM_LOGGING_LEVEL=INFO

cd "${INSTALL_DIR}"
tar -xvf jemalloc-5.3.0.tar.bz2
cd jemalloc-5.3.0
./configure --prefix="${INSTALL_DIR}"
make -j"$(nproc)"
make install
export LD_PRELOAD=${INSTALL_DIR}/lib/libjemalloc.so.2:${LD_PRELOAD:-}

# # ================= 可选：安装 MindSpeed 栈 =================
# # 纯 VERL engine 路线不依赖 MindSpeed-MM YAML。默认不安装，避免和新版 VERL engine 混淆。
# INSTALL_MINDSPEED_STACK=${INSTALL_MINDSPEED_STACK:-0}
# if [ "${INSTALL_MINDSPEED_STACK}" = "1" ]; then
#     MindSpeed_PATH=${MindSpeed_PATH:-/opt/huawei/dataset/zyr_yuyin/lyf/verl-slow-stable}
#     cd "${MindSpeed_PATH}"
#     cd Megatron-LM && pip install -e . --no-deps && cd ..
#     cd MindSpeed && pip install -e . --no-deps && cd ..
#     cd MindSpeed-MM && mkdir -p logs data ckpt && pip install -e . --no-deps && cd ..
#     pip install beartype bs4 diffusers==0.30.3 ftfy imageio-ffmpeg pandarallel pytest-mock
# else
#     echo "--> Skip MindSpeed/MindSpeed-MM installation for pure VERL engine route."
# fi



# ================= 安装 Triton-Ascend 3.2.1 =================
# 1. 卸载 triton（增加 -y 自动确认）
pip uninstall -y triton

# 2. 卸载 triton-ascend（增加 -y 自动确认）
pip uninstall -y triton-ascend
pip install --no-cache-dir --force-reinstall triton==3.5.0
pip install --no-deps /opt/huawei/dataset/zyr_yuyin/bkgs/triton_ascend-3.2.1-cp311-cp311-manylinux_2_27_aarch64.manylinux_2_28_aarch64.whl


# ================= 安装新版 VERL =================
cd "${WORK_DIR}"
pip install -r requirements-npu.txt
pip install -e .
pip install --upgrade 'urllib3==1.26.11'
pip install loguru
pip install tree_sitter==0.21.3
pip install tree-sitter-java==0.21.0
pip install tree-sitter-javascript==0.21.4

ACL_PATH=/home/ma-user/Ascend/ascend-toolkit/latest/aarch64-linux/lib64
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${ACL_PATH}
echo "LD_LIBRARY_PATH=${LD_LIBRARY_PATH}"

pip uninstall -y transformers || true
pip install transformers==5.3.0
pip install accelerate==1.13.0 mathruler
pip install jsonargparse
pip install deepdiff sympy html2text requests bs4 mpmath swanlab PandoraBox json_repair openai httpx
pip list

# ================= 检查 Nanoclaw recipe =================
if [ ! -f "${WORK_DIR}/nanoclaw_recipe/nanoclaw.py" ]; then
    echo "ERROR: Nanoclaw recipe not found: ${WORK_DIR}/nanoclaw_recipe/nanoclaw.py" >&2
    exit 2
fi
test -f "${WORK_DIR}/nanoclaw_recipe/__init__.py"

# ================= PLOG =================
ma_vj_name=$(echo "${MA_VJ_NAME}" | sed 's:ma-job:modelarts-job:g')
task_name=worker-${VC_TASK_INDEX}
task_plog_path=${MA_LOG_DIR}/${ma_vj_name}/${task_name}
mkdir -p "${task_plog_path}"
export ASCEND_PROCESS_LOG_PATH=${task_plog_path}/${VC_TASK_INDEX}
echo "plog path: ${ASCEND_PROCESS_LOG_PATH}"

MASTER_ADDR=${MA_VJ_NAME}-${MA_TASK_NAME}-${VC_TASK_INDEX}.${MA_VJ_NAME}
MASTER_PORT=${PORT}
MA_CURRENT_INSTANCE_NAME=${MA_CURRENT_INSTANCE_NAME}

cd "${WORK_DIR}"

mkdir -p /cache/ray_tmp

echo "Cleaning up old Ray processes..."
ray stop --force || true
sleep 5
rm -rf /cache/ray_tmp/*
pkill -9 -f raylet || true
pkill -9 -f plasma_store || true
pkill -9 -f gcs_server || true
echo "Waiting 20s for NPU/Ray resources to be released..."
npu-smi info || true
sleep 20

# ================= NPU / HCCL / Ray 环境 =================
export NON_MEGATRON=true
export MULTI_STREAM_MEMORY_REUSE=2
export OMP_NUM_THREADS=1
export PYTORCH_NPU_ALLOC_CONF=${PYTORCH_NPU_ALLOC_CONF:-max_split_size_mb:512}
export VLLM_LOGGING_LEVEL=INFO
export RAY_DEDUP_LOGS=0
export HCCL_EXEC_TIMEOUT=${HCCL_EXEC_TIMEOUT:-3600}
export HCCL_LOG_LEVEL=${HCCL_LOG_LEVEL:-WARN}
export HCCL_CONNECT_TIMEOUT=${HCCL_CONNECT_TIMEOUT:-3600}
export HCCL_EVENT_TIMEOUT=${HCCL_EVENT_TIMEOUT:-7200}
export ACL_DEVICE_SYNC_TIMEOUT=${ACL_DEVICE_SYNC_TIMEOUT:-7200}
export GLOO_SOCKET_TIMEOUT=${GLOO_SOCKET_TIMEOUT:-7200}

# 关键：降低 HCCL buffer，增加 socket 端口范围，缓解 HcclAllreduce ra socket batch connect failed。
export HCCL_BUFFSIZE=${HCCL_BUFFSIZE:-300}
export P2P_HCCL_BUFFSIZE=${P2P_HCCL_BUFFSIZE:-64}
export HCCL_HOST_SOCKET_PORT_RANGE=${HCCL_HOST_SOCKET_PORT_RANGE:-60000-60050}
export HCCL_NPU_SOCKET_PORT_RANGE=${HCCL_NPU_SOCKET_PORT_RANGE:-61000-61050}

export CUDA_DEVICE_MAX_CONNECTIONS=1
export VLLM_ASCEND_ENABLE_NZ=${VLLM_ASCEND_ENABLE_NZ:-0}
export HCCL_OP_EXPANSION_MODE=${HCCL_OP_EXPANSION_MODE:-AIV}
export VLLM_ENGINE_ITERATION_TIMEOUT_S=${VLLM_ENGINE_ITERATION_TIMEOUT_S:-3600}
export WANDB_MODE=${WANDB_MODE:-disabled}
export PYTHONUNBUFFERED=1
export TASK_QUEUE_ENABLE=${TASK_QUEUE_ENABLE:-1}
export COMBINED_ENABLE=${COMBINED_ENABLE:-1}
export TOKENIZERS_PARALLELISM=false
export CLOSE_MATMUL_K_SHIFT=${CLOSE_MATMUL_K_SHIFT:-1}
export ATB_MATMUL_SHUFFLE_K_ENABLE=${ATB_MATMUL_SHUFFLE_K_ENABLE:-0}
export HCCL_DETERMINISTIC=${HCCL_DETERMINISTIC:-true}
export VLLM_ENABLE_V1_MULTIPROCESSING=${VLLM_ENABLE_V1_MULTIPROCESSING:-0}
export VLLM_USE_V1=${VLLM_USE_V1:-1}
export ASCEND_GLOBAL_LOG_LEVEL=${ASCEND_GLOBAL_LOG_LEVEL:-3}
export HYDRA_FULL_ERROR=1
export RAY_gcs_server_rpc_server_thread_num=${RAY_gcs_server_rpc_server_thread_num:-32}
export RAY_gcs_server_request_timeout_seconds=${RAY_gcs_server_request_timeout_seconds:-600}
export RAY_timeout_ms=${RAY_timeout_ms:-600000}
export RAY_worker_register_timeout_seconds=${RAY_worker_register_timeout_seconds:-600}
export RAY_USAGE_STATS_ENABLED=0
export VERL_REUSE_AGENT_LOOP=${VERL_REUSE_AGENT_LOOP:-1}

ulimit -n 65536

# Ray 不要覆盖 ASCEND_RT_VISIBLE_DEVICES；VERL 内部按 local_rank 选卡。
export RAY_EXPERIMENTAL_NOSET_ASCEND_RT_VISIBLE_DEVICES=1

# ================= 路径与数据配置 =================
HDFS_ROOT=${HDFS_ROOT:-$PWD}
DATA_ROOT=${DATA_ROOT:-/opt/huawei/dataset/zyr_yuyin/lyf/verl-nanoclaw-rl/nanoclawRL_temp_ckpt}

# Nanoclaw 数据输入支持两种目录，优先推荐 0625 扁平格式：
#   base_tasks/data_*/env_builder.py
#   base_tasks/data_*/prompts.md
#   base_tasks/data_*/workplace_verifier.py
#   base_tasks/data_*/manifest.json
# 也兼容旧格式：base_tasks/tasks/data_* + base_tasks/scripts|scrips/data_*。
DEFAULT_NANOCLAW_BASE_TASKS=${DEFAULT_NANOCLAW_BASE_TASKS:-/opt/huawei/dataset/zyr_yuyin/lyf/datasets/nanoclawRLdata/0707_6000_one_step_qwen3_7_max_乱序版_去重复id/exported_new_data}
train_base_tasks=${TRAIN_DATA_PATH:-${BASE_TASKS:-${DEFAULT_NANOCLAW_BASE_TASKS}}}
val_base_tasks=${VAL_DATA_PATH:-${VAL_BASE_TASKS:-${train_base_tasks}}}
train_files="['$train_base_tasks']"
test_files="['$val_base_tasks']"

if [ ! -d "${train_base_tasks}" ]; then
    echo "ERROR: Nanoclaw TRAIN_DATA_PATH/BASE_TASKS directory not found: ${train_base_tasks}" >&2
    exit 2
fi
if [ ! -d "${val_base_tasks}" ]; then
    echo "ERROR: Nanoclaw VAL_DATA_PATH/VAL_BASE_TASKS directory not found: ${val_base_tasks}" >&2
    exit 2
fi

model_path=${MODEL_PATH:-/opt/huawei/dataset/zyr_yuyin/models/Qwen/Qwen3___5-27B}

# 纯 VERL engine 路线：不要使用 MindSpeed-MM YAML。
unset MM_CONFIG_FILE || true

# Nanoclaw 工具配置
tool_config_path=${TOOL_CONFIG_PATH:-nanoclaw_recipe/nanoclaw_tool_config.yaml}
nanoclaw_task_glob=${NANOCLAW_TASK_GLOB:-data_*}
nanoclaw_task_ids=${NANOCLAW_TASK_IDS:-}
# 多机训练必须用所有节点都能访问的共享目录；不要用 /tmp，否则 reward worker 可能跨节点找不到 workspace。
nanoclaw_temp_root=${NANOCLAW_TEMP_ROOT:-/opt/huawei/dataset/zyr_yuyin/lyf/verl-nanoclaw-rl/nanoclawRL_temp_workplace_v10_one_step_think_soft_final_answer_half_turn_penalty_qwen37max_test_0708_6000_mask_fix_env_score_dir}
# 默认保留每个 step/data_sample 的目录，方便复盘每条 GRPO 采样；磁盘紧张时手动设 NANOCLAW_CLEANUP_WORKSPACES=True。
nanoclaw_cleanup_workspaces=${NANOCLAW_CLEANUP_WORKSPACES:-False}
nanoclaw_keep_failed_workspaces=${NANOCLAW_KEEP_FAILED_WORKSPACES:-False}
nanoclaw_env_builder_timeout=${NANOCLAW_ENV_BUILDER_TIMEOUT:-120}
nanoclaw_verifier_timeout=${NANOCLAW_VERIFIER_TIMEOUT:-3600}
nanoclaw_reward_score_mode=${NANOCLAW_REWARD_SCORE_MODE:-ratio}
nanoclaw_allow_bash=${NANOCLAW_ALLOW_BASH:-True}
nanoclaw_max_steps=${NANOCLAW_MAX_STEPS:-}
nanoclaw_require_final_answer=${NANOCLAW_REQUIRE_FINAL_ANSWER:-True}
# 可选的稠密奖励：关闭 require_final_answer 时，正常输出非空 final answer 仍可获得额外奖励。
nanoclaw_final_answer_bonus_enable=${NANOCLAW_FINAL_ANSWER_BONUS_ENABLE:-False}
nanoclaw_final_answer_bonus_score=${NANOCLAW_FINAL_ANSWER_BONUS_SCORE:-0.0}
nanoclaw_turn_penalty_only_positive_score=${NANOCLAW_TURN_PENALTY_ONLY_POSITIVE_SCORE:-True}
nanoclaw_assistant_turn_penalty=${NANOCLAW_ASSISTANT_TURN_PENALTY:-0.001}
nanoclaw_duplicate_tool_call_penalty=${NANOCLAW_DUPLICATE_TOOL_CALL_PENALTY:-0.0}
nanoclaw_repeated_response_penalty=${NANOCLAW_REPEATED_RESPONSE_PENALTY:-0.0}
nanoclaw_repeated_response_min_chars=${NANOCLAW_REPEATED_RESPONSE_MIN_CHARS:-35}
nanoclaw_repeated_response_min_consecutive_repeats=${NANOCLAW_REPEATED_RESPONSE_MIN_CONSECUTIVE_REPEATS:-5}
nanoclaw_mask_looping_responses=${NANOCLAW_MASK_LOOPING_RESPONSES:-True}
nanoclaw_mask_only_positive_advantage=${NANOCLAW_MASK_ONLY_POSITIVE_ADVANTAGE:-True}
nanoclaw_mask_budget_exhausted_last_turn=${NANOCLAW_MASK_BUDGET_EXHAUSTED_LAST_TURN:-True}
nanoclaw_mask_duplicate_tool_result_turns=${NANOCLAW_MASK_DUPLICATE_TOOL_RESULT_TURNS:-True}

# verify_workplace.py 如需调用本地 OpenAI-compatible API，可用这些变量传入 reward。
# 默认假设 5 机 40 卡：前 4 个节点加入 Ray 训练，第 5 个节点部署 verifier/vLLM API。
verifier_api_node_rank=${VERIFIER_API_NODE_RANK:-4}
verifier_api_port=${VERIFIER_API_PORT:-8000}
verifier_api_host=${VERIFIER_API_HOST:-${MA_VJ_NAME}-${MA_TASK_NAME}-${verifier_api_node_rank}.${MA_VJ_NAME}}
verifier_api_start_cmd=${VERIFIER_API_START_CMD:-}
verifier_api_bind_host=${VERIFIER_API_BIND_HOST:-0.0.0.0}
verifier_api_tp=${VERIFIER_API_TP:-4}
verifier_api_devices=${VERIFIER_API_DEVICES:-0,1,2,3}
verifier_api_max_model_len=${VERIFIER_API_MAX_MODEL_LEN:-32768}
verifier_api_max_num_batched_tokens=${VERIFIER_API_MAX_NUM_BATCHED_TOKENS:-32768}
verifier_api_max_num_seqs=${VERIFIER_API_MAX_NUM_SEQS:-160}
verifier_api_gpu_memory_utilization=${VERIFIER_API_GPU_MEMORY_UTILIZATION:-0.70}
verifier_api_enforce_eager=${VERIFIER_API_ENFORCE_EAGER:-0}
verifier_api_enable_graph_mode=${VERIFIER_API_ENABLE_GRAPH_MODE:-1}
verifier_api_enable_prefix_caching=${VERIFIER_API_ENABLE_PREFIX_CACHING:-0}
verifier_api_startup_timeout=${VERIFIER_API_STARTUP_TIMEOUT:-1800}
verifier_api_log=${VERIFIER_API_LOG:-logs/vllm-verifier-api.log}
mock_api_base=${MOCK_API_BASE:-http://${verifier_api_host}:${verifier_api_port}/v1}
mock_api_key=${MOCK_API_KEY:-dummy_key}
mock_model_name=${MOCK_MODEL_NAME:-qwen3_5_27b_verifier}
# verify_workplace.py 内部 OpenAI/httpx 单次请求超时；reward API 排队时宁可多等，不要轻易误判 0 分。
mock_api_timeout=${MOCK_API_TIMEOUT:-1800}
mock_api_connect_timeout=${MOCK_API_CONNECT_TIMEOUT:-300}
# 强制 verifier/OpenAI judge 请求关闭 thinking，sitecustomize 会自动注入 extra_body.chat_template_kwargs.enable_thinking=False。
nanoclaw_force_no_thinking=${NANOCLAW_FORCE_NO_THINKING:-1}
nanoclaw_force_max_tokens=${NANOCLAW_FORCE_MAX_TOKENS:-50}
# 默认控制台只打一行 reward 摘要；如需每项 details，设 NANOCLAW_REWARD_PRINT_DETAILS=1。
nanoclaw_reward_print_details=${NANOCLAW_REWARD_PRINT_DETAILS:-0}
# verifier API 是单独节点，默认低并发，避免 RewardLoopWorker 同时打爆 API 导致排队超时。
reward_num_workers=${REWARD_NUM_WORKERS:-52}

project_name=${PROJECT_NAME:-qwen3.5-27b_nanoclaw_grpo_verl_engine_0608_24k}
experiment_name=${EXPERIMENT_NAME:-qwen3.5-27b_nanoclaw_grpo_verl_engine_0608_24k_textonly_one_step_think_soft_final_answer_half_turn_penalty_qwen37max_0708_6000_fix_length}
default_local_dir=${DEFAULT_LOCAL_DIR:-$DATA_ROOT/checkpoint/$experiment_name}
start_time=$(date +%Y%m%d)_$(date +%H%M%S)
mkdir -p logs "${default_local_dir}"

# ================= 算法与并行参数 =================
adv_estimator=grpo
max_turns=${MAX_TURNS:-28}
max_prompt_length=${MAX_PROMPT_LENGTH:-8192}
max_response_length=${MAX_RESPONSE_LENGTH:-32768}
max_assistant_response_length=${MAX_ASSISTANT_RESPONSE_LENGTH:-16384}
max_tool_response_length=${MAX_TOOL_RESPONSE_LENGTH:-8192}
max_model_len=$((max_prompt_length + max_response_length))
actor_lr=${ACTOR_LR:-1e-6}

train_batch_size=${TRAIN_BATCH_SIZE:-64}
ppo_mini_batch_size=${PPO_MINI_BATCH_SIZE:-16}
n_resp_per_prompt=${N_RESP_PER_PROMPT:-8}
# 先压低验证，避免验证和训练稳定性混在一起。
n_resp_per_prompt_val=${N_RESP_PER_PROMPT_VAL:-1}
log_val_generations=${LOG_VAL_GENERATIONS:-10}

infer_tp=${INFER_TP:-4}
train_sp=${TRAIN_SP:-8}
offload=${OFFLOAD:-True}

# 默认沿用旧 new-engine 跑通 4k 前几步的形状；如 HCCL allreduce 仍失败，试 ACTOR_STRATEGY=fsdp2 FSDP_SIZE=16。
actor_strategy=${ACTOR_STRATEGY:-fsdp}
fsdp_size=${FSDP_SIZE:-}

actor_pack=${ACTOR_PACK:-1}
logprob_pack=${LOGPROB_PACK:-2}
actor_max_token_len_per_gpu=${ACTOR_MAX_TOKEN_LEN_PER_GPU:-$(((max_model_len * actor_pack + train_sp - 1) / train_sp))}
log_prob_max_token_len_per_gpu=${LOG_PROB_MAX_TOKEN_LEN_PER_GPU:-$(((max_model_len * logprob_pack + train_sp - 1) / train_sp))}
rollout_max_num_batched_tokens=${ROLLOUT_MAX_NUM_BATCHED_TOKENS:-16384}
rollout_gpu_memory_utilization=${ROLLOUT_GPU_MEMORY_UTILIZATION:-0.40}
update_weights_bucket_mb=${UPDATE_WEIGHTS_BUCKET_MB:-4096}

# Qwen 官方推荐：Instruct/non-thinking reasoning tasks
rollout_temperature=${ROLLOUT_TEMPERATURE:-1.0}
rollout_top_p=${ROLLOUT_TOP_P:-0.95}
rollout_top_k=${ROLLOUT_TOP_K:-20}
rollout_min_p=${ROLLOUT_MIN_P:-0.0}
rollout_presence_penalty=${ROLLOUT_PRESENCE_PENALTY:-1.5}
rollout_frequency_penalty=${ROLLOUT_FREQUENCY_PENALTY:-0.3}
rollout_repetition_penalty=${ROLLOUT_REPETITION_PENALTY:-1.0}

echo "DEBUG: max_response_length=${max_response_length}, max_assistant_response_length=${max_assistant_response_length}, max_model_len=${max_model_len}"
echo "DEBUG: max_turns=${max_turns}"
echo "DEBUG: max_tool_response_length=${max_tool_response_length}"
echo "DEBUG: train_batch_size=${train_batch_size}, ppo_mini_batch_size=${ppo_mini_batch_size}, n=${n_resp_per_prompt}"
echo "DEBUG: train_sp=${train_sp}, infer_tp=${infer_tp}, actor_strategy=${actor_strategy}, fsdp_size=${fsdp_size:-<default>}"
echo "DEBUG: actor_max_token_len_per_gpu=${actor_max_token_len_per_gpu}, log_prob_max_token_len_per_gpu=${log_prob_max_token_len_per_gpu}"
echo "DEBUG: rollout sampling temperature=${rollout_temperature}, top_p=${rollout_top_p}, top_k=${rollout_top_k}, min_p=${rollout_min_p}, presence_penalty=${rollout_presence_penalty}, frequency_penalty=${rollout_frequency_penalty}, repetition_penalty=${rollout_repetition_penalty}"
echo "DEBUG: HCCL_BUFFSIZE=${HCCL_BUFFSIZE}, HCCL_HOST_SOCKET_PORT_RANGE=${HCCL_HOST_SOCKET_PORT_RANGE}, HCCL_NPU_SOCKET_PORT_RANGE=${HCCL_NPU_SOCKET_PORT_RANGE}"

val_before_train=${VAL_BEFORE_TRAIN:-False}
trainer_use_v1=${TRAINER_USE_V1:-True}
test_freq=${TEST_FREQ:-5000}
save_freq=${SAVE_FREQ:-35}

# ================= 分布式 =================
export TOTAL_NNODES=${TOTAL_NNODES:-5}
export TRAIN_NNODES=${TRAIN_NNODES:-4}
export NNODES=${NNODES:-${TRAIN_NNODES}}
export NODE_RANK=${VC_TASK_INDEX}
export NPUS_PER_NODE=${NPUS_PER_NODE:-8}
export WORLD_SIZE=$((NPUS_PER_NODE * NNODES))

export MASTER_ADDR=${MA_VJ_NAME}-${MA_TASK_NAME}-0.${MA_VJ_NAME}
export MASTER_PORT=${MASTER_PORT:-6167}
export DASHBOARD_PORT=${DASHBOARD_PORT:-8191}
export RAY_PORT=${RAY_PORT:-6167}

readonly SOCKET_IFNAME=${SOCKET_IFNAME:-eth0}
export HCCL_SOCKET_IFNAME=${HCCL_SOCKET_IFNAME:-${SOCKET_IFNAME}}
export GLOO_SOCKET_IFNAME=${GLOO_SOCKET_IFNAME:-${SOCKET_IFNAME}}
export CURRENT_IP=$(ifconfig ${SOCKET_IFNAME} | grep -Eo 'inet (addr:)?([0-9]{1,3}\.){3}[0-9]{1,3}' | awk '{print $NF}')
export RAY_NODE_IP=${MA_CURRENT_IP:-${CURRENT_IP}}

export ASCEND_RT_VISIBLE_DEVICES=${ASCEND_RT_VISIBLE_DEVICES:-$(seq -s, 0 $((NPUS_PER_NODE - 1)))}

cat <<EOF
DEBUG: MASTER_ADDR=${MASTER_ADDR}
DEBUG: MASTER_PORT=${MASTER_PORT}
DEBUG: RAY_PORT=${RAY_PORT}
DEBUG: MA_CURRENT_IP=${MA_CURRENT_IP}
DEBUG: CURRENT_IP=${CURRENT_IP}
DEBUG: RAY_NODE_IP=${RAY_NODE_IP}
DEBUG: ASCEND_RT_VISIBLE_DEVICES=${ASCEND_RT_VISIBLE_DEVICES}
DEBUG: HCCL_SOCKET_IFNAME=${HCCL_SOCKET_IFNAME}
DEBUG: GLOO_SOCKET_IFNAME=${GLOO_SOCKET_IFNAME}
DEBUG: TOTAL_NNODES=${TOTAL_NNODES}
DEBUG: TRAIN_NNODES=${TRAIN_NNODES}
DEBUG: VERIFIER_API_NODE_RANK=${verifier_api_node_rank}
DEBUG: MOCK_API_BASE=${mock_api_base}
DEBUG: MOCK_MODEL_NAME=${mock_model_name}
DEBUG: MOCK_API_TIMEOUT=${mock_api_timeout}
DEBUG: NANOCLAW_FORCE_NO_THINKING=${nanoclaw_force_no_thinking}
DEBUG: NANOCLAW_FORCE_MAX_TOKENS=${nanoclaw_force_max_tokens}
DEBUG: NANOCLAW_REWARD_PRINT_DETAILS=${nanoclaw_reward_print_details}
DEBUG: NANOCLAW_REQUIRE_FINAL_ANSWER=${nanoclaw_require_final_answer}
DEBUG: NANOCLAW_FINAL_ANSWER_BONUS_ENABLE=${nanoclaw_final_answer_bonus_enable}
DEBUG: NANOCLAW_FINAL_ANSWER_BONUS_SCORE=${nanoclaw_final_answer_bonus_score}
DEBUG: NANOCLAW_TURN_PENALTY_ONLY_POSITIVE_SCORE=${nanoclaw_turn_penalty_only_positive_score}
DEBUG: NANOCLAW_ASSISTANT_TURN_PENALTY=${nanoclaw_assistant_turn_penalty}
DEBUG: NANOCLAW_DUPLICATE_TOOL_CALL_PENALTY=${nanoclaw_duplicate_tool_call_penalty}
DEBUG: NANOCLAW_REPEATED_RESPONSE_PENALTY=${nanoclaw_repeated_response_penalty}
DEBUG: NANOCLAW_REPEATED_RESPONSE_MIN_CHARS=${nanoclaw_repeated_response_min_chars}
DEBUG: NANOCLAW_REPEATED_RESPONSE_MIN_CONSECUTIVE_REPEATS=${nanoclaw_repeated_response_min_consecutive_repeats}
DEBUG: NANOCLAW_MASK_LOOPING_RESPONSES=${nanoclaw_mask_looping_responses}
DEBUG: NANOCLAW_MASK_ONLY_POSITIVE_ADVANTAGE=${nanoclaw_mask_only_positive_advantage}
DEBUG: NANOCLAW_MASK_BUDGET_EXHAUSTED_LAST_TURN=${nanoclaw_mask_budget_exhausted_last_turn}
DEBUG: NANOCLAW_MASK_DUPLICATE_TOOL_RESULT_TURNS=${nanoclaw_mask_duplicate_tool_result_turns}
DEBUG: NANOCLAW_LOOPING_RESPONSE_MIN_CHARS=${nanoclaw_looping_response_min_chars}
DEBUG: NANOCLAW_LOOPING_RESPONSE_MIN_CONSECUTIVE_REPEATS=${nanoclaw_looping_response_min_consecutive_repeats}
DEBUG: VERIFIER_API_TP=${verifier_api_tp}
DEBUG: VERIFIER_API_DEVICES=${verifier_api_devices}
DEBUG: VERIFIER_API_MAX_NUM_SEQS=${verifier_api_max_num_seqs}
DEBUG: VERIFIER_API_ENFORCE_EAGER=${verifier_api_enforce_eager}
DEBUG: VERIFIER_API_ENABLE_GRAPH_MODE=${verifier_api_enable_graph_mode}
DEBUG: REWARD_NUM_WORKERS=${reward_num_workers}
EOF

if [ "${NODE_RANK}" = "${verifier_api_node_rank}" ]; then
    echo "--> [Verifier API Node] This node is reserved for vLLM/OpenAI-compatible verifier API."
    echo "--> [Verifier API Node] API base: ${mock_api_base}"
    export VLLM_ENABLE_GRAPH_MODE=${verifier_api_enable_graph_mode}
    mkdir -p "$(dirname "${verifier_api_log}")"
    if [ -n "${verifier_api_start_cmd}" ]; then
        echo "--> [Verifier API Node] Running VERIFIER_API_START_CMD..."
        bash -lc "${verifier_api_start_cmd}" &
        verifier_api_pid=$!
    else
        echo "--> [Verifier API Node] Starting default vLLM verifier API..."
        export ASCEND_RT_VISIBLE_DEVICES=${verifier_api_devices}
        verifier_api_args=(
            --model "${model_path}"
            --tokenizer "${model_path}"
            --host "${verifier_api_bind_host}"
            --port "${verifier_api_port}"
            --served-model-name "${mock_model_name}"
            --tensor-parallel-size "${verifier_api_tp}"
            --dtype bfloat16
            --max-model-len "${verifier_api_max_model_len}"
            --max-num-batched-tokens "${verifier_api_max_num_batched_tokens}"
            --max-num-seqs "${verifier_api_max_num_seqs}"
            --gpu-memory-utilization "${verifier_api_gpu_memory_utilization}"
            --trust-remote-code
        )
        if [ "${verifier_api_enforce_eager}" = "1" ] || [ "${verifier_api_enforce_eager}" = "true" ] || [ "${verifier_api_enforce_eager}" = "True" ]; then
            verifier_api_args+=(--enforce-eager)
        fi
        if [ "${verifier_api_enable_prefix_caching}" = "1" ] || [ "${verifier_api_enable_prefix_caching}" = "true" ] || [ "${verifier_api_enable_prefix_caching}" = "True" ]; then
            verifier_api_args+=(--enable-prefix-caching)
        fi
        echo "--> [Verifier API Node] Command: python3 -m vllm.entrypoints.openai.api_server ${verifier_api_args[*]}"
        python3 -m vllm.entrypoints.openai.api_server "${verifier_api_args[@]}" >"${verifier_api_log}" 2>&1 &
        verifier_api_pid=$!
    fi

    echo "--> [Verifier API Node] vLLM API pid=${verifier_api_pid}, log=${verifier_api_log}"
    echo "--> [Verifier API Node] Waiting for ${mock_api_base}/models ..."
    python3 - "${mock_api_base}/models" "${verifier_api_startup_timeout}" "${verifier_api_log}" "${verifier_api_pid}" <<'PY'
import os
import sys
import time
import urllib.request
from pathlib import Path

url = sys.argv[1]
timeout = float(sys.argv[2])
log_path = Path(sys.argv[3])
pid = int(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[4] else None
started = time.time()
last_error = None
while time.time() - started < timeout:
    if pid is not None:
        try:
            os.kill(pid, 0)
        except OSError:
            print(f"ERROR: verifier API process exited early: pid={pid}", file=sys.stderr)
            if log_path.is_file():
                print("\n".join(log_path.read_text(encoding="utf-8", errors="replace").splitlines()[-120:]), file=sys.stderr)
            sys.exit(1)
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            if 200 <= response.status < 300:
                print(f"READY: {url}", file=sys.stderr)
                sys.exit(0)
    except Exception as exc:
        last_error = exc
    time.sleep(5)
print(f"ERROR: timed out waiting for {url}; last_error={last_error}", file=sys.stderr)
if log_path.is_file():
    print("\n".join(log_path.read_text(encoding="utf-8", errors="replace").splitlines()[-120:]), file=sys.stderr)
sys.exit(1)
PY
    echo "--> [Verifier API Node] Ready. Keeping node alive."
    wait "${verifier_api_pid}"
fi

export TMPDIR=/cache/ray_tmp
export HCCL_ASYNC_ERROR_HANDLING=${HCCL_ASYNC_ERROR_HANDLING:-0}

wait_for_ray_npu_resources() {
    expected_npu=$1
    timeout_seconds=${2:-900}
    begin_ts=$(date +%s)

    while true; do
        total_npu=$(python3 - <<'PY' 2>/dev/null
import ray

try:
    ray.init(address="auto", ignore_reinit_error=True, logging_level="ERROR")
    print(int(ray.cluster_resources().get("NPU", 0)))
    ray.shutdown()
except Exception:
    print(0)
PY
)
        total_npu=${total_npu:-0}
        now_ts=$(date +%s)
        elapsed=$((now_ts - begin_ts))

        echo "Ray NPU resources: ${total_npu}/${expected_npu}, elapsed=${elapsed}s"
        ray status || true

        if [ "${total_npu}" -ge "${expected_npu}" ]; then
            echo "Ray cluster is ready: ${total_npu}/${expected_npu} NPU resources registered."
            break
        fi

        if [ "${elapsed}" -ge "${timeout_seconds}" ]; then
            echo "ERROR: Timed out waiting for Ray NPU resources: ${total_npu}/${expected_npu}" >&2
            return 1
        fi

        sleep 5
    done
}

wait_for_verifier_api() {
    api_url="${mock_api_base}/models"
    timeout_seconds=${VERIFIER_API_CLIENT_WAIT_TIMEOUT:-1800}
    begin_ts=$(date +%s)
    last_diag_ts=0
    while true; do
        verifier_check_output=$(python3 - "${api_url}" <<'PY' 2>&1
import socket
import sys
import urllib.parse
import urllib.request

url = sys.argv[1]
parsed = urllib.parse.urlparse(url)
host = parsed.hostname
port = parsed.port or (443 if parsed.scheme == "https" else 80)
print(f"check url={url} host={host} port={port}")
try:
    infos = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    print("dns=" + ",".join(sorted({item[4][0] for item in infos})))
except Exception as exc:
    print(f"dns_error={type(exc).__name__}: {exc}")
    raise SystemExit(1)
try:
    with socket.create_connection((host, port), timeout=5):
        print("tcp=ok")
except Exception as exc:
    print(f"tcp_error={type(exc).__name__}: {exc}")
    raise SystemExit(1)
try:
    with urllib.request.urlopen(url, timeout=10) as response:
        print(f"http_status={response.status}")
        raise SystemExit(0 if 200 <= response.status < 300 else 1)
except Exception as exc:
    print(f"http_error={type(exc).__name__}: {exc}")
    raise SystemExit(1)
PY
)
        check_rc=$?
        if [ "${check_rc}" = "0" ]; then
            echo "Verifier API is ready: ${api_url}"
            echo "${verifier_check_output}"
            break
        fi
        now_ts=$(date +%s)
        elapsed=$((now_ts - begin_ts))
        echo "Waiting for verifier API: ${api_url}, elapsed=${elapsed}s"
        if [ $((now_ts - last_diag_ts)) -ge 60 ]; then
            last_diag_ts=${now_ts}
            echo "--- verifier API check diagnostics ---"
            echo "${verifier_check_output}"
            echo "--- expected verifier node: rank=${verifier_api_node_rank}, host=${verifier_api_host}, port=${verifier_api_port} ---"
            echo "--- check verifier node log: ${verifier_api_log} ---"
            echo "--------------------------------------"
        fi
        if [ "${elapsed}" -ge "${timeout_seconds}" ]; then
            echo "ERROR: Timed out waiting for verifier API: ${api_url}" >&2
            echo "Last verifier API diagnostics:" >&2
            echo "${verifier_check_output}" >&2
            return 1
        fi
        sleep 10
    done
}

# ================= Nanoclaw workspace 根目录 =================
mkdir -p "${nanoclaw_temp_root}"
if ! touch "${nanoclaw_temp_root}/.nanoclaw_write_test_${NODE_RANK}" 2>/dev/null; then
    echo "ERROR: Cannot write NANOCLAW_TEMP_ROOT: ${nanoclaw_temp_root}" >&2
    exit 2
fi
rm -f "${nanoclaw_temp_root}/.nanoclaw_write_test_${NODE_RANK}" || true
if [[ "${nanoclaw_temp_root}" == /tmp/* ]]; then
    echo "WARNING: NANOCLAW_TEMP_ROOT is under /tmp. Multi-node reward workers may not see rollout workspaces." >&2
    echo "WARNING: Prefer a shared path, e.g. ${DATA_ROOT}/nanoclaw_workspaces" >&2
fi
echo "DEBUG: Nanoclaw train_base_tasks=${train_base_tasks}"
echo "DEBUG: Nanoclaw val_base_tasks=${val_base_tasks}"
echo "DEBUG: Nanoclaw task_glob=${nanoclaw_task_glob}, task_ids=${nanoclaw_task_ids:-<all>}"
echo "DEBUG: Nanoclaw temp_root=${nanoclaw_temp_root}, cleanup=${nanoclaw_cleanup_workspaces}, keep_failed=${nanoclaw_keep_failed_workspaces}"

# ================= 生成 Ray runtime env =================
RUNTIME_ENV_FILE=${WORK_DIR}/verl_engine_runtime_env.generated.yaml
cat > "${RUNTIME_ENV_FILE}" <<YAML
working_dir: ./
excludes: ["/.git/", "/logs/", "/checkpoint/"]
env_vars:
  TORCH_NCCL_AVOID_RECORD_STREAMS: "1"
  CUDA_DEVICE_MAX_CONNECTIONS: "1"
  HCCL_HOST_SOCKET_PORT_RANGE: "${HCCL_HOST_SOCKET_PORT_RANGE}"
  HCCL_NPU_SOCKET_PORT_RANGE: "${HCCL_NPU_SOCKET_PORT_RANGE}"
  HCCL_CONNECT_TIMEOUT: "${HCCL_CONNECT_TIMEOUT}"
  HCCL_EXEC_TIMEOUT: "${HCCL_EXEC_TIMEOUT}"
  HCCL_EVENT_TIMEOUT: "${HCCL_EVENT_TIMEOUT}"
  HCCL_LOG_LEVEL: "${HCCL_LOG_LEVEL}"
  HCCL_BUFFSIZE: "${HCCL_BUFFSIZE}"
  P2P_HCCL_BUFFSIZE: "${P2P_HCCL_BUFFSIZE}"
  VLLM_USE_V1: "${VLLM_USE_V1}"
  VLLM_ENABLE_GRAPH_MODE: "${verifier_api_enable_graph_mode}"
  VLLM_ASCEND_ENABLE_NZ: "${VLLM_ASCEND_ENABLE_NZ}"
  VLLM_ENABLE_V1_MULTIPROCESSING: "${VLLM_ENABLE_V1_MULTIPROCESSING}"
  VLLM_ENGINE_ITERATION_TIMEOUT_S: "${VLLM_ENGINE_ITERATION_TIMEOUT_S}"
  RAY_EXPERIMENTAL_NOSET_ASCEND_RT_VISIBLE_DEVICES: "${RAY_EXPERIMENTAL_NOSET_ASCEND_RT_VISIBLE_DEVICES}"
  TOKENIZERS_PARALLELISM: "false"
  HYDRA_FULL_ERROR: "1"
  PYTHONUNBUFFERED: "1"
  RAY_DEDUP_LOGS: "0"
  WANDB_MODE: "${WANDB_MODE}"
  MOCK_API_BASE: "${mock_api_base}"
  MOCK_API_KEY: "${mock_api_key}"
  MOCK_MODEL_NAME: "${mock_model_name}"
  MOCK_API_TIMEOUT: "${mock_api_timeout}"
  MOCK_API_CONNECT_TIMEOUT: "${mock_api_connect_timeout}"
  NANOCLAW_FORCE_NO_THINKING: "${nanoclaw_force_no_thinking}"
  NANOCLAW_FORCE_MAX_TOKENS: "${nanoclaw_force_max_tokens}"
  NANOCLAW_REWARD_PRINT_DETAILS: "${nanoclaw_reward_print_details}"
  NANOCLAW_REQUIRE_FINAL_ANSWER: "${nanoclaw_require_final_answer}"
  NANOCLAW_FINAL_ANSWER_BONUS_ENABLE: "${nanoclaw_final_answer_bonus_enable}"
  NANOCLAW_FINAL_ANSWER_BONUS_SCORE: "${nanoclaw_final_answer_bonus_score}"
  NANOCLAW_TURN_PENALTY_ONLY_POSITIVE_SCORE: "${nanoclaw_turn_penalty_only_positive_score}"
  NANOCLAW_ASSISTANT_TURN_PENALTY: "${nanoclaw_assistant_turn_penalty}"
  NANOCLAW_DUPLICATE_TOOL_CALL_PENALTY: "${nanoclaw_duplicate_tool_call_penalty}"
  NANOCLAW_REPEATED_RESPONSE_PENALTY: "${nanoclaw_repeated_response_penalty}"
  NANOCLAW_REPEATED_RESPONSE_MIN_CHARS: "${nanoclaw_repeated_response_min_chars}"
  NANOCLAW_REPEATED_RESPONSE_MIN_CONSECUTIVE_REPEATS: "${nanoclaw_repeated_response_min_consecutive_repeats}"
  NANOCLAW_MASK_LOOPING_RESPONSES: "${nanoclaw_mask_looping_responses}"
  NANOCLAW_MASK_ONLY_POSITIVE_ADVANTAGE: "${nanoclaw_mask_only_positive_advantage}"
  NANOCLAW_MASK_BUDGET_EXHAUSTED_LAST_TURN: "${nanoclaw_mask_budget_exhausted_last_turn}"
  NANOCLAW_MASK_DUPLICATE_TOOL_RESULT_TURNS: "${nanoclaw_mask_duplicate_tool_result_turns}"
  NANOCLAW_LOOPING_RESPONSE_MIN_CHARS: "${nanoclaw_looping_response_min_chars}"
  NANOCLAW_LOOPING_RESPONSE_MIN_CONSECUTIVE_REPEATS: "${nanoclaw_looping_response_min_consecutive_repeats}"
YAML

# ================= 启动 Ray 多机集群 =================
if [ "${NODE_RANK}" = "0" ]; then
    echo "--> [Head Node] Starting Ray Head on ${CURRENT_IP}..."
    ray start --head \
        --node-ip-address=${RAY_NODE_IP} \
        --port=${RAY_PORT} \
        --dashboard-host=0.0.0.0 \
        --dashboard-port=${DASHBOARD_PORT} \
        --resources="{\"NPU\":${NPUS_PER_NODE}}" \
        --disable-usage-stats \
        --block &

    sleep 10
    wait_for_ray_npu_resources ${WORLD_SIZE} 900 || exit 1
    wait_for_verifier_api || exit 1
else
    echo "--> [Worker Node] Starting Ray Worker, connecting to ${MASTER_ADDR}:${RAY_PORT}..."
    sleep 20
    ray start --address=${MASTER_ADDR}:${RAY_PORT} \
        --node-ip-address=${RAY_NODE_IP} \
        --resources="{\"NPU\":${NPUS_PER_NODE}}" \
        --disable-usage-stats \
        --block &
    sleep 10
fi

# ================= 训练参数数组 =================
training_args=(
    python3 -m verl.trainer.main_ppo
    +ray_kwargs.ray_init.address=auto
    reward.num_workers=${reward_num_workers}
    algorithm.adv_estimator=${adv_estimator}
    algorithm.use_kl_in_reward=False
    algorithm.kl_ctrl.kl_coef=0.0
    data.train_files="${train_files}"
    data.val_files="${test_files}"
    data.return_raw_chat=True
    data.return_multi_modal_inputs=False
    data.image_key=images
    data.shuffle=False
    data.train_batch_size=${train_batch_size}
    data.max_prompt_length=${max_prompt_length}
    data.max_response_length=${max_response_length}
    data.filter_overlong_prompts=True
    data.truncation=error
    data.custom_cls.path=pkg://nanoclaw_recipe.nanoclaw
    data.custom_cls.name=CustomRLHFDataset
    "data.tool_config_path=${tool_config_path}"
    "+data.nanoclaw_task_glob=${nanoclaw_task_glob}"
    "+data.nanoclaw_temp_root=${nanoclaw_temp_root}"
    "+data.nanoclaw_cleanup_workspaces=${nanoclaw_cleanup_workspaces}"
    "+data.nanoclaw_keep_failed_workspaces=${nanoclaw_keep_failed_workspaces}"
    "+data.nanoclaw_env_builder_timeout=${nanoclaw_env_builder_timeout}"
    "+data.nanoclaw_verifier_timeout=${nanoclaw_verifier_timeout}"
    "+data.nanoclaw_reward_score_mode=${nanoclaw_reward_score_mode}"
    "+data.nanoclaw_allow_bash=${nanoclaw_allow_bash}"
    +data.apply_chat_template_kwargs.enable_thinking=True
    reward.custom_reward_function.path=pkg://nanoclaw_recipe.nanoclaw
    reward.custom_reward_function.name=compute_score
    "+reward.custom_reward_function.reward_kwargs.cleanup_workspaces=${nanoclaw_cleanup_workspaces}"
    "+reward.custom_reward_function.reward_kwargs.keep_failed_workspaces=${nanoclaw_keep_failed_workspaces}"
    "+reward.custom_reward_function.reward_kwargs.verifier_timeout=${nanoclaw_verifier_timeout}"
    "+reward.custom_reward_function.reward_kwargs.reward_score_mode=${nanoclaw_reward_score_mode}"
    "+reward.custom_reward_function.reward_kwargs.require_final_answer=${nanoclaw_require_final_answer}"
    "+reward.custom_reward_function.reward_kwargs.final_answer_bonus_enable=${nanoclaw_final_answer_bonus_enable}"
    "+reward.custom_reward_function.reward_kwargs.final_answer_bonus_score=${nanoclaw_final_answer_bonus_score}"
    "+reward.custom_reward_function.reward_kwargs.turn_penalty_only_positive_score=${nanoclaw_turn_penalty_only_positive_score}"
    "+reward.custom_reward_function.reward_kwargs.assistant_turn_penalty=${nanoclaw_assistant_turn_penalty}"
    "+reward.custom_reward_function.reward_kwargs.duplicate_tool_call_penalty=${nanoclaw_duplicate_tool_call_penalty}"
    "+reward.custom_reward_function.reward_kwargs.repeated_response_penalty=${nanoclaw_repeated_response_penalty}"
    "+reward.custom_reward_function.reward_kwargs.repeated_response_min_chars=${nanoclaw_repeated_response_min_chars}"
    "+reward.custom_reward_function.reward_kwargs.repeated_response_min_consecutive_repeats=${nanoclaw_repeated_response_min_consecutive_repeats}"
    "+reward.custom_reward_function.reward_kwargs.mock_api_base=${mock_api_base}"
    "+reward.custom_reward_function.reward_kwargs.mock_api_key=${mock_api_key}"
    "+reward.custom_reward_function.reward_kwargs.mock_model_name=${mock_model_name}"
    "+reward.custom_reward_function.reward_kwargs.mock_api_timeout=${mock_api_timeout}"
    "+reward.custom_reward_function.reward_kwargs.mock_api_connect_timeout=${mock_api_connect_timeout}"
    actor_rollout_ref.model.path=${model_path}
    actor_rollout_ref.model.use_remove_padding=True
    actor_rollout_ref.model.enable_gradient_checkpointing=True
    actor_rollout_ref.actor.strategy=${actor_strategy}
    actor_rollout_ref.ref.strategy=${actor_strategy}
    actor_rollout_ref.actor.use_kl_loss=True
    actor_rollout_ref.actor.kl_loss_coef=0.0005
    actor_rollout_ref.actor.clip_ratio_low=0.2
    actor_rollout_ref.actor.clip_ratio_high=0.28
    actor_rollout_ref.actor.clip_ratio_c=10.0
    actor_rollout_ref.actor.optim.lr=${actor_lr}
    actor_rollout_ref.actor.use_dynamic_bsz=True
    actor_rollout_ref.actor.ppo_mini_batch_size=${ppo_mini_batch_size}
    actor_rollout_ref.actor.ppo_max_token_len_per_gpu=${actor_max_token_len_per_gpu}
    actor_rollout_ref.actor.ulysses_sequence_parallel_size=${train_sp}
    actor_rollout_ref.actor.fsdp_config.param_offload=${offload}
    actor_rollout_ref.actor.fsdp_config.optimizer_offload=${offload}
    actor_rollout_ref.ref.fsdp_config.param_offload=${offload}
    actor_rollout_ref.ref.log_prob_use_dynamic_bsz=True
    actor_rollout_ref.ref.log_prob_max_token_len_per_gpu=${log_prob_max_token_len_per_gpu}
    actor_rollout_ref.ref.ulysses_sequence_parallel_size=${train_sp}
    actor_rollout_ref.rollout.name=vllm
    actor_rollout_ref.rollout.mode=async
    actor_rollout_ref.rollout.temperature=${rollout_temperature}
    actor_rollout_ref.rollout.top_p=${rollout_top_p}
    actor_rollout_ref.rollout.top_k=${rollout_top_k}
    actor_rollout_ref.rollout.min_p=${rollout_min_p}
    actor_rollout_ref.rollout.presence_penalty=${rollout_presence_penalty}
    actor_rollout_ref.rollout.frequency_penalty=${rollout_frequency_penalty}
    actor_rollout_ref.rollout.repetition_penalty=${rollout_repetition_penalty}
    actor_rollout_ref.rollout.tensor_model_parallel_size=${infer_tp}
    actor_rollout_ref.rollout.checkpoint_engine.update_weights_bucket_megabytes=${update_weights_bucket_mb}
    actor_rollout_ref.rollout.log_prob_use_dynamic_bsz=True
    actor_rollout_ref.rollout.log_prob_max_token_len_per_gpu=${log_prob_max_token_len_per_gpu}
    actor_rollout_ref.rollout.enable_chunked_prefill=True
    actor_rollout_ref.rollout.max_num_batched_tokens=${rollout_max_num_batched_tokens}
    actor_rollout_ref.rollout.free_cache_engine=True
    actor_rollout_ref.rollout.enforce_eager=False
    actor_rollout_ref.rollout.enable_prefix_caching=False
    actor_rollout_ref.rollout.multi_turn.enable=True
    actor_rollout_ref.rollout.multi_turn.max_user_turns=${max_turns}
    actor_rollout_ref.rollout.multi_turn.max_assistant_turns=${max_turns}
    actor_rollout_ref.rollout.multi_turn.max_assistant_response_length=${max_assistant_response_length}
    "actor_rollout_ref.rollout.multi_turn.tool_config_path=${tool_config_path}"
    actor_rollout_ref.rollout.multi_turn.format=qwen3_coder
    "actor_rollout_ref.rollout.multi_turn.max_tool_response_length=${max_tool_response_length}"
    actor_rollout_ref.rollout.gpu_memory_utilization=${rollout_gpu_memory_utilization}
    actor_rollout_ref.rollout.n=${n_resp_per_prompt}
    actor_rollout_ref.rollout.val_kwargs.temperature=${rollout_temperature}
    actor_rollout_ref.rollout.val_kwargs.top_p=${rollout_top_p}
    actor_rollout_ref.rollout.val_kwargs.top_k=${rollout_top_k}
    actor_rollout_ref.rollout.val_kwargs.min_p=${rollout_min_p}
    actor_rollout_ref.rollout.val_kwargs.presence_penalty=${rollout_presence_penalty}
    actor_rollout_ref.rollout.val_kwargs.frequency_penalty=${rollout_frequency_penalty}
    actor_rollout_ref.rollout.val_kwargs.repetition_penalty=${rollout_repetition_penalty}
    actor_rollout_ref.rollout.val_kwargs.do_sample=True
    actor_rollout_ref.rollout.val_kwargs.n=${n_resp_per_prompt_val}
    actor_rollout_ref.actor.use_torch_compile=False
    actor_rollout_ref.ref.use_torch_compile=False
    actor_rollout_ref.actor.use_torch_compile=False
    actor_rollout_ref.ref.use_torch_compile=False
    actor_rollout_ref.actor.fsdp_config.use_torch_compile=False
    actor_rollout_ref.ref.fsdp_config.use_torch_compile=False
    critic.fsdp.use_torch_compile=False
    trainer.use_v1=${trainer_use_v1}
    trainer.critic_warmup=0
    trainer.balance_batch=True
    trainer.logger=['console','tensorboard']
    trainer.project_name=${project_name}
    trainer.experiment_name=${experiment_name}
    trainer.nnodes=${NNODES}
    trainer.n_gpus_per_node=${NPUS_PER_NODE}
    trainer.val_before_train=${val_before_train}
    trainer.log_val_generations=${log_val_generations}
    trainer.save_freq=${save_freq}
    trainer.default_local_dir=${default_local_dir}
    trainer.test_freq=${test_freq}
    trainer.total_epochs=10
)

if [ -n "${fsdp_size}" ]; then
    training_args+=(
        actor_rollout_ref.actor.fsdp_config.fsdp_size=${fsdp_size}
        actor_rollout_ref.ref.fsdp_config.fsdp_size=${fsdp_size}
    )
fi

if [ -n "${nanoclaw_task_ids}" ]; then
    training_args+=("+data.nanoclaw_task_ids=${nanoclaw_task_ids}")
fi

if [ -n "${nanoclaw_max_steps}" ]; then
    training_args+=("+data.nanoclaw_max_steps=${nanoclaw_max_steps}")
fi

# ================= 启动训练主进程：仅主节点执行 =================
if [ "${NODE_RANK}" = "0" ]; then
    echo "--> [Head Node] Starting VERL unified engine training..."
    echo "DEBUG: runtime_env=${RUNTIME_ENV_FILE}"
    echo "DEBUG: entrypoint=${training_args[*]}"

    ray job submit \
        --address="http://127.0.0.1:${DASHBOARD_PORT}" \
        --runtime-env="${RUNTIME_ENV_FILE}" \
        -- \
        "${training_args[@]}" 2>&1 | tee "logs/qwen3.5-nanoclaw-grpo-verl-engine-${start_time}.log"
else
    echo "--> [Worker Node] Setup finished. Keeping node alive for Ray..."
    tail -f /dev/null
fi
