from __future__ import annotations

import argparse
import os
import sys

from without_skill._shared.cli_utils import (
    HiddenCommandArgumentParser,
    agent_error_message,
    agent_payload,
    generate_session_id,
    parse_csv_list,
    print_json,
    resolve_bound_session_id,
    resolve_scenario_id,
)
from .environment import ArxivReviewRoadmapEnvironment


SESSION_ENV = "ARXIV_REVIEW_ROADMAP_SESSION_ID"
STATE_ENV = "ARXIV_REVIEW_ROADMAP_STATE_ROOT"
SCENARIO_ENV = "ARXIV_REVIEW_ROADMAP_SCENARIO_ID"
DEFAULT_SCENARIO_ID = "arxiv_review_tool_reasoning_q2_2026"


def build_parser() -> argparse.ArgumentParser:
    shared = argparse.ArgumentParser(add_help=False)
    shared.add_argument("--data-root", type=str, default=None)
    shared.add_argument("--state-root", type=str, default=None)

    agent_session = argparse.ArgumentParser(add_help=False)
    agent_session.add_argument("--session-id", type=str, default=None, help=argparse.SUPPRESS)

    parser = HiddenCommandArgumentParser(description="ArXiv review and roadmap training environment CLI.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list-scenarios", parents=[shared], help="List scenarios.")

    prepare = subparsers.add_parser("prepare-rollout", aliases=["create-session"], parents=[shared], help=argparse.SUPPRESS)
    prepare.add_argument("--session-id", type=str, default=None, help=argparse.SUPPRESS)
    prepare.add_argument("--scenario-id", type=str, default=None)
    prepare.add_argument("--show-bindings", action="store_true")
    prepare.add_argument("--show-task", action="store_true")
    prepare.add_argument("--overwrite", action="store_true")

    subparsers.add_parser("reset-rollout", aliases=["reset-session"], parents=[shared, agent_session], help=argparse.SUPPRESS)
    subparsers.add_parser("task", parents=[shared, agent_session], help="Show task.")

    list_papers_cmd = subparsers.add_parser("list-papers", parents=[shared, agent_session], help="List papers.")
    list_papers_cmd.add_argument("--query", type=str, default="")
    list_papers_cmd.add_argument("--direction", type=str, default=None)
    list_papers_cmd.add_argument("--year-min", type=int, default=None)
    list_papers_cmd.add_argument("--limit", type=int, default=None)

    get_paper_cmd = subparsers.add_parser("get-paper", parents=[shared, agent_session], help="Get paper.")
    get_paper_cmd.add_argument("--paper-id", required=True, type=str)

    subparsers.add_parser("list-attachments", parents=[shared, agent_session], help="List attachments.")
    read_attachment_cmd = subparsers.add_parser("read-attachment", parents=[shared, agent_session], help="Read attachment.")
    read_attachment_cmd.add_argument("--attachment-path", required=True, type=str)

    gen_cmd = subparsers.add_parser("generate-review", parents=[shared, agent_session], help="Generate review and roadmap.")
    gen_cmd.add_argument("--direction", required=True, type=str)
    gen_cmd.add_argument("--paper-ids", type=str, default=None)

    list_cache_cmd = subparsers.add_parser("list-cache", parents=[shared, agent_session], help="List cache.")
    list_cache_cmd.add_argument("--entry-type", type=str, default=None)
    list_cache_cmd.add_argument("--cache-key", type=str, default=None)
    list_cache_cmd.add_argument("--limit", type=int, default=None)

    get_cache_cmd = subparsers.add_parser("get-cache-entry", parents=[shared, agent_session], help="Get cache entry.")
    get_cache_cmd.add_argument("--entry-id", required=True, type=str)

    subparsers.add_parser("session-summary", parents=[shared, agent_session], help="Show summary.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    env = ArxivReviewRoadmapEnvironment(data_root=args.data_root, state_root=args.state_root)
    try:
        if args.command == "list-scenarios":
            return print_json({"status": "success", "data": env.list_scenarios()})
        if args.command in {"prepare-rollout", "create-session"}:
            session_id = getattr(args, "session_id", None) or os.getenv(SESSION_ENV, "").strip() or generate_session_id("arxiv-review")
            scenario_id = resolve_scenario_id(args, SCENARIO_ENV, DEFAULT_SCENARIO_ID)
            env.create_session(session_id, scenario_id, overwrite=args.overwrite)
            payload = {"session_id": session_id, "scenario_id": scenario_id, "state_root": str(env.store.state_root)}
            if args.show_bindings:
                payload["bindings"] = {SESSION_ENV: session_id, STATE_ENV: str(env.store.state_root), SCENARIO_ENV: scenario_id}
            if args.show_task:
                payload["task"] = agent_payload(env.get_task(session_id))
            return print_json({"status": "success", "data": payload})

        session_id = resolve_bound_session_id(args, SESSION_ENV)
        if args.command in {"reset-rollout", "reset-session"}:
            return print_json({"status": "success", "data": agent_payload(env.reset_session(session_id))})
        if args.command == "task":
            return print_json({"status": "success", "data": agent_payload(env.view_task(session_id)["data"])})
        if args.command == "list-papers":
            data = env.list_papers(session_id, query=args.query, direction=args.direction, year_min=args.year_min, limit=args.limit)
            return print_json({"status": "success", "data": data["data"]})
        if args.command == "get-paper":
            data = env.get_paper(session_id, args.paper_id)
            return print_json({"status": "success", "data": data["data"]})
        if args.command == "list-attachments":
            return print_json({"status": "success", "data": env.list_attachments(session_id)["data"]})
        if args.command == "read-attachment":
            return print_json({"status": "success", "data": env.read_attachment(session_id, args.attachment_path)["data"]})
        if args.command == "generate-review":
            data = env.generate_review(session_id, direction=args.direction, paper_ids=parse_csv_list(args.paper_ids))
            return print_json({"status": "success", "data": data["data"]})
        if args.command == "list-cache":
            data = env.list_cache(session_id, entry_type=args.entry_type, cache_key=args.cache_key, limit=args.limit)
            return print_json({"status": "success", "data": data["data"]})
        if args.command == "get-cache-entry":
            data = env.get_cache_entry(session_id, args.entry_id)
            return print_json({"status": "success", "data": data["data"]})
        if args.command == "session-summary":
            return print_json({"status": "success", "data": agent_payload(env.session_summary(session_id))})
    except Exception as exc:
        return print_json({"status": "error", "message": agent_error_message(exc)}, exit_code=1)
    return print_json({"status": "error", "message": f"Unknown command: {args.command}"}, exit_code=1)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
