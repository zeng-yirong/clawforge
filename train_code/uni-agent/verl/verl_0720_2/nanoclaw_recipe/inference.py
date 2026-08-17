from __future__ import annotations

import copy
import json
import os
import uuid
from pathlib import Path
from pprint import pprint
from typing import Any

import hydra
import numpy as np
import ray
import torch
from omegaconf import DictConfig, ListConfig, OmegaConf
from torch.utils.data import DataLoader, SequentialSampler

from verl.experimental.agent_loop import AgentLoopManager
from verl.protocol import DataProto
from verl.trainer.ppo.utils import create_rl_dataset
from verl.utils import hf_processor, hf_tokenizer
from verl.utils.dataset.rl_dataset import collate_fn
from verl.utils.device import auto_set_device
from verl.utils.fs import copy_to_local
from verl.workers.rollout.llm_server import LLMServerManager

from nanoclaw_recipe.nanoclaw import prepare_workspace, safe_name


CLAW_EVAL_OFFLINE_FORMAT = "claw-eval-nanoclaw-offline-v1"
CLAW_EVAL_OFFLINE_TASK_COUNT = 128
NANOCLAW_AIME_FORMAT = "nanoclaw-aime-v1"
CLAW_BENCH_PRO_FORMAT = "clawbenchpro-training-compatible-v1"


def plain_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): plain_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [plain_value(item) for item in value]
    if isinstance(value, np.ndarray):
        return plain_value(value.tolist())
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, torch.Tensor):
        return plain_value(value.detach().cpu().tolist())
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return repr(value)


def config_value(config: DictConfig, key: str, default: Any) -> Any:
    inference_config = config.get("inference")
    if inference_config is None:
        return default
    return inference_config.get(key, default)


def normalize_data_files(data_files: Any) -> list[str]:
    if isinstance(data_files, str):
        return [data_files]
    if isinstance(data_files, ListConfig):
        return [str(item) for item in data_files]
    return [str(item) for item in data_files]


