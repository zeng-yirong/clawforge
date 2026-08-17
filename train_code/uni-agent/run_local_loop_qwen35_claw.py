#!/usr/bin/env python3
"""Run Claw WORKPLACE tasks with a local Qwen3.5 vLLM instance.
The runner deliberately reuses the same task construction and runtime pieces as
training:
* ``ClawNativeDataset`` builds the prompt, per-task workspace setup command,
  CLI session bindings, and verifier configuration.
* ``AgentEnv`` creates one persistent local-native shell per rollout.
* ``ToolsManager`` parses Qwen XML tool calls and executes the scaffold tools.
* ``ClawRewardSpec`` invokes each task's ``verify_workplace.py`` and emits the
  normalized reward used for data filtering.
It differs from the verl training path only in generation: prompts for active
rollouts are batched through a local in-process vLLM ``LLM`` instance.
"""

from __future__ import annotations

import argparse
import asyncio
import copy
import importlib
import json
import logging
import os
import sys
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from tqdm import tqdm

from uni_agent.datasets.claw_native import ClawNativeDataset
from uni_agent.interaction import ToolsManager, ToolsManagerConfig
from uni_agent.interaction.tool_parser import FunctionCallFormatError
from uni_agent.interaction.tool_status import command_status_from_exit_code
from uni_agent.reward import load_reward_spec
from uni_agent.tools import ToolConfig


LOGGER = logging.getLogger(__name__)
REPO_ROOT = Path(__file__).resolve().parent
DEFAULT_TASKS_DIR = "claw_envs/claw_chains/example_tasks"
DEFAULT_TOOL_DOCS_DIR = "claw_envs/claw_chains/claw_tool_env_docs"
TOOL_NAMES = ["read", "write", "edit", "str_replace_editor", "ls", "find", "grep", "execute_bash", "finish"]


@dataclass
class ClawTask:
    sample_key: str
    sample_index: int
    task_id: str
    env_name: str
    scenario_id: str | None
    row: dict[str, Any]
    messages: list[dict[str, Any]]
    env: Any = None
    reward_spec: Any = None
    model_turns: int = 0
    timeout_budget: int = 3
    status: str = "running"
    exit_reason: str = ""
    error: str | None = None
    final_response: str = ""
    tool_trace: list[dict[str, Any]] = field(default_factory=list)
    reward: float = 0.0
    reward_info: dict[str, Any] = field(default_factory=dict)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Claw WORKPLACE tasks with local vLLM inference.")
    parser.add_argument("--model", required=True, help="Local Qwen3.5 model directory.")
    parser.add_argument("--tokenizer", default=None, help="Tokenizer directory; defaults to --model.")
    parser.add_argument("--tasks-dir", default=DEFAULT_TASKS_DIR, help="WORKPLACE tasks directory or JSON/JSONL manifest.")
    parser.add_argument("--output-file", required=True, help="JSONL file receiving one scored rollout per task.")
    parser.add_argument("--claw-repo-root", default=str(REPO_ROOT), help="uni-agent repository path on the inference host.")
    parser.add_argument("--tool-docs-dir", default=DEFAULT_TOOL_DOCS_DIR)
    parser.add_argument("--claw-format", choices=["without_skill", "skill", "both"], default="without_skill")
    parser.add_argument("--tool-parser", choices=["qwen3_coder", "hermes"], default="qwen3_coder")
    parser.add_argument("--task-ids", default="", help="Comma-separated task ids to include.")
    parser.add_argument("--env-names", default="", help="Comma-separated Claw environment names to include.")
    parser.add_argument("--no-cli", dest="include_cli", action="store_false", help="Disable optional Claw CLI setup.")
    parser.set_defaults(include_cli=True)
    parser.add_argument("--resume", action="store_true", help="Skip sample keys already present in --output-file.")
    parser.add_argument("--start-index", type=int, default=0)
    parser.add_argument("--end-index", type=int, default=-1)
    parser.add_argument("--max-samples", type=int, default=-1)
    parser.add_argument("--min-reward", type=float, default=1.0, help="Verifier reward threshold used for the output keep flag.")

    parser.add_argument("--tensor-parallel-size", type=int, default=1)
    parser.add_argument("--max-model-len", type=int, default=32768)
    parser.add_argument("--max-num-batched-tokens", type=int, default=32768)
    parser.add_argument("--gpu-memory-utilization", type=float, default=0.90)
    parser.add_argument("--dtype", default="auto")
    parser.add_argument("--no-trust-remote-code", dest="trust_remote_code", action="store_false")
    parser.set_defaults(trust_remote_code=True)
    parser.add_argument("--disable-enforce-eager", dest="enforce_eager", action="store_false")
    parser.set_defaults(enforce_eager=True)

    parser.add_argument("--max-new-tokens", type=int, default=8192)
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--top-p", type=float, default=0.8)
    parser.add_argument("--top-k", type=int, default=20)
    parser.add_argument("--batch-size", type=int, default=32, help="Active rollouts sent to vLLM per generation call.")
    parser.add_argument("--env-concurrency", type=int, default=16, help="Concurrent environment setup/reward operations.")
    parser.add_argument("--max-retries", type=int, default=3, help="Retries for a failed vLLM batch generation.")
    parser.add_argument("--max-turns", type=int, default=50, help="Maximum model generations per rollout.")
    parser.add_argument("--startup-timeout", type=int, default=120)
    parser.add_argument("--action-timeout", type=int, default=120)
    parser.add_argument("--timeout-budget", type=int, default=3)
    parser.add_argument("--eval-timeout", type=float, default=300.0)
    parser.add_argument("--tool-install-dir", default="~/.uni-agent/bin")
    parser.add_argument("--no-restrict-workspace", dest="restrict_workspace", action="store_false")
    parser.add_argument("--no-restrict-bash", dest="restrict_bash", action="store_false")
    parser.set_defaults(restrict_workspace=True, restrict_bash=True)
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], default="INFO")
    return parser.parse_args()


