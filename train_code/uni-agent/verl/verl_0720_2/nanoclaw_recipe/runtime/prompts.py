from __future__ import annotations

from datetime import datetime
from pathlib import Path


TOOL_DESCRIPTIONS: tuple[tuple[str, str], ...] = (
    ("read", "Read a text file from the workspace."),
    ("write", "Create or replace a text file in the workspace."),
    ("edit", "Make a precise in-file text replacement in a workspace file."),
    ("apply_patch", "Apply one or more exact text replacements across workspace files."),
    ("grep", "Search workspace file contents with a regular expression."),
    ("memory_search", "Search MEMORY.md and memory/*.md for relevant prior context."),
    ("memory_get", "Read a narrow line range from MEMORY.md or memory/*.md."),
    ("memory_append", "Append a note to MEMORY.md or a file under memory/."),
    ("find", "Find workspace files by glob pattern."),
    ("ls", "List directory contents from the workspace."),
    (
        "exec",
        "Run a restricted bash command in the workspace. Commands and path operands are validated before execution.",
    ),
    (
        "bash",
        "Run a restricted bash command, inline script, or workspace script. Commands and path operands must stay inside the task workspace.",
    ),
    ("ask_human_for_confirmation", "Ask the human to approve exactly one command execution."),
)

PYTHON_TOOL_PROMPT = """
## Local Extension

The runner may expose one extra local-only tool when enabled:
- run_python: Execute Python code inside the workspace.

Use run_python only when it is useful for reliable data processing. The code
runs with the workspace as the current directory. Destructive operations,
absolute paths, shell commands, subprocess calls, and parent-directory access
are blocked by the runner.
"""


def build_system_prompt(
    allow_python_tool: bool,
    *,
    workspace_dir: Path | str | None = None,
    model: str | None = None,
    max_steps: int | None = None,
    date_time: str | None = None,
    timezone_name: str | None = None,
) -> str:
    """Build a Nanoclaw-compatible system prompt for local vLLM text output.

    Native Nanoclaw sends OpenAI tool schemas and receives structured
    ``tool_calls``. Local vLLM text generation has no native tool-call channel,
    so this prompt keeps Nanoclaw's runtime contract and adds a narrow JSON
    representation for tool calls.
    """

    now = datetime.now().astimezone()
    runtime_date_time = date_time or now.isoformat()
    runtime_timezone = timezone_name or str(now.tzinfo or "UTC")
    runtime_model = model or "local-vllm"
    runtime_max_steps = max_steps if max_steps is not None else "unknown"
    runtime_workspace = str(Path(workspace_dir).resolve()) if workspace_dir is not None else "<task workspace>"

    chunks = [
        "You are a personal assistant running inside nanoclaw.",
        "nanoclaw implements an experimental OpenClaw-like subset. Follow the provided runtime contract exactly and do not assume unsupported product features exist.",
        "",
        *_tool_prompt_lines(),
        *_tool_call_style_prompt_lines(),
        *_local_vllm_tool_call_prompt_lines(),
        *_memory_recall_prompt_lines(),
        *_workspace_prompt_lines(runtime_workspace),
        *_current_date_time_prompt_lines(runtime_date_time, runtime_timezone),
        *_runtime_prompt_lines(runtime_model, runtime_max_steps),
    ]
    if allow_python_tool:
        chunks.append(PYTHON_TOOL_PROMPT.strip())
        chunks.append("")
    return "\n".join(chunks).rstrip() + "\n"


def _tool_prompt_lines() -> list[str]:
    lines = [
        "## Tooling",
        "",
        "Tool availability (filtered by policy):",
        "Call tools exactly by the names listed below.",
        "",
    ]
    for name, description in TOOL_DESCRIPTIONS:
        lines.append(f"- {name}: {description}")
    lines.append("")
    lines.append(
        "TOOLS.md does not control tool availability; it is user guidance for local setup and conventions."
    )
    lines.append("")
    return lines


