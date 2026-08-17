from __future__ import annotations

import argparse
import json
import os
import random
import sys
from datetime import datetime, timezone
from typing import Any

from .environment import TravelPolicyEnvironment

TRAVEL_POLICY_SESSION_ID_ENV = "TRAVEL_POLICY_SESSION_ID"
TRAVEL_POLICY_SCENARIO_ID_ENV = "TRAVEL_POLICY_SCENARIO_ID"
DEFAULT_SCENARIO_ID = "q2_business_travel_2026"
_HIDDEN_HELP_MARKERS = ("prepare-rollout", "reset-rollout", "==SUPPRESS==")


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _generate_session_id() -> str:
    return f"tp-{_utc_stamp()}-{random.randint(1000, 9999)}"


class TravelPolicyArgumentParser(argparse.ArgumentParser):
    def format_help(self) -> str:
        help_text = super().format_help()
        lines = [
            line
            for line in help_text.splitlines()
            if not any(marker in line for marker in _HIDDEN_HELP_MARKERS)
        ]
        return "\n".join(lines) + ("\n" if help_text.endswith("\n") else "")


def _get_env() -> TravelPolicyEnvironment:
    env = TravelPolicyEnvironment()
    session_id = os.environ.get(TRAVEL_POLICY_SESSION_ID_ENV, "").strip()
    if session_id:
        env.bind_session(session_id)
    return env


def _print_json(payload: dict[str, Any], *, exit_code: int = 0) -> int:
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return exit_code


def _resolve_bound_session_id(args: argparse.Namespace) -> str:
    explicit = getattr(args, "session_id", None)
    if explicit:
        return explicit
    env_value = os.environ.get(TRAVEL_POLICY_SESSION_ID_ENV, "").strip()
    if env_value:
        return env_value
    raise ValueError(
        f"No active rollout session is bound. The trainer must set {TRAVEL_POLICY_SESSION_ID_ENV} "
        "before agent commands run."
    )


def _resolve_scenario_id(args: argparse.Namespace) -> str:
    scenario_id = getattr(args, "scenario_id", None)
    if scenario_id:
        return scenario_id
    env_value = os.environ.get(TRAVEL_POLICY_SCENARIO_ID_ENV, "").strip()
    if env_value:
        return env_value
    return DEFAULT_SCENARIO_ID


def _add_common_args(parser: TravelPolicyArgumentParser):
    parser.add_argument("--event-at", default="", help="Event timestamp")


def cmd_list_scenarios(args):
    env = _get_env()
    scenarios = env.list_scenarios()
    return _print_json({"status": "success", "data": scenarios})


def cmd_prepare_rollout(args):
    env = _get_env()
    session_id = getattr(args, "session_id", None) or os.getenv(TRAVEL_POLICY_SESSION_ID_ENV, "").strip()
    session_id = session_id or _generate_session_id()
    scenario_id = _resolve_scenario_id(args)
    env.prepare_rollout(session_id, scenario_id)
    return _print_json({
        "status": "success",
        "data": {
            "session_id": session_id,
            "scenario_id": scenario_id,
            "state_root": str(env.store.state_root) if hasattr(env, 'store') and hasattr(env.store, 'state_root') else "",
        }
    })


def cmd_reset_rollout(args):
    env = _get_env()
    result = env.reset_rollout()
    print(result["message"])


def _comma_split(val: str) -> list[str]:
    return [x.strip() for x in val.split(",") if x.strip()]


cmd_list_platforms_parser = TravelPolicyArgumentParser(add_help=False)
cmd_list_platforms_parser.add_argument("--event-at", default="")

cmd_get_platform_parser = TravelPolicyArgumentParser(add_help=False)
_add_common_args(cmd_get_platform_parser)
cmd_get_platform_parser.add_argument("--platform-id", required=True)

