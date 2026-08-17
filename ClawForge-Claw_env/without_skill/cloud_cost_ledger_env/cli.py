from __future__ import annotations

import argparse
import json
import os
import random
import sys
from datetime import datetime, timezone
from typing import Any

from .environment import CloudCostLedgerEnvironment


CLOUD_COST_LEDGER_SESSION_ID_ENV = "CLOUD_COST_LEDGER_SESSION_ID"
CLOUD_COST_LEDGER_STATE_ROOT_ENV = "CLOUD_COST_LEDGER_STATE_ROOT"
CLOUD_COST_LEDGER_SCENARIO_ID_ENV = "CLOUD_COST_LEDGER_SCENARIO_ID"
DEFAULT_SCENARIO_ID = "cloud_cluster_monthly_cost_q2_2026"
_HIDDEN_HELP_MARKERS = ("(create-session)", "(reset-session)", "==SUPPRESS==")


def _print_json(payload: dict[str, Any], *, exit_code: int = 0) -> int:
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return exit_code


class CloudCostLedgerArgumentParser(argparse.ArgumentParser):
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
    return f"cloud-cost-{_utc_stamp()}-{random.randint(1000, 9999)}"


def _resolve_bound_session_id(args: argparse.Namespace) -> str:
    explicit = getattr(args, "session_id", None)
    if explicit:
        return explicit

    env_value = os.getenv(CLOUD_COST_LEDGER_SESSION_ID_ENV, "").strip()
    if env_value:
        return env_value

    raise ValueError(
        f"No active rollout session is bound. The trainer must set {CLOUD_COST_LEDGER_SESSION_ID_ENV} "
        "before agent commands run."
    )


def _resolve_scenario_id(args: argparse.Namespace) -> str:
    explicit = getattr(args, "scenario_id", None)
    if explicit:
        return explicit

    env_value = os.getenv(CLOUD_COST_LEDGER_SCENARIO_ID_ENV, "").strip()
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


def _parse_csv_list(value: str | None) -> list[str] | None:
    if value is None:
        return None
    items = [item.strip() for item in value.split(",") if item.strip()]
    return items or None


