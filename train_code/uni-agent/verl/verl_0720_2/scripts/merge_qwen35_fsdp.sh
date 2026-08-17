#!/usr/bin/env bash
# Merge the FSDP actor checkpoint from run_qwen3_8b_0713.sh, then check it.
# Usage: bash scripts/merge_qwen35_fsdp.sh <global_step> [checkpoint_root]
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
STEP="${1:?Usage: $0 <global_step> [checkpoint_root]}"
CKPT_ROOT="${2:-${DEFAULT_LOCAL_DIR:-${MODEL_PATH:-/opt/huawei/dataset/zyr_yuyin/models/Qwen/Qwen3___5-27B}/source_env}}"
ACTOR_DIR="${CKPT_ROOT%/}/global_step_${STEP}/actor"
OUT_DIR="${ACTOR_DIR}/huggingface"

[[ -f "${ACTOR_DIR}/fsdp_config.json" ]] || { echo "FSDP checkpoint not found: ${ACTOR_DIR}" >&2; exit 1; }

PYTHONPATH="${ROOT}${PYTHONPATH:+:${PYTHONPATH}}" "${PYTHON_BIN:-python3}" -m verl.model_merger merge \
    --backend fsdp --local_dir "${ACTOR_DIR}" --target_dir "${OUT_DIR}"
"${PYTHON_BIN:-python3}" "${ROOT}/scripts/check_safetensors.py" "${OUT_DIR}"