cmd_search_flights_parser = TravelPolicyArgumentParser(add_help=False)
_add_common_args(cmd_search_flights_parser)
cmd_search_flights_parser.add_argument("--platform-id", required=True)
cmd_search_flights_parser.add_argument("--origin", required=True)
cmd_search_flights_parser.add_argument("--destination", required=True)
cmd_search_flights_parser.add_argument("--departure-date", required=True)
cmd_search_flights_parser.add_argument("--return-date")
cmd_search_flights_parser.add_argument("--cabin-class", default="economy")
cmd_search_flights_parser.add_argument("--passengers", type=int, default=1)

cmd_compare_prices_parser = TravelPolicyArgumentParser(add_help=False)
_add_common_args(cmd_compare_prices_parser)
cmd_compare_prices_parser.add_argument("--origin", required=True)
cmd_compare_prices_parser.add_argument("--destination", required=True)
cmd_compare_prices_parser.add_argument("--departure-date", required=True)
cmd_compare_prices_parser.add_argument("--return-date")
cmd_compare_prices_parser.add_argument("--cabin-class", default="economy")
cmd_compare_prices_parser.add_argument("--passengers", type=int, default=1)

cmd_platform_fee_parser = TravelPolicyArgumentParser(add_help=False)
_add_common_args(cmd_platform_fee_parser)
cmd_platform_fee_parser.add_argument("--platform-id", required=True)

cmd_filter_region_parser = TravelPolicyArgumentParser(add_help=False)
_add_common_args(cmd_filter_region_parser)
cmd_filter_region_parser.add_argument("--region", required=True)

cmd_platform_discounts_parser = TravelPolicyArgumentParser(add_help=False)
_add_common_args(cmd_platform_discounts_parser)
cmd_platform_discounts_parser.add_argument("--platform-id", required=True)

cmd_calculate_cost_parser = TravelPolicyArgumentParser(add_help=False)
_add_common_args(cmd_calculate_cost_parser)
cmd_calculate_cost_parser.add_argument("--platform-id", required=True)
cmd_calculate_cost_parser.add_argument("--base-price", type=float, required=True)
cmd_calculate_cost_parser.add_argument("--cabin-class", default="economy")
cmd_calculate_cost_parser.add_argument("--baggage-fee", type=float, default=0)
cmd_calculate_cost_parser.add_argument("--seat-selection-fee", type=float, default=0)

cmd_list_policies_parser = TravelPolicyArgumentParser(add_help=False)
_add_common_args(cmd_list_policies_parser)

cmd_get_policy_parser = TravelPolicyArgumentParser(add_help=False)
_add_common_args(cmd_get_policy_parser)
cmd_get_policy_parser.add_argument("--policy-id", required=True)

cmd_validate_booking_parser = TravelPolicyArgumentParser(add_help=False)
_add_common_args(cmd_validate_booking_parser)
cmd_validate_booking_parser.add_argument("--policy-id", required=True)
cmd_validate_booking_parser.add_argument("--estimated-cost", type=float, required=True)
cmd_validate_booking_parser.add_argument("--cabin-class", required=True)
cmd_validate_booking_parser.add_argument("--advance-booking-days", type=int, required=True)

cmd_approval_chain_parser = TravelPolicyArgumentParser(add_help=False)
_add_common_args(cmd_approval_chain_parser)
cmd_approval_chain_parser.add_argument("--policy-id", required=True)
cmd_approval_chain_parser.add_argument("--estimated-cost", type=float, required=True)

cmd_check_compliance_parser = TravelPolicyArgumentParser(add_help=False)
_add_common_args(cmd_check_compliance_parser)
cmd_check_compliance_parser.add_argument("--policy-id", required=True)
cmd_check_compliance_parser.add_argument("--booking-details", required=True)

cmd_policy_restrictions_parser = TravelPolicyArgumentParser(add_help=False)
_add_common_args(cmd_policy_restrictions_parser)
cmd_policy_restrictions_parser.add_argument("--policy-id", required=True)

cmd_policy_limits_parser = TravelPolicyArgumentParser(add_help=False)
_add_common_args(cmd_policy_limits_parser)
cmd_policy_limits_parser.add_argument("--policy-id", required=True)

