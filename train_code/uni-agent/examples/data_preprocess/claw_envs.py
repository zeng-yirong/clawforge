# ruff: noqa: E501
"""Build a training parquet for the ``claw_envs`` WORKPLACE tasks.

Training data follows the four-file WORKPLACE paradigm produced by
``claw_envs/claw_chains/gen_claw_workplace_tasks.py``. On disk a task is:

    <tasks-dir>/tasks/prompts/<id>.md         user-voice prompt (no solution steps)
    <tasks-dir>/tasks/<id>/env_builder.py     builds the initial workspace tree (cwd-relative)
    <tasks-dir>/scripts/<id>/verify_workplace.py   CODE-ONLY scorer -> workplace_score.json

Task ids look like ``wp_<env>__<idx>`` (e.g. ``wp_travel_policy_envs__046``);
the env name is parsed out of the id.

The agent solves the task with generic file operations only (read the tree,
write answer artifacts like ``ops/best_flight.json``). It does NOT call any
environment CLI -- per the generator, CLI/tool names never appear in the prompt.

Runtime model (paired with ``examples/claw_envs/agent_config.yaml``):

* ``post_setup_cmd`` (emitted here) creates a unique workspace via ``mktemp -d``,
  exports it as ``CLAW_WORKSPACE``, copies the task's ``env_builder.py`` in,
  ``cd``s there and runs it, then ``cd``s back into the workspace so the agent's
  shell starts in it. Because ``local_native`` reuses one bash session across
  ``env.start()`` -> agent turns -> reward, ``CLAW_WORKSPACE`` and the workspace
  contents persist all the way to scoring.
* Reward = the ``claw`` spec: it runs the task's ``verify_workplace.py`` against
  ``CLAW_WORKSPACE`` and reads ``workplace_score.json`` -> ``total/max``.

Two prompt formats (``--format``), a system-prompt-content axis only:

* ``without_skill`` -- plain generic-file-ops system prompt.
* ``skill``         -- the same, PLUS the matching env's ``SKILL.md`` injected as
  domain reference (extra background guidance; the task is still file-ops).

Both point at the same ``example_tasks``-style directory; the split only changes
what extra context is prepended to the system prompt.

Usage::

    python examples/data_preprocess/claw_envs.py \
        --format without_skill \
        --tasks-dir claw_envs/claw_chains/example_tasks \
        --repo-root "$PWD" \
        --local-save-dir ~/data/claw_envs
"""

import argparse
import re
from pathlib import Path

from datasets import Dataset

DEFAULT_REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TASKS_DIR = "claw_envs/claw_chains/example_tasks"

TASK_ID_RE = re.compile(r"^wp_(?P<env>.+)__(?P<idx>\d+)$")

SYSTEM_PROMPT_BASE = """
You are a capable assistant working inside a sandboxed workspace on a real task from a colleague.

Your working directory already contains the task's files (data, logs, configs, and possibly distractors). Read what you need with the file tools (`read`, `ls`, `find`, `grep`, `str_replace_editor`), reason about the request, and produce the exact output artifact(s) the colleague asks for using `write`/`edit`/`str_replace_editor`. Paths in the request are relative to your working directory.

Guidelines:
- Inspect the workspace before acting; there may be stale versions, drafts, or decoy records mixed in with the authoritative data.
- Produce exactly what is requested -- the right file at the right path, with the right fields and values, and nothing extra.
- Use `execute_bash` if you need to compute or transform data, but the deliverable is always the file(s) the task asks for.
- Call `finish` when the deliverable is complete.
""".strip()

SKILL_REFERENCE_HEADER = """
## Domain reference

The following background may help you understand this domain. It is reference material, not a list of steps to run:
""".strip()


def _discover_tasks(tasks_dir: Path) -> list[dict]:
    """Find WORKPLACE tasks by the on-disk directory convention.

    A task ``<id>`` is included only if all three files exist:
    prompt, env_builder, verifier.
    """
    prompts_dir = tasks_dir / "tasks" / "prompts"
    if not prompts_dir.is_dir():
        raise FileNotFoundError(f"No prompts dir under {tasks_dir}: {prompts_dir}")

    tasks: list[dict] = []
    for prompt_path in sorted(prompts_dir.glob("*.md")):
        task_id = prompt_path.stem
        env_builder = tasks_dir / "tasks" / task_id / "env_builder.py"
        verifier = tasks_dir / "scripts" / task_id / "verify_workplace.py"
        if not env_builder.is_file() or not verifier.is_file():
            print(f"  skip {task_id}: missing env_builder or verify_workplace", flush=True)
            continue
        m = TASK_ID_RE.match(task_id)
        env_name = m.group("env") if m else "unknown"
        tasks.append(
            {
                "task_id": task_id,
                "env_name": env_name,
                "prompt_path": prompt_path,
                "env_builder": env_builder,
                "verifier": verifier,
            }
        )
    return tasks