def validate_benchmark_config(config: DictConfig) -> tuple[Path, list[str], str]:
    """Validate a complete manifest-backed Nanoclaw benchmark split."""
    data_files = normalize_data_files(config.data.train_files)
    if len(data_files) != 1:
        raise ValueError(
            "Nanoclaw benchmark inference requires exactly one data.train_files directory; "
            f"received {data_files}"
        )

    benchmark_root = Path(data_files[0]).expanduser().resolve()
    manifest_path = benchmark_root / "benchmark_manifest.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(
            "Nanoclaw benchmark_manifest.json not found: "
            f"{manifest_path}"
        )
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValueError(f"failed to read {manifest_path}: {exc}") from exc

    benchmark_format = str(manifest.get("format") or "")
    supported_formats = {
        CLAW_EVAL_OFFLINE_FORMAT,
        NANOCLAW_AIME_FORMAT,
        CLAW_BENCH_PRO_FORMAT,
    }
    if benchmark_format not in supported_formats:
        raise ValueError(
            f"unsupported Nanoclaw benchmark format: {benchmark_format!r}; expected one of "
            + ", ".join(repr(item) for item in sorted(supported_formats))
        )
    manifest_tasks = manifest.get("tasks")
    if not isinstance(manifest_tasks, list):
        raise ValueError(f"invalid tasks list in {manifest_path}")
    declared_count = int(manifest.get("task_count", -1))
    if benchmark_format == CLAW_EVAL_OFFLINE_FORMAT:
        expected_count = CLAW_EVAL_OFFLINE_TASK_COUNT
    elif benchmark_format == NANOCLAW_AIME_FORMAT:
        expected_count = 30
    else:
        # Generic training-compatible bundles, including the ClawBenchPro
        # adapter, declare their complete split size in the manifest.
        expected_count = declared_count
        if expected_count <= 0:
            raise ValueError(
                f"{benchmark_format} requires a positive task_count in {manifest_path}; "
                f"received {declared_count}"
            )
    if declared_count != expected_count or len(manifest_tasks) != expected_count:
        raise ValueError(
            f"complete {benchmark_format} inference requires exactly "
            f"{expected_count} tasks, but manifest declares "
            f"task_count={declared_count}, tasks={len(manifest_tasks)}"
        )

    task_ids = [str(item.get("task_id") or "") for item in manifest_tasks if isinstance(item, dict)]
    if len(task_ids) != expected_count or len(set(task_ids)) != expected_count:
        raise ValueError("benchmark manifest contains missing or duplicate task IDs")
    if any(not task_id.startswith("data_") for task_id in task_ids):
        raise ValueError("all manifest task IDs must start with 'data_'")

    task_glob = str(config.data.get("nanoclaw_task_glob", "data_*"))
    if task_glob != "data_*":
        raise ValueError(
            "manifest-backed inference requires data.nanoclaw_task_glob=data_*; "
            f"received {task_glob!r}"
        )
    task_subset = config.data.get("nanoclaw_task_ids", None)
    if task_subset not in (None, "", [], ()):
        raise ValueError(
            "data.nanoclaw_task_ids must be empty in complete manifest-backed inference; "
            "prepare a separate manifest-backed smoke-test bundle instead"
        )
    max_samples = int(config.data.get("train_max_samples", -1))
    if 0 < max_samples < expected_count:
        raise ValueError(
            f"data.train_max_samples would truncate the {expected_count}-task benchmark; "
            f"received {max_samples}"
        )

    missing_task_dirs = [task_id for task_id in task_ids if not (benchmark_root / task_id).is_dir()]
    if missing_task_dirs:
        raise FileNotFoundError(
            "converted task directories are missing: " + ", ".join(missing_task_dirs[:20])
        )
    # Claw-Eval's converter stores large shared fixtures under
    # _workspace_seeds. AIME tasks are self-contained flat task bundles whose
    # env_builder.py installs math_tools.py, so they intentionally have no
    # _workspace_seeds directory.
    if benchmark_format == CLAW_EVAL_OFFLINE_FORMAT:
        missing_seeds = [
            task_id
            for task_id in task_ids
            if not (benchmark_root / "_workspace_seeds" / task_id).is_dir()
        ]
        if missing_seeds:
            raise FileNotFoundError(
                "workspace seeds are missing: " + ", ".join(missing_seeds[:20])
            )

    print(
        f"[nanoclaw_benchmark_preflight] root={benchmark_root} "
        f"format={benchmark_format} tasks={len(task_ids)} mode=full",
        flush=True,
    )
    return benchmark_root, task_ids, benchmark_format


def init_ray(config: DictConfig) -> None:
    if ray.is_initialized():
        return
    ray_init_kwargs = OmegaConf.to_container(config.ray_kwargs.get("ray_init", {}), resolve=True) or {}
    runtime_env_config = ray_init_kwargs.pop("runtime_env", {}) or {}
    # inference.sh launches this driver with `ray job submit --runtime-env=...`.
    # In that mode the job already owns the working_dir and environment. Passing
    # the same runtime_env to ray.init again can make Ray re-package the staged
    # working directory (or reject the nested working_dir). Connect only.
    if bool(config_value(config, "ray_job_runtime_env_applied", False)):
        ray_init_kwargs.pop("runtime_env", None)
        print(
            "[ray_init] runtime env already applied by ray job; connecting without nested runtime_env",
            flush=True,
        )
        ray.init(**ray_init_kwargs)
        return
    if isinstance(runtime_env_config, str):
        runtime_env_path = Path(runtime_env_config).expanduser().resolve()
        runtime_env = OmegaConf.to_container(OmegaConf.load(runtime_env_path), resolve=True) or {}
    else:
        runtime_env = dict(runtime_env_config)
    env_vars = dict(runtime_env.get("env_vars", {}) or {})
    env_vars.setdefault("TOKENIZERS_PARALLELISM", "false")
    env_vars.setdefault("NCCL_DEBUG", "WARN")
    env_vars.setdefault("VLLM_USE_V1", os.environ.get("VLLM_USE_V1", "1"))
    env_vars.setdefault("RAY_EXPERIMENTAL_NOSET_ASCEND_RT_VISIBLE_DEVICES", "1")
    for key, value in os.environ.items():
        if key.startswith(("NANOCLAW_", "HCCL_", "VLLM_")):
            env_vars.setdefault(key, value)
    runtime_env["env_vars"] = env_vars
    ray_init_kwargs["runtime_env"] = runtime_env
    ray.init(**ray_init_kwargs)


