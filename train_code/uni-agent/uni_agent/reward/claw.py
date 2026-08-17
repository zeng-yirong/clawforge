"""Reward spec for the ``claw_envs`` WORKPLACE training tasks.

Training data follows the four-file WORKPLACE paradigm (see
``claw_envs/claw_chains/gen_claw_workplace_tasks.py``):

    tasks/prompts/{id}.md              user-voice script (no solution steps)
    tasks/{id}/env_builder.py          builds the initial workspace file tree
    scripts/{id}/verify_workplace.py   CODE-ONLY scorer -> workplace_score.json

The verifier always scores files in a WORKPLACE directory. A rollout may also
prepare a matching claw CLI session so the agent can query or act on the
environment through ``execute_bash``, but the reward still comes from the
per-task ``verify_workplace.py`` supplied by the training row. It must not call
an environment package ``evaluator.py``.

Runtime setup (done in the loop's ``post_setup_cmd``, built by the native
dataset or preprocessing script):

1. ``export CLAW_WORKSPACE="$(mktemp -d ...)"`` -- a unique workspace per
   rollout (no cross-rollout collisions on the shared host).
2. copy the task's ``env_builder.py`` into it, ``cd`` there, run it.

Because the local (``local_native``) deployment reuses one persistent bash
session across ``env.start()`` -> agent turns -> reward, that ``CLAW_WORKSPACE``
export and the workspace contents are all still there at reward time.

This reward spec then scores the rollout the WORKPLACE way, per task:

1. Resolve the workspace path (from ``CLAW_WORKSPACE`` in the session, or a
   literal ``workspace`` config value).
2. Run the task's ``verify_workplace.py <workspace>`` in the session. It
   inspects the workspace and writes ``workplace_score.json``.
3. Read ``workplace_score.json`` back and compute ``total_score / max_score``
   (clamped to ``[0, 1]``).

Nothing here is env-specific: the verifier script path and workspace come from
the per-task config in the dataset's ``tools_kwargs.reward``.
"""

from __future__ import annotations

import json
import shlex

from uni_agent.async_logging import get_logger
from uni_agent.interaction import AgentEnv
from uni_agent.reward.base import AbstractRewardSpec
from uni_agent.reward.registry import register_reward_spec
from uni_agent.utils import auto_await

SCORE_FILENAME = "workplace_score.json"


