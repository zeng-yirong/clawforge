# Copyright 2025 Bytedance Ltd. and/or its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Nanoclaw-specific rollout metadata, trajectory persistence, and behavior masking."""

import copy
import json
import os
import re
import time
from pathlib import Path
from typing import Any


def inject_nanoclaw_trajectory(tools_kwargs: dict[str, Any], trajectory: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(tools_kwargs, dict):
        return tools_kwargs

    trajectory_metadata = {
        "rollout_step": trajectory.get("step"),
        "rollout_sample_index": trajectory.get("sample_index"),
        "rollout_n": trajectory.get("rollout_n"),
        "validate": trajectory.get("validate"),
    }
    for tool_kwargs in tools_kwargs.values():
        if not isinstance(tool_kwargs, dict):
            continue
        containers = [tool_kwargs]
        create_kwargs = tool_kwargs.get("create_kwargs")
        if isinstance(create_kwargs, dict):
            containers.append(create_kwargs)
        for container in containers:
            task_config = container.get("nanoclaw")
            if isinstance(task_config, dict):
                task_config.update(trajectory_metadata)
    return tools_kwargs


def safe_json_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): safe_json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [safe_json_value(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return repr(value)


def truncate_text(value: Any, limit: int = 20000) -> Any:
    if isinstance(value, str):
        return value if len(value) <= limit else value[:limit] + f"...(truncated {len(value) - limit} chars)"
    if isinstance(value, dict):
        return {key: truncate_text(item, limit=limit) for key, item in value.items()}
    if isinstance(value, list):
        return [truncate_text(item, limit=limit) for item in value]
    return value


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def nanoclaw_rollout_info(agent_data: "AgentData", nanoclaw_state: dict[str, Any]) -> dict[str, Any]:
    return {
        "label": agent_data.extra_fields.get("rollout_label"),
        "task_id": agent_data.extra_fields.get("rollout_task_id") or nanoclaw_state.get("task_id"),
        "step": agent_data.extra_fields.get("rollout_step") or nanoclaw_state.get("rollout_step"),
        "sample_index": agent_data.extra_fields.get("rollout_sample_index")
        if agent_data.extra_fields.get("rollout_sample_index") is not None
        else nanoclaw_state.get("rollout_sample_index"),
        "rollout_n": agent_data.extra_fields.get("rollout_n")
        if agent_data.extra_fields.get("rollout_n") is not None
        else nanoclaw_state.get("rollout_n"),
    }


def build_nanoclaw_conversation_messages(agent_data: "AgentData") -> list[dict[str, Any]]:
    messages: list[dict[str, Any]] = []
    for message in agent_data.messages:
        if message.get("role") in {"assistant", "tool"}:
            break
        messages.append(copy.deepcopy(message))

    for event in agent_data.trajectory_events:
        if not isinstance(event, dict):
            continue
        event_type = event.get("type")
        if event_type == "assistant":
            messages.append({"role": "assistant", "content": event.get("content") or ""})
        elif event_type == "tool":
            response = event.get("response")
            if isinstance(response, dict):
                tool_message = copy.deepcopy(response)
                tool_message.setdefault("role", "tool")
            else:
                tool_message = {"role": "tool", "content": response or ""}
            if event.get("tool") is not None and "name" not in tool_message:
                tool_message["name"] = str(event.get("tool"))
            messages.append(tool_message)

    return messages or copy.deepcopy(agent_data.messages)


def nanoclaw_final_answer(agent_data: "AgentData") -> str | None:
    if agent_data.termination_reason != "completed_no_tool_call":
        return None
    for event in reversed(agent_data.trajectory_events):
        if isinstance(event, dict) and event.get("type") == "assistant":
            content = event.get("content")
            return content if isinstance(content, str) else None
    return None


def bool_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def int_env(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return default


def nanoclaw_canonical_json_key(value: Any) -> str:
    try:
        return json.dumps(safe_json_value(value), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    except (TypeError, ValueError):
        return repr(value)


def nanoclaw_assistant_turn_spans(agent_data: "AgentData") -> dict[int, tuple[int, int]]:
    spans: dict[int, tuple[int, int]] = {}
    for event in agent_data.trajectory_events:
        if not isinstance(event, dict) or event.get("type") != "assistant":
            continue
        assistant_turn = event.get("assistant_turn")
        start = event.get("response_start")
        end = event.get("response_end")
        if isinstance(assistant_turn, int) and isinstance(start, int) and isinstance(end, int) and end > start:
            spans[assistant_turn] = (start, end)
    return spans


def nanoclaw_record_bad_turn_span(
    agent_data: "AgentData",
    assistant_turn: int,
    reason: str,
    start: int,
    end: int,
) -> None:
    end = min(end, len(agent_data.response_mask))
    if end <= start:
        return
    bad_turn_spans = agent_data.extra_fields.setdefault("nanoclaw_bad_turn_spans", [])
    if not isinstance(bad_turn_spans, list):
        bad_turn_spans = []
        agent_data.extra_fields["nanoclaw_bad_turn_spans"] = bad_turn_spans
    for item in bad_turn_spans:
        if (
            isinstance(item, dict)
            and item.get("assistant_turn") == assistant_turn
            and item.get("reason") == reason
            and item.get("start") == start
            and item.get("end") == end
        ):
            return
    token_count = sum(1 for token in agent_data.response_mask[start:end] if token)
    bad_turn_spans.append(
        {
            "assistant_turn": assistant_turn,
            "reason": reason,
            "start": start,
            "end": end,
            "token_count": token_count,
        }
    )
    metric_prefix = f"nanoclaw_{reason}"
    agent_data.metrics[f"{metric_prefix}_candidate_turns"] = agent_data.metrics.get(f"{metric_prefix}_candidate_turns", 0) + 1
    agent_data.metrics[f"{metric_prefix}_candidate_tokens"] = (
        agent_data.metrics.get(f"{metric_prefix}_candidate_tokens", 0) + token_count
    )
    agent_data.metrics["nanoclaw_bad_turn_candidate_turns"] = agent_data.metrics.get("nanoclaw_bad_turn_candidate_turns", 0) + 1
    agent_data.metrics["nanoclaw_bad_turn_candidate_tokens"] = (
        agent_data.metrics.get("nanoclaw_bad_turn_candidate_tokens", 0) + token_count
    )
    for event in agent_data.trajectory_events:
        if isinstance(event, dict) and event.get("type") == "assistant" and event.get("assistant_turn") == assistant_turn:
            reasons = event.setdefault("bad_turn_candidate_reasons", [])
            if isinstance(reasons, list) and reason not in reasons:
                reasons.append(reason)
            event["bad_turn_candidate"] = True
            break


def nanoclaw_mask_assistant_turn(
    agent_data: "AgentData",
    assistant_turn: int,
    reason: str,
    spans: dict[int, tuple[int, int]],
    masked_turns: set[int],
) -> None:
    span = spans.get(assistant_turn)
    if span is None or assistant_turn in masked_turns:
        return
    start, end = span
    end = min(end, len(agent_data.response_mask))
    if end <= start:
        return
    if bool_env("NANOCLAW_MASK_ONLY_POSITIVE_ADVANTAGE", False):
        nanoclaw_record_bad_turn_span(agent_data, assistant_turn, reason, start, end)
        masked_turns.add(assistant_turn)
        return
    token_count = sum(1 for token in agent_data.response_mask[start:end] if token)
    agent_data.response_mask[start:end] = [0] * (end - start)
    masked_turns.add(assistant_turn)
    metric_prefix = f"nanoclaw_{reason}"
    agent_data.metrics[f"{metric_prefix}_masked_turns"] = agent_data.metrics.get(f"{metric_prefix}_masked_turns", 0) + 1
    agent_data.metrics[f"{metric_prefix}_masked_tokens"] = (
        agent_data.metrics.get(f"{metric_prefix}_masked_tokens", 0) + token_count
    )
    agent_data.metrics["nanoclaw_posthoc_masked_turns"] = agent_data.metrics.get("nanoclaw_posthoc_masked_turns", 0) + 1
    agent_data.metrics["nanoclaw_posthoc_masked_tokens"] = (
        agent_data.metrics.get("nanoclaw_posthoc_masked_tokens", 0) + token_count
    )
    for event in agent_data.trajectory_events:
        if isinstance(event, dict) and event.get("type") == "assistant" and event.get("assistant_turn") == assistant_turn:
            reasons = event.setdefault("posthoc_mask_reasons", [])
            if isinstance(reasons, list) and reason not in reasons:
                reasons.append(reason)
            event["posthoc_masked"] = True
            break


def nanoclaw_apply_posthoc_turn_masks(agent_data: "AgentData") -> None:
    spans = nanoclaw_assistant_turn_spans(agent_data)
    if not spans:
        return
    masked_turns: set[int] = set()

    if bool_env("NANOCLAW_MASK_BUDGET_EXHAUSTED_LAST_TURN", False) and agent_data.termination_reason in {
        "max_assistant_response_tokens",
        "max_response_tokens",
    }:
        for event in reversed(agent_data.trajectory_events):
            if isinstance(event, dict) and event.get("type") == "assistant":
                assistant_turn = event.get("assistant_turn")
                if isinstance(assistant_turn, int):
                    nanoclaw_mask_assistant_turn(
                        agent_data,
                        assistant_turn,
                        "budget_exhausted_last_turn",
                        spans,
                        masked_turns,
                    )
                break

    if bool_env("NANOCLAW_MASK_DUPLICATE_TOOL_RESULT_TURNS", False):
        seen_tool_results: set[str] = set()
        for event in agent_data.trajectory_events:
            if not isinstance(event, dict) or event.get("type") != "tool":
                continue
            key = nanoclaw_canonical_json_key(
                {
                    "tool": event.get("tool"),
                    "arguments": event.get("arguments"),
                    "response": event.get("response"),
                    "result": event.get("result"),
                }
            )
            if key not in seen_tool_results:
                seen_tool_results.add(key)
                continue
            assistant_turn = event.get("assistant_turn")
            if isinstance(assistant_turn, int):
                event["duplicate_tool_result"] = True
                nanoclaw_mask_assistant_turn(
                    agent_data,
                    assistant_turn,
                    "duplicate_tool_result_turn",
                    spans,
                    masked_turns,
                )


def normalized_loop_text(text: Any) -> str:
    value = str(text or "").replace("\r\n", "\n").replace("\r", "\n")
    value = re.sub(r"[ \t]+", " ", value)
    value = re.sub(r"\n[ \t]+", "\n", value)
    return value.strip()


def consecutive_loop_chunks(chunks: list[str], min_chars: int) -> int:
    extra_repeats = 0
    chunk_index = 0
    while chunk_index < len(chunks):
        current_chunk = chunks[chunk_index]
        if len(current_chunk) < min_chars:
            chunk_index += 1
            continue
        run_length = 1
        next_index = chunk_index + 1
        while next_index < len(chunks) and chunks[next_index] == current_chunk:
            run_length += 1
            next_index += 1
        if run_length > 1:
            extra_repeats += run_length - 1
        chunk_index = next_index
    return extra_repeats


def continuous_separator_loop_count(text: str, min_chars: int) -> int:
    for separator in ("</think>", "\n\n", "\n"):
        if separator not in text:
            continue
        chunks = [normalized_loop_text(part) for part in text.split(separator)]
        chunks = [chunk for chunk in chunks if chunk]
        extra_repeats = consecutive_loop_chunks(chunks, min_chars)
        if extra_repeats:
            return extra_repeats
    return 0


def continuous_token_loop_count(text: str, min_chars: int, max_unit_tokens: int = 512) -> int:
    token_matches = list(re.finditer(r"\S+", text))
    token_count = len(token_matches)
    if token_count < 2:
        return 0
    tokens = [match.group(0) for match in token_matches]
    max_unit_tokens = min(max_unit_tokens, token_count // 2)
    best_extra_repeats = 0
    for unit_token_count in range(1, max_unit_tokens + 1):
        start_token_index = 0
        while start_token_index + 2 * unit_token_count <= token_count:
            unit_start_char = token_matches[start_token_index].start()
            unit_end_char = token_matches[start_token_index + unit_token_count - 1].end()
            if unit_end_char - unit_start_char < min_chars:
                start_token_index += 1
                continue
            first_unit = tokens[start_token_index : start_token_index + unit_token_count]
            next_start = start_token_index + unit_token_count
            if first_unit != tokens[next_start : next_start + unit_token_count]:
                start_token_index += 1
                continue
            run_length = 2
            next_start += unit_token_count
            while next_start + unit_token_count <= token_count and first_unit == tokens[next_start : next_start + unit_token_count]:
                run_length += 1
                next_start += unit_token_count
            best_extra_repeats = max(best_extra_repeats, run_length - 1)
            start_token_index += run_length * unit_token_count
    return best_extra_repeats


def nanoclaw_looping_response_repeat_count(text: Any, min_chars: int, min_consecutive_repeats: int = 2) -> int:
    normalized = normalized_loop_text(text)
    min_consecutive_repeats = max(2, min_consecutive_repeats)
    if len(normalized) < min_chars * min_consecutive_repeats:
        return 0
    separator_repeats = continuous_separator_loop_count(normalized, min_chars)
    if separator_repeats >= min_consecutive_repeats - 1:
        return separator_repeats
    token_repeats = continuous_token_loop_count(normalized, min_chars)
    return token_repeats if token_repeats >= min_consecutive_repeats - 1 else 0


def nanoclaw_history_status(termination_reason: str) -> str:
    if termination_reason == "completed_no_tool_call":
        return "completed"
    if termination_reason in {
        "max_response_tokens",
        "max_response_tokens_after_tool",
        "max_assistant_response_tokens",
        "max_assistant_turns",
        "max_user_turns",
    }:
        return "failed"
    return termination_reason or "unknown"


def write_nanoclaw_conversation_history(
    agent_data: "AgentData",
    *,
    nanoclaw_state: dict[str, Any],
    rollout: dict[str, Any],
    elapsed: float,
    path: Path,
) -> None:
    payload = {
        "task_id": rollout.get("task_id"),
        "rollout_label": rollout.get("label"),
        "rollout_step": rollout.get("step"),
        "rollout_sample_index": rollout.get("sample_index"),
        "rollout_n": rollout.get("rollout_n"),
        "status": nanoclaw_history_status(agent_data.termination_reason),
        "termination_reason": agent_data.termination_reason,
        "final_answer": nanoclaw_final_answer(agent_data),
        "error": None,
        "started_at": nanoclaw_state.get("created_at"),
        "updated_at": utc_now(),
        "steps_used": agent_data.assistant_turns,
        "assistant_turns": agent_data.assistant_turns,
        "user_turns": agent_data.user_turns,
        "tool_call_count": agent_data.tool_call_count,
        "response_tokens": len(agent_data.response_mask),
        "elapsed_seconds": elapsed,
        "messages": safe_json_value(build_nanoclaw_conversation_messages(agent_data)),
        "events": safe_json_value(agent_data.trajectory_events),
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_nanoclaw_trajectory(agent_data: "AgentData", *, elapsed: float) -> None:
    nanoclaw_state = agent_data.extra_fields.get("nanoclaw") if isinstance(agent_data.extra_fields, dict) else None
    if not isinstance(nanoclaw_state, dict) or not nanoclaw_state.get("result_dir"):
        return
    result_dir = Path(str(nanoclaw_state["result_dir"]))
    rollout = nanoclaw_rollout_info(agent_data, nanoclaw_state)
    conversation_history_path = result_dir / "conversation_history.json"
    workspace = safe_json_value(nanoclaw_state)
    if isinstance(workspace, dict):
        workspace["conversation_history"] = str(conversation_history_path)
    payload = {
        "request_id": agent_data.request_id,
        "summary": {
            "termination_reason": agent_data.termination_reason,
            "assistant_turns": agent_data.assistant_turns,
            "user_turns": agent_data.user_turns,
            "tool_call_count": agent_data.tool_call_count,
            "response_tokens": len(agent_data.response_mask),
            "elapsed_seconds": elapsed,
        },
        "rollout": rollout,
        "workspace": workspace,
        "messages": truncate_text(safe_json_value(agent_data.messages)),
        "events": truncate_text(safe_json_value(agent_data.trajectory_events)),
        "metrics": safe_json_value(agent_data.metrics),
        "tool_rewards": safe_json_value(agent_data.tool_rewards),
    }
    (result_dir / "trajectory.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_nanoclaw_conversation_history(
        agent_data,
        nanoclaw_state=nanoclaw_state,
        rollout=rollout,
        elapsed=elapsed,
        path=conversation_history_path,
    )