def build_dataset(config: DictConfig, expected_count: int):
    model_path = copy_to_local(
        config.actor_rollout_ref.model.path,
        use_shm=config.actor_rollout_ref.model.get("use_shm", False),
    )
    trust_remote_code = config.data.get("trust_remote_code", False)
    tokenizer = hf_tokenizer(model_path, trust_remote_code=trust_remote_code)
    processor = hf_processor(model_path, trust_remote_code=trust_remote_code, use_fast=True)
    dataset = create_rl_dataset(
        normalize_data_files(config.data.train_files),
        config.data,
        tokenizer,
        processor,
        is_train=False,
        max_samples=config.data.get("train_max_samples", -1),
    )
    if len(dataset) != expected_count:
        raise ValueError(
            "CustomRLHFDataset did not load the complete benchmark split: "
            f"expected {expected_count}, got {len(dataset)}"
        )
    return dataset, tokenizer


def build_dataloader(config: DictConfig, dataset) -> DataLoader:
    prompt_batch_size = int(config_value(config, "prompt_batch_size", 8))
    if prompt_batch_size <= 0:
        raise ValueError("inference.prompt_batch_size must be positive")
    num_workers = int(config_value(config, "dataloader_num_workers", 0))
    if num_workers < 0:
        raise ValueError("inference.dataloader_num_workers must be non-negative")
    return DataLoader(
        dataset=dataset,
        batch_size=prompt_batch_size,
        sampler=SequentialSampler(dataset),
        collate_fn=collate_fn,
        num_workers=num_workers,
        drop_last=False,
        pin_memory=False,
    )


def create_agent_loop_manager(config: DictConfig) -> tuple[LLMServerManager, AgentLoopManager]:
    """Create the training-identical rollout stack without any reward/verifier workers."""
    llm_server_manager = LLMServerManager.create(
        config=config,
        worker_group=None,
        rollout_resource_pool=None,
    )
    agent_loop_manager = AgentLoopManager.create(
        config=config,
        llm_client=llm_server_manager.get_client(),
        reward_loop_worker_handles=None,
    )
    return llm_server_manager, agent_loop_manager


def align_non_tensor_batch_fields(outputs: list[DataProto]) -> None:
    """Align optional non-tensor fields returned by AgentLoop workers.

    Some trajectory fields are conditional. For example, ``nanoclaw`` is only
    added when a rollout actually invokes the Nanoclaw workspace tool. Because
    balanced inference dispatches different prompt groups to different workers,
    their returned ``non_tensor_batch`` dictionaries can have different keys.

    ``DataProto.concat`` expects every input to contain the same keys and every
    concatenated non-tensor field to have the same leading dimension as the
    tensor batch. Fill a missing optional field with object ``None`` values for
    that worker while rejecting fields that are already internally malformed.
    """
    if not outputs:
        return

    all_keys: set[str] = set()
    for chunk_output in outputs:
        all_keys.update(chunk_output.non_tensor_batch.keys())

    for worker_index, chunk_output in enumerate(outputs):
        chunk_size = len(chunk_output)
        for key in all_keys:
            if key not in chunk_output.non_tensor_batch:
                missing_values = np.empty(chunk_size, dtype=object)
                missing_values[:] = None
                chunk_output.non_tensor_batch[key] = missing_values
                continue

            value = chunk_output.non_tensor_batch[key]
            if not isinstance(value, np.ndarray):
                raise TypeError(
                    "AgentLoop worker returned a non-numpy non-tensor field: "
                    f"worker={worker_index}, key={key!r}, type={type(value).__name__}"
                )
            if value.ndim == 0 or value.shape[0] != chunk_size:
                field_length = 0 if value.ndim == 0 else value.shape[0]
                raise ValueError(
                    "AgentLoop worker returned an inconsistent non-tensor field: "
                    f"worker={worker_index}, key={key!r}, "
                    f"field_length={field_length}, worker_batch_size={chunk_size}"
                )


