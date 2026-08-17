from __future__ import annotations

import argparse
import json
import os
import random
import sys
from datetime import datetime, timezone
from typing import Any

from .environment import LogisticsEnvironment

LOGISTICS_SESSION_ID_ENV = "LOGISTICS_SESSION_ID"
LOGISTICS_SCENARIO_ID_ENV = "LOGISTICS_SCENARIO_ID"
DEFAULT_SCENARIO_ID = "fulfillment_inventory_reconcile"
_HIDDEN_HELP_MARKERS = ("(create-session)", "(reset-session)", "==SUPPRESS==")


def _print_json(payload: dict[str, Any], *, exit_code: int = 0) -> int:
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return exit_code


class LogisticsArgumentParser(argparse.ArgumentParser):
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
    return f"le-{_utc_stamp()}-{random.randint(1000, 9999)}"


def _resolve_bound_session_id(args: argparse.Namespace) -> str:
    explicit = getattr(args, "session_id", None)
    if explicit:
        return explicit

    env_value = os.getenv(LOGISTICS_SESSION_ID_ENV, "").strip()
    if env_value:
        return env_value

    raise ValueError(
        f"No active rollout session is bound. The trainer must set {LOGISTICS_SESSION_ID_ENV} "
        "before agent commands run."
    )


def _resolve_scenario_id(args: argparse.Namespace) -> str:
    scenario_id = getattr(args, "scenario_id", None)
    if scenario_id:
        return scenario_id

    env_value = os.getenv(LOGISTICS_SCENARIO_ID_ENV, "").strip()
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

    parser = LogisticsArgumentParser(description="Logistics Envs CLI - Order processing, returns, and inventory reconciliation.")
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

    list_orders = subparsers.add_parser("list-orders", help="List orders.", parents=[shared, agent_session])
    list_orders.add_argument("--query", type=str, default="")
    list_orders.add_argument("--status", type=str, default=None)
    list_orders.add_argument("--customer-id", type=str, default=None)
    list_orders.add_argument("--limit", type=int, default=None)

    get_order = subparsers.add_parser("get-order", help="Get order details.", parents=[shared, agent_session])
    get_order.add_argument("--order-id", required=True, type=str)

    update_order = subparsers.add_parser("update-order-status", help="Update order status.", parents=[shared, agent_session])
    update_order.add_argument("--order-id", required=True, type=str)
    update_order.add_argument("--new-status", required=True, type=str)

    list_shipments = subparsers.add_parser("list-shipments", help="List shipments.", parents=[shared, agent_session])
    list_shipments.add_argument("--query", type=str, default="")
    list_shipments.add_argument("--status", type=str, default=None)
    list_shipments.add_argument("--carrier", type=str, default=None)
    list_shipments.add_argument("--limit", type=int, default=None)

    get_shipment = subparsers.add_parser("get-shipment", help="Get shipment details.", parents=[shared, agent_session])
    get_shipment.add_argument("--shipment-id", required=True, type=str)

    update_shipment = subparsers.add_parser("update-shipment-status", help="Update shipment status.", parents=[shared, agent_session])
    update_shipment.add_argument("--shipment-id", required=True, type=str)
    update_shipment.add_argument("--new-status", required=True, type=str)
    update_shipment.add_argument("--tracking-number", type=str, default=None)
    update_shipment.add_argument("--current-location", type=str, default=None)

    list_returns = subparsers.add_parser("list-returns", help="List returns.", parents=[shared, agent_session])
    list_returns.add_argument("--query", type=str, default="")
    list_returns.add_argument("--status", type=str, default=None)
    list_returns.add_argument("--customer-id", type=str, default=None)
    list_returns.add_argument("--limit", type=int, default=None)

    get_return = subparsers.add_parser("get-return", help="Get return details.", parents=[shared, agent_session])
    get_return.add_argument("--return-id", required=True, type=str)

    approve_ret = subparsers.add_parser("approve-return", help="Approve a return.", parents=[shared, agent_session])
    approve_ret.add_argument("--return-id", required=True, type=str)
    approve_ret.add_argument("--notes", type=str, default=None)

    reject_ret = subparsers.add_parser("reject-return", help="Reject a return.", parents=[shared, agent_session])
    reject_ret.add_argument("--return-id", required=True, type=str)
    reject_ret.add_argument("--reason", required=True, type=str)

    inspect_ret = subparsers.add_parser("inspect-return", help="Inspect a return.", parents=[shared, agent_session])
    inspect_ret.add_argument("--return-id", required=True, type=str)
    inspect_ret.add_argument("--inspection-notes", required=True, type=str)
    inspect_ret.add_argument("--resolution", required=True, type=str)
    inspect_ret.add_argument("--condition", type=str, default="acceptable")

    receive_ret = subparsers.add_parser("receive-return", help="Mark return as received.", parents=[shared, agent_session])
    receive_ret.add_argument("--return-id", required=True, type=str)

    list_inventory = subparsers.add_parser("list-inventory", help="List inventory.", parents=[shared, agent_session])
    list_inventory.add_argument("--query", type=str, default="")
    list_inventory.add_argument("--category", type=str, default=None)
    list_inventory.add_argument("--warehouse-id", type=str, default=None)
    list_inventory.add_argument("--low-stock-only", action="store_true")
    list_inventory.add_argument("--limit", type=int, default=None)

    get_inventory = subparsers.add_parser("get-inventory", help="Get inventory item details.", parents=[shared, agent_session])
    get_inventory.add_argument("--sku", required=True, type=str)

    adjust_inv = subparsers.add_parser("adjust-inventory", help="Adjust inventory level.", parents=[shared, agent_session])
    adjust_inv.add_argument("--sku", required=True, type=str)
    adjust_inv.add_argument("--warehouse-id", required=True, type=str)
    adjust_inv.add_argument("--quantity-change", required=True, type=int)
    adjust_inv.add_argument("--reason-code", required=True, type=str)
    adjust_inv.add_argument("--notes", type=str, default=None)

    reserve_inv = subparsers.add_parser("reserve-inventory", help="Reserve inventory.", parents=[shared, agent_session])
    reserve_inv.add_argument("--sku", required=True, type=str)
    reserve_inv.add_argument("--warehouse-id", required=True, type=str)
    reserve_inv.add_argument("--quantity", required=True, type=int)

    gen_report = subparsers.add_parser("generate-reconciliation-report", help="Generate reconciliation report.", parents=[shared, agent_session])
    gen_report.add_argument("--warehouse-id", type=str, default=None)

    read_att = subparsers.add_parser("read-attachment", help="Read an attachment.", parents=[shared, agent_session])
    read_att.add_argument("--attachment-id", required=True, type=str)

    subparsers.add_parser(
        "session-summary",
        help="Show session progress and summary.",
        parents=[shared, agent_session],
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    env = LogisticsEnvironment(data_root=args.data_root, state_root=args.state_root)

    try:
        if args.command == "list-scenarios":
            return _print_json({"status": "success", "data": env.list_scenarios()})

        if args.command in {"prepare-rollout", "create-session"}:
            session_id = getattr(args, "session_id", None) or os.getenv(LOGISTICS_SESSION_ID_ENV, "").strip()
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
                    LOGISTICS_SESSION_ID_ENV: session_id,
                    "LOGISTICS_STATE_ROOT": str(env.store.state_root),
                    LOGISTICS_SCENARIO_ID_ENV: scenario_id,
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

        if args.command == "list-orders":
            data = env.list_orders(
                session_id,
                query=args.query,
                status=args.status,
                customer_id=args.customer_id,
                limit=args.limit,
            )
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "get-order":
            data = env.get_order(session_id, args.order_id)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "update-order-status":
            data = env.update_order_status(session_id, args.order_id, args.new_status)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "list-shipments":
            data = env.list_shipments(
                session_id,
                query=args.query,
                status=args.status,
                carrier=args.carrier,
                limit=args.limit,
            )
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "get-shipment":
            data = env.get_shipment(session_id, args.shipment_id)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "update-shipment-status":
            data = env.update_shipment_status(
                session_id,
                args.shipment_id,
                args.new_status,
                tracking_number=args.tracking_number,
                current_location=args.current_location,
            )
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "list-returns":
            data = env.list_returns(
                session_id,
                query=args.query,
                status=args.status,
                customer_id=args.customer_id,
                limit=args.limit,
            )
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "get-return":
            data = env.get_return(session_id, args.return_id)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "approve-return":
            data = env.approve_return(session_id, args.return_id, notes=args.notes)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "reject-return":
            data = env.reject_return(session_id, args.return_id, reason=args.reason)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "inspect-return":
            data = env.inspect_return(
                session_id,
                args.return_id,
                inspection_notes=args.inspection_notes,
                resolution=args.resolution,
                condition=args.condition,
            )
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "receive-return":
            data = env.receive_return(session_id, args.return_id)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "list-inventory":
            data = env.list_inventory(
                session_id,
                query=args.query,
                category=args.category,
                warehouse_id=args.warehouse_id,
                low_stock_only=args.low_stock_only,
                limit=args.limit,
            )
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "get-inventory":
            data = env.get_inventory_item(session_id, args.sku)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "adjust-inventory":
            data = env.adjust_inventory(
                session_id,
                sku=args.sku,
                warehouse_id=args.warehouse_id,
                quantity_change=args.quantity_change,
                reason_code=args.reason_code,
                notes=args.notes,
            )
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "reserve-inventory":
            data = env.reserve_inventory(
                session_id,
                sku=args.sku,
                warehouse_id=args.warehouse_id,
                quantity=args.quantity,
            )
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "generate-reconciliation-report":
            data = env.generate_reconciliation_report(session_id, warehouse_id=args.warehouse_id)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "read-attachment":
            data = env.read_attachment(session_id, args.attachment_id)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "session-summary":
            return _print_json({"status": "success", "data": _agent_payload(env.session_summary(session_id))})

    except Exception as exc:
        return _print_json({"status": "error", "message": _agent_error_message(exc)}, exit_code=1)

    return _print_json({"status": "error", "message": f"Unknown command: {args.command}"}, exit_code=1)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