def _skill_md_for_env(repo_root: Path, env_name: str) -> str | None:
    """Return the env's SKILL.md body (frontmatter stripped) if present."""
    skill_path = repo_root / "claw_envs" / env_name / "SKILL.md"
    if not skill_path.is_file():
        return None
    text = skill_path.read_text(encoding="utf-8")
    # Strip YAML frontmatter (--- ... ---) if present; keep the body.
    stripped = text.lstrip()
    if stripped.startswith("---"):
        end = stripped.find("\n---", 3)
        if end != -1:
            return stripped[end + 4 :].lstrip("\n")
    return text


def _build_post_setup_cmd(repo_root: Path, task: dict) -> str:
    """Create the workspace, run env_builder.py in it, land the shell there.

    Steps (chained with ``&&`` so a failure aborts start):
      1. export a unique workspace dir (mktemp -d) as CLAW_WORKSPACE.
      2. copy the task's env_builder.py into it.
      3. cd into it and run env_builder.py (it uses cwd-relative paths).
      4. stay in the workspace so the agent's first turn starts there.
    """
    builder = (repo_root / task["env_builder"].relative_to(repo_root)).as_posix()
    return " && ".join(
        [
            f'export CLAW_WORKSPACE="$(mktemp -d -t claw_{task["env_name"]}_XXXXXX)"',
            f'cp {_q(builder)} "$CLAW_WORKSPACE/env_builder.py"',
            'cd "$CLAW_WORKSPACE"',
            "python env_builder.py",
        ]
    )


def _q(path: str) -> str:
    # Minimal shell-quote for paths embedded in post_setup_cmd.
    return "'" + path.replace("'", "'\\''") + "'"


def _build_sample(repo_root: Path, task: dict, fmt: str) -> dict:
    prompt_text = task["prompt_path"].read_text(encoding="utf-8").strip()

    system_prompt = SYSTEM_PROMPT_BASE
    if fmt == "skill":
        skill_body = _skill_md_for_env(repo_root, task["env_name"])
        if skill_body:
            system_prompt = SYSTEM_PROMPT_BASE + "\n\n" + SKILL_REFERENCE_HEADER + "\n\n" + skill_body.strip()
        else:
            print(f"  note: no SKILL.md for env {task['env_name']!r}; using base prompt for {task['task_id']}", flush=True)

    verifier = (repo_root / task["verifier"].relative_to(repo_root)).as_posix()

    tools_kwargs = {
        "env": {
            "post_setup_cmd": _build_post_setup_cmd(repo_root, task),
        },
        "reward": {
            "name": "claw",
            "verify_script": verifier,
            "workspace_env_var": "CLAW_WORKSPACE",
            "eval_timeout": 300,
            "metadata": {
                "env_name": task["env_name"],
                "task_id": task["task_id"],
                "format": fmt,
            },
        },
    }

    return {
        "prompt": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt_text},
        ],
        "agent_name": "swe_agent",
        "extra_info": {
            "task_id": task["task_id"],
            "data_source": f"claw_envs:{task['env_name']}",
            "format": fmt,
            "tools_kwargs": tools_kwargs,
        },
    }


def build_dataset(repo_root: Path, tasks_dir: Path, fmt: str) -> Dataset:
    tasks = _discover_tasks(tasks_dir)
    if not tasks:
        raise ValueError(f"No WORKPLACE tasks discovered under {tasks_dir}")
    samples = [_build_sample(repo_root, task, fmt) for task in tasks]
    print(f"Built {len(samples)} WORKPLACE task(s) [format={fmt}] from {tasks_dir}", flush=True)
    return Dataset.from_list(samples)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--format", choices=["skill", "without_skill"], default="without_skill")
    parser.add_argument(
        "--tasks-dir",
        default=DEFAULT_TASKS_DIR,
        help="Directory holding tasks/prompts/, tasks/<id>/, scripts/<id>/ (relative to repo root or absolute).",
    )
    parser.add_argument(
        "--repo-root",
        default=str(DEFAULT_REPO_ROOT),
        help="Absolute path to the uni-agent repo root as it appears on the training host.",
    )
    parser.add_argument("--local-save-dir", default="~/data/claw_envs")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).expanduser().resolve()
    tasks_dir = Path(args.tasks_dir)
    if not tasks_dir.is_absolute():
        tasks_dir = (repo_root / tasks_dir).resolve()

    dataset = build_dataset(repo_root, tasks_dir, args.format)

    output_dir = Path(args.local_save_dir).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"claw_envs_{args.format}.parquet"
    dataset.to_parquet(str(output_path))
    print(f"Wrote {output_path}", flush=True)


if __name__ == "__main__":
    main()