def setup_logging(level: str) -> None:
    logging.basicConfig(level=getattr(logging, level), format="%(asctime)s %(levelname)s %(name)s: %(message)s")


def resolve_path(path: str, base_dir: Path) -> Path:
    value = Path(path).expanduser()
    return value if value.is_absolute() else (base_dir / value).resolve()


def parse_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def clean_unicode(value: Any) -> Any:
    if isinstance(value, str):
        return value.encode("utf-16", "surrogatepass").decode("utf-16", "ignore")
    if isinstance(value, dict):
        return {str(clean_unicode(key)): clean_unicode(item) for key, item in value.items()}
    if isinstance(value, list | tuple):
        return [clean_unicode(item) for item in value]
    if hasattr(value, "model_dump"):
        return clean_unicode(value.model_dump())
    return value


def import_external_vllm() -> tuple[Any, Any]:
    script_dir = Path(__file__).resolve().parent
    original_sys_path = list(sys.path)
    try:
        sys.modules.pop("vllm", None)
        sys.path = [entry for entry in sys.path if Path(entry or os.getcwd()).resolve() != script_dir]
        module = importlib.import_module("vllm")
    finally:
        sys.path = original_sys_path
    return module.LLM, module.SamplingParams


def build_dataset(args: argparse.Namespace) -> ClawNativeDataset:
    repo_root = resolve_path(args.claw_repo_root, REPO_ROOT)
    tasks_dir = resolve_path(args.tasks_dir, repo_root)
    tool_docs_dir = resolve_path(args.tool_docs_dir, repo_root)
    config = {
        "claw_repo_root": str(repo_root),
        "claw_tool_docs_dir": str(tool_docs_dir),
        "claw_include_cli": args.include_cli,
        "claw_restrict_workspace": args.restrict_workspace,
        "claw_restrict_bash": args.restrict_bash,
        "claw_format": args.claw_format,
        "claw_task_ids": parse_csv(args.task_ids),
        "claw_envs": parse_csv(args.env_names),
        "claw_eval_timeout": args.eval_timeout,
        "filter_overlong_prompts": False,
        "shuffle": False,
        "need_tools_kwargs": True,
    }
    return ClawNativeDataset(data_files=str(tasks_dir), tokenizer=None, processor=None, config=config, max_samples=args.max_samples)


def load_processed_keys(output_file: Path) -> set[str]:
    if not output_file.is_file():
        return set()
    processed: set[str] = set()
    with output_file.open("r", encoding="utf-8") as handle:
        for line in handle:
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            sample_key = record.get("sample_key")
            if isinstance(sample_key, str):
                processed.add(sample_key)
    return processed


