from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from .backend import build_llm, build_sampling_params, load_tokenizer
from .runner import build_run_requests, iter_jsonl_results, make_result_dir, run_task, run_tasks_batched, utc_now, write_summary
from .tasks import discover_tasks


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Nanoclaw-compatible workplace tasks with local vLLM or an OpenAI-compatible API.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--base-tasks", required=True, help="Input base_tasks directory.")
    parser.add_argument("--output", required=True, help="Output result root directory.")
    parser.add_argument("--model", required=True, help="Local model path or model name for vLLM.")
    parser.add_argument("--tokenizer", default=None, help="Tokenizer path; defaults to --model.")
    parser.add_argument(
        "--backend",
        default="local",
        choices=("local", "openai"),
        help="Use in-process vLLM ('local') or an OpenAI-compatible API ('openai').",
    )
    parser.add_argument("--api-base", default="http://127.0.0.1:8000/v1", help="OpenAI-compatible API base URL.")
    parser.add_argument("--api-key", default="dummy_key", help="OpenAI-compatible API key.")
    parser.add_argument("--served-model-name", default=None, help="Served model name for API mode; defaults to --model.")
    parser.add_argument("--api-timeout", type=float, default=1800.0, help="OpenAI API request timeout in seconds.")
    parser.add_argument(
        "--api-max-workers",
        type=int,
        default=None,
        help="Max concurrent API requests from this runner; defaults to --agent-batch-size.",
    )
    parser.add_argument(
        "--task-id",
        action="append",
        default=None,
        help="Run only this task id. Can be specified multiple times.",
    )
    parser.add_argument("--task-glob", default="data_*", help="Task directory glob under base_tasks/tasks.")
    parser.add_argument("--n", type=int, default=1, help="Number of independent samples per task, saved as data_x_sample_i.")
    parser.add_argument("--rollout-step", type=int, default=1, help="Output step id, saved under step_<rollout-step>.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing task result dirs.")
    parser.add_argument("--resume", action="store_true", help="Skip completed task result dirs.")
    parser.add_argument("--run-verifier", action="store_true", help="Run copied verify_workplace.py after inference.")
    parser.add_argument("--verifier-timeout", type=float, default=120.0, help="Verifier timeout in seconds.")
    parser.add_argument("--verifier-workers", type=int, default=2, help="Concurrent verifier workers in batched mode.")
    parser.add_argument(
        "--prepare-window-size",
        type=int,
        default=None,
        help="Max prepared/running samples kept in memory and on disk at once; defaults to --agent-batch-size.",
    )

    thinking = parser.add_mutually_exclusive_group()
    thinking.add_argument("--enable-thinking", dest="enable_thinking", action="store_true")
    thinking.add_argument("--disable-thinking", dest="enable_thinking", action="store_false")
    parser.set_defaults(enable_thinking=False)

    parser.add_argument("--tensor-parallel-size", type=int, default=1)
    parser.add_argument("--dtype", default="bfloat16", choices=("auto", "float16", "bfloat16", "float32"))
    parser.add_argument("--max-model-len", type=int, default=8192)
    parser.add_argument("--max-num-batched-tokens", type=int, default=None)
    parser.add_argument("--max-num-seqs", type=int, default=None)
    parser.add_argument("--gpu-memory-utilization", type=float, default=0.85)
    parser.add_argument("--trust-remote-code", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--enforce-eager", action="store_true")
    parser.add_argument("--enable-prefix-caching", action="store_true")

    parser.add_argument("--max-steps", type=int, default=20, help="Maximum agent/tool turns per task.")
    parser.add_argument(
        "--agent-batch-size",
        type=int,
        default=1,
        help="Number of active tasks to advance in each vLLM.generate batch.",
    )
    parser.add_argument("--max-tokens", type=int, default=2048, help="Maximum generated tokens per turn.")
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--top-p", type=float, default=0.95)
    parser.add_argument("--top-k", type=int, default=-1)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--read-limit", type=int, default=24000, help="Maximum characters returned by read.")
    parser.add_argument("--list-limit", type=int, default=500, help="Maximum entries returned by ls/find/grep.")
    parser.add_argument("--allow-python-tool", action="store_true", help="Enable model generated Python execution.")
    parser.add_argument("--python-timeout", type=float, default=20.0, help="run_python timeout in seconds.")
    parser.add_argument("--bash-timeout", type=float, default=20.0, help="restricted bash/exec timeout in seconds.")
    args = parser.parse_args(argv)

    if args.max_steps <= 0:
        parser.error("--max-steps must be positive")
    if args.n <= 0:
        parser.error("--n must be positive")
    if args.rollout_step <= 0:
        parser.error("--rollout-step must be positive")
    if args.agent_batch_size <= 0:
        parser.error("--agent-batch-size must be positive")
    if args.prepare_window_size is not None and args.prepare_window_size <= 0:
        parser.error("--prepare-window-size must be positive")
    if args.api_timeout <= 0:
        parser.error("--api-timeout must be positive")
    if args.api_max_workers is not None and args.api_max_workers <= 0:
        parser.error("--api-max-workers must be positive")
    if args.verifier_workers <= 0:
        parser.error("--verifier-workers must be positive")
    if args.resume and args.overwrite:
        parser.error("--resume and --overwrite are mutually exclusive")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    base_tasks = Path(args.base_tasks).expanduser().resolve()
    output_root = Path(args.output).expanduser().resolve()
    requested_task_ids = set(args.task_id) if args.task_id else None
    specs = discover_tasks(base_tasks, task_glob=args.task_glob, task_ids=requested_task_ids)

    print(f"[info] base_tasks={base_tasks}", file=sys.stderr)
    print(f"[info] output={output_root}", file=sys.stderr)
    requests = build_run_requests(specs, n=args.n, rollout_step=args.rollout_step)

    print(f"[info] tasks={len(specs)}", file=sys.stderr)
    print(f"[info] samples={len(requests)} n={args.n} rollout_step={args.rollout_step}", file=sys.stderr)
    print(f"[info] model={args.model}", file=sys.stderr)
    print(f"[info] backend={args.backend}", file=sys.stderr)
    if args.backend == "openai":
        print(f"[info] api_base={args.api_base}", file=sys.stderr)
        print(f"[info] served_model_name={args.served_model_name or args.model}", file=sys.stderr)
    print(f"[info] agent_batch_size={args.agent_batch_size}", file=sys.stderr)
    print(f"[info] prepare_window_size={args.prepare_window_size or args.agent_batch_size}", file=sys.stderr)

    tokenizer = load_tokenizer(args)
    llm = build_llm(args)
    sampling_params = build_sampling_params(args)

    started_at = utc_now()
    results: list[dict[str, Any]] = []
    output_root.mkdir(parents=True, exist_ok=True)

    if args.agent_batch_size > 1 and len(requests) > 1:
        results = run_tasks_batched(
            requests=requests,
            result_root=output_root,
            llm=llm,
            tokenizer=tokenizer,
            sampling_params=sampling_params,
            args=args,
        )
        (output_root / "results.jsonl").write_text(iter_jsonl_results(results), encoding="utf-8")
        write_summary(output_root, results, started_at)
    else:
        for request in requests:
            spec = request.spec
            rollout_label = f"step_{request.rollout_step}/{spec.task_id}_sample_{request.rollout_n}"
            print(f"[task] {rollout_label}", file=sys.stderr)
            try:
                result = run_task(
                    request=request,
                    result_root=output_root,
                    llm=llm,
                    tokenizer=tokenizer,
                    sampling_params=sampling_params,
                    args=args,
                )
            except Exception as exc:
                result = {
                    "task_id": spec.task_id,
                    "status": "failed",
                    "result_dir": str(make_result_dir(output_root, request)),
                    "error": f"{type(exc).__name__}: {exc}",
                    "rollout_step": request.rollout_step,
                    "rollout_sample_index": request.rollout_sample_index,
                    "rollout_n": request.rollout_n,
                    "rollout_label": rollout_label,
                }
                print(f"[error] {rollout_label}: {result['error']}", file=sys.stderr)
            results.append(result)
            (output_root / "results.jsonl").write_text(iter_jsonl_results(results), encoding="utf-8")
            write_summary(output_root, results, started_at)

    completed = sum(1 for result in results if result.get("status") == "completed")
    failed = sum(1 for result in results if result.get("status") == "failed")
    skipped = sum(1 for result in results if result.get("status") == "skipped")
    print(f"[done] completed={completed} failed={failed} skipped={skipped} output={output_root}", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
