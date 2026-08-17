from __future__ import annotations

import argparse
import json
import os
import random
import sys
from datetime import datetime, timezone
from typing import Any

from .environment import CompeteTrackEnvironment

COMPETE_TRACK_SESSION_ID_ENV = "COMPETE_TRACK_SESSION_ID"
COMPETE_TRACK_STATE_ROOT_ENV = "COMPETE_TRACK_STATE_ROOT"
COMPETE_TRACK_SCENARIO_ID_ENV = "COMPETE_TRACK_SCENARIO_ID"
DEFAULT_SCENARIO_ID = "competitor_monitoring_q2_2026"
_HIDDEN_HELP_MARKERS = ("(create-session)", "(reset-session)", "==SUPPRESS==")


def _print_json(payload: dict[str, Any], *, exit_code: int = 0) -> int:
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return exit_code


class CompeteTrackArgumentParser(argparse.ArgumentParser):
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
    return f"ct-{_utc_stamp()}-{random.randint(1000, 9999)}"


def _resolve_bound_session_id(args: argparse.Namespace) -> str:
    explicit = getattr(args, "session_id", None)
    if explicit:
        return explicit

    env_value = os.getenv(COMPETE_TRACK_SESSION_ID_ENV, "").strip()
    if env_value:
        return env_value

    raise ValueError(
        f"No active rollout session is bound. The trainer must set {COMPETE_TRACK_SESSION_ID_ENV} "
        "before agent commands run."
    )


