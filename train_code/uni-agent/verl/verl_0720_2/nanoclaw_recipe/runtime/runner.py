from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from uuid import uuid4
from collections.abc import Iterable
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .backend import generate_reply, generate_replies
from .prompts import build_system_prompt
from .protocol import parse_model_reply
from .tools import execute_actions, workspace_subprocess_env
from .types import TaskRunRequest, TaskRunState, TaskSpec

try:
    from nanoclaw_recipe.common import copy_task_bundle as _copy_task_bundle, safe_name
except Exception:
    _copy_task_bundle = None

    def safe_name(raw_name: str) -> str:
        return "".join(ch if ch.isalnum() or ch in "_.-" else "_" for ch in raw_name).strip("._") or "task"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def copy_task_bundle(spec: TaskSpec, result_dir: Path) -> None:
    if _copy_task_bundle is not None:
        _copy_task_bundle(
            {
                "task_dir": str(spec.task_dir),
                "prompt_path": str(spec.prompt_path),
                "env_builder_path": str(spec.env_builder_path),
                "verifier_path": str(spec.verifier_path) if spec.verifier_path else None,
                "manifest_path": str(spec.manifest_path) if spec.manifest_path else None,
            },
            result_dir,
        )
        return

    for child in sorted(spec.task_dir.iterdir()):
        if child.name in {"workspace_before", "workspace_after", "workplace_before", "workplace_after", "__pycache__"}:
            continue
        destination = result_dir / child.name
        if child.is_dir():
            shutil.copytree(child, destination, dirs_exist_ok=True)
        elif child.is_file():
            shutil.copy2(child, destination)


def build_run_requests(specs: list[TaskSpec], *, n: int, rollout_step: int) -> list[TaskRunRequest]:
    requests: list[TaskRunRequest] = []
    for sample_index, spec in enumerate(specs):
        for rollout_n in range(n):
            requests.append(
                TaskRunRequest(
                    spec=spec,
                    rollout_step=rollout_step,
                    rollout_sample_index=sample_index,
                    rollout_n=rollout_n,
                )
            )
    return requests


def run_task(
    *,
    request: TaskRunRequest,
    result_root: Path,
    llm: Any,
    tokenizer: Any,
    sampling_params: Any,
    args: argparse.Namespace,
) -> dict[str, Any]:
    prepared = prepare_task_run_state(request=request, result_root=result_root, args=args)
    if isinstance(prepared, dict):
        return prepared

    state = prepared
    try:
        while state.status == "running" and state.steps_used < args.max_steps:
            reply = generate_reply(
                llm=llm,
                tokenizer=tokenizer,
                sampling_params=sampling_params,
                messages=state.messages,
                enable_thinking=args.enable_thinking,
            )
            process_task_reply(state, reply, args=args)
    except Exception as exc:
        state.status = "failed"
        state.error = f"{type(exc).__name__}: {exc}"
        state.events.append({"step": state.steps_used + 1, "error": state.error})
        write_task_state_history(state)
        raise

    return finalize_task_state(state, args=args)


def make_result_dir(result_root: Path, request: TaskRunRequest) -> Path:
    step_dir = result_root / f"step_{request.rollout_step}"
    return step_dir / f"{safe_name(request.spec.task_id)}_sample_{request.rollout_n}"


def prepare_task_run_state(
    *,
    request: TaskRunRequest,
    result_root: Path,
    args: argparse.Namespace,
) -> TaskRunState | dict[str, Any]:
    spec = request.spec
    result_dir = make_result_dir(result_root, request)
    if result_dir.exists():
        if args.overwrite:
            shutil.rmtree(result_dir)
        elif args.resume and is_completed_result(result_dir):
            print(f"[skip] step_{request.rollout_step}/{spec.task_id}_sample_{request.rollout_n}: completed result exists at {result_dir}", file=sys.stderr)
            return {
                "task_id": spec.task_id,
                "status": "skipped",
                "result_dir": str(result_dir),
                "rollout_step": request.rollout_step,
                "rollout_sample_index": request.rollout_sample_index,
                "rollout_n": request.rollout_n,
            }
        else:
            raise FileExistsError(f"result dir already exists: {result_dir}; pass --overwrite or --resume")

    result_dir.mkdir(parents=True, exist_ok=False)
    workspace_after = result_dir / "workspace_after"
    workspace_before = result_dir / "workspace_before"
    workspace_after.mkdir(parents=True, exist_ok=False)

    prompt_text = spec.prompt_path.read_text(encoding="utf-8")
    copy_task_bundle(spec, result_dir)

    env_result = run_env_builder(spec.env_builder_path, workspace_after)
    shutil.copytree(workspace_after, workspace_before)

    messages = build_initial_messages(
        prompt_text=prompt_text,
        workspace_after=workspace_after,
        args=args,
    )
    started_at = utc_now()
    state = TaskRunState(
        spec=spec,
        request=request,
        request_id=uuid4().hex,
        rollout_label=f"step_{request.rollout_step}/{spec.task_id}_sample_{request.rollout_n}",
        result_dir=result_dir,
        workspace_before=workspace_before,
        workspace_after=workspace_after,
        history_path=result_dir / "conversation_history.json",
        metadata_path=result_dir / "runner_metadata.json",
        prompt_text=prompt_text,
        env_result=env_result,
        started_at=started_at,
        started_time=time.time(),
        messages=messages,
    )
    write_task_state_history(state)
    return state