def build_parser() -> argparse.ArgumentParser:
    shared = argparse.ArgumentParser(add_help=False)
    shared.add_argument("--data-root", type=str, default=None, help="Override the environment data directory.")
    shared.add_argument("--state-root", type=str, default=None, help="Override the session state directory.")

    agent_session = argparse.ArgumentParser(add_help=False)
    agent_session.add_argument("--session-id", type=str, default=None, help=argparse.SUPPRESS)

    parser = CloudCostLedgerArgumentParser(description="Cloud cost ledger training environment CLI.")
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

    list_clusters_cmd = subparsers.add_parser(
        "list-clusters",
        help="List available clusters from the simulated ledger scope.",
        parents=[shared, agent_session],
    )
    list_clusters_cmd.add_argument("--query", type=str, default="")
    list_clusters_cmd.add_argument("--domain", type=str, default=None)
    list_clusters_cmd.add_argument("--cluster-role", type=str, default=None)
    list_clusters_cmd.add_argument("--environment", type=str, default=None)
    list_clusters_cmd.add_argument("--limit", type=int, default=None)

    get_cluster_cmd = subparsers.add_parser(
        "get-cluster",
        help="Get detailed cluster metadata.",
        parents=[shared, agent_session],
    )
    get_cluster_cmd.add_argument("--cluster-id", required=True, type=str)

    list_ledger_cmd = subparsers.add_parser(
        "list-ledger-entries",
        help="List resource ledger entries with optional filters.",
        parents=[shared, agent_session],
    )
    list_ledger_cmd.add_argument("--cluster-id", type=str, default=None)
    list_ledger_cmd.add_argument("--resource-family", type=str, default=None)
    list_ledger_cmd.add_argument("--metric-code", type=str, default=None)
    list_ledger_cmd.add_argument("--limit", type=int, default=None)

    get_ledger_cmd = subparsers.add_parser(
        "get-ledger-entry",
        help="Get one resource ledger entry by id.",
        parents=[shared, agent_session],
    )
    get_ledger_cmd.add_argument("--entry-id", required=True, type=str)

    list_pricing_cmd = subparsers.add_parser(
        "list-pricing-catalogs",
        help="List pricing catalogs available to the scenario.",
        parents=[shared, agent_session],
    )
    list_pricing_cmd.add_argument("--status", type=str, default=None)
    list_pricing_cmd.add_argument("--current-only", action="store_true")

    get_pricing_cmd = subparsers.add_parser(
        "get-pricing-catalog",
        help="Get the full content of a pricing catalog.",
        parents=[shared, agent_session],
    )
    get_pricing_cmd.add_argument("--catalog-id", required=True, type=str)

    subparsers.add_parser("list-attachments", help="List supporting attachments.", parents=[shared, agent_session])

    read_attachment_cmd = subparsers.add_parser(
        "read-attachment",
        help="Read a scenario attachment.",
        parents=[shared, agent_session],
    )
    read_attachment_cmd.add_argument("--attachment-path", required=True, type=str)

    aggregate_cmd = subparsers.add_parser(
        "aggregate-cluster-usage",
        help="Aggregate compute and storage usage for one cluster into cache.",
        parents=[shared, agent_session],
    )
    aggregate_cmd.add_argument("--cluster-id", required=True, type=str)

    report_cmd = subparsers.add_parser(
        "generate-cost-report",
        help="Generate a monthly cluster cost detail report and store it in cache.",
        parents=[shared, agent_session],
    )
    report_cmd.add_argument("--catalog-id", required=True, type=str)
    report_cmd.add_argument(
        "--cluster-ids",
        type=str,
        default=None,
        help="Optional comma-separated cluster ids. Defaults to all business clusters in the session.",
    )
    report_cmd.add_argument("--billing-month", type=str, default=None)

    list_cache_cmd = subparsers.add_parser(
        "list-cache",
        help="List cached aggregates and reports created during the session.",
        parents=[shared, agent_session],
    )
    list_cache_cmd.add_argument("--entry-type", type=str, default=None)
    list_cache_cmd.add_argument("--cache-key", type=str, default=None)
    list_cache_cmd.add_argument("--limit", type=int, default=None)

    get_cache_cmd = subparsers.add_parser(
        "get-cache-entry",
        help="Get one cached aggregate or report by entry id.",
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
    env = CloudCostLedgerEnvironment(data_root=args.data_root, state_root=args.state_root)

    try:
        if args.command == "list-scenarios":
            return _print_json({"status": "success", "data": env.list_scenarios()})

        if args.command in {"prepare-rollout", "create-session"}:
            session_id = getattr(args, "session_id", None) or os.getenv(CLOUD_COST_LEDGER_SESSION_ID_ENV, "").strip()
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
                    CLOUD_COST_LEDGER_SESSION_ID_ENV: session_id,
                    CLOUD_COST_LEDGER_STATE_ROOT_ENV: str(env.store.state_root),
                    CLOUD_COST_LEDGER_SCENARIO_ID_ENV: scenario_id,
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

        if args.command == "list-clusters":
            data = env.list_clusters(
                session_id,
                query=args.query,
                domain=args.domain,
                cluster_role=args.cluster_role,
                environment=args.environment,
                limit=args.limit,
            )
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "get-cluster":
            data = env.get_cluster(session_id, args.cluster_id)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "list-ledger-entries":
            data = env.list_ledger_entries(
                session_id,
                cluster_id=args.cluster_id,
                resource_family=args.resource_family,
                metric_code=args.metric_code,
                limit=args.limit,
            )
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "get-ledger-entry":
            data = env.get_ledger_entry(session_id, args.entry_id)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "list-pricing-catalogs":
            data = env.list_pricing_catalogs(
                session_id,
                status=args.status,
                current_only=args.current_only,
            )
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "get-pricing-catalog":
            data = env.get_pricing_catalog(session_id, args.catalog_id)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "list-attachments":
            data = env.list_attachments(session_id)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "read-attachment":
            data = env.read_attachment(session_id, args.attachment_path)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "aggregate-cluster-usage":
            data = env.aggregate_cluster_usage(session_id, args.cluster_id)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "generate-cost-report":
            data = env.generate_cost_report(
                session_id,
                args.catalog_id,
                cluster_ids=_parse_csv_list(args.cluster_ids),
                billing_month=args.billing_month,
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