def write_jsonl(output_file: Path, records: list[dict[str, Any]]) -> None:
    if not records:
        return
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("a", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(clean_unicode(record), ensure_ascii=False, default=str) + "\n")


def create_tasks(dataset: ClawNativeDataset, args: argparse.Namespace, processed_keys: set[str]) -> list[ClawTask]:
    rows = [dataset[index] for index in range(len(dataset))]
    end = args.end_index if args.end_index >= 0 else len(rows)
    selected = rows[args.start_index : end]
    tasks: list[ClawTask] = []
    for row in selected:
        extra_info = row.get("extra_info", {})
        task_id = str(extra_info.get("task_id") or "unknown")
        sample_index = int(row.get("index", extra_info.get("index", 0)))
        fmt = str(extra_info.get("format") or args.claw_format)
        sample_key = f"{task_id}:{fmt}:{sample_index}"
        if args.resume and sample_key in processed_keys:
            continue
        tasks.append(
            ClawTask(
                sample_key=sample_key,
                sample_index=sample_index,
                task_id=task_id,
                env_name=str(extra_info.get("env_name") or "unknown"),
                scenario_id=extra_info.get("scenario_id"),
                row=row,
                messages=copy.deepcopy(row["raw_prompt"]),
                timeout_budget=args.timeout_budget,
            )
        )
    return tasks


def build_sampling_params(args: argparse.Namespace, sampling_params_cls: Any) -> Any:
    kwargs = {"temperature": args.temperature, "top_p": args.top_p, "max_tokens": args.max_new_tokens}
    if args.top_k > 0:
        kwargs["top_k"] = args.top_k
    return sampling_params_cls(**kwargs)


