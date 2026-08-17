from __future__ import annotations

import argparse
import json
import os
import random
import sys
from datetime import datetime, timezone
from typing import Any

from .environment import FinanceEnvironment

FINANCE_SESSION_ID_ENV = "FINANCE_SESSION_ID"
FINANCE_STATE_ROOT_ENV = "FINANCE_STATE_ROOT"
FINANCE_SCENARIO_ID_ENV = "FINANCE_SCENARIO_ID"
DEFAULT_SCENARIO_ID = "multi_dim_brief_tech_sector"
_HIDDEN_HELP_MARKERS = ("(create-session)", "(reset-session)", "==SUPPRESS==")


def _print_json(payload: dict[str, Any], *, exit_code: int = 0) -> int:
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return exit_code


class FinanceArgumentParser(argparse.ArgumentParser):
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
    return f"fin-{_utc_stamp()}-{random.randint(1000, 9999)}"


def _resolve_bound_session_id(args: argparse.Namespace) -> str:
    explicit = getattr(args, "session_id", None)
    if explicit:
        return explicit

    env_value = os.getenv(FINANCE_SESSION_ID_ENV, "").strip()
    if env_value:
        return env_value

    raise ValueError(
        f"No active rollout session is bound. The trainer must set {FINANCE_SESSION_ID_ENV} "
        "before agent commands run."
    )