def build_initial_messages(
    *,
    prompt_text: str,
    workspace_after: Path,
    args: argparse.Namespace,
) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": build_system_prompt(
                args.allow_python_tool,
                workspace_dir=workspace_after,
                model=args.model,
                max_steps=args.max_steps,
            ),
        },
        {
            "role": "user",
            "content": (
                "Solve this task by using Nanoclaw-compatible tool calls to inspect and modify the workspace.\n"
                "On every assistant turn, first write a concise Thought section, then write either an Action section with JSON tool calls or a Final section.\n"
                "Only provide a final answer after the requested workspace changes are complete.\n\n"
                f"Task:\n{prompt_text}"
            ),
        },
    ]


def run_tasks_batched(
    *,
    requests: list[TaskRunRequest],
    result_root: Path,
    llm: Any,
    tokenizer: Any,
    sampling_params: Any,
    args: argparse.Namespace,
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    states: list[TaskRunState] = []
    finalized_state_ids: set[int] = set()
    finalize_futures: dict[Future[dict[str, Any]], TaskRunState] = {}
    max_verifier_workers = max(1, int(getattr(args, "verifier_workers", 1)))
    prepare_window_size = max(1, int(getattr(args, "prepare_window_size", None) or args.agent_batch_size))
    request_index = 0

    def append_result(result: dict[str, Any]) -> None:
        results.append(result)
        (result_root / "results.jsonl").write_text(iter_jsonl_results(results), encoding="utf-8")

    def prepare_one(request: TaskRunRequest) -> None:
        spec = request.spec
        print(f"[prepare] step_{request.rollout_step}/{spec.task_id}_sample_{request.rollout_n}", file=sys.stderr)
        try:
            prepared = prepare_task_run_state(request=request, result_root=result_root, args=args)
        except Exception as exc:
            result_dir = make_result_dir(result_root, request)
            result = {
                "task_id": spec.task_id,
                "status": "failed",
                "result_dir": str(result_dir),
                "error": f"{type(exc).__name__}: {exc}",
                "rollout_step": request.rollout_step,
                "rollout_sample_index": request.rollout_sample_index,
                "rollout_n": request.rollout_n,
                "rollout_label": f"step_{request.rollout_step}/{spec.task_id}_sample_{request.rollout_n}",
            }
            append_result(result)
            print(f"[error] {result['rollout_label']}: {result['error']}", file=sys.stderr)
            return

        if isinstance(prepared, dict):
            append_result(prepared)
        else:
            states.append(prepared)

    def fill_prepare_window() -> None:
        nonlocal request_index
        running_or_pending_finalize = sum(
            1 for state in states if state.status == "running" or id(state) not in finalized_state_ids
        )
        while request_index < len(requests) and running_or_pending_finalize < prepare_window_size:
            prepare_one(requests[request_index])
            request_index += 1
            running_or_pending_finalize = sum(
                1 for state in states if state.status == "running" or id(state) not in finalized_state_ids
            )

    def collect_finished_finalizers(done_only: bool) -> None:
        futures = list(finalize_futures)
        for future in futures:
            if done_only and not future.done():
                continue
            state = finalize_futures.pop(future)
            try:
                result = future.result()
            except Exception as exc:
                result = {
                    "task_id": state.spec.task_id,
                    "status": "failed",
                    "result_dir": str(state.result_dir),
                    "error": f"finalize {type(exc).__name__}: {exc}",
                    "rollout_step": state.request.rollout_step,
                    "rollout_sample_index": state.request.rollout_sample_index,
                    "rollout_n": state.request.rollout_n,
                    "rollout_label": state.rollout_label,
                }
                print(f"[finalize_error] {state.rollout_label}: {result['error']}", file=sys.stderr)
            append_result(result)
            states[:] = [existing_state for existing_state in states if existing_state is not state]
            print(
                f"[finalized] {state.rollout_label} status={result.get('status')} verifier={bool(state.verifier_result)}",
                file=sys.stderr,
            )

    def submit_finalize(executor: ThreadPoolExecutor, state: TaskRunState) -> None:
        if id(state) in finalized_state_ids:
            return
        finalized_state_ids.add(id(state))
        future = executor.submit(finalize_task_state, state, args=args)
        finalize_futures[future] = state
        print(
            f"[verify_submit] {state.rollout_label} status={state.status} dir={state.result_dir}",
            file=sys.stderr,
        )

    print(
        f"[prepare_window] size={prepare_window_size} total_samples={len(requests)}",
        file=sys.stderr,
    )

    with ThreadPoolExecutor(max_workers=max_verifier_workers) as finalize_executor:
        fill_prepare_window()
        while True:
            collect_finished_finalizers(done_only=True)
            fill_prepare_window()

            active_states = [state for state in states if state.status == "running"]
            if not active_states:
                if request_index >= len(requests) and not finalize_futures:
                    break
                if finalize_futures:
                    collect_finished_finalizers(done_only=False)
                    continue
                fill_prepare_window()
                continue

            current_batch = active_states[: args.agent_batch_size]
            print(
                "[batch] "
                + ", ".join(f"{state.rollout_label}:step{state.steps_used + 1}" for state in current_batch),
                file=sys.stderr,
            )

            try:
                replies = generate_replies(
                    llm=llm,
                    tokenizer=tokenizer,
                    sampling_params=sampling_params,
                    message_batches=[state.messages for state in current_batch],
                    enable_thinking=args.enable_thinking,
                )
                for state, reply in zip(current_batch, replies, strict=True):
                    process_task_reply(state, reply, args=args)
            except Exception as exc:
                error = f"{type(exc).__name__}: {exc}"
                for state in current_batch:
                    state.status = "failed"
                    state.error = error
                    state.events.append({"step": state.steps_used + 1, "error": error})
                    write_task_state_history(state)

            for state in current_batch:
                if state.status == "running":
                    continue
                submit_finalize(finalize_executor, state)

        for state in states:
            if id(state) in finalized_state_ids:
                continue
            submit_finalize(finalize_executor, state)
        collect_finished_finalizers(done_only=False)

    return results

def process_task_reply(state: TaskRunState, reply: str, *, args: argparse.Namespace) -> None:
    state.steps_used += 1
    step = state.steps_used
    state.messages.append({"role": "assistant", "content": reply})

    try:
        parsed_reply = parse_model_reply(reply)
    except ValueError as exc:
        observation = (
            f"Action parse error: {exc}. Output exactly one turn in this format: "
            "Thought: concise analysis, then Action: JSON tool_calls/actions; "
            "or Thought: concise analysis, then Final: final answer only when the task is complete."
        )
        state.events.append({"step": step, "reply": reply, "error": observation})
        if step >= args.max_steps:
            state.status = "failed"
            state.error = f"exceeded max steps ({args.max_steps}) without valid Thought+Action or Thought+Final"
        else:
            state.messages.append({"role": "user", "content": observation_message(observation)})
        write_task_state_history(state)
        return

    if parsed_reply.is_final:
        state.status = "completed"
        state.final_answer = parsed_reply.final_answer or ""
        state.events.append(
            {
                "step": step,
                "reply": reply,
                "thought": parsed_reply.thought,
                "is_final": True,
                "final_response_mode": "thought_final" if parsed_reply.thought else "plain_text_without_tool_calls",
            }
        )
        write_task_state_history(state)
        return

    actions = parsed_reply.actions or []
    action_events, observation, is_final, final_answer = execute_actions(
        actions,
        state.workspace_after,
        args=args,
        step=step,
    )
    state.events.append(
        {
            "step": step,
            "reply": reply,
            "thought": parsed_reply.thought,
            "actions": action_events,
            "observation": observation,
            "is_final": is_final,
        }
    )
    if is_final:
        state.status = "completed"
        state.final_answer = final_answer or ""
        write_task_state_history(state)
        return

    if step >= args.max_steps:
        state.status = "failed"
        state.error = f"exceeded max steps ({args.max_steps}) without final answer"
    else:
        state.messages.append({"role": "user", "content": observation_message(observation)})
    write_task_state_history(state)


def observation_message(observation: str) -> str:
    return (
        f"Observation:\n{observation}\n\n"
        "Analyze the observation first. Then respond with either:\n"
        "Thought:\n<concise analysis>\nAction:\n<JSON tool call(s)>\n\n"
        "or, if the task is complete:\n"
        "Thought:\n<concise completion check>\nFinal:\n<final answer>"
    )
def finalize_task_state(state: TaskRunState, *, args: argparse.Namespace) -> dict[str, Any]:
    if state.status == "running":
        state.status = "failed"
        state.error = state.error or f"exceeded max steps ({args.max_steps}) without final answer"

    if args.run_verifier and state.spec.verifier_path is not None:
        state.verifier_result = run_verifier(
            state.spec.verifier_path,
            state.workspace_after,
            timeout=args.verifier_timeout,
        )

    write_task_state_history(state)
    finished_at = utc_now()
    elapsed = round(time.time() - state.started_time, 3)
    metadata = {
        "task_id": state.spec.task_id,
        "status": state.status,
        "error": state.error,
        "final_answer": state.final_answer,
        "steps_used": state.steps_used,
        "started_at": state.started_at,
        "finished_at": finished_at,
        "elapsed_seconds": elapsed,
        "result_dir": str(state.result_dir),
        "rollout_label": state.rollout_label,
        "rollout_step": state.request.rollout_step,
        "rollout_sample_index": state.request.rollout_sample_index,
        "rollout_n": state.request.rollout_n,
        "prompt_path": str(state.spec.prompt_path),
        "env_builder_path": str(state.spec.env_builder_path),
        "verifier_source_path": str(state.spec.verifier_path) if state.spec.verifier_path else None,
        "workspace_before": str(state.workspace_before),
        "workspace_after": str(state.workspace_after),
        "conversation_history": str(state.history_path),
        "trajectory": str(state.result_dir / "trajectory.json"),
        "env_builder": state.env_result,
        "verifier": state.verifier_result,
        "model": args.model,
        "tokenizer": args.tokenizer or args.model,
        "max_steps": args.max_steps,
        "agent_batch_size": args.agent_batch_size,
        "allow_python_tool": args.allow_python_tool,
        "bash_timeout": getattr(args, "bash_timeout", 20.0),
        "backend": getattr(args, "backend", "local"),
        "api_base": getattr(args, "api_base", None) if getattr(args, "backend", "local") == "openai" else None,
        "served_model_name": getattr(args, "served_model_name", None),
        "tool_call_transport": "openai_chat_completions" if getattr(args, "backend", "local") == "openai" else "local_vllm_json_text",
    }
    state.metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_trajectory(state, elapsed=elapsed)
    return {
        "task_id": state.spec.task_id,
        "status": state.status,
        "result_dir": str(state.result_dir),
        "error": state.error,
        "rollout_label": state.rollout_label,
        "rollout_step": state.request.rollout_step,
        "rollout_sample_index": state.request.rollout_sample_index,
        "rollout_n": state.request.rollout_n,
        "steps_used": state.steps_used,
        "verifier": state.verifier_result,
    }


def write_task_state_history(state: TaskRunState) -> None:
    write_history(
        state.history_path,
        spec=state.spec,
        request=state.request,
        rollout_label=state.rollout_label,
        status=state.status,
        final_answer=state.final_answer,
        error=state.error,
        messages=state.messages,
        events=state.events,
        started_at=state.started_at,
        steps_used=state.steps_used,
    )


def is_completed_result(result_dir: Path) -> bool:
    metadata_path = result_dir / "runner_metadata.json"
    if not metadata_path.is_file():
        return False
    try:
        payload = json.loads(metadata_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    return payload.get("status") == "completed"


def run_env_builder(env_builder_path: Path, workspace: Path) -> dict[str, Any]:
    started = time.time()
    process = subprocess.run(
        [sys.executable, str(env_builder_path)],
        cwd=workspace,
        text=True,
        capture_output=True,
        env=workspace_subprocess_env(workspace),
        check=False,
    )
    result = {
        "returncode": process.returncode,
        "stdout": process.stdout,
        "stderr": process.stderr,
        "elapsed_seconds": round(time.time() - started, 3),
    }
    if process.returncode != 0:
        raise RuntimeError(
            f"env_builder.py failed for {env_builder_path} with code {process.returncode}\n"
            f"stdout:\n{process.stdout}\n\nstderr:\n{process.stderr}"
        )
    return result


def run_verifier(verifier_path: Path, workspace: Path, *, timeout: float) -> dict[str, Any]:
    started = time.time()
    try:
        process = subprocess.run(
            [sys.executable, str(verifier_path), str(workspace)],
            cwd=verifier_path.parent,
            text=True,
            capture_output=True,
            env=workspace_subprocess_env(workspace),
            timeout=timeout,
            check=False,
        )
        result: dict[str, Any] = {
            "returncode": process.returncode,
            "stdout": process.stdout,
            "stderr": process.stderr,
            "elapsed_seconds": round(time.time() - started, 3),
        }
    except subprocess.TimeoutExpired as exc:
        result = {
            "returncode": None,
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or "",
            "elapsed_seconds": round(time.time() - started, 3),
            "error": f"verifier timed out after {timeout:g}s",
        }

    score_path = workspace / "workplace_score.json"
    if score_path.is_file():
        try:
            result["workplace_score"] = json.loads(score_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            result["workplace_score_error"] = str(exc)
    return result


def write_history(
    path: Path,
    *,
    spec: TaskSpec,
    request: TaskRunRequest,
    rollout_label: str,
    status: str,
    final_answer: str | None,
    error: str | None,
    messages: list[dict[str, str]],
    events: list[dict[str, Any]],
    started_at: str,
    steps_used: int,
) -> None:
    payload = {
        "task_id": spec.task_id,
        "rollout_label": rollout_label,
        "rollout_step": request.rollout_step,
        "rollout_sample_index": request.rollout_sample_index,
        "rollout_n": request.rollout_n,
        "status": status,
        "final_answer": final_answer,
        "error": error,
        "started_at": started_at,
        "updated_at": utc_now(),
        "steps_used": steps_used,
        "messages": messages,
        "events": events,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def truncate_text(value: Any, limit: int = 20000) -> Any:
    if isinstance(value, str):
        return value if len(value) <= limit else value[:limit] + f"...(truncated {len(value) - limit} chars)"
    if isinstance(value, dict):
        return {key: truncate_text(item, limit=limit) for key, item in value.items()}
    if isinstance(value, list):
        return [truncate_text(item, limit=limit) for item in value]
    return value


def write_trajectory(state: TaskRunState, *, elapsed: float) -> None:
    payload = {
        "request_id": state.request_id,
        "summary": {
            "termination_reason": state.status,
            "assistant_turns": sum(1 for message in state.messages if message.get("role") == "assistant"),
            "user_turns": sum(1 for message in state.messages if message.get("role") == "user"),
            "tool_call_count": sum(len(event.get("actions") or []) for event in state.events),
            "response_tokens": None,
            "elapsed_seconds": elapsed,
        },
        "rollout": {
            "label": state.rollout_label,
            "task_id": state.spec.task_id,
            "step": state.request.rollout_step,
            "sample_index": state.request.rollout_sample_index,
            "rollout_n": state.request.rollout_n,
        },
        "workspace": {
            "task_id": state.spec.task_id,
            "status": state.status,
            "result_dir": str(state.result_dir),
            "workspace_before": str(state.workspace_before),
            "workspace_after": str(state.workspace_after),
            "prompt_path": str(state.spec.prompt_path),
            "env_builder_path": str(state.spec.env_builder_path),
            "verifier_path": str(state.spec.verifier_path) if state.spec.verifier_path else None,
            "env_builder": state.env_result,
            "verifier": state.verifier_result,
        },
        "messages": truncate_text(state.messages),
        "events": truncate_text(state.events),
        "metrics": {},
        "tool_rewards": [],
    }
    (state.result_dir / "trajectory.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_summary(output_root: Path, results: list[dict[str, Any]], started_at: str) -> None:
    summary = {
        "started_at": started_at,
        "finished_at": utc_now(),
        "total": len(results),
        "completed": sum(1 for result in results if result.get("status") == "completed"),
        "failed": sum(1 for result in results if result.get("status") == "failed"),
        "skipped": sum(1 for result in results if result.get("status") == "skipped"),
        "samples": len(results),
        "results": results,
    }
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def iter_jsonl_results(results: Iterable[dict[str, Any]]) -> str:
    return "".join(json.dumps(result, ensure_ascii=False) + "\n" for result in results)