def _resolve_scenario_id(args: argparse.Namespace) -> str:
    scenario_id = getattr(args, "scenario_id", None)
    if scenario_id:
        return scenario_id

    env_value = os.getenv(COMPETE_TRACK_SCENARIO_ID_ENV, "").strip()
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

    parser = CompeteTrackArgumentParser(description="Competition Tracking environment CLI.")
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

    list_competitors = subparsers.add_parser("list-competitors", help="List competitors.", parents=[shared, agent_session])
    list_competitors.add_argument("--query", type=str, default="")
    list_competitors.add_argument("--sector", type=str, default=None)
    list_competitors.add_argument("--min-market-share", type=float, default=None)
    list_competitors.add_argument("--sort-by", type=str, default="market_cap")

    get_competitor = subparsers.add_parser("get-competitor", help="Get competitor details.", parents=[shared, agent_session])
    get_competitor.add_argument("--competitor-id", required=True, type=str)

    screen_competitors = subparsers.add_parser("screen-competitors", help="Screen competitors by criteria.", parents=[shared, agent_session])
    screen_competitors.add_argument("--min-market-cap", type=int, default=None)
    screen_competitors.add_argument("--max-market-cap", type=int, default=None)
    screen_competitors.add_argument("--min-market-share", type=float, default=None)
    screen_competitors.add_argument("--min-revenue-growth", type=float, default=None)
    screen_competitors.add_argument("--sectors", type=str, default=None, help="Comma-separated list")
    screen_competitors.add_argument("--sort-by", type=str, default="market_cap")

    compare_competitors = subparsers.add_parser("compare-competitors", help="Compare competitors.", parents=[shared, agent_session])
    compare_competitors.add_argument("--competitor-ids", required=True, type=str, help="Comma-separated list")
    compare_competitors.add_argument("--metrics", type=str, default=None, help="Comma-separated list")

    list_policies = subparsers.add_parser("list-policies", help="List regulatory policies.", parents=[shared, agent_session])
    list_policies.add_argument("--query", type=str, default="")
    list_policies.add_argument("--policy-type", type=str, default=None)
    list_policies.add_argument("--jurisdiction", type=str, default=None)
    list_policies.add_argument("--status", type=str, default=None)
    list_policies.add_argument("--impact-level", type=str, default=None)
    list_policies.add_argument("--limit", type=int, default=None)

    get_policy = subparsers.add_parser("get-policy", help="Get policy details.", parents=[shared, agent_session])
    get_policy.add_argument("--policy-id", required=True, type=str)

    get_policy_impact = subparsers.add_parser("get-policy-impact", help="Get policy impact analysis.", parents=[shared, agent_session])
    get_policy_impact.add_argument("--policy-id", required=True, type=str)
    get_policy_impact.add_argument("--competitor-ids", type=str, default=None, help="Comma-separated list")

    filter_policies_by_competitor = subparsers.add_parser("filter-policies-by-competitor", help="Filter policies by competitor.", parents=[shared, agent_session])
    filter_policies_by_competitor.add_argument("--competitor-id", required=True, type=str)
    filter_policies_by_competitor.add_argument("--impact-level", type=str, default=None)

    get_regulatory_risks = subparsers.add_parser("get-regulatory-risks", help="Get regulatory risks.", parents=[shared, agent_session])
    get_regulatory_risks.add_argument("--competitor-id", type=str, default=None)
    get_regulatory_risks.add_argument("--min-impact-level", type=str, default="medium")

    list_users = subparsers.add_parser("list-users", help="List users.", parents=[shared, agent_session])
    list_users.add_argument("--query", type=str, default="")
    list_users.add_argument("--acquisition-source", type=str, default=None)
    list_users.add_argument("--user-tier", type=str, default=None)
    list_users.add_argument("--cohort", type=str, default=None)
    list_users.add_argument("--limit", type=int, default=None)

    get_user = subparsers.add_parser("get-user", help="Get user details.", parents=[shared, agent_session])
    get_user.add_argument("--user-id", required=True, type=str)

    screen_users = subparsers.add_parser("screen-users", help="Screen users by criteria.", parents=[shared, agent_session])
    screen_users.add_argument("--min-lifetime-value", type=float, default=None)
    screen_users.add_argument("--min-engagement-score", type=float, default=None)
    screen_users.add_argument("--user-tiers", type=str, default=None, help="Comma-separated list")
    screen_users.add_argument("--acquisition-sources", type=str, default=None, help="Comma-separated list")
    screen_users.add_argument("--sort-by", type=str, default="lifetime_value")

    update_user_tier = subparsers.add_parser("update-user-tier", help="Update user tier.", parents=[shared, agent_session])
    update_user_tier.add_argument("--user-id", required=True, type=str)
    update_user_tier.add_argument("--new-tier", required=True, type=str)
    update_user_tier.add_argument("--reason", required=True, type=str)

    analyze_acquisition_sources = subparsers.add_parser("analyze-acquisition-sources", help="Analyze acquisition sources.", parents=[shared, agent_session])

    generate_competitive_landscape = subparsers.add_parser("generate-competitive-landscape", help="Generate competitive landscape.", parents=[shared, agent_session])
    generate_competitive_landscape.add_argument("--competitor-ids", required=True, type=str, help="Comma-separated list")

    generate_regulatory_summary = subparsers.add_parser("generate-regulatory-summary", help="Generate regulatory summary.", parents=[shared, agent_session])
    generate_regulatory_summary.add_argument("--competitor-ids", type=str, default=None, help="Comma-separated list")
    generate_regulatory_summary.add_argument("--impact-filter", type=str, default=None)

    generate_user_acquisition_analysis = subparsers.add_parser("generate-user-acquisition-analysis", help="Generate user acquisition analysis.", parents=[shared, agent_session])
    generate_user_acquisition_analysis.add_argument("--cohort-filter", type=str, default=None)

    list_reports = subparsers.add_parser("list-reports", help="List reports.", parents=[shared, agent_session])
    list_reports.add_argument("--report-type", type=str, default=None)
    list_reports.add_argument("--status", type=str, default=None)
    list_reports.add_argument("--limit", type=int, default=None)

    create_market_report = subparsers.add_parser("create-market-report", help="Create market report.", parents=[shared, agent_session])
    create_market_report.add_argument("--title", required=True, type=str)
    create_market_report.add_argument("--report-type", required=True, type=str)
    create_market_report.add_argument("--competitor-ids", required=True, type=str, help="Comma-separated list")
    create_market_report.add_argument("--include-sections", required=True, type=str, help="Comma-separated list")
    create_market_report.add_argument("--findings", required=True, type=str, help="Comma-separated list")

    finalize_report = subparsers.add_parser("finalize-report", help="Finalize report.", parents=[shared, agent_session])
    finalize_report.add_argument("--report-id", required=True, type=str)

    list_alerts = subparsers.add_parser("list-alerts", help="List alerts.", parents=[shared, agent_session])
    list_alerts.add_argument("--alert-type", type=str, default=None)
    list_alerts.add_argument("--severity", type=str, default=None)
    list_alerts.add_argument("--acknowledged", type=str, default=None, choices=["true", "false"])
    list_alerts.add_argument("--limit", type=int, default=None)

    create_alert = subparsers.add_parser("create-alert", help="Create alert.", parents=[shared, agent_session])
    create_alert.add_argument("--alert-type", required=True, type=str)
    create_alert.add_argument("--title", required=True, type=str)
    create_alert.add_argument("--description", required=True, type=str)
    create_alert.add_argument("--severity", required=True, type=str)
    create_alert.add_argument("--related-competitor-id", type=str, default=None)
    create_alert.add_argument("--related-policy-id", type=str, default=None)

    acknowledge_alert = subparsers.add_parser("acknowledge-alert", help="Acknowledge alert.", parents=[shared, agent_session])
    acknowledge_alert.add_argument("--alert-id", required=True, type=str)
    acknowledge_alert.add_argument("--acknowledged-by", required=True, type=str)
    acknowledge_alert.add_argument("--notes", type=str, default=None)

    subparsers.add_parser("session-summary", help="Show session progress and summary.", parents=[shared, agent_session])

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    env = CompeteTrackEnvironment(data_root=args.data_root, state_root=args.state_root)

    try:
        if args.command == "list-scenarios":
            return _print_json({"status": "success", "data": env.list_scenarios()})

        if args.command in {"prepare-rollout", "create-session"}:
            session_id = getattr(args, "session_id", None) or os.getenv(COMPETE_TRACK_SESSION_ID_ENV, "").strip()
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
                    COMPETE_TRACK_SESSION_ID_ENV: session_id,
                    COMPETE_TRACK_STATE_ROOT_ENV: str(env.store.state_root),
                    COMPETE_TRACK_SCENARIO_ID_ENV: scenario_id,
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

        if args.command == "list-competitors":
            data = env.list_competitors(session_id, query=args.query, sector=args.sector, min_market_share=args.min_market_share, sort_by=args.sort_by)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "get-competitor":
            data = env.get_competitor(session_id, args.competitor_id)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "screen-competitors":
            sectors = args.sectors.split(",") if args.sectors else None
            data = env.screen_competitors(session_id, min_market_cap=args.min_market_cap, max_market_cap=args.max_market_cap, min_market_share=args.min_market_share, min_revenue_growth=args.min_revenue_growth, sectors=sectors, sort_by=args.sort_by)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "compare-competitors":
            competitor_ids = [c.strip() for c in args.competitor_ids.split(",")]
            metrics = [m.strip() for m in args.metrics.split(",")] if args.metrics else None
            data = env.compare_competitors(session_id, competitor_ids, metrics)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "list-policies":
            data = env.list_policies(session_id, query=args.query, policy_type=args.policy_type, jurisdiction=args.jurisdiction, status=args.status, impact_level=args.impact_level, limit=args.limit)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "get-policy":
            data = env.get_policy(session_id, args.policy_id)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "get-policy-impact":
            competitor_ids = [c.strip() for c in args.competitor_ids.split(",")] if args.competitor_ids else None
            data = env.get_policy_impact(session_id, args.policy_id, competitor_ids)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "filter-policies-by-competitor":
            data = env.filter_policies_by_competitor(session_id, args.competitor_id, impact_level=args.impact_level)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "get-regulatory-risks":
            data = env.get_regulatory_risks(session_id, args.competitor_id, args.min_impact_level)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "list-users":
            data = env.list_users(session_id, query=args.query, acquisition_source=args.acquisition_source, user_tier=args.user_tier, cohort=args.cohort, limit=args.limit)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "get-user":
            data = env.get_user(session_id, args.user_id)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "screen-users":
            user_tiers = [t.strip() for t in args.user_tiers.split(",")] if args.user_tiers else None
            acquisition_sources = [s.strip() for s in args.acquisition_sources.split(",")] if args.acquisition_sources else None
            data = env.screen_users(session_id, min_lifetime_value=args.min_lifetime_value, min_engagement_score=args.min_engagement_score, user_tiers=user_tiers, acquisition_sources=acquisition_sources, sort_by=args.sort_by)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "update-user-tier":
            data = env.update_user_tier(session_id, args.user_id, args.new_tier, args.reason)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "analyze-acquisition-sources":
            data = env.analyze_acquisition_sources(session_id)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "generate-competitive-landscape":
            competitor_ids = [c.strip() for c in args.competitor_ids.split(",")]
            data = env.generate_competitive_landscape(session_id, competitor_ids)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "generate-regulatory-summary":
            competitor_ids = [c.strip() for c in args.competitor_ids.split(",")] if args.competitor_ids else None
            data = env.generate_regulatory_summary(session_id, competitor_ids, args.impact_filter)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "generate-user-acquisition-analysis":
            data = env.generate_user_acquisition_analysis(session_id, args.cohort_filter)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "list-reports":
            data = env.list_reports(session_id, report_type=args.report_type, status=args.status, limit=args.limit)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "create-market-report":
            competitor_ids = [c.strip() for c in args.competitor_ids.split(",")]
            include_sections = [s.strip() for s in args.include_sections.split(",")]
            findings = [f.strip() for f in args.findings.split(",")]
            data = env.create_market_report(session_id, args.title, args.report_type, competitor_ids, include_sections, findings)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "finalize-report":
            data = env.finalize_report(session_id, args.report_id)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "list-alerts":
            acknowledged = None
            if args.acknowledged is not None:
                acknowledged = args.acknowledged.lower() == "true"
            data = env.list_alerts(session_id, alert_type=args.alert_type, severity=args.severity, acknowledged=acknowledged, limit=args.limit)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "create-alert":
            data = env.create_alert(session_id, args.alert_type, args.title, args.description, args.severity, args.related_competitor_id, args.related_policy_id)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "acknowledge-alert":
            data = env.acknowledge_alert(session_id, args.alert_id, args.acknowledged_by, args.notes)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "session-summary":
            return _print_json({"status": "success", "data": _agent_payload(env.session_summary(session_id))})

    except Exception as exc:
        return _print_json({"status": "error", "message": _agent_error_message(exc)}, exit_code=1)

    return _print_json({"status": "error", "message": f"Unknown command: {args.command}"}, exit_code=1)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