def generate_sequences_balanced(agent_loop_manager: AgentLoopManager, prompts: DataProto) -> DataProto:
    """Dispatch a real-only batch without creating padded duplicate trajectories."""
    prompt_indices = prompts.non_tensor_batch.get("index")
    if prompt_indices is None:
        prompt_indices = np.arange(len(prompts))
    group_boundaries = [0]
    for row_index in range(1, len(prompts)):
        if prompt_indices[row_index] != prompt_indices[row_index - 1]:
            group_boundaries.append(row_index)
    group_boundaries.append(len(prompts))
    rollout_groups = [
        np.arange(group_boundaries[i], group_boundaries[i + 1])
        for i in range(len(group_boundaries) - 1)
    ]
    active_worker_count = min(len(rollout_groups), len(agent_loop_manager.agent_loop_workers))
    if active_worker_count <= 0:
        raise ValueError("cannot generate an empty inference batch")
    group_chunks = np.array_split(np.arange(len(rollout_groups)), active_worker_count)
    index_chunks = [
        np.concatenate([rollout_groups[group_index] for group_index in group_chunk])
        for group_chunk in group_chunks
        if len(group_chunk) > 0
    ]
    prompt_chunks = [prompts.select_idxs(indices) for indices in index_chunks]
    active_workers = agent_loop_manager.agent_loop_workers[: len(prompt_chunks)]
    outputs = ray.get(
        [
            worker.generate_sequences.remote(chunk)
            for worker, chunk in zip(active_workers, prompt_chunks, strict=True)
        ]
    )

    if not outputs:
        raise RuntimeError("AgentLoop workers returned no inference outputs")

    # Tool use and other trajectory-dependent behavior can create optional
    # fields on only a subset of workers. Align them before DataProto.concat so
    # every concatenated non-tensor array has the full rollout batch length.
    align_non_tensor_batch_fields(outputs)
    output = DataProto.concat(outputs)

    metrics = []
    for worker_index, chunk_output in enumerate(outputs):
        worker_metrics = chunk_output.meta_info.pop("metrics", None)
        if worker_metrics is None:
            raise RuntimeError(
                "AgentLoop worker output is missing metrics: "
                f"worker={worker_index}"
            )
        metrics.append(worker_metrics)

    timing = agent_loop_manager._performance_metrics(metrics, output)
    output.meta_info = {"timing": timing, **outputs[0].meta_info}
    return output


def get_row_value(data: DataProto, key: str, row_index: int, default: Any = None) -> Any:
    values = data.non_tensor_batch.get(key)
    if values is None or row_index >= len(values):
        return default
    return values[row_index]


def is_valid_json_file(path: Path) -> bool:
    if not path.is_file():
        return False
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return False
    return True


def rollout_workspace_is_materialized(state: Any) -> bool:
    """Return whether an existing rollout state points to real output on disk."""
    if not isinstance(state, dict):
        return False
    if state.get("status") != "ready":
        return False
    result_dir_value = state.get("result_dir")
    workspace_after_value = state.get("workspace_after")
    if not result_dir_value or not workspace_after_value:
        return False
    result_dir = Path(str(result_dir_value))
    workspace_after = Path(str(workspace_after_value))
    return result_dir.is_dir() and workspace_after.is_dir()


