from __future__ import annotations

import argparse
import json
import os
import random
import sys
from datetime import datetime, timezone
from typing import Any

from .environment import ProductCompetitionEnvironment


WITHOUT_SKILL_SESSION_ID_ENV = "WITHOUT_SKILL_SESSION_ID"
WITHOUT_SKILL_STATE_ROOT_ENV = "WITHOUT_SKILL_STATE_ROOT"
WITHOUT_SKILL_SCENARIO_ID_ENV = "WITHOUT_SKILL_SCENARIO_ID"
DEFAULT_SCENARIO_ID = "sku_competition_report_apac_q2_2026"
_HIDDEN_HELP_MARKERS = ("(create-session)", "(reset-session)", "==SUPPRESS==")


def _print_json(payload: dict[str, Any], *, exit_code: int = 0) -> int:
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return exit_code


class ProductCompetitionArgumentParser(argparse.ArgumentParser):
    def format_help(self) -> str:
        help_text = super().format_help()
        lines = [
            line
            for line in help_text.splitlines()
            if not any(marker in line for marker in _HIDDEN_HELP_MARKERS)
        ]
        return "\n".join(lines) + ("\n" if help_text.endswith("\n") else "")


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _generate_session_id() -> str:
    return f"sku-{_utc_stamp()}-{random.randint(1000, 9999)}"


def _resolve_bound_session_id(args: argparse.Namespace) -> str:
    explicit = getattr(args, "session_id", None)
    if explicit:
        return explicit

    env_value = os.getenv(WITHOUT_SKILL_SESSION_ID_ENV, "").strip()
    if env_value:
        return env_value

    raise ValueError(
        f"No active rollout session is bound. The trainer must set {WITHOUT_SKILL_SESSION_ID_ENV} "
        "before agent commands run."
    )


def _resolve_scenario_id(args: argparse.Namespace) -> str:
    explicit = getattr(args, "scenario_id", None)
    if explicit:
        return explicit

    env_value = os.getenv(WITHOUT_SKILL_SCENARIO_ID_ENV, "").strip()
    if env_value:
        return env_value

    return DEFAULT_SCENARIO_ID


def _agent_payload(data: dict[str, Any]) -> dict[str, Any]:
    filtered = dict(data)
    filtered.pop("session_id", None)
    filtered.pop("state_root", None)
    return filtered


def _agent_error_message(exc: Exception) -> str:
    message = str(exc)
    if message.startswith("Session not found:"):
        return "No active rollout state was found. The trainer must prepare the rollout session first."
    if message.startswith("Timed out waiting for session lock:"):
        return "The rollout session is busy. Retry the command."
    return message


