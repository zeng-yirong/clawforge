import json
from pathlib import Path

import pytest

from uni_agent.datasets.claw_native import ClawNativeDataset


REPO_ROOT = Path(__file__).resolve().parents[2]
TASKS_DIR = REPO_ROOT / "claw_envs" / "claw_chains" / "example_tasks"


class TinyTokenizer:
    def apply_chat_template(self, messages, add_generation_prompt=True, **kwargs):
        del add_generation_prompt, kwargs
        text = "\n".join(message["content"] for message in messages)
        return list(range(max(1, len(text.split()))))


def _config(**overrides):
    base = {
        "claw_repo_root": str(REPO_ROOT),
        "claw_include_cli": True,
        "claw_format": "without_skill",
        "filter_overlong_prompts": False,
        "max_prompt_length": 100_000,
    }
    base.update(overrides)
    return base


def test_reads_workplace_tasks_without_parquet_and_builds_cli_setup():
    dataset = ClawNativeDataset(
        data_files=[str(TASKS_DIR)],
        tokenizer=TinyTokenizer(),
        processor=None,
        config=_config(claw_task_ids=["wp_smart_home_envs__021"]),
    )

    assert len(dataset) == 1
    row = dataset[0]

    assert row["agent_name"] == "swe_agent"
    assert row["raw_prompt"][0]["role"] == "system"
    assert "python -m claw_envs.smart_home_envs.cli" in row["raw_prompt"][0]["content"]

    tools_kwargs = row["tools_kwargs"]
    setup_cmd = tools_kwargs["env"]["post_setup_cmd"]
    assert "CLAW_WORKSPACE" in setup_cmd
    assert "python env_builder.py" in setup_cmd
    assert "prepare-rollout" in setup_cmd
    assert "SMART_HOME_SESSION_ID" in setup_cmd
    assert setup_cmd.endswith('cd "$CLAW_WORKSPACE"')
    assert tools_kwargs["env"]["restrict_workspace"] is True
    assert tools_kwargs["env"]["restrict_bash_commands"] is True
    assert "python -m claw_envs.smart_home_envs.cli" in tools_kwargs["env"]["allowed_bash_command_prefixes"]

    reward = tools_kwargs["reward"]
    assert reward["name"] == "claw"
    assert reward["workspace_env_var"] == "CLAW_WORKSPACE"
    assert reward["verify_script"].endswith(
        "claw_envs/claw_chains/example_tasks/scripts/wp_smart_home_envs__021/verify_workplace.py"
    )
    assert reward["metadata"]["task_id"] == "wp_smart_home_envs__021"
    assert reward["metadata"]["scenario_id"] == "energy_aware_climate"


def test_skill_format_prompts_model_to_read_skill_file():
    dataset = ClawNativeDataset(
        data_files=[str(TASKS_DIR)],
        tokenizer=TinyTokenizer(),
        processor=None,
        config=_config(claw_format="skill", claw_task_ids=["wp_smart_home_envs__021"]),
    )

    system_prompt = dataset[0]["raw_prompt"][0]["content"]

    assert "SKILL.md" in system_prompt
    assert str(REPO_ROOT / "claw_envs" / "smart_home_envs" / "SKILL.md").replace("\\", "/") in system_prompt
    assert "Command prefix: `python -m claw_envs.smart_home_envs.cli`" in system_prompt


def test_chain_only_jsonl_requires_a_workplace_verifier(tmp_path):
    chain_file = tmp_path / "post_mails.jsonl"
    chain_file.write_text(
        json.dumps(
            {
                "env_name": "post_mails",
                "scenario_id": "orbital_launch",
                "chain": [{"layer": "cli", "op": "task"}],
            }
        )
        + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="chain-only claw record"):
        ClawNativeDataset(
            data_files=[str(chain_file)],
            tokenizer=TinyTokenizer(),
            processor=None,
            config=_config(),
        )
