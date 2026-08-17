# Native claw dataset for verl

`uni_agent.datasets.ClawNativeDataset` lets verl train from claw task directories
or JSON/JSONL manifests without first writing parquet files.

## Expected training data

The simplest input is an `example_tasks`-style directory:

```text
claw_envs/claw_chains/example_tasks/
  tasks/prompts/<task_id>.md
  tasks/<task_id>/env_builder.py
  scripts/<task_id>/verify_workplace.py
```

Each row is scored by its own `verify_workplace.py`; the runtime reward does not
call an environment package `evaluator.py`.

The dataset can also read JSON/JSONL manifests. A manifest record must either
already be a full verl-style row with `prompt` and `extra_info`, or include:

```json
{
  "task_id": "wp_smart_home_envs__021",
  "env_name": "smart_home_envs",
  "prompt_path": "claw_envs/claw_chains/example_tasks/tasks/prompts/wp_smart_home_envs__021.md",
  "env_builder": "claw_envs/claw_chains/example_tasks/tasks/wp_smart_home_envs__021/env_builder.py",
  "verify_script": "claw_envs/claw_chains/example_tasks/scripts/wp_smart_home_envs__021/verify_workplace.py",
  "scenario_id": "energy_aware_climate"
}
```

Records from `claw_chains_out/*.jsonl` contain chain traces only. They are not
directly scoreable for RL unless a manifest maps them to a prompt, workspace
builder, and verifier.

## verl overrides

Use verl's existing `data.custom_cls` hook:

```bash
data.custom_cls.path=pkg://uni_agent.datasets.claw_native
data.custom_cls.name=ClawNativeDataset
data.train_files='["/path/to/uni-agent/claw_envs/claw_chains/example_tasks"]'
data.val_files='["/path/to/uni-agent/claw_envs/claw_chains/example_tasks"]'
data.claw_repo_root=/path/to/uni-agent
data.claw_include_cli=true
data.claw_restrict_workspace=true
data.claw_restrict_bash=true
data.claw_format=without_skill
data.claw_tool_docs_dir=/path/to/uni-agent/claw_envs/claw_chains/claw_tool_env_docs
data.need_tools_kwargs=true
actor_rollout_ref.rollout.mode=async
actor_rollout_ref.rollout.agent.agent_loop_config_path=/path/to/uni-agent/examples/claw_envs/agent_config.yaml
actor_rollout_ref.rollout.agent.default_agent_loop=swe_agent
```

For a ModelArts/NPU-style launcher, use:

```bash
bash /path/to/uni-agent/examples/claw_envs/run_claw_dapo.sh
```

Common overrides:

```bash
VERL_DIR=/path/to/verl \
UNI_AGENT_DIR=/path/to/uni-agent \
MODEL_PATH=/path/to/model \
CLAW_TASKS_DIR=/path/to/uni-agent/claw_envs/claw_chains/example_tasks \
CLAW_FORMAT=without_skill \
bash /path/to/uni-agent/examples/claw_envs/run_claw_dapo.sh
```

For the two prompt formats:

```bash
# Tool docs are rendered into the system prompt.
data.claw_format=without_skill

# The system prompt tells the model to read the env's SKILL.md, then use CLI.
data.claw_format=skill

# Duplicate each task into both formats.
data.claw_format=both
```

## Runtime behavior

For each sample, the dataset emits `extra_info.tools_kwargs` with:

- `env.post_setup_cmd`: creates `CLAW_WORKSPACE`, runs that task's
  `env_builder.py`, exports CLI session/state/scenario environment variables,
  and runs the env CLI's hidden `prepare-rollout`.
- `reward`: `name: claw`, the sample's `verify_script`, and
  `workspace_env_var: CLAW_WORKSPACE`.

The agent starts in `CLAW_WORKSPACE`. It should use file tools for local files
and `execute_bash` for commands such as:

```bash
python -m claw_envs.smart_home_envs.cli task
python -m claw_envs.smart_home_envs.cli get-all-devices
```

The model should not edit the CLI rollout state files or environment package
implementation directly.

By default, native claw samples also enforce this at runtime:

- File tools with `--path` are denied if the path resolves outside
  `CLAW_WORKSPACE`.
- Raw `execute_bash` commands are denied unless they directly start with the
  current environment CLI prefix, such as
  `python -m claw_envs.smart_home_envs.cli`.
- Shell control operators, redirection, command substitution, and hidden session
  management subcommands such as `prepare-rollout` and `reset-rollout` are
  denied for model-issued bash commands.

The setup command itself still runs `prepare-rollout` before the model starts;
the restriction applies to model tool calls.