cmd_domestic_intl_parser = TravelPolicyArgumentParser(add_help=False)
_add_common_args(cmd_domestic_intl_parser)
cmd_domestic_intl_parser.add_argument("--policy-id", required=True)
cmd_domestic_intl_parser.add_argument("--is-international", type=bool, default=False)

cmd_initiate_approval_parser = TravelPolicyArgumentParser(add_help=False)
_add_common_args(cmd_initiate_approval_parser)
cmd_initiate_approval_parser.add_argument("--policy-id", required=True)
cmd_initiate_approval_parser.add_argument("--estimated-cost", type=float, required=True)
cmd_initiate_approval_parser.add_argument("--approver-email", required=True)
cmd_initiate_approval_parser.add_argument("--justification", required=True)
cmd_initiate_approval_parser.add_argument("--booking-details", default="{}")

cmd_approve_parser = TravelPolicyArgumentParser(add_help=False)
_add_common_args(cmd_approve_parser)
cmd_approve_parser.add_argument("--approval-id", required=True)
cmd_approve_parser.add_argument("--approver-email", required=True)
cmd_approve_parser.add_argument("--comments")

cmd_reject_parser = TravelPolicyArgumentParser(add_help=False)
_add_common_args(cmd_reject_parser)
cmd_reject_parser.add_argument("--approval-id", required=True)
cmd_reject_parser.add_argument("--approver-email", required=True)
cmd_reject_parser.add_argument("--rejection-reason", required=True)

cmd_check_approval_parser = TravelPolicyArgumentParser(add_help=False)
_add_common_args(cmd_check_approval_parser)
cmd_check_approval_parser.add_argument("--approval-id", required=True)

cmd_list_pending_parser = TravelPolicyArgumentParser(add_help=False)
_add_common_args(cmd_list_pending_parser)

cmd_escalate_parser = TravelPolicyArgumentParser(add_help=False)
_add_common_args(cmd_escalate_parser)
cmd_escalate_parser.add_argument("--approval-id", required=True)
cmd_escalate_parser.add_argument("--escalation-reason", required=True)
cmd_escalate_parser.add_argument("--new-approver-email", required=True)

cmd_bulk_approve_parser = TravelPolicyArgumentParser(add_help=False)
_add_common_args(cmd_bulk_approve_parser)
cmd_bulk_approve_parser.add_argument("--approval-ids", required=True)
cmd_bulk_approve_parser.add_argument("--approver-email", required=True)
cmd_bulk_approve_parser.add_argument("--comments")

cmd_approval_history_parser = TravelPolicyArgumentParser(add_help=False)
_add_common_args(cmd_approval_history_parser)

cmd_create_booking_parser = TravelPolicyArgumentParser(add_help=False)
_add_common_args(cmd_create_booking_parser)
cmd_create_booking_parser.add_argument("--platform-id", required=True)
cmd_create_booking_parser.add_argument("--platform-name", required=True)
cmd_create_booking_parser.add_argument("--total-cost", type=float, required=True)
cmd_create_booking_parser.add_argument("--approval-id")
cmd_create_booking_parser.add_argument("--booking-ref")
cmd_create_booking_parser.add_argument("--flight-details", default="{}")

cmd_cancel_booking_parser = TravelPolicyArgumentParser(add_help=False)
_add_common_args(cmd_cancel_booking_parser)
cmd_cancel_booking_parser.add_argument("--booking-ref", required=True)
cmd_cancel_booking_parser.add_argument("--cancellation-reason", required=True)

cmd_get_booking_parser = TravelPolicyArgumentParser(add_help=False)
_add_common_args(cmd_get_booking_parser)
cmd_get_booking_parser.add_argument("--booking-ref", required=True)

cmd_list_bookings_parser = TravelPolicyArgumentParser(add_help=False)
_add_common_args(cmd_list_bookings_parser)
cmd_list_bookings_parser.add_argument("--status-filter")

