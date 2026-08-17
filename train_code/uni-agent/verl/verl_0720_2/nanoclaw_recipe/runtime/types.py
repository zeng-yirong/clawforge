from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class TaskSpec:
    task_id: str
    task_dir: Path
    prompt_path: Path
    env_builder_path: Path
    verifier_path: Path | None
    base_tasks: Path | None = None
    input_layout: str = "legacy"
    manifest_path: Path | None = None


@dataclass(frozen=True, slots=True)
class TaskRunRequest:
    spec: TaskSpec
    rollout_step: int = 1
    rollout_sample_index: int = 0
    rollout_n: int = 0


@dataclass(frozen=True, slots=True)
class ToolResult:
    observation: str
    is_final: bool = False
    final_answer: str | None = None


@dataclass(slots=True)
class TaskRunState:
    spec: TaskSpec
    request: TaskRunRequest
    request_id: str
    rollout_label: str
    result_dir: Path
    workspace_before: Path
    workspace_after: Path
    history_path: Path
    metadata_path: Path
    prompt_text: str
    env_result: dict[str, Any]
    started_at: str
    started_time: float
    messages: list[dict[str, str]] = field(default_factory=list)
    events: list[dict[str, Any]] = field(default_factory=list)
    status: str = "running"
    error: str | None = None
    final_answer: str | None = None
    steps_used: int = 0
    verifier_result: dict[str, Any] | None = None
