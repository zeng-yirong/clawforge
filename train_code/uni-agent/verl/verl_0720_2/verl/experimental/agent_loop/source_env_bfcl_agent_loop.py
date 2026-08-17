"""BFCL-compatible SourceEnv agent loop.

This module deliberately leaves :mod:`source_env_agent_loop` unchanged.  It
reuses the same SourceEnv runtime and validation flow, but changes only the
model-facing tool-call protocol to the Qwen format used by the local BFCL
handler:

    <tool_call>
    {"name":"EnvironmentName.tool_name","arguments":{"parameter":"value"}}
    </tool_call>

For a normal answer, the model emits plain text and no ``<tool_call>`` tag.
"""

import copy
import json
import re
from dataclasses import dataclass
from typing import Any, Optional

from verl.experimental.agent_loop.agent_loop import register
from verl.experimental.agent_loop.source_env_agent_loop import (
    AgentData,
    AgentState,
    SourceEnvAgentLoop,
    strip_markdown,
    to_jsonable,
)
from verl.utils.profiler import simple_timer


# Keep the newline layout identical to BFCL's QwenFCHandler parser.  In
# particular, QwenFCHandler extracts ``<tool_call>\n...\n</tool_call>``.
BFCL_QWEN_TOOL_CALL_RE = re.compile(
    r"<tool_call>\n(.*?)\n</tool_call>", re.DOTALL
)


@dataclass(frozen=True)
class ToolBinding:
    """Maps the model-visible BFCL name back to a SourceEnv method."""

    env_name: str
    method_name: str
    parameter_order: tuple[str, ...]


@dataclass(frozen=True)
class BFCLToolCall:
    """A validated BFCL/Qwen textual tool call."""

    name: str
    arguments: dict[str, Any]


def parse_bfcl_qwen_response(
    text: str,
) -> tuple[list[BFCLToolCall], str, Optional[str]]:
    """Parse BFCL Qwen ``<tool_call>`` tags from a model response.

    Returns ``(tool_calls, remaining_content, error)``.  A response without a
    tool tag is a valid normal assistant answer.  Once a tool-call marker is
    present, however, every call must use the exact BFCL newline/tag layout and
    contain a JSON object with a string ``name`` and object ``arguments``.
    """

    cleaned = strip_markdown(text)
    has_tool_marker = "<tool_call" in cleaned.lower() or "</tool_call>" in cleaned.lower()
    raw_calls = BFCL_QWEN_TOOL_CALL_RE.findall(cleaned)

    if has_tool_marker and not raw_calls:
        return [], cleaned, "Malformed BFCL tool call; expected <tool_call>\\nJSON\\n</tool_call>."

    parsed_calls: list[BFCLToolCall] = []
    for raw_call in raw_calls:
        try:
            payload = json.loads(raw_call)
        except json.JSONDecodeError as exc:
            return [], cleaned, f"Tool call is not valid JSON: {exc}"

        if not isinstance(payload, dict):
            return [], cleaned, "Tool call JSON must be an object."

        name = payload.get("name")
        arguments = payload.get("arguments")
        if not isinstance(name, str) or not name:
            return [], cleaned, "Tool call must contain a non-empty string field 'name'."
        if not isinstance(arguments, dict):
            return [], cleaned, "Tool call field 'arguments' must be a JSON object."

        parsed_calls.append(BFCLToolCall(name=name, arguments=arguments))

    remaining_content = BFCL_QWEN_TOOL_CALL_RE.sub("", cleaned).strip()
    return parsed_calls, remaining_content, None


