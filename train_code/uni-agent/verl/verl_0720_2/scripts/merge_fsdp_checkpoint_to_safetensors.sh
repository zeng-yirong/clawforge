#!/usr/bin/env bash
# Merge a verl FSDP actor checkpoint into a Hugging Face safetensors model and
# validate the result.  Run this on the machine that has the same Python
# environment as the finished verl training job.
#
# Example:
#   bash scripts/merge_fsdp_checkpoint_to_safetensors.sh \
#     /path/to/source_env/qwen3.5_source_env_0713/global_step_123/actor \
#     /path/to/qwen3.5_source_env_0713_hf
#
# If the checkpoint does not contain actor/huggingface/{config,tokenizer} files
# (very old checkpoints only), pass the original base-model directory as the
# third argument.

set -Eeuo pipefail

readonly SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_DIR="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
readonly PYTHON_BIN="${PYTHON_BIN:-python3}"

usage() {
    cat <<'EOF'
Usage:
  bash scripts/merge_fsdp_checkpoint_to_safetensors.sh \
    <actor_checkpoint_dir> <output_hf_dir> [base_model_dir]

Arguments:
  actor_checkpoint_dir  verl actor checkpoint directory, for example:
                        .../global_step_123/actor
  output_hf_dir         New, empty directory for the merged HF model.
  base_model_dir        Optional fallback used only when the checkpoint lacks
                        huggingface/config.json and tokenizer files.

Environment variables:
  PYTHON_BIN=python3      Python interpreter from the verl training environment.
  VERIFY_LOAD=1           Also load the complete merged model with Transformers.
                          Needs roughly one model-size of extra host RAM.
  TRUST_REMOTE_CODE=1     Pass trust_remote_code=True to the checker.

The merger is CPU-side. Do not start Ray or torchrun for this operation.
EOF
}

if [[ $# -lt 2 || $# -gt 3 ]]; then
    usage >&2
    exit 2
fi

checkpoint_dir="${1%/}"
output_dir="${2%/}"
base_model_dir="${3:-}"

if [[ ! -d "${checkpoint_dir}" ]]; then
    echo "ERROR: actor checkpoint directory does not exist: ${checkpoint_dir}" >&2
    exit 2
fi

if [[ -e "${output_dir}" && ! -d "${output_dir}" ]]; then
    echo "ERROR: output path exists but is not a directory: ${output_dir}" >&2
    exit 2
fi

# Refuse to write into a non-empty directory. This avoids accidentally mixing
# a failed/incomplete merge with a new one. Choose a new directory instead.
if [[ -d "${output_dir}" ]] && [[ -n "$(find "${output_dir}" -mindepth 1 -maxdepth 1 -print -quit)" ]]; then
    echo "ERROR: output directory must be new or empty: ${output_dir}" >&2
    echo "       Existing files are left untouched. Pick another output directory." >&2
    exit 2
fi

if [[ ! -f "${checkpoint_dir}/fsdp_config.json" ]]; then
    echo "ERROR: ${checkpoint_dir}/fsdp_config.json is missing." >&2
    echo "       This script only accepts a verl FSDP actor checkpoint directory." >&2
    exit 2
fi

if ! compgen -G "${checkpoint_dir}/model_world_size_*_rank_*.pt" >/dev/null; then
    echo "ERROR: no FSDP model shard named model_world_size_*_rank_*.pt was found in ${checkpoint_dir}" >&2
    exit 2
fi

if [[ ! -f "${checkpoint_dir}/huggingface/config.json" ]]; then
    if [[ -z "${base_model_dir}" || ! -f "${base_model_dir}/config.json" ]]; then
        echo "ERROR: checkpoint does not contain huggingface/config.json." >&2
        echo "       Pass the original base-model directory as the third argument." >&2
        exit 2
    fi
fi

export PYTHONPATH="${PROJECT_DIR}${PYTHONPATH:+:${PYTHONPATH}}"

"${PYTHON_BIN}" - "${checkpoint_dir}" <<'PY'
import glob
import json
import os
import re
import sys

checkpoint_dir = sys.argv[1]
pattern = re.compile(r"model_world_size_(\d+)_rank_(\d+)\.pt$")
seen = {}
for path in glob.glob(os.path.join(checkpoint_dir, "model_world_size_*_rank_*.pt")):
    match = pattern.search(os.path.basename(path))
    if match:
        world_size, rank = map(int, match.groups())
        seen.setdefault(world_size, set()).add(rank)

if len(seen) != 1:
    raise SystemExit(f"Expected one FSDP world size, found: { {k: sorted(v) for k, v in seen.items()} }")

world_size, ranks = next(iter(seen.items()))
missing = sorted(set(range(world_size)) - ranks)
extra = sorted(ranks - set(range(world_size)))
if missing or extra:
    raise SystemExit(
        f"FSDP checkpoint is incomplete: world_size={world_size}, "
        f"present={len(ranks)}, missing={missing}, extra={extra}"
    )

with open(os.path.join(checkpoint_dir, "fsdp_config.json"), encoding="utf-8") as f:
    fsdp_config = json.load(f)

if fsdp_config.get("world_size") != world_size:
    raise SystemExit(
        "fsdp_config.json world_size does not match model filenames: "
        f"{fsdp_config.get('world_size')} != {world_size}"
    )

print(
    "Checkpoint preflight passed: "
    f"FSDP_version={fsdp_config.get('FSDP_version')}, world_size={world_size}, model_shards={len(ranks)}"
)
PY

merge_args=(
    "${PYTHON_BIN}" "${PROJECT_DIR}/scripts/legacy_model_merger.py" merge
    --backend fsdp
    --local_dir "${checkpoint_dir}"
    --target_dir "${output_dir}"
)

# Current verl checkpoints always include the configuration under
# actor/huggingface. Keep compatibility with old checkpoints that did not.
if [[ ! -f "${checkpoint_dir}/huggingface/config.json" ]]; then
    merge_args+=(--hf_model_path "${base_model_dir}")
fi

echo "==> Merging FSDP checkpoint to Hugging Face safetensors"
printf '    %q ' "${merge_args[@]}"
printf '\n'
"${merge_args[@]}"

echo "==> Checking merged model"
check_args=("${PYTHON_BIN}" "${PROJECT_DIR}/scripts/check_hf_safetensors_model.py" --model-dir "${output_dir}")
if [[ "${VERIFY_LOAD:-0}" == "1" ]]; then
    check_args+=(--load-model)
fi
if [[ "${TRUST_REMOTE_CODE:-0}" == "1" ]]; then
    check_args+=(--trust-remote-code)
fi
"${check_args[@]}"

echo "SUCCESS: merged safetensors model is ready at: ${output_dir}"
echo "         Check report: ${output_dir}/merge_check.json"