def _resolve_scenario_id(args: argparse.Namespace) -> str:
    scenario_id = getattr(args, "scenario_id", None)
    if scenario_id:
        return scenario_id

    env_value = os.getenv(FINANCE_SCENARIO_ID_ENV, "").strip()
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

    parser = FinanceArgumentParser(description="Finance training environment CLI.")
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

    list_stocks = subparsers.add_parser("list-stocks", help="List available stocks.", parents=[shared, agent_session])
    list_stocks.add_argument("--query", type=str, default="")
    list_stocks.add_argument("--sector", type=str, default=None)
    list_stocks.add_argument("--min-market-cap", type=int, default=None)
    list_stocks.add_argument("--limit", type=int, default=None)

    get_stock = subparsers.add_parser("get-stock", help="Get detailed stock information.", parents=[shared, agent_session])
    get_stock.add_argument("--symbol", required=True, type=str)

    screen_stocks = subparsers.add_parser("screen-stocks", help="Screen stocks by criteria.", parents=[shared, agent_session])
    screen_stocks.add_argument("--sector", type=str, default=None)
    screen_stocks.add_argument("--min-market-cap", type=int, default=None)
    screen_stocks.add_argument("--max-pe-ratio", type=float, default=None)
    screen_stocks.add_argument("--min-revenue-growth", type=float, default=None)
    screen_stocks.add_argument("--min-dividend-yield", type=float, default=None)
    screen_stocks.add_argument("--sort-by", type=str, default="market_cap")

    list_news = subparsers.add_parser("list-news", help="List financial news articles.", parents=[shared, agent_session])
    list_news.add_argument("--query", type=str, default="")
    list_news.add_argument("--symbol", type=str, default=None)
    list_news.add_argument("--category", type=str, default=None)
    list_news.add_argument("--limit", type=int, default=None)

    get_news = subparsers.add_parser("get-news", help="Get full news article content.", parents=[shared, agent_session])
    get_news.add_argument("--news-id", required=True, type=str)

    list_earnings = subparsers.add_parser("list-earnings", help="List earnings records.", parents=[shared, agent_session])
    list_earnings.add_argument("--symbol", type=str, default=None)
    list_earnings.add_argument("--beat-only", action="store_true")
    list_earnings.add_argument("--limit", type=int, default=None)

    get_earnings = subparsers.add_parser("get-earnings", help="Get detailed earnings information.", parents=[shared, agent_session])
    get_earnings.add_argument("--earnings-id", required=True, type=str)

    create_earnings_summary = subparsers.add_parser(
        "create-earnings-summary",
        help="Create earnings summary for multiple tickers.",
        parents=[shared, agent_session],
    )
    create_earnings_summary.add_argument("--symbols", required=True, type=str, help="Comma-separated tickers")

    list_briefs = subparsers.add_parser("list-briefs", help="List investment briefs.", parents=[shared, agent_session])
    list_briefs.add_argument("--query", type=str, default="")
    list_briefs.add_argument("--ticker", type=str, default=None)
    list_briefs.add_argument("--brief-type", type=str, default=None)
    list_briefs.add_argument("--status", type=str, default=None)
    list_briefs.add_argument("--limit", type=int, default=None)

    get_brief = subparsers.add_parser("get-brief", help="Get detailed brief content.", parents=[shared, agent_session])
    get_brief.add_argument("--brief-id", required=True, type=str)

    create_brief = subparsers.add_parser("create-brief", help="Create a new investment brief.", parents=[shared, agent_session])
    create_brief.add_argument("--ticker", required=True, type=str)
    create_brief.add_argument("--title", required=True, type=str)
    create_brief.add_argument("--brief-type", required=True, type=str)
    create_brief.add_argument("--summary", required=True, type=str)
    create_brief.add_argument("--investment-rationale", required=True, type=str, help="Comma-separated list")
    create_brief.add_argument("--risks", required=True, type=str, help="Comma-separated list")
    create_brief.add_argument("--valuation-methodology", required=True, type=str)
    create_brief.add_argument("--key-metrics", required=True, type=str, help="JSON string")

    update_brief = subparsers.add_parser("update-brief", help="Update brief content.", parents=[shared, agent_session])
    update_brief.add_argument("--brief-id", required=True, type=str)
    update_brief.add_argument("--updates", required=True, type=str, help="JSON string")

    submit_brief = subparsers.add_parser("submit-brief", help="Submit brief for review.", parents=[shared, agent_session])
    submit_brief.add_argument("--brief-id", required=True, type=str)

    review_brief = subparsers.add_parser("review-brief", help="Review a submitted brief.", parents=[shared, agent_session])
    review_brief.add_argument("--brief-id", required=True, type=str)
    review_brief.add_argument("--decision", required=True, type=str, choices=["approve", "reject", "request_changes"])
    review_brief.add_argument("--comments", type=str, default=None)

    generate_sector_overview = subparsers.add_parser(
        "generate-sector-overview",
        help="Generate sector overview report.",
        parents=[shared, agent_session],
    )
    generate_sector_overview.add_argument("--sector", required=True, type=str)

    provide_recommendations = subparsers.add_parser(
        "provide-recommendations",
        help="Get investment recommendations for tickers.",
        parents=[shared, agent_session],
    )
    provide_recommendations.add_argument("--symbols", required=True, type=str, help="Comma-separated tickers")

    subparsers.add_parser(
        "session-summary",
        help="Show session progress and summary.",
        parents=[shared, agent_session],
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    env = FinanceEnvironment(data_root=args.data_root, state_root=args.state_root)

    try:
        if args.command == "list-scenarios":
            return _print_json({"status": "success", "data": env.list_scenarios()})

        if args.command in {"prepare-rollout", "create-session"}:
            session_id = getattr(args, "session_id", None) or os.getenv(FINANCE_SESSION_ID_ENV, "").strip()
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
                    FINANCE_SESSION_ID_ENV: session_id,
                    FINANCE_STATE_ROOT_ENV: str(env.store.state_root),
                    FINANCE_SCENARIO_ID_ENV: scenario_id,
                }
            if args.show_task:
                payload["task"] = _agent_payload(env.get_task(session_id))
            return _print_json({"status": "success", "data": payload})

        session_id = _resolve_bound_session_id(args)

        if args.command in {"reset-rollout", "reset-session"}:
            data = env.reset_session(session_id)
            return _print_json({"status": "success", "data": _agent_payload(data)})

        if args.command == "task":
            return _print_json({"status": "success", "data": _agent_payload(env.get_task(session_id))})

        if args.command == "list-stocks":
            data = env.list_stocks(
                session_id,
                query=args.query,
                sector=args.sector,
                min_market_cap=args.min_market_cap,
                limit=args.limit,
            )
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "get-stock":
            data = env.get_stock(session_id, args.symbol)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "screen-stocks":
            data = env.screen_stocks(
                session_id,
                sector=args.sector,
                min_market_cap=args.min_market_cap,
                max_pe_ratio=args.max_pe_ratio,
                min_revenue_growth=args.min_revenue_growth,
                min_dividend_yield=args.min_dividend_yield,
                sort_by=args.sort_by,
            )
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "list-news":
            data = env.list_news(
                session_id,
                query=args.query,
                ticker=args.symbol,
                category=args.category,
                limit=args.limit,
            )
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "get-news":
            data = env.get_news(session_id, args.news_id)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "list-earnings":
            data = env.list_earnings(
                session_id,
                ticker=args.symbol,
                beat_only=args.beat_only,
                limit=args.limit,
            )
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "get-earnings":
            data = env.get_earnings(session_id, args.earnings_id)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "create-earnings-summary":
            tickers = [t.strip() for t in args.symbols.split(",")]
            data = env.create_earnings_summary(session_id, tickers)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "list-briefs":
            data = env.list_briefs(
                session_id,
                query=args.query,
                ticker=args.ticker,
                brief_type=args.brief_type,
                status=args.status,
                limit=args.limit,
            )
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "get-brief":
            data = env.get_brief(session_id, args.brief_id)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "create-brief":
            investment_rationale = [r.strip() for r in args.investment_rationale.split(",")]
            risks = [r.strip() for r in args.risks.split(",")]
            key_metrics = json.loads(args.key_metrics)
            data = env.create_brief(
                session_id,
                ticker=args.ticker,
                title=args.title,
                brief_type=args.brief_type,
                summary=args.summary,
                investment_rationale=investment_rationale,
                risks=risks,
                valuation_methodology=args.valuation_methodology,
                key_metrics=key_metrics,
            )
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "update-brief":
            updates = json.loads(args.updates)
            data = env.update_brief(session_id, args.brief_id, updates)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "submit-brief":
            data = env.submit_brief(session_id, args.brief_id)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "review-brief":
            data = env.review_brief(session_id, args.brief_id, args.decision, args.comments)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "generate-sector-overview":
            data = env.generate_sector_overview(session_id, args.sector)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "provide-recommendations":
            tickers = [t.strip() for t in args.symbols.split(",")]
            data = env.provide_recommendations(session_id, tickers)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "session-summary":
            return _print_json({"status": "success", "data": _agent_payload(env.session_summary(session_id))})

    except Exception as exc:
        return _print_json({"status": "error", "message": _agent_error_message(exc)}, exit_code=1)

    return _print_json({"status": "error", "message": f"Unknown command: {args.command}"}, exit_code=1)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