@register("source_env_bfcl_agent")
class SourceEnvBFCLAgentLoop(SourceEnvAgentLoop):
    """SourceEnv loop with BFCL-Qwen compatible tool calls.

    The legacy ``source_env_agent`` continues to use an outer JSON envelope
    and ``env['name'].method(...)`` strings.  This loop exposes fully
    qualified ``EnvironmentName.method_name`` tool names to the model, then
    maps them back to the legacy execution-trace form before validation.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._tool_registry: dict[str, ToolBinding] = {}

    @staticmethod
    def _build_tool_registry(
        env_names: list[str], tool_definitions: dict[str, list[dict[str, Any]]]
    ) -> tuple[list[dict[str, Any]], dict[str, ToolBinding]]:
        """Flatten tools and always namespace them by environment.

        The environment component is required even for a globally unique
        method.  It preserves the source of each call so that the structured
        BFCL action can be losslessly reconstructed as the legacy trace format
        required by existing validation scripts:

        ``HotelBookingSystem.get_room_details`` ->
        ``env['HotelBookingSystem'].get_room_details(...)``.
        """

        candidates: list[tuple[str, dict[str, Any], str]] = []
        for env_name in env_names:
            for tool in tool_definitions.get(env_name, []):
                if not isinstance(tool, dict) or not isinstance(tool.get("name"), str):
                    raise ValueError(f"Invalid tool definition for environment {env_name!r}: {tool!r}")
                method_name = tool["name"]
                candidates.append((env_name, tool, method_name))

        flattened_tools: list[dict[str, Any]] = []
        registry: dict[str, ToolBinding] = {}
        for env_name, tool, method_name in candidates:
            public_name = f"{env_name}.{method_name}"
            if public_name in registry:
                raise ValueError(
                    "Cannot construct an unambiguous BFCL tool name for "
                    f"{public_name!r}. Rename one of the source-environment tools."
                )

            # BFCL's tool schema contains name/description/parameters.  The
            # source-env-only response schema is intentionally not shown to the
            # model in this mode.
            public_tool = copy.deepcopy(tool)
            public_tool["name"] = public_name
            public_tool.pop("response", None)
            flattened_tools.append(public_tool)
            parameters = tool.get("parameters", {})
            properties = parameters.get("properties", {}) if isinstance(parameters, dict) else {}
            parameter_order = tuple(properties.keys()) if isinstance(properties, dict) else ()
            registry[public_name] = ToolBinding(
                env_name=env_name,
                method_name=method_name,
                parameter_order=parameter_order,
            )

        return flattened_tools, registry

    @staticmethod
    def _build_system_prompt(
        base_system_messages: list[str],
        env_names: list[str],
        env_descriptions: dict[str, dict[str, Any]],
        flattened_tools: list[dict[str, Any]],
    ) -> str:
        """Build the BFCL/Qwen-style system message used during training."""

        sections: list[str] = []
        existing_system = "\n\n".join(message for message in base_system_messages if message)
        if existing_system:
            sections.append(existing_system)

        selected_env_descriptions = {
            env_name: {
                "env_des": env_descriptions.get(env_name, {}).get("env_des", ""),
                "state_des": env_descriptions.get(env_name, {}).get("state_des", ""),
            }
            for env_name in env_names
        }
        if selected_env_descriptions:
            sections.append(
                "# Environment Descriptions\n\n"
                + json.dumps(to_jsonable(selected_env_descriptions), ensure_ascii=False, indent=2)
            )

        if flattened_tools:
            tool_docs = "\n".join(
                json.dumps(tool, ensure_ascii=False) for tool in flattened_tools
            )
            sections.append(
                "# Tools\n\n"
                "You may call one or more functions to assist with the user query. "
                "Use only the functions listed below. Do not invent function names, "
                "parameters, IDs, or state.\n\n"
                "You are provided with function signatures within <tools></tools> XML tags:\n"
                f"<tools>\n{tool_docs}\n</tools>\n\n"
                "For each function call, return a JSON object with function name and "
                "arguments within <tool_call></tool_call> XML tags. Return each call "
                "in exactly this form:\n"
                "<tool_call>\n"
                '{"name":"EnvironmentName.function_name","arguments":{"parameter":"value"}}\n'
                "</tool_call>\n\n"
                "Use JSON values inside arguments: strings use double quotes, booleans "
                "are true/false, and null is null. If multiple calls are needed, emit "
                "multiple <tool_call> blocks in execution order. Return only tool-call "
                "blocks when calling tools. Every listed function name includes its "
                "environment name (EnvironmentName.function_name); use that full name "
                "exactly.\n\n"
                "If no tool call is needed, respond directly with the normal assistant "
                "answer. Do not output a JSON envelope, need_tool_call, or a tool_call field."
            )
        else:
            sections.append(
                "No tools are available. Respond directly with the normal assistant answer."
            )

        return "\n\n".join(sections)

    def _prepare_initial_messages(
        self,
        raw_messages: list[dict[str, Any]],
        env_names: list[str],
        env_descriptions: dict[str, dict[str, Any]],
        tool_definitions: dict[str, list[dict[str, Any]]],
    ) -> list[dict[str, Any]]:
        flattened_tools, self._tool_registry = self._build_tool_registry(
            env_names, tool_definitions
        )

        original_messages = copy.deepcopy(raw_messages)
        base_system_messages = [
            str(message.get("content", ""))
            for message in original_messages
            if message.get("role") == "system"
        ]
        non_system_messages = [
            message for message in original_messages if message.get("role") != "system"
        ]
        system_prompt = self._build_system_prompt(
            base_system_messages,
            env_names,
            env_descriptions,
            flattened_tools,
        )
        return [{"role": "system", "content": system_prompt}, *non_system_messages]

    @staticmethod
    def _render_execution_trace(binding: ToolBinding, arguments: dict[str, Any]) -> str:
        """Map a structured BFCL call to the legacy validator trace shape.

        The parent ``run`` method passes ``agent_data.execution_trace`` to the
        existing validation script after the trajectory finishes.  Appending
        this converted representation at execution time guarantees that the
        validator continues to receive its immutable historical protocol.
        """

        # JSON object order from a model is not a stable validation contract.
        # Reconstruct the legacy call in the schema/signature order first,
        # then retain any invalid extra arguments at the end so execution and
        # validation still expose the model's actual mistake.
        ordered_keys = [key for key in binding.parameter_order if key in arguments]
        ordered_keys.extend(
            key for key in arguments if key not in binding.parameter_order
        )
        rendered_arguments = ", ".join(
            f"{key}={arguments[key]!r}" for key in ordered_keys
        )
        return f"env[{binding.env_name!r}].{binding.method_name}({rendered_arguments})"

    def _execute_tool_calls(
        self, agent_data: AgentData, tool_calls: list[BFCLToolCall]
    ) -> list[str]:
        """Execute structured model calls and return one raw result per call."""

        execution_results: list[str] = []
        for tool_call in tool_calls:
            binding = self._tool_registry.get(tool_call.name)
            if binding is None:
                execution_results.append(
                    json.dumps(
                        {"error": f"Unknown tool {tool_call.name!r}."}, ensure_ascii=False
                    )
                )
                continue

            trace_call = self._render_execution_trace(binding, tool_call.arguments)
            agent_data.execution_trace.append(trace_call)
            try:
                loaded_env = agent_data.runtime.envs[binding.env_name]
                method = getattr(loaded_env.instance, binding.method_name)
                result = method(**tool_call.arguments)
                execution_results.append(json.dumps(to_jsonable(result), ensure_ascii=False))
            except Exception as exc:
                execution_results.append(json.dumps({"error": str(exc)}, ensure_ascii=False))

        return execution_results

    async def _handle_generating_state(
        self, agent_data: AgentData, sampling_params: dict[str, Any]
    ) -> AgentState:
        """Generate once, then branch on BFCL tool tags or a direct answer."""

        if self.max_agent_turns and agent_data.agent_turns >= self.max_agent_turns:
            for message in reversed(agent_data.messages):
                if message.get("role") == "assistant":
                    agent_data.final_response = str(message.get("content", "")).strip()
                    break
            else:
                agent_data.final_response = ""
            agent_data.status = "max_agent_turns_reached"
            return AgentState.TERMINATED

        current_prompt_len = len(agent_data.prompt_ids)
        if current_prompt_len >= self.response_length:
            agent_data.status = "prompt_length_exceeded"
            agent_data.final_response = (
                agent_data.messages[-1].get("content", "") if agent_data.messages else ""
            )
            return AgentState.TERMINATED

        sampling_params = dict(sampling_params)
        sampling_params.setdefault("max_tokens", self.response_length - current_prompt_len)
        sampling_params["max_tokens"] = max(1, sampling_params["max_tokens"])
        with simple_timer("generate_sequences", agent_data.metrics):
            output = await self.server_manager.generate(
                request_id=agent_data.request_id,
                prompt_ids=agent_data.prompt_ids,
                sampling_params=sampling_params,
                image_data=agent_data.image_data,
                video_data=agent_data.video_data,
            )

        agent_data.agent_turns += 1
        agent_data.response_ids = output.token_ids
        agent_data.prompt_ids += agent_data.response_ids
        agent_data.response_mask += [1] * len(agent_data.response_ids)
        if output.log_probs:
            agent_data.response_logprobs += output.log_probs

        assistant_message = await self.loop.run_in_executor(
            None,
            lambda: self.tokenizer.decode(agent_data.response_ids, skip_special_tokens=True),
        )
        agent_data.messages.append({"role": "assistant", "content": assistant_message})

        if len(agent_data.response_mask) >= self.response_length:
            agent_data.final_response = assistant_message.strip()
            agent_data.status = "response_length_reached"
            return AgentState.TERMINATED
        if self.max_user_turns and agent_data.next_step_index > self.max_user_turns:
            agent_data.final_response = assistant_message.strip()
            agent_data.status = "max_user_turns_reached"
            return AgentState.TERMINATED

        tool_calls, remaining_content, parse_error = parse_bfcl_qwen_response(assistant_message)
        if parse_error:
            agent_data.error = f"invalid_bfcl_tool_format: {parse_error}"
            agent_data.final_response = assistant_message.strip()
            agent_data.status = "invalid_format"
            return AgentState.TERMINATED

        if tool_calls:
            unknown_tools = [call.name for call in tool_calls if call.name not in self._tool_registry]
            if unknown_tools:
                agent_data.error = f"unknown_tool: {unknown_tools}"
                agent_data.final_response = assistant_message.strip()
                agent_data.status = "invalid_tool"
                return AgentState.TERMINATED
            agent_data.pending_tool_calls = tool_calls
            return AgentState.PROCESSING_TOOLS

        # BFCL convention: the absence of a tool-call tag is a normal assistant
        # answer, not a JSON-format error.
        agent_data.final_response = remaining_content or assistant_message.strip()
        if agent_data.next_step_index < len(agent_data.user_plan):
            return AgentState.APPENDING_USER_STEP
        agent_data.status = "done"
        return AgentState.TERMINATED

    async def _handle_processing_tools_state(self, agent_data: AgentData) -> AgentState:
        """Append raw execution results as tool messages, like BFCL Qwen FC."""

        with simple_timer("tool_calls", agent_data.metrics):
            execution_results = self._execute_tool_calls(
                agent_data, agent_data.pending_tool_calls
            )

        add_messages = [
            {"role": "tool", "content": execution_result}
            for execution_result in execution_results
        ]
        appended = await self._append_messages_to_prompt(
            agent_data, add_messages, mask_value=0
        )
        if not appended:
            agent_data.status = "response_length_reached"
            return AgentState.TERMINATED
        return AgentState.GENERATING