@register_reward_spec("claw")
class ClawRewardSpec(AbstractRewardSpec):
    """Score a WORKPLACE claw task by running its per-task verifier in the env.

    Config (deep-merged from the dataset's ``tools_kwargs.reward``):

    - ``verify_script`` (str, required): path (in the runtime) to the task's
      ``verify_workplace.py``.
    - ``workspace`` (str): absolute workspace path. If omitted, it is resolved
      at reward time from ``workspace_env_var`` in the rollout session.
    - ``workspace_env_var`` (str): shell env var holding the workspace path.
      Default ``CLAW_WORKSPACE`` (what ``post_setup_cmd`` exports).
    - ``python_bin`` (str): interpreter to run the verifier. Default ``python``.
    - ``max_score`` (float): fallback denominator. Default 100. Overridden by
      the score file's own ``max_score`` or (if ``derive_max_from_details``)
      the sum of ``details[].max_score``.
    - ``derive_max_from_details`` (bool): default true.
    - ``eval_timeout`` (float): verifier timeout. Default 300s.
    - ``metadata`` (dict): opaque per-task info (task_id, env_name, format),
      logged for traceability.
    """

    def __init__(
        self,
        *,
        run_id: str,
        env: AgentEnv,
        verify_script: str,
        workspace: str | None = None,
        workspace_env_var: str = "CLAW_WORKSPACE",
        python_bin: str = "python",
        max_score: float = 100.0,
        derive_max_from_details: bool = True,
        metadata: dict | None = None,
        eval_timeout: int | float = 300,
    ):
        self.run_id = run_id
        self.env = env
        self.verify_script = verify_script
        self.workspace = workspace
        self.workspace_env_var = workspace_env_var
        self.python_bin = python_bin
        self.max_score = float(max_score)
        self.derive_max_from_details = derive_max_from_details
        self.metadata = metadata or {}
        self.eval_timeout = float(eval_timeout)
        self.logger = get_logger("reward_spec", run_id=run_id)

    async def _resolve_workspace(self) -> str:
        """Return the workspace path (literal config, or read from the session)."""
        if self.workspace:
            return self.workspace
        # ``printf %s`` avoids a trailing newline; the run_action layer also
        # strips, but keep it clean for the read_file path below.
        out = await self.env.communicate(
            f'printf %s "${{{self.workspace_env_var}}}"',
            check="ignore",
        )
        return (out or "").strip()

    def _reward_from_score_obj(self, score_obj: dict) -> tuple[float, float, float]:
        """Return ``(reward, total, max_score)`` from a parsed score object."""
        total = float(score_obj.get("total_score", 0.0))

        max_score = self.max_score
        if self.derive_max_from_details:
            details = score_obj.get("details")
            if isinstance(details, list) and details:
                summed = sum(float(d.get("max_score", 0.0)) for d in details)
                if summed > 0:
                    max_score = summed
        # An explicit max_score in the score file wins if present.
        if "max_score" in score_obj:
            try:
                explicit = float(score_obj["max_score"])
                if explicit > 0:
                    max_score = explicit
            except (TypeError, ValueError):
                pass

        if max_score <= 0:
            self.logger.warning(f"claw workplace max_score={max_score} <= 0; reward=0")
            return 0.0, total, max_score
        reward = max(0.0, min(1.0, total / max_score))
        return reward, total, max_score

    @auto_await
    async def compute_reward(self, **kwargs) -> tuple[float, dict]:
        result: dict = {
            "verify_script": self.verify_script,
            "metadata": self.metadata,
            "reward": 0.0,
        }

        try:
            workspace = await self._resolve_workspace()
        except Exception as exc:  # noqa: BLE001
            self.logger.error(f"Failed to resolve claw workspace: {exc}")
            result["error"] = f"workspace_resolve_failed: {exc}"
            return 0.0, result

        result["workspace"] = workspace
        if not workspace:
            self.logger.error(f"claw workspace is empty (env var {self.workspace_env_var} unset?)")
            result["error"] = "workspace_empty"
            return 0.0, result

        verify_cmd = (
            f"{self.python_bin} {shlex.quote(self.verify_script)} {shlex.quote(workspace)}"
        )
        try:
            verify_output = await self.env.communicate(
                verify_cmd,
                timeout=self.eval_timeout,
                check="ignore",
            )
            result["verify_output"] = verify_output
        except Exception as exc:  # noqa: BLE001 - reward must degrade gracefully
            self.logger.error(f"claw verify_workplace.py failed to run: {exc}")
            result["error"] = f"verify_execution_failed: {exc}"
            return 0.0, result

        score_path = f"{workspace.rstrip('/')}/{SCORE_FILENAME}"
        try:
            raw = await self.env.read_file(score_path)
        except Exception as exc:  # noqa: BLE001
            self.logger.error(f"Failed to read {score_path}: {exc}\nverifier stdout:\n{verify_output}")
            result["error"] = f"score_file_unreadable: {exc}"
            return 0.0, result

        try:
            score_obj = json.loads(raw)
        except json.JSONDecodeError as exc:
            self.logger.error(f"Failed to parse {SCORE_FILENAME}: {exc}\nraw={raw!r}")
            result["error"] = f"score_json_decode_error: {exc}"
            return 0.0, result

        reward, total, max_score = self._reward_from_score_obj(score_obj)
        result["reward"] = reward
        result["score"] = score_obj
        result["total_score"] = total
        result["max_score"] = max_score
        self.logger.info(
            f"claw workplace reward: {reward} ({total}/{max_score}) task={self.metadata.get('task_id')}"
        )
        return reward, result
