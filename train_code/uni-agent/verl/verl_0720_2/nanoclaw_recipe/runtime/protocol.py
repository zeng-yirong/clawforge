from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any


SECTION_MARKER_RE = re.compile(r"(?im)^[ \t]*(thought|action|final(?: answer)?)\s*:\s*")


@dataclass(frozen=True, slots=True)
class ParsedModelReply:
    thought: str | None
    actions: list[dict[str, Any]] | None = None
    final_answer: str | None = None

    @property
    def is_final(self) -> bool:
        return self.final_answer is not None


def parse_model_reply(text: str) -> ParsedModelReply:
    """Parse a model turn using the visible Thought + Action/Final protocol.

    Preferred formats::

        Thought:
        ...
        Action:
        {"tool": "read", "arguments": {"path": "data/a.txt"}}

        Thought:
        ...
        Final:
        Done.

    The legacy JSON-only tool-call format is still accepted for compatibility.
    """

    action_match = find_section_marker(text, {"action"})
    if action_match is not None:
        action_text = text[action_match.end() :].strip()
        actions = extract_tool_actions(action_text)
        return ParsedModelReply(thought=extract_thought(text, stop_match=action_match), actions=actions)

    final_match = find_section_marker(text, {"final", "final answer"})
    if final_match is not None:
        final_answer = text[final_match.end() :].strip()
        if not final_answer:
            raise ValueError("Final section is empty")
        return ParsedModelReply(
            thought=extract_thought(text, stop_match=final_match),
            final_answer=final_answer,
        )

    try:
        return ParsedModelReply(thought=extract_prefix_thought(text), actions=extract_tool_actions(text))
    except ValueError:
        if is_plain_final_text(text):
            return ParsedModelReply(thought=None, final_answer=text.strip())
        raise


def find_section_marker(text: str, names: set[str]) -> re.Match[str] | None:
    normalized_names = {name.lower() for name in names}
    for match in SECTION_MARKER_RE.finditer(text):
        if match.group(1).lower() in normalized_names:
            return match
    return None


def extract_thought(text: str, *, stop_match: re.Match[str] | None) -> str | None:
    thought_match = find_section_marker(text, {"thought"})
    if thought_match is not None:
        end = stop_match.start() if stop_match is not None and stop_match.start() > thought_match.end() else len(text)
        thought = text[thought_match.end() : end].strip()
        return thought or None

    if stop_match is not None:
        prefix = text[: stop_match.start()].strip()
        return prefix or None
    return None


def extract_prefix_thought(text: str) -> str | None:
    json_start = find_first_json_start(text)
    if json_start is None:
        return None
    prefix = text[:json_start].strip()
    return prefix or None


def is_plain_final_text(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return False
    if stripped.startswith("```"):
        return False
    return stripped[0] not in "[{"


def extract_tool_actions(text: str) -> list[dict[str, Any]]:
    parsed = extract_json_value(text)
    if isinstance(parsed, dict):
        if "actions" in parsed:
            raw_actions = parsed["actions"]
        elif "tool_calls" in parsed:
            raw_actions = parsed["tool_calls"]
        else:
            raw_actions = [parsed]
    elif isinstance(parsed, list):
        raw_actions = parsed
    else:
        raise ValueError("tool call JSON must be an object or array")

    if not isinstance(raw_actions, list) or not raw_actions:
        raise ValueError("actions must be a non-empty array")

    actions: list[dict[str, Any]] = []
    for index, raw_action in enumerate(raw_actions, start=1):
        if not isinstance(raw_action, dict):
            raise ValueError(f"action #{index} must be an object")
        actions.append(normalize_tool_action(raw_action))
    return actions


def normalize_tool_action(raw_action: dict[str, Any]) -> dict[str, Any]:
    if "function" in raw_action and isinstance(raw_action["function"], dict):
        function = raw_action["function"]
        return normalize_named_tool_action(function.get("name"), function.get("arguments", {}))
    if "tool" in raw_action or "name" in raw_action:
        return normalize_named_tool_action(
            raw_action.get("tool", raw_action.get("name")),
            raw_action.get("arguments", {}),
        )
    if "action" in raw_action:
        return dict(raw_action)
    raise ValueError("action object must contain 'tool', 'name', 'function', or 'action'")


def normalize_named_tool_action(name: Any, arguments: Any) -> dict[str, Any]:
    if not isinstance(name, str) or not name.strip():
        raise ValueError("tool name must be a non-empty string")
    if isinstance(arguments, str):
        try:
            arguments = json.loads(arguments) if arguments.strip() else {}
        except json.JSONDecodeError as exc:
            raise ValueError(f"tool arguments are not valid JSON: {exc}") from exc
    if arguments is None:
        arguments = {}
    if not isinstance(arguments, dict):
        raise ValueError("tool arguments must be an object")
    action = dict(arguments)
    action["action"] = name.strip()
    return action


def extract_json_value(text: str) -> Any:
    stripped = strip_code_fence(text.strip())
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        return json.loads(find_first_json_value(stripped))


def strip_code_fence(text: str) -> str:
    if not text.startswith("```"):
        return text
    lines = text.splitlines()
    if len(lines) >= 3 and lines[-1].strip() == "```":
        return "\n".join(lines[1:-1]).strip()
    return text


def find_first_json_start(text: str) -> int | None:
    object_start = text.find("{")
    array_start = text.find("[")
    starts = [index for index in (object_start, array_start) if index != -1]
    return min(starts) if starts else None


def find_first_json_value(text: str) -> str:
    start = find_first_json_start(text)
    if start is None:
        raise ValueError("no JSON object or array found")
    opening = text[start]
    closing = "}" if opening == "{" else "]"

    depth = 0
    in_string = False
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
        elif char == opening:
            depth += 1
        elif char == closing:
            depth -= 1
            if depth == 0:
                return text[start : index + 1]
    raise ValueError("unterminated JSON value")
