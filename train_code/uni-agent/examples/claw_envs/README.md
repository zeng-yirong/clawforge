# Claw-env local training (WORKPLACE tasks)

Wire the `claw_envs` WORKPLACE tasks into verl RL training, running **locally on
the host** (no container isolation).

## The WORKPLACE task model

Training data follows the four-file paradigm produced by
`claw_envs/claw_chains/gen_claw_workplace_tasks.py`. On disk, one task is:

```
<tasks-dir>/tasks/prompts/<id>.md          user-voice prompt (no solution steps)
<tasks-dir>/tasks/<id>/env_builder.py      builds the initial workspace tree (cwd-relative)
<tasks-dir>/scripts/<id>/verify_workplace.py   CODE-ONLY scorer -> workplace_score.json
```

Task ids are `wp_<env>__<idx>` (e.g. `wp_travel_policy_envs__046`). The agent
solves the task with **generic file operations only** — read the tree
`env_builder.py` laid down, write the requested artifact (e.g.
`ops/best_flight.json`). There is **no environment CLI**: the per-env
`cli.py`/`evaluator.py`/`SKILL.md` are task-generation skeletons, not part of the
rollout.

Scoring is **per task**: each task's own `verify_workplace.py` inspects the
workspace and writes `workplace_score.json` with `{total_score, details:[...]}`.
Reward = `total_score / max_score`, clamped to `[0, 1]`.

## How a rollout runs

1. **Deployment: `local_native`.** One persistent pexpect bash session per
   rollout (no Docker), purpose-built to survive verl's `asyncio.run` pattern.
2. **Setup (`post_setup_cmd`, built by the preprocessing script):**
   - `export CLAW_WORKSPACE="$(mktemp -d ...)"` — a unique workspace per rollout
     (concurrent rollouts never collide),
   - copy the task's `env_builder.py` in, `cd` there, run it,
   - the shell stays in the workspace, so the agent's first turn starts in it.
3. **Interaction:** the agent uses
   `read`/`write`/`edit`/`str_replace_editor`/`ls`/`find`/`grep`
   (+ `execute_bash` for computation) and writes the deliverable file.
4. **Reward (`claw` spec):** runs the task's `verify_workplace.py $CLAW_WORKSPACE`
   in the same session, reads `workplace_score.json`. Because the session
   persists across start → turns → reward, the workspace and its artifacts are
   all still there.

## Two prompt formats

A **system-prompt-content axis only** (both use the same task files and reward):

| Format          | System prompt                                                    | Config              |
| --------------- | ---------------------------------------------------------------- | ------------------- |
| `without_skill` | Generic file-ops instructions.                                   | `agent_config.yaml` |
| `skill`         | Same, **plus** the matching env's `SKILL.md` injected as domain reference. | `agent_config.yaml` |

The generator forbids CLI/tool names in WORKPLACE prompts, so there's no runtime
`SkillsManager` — the `skill` format just prepends `claw_envs/<env>/SKILL.md`
(frontmatter stripped) as extra background. One agent config serves both.

## Files

- `agent_config.yaml` — thin mode-2 shell; per-task config arrives via `tools_kwargs`.
- `../data_preprocess/claw_envs.py` — discovers tasks by directory convention and
  builds the parquet for either format.
- `smoke_test.py` — runs the reference task end-to-end (no verl/LLM), writes the
  correct answer, expects reward 1.0. Run this first.
- `../../uni_agent/reward/claw.py` — the `claw` WORKPLACE reward spec.

## Quickstart

```bash
# 1. Smoke-test the runtime wiring (Linux host, bash available).
python examples/claw_envs/smoke_test.py --repo-root "$PWD"

# 2. Build a dataset from the example tasks (without_skill format).
python examples/data_preprocess/claw_envs.py \
    --format without_skill \
    --tasks-dir claw_envs/claw_chains/example_tasks \
    --repo-root "$PWD" --local-save-dir ~/data/claw_envs
# ...or the skill format (injects each env's SKILL.md):
python examples/data_preprocess/claw_envs.py \
    --format skill \
    --tasks-dir claw_envs/claw_chains/example_tasks \
    --repo-root "$PWD" --local-save-dir ~/data/claw_envs

# 3. Point a verl training run at the parquet + agent config:
#      actor_rollout_ref.rollout.agent.agent_loop_config_path=examples/claw_envs/agent_config.yaml
#      actor_rollout_ref.rollout.agent.default_agent_loop=swe_agent
#      actor_rollout_ref.rollout.mode=async
#    (see examples/agent_train/*.sh for the full launcher pattern.)
```

## Adding more tasks

Point `--tasks-dir` at any directory that follows the `tasks/prompts/`,
`tasks/<id>/env_builder.py`, `scripts/<id>/verify_workplace.py` convention (e.g.
the output of `gen_claw_workplace_tasks.py` in
`claw_envs/claw_chains/claw_workplace_tasks/`). No per-task config needed — the
preprocessing script discovers them all.

## Notes

- **No isolation.** Commands run on the host as the training user. Each rollout
  gets its own `mktemp` workspace, but there is no filesystem/network sandbox —
  run only trusted tasks and models.
- `env_builder.py` uses cwd-relative paths; setup `cd`s into the fresh workspace
  before running it (never hardcode an `assets/<id>` prefix, per the generator).
- `local_native` is Unix-only (pexpect PTY, `/usr/bin/env bash`). Your Linux
  Docker host satisfies this; `host` is an asyncio-based fallback.
- `tool_install_dir` defaults to `~/.uni-agent/bin` (user-writable, no root).