def ensure_rollout_workspaces(data: DataProto, tokenizer) -> None:
    """Materialize an unmodified workspace for trajectories that made no tool call.

    Training normally gets this fallback from the reward path. Pure rollout has no
    reward path, but benchmark adapters still need one final workspace per sample.
    This function only runs env_builder.py; it never invokes a verifier.
    """
    states = data.non_tensor_batch.get("nanoclaw")
    if states is None:
        states = np.empty(len(data), dtype=object)
        states[:] = None
        data.non_tensor_batch["nanoclaw"] = states

    reward_models = data.non_tensor_batch.get("reward_model")
    for row_index in range(len(data)):
        state = states[row_index]
        if rollout_workspace_is_materialized(state):
            result_dir = Path(str(state["result_dir"]))
            history_path = result_dir / "conversation_history.json"
            trajectory_path = result_dir / "trajectory.json"
            # ToolAgentLoop deliberately treats trajectory persistence failures
            # as warnings. Pure inference must repair that output before it can
            # count the rollout as complete.
            if not is_valid_json_file(history_path) or not is_valid_json_file(trajectory_path):
                request_id = str(state.get("request_id") or f"inference_repair_{uuid.uuid4().hex}")
                write_fallback_trajectory(data, row_index, tokenizer, state, request_id=request_id)
            continue

        if isinstance(state, dict) and (state.get("result_dir") or state.get("workspace_after")):
            raise RuntimeError(
                "Nanoclaw rollout state points to a missing workspace and cannot be treated as saved: "
                f"row={row_index}, task_id={state.get('task_id')!r}, "
                f"result_dir={state.get('result_dir')!r}, "
                f"workspace_after={state.get('workspace_after')!r}, status={state.get('status')!r}"
            )

        reward_model = reward_models[row_index] if reward_models is not None else None
        task_config = reward_model.get("ground_truth") if isinstance(reward_model, dict) else None
        if not isinstance(task_config, dict):
            raise ValueError(f"missing Nanoclaw task config for rollout row {row_index}")

        task_config = copy.deepcopy(task_config)
        task_config.update(
            {
                "rollout_step": get_row_value(data, "rollout_step", row_index),
                "rollout_sample_index": get_row_value(data, "rollout_sample_index", row_index),
                "rollout_n": get_row_value(data, "rollout_n", row_index),
                "validate": False,
            }
        )
        request_id = f"inference_{uuid.uuid4().hex}"
        state = prepare_workspace(task_config, request_id=request_id, source="inference_output")
        states[row_index] = state
        write_fallback_trajectory(data, row_index, tokenizer, state, request_id=request_id)


def response_token_data(data: DataProto, row_index: int) -> tuple[list[int], list[int], list[int]]:
    responses = data.batch["responses"][row_index].detach().cpu()
    response_mask = data.batch["response_mask"][row_index].detach().cpu()
    prompt_width = data.batch["prompts"].shape[1]
    response_attention_mask = data.batch["attention_mask"][row_index, prompt_width:].detach().cpu().bool()
    response_ids = responses[response_attention_mask].tolist()
    training_mask = response_mask[response_attention_mask].tolist()
    assistant_ids = responses[response_attention_mask & response_mask.bool()].tolist()
    return response_ids, training_mask, assistant_ids