cmd_update_booking_parser = TravelPolicyArgumentParser(add_help=False)
_add_common_args(cmd_update_booking_parser)
cmd_update_booking_parser.add_argument("--booking-ref", required=True)
cmd_update_booking_parser.add_argument("--update-fields", default="{}")

cmd_booking_itinerary_parser = TravelPolicyArgumentParser(add_help=False)
_add_common_args(cmd_booking_itinerary_parser)
cmd_booking_itinerary_parser.add_argument("--booking-ref", required=True)

cmd_confirm_booking_parser = TravelPolicyArgumentParser(add_help=False)
_add_common_args(cmd_confirm_booking_parser)
cmd_confirm_booking_parser.add_argument("--booking-ref", required=True)

cmd_booking_stats_parser = TravelPolicyArgumentParser(add_help=False)
_add_common_args(cmd_booking_stats_parser)

cmd_session_summary_parser = TravelPolicyArgumentParser(add_help=False)
_add_common_args(cmd_session_summary_parser)


def cmd_list_platforms(args):
    env = _get_env()
    env.set_event_time(args.event_at)
    platforms = env.list_platforms()
    for p in platforms:
        print(f"{p['platform_id']}: {p['name']} ({p.get('region', 'N/A')})")


def cmd_get_platform(args):
    env = _get_env()
    env.set_event_time(args.event_at)
    result = env.get_platform(args.platform_id)
    import json
    print(json.dumps(result, indent=2))


def cmd_search_flights(args):
    env = _get_env()
    env.set_event_time(args.event_at)
    result = env.search_flights(
        args.platform_id, args.origin, args.destination, args.departure_date,
        args.return_date, args.cabin_class, args.passengers
    )
    import json
    print(json.dumps(result, indent=2))


def cmd_compare_prices(args):
    env = _get_env()
    env.set_event_time(args.event_at)
    result = env.compare_platform_prices(
        args.origin, args.destination, args.departure_date,
        args.return_date, args.cabin_class, args.passengers
    )
    import json
    print(json.dumps(result, indent=2))


def cmd_platform_fee(args):
    env = _get_env()
    env.set_event_time(args.event_at)
    result = env.get_platform_fee_structure(args.platform_id)
    import json
    print(json.dumps(result, indent=2))


def cmd_filter_region(args):
    env = _get_env()
    env.set_event_time(args.event_at)
    platforms = env.filter_platforms_by_region(args.region)
    for p in platforms:
        print(f"{p['platform_id']}: {p['name']}")


def cmd_platform_discounts(args):
    env = _get_env()
    env.set_event_time(args.event_at)
    result = env.get_platform_discounts(args.platform_id)
    import json
    print(json.dumps(result, indent=2))


def cmd_calculate_cost(args):
    env = _get_env()
    env.set_event_time(args.event_at)
    result = env.calculate_total_cost(
        args.platform_id, args.base_price, args.cabin_class,
        args.baggage_fee, args.seat_selection_fee
    )
    import json
    print(json.dumps(result, indent=2))


def cmd_list_policies(args):
    env = _get_env()
    env.set_event_time(args.event_at)
    policies = env.list_policies()
    for p in policies:
        print(f"{p['policy_id']}: {p.get('name', 'N/A')}")


def cmd_get_policy(args):
    env = _get_env()
    env.set_event_time(args.event_at)
    result = env.get_policy(args.policy_id)
    import json
    print(json.dumps(result, indent=2))


def cmd_validate_booking(args):
    env = _get_env()
    env.set_event_time(args.event_at)
    import json
    booking_details = json.loads(args.booking_details) if args.booking_details != "{}" else {}
    result = env.validate_booking_against_policy(
        args.policy_id, args.estimated_cost, args.cabin_class, args.advance_booking_days
    )
    print(json.dumps(result, indent=2))