def build_parser() -> argparse.ArgumentParser:
    shared = argparse.ArgumentParser(add_help=False)
    shared.add_argument("--data-root", type=str, default=None, help="Override the environment data directory.")
    shared.add_argument("--state-root", type=str, default=None, help="Override the session state directory.")

    agent_session = argparse.ArgumentParser(add_help=False)
    agent_session.add_argument("--session-id", type=str, default=None, help=argparse.SUPPRESS)

    parser = ProductCompetitionArgumentParser(description="Product catalog competition training environment CLI.")
    subparsers = parser.add_subparsers(dest="command", required=True, metavar="command")

    subparsers.add_parser("list-scenarios", help="List available scenarios.", parents=[shared])

    prepare = subparsers.add_parser(
        "prepare-rollout",
        aliases=["create-session"],
        help=argparse.SUPPRESS,
        parents=[shared],
    )
    prepare.add_argument("--session-id", type=str, default=None, help=argparse.SUPPRESS)
    prepare.add_argument("--scenario-id", type=str, default=None)
    prepare.add_argument("--show-bindings", action="store_true")
    prepare.add_argument("--show-task", action="store_true")
    prepare.add_argument("--overwrite", action="store_true")

    subparsers.add_parser(
        "reset-rollout",
        aliases=["reset-session"],
        help=argparse.SUPPRESS,
        parents=[shared, agent_session],
    )

    subparsers.add_parser("task", help="Show the task prompt and workspace summary.", parents=[shared, agent_session])

    list_brands_cmd = subparsers.add_parser("list-brands", help="List brands in the catalog.", parents=[shared, agent_session])
    list_brands_cmd.add_argument("--query", type=str, default="")
    list_brands_cmd.add_argument("--category-id", type=str, default=None)
    list_brands_cmd.add_argument("--limit", type=int, default=None)

    get_brand_cmd = subparsers.add_parser("get-brand", help="Get detailed brand information.", parents=[shared, agent_session])
    get_brand_cmd.add_argument("--brand-id", required=True, type=str)

    list_skus_cmd = subparsers.add_parser("list-skus", help="List SKUs with optional filters.", parents=[shared, agent_session])
    list_skus_cmd.add_argument("--brand-id", type=str, default=None)
    list_skus_cmd.add_argument("--category-id", type=str, default=None)
    list_skus_cmd.add_argument("--query", type=str, default="")
    list_skus_cmd.add_argument("--status", type=str, default="active")
    list_skus_cmd.add_argument("--limit", type=int, default=None)

    get_sku_cmd = subparsers.add_parser("get-sku", help="Get detailed SKU information.", parents=[shared, agent_session])
    get_sku_cmd.add_argument("--sku-id", required=True, type=str)

    list_price_books_cmd = subparsers.add_parser(
        "list-price-books",
        help="List available price books.",
        parents=[shared, agent_session],
    )
    list_price_books_cmd.add_argument("--status", type=str, default=None)
    list_price_books_cmd.add_argument("--current-only", action="store_true")

    get_price_book_cmd = subparsers.add_parser(
        "get-price-book",
        help="Get the full content of a price book.",
        parents=[shared, agent_session],
    )
    get_price_book_cmd.add_argument("--price-book-id", required=True, type=str)

    subparsers.add_parser("list-attachments", help="List supporting attachments.", parents=[shared, agent_session])

    read_attachment_cmd = subparsers.add_parser(
        "read-attachment",
        help="Read an attachment used by the scenario.",
        parents=[shared, agent_session],
    )
    read_attachment_cmd.add_argument("--attachment-path", required=True, type=str)

    extract_cmd = subparsers.add_parser(
        "extract-brand-catalog",
        help="Extract all SKU selling points, ingredients, and pricing for a brand into cache.",
        parents=[shared, agent_session],
    )
    extract_cmd.add_argument("--brand-id", required=True, type=str)
    extract_cmd.add_argument("--price-book-id", required=True, type=str)

    report_cmd = subparsers.add_parser(
        "generate-category-report",
        help="Generate a same-category competitor comparison report and store it in cache.",
        parents=[shared, agent_session],
    )
    report_cmd.add_argument("--brand-id", required=True, type=str)
    report_cmd.add_argument("--price-book-id", required=True, type=str)
    report_cmd.add_argument("--category-id", type=str, default=None)

    list_cache_cmd = subparsers.add_parser(
        "list-cache",
        help="List cache entries created during the session.",
        parents=[shared, agent_session],
    )
    list_cache_cmd.add_argument("--entry-type", type=str, default=None)
    list_cache_cmd.add_argument("--cache-key", type=str, default=None)
    list_cache_cmd.add_argument("--limit", type=int, default=None)

    get_cache_cmd = subparsers.add_parser(
        "get-cache-entry",
        help="Get one cached extract or report by entry id.",
        parents=[shared, agent_session],
    )
    get_cache_cmd.add_argument("--entry-id", required=True, type=str)

    subparsers.add_parser(
        "session-summary",
        help="Show session progress and summary.",
        parents=[shared, agent_session],
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    env = ProductCompetitionEnvironment(data_root=args.data_root, state_root=args.state_root)

    try:
        if args.command == "list-scenarios":
            return _print_json({"status": "success", "data": env.list_scenarios()})

        if args.command in {"prepare-rollout", "create-session"}:
            session_id = getattr(args, "session_id", None) or os.getenv(WITHOUT_SKILL_SESSION_ID_ENV, "").strip()
            session_id = session_id or _generate_session_id()
            scenario_id = _resolve_scenario_id(args)
            env.create_session(session_id, scenario_id, overwrite=args.overwrite)
            payload = {
                "session_id": session_id,
                "scenario_id": scenario_id,
                "state_root": str(env.store.state_root),
            }
            if args.show_bindings:
                payload["bindings"] = {
                    WITHOUT_SKILL_SESSION_ID_ENV: session_id,
                    WITHOUT_SKILL_STATE_ROOT_ENV: str(env.store.state_root),
                    WITHOUT_SKILL_SCENARIO_ID_ENV: scenario_id,
                }
            if args.show_task:
                payload["task"] = _agent_payload(env.get_task(session_id))
            return _print_json({"status": "success", "data": payload})

        session_id = _resolve_bound_session_id(args)

        if args.command in {"reset-rollout", "reset-session"}:
            data = env.reset_session(session_id)
            return _print_json({"status": "success", "data": _agent_payload(data)})

        if args.command == "task":
            return _print_json({"status": "success", "data": _agent_payload(env.view_task(session_id)["data"])})

        if args.command == "list-brands":
            data = env.list_brands(
                session_id,
                query=args.query,
                category_id=args.category_id,
                limit=args.limit,
            )
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "get-brand":
            data = env.get_brand(session_id, args.brand_id)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "list-skus":
            data = env.list_skus(
                session_id,
                brand_id=args.brand_id,
                category_id=args.category_id,
                query=args.query,
                status=args.status,
                limit=args.limit,
            )
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "get-sku":
            data = env.get_sku(session_id, args.sku_id)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "list-price-books":
            data = env.list_price_books(
                session_id,
                status=args.status,
                current_only=args.current_only,
            )
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "get-price-book":
            data = env.get_price_book(session_id, args.price_book_id)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "list-attachments":
            data = env.list_attachments(session_id)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "read-attachment":
            data = env.read_attachment(session_id, args.attachment_path)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "extract-brand-catalog":
            data = env.extract_brand_catalog(session_id, args.brand_id, args.price_book_id)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "generate-category-report":
            data = env.generate_category_report(
                session_id,
                args.brand_id,
                args.price_book_id,
                category_id=args.category_id,
            )
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "list-cache":
            data = env.list_cache(
                session_id,
                entry_type=args.entry_type,
                cache_key=args.cache_key,
                limit=args.limit,
            )
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "get-cache-entry":
            data = env.get_cache_entry(session_id, args.entry_id)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "session-summary":
            return _print_json({"status": "success", "data": _agent_payload(env.session_summary(session_id))})

    except Exception as exc:
        return _print_json({"status": "error", "message": _agent_error_message(exc)}, exit_code=1)

    return _print_json({"status": "error", "message": f"Unknown command: {args.command}"}, exit_code=1)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
