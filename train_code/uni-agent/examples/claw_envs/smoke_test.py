#!/usr/bin/env python3
"""End-to-end smoke test for claw-env WORKPLACE training wiring (no verl, no LLM).

Exercises the exact runtime path a rollout uses, minus the model:

    AgentEnv(local_native).start()   # post_setup_cmd: mktemp workspace + env_builder.py
      -> install_tools()             # L1 file tools onto PATH
      -> communicate(<write artifact>)   # what a correct agent would produce
      -> ClawRewardSpec.compute_reward() # runs verify_workplace.py, reads workplace_score.json

Run on the Linux training host to confirm the workspace is built, the session
persists across turns, and the per-task verifier scores the artifact -- before
wiring the parquet into a real verl run.

    python examples/claw_envs/smoke_test.py --repo-root "$PWD"

Uses the reference task ``wp_travel_policy_envs__046`` and writes the known
correct answer, so the printed reward should be 1.0.
"""

from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from uni_agent.interaction import AgentEnv, AgentEnvConfig
from uni_agent.reward.registry import load_reward_spec
from uni_agent.tools import ToolConfig

# Reference task + its known-correct deliverable (from the verifier's expected
# flight_id / price for the active v2 policy + preferred vendor).
TASK_ID = "wp_travel_policy_envs__046"
ENV_NAME = "travel_policy_envs"
CORRECT_ARTIFACT_REL = "ops/best_flight.json"
CORRECT_ARTIFACT_JSON = '{"flight_id": "SB-123", "price": 8500}'


def _post_setup_cmd(repo_root: Path) -> str:
    builder = (repo_root / "claw_envs/claw_chains/example_tasks/tasks" / TASK_ID / "env_builder.py").as_posix()
    return " && ".join(
        [
            f'export CLAW_WORKSPACE="$(mktemp -d -t claw_{ENV_NAME}_XXXXXX)"',
            f"cp '{builder}' \"$CLAW_WORKSPACE/env_builder.py\"",
            'cd "$CLAW_WORKSPACE"',
            "python env_builder.py",
        ]
    )


async def run(repo_root: Path) -> float:
    env_config = AgentEnvConfig(
        deployment={"type": "local_native", "startup_timeout": 120},
        tool_install_dir=Path("~/.uni-agent/bin").expanduser(),
        env_variables={"PAGER": "cat", "GIT_PAGER": "cat"},
        post_setup_cmd=_post_setup_cmd(repo_root),
    )
    env = AgentEnv(run_id="smoke-test", env_config=env_config)

    tool_names = ["read", "write", "edit", "str_replace_editor", "ls", "find", "grep", "execute_bash", "finish"]
    tools = [ToolConfig(name=n).get_tool() for n in tool_names]

    await env.start()
    print("[smoke] env started + workspace built")
    try:
        await env.install_tools(tools)
        print("[smoke] tools installed")

        # Confirm the workspace tree exists (what the agent would inspect).
        tree = await env.run_action("ls -R data 2>/dev/null | head -20", action_timeout=30)
        print(f"[smoke] workspace data tree:\n{tree.strip()[:400]}")

        # Simulate a correct agent: write the deliverable at the requested path.
        # (mkdir + write, in the workspace cwd which post_setup_cmd left us in.)
        write_cmd = (
            f"mkdir -p $(dirname {CORRECT_ARTIFACT_REL}) && "
            f"cat > {CORRECT_ARTIFACT_REL} <<'EOF'\n{CORRECT_ARTIFACT_JSON}\nEOF"
        )
        await env.run_action(write_cmd, action_timeout=30)
        print(f"[smoke] wrote {CORRECT_ARTIFACT_REL}")

        verifier = (
            repo_root / "claw_envs/claw_chains/example_tasks/scripts" / TASK_ID / "verify_workplace.py"
        ).as_posix()
        reward_spec = load_reward_spec(
            {
                "name": "claw",
                "run_id": "smoke-test",
                "env": env,
                "verify_script": verifier,
                "workspace_env_var": "CLAW_WORKSPACE",
                "metadata": {"env_name": ENV_NAME, "task_id": TASK_ID},
            }
        )
        reward, detail = await reward_spec.compute_reward(interaction_result={})
        print(f"\n[smoke] reward = {reward} ({detail.get('total_score')}/{detail.get('max_score')})")
        if "error" in detail:
            print(f"[smoke] error = {detail['error']}")
        return reward
    finally:
        await env.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo-root",
        default=str(Path(__file__).resolve().parents[2]),
        help="Absolute path to the uni-agent repo root on this host.",
    )
    args = parser.parse_args()
    repo_root = Path(args.repo_root).expanduser().resolve()

    reward = asyncio.run(run(repo_root))
    if reward < 1.0:
        raise SystemExit(f"Smoke test expected reward 1.0 for the correct answer, got {reward}; wiring is broken.")
    print("\n[smoke] PASS")


if __name__ == "__main__":
    main()