def cmd_approval_chain(args):
    env = _get_env()
    env.set_event_time(args.event_at)
    result = env.get_policy_approval_chain(args.policy_id, args.estimated_cost)
    import json
    print(json.dumps(result, indent=2))


def cmd_check_compliance(args):
    env = _get_env()
    env.set_event_time(args.event_at)
    import json
    booking_details = json.loads(args.booking_details)
    result = env.check_policy_compliance(args.policy_id, booking_details)
    print(json.dumps(result, indent=2))


def cmd_policy_restrictions(args):
    env = _get_env()
    env.set_event_time(args.event_at)
    result = env.get_policy_restrictions(args.policy_id)
    import json
    print(json.dumps(result, indent=2))


def cmd_policy_limits(args):
    env = _get_env()
    env.set_event_time(args.event_at)
    result = env.get_policy_travel_limits(args.policy_id)
    import json
    print(json.dumps(result, indent=2))


def cmd_domestic_intl(args):
    env = _get_env()
    env.set_event_time(args.event_at)
    result = env.get_domestic_vs_international_policy(args.policy_id, args.is_international)
    import json
    print(json.dumps(result, indent=2))


def cmd_initiate_approval(args):
    env = _get_env()
    env.set_event_time(args.event_at)
    import json
    booking_details = json.loads(args.booking_details) if args.booking_details != "{}" else {}
    result = env.initiate_approval_request(
        args.policy_id, booking_details, args.estimated_cost,
        args.approver_email, args.justification
    )
    print(json.dumps(result, indent=2))


def cmd_approve(args):
    env = _get_env()
    env.set_event_time(args.event_at)
    result = env.approve_request(args.approval_id, args.approver_email, args.comments)
    import json
    print(json.dumps(result, indent=2))


def cmd_reject(args):
    env = _get_env()
    env.set_event_time(args.event_at)
    result = env.reject_request(args.approval_id, args.approver_email, args.rejection_reason)
    import json
    print(json.dumps(result, indent=2))


def cmd_check_approval(args):
    env = _get_env()
    env.set_event_time(args.event_at)
    result = env.check_approval_status(args.approval_id)
    import json
    print(json.dumps(result, indent=2))


def cmd_list_pending(args):
    env = _get_env()
    env.set_event_time(args.event_at)
    result = env.list_pending_approvals()
    import json
    print(json.dumps(result, indent=2))


def cmd_escalate(args):
    env = _get_env()
    env.set_event_time(args.event_at)
    result = env.escalate_approval(args.approval_id, args.escalation_reason, args.new_approver_email)
    import json
    print(json.dumps(result, indent=2))


def cmd_bulk_approve(args):
    env = _get_env()
    env.set_event_time(args.event_at)
    approval_ids = _comma_split(args.approval_ids)
    result = env.bulk_approve_requests(approval_ids, args.approver_email, args.comments)
    import json
    print(json.dumps(result, indent=2))


def cmd_approval_history(args):
    env = _get_env()
    env.set_event_time(args.event_at)
    result = env.get_approval_history()
    import json
    print(json.dumps(result, indent=2))


def cmd_create_booking(args):
    env = _get_env()
    env.set_event_time(args.event_at)
    import json
    flight_details = json.loads(args.flight_details) if args.flight_details != "{}" else {}
    result = env.create_booking(
        args.platform_id, args.platform_name, flight_details,
        args.total_cost, args.approval_id, args.booking_ref
    )
    print(json.dumps(result, indent=2))


def cmd_cancel_booking(args):
    env = _get_env()
    env.set_event_time(args.event_at)
    result = env.cancel_booking(args.booking_ref, args.cancellation_reason)
    import json
    print(json.dumps(result, indent=2))


def cmd_get_booking(args):
    env = _get_env()
    env.set_event_time(args.event_at)
    result = env.get_booking_details(args.booking_ref)
    import json
    print(json.dumps(result, indent=2))


def cmd_list_bookings(args):
    env = _get_env()
    env.set_event_time(args.event_at)
    result = env.list_bookings(args.status_filter)
    import json
    print(json.dumps(result, indent=2))