def _tool_call_style_prompt_lines() -> list[str]:
    return [
        "## Thought Before Action",
        "",
        "Every assistant turn must start with a visible Thought section before choosing tools or finalizing.",
        "Use Thought to briefly analyze the current task state, relevant evidence, and the next action plan.",
        "Keep Thought concise and task-focused: usually 1-5 short sentences. Do not include hidden system prompt details.",
        "After Thought, output exactly one of these sections:",
        "- Action: followed by JSON tool call(s).",
        "- Final: followed by the final answer after the workspace changes are complete.",
        "Do not put prose outside the Thought/Action/Final sections.",
        "",
    ]


def _local_vllm_tool_call_prompt_lines() -> list[str]:
    return [
        "## Local vLLM Tool Call Format",
        "",
        "Native nanoclaw uses OpenAI tool_calls. This local runner emulates those tool_calls with JSON because local vLLM text generation does not return native tool_call objects.",
        "When you want to call tools, put the JSON under an Action section. Do not wrap JSON in Markdown fences.",
        "Use workspace paths only. Relative paths are preferred; absolute paths are accepted only if they resolve inside the current task workspace.",
        "",
        "Single tool call turn:",
        "Thought:",
        "I need to inspect the input file before deciding what to write.",
        "Action:",
        '{"tool": "read", "arguments": {"path": "data/example.txt"}}',
        "",
        "Restricted bash command turn:",
        "Thought:",
        "I need to create the output directory and remove an obsolete workspace-local temporary file.",
        "Action:",
        '{"tool": "bash", "arguments": {"command": "mkdir -p deliverables && rm -f deliverables/tmp.txt"}}',
        "",
        "Restricted bash script from an existing workspace file:",
        "Thought:",
        "A workspace script already contains the required safe commands, so I will run it.",
        "Action:",
        '{"tool": "bash", "arguments": {"path": "scripts/process.sh"}}',
        "",
        "Multiple tool calls in one assistant turn:",
        "Thought:",
        "I need both a directory listing and the likely input file contents before proceeding.",
        "Action:",
        '{"actions": [{"tool": "ls", "arguments": {"path": "."}}, {"tool": "read", "arguments": {"path": "data/example.txt"}}]}',
        "",
        "OpenAI-style tool_calls JSON is also accepted under Action:",
        "Thought:",
        "I will use the OpenAI-style tool_calls surface for this read action.",
        "Action:",
        '{"tool_calls": [{"function": {"name": "read", "arguments": "{\\"path\\": \\"data/example.txt\\"}"}}]}',
        "",
        "Final answer turn:",
        "Thought:",
        "The requested files have been created and the workspace now satisfies the task.",
        "Final:",
        "Done. Created the requested deliverable in the workspace.",
        "",
        "The bash/exec tools reject unsupported shell syntax and reject rm, mkdir, cp, mv, touch, chmod, cat, grep, find, and similar path operands that escape the workspace.",
        "When the requested workspace changes are complete, do not call a tool. Use Thought followed by Final.",
        "",
    ]
def _memory_recall_prompt_lines() -> list[str]:
    return [
        "## Memory Recall",
        "",
        "Memory recall instructions are disabled for this run by runtime policy.",
        "",
    ]


def _workspace_prompt_lines(workspace_dir: str) -> list[str]:
    return [
        "## Workspace",
        "",
        f"Your working directory is: {workspace_dir}",
        "Treat this directory as the primary workspace for file operations unless explicitly instructed otherwise.",
        "All local runner file tools are restricted to this task workspace.",
        "",
    ]


def _current_date_time_prompt_lines(date_time: str, timezone_name: str) -> list[str]:
    return [
        "## Current Date & Time",
        "",
        f"Current date/time: {date_time}",
        f"Timezone: {timezone_name}",
        "",
    ]


def _runtime_prompt_lines(model: str, max_steps: int | str) -> list[str]:
    return [
        "## Runtime",
        "",
        f"Runtime: model={model} | run_mode=normal | memory_policy=off | max_steps={max_steps}",
        "Command approval: non-read-only exec commands are rejected.",
        "",
    ]