def write_fallback_trajectory(
    data: DataProto,
    row_index: int,
    tokenizer,
    state: dict[str, Any],
    *,
    request_id: str,
) -> None:
    """Write trajectory files for a rollout that never initialized a tool workspace."""
    response_ids, response_mask, assistant_ids = response_token_data(data, row_index)
    result_dir = Path(str(state["result_dir"]))
    final_answer = get_row_value(data, "rollout_final_answer", row_index)
    termination_reason = get_row_value(data, "rollout_termination_reason", row_index)
    raw_prompt = plain_value(get_row_value(data, "raw_prompt", row_index, []))
    assistant_text = tokenizer.decode(assistant_ids, skip_special_tokens=False)
    trajectory_text = tokenizer.decode(response_ids, skip_special_tokens=False)
    conversation_messages = list(raw_prompt) if isinstance(raw_prompt, list) else []
    if assistant_text:
        conversation_messages.append({"role": "assistant", "content": assistant_text})

    conversation = {
        "task_id": state.get("task_id"),
        "rollout_step": get_row_value(data, "rollout_step", row_index),
        "rollout_sample_index": get_row_value(data, "rollout_sample_index", row_index),
        "rollout_n": get_row_value(data, "rollout_n", row_index),
        "status": "completed" if termination_reason == "completed_no_tool_call" else "failed",
        "termination_reason": termination_reason,
        "final_answer": final_answer,
        "assistant_turns": get_row_value(data, "rollout_assistant_turns", row_index),
        "user_turns": get_row_value(data, "rollout_user_turns", row_index),
        "tool_call_count": get_row_value(data, "rollout_tool_call_count", row_index),
        "response_token_count": len(response_ids),
        "assistant_token_count": int(sum(response_mask)),
        "messages": conversation_messages,
        "events": [],
    }
    trajectory = {
        "request_id": request_id,
        "summary": {
            "termination_reason": termination_reason,
            "assistant_turns": conversation["assistant_turns"],
            "user_turns": conversation["user_turns"],
            "tool_call_count": conversation["tool_call_count"],
            "response_tokens": len(response_ids),
        },
        "rollout": {
            "task_id": state.get("task_id"),
            "step": conversation["rollout_step"],
            "sample_index": conversation["rollout_sample_index"],
            "rollout_n": conversation["rollout_n"],
        },
        "workspace": plain_value(state),
        "messages": conversation_messages,
        "events": [],
        "trajectory_text": trajectory_text,
    }
    (result_dir / "conversation_history.json").write_text(
        json.dumps(conversation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (result_dir / "trajectory.json").write_text(
        json.dumps(trajectory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def validate_batch_rollout_paths(data: DataProto, output_root: Path) -> None:
    """Validate the exact task/sample directory selected for each rollout row."""
    states = data.non_tensor_batch.get("nanoclaw")
    if states is None or len(states) != len(data):
        raise RuntimeError(
            "Nanoclaw inference batch has no complete workspace-state mapping: "
            f"rows={len(data)}, states={0 if states is None else len(states)}"
        )

    seen_paths: dict[Path, int] = {}
    errors: list[str] = []
    for row_index in range(len(data)):
        state = states[row_index]
        task_id = get_row_value(data, "rollout_task_id", row_index)
        if task_id is None and isinstance(state, dict):
            task_id = state.get("task_id")
        sample_index = get_row_value(data, "rollout_n", row_index)
        if sample_index is None:
            sample_index = get_row_value(data, "rollout_index", row_index)

        try:
            sample_index = int(sample_index)
        except (TypeError, ValueError):
            errors.append(
                f"row={row_index}: invalid rollout_n={sample_index!r}, task_id={task_id!r}"
            )
            continue
        if not task_id:
            errors.append(f"row={row_index}: missing rollout task ID, rollout_n={sample_index}")
            continue
        if not isinstance(state, dict) or not state.get("result_dir"):
            errors.append(
                f"row={row_index}: missing Nanoclaw result state, "
                f"task_id={task_id!r}, rollout_n={sample_index}"
            )
            continue

        expected_path = (output_root / "step_1" / f"{safe_name(str(task_id))}_sample_{sample_index}").resolve()
        actual_path = Path(str(state["result_dir"])).expanduser().resolve()
        if actual_path != expected_path:
            errors.append(
                f"row={row_index}: non-canonical result directory, task_id={task_id!r}, "
                f"rollout_n={sample_index}, expected={expected_path}, actual={actual_path}"
            )
        if actual_path in seen_paths:
            errors.append(
                f"row={row_index}: duplicate result directory also used by row={seen_paths[actual_path]}, "
                f"task_id={task_id!r}, rollout_n={sample_index}, path={actual_path}"
            )
        else:
            seen_paths[actual_path] = row_index
        if not rollout_workspace_is_materialized(state):
            errors.append(
                f"row={row_index}: result directory/workspace is missing on disk, "
                f"task_id={task_id!r}, rollout_n={sample_index}, path={actual_path}"
            )

    if errors:
        raise RuntimeError(
            "Nanoclaw rollout-to-directory mapping is invalid:\n  " + "\n  ".join(errors)
        )


def audit_saved_rollout_directories(
    output_root: Path,
    task_ids: list[str],
    rollout_n: int,
) -> None:
    """Require one canonical, complete directory for every task/sample pair."""
    step_dir = output_root / "step_1"
    missing_dirs: list[str] = []
    incomplete_dirs: list[str] = []
    conflict_dirs: list[str] = []

    for task_id in task_ids:
        safe_task_id = safe_name(task_id)
        for sample_index in range(rollout_n):
            expected_name = f"{safe_task_id}_sample_{sample_index}"
            result_dir = step_dir / expected_name
            if not result_dir.is_dir():
                missing_dirs.append(str(result_dir))
                if step_dir.is_dir():
                    conflict_dirs.extend(
                        str(path)
                        for path in sorted(step_dir.glob(f"{expected_name}_*"))
                        if path.is_dir()
                    )
                continue

            missing_parts = []
            if not (result_dir / "workspace_after").is_dir():
                missing_parts.append("workspace_after/")
            if not is_valid_json_file(result_dir / "nanoclaw_metadata.json"):
                missing_parts.append("nanoclaw_metadata.json")
            if not is_valid_json_file(result_dir / "conversation_history.json"):
                missing_parts.append("conversation_history.json")
            if not is_valid_json_file(result_dir / "trajectory.json"):
                missing_parts.append("trajectory.json")
            if missing_parts:
                incomplete_dirs.append(f"{result_dir}: missing_or_invalid={','.join(missing_parts)}")

            if step_dir.is_dir():
                conflict_dirs.extend(
                    str(path)
                    for path in sorted(step_dir.glob(f"{expected_name}_*"))
                    if path.is_dir()
                )

    unique_conflicts = sorted(set(conflict_dirs))
    if missing_dirs or incomplete_dirs or unique_conflicts:
        diagnostics = [
            "Nanoclaw inference output is incomplete on disk.",
            f"expected_task_count={len(task_ids)}, rollout_n={rollout_n}, "
            f"expected_directories={len(task_ids) * rollout_n}",
        ]
        if missing_dirs:
            diagnostics.append("missing canonical directories:\n  " + "\n  ".join(missing_dirs))
        if incomplete_dirs:
            diagnostics.append("incomplete canonical directories:\n  " + "\n  ".join(incomplete_dirs))
        if unique_conflicts:
            diagnostics.append(
                "conflicting request-id-suffixed directories (usually caused by duplicate initialization "
                "or stale output):\n  " + "\n  ".join(unique_conflicts)
            )
        raise RuntimeError("\n".join(diagnostics))

    print(
        f"[nanoclaw_output_audit_ok] root={output_root} step=1 "
        f"tasks={len(task_ids)} rollout_n={rollout_n} directories={len(task_ids) * rollout_n}",
        flush=True,
    )


@hydra.main(config_path="../verl/trainer/config", config_name="ppo_trainer", version_base=None)
def main(config: DictConfig) -> None:
    auto_set_device(config)
    OmegaConf.resolve(config)

    benchmark_root, expected_task_ids, benchmark_format = validate_benchmark_config(config)
    expected_task_count = len(expected_task_ids)
    output_root = Path(str(config.data.nanoclaw_temp_root)).expanduser().resolve()

    model_name = str(config_value(config, "model_name", Path(str(config.actor_rollout_ref.model.path)).name))
    rollout_n = int(config.actor_rollout_ref.rollout.n)
    if rollout_n <= 0:
        raise ValueError("actor_rollout_ref.rollout.n must be positive")
    if config.actor_rollout_ref.rollout.mode != "async":
        raise ValueError("Nanoclaw inference requires actor_rollout_ref.rollout.mode=async")
    if not config.actor_rollout_ref.rollout.multi_turn.enable:
        raise ValueError("Nanoclaw inference requires actor_rollout_ref.rollout.multi_turn.enable=True")
    total_rollout_devices = int(config.actor_rollout_ref.rollout.nnodes) * int(
        config.actor_rollout_ref.rollout.n_gpus_per_node
    )
    rollout_world_size = (
        int(config.actor_rollout_ref.rollout.tensor_model_parallel_size)
        * int(config.actor_rollout_ref.rollout.data_parallel_size)
        * int(config.actor_rollout_ref.rollout.pipeline_model_parallel_size)
    )
    if total_rollout_devices <= 0 or total_rollout_devices % rollout_world_size != 0:
        raise ValueError(
            "rollout devices must be a positive multiple of TP*DP*PP: "
            f"devices={total_rollout_devices}, replica_world_size={rollout_world_size}"
        )

    print("Resolved inference config:")
    pprint(OmegaConf.to_container(config, resolve=True))
    init_ray(config)
    dataset, tokenizer = build_dataset(config, expected_task_count)
    print(
        f"[nanoclaw_benchmark_dataset_ready] root={benchmark_root} format={benchmark_format} "
        f"prompts={len(dataset)} first={expected_task_ids[0]} last={expected_task_ids[-1]}",
        flush=True,
    )
    dataloader = build_dataloader(config, dataset)
    _, agent_loop_manager = create_agent_loop_manager(config)

    total_prompts = 0
    total_rollouts = 0
    try:
        for batch_index, batch_dict in enumerate(dataloader, start=1):
            prompt_count = len(batch_dict["dummy_tensor"])
            batch = DataProto.from_single_dict(batch_dict)
            batch.non_tensor_batch["uid"] = np.array(
                [str(uuid.uuid4()) for _ in range(prompt_count)],
                dtype=object,
            )
            # Inference is one benchmark step regardless of dataloader batch count.
            # This keeps all outputs under step_1/data_x_sample_y/.
            batch.meta_info.update({"global_steps": 1, "validate": False})
            rollout_batch = batch.repeat(repeat_times=rollout_n, interleave=True)
            original_rollout_count = len(rollout_batch)

            print(
                f"[nanoclaw_inference_batch] batch={batch_index} prompts={prompt_count} "
                f"rollouts={original_rollout_count}",
                flush=True,
            )
            output = generate_sequences_balanced(agent_loop_manager, rollout_batch)
            output = rollout_batch.union(output)
            ensure_rollout_workspaces(output, tokenizer)
            validate_batch_rollout_paths(output, output_root)

            total_prompts += prompt_count
            total_rollouts += len(output)
    finally:
        ray.shutdown()

    if total_prompts != expected_task_count:
        raise RuntimeError(
            "incomplete Nanoclaw benchmark inference: "
            f"expected {expected_task_count} prompts, processed {total_prompts}"
        )
    expected_rollouts = expected_task_count * rollout_n
    if total_rollouts != expected_rollouts:
        raise RuntimeError(
            "incomplete Nanoclaw benchmark rollouts: "
            f"expected {expected_rollouts}, produced {total_rollouts}"
        )

    # In-memory rollout counts do not prove that AgentLoop workers persisted
    # every result. Require the canonical task/sample directory for every
    # expected rollout before reporting this checkpoint as complete.
    audit_saved_rollout_directories(output_root, expected_task_ids, rollout_n)

    print(
        f"[nanoclaw_inference_done] prompts={total_prompts} rollouts={total_rollouts} "
        f"model={model_name} benchmark={benchmark_format}",
        flush=True,
    )


if __name__ == "__main__":
    main()