def cmd_update_booking(args):
    env = _get_env()
    env.set_event_time(args.event_at)
    import json
    update_fields = json.loads(args.update_fields)
    result = env.update_booking(args.booking_ref, update_fields)
    print(json.dumps(result, indent=2))


def cmd_booking_itinerary(args):
    env = _get_env()
    env.set_event_time(args.event_at)
    result = env.get_booking_itinerary(args.booking_ref)
    import json
    print(json.dumps(result, indent=2))


def cmd_confirm_booking(args):
    env = _get_env()
    env.set_event_time(args.event_at)
    result = env.confirm_booking_received(args.booking_ref)
    import json
    print(json.dumps(result, indent=2))


def cmd_booking_stats(args):
    env = _get_env()
    env.set_event_time(args.event_at)
    result = env.get_booking_statistics()
    import json
    print(json.dumps(result, indent=2))


def cmd_session_summary(args):
    env = _get_env()
    env.set_event_time(args.event_at)
    result = env.session_summary()
    import json
    print(json.dumps(result, indent=2))


def main():
    parser = TravelPolicyArgumentParser(description="Travel Policy Environment CLI")
    subparsers = parser.add_subparsers(dest="command")

    p_list_scenarios = subparsers.add_parser("list-scenarios", help="List available scenarios")

    p_prepare = subparsers.add_parser("prepare-rollout", help=argparse.SUPPRESS)
    p_prepare.add_argument("--session-id", type=str, default=None)
    p_prepare.add_argument("--scenario-id", type=str, default=None)
    p_prepare.add_argument("--show-task", action="store_true")

    p_reset = subparsers.add_parser("reset-rollout", help=argparse.SUPPRESS)

    p_list_platforms = subparsers.add_parser("list-platforms", help="List all platforms", parents=[cmd_list_platforms_parser])
    p_get_platform = subparsers.add_parser("get-platform", help="Get platform details", parents=[cmd_get_platform_parser])
    p_search = subparsers.add_parser("search-flights", help="Search flights on platform", parents=[cmd_search_flights_parser])
    p_compare = subparsers.add_parser("compare-platform-prices", help="Compare prices across platforms", parents=[cmd_compare_prices_parser])
    p_fee = subparsers.add_parser("platform-fee-structure", help="Get platform fee structure", parents=[cmd_platform_fee_parser])
    p_filter = subparsers.add_parser("filter-platforms-by-region", help="Filter platforms by region", parents=[cmd_filter_region_parser])
    p_discounts = subparsers.add_parser("platform-discounts", help="Get platform discounts", parents=[cmd_platform_discounts_parser])
    p_calc = subparsers.add_parser("calculate-total-cost", help="Calculate total cost", parents=[cmd_calculate_cost_parser])

    p_list_policies = subparsers.add_parser("list-policies", help="List all policies", parents=[cmd_list_policies_parser])
    p_get_policy = subparsers.add_parser("get-policy", help="Get policy details", parents=[cmd_get_policy_parser])
    p_validate = subparsers.add_parser("validate-booking-against-policy", help="Validate booking", parents=[cmd_validate_booking_parser])
    p_chain = subparsers.add_parser("get-policy-approval-chain", help="Get approval chain", parents=[cmd_approval_chain_parser])
    p_compliance = subparsers.add_parser("check-policy-compliance", help="Check compliance", parents=[cmd_check_compliance_parser])
    p_restrict = subparsers.add_parser("get-policy-restrictions", help="Get policy restrictions", parents=[cmd_policy_restrictions_parser])
    p_limits = subparsers.add_parser("get-policy-travel-limits", help="Get travel limits", parents=[cmd_policy_limits_parser])
    p_dom_intl = subparsers.add_parser("get-domestic-international-policy", help="Get domestic/intl policy", parents=[cmd_domestic_intl_parser])

    p_init_approval = subparsers.add_parser("initiate-approval-request", help="Initiate approval", parents=[cmd_initiate_approval_parser])
    p_approve = subparsers.add_parser("approve-request", help="Approve request", parents=[cmd_approve_parser])
    p_reject = subparsers.add_parser("reject-request", help="Reject request", parents=[cmd_reject_parser])
    p_check = subparsers.add_parser("check-approval-status", help="Check approval status", parents=[cmd_check_approval_parser])
    p_pending = subparsers.add_parser("list-pending-approvals", help="List pending approvals", parents=[cmd_list_pending_parser])
    p_escalate = subparsers.add_parser("escalate-approval", help="Escalate approval", parents=[cmd_escalate_parser])
    p_bulk = subparsers.add_parser("bulk-approve-requests", help="Bulk approve", parents=[cmd_bulk_approve_parser])
    p_history = subparsers.add_parser("get-approval-history", help="Get approval history", parents=[cmd_approval_history_parser])

    p_create = subparsers.add_parser("create-booking", help="Create booking", parents=[cmd_create_booking_parser])
    p_cancel = subparsers.add_parser("cancel-booking", help="Cancel booking", parents=[cmd_cancel_booking_parser])
    p_get = subparsers.add_parser("get-booking-details", help="Get booking details", parents=[cmd_get_booking_parser])
    p_list = subparsers.add_parser("list-bookings", help="List bookings", parents=[cmd_list_bookings_parser])
    p_update = subparsers.add_parser("update-booking", help="Update booking", parents=[cmd_update_booking_parser])
    p_itin = subparsers.add_parser("get-booking-itinerary", help="Get itinerary", parents=[cmd_booking_itinerary_parser])
    p_confirm = subparsers.add_parser("confirm-booking-received", help="Confirm booking", parents=[cmd_confirm_booking_parser])
    p_stats = subparsers.add_parser("get-booking-statistics", help="Get booking stats", parents=[cmd_booking_stats_parser])

    p_summary = subparsers.add_parser("session-summary", help="Get session summary", parents=[cmd_session_summary_parser])

    args = parser.parse_args()

    commands = {
        "list-scenarios": cmd_list_scenarios,
        "prepare-rollout": cmd_prepare_rollout,
        "reset-rollout": cmd_reset_rollout,
        "list-platforms": cmd_list_platforms,
        "get-platform": cmd_get_platform,
        "search-flights": cmd_search_flights,
        "compare-platform-prices": cmd_compare_prices,
        "platform-fee-structure": cmd_platform_fee,
        "filter-platforms-by-region": cmd_filter_region,
        "platform-discounts": cmd_platform_discounts,
        "calculate-total-cost": cmd_calculate_cost,
        "list-policies": cmd_list_policies,
        "get-policy": cmd_get_policy,
        "validate-booking-against-policy": cmd_validate_booking,
        "get-policy-approval-chain": cmd_approval_chain,
        "check-policy-compliance": cmd_check_compliance,
        "get-policy-restrictions": cmd_policy_restrictions,
        "get-policy-travel-limits": cmd_policy_limits,
        "get-domestic-international-policy": cmd_domestic_intl,
        "initiate-approval-request": cmd_initiate_approval,
        "approve-request": cmd_approve,
        "reject-request": cmd_reject,
        "check-approval-status": cmd_check_approval,
        "list-pending-approvals": cmd_list_pending,
        "escalate-approval": cmd_escalate,
        "bulk-approve-requests": cmd_bulk_approve,
        "get-approval-history": cmd_approval_history,
        "create-booking": cmd_create_booking,
        "cancel-booking": cmd_cancel_booking,
        "get-booking-details": cmd_get_booking,
        "list-bookings": cmd_list_bookings,
        "update-booking": cmd_update_booking,
        "get-booking-itinerary": cmd_booking_itinerary,
        "confirm-booking-received": cmd_confirm_booking,
        "get-booking-statistics": cmd_booking_stats,
        "session-summary": cmd_session_summary,
    }

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