def render_prompt(tokenizer: Any, messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> str:
    kwargs = {"tools": tools, "tokenize": False, "add_generation_prompt": True}
    try:
        prompt = tokenizer.apply_chat_template(messages, enable_thinking=False, **kwargs)
    except TypeError:
        prompt = tokenizer.apply_chat_template(messages, **kwargs)
    return str(clean_unicode(prompt))


def generate_batch(
    llm: Any,
    tokenizer: Any,
    sampling_params: Any,
    tools: list[dict[str, Any]],
    tasks: list[ClawTask],
    max_retries: int = 3,
) -> list[str | None]:
    prompts: list[str] = []
    valid_indices: list[int] = []
    outputs: list[str | None] = [None] * len(tasks)
    for index, task in enumerate(tasks):
        try:
            prompts.append(render_prompt(tokenizer, task.messages, tools))
            valid_indices.append(index)
        except Exception as exc:  # noqa: BLE001
            task.status = "template_error"
            task.exit_reason = "template_error"
            task.error = str(exc)

    if not prompts:
        return outputs

    last_error: Exception | None = None
    for attempt in range(max_retries):
        try:
            results = llm.generate(prompts, sampling_params)
            for result_index, result in enumerate(results):
                generated = result.outputs[0].text if result.outputs else ""
                outputs[valid_indices[result_index]] = generated
            return outputs
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            LOGGER.warning("vLLM generation attempt %d/%d failed: %s", attempt + 1, max_retries, exc)
            time.sleep(min(2**attempt, 8))

    for index in valid_indices:
        task = tasks[index]
        task.status = "generation_error"
        task.exit_reason = "generation_error"
        task.error = str(last_error)
    return outputs


async def setup_task(task: ClawTask, args: argparse.Namespace, tools_manager: ToolsManager) -> None:
    from uni_agent.interaction import AgentEnv, AgentEnvConfig

    env_overrides = copy.deepcopy(task.row["tools_kwargs"]["env"])
    env_config = AgentEnvConfig(
        deployment={"type": "local_native", "startup_timeout": args.startup_timeout},
        env_variables={"PAGER": "cat", "MANPAGER": "cat", "GIT_PAGER": "cat", "TQDM_DISABLE": "1"},
        tool_install_dir=Path(args.tool_install_dir).expanduser(),
        **env_overrides,
    )
    env = AgentEnv(run_id=str(uuid.uuid4()), env_config=env_config)
    task.env = env
    await env.start()
    await env.install_tools(tools_manager.tools)
    reward_config = {**task.row["tools_kwargs"]["reward"], "run_id": env.run_id, "env": env}
    task.reward_spec = load_reward_spec(reward_config)


async def setup_tasks(
    tasks: list[ClawTask], args: argparse.Namespace, tools_manager: ToolsManager
) -> tuple[list[ClawTask], list[ClawTask]]:
    semaphore = asyncio.Semaphore(args.env_concurrency)

    async def setup_one(task: ClawTask) -> ClawTask:
        try:
            async with semaphore:
                await setup_task(task, args, tools_manager)
        except Exception as exc:  # noqa: BLE001
            task.status = "setup_error"
            task.exit_reason = "setup_error"
            task.error = str(exc)
            if task.env is not None:
                await task.env.close()
        return task

    initialized = await asyncio.gather(*(setup_one(task) for task in tasks))
    active = [task for task in initialized if task.status == "running"]
    completed = [task for task in initialized if task.status != "running"]
    return active, completed


async def execute_tool_call(task: ClawTask, tool_call: Any, tools_manager: ToolsManager, args: argparse.Namespace) -> bool:
    from uni_agent.interaction.env import (
        ActionIncorrectSyntaxError,
        ActionPermissionError,
        ActionTimeoutError,
        TerminalNotAliveError,
    )

    assert task.env is not None
    action = tools_manager.get_tool_bash_command(tool_call)
    result: dict[str, Any] = {
        "tool_call_id": tool_call.id,
        "name": tool_call.function.name,
        "arguments": tool_call.function.arguments,
        "action": action,
    }
    terminal = False
    started = time.perf_counter()
    try:
        action_result = await task.env.run_action_with_status(action, action_timeout=args.action_timeout)
        observation = str(action_result["observation"])
        exit_code = int(action_result["exit_code"])
        status, terminal = command_status_from_exit_code(tool_call.function.name, exit_code)
    except ActionTimeoutError as exc:
        observation = str(exc)
        status = "timeout"
        task.timeout_budget -= 1
    except ActionIncorrectSyntaxError as exc:
        observation = str(exc)
        status = "syntax_error"
    except ActionPermissionError as exc:
        observation = str(exc)
        status = "permission_error"
    except TerminalNotAliveError as exc:
        observation = str(exc)
        status = "terminal_dead"
        terminal = True
        task.status = "terminal_dead"
        task.exit_reason = "terminal_dead"
        task.error = observation
    result.update({"status": status, "observation": observation, "elapsed_seconds": time.perf_counter() - started})
    task.tool_trace.append(result)
    if tool_call.function.name == "finish" and status == "ok":
        task.final_response = str(tool_call.function.arguments.get("answer", ""))
    task.messages.append(
        {"role": "tool", "tool_call_id": tool_call.id, "name": tool_call.function.name, "content": observation}
    )
    if task.timeout_budget < 0:
        task.status = "timeout_budget_exhausted"
        task.exit_reason = "timeout_budget_exhausted"
        terminal = True
    if terminal and task.status == "running":
        task.status = "finished" if tool_call.function.name == "finish" else "completed"
        task.exit_reason = "finished" if tool_call.function.name == "finish" else "terminal_tool"
    return terminal


async def advance_task(task: ClawTask, model_output: str, tools_manager: ToolsManager, args: argparse.Namespace) -> bool:
    if task.status != "running":
        return True
    task.model_turns += 1
    task.messages.append({"role": "assistant", "content": model_output})

    def stop_at_turn_limit() -> bool:
        if task.model_turns < args.max_turns:
            return False
        task.status = "max_turns"
        task.exit_reason = "max_turns"
        return True

    try:
        content, tool_calls = await tools_manager.parse_action(model_output=model_output)
    except FunctionCallFormatError as exc:
        observation = str(exc)
        task.tool_trace.append({"name": "parse_action", "status": "format_error", "observation": observation})
        task.messages.append({"role": "tool", "content": observation})
        return stop_at_turn_limit()

    if not tool_calls:
        observation = "No function call found in the response. Use the available tools or call finish."
        task.tool_trace.append({"name": "parse_action", "status": "format_error", "observation": observation})
        task.messages.append({"role": "tool", "content": observation})
        task.final_response = content.strip()
        return stop_at_turn_limit()

    for tool_call in tool_calls:
        if await execute_tool_call(task, tool_call, tools_manager, args):
            return True
    return stop_at_turn_limit()


async def finalize_task(task: ClawTask, min_reward: float) -> dict[str, Any]:
    try:
        if task.reward_spec is not None and task.env is not None:
            task.reward, task.reward_info = await task.reward_spec.compute_reward(interaction_result={"messages": task.messages})
    except Exception as exc:  # noqa: BLE001
        task.reward_info = {"error": f"reward_exception: {exc}"}
        if task.error is None:
            task.error = str(exc)
    finally:
        if task.env is not None:
            await task.env.close()

    return {
        "sample_key": task.sample_key,
        "sample_index": task.sample_index,
        "task_id": task.task_id,
        "env_name": task.env_name,
        "scenario_id": task.scenario_id,
        "status": task.status,
        "exit_reason": task.exit_reason,
        "error": task.error,
        "model_turns": task.model_turns,
        "final_response": task.final_response,
        "reward": task.reward,
        "keep": task.reward >= min_reward,
        "reward_info": task.reward_info,
        "tool_trace": task.tool_trace,
        "messages": task.messages,
        "tools_kwargs": task.row.get("tools_kwargs", {}),
    }


async def run_batch(
    tasks: list[ClawTask], llm: Any, tokenizer: Any, sampling_params: Any, tools_manager: ToolsManager, args: argparse.Namespace
) -> list[dict[str, Any]]:
    active, completed = await setup_tasks(tasks, args, tools_manager)
    while active:
        generated = generate_batch(
            llm, tokenizer, sampling_params, tools_manager.tools_schemas, active, max_retries=args.max_retries
        )
        next_active: list[ClawTask] = []
        advances = await asyncio.gather(
            *(advance_task(task, output or "", tools_manager, args) for task, output in zip(active, generated))
        )
        for task, terminal in zip(active, advances):
            if task.status != "running" or terminal:
                completed.append(task)
            else:
                next_active.append(task)
        active = next_active

    return await asyncio.gather(*(finalize_task(task, args.min_reward) for task in completed))


async def run(args: argparse.Namespace) -> None:
    dataset = build_dataset(args)
    output_file = resolve_path(args.output_file, REPO_ROOT)
    processed_keys = load_processed_keys(output_file) if args.resume else set()
    tasks = create_tasks(dataset, args, processed_keys)
    LOGGER.info("Loaded %d Claw rollout(s) after filters and resume.", len(tasks))
    if not tasks:
        return

    llm_cls, sampling_params_cls = import_external_vllm()
    from transformers import AutoTokenizer

    tokenizer_path = args.tokenizer or args.model
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_path, trust_remote_code=args.trust_remote_code)
    llm = llm_cls(
        model=args.model,
        tokenizer=tokenizer_path,
        tensor_parallel_size=args.tensor_parallel_size,
        trust_remote_code=args.trust_remote_code,
        max_model_len=args.max_model_len,
        max_num_batched_tokens=args.max_num_batched_tokens,
        gpu_memory_utilization=args.gpu_memory_utilization,
        dtype=args.dtype,
        enforce_eager=args.enforce_eager,
    )
    sampling_params = build_sampling_params(args, sampling_params_cls)
    tools_manager = ToolsManager(
        ToolsManagerConfig(tools=[ToolConfig(name=name) for name in TOOL_NAMES], parser=args.tool_parser)
    )

    progress = tqdm(total=len(tasks), desc="Claw Qwen3.5 inference")
    for start in range(0, len(tasks), args.batch_size):
        batch = tasks[start : start + args.batch_size]
        records = await run_batch(batch, llm, tokenizer, sampling_params, tools_manager, args)
        write_jsonl(output_file, records)
        progress.update(len(records))
        average_reward = sum(float(record["reward"]) for record in records) / max(len(records), 1)
        LOGGER.info("Wrote %d rollouts (batch average reward %.4f) to %s", len(records), average_reward, output_file)
    progress.close()


def main() -> None:
    args = parse_args()
    setup_logging(args.log_level)
    asyncio.run(run(args))


if __name__ == "__main__":
    main()
