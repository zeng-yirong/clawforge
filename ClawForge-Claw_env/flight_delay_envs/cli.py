from __future__ import annotations

import argparse
import json
import os
import random
import sys
from datetime import datetime, timezone
from typing import Any

from .environment import FlightDelayEnvironment

FLIGHT_DELAY_SESSION_ID_ENV = "FLIGHT_DELAY_SESSION_ID"
FLIGHT_DELAY_STATE_ROOT_ENV = "FLIGHT_DELAY_STATE_ROOT"
FLIGHT_DELAY_SCENARIO_ID_ENV = "FLIGHT_DELAY_SCENARIO_ID"
DEFAULT_SCENARIO_ID = "flight_delay_cascade"
_HIDDEN_HELP_MARKERS = ("(create-session)", "(reset-session)", "==SUPPRESS==")


def _print_json(payload: dict[str, Any], *, exit_code: int = 0) -> int:
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return exit_code


class FlightDelayArgumentParser(argparse.ArgumentParser):
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
    return f"fld-{_utc_stamp()}-{random.randint(1000, 9999)}"


def _resolve_bound_session_id(args: argparse.Namespace) -> str:
    explicit = getattr(args, "session_id", None)
    if explicit:
        return explicit

    env_value = os.getenv(FLIGHT_DELAY_SESSION_ID_ENV, "").strip()
    if env_value:
        return env_value

    raise ValueError(
        f"No active rollout session is bound. The trainer must set {FLIGHT_DELAY_SESSION_ID_ENV} "
        "before agent commands run."
    )


def _resolve_scenario_id(args: argparse.Namespace) -> str:
    scenario_id = getattr(args, "scenario_id", None)
    if scenario_id:
        return scenario_id

    env_value = os.getenv(FLIGHT_DELAY_SCENARIO_ID_ENV, "").strip()
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

    parser = FlightDelayArgumentParser(description="Flight delay cascade management environment CLI.")
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

    list_flights = subparsers.add_parser("list-flights", help="List available flights.", parents=[shared, agent_session])
    list_flights.add_argument("--query", type=str, default="")
    list_flights.add_argument("--status", type=str, default=None)
    list_flights.add_argument("--airline", type=str, default=None)
    list_flights.add_argument("--limit", type=int, default=None)

    get_flight = subparsers.add_parser("get-flight", help="Get detailed flight information.", parents=[shared, agent_session])
    get_flight.add_argument("--flight-id", required=True, type=str)

    check_flight_status = subparsers.add_parser("check-flight-status", help="Check flight status and delay information.", parents=[shared, agent_session])
    check_flight_status.add_argument("--flight-id", required=True, type=str)

    detect_delayed = subparsers.add_parser("detect-delayed-flights", help="Detect all delayed flights in the session.", parents=[shared, agent_session])

    get_affected_connections = subparsers.add_parser("get-affected-connections", help="Get hotel and transport bookings affected by a flight delay.", parents=[shared, agent_session])
    get_affected_connections.add_argument("--flight-id", required=True, type=str)

    list_hotel_bookings = subparsers.add_parser("list-hotel-bookings", help="List hotel bookings.", parents=[shared, agent_session])
    list_hotel_bookings.add_argument("--query", type=str, default="")
    list_hotel_bookings.add_argument("--status", type=str, default=None)
    list_hotel_bookings.add_argument("--guest-name", type=str, default=None)
    list_hotel_bookings.add_argument("--limit", type=int, default=None)

    get_hotel_booking = subparsers.add_parser("get-hotel-booking", help="Get detailed hotel booking information.", parents=[shared, agent_session])
    get_hotel_booking.add_argument("--booking-id", required=True, type=str)

    create_hotel_booking = subparsers.add_parser("create-hotel-booking", help="Create a new hotel booking.", parents=[shared, agent_session])
    create_hotel_booking.add_argument("--hotel-id", required=True, type=str)
    create_hotel_booking.add_argument("--hotel-name", required=True, type=str)
    create_hotel_booking.add_argument("--check-in", required=True, type=str)
    create_hotel_booking.add_argument("--check-out", required=True, type=str)
    create_hotel_booking.add_argument("--guest-name", required=True, type=str)
    create_hotel_booking.add_argument("--guest-count", type=int, default=1)
    create_hotel_booking.add_argument("--room-type", type=str, default="standard")
    create_hotel_booking.add_argument("--special-requests", type=str, default=None)
    create_hotel_booking.add_argument("--linked-flight-id", type=str, default=None)

    adjust_hotel = subparsers.add_parser("adjust-hotel-booking", help="Adjust hotel booking check-in/check-out times.", parents=[shared, agent_session])
    adjust_hotel.add_argument("--booking-id", required=True, type=str)
    adjust_hotel.add_argument("--new-check-in", type=str, default=None)
    adjust_hotel.add_argument("--new-check-out", type=str, default=None)

    cancel_hotel = subparsers.add_parser("cancel-hotel-booking", help="Cancel a hotel booking.", parents=[shared, agent_session])
    cancel_hotel.add_argument("--booking-id", required=True, type=str)
    cancel_hotel.add_argument("--cancellation-reason", required=True, type=str)

    list_transport_bookings = subparsers.add_parser("list-transport-bookings", help="List transport bookings.", parents=[shared, agent_session])
    list_transport_bookings.add_argument("--query", type=str, default="")
    list_transport_bookings.add_argument("--status", type=str, default=None)
    list_transport_bookings.add_argument("--transport-type", type=str, default=None)
    list_transport_bookings.add_argument("--limit", type=int, default=None)

    get_transport_booking = subparsers.add_parser("get-transport-booking", help="Get detailed transport booking information.", parents=[shared, agent_session])
    get_transport_booking.add_argument("--booking-id", required=True, type=str)

    create_transport = subparsers.add_parser("create-transport-booking", help="Create a new transport booking.", parents=[shared, agent_session])
    create_transport.add_argument("--transport-type", required=True, type=str)
    create_transport.add_argument("--service-provider", required=True, type=str)
    create_transport.add_argument("--passenger-name", required=True, type=str)
    create_transport.add_argument("--passenger-phone", required=True, type=str)
    create_transport.add_argument("--pickup-location", required=True, type=str)
    create_transport.add_argument("--dropoff-location", required=True, type=str)
    create_transport.add_argument("--pickup-time", required=True, type=str)
    create_transport.add_argument("--vehicle-type", type=str, default="standard")
    create_transport.add_argument("--passengers-count", type=int, default=1)
    create_transport.add_argument("--special-requests", type=str, default=None)
    create_transport.add_argument("--linked-flight-id", type=str, default=None)

    reschedule_transport = subparsers.add_parser("reschedule-transport-booking", help="Reschedule a transport booking.", parents=[shared, agent_session])
    reschedule_transport.add_argument("--booking-id", required=True, type=str)
    reschedule_transport.add_argument("--new-pickup-time", required=True, type=str)

    cancel_transport = subparsers.add_parser("cancel-transport-booking", help="Cancel a transport booking.", parents=[shared, agent_session])
    cancel_transport.add_argument("--booking-id", required=True, type=str)
    cancel_transport.add_argument("--cancellation-reason", required=True, type=str)

    list_notifications = subparsers.add_parser("list-notifications", help="List notifications.", parents=[shared, agent_session])
    list_notifications.add_argument("--query", type=str, default="")
    list_notifications.add_argument("--notification-type", type=str, default=None)
    list_notifications.add_argument("--status", type=str, default=None)
    list_notifications.add_argument("--recipient-email", type=str, default=None)
    list_notifications.add_argument("--limit", type=int, default=None)

    get_notification = subparsers.add_parser("get-notification", help="Get detailed notification information.", parents=[shared, agent_session])
    get_notification.add_argument("--notification-id", required=True, type=str)

    compose_delay_notification = subparsers.add_parser("compose-delay-notification", help="Compose a flight delay notification for a recipient.", parents=[shared, agent_session])
    compose_delay_notification.add_argument("--flight-id", required=True, type=str)
    compose_delay_notification.add_argument("--recipient-name", required=True, type=str)
    compose_delay_notification.add_argument("--recipient-email", required=True, type=str)

    send_notification = subparsers.add_parser("send-notification", help="Send a notification.", parents=[shared, agent_session])
    send_notification.add_argument("--notification-id", required=True, type=str)

    list_conferences = subparsers.add_parser("list-conferences", help="List conferences.", parents=[shared, agent_session])
    list_conferences.add_argument("--query", type=str, default="")
    list_conferences.add_argument("--status", type=str, default=None)
    list_conferences.add_argument("--location", type=str, default=None)
    list_conferences.add_argument("--limit", type=int, default=None)

    get_conference = subparsers.add_parser("get-conference", help="Get detailed conference information.", parents=[shared, agent_session])
    get_conference.add_argument("--conference-id", required=True, type=str)

    list_attendees = subparsers.add_parser("list-attendees", help="List conference attendees.", parents=[shared, agent_session])
    list_attendees.add_argument("--conference-id", required=True, type=str)
    list_attendees.add_argument("--attending", type=bool, default=None)
    list_attendees.add_argument("--query", type=str, default="")

    get_notification_stats = subparsers.add_parser("notification-stats", help="Get notification statistics.", parents=[shared, agent_session])

    subparsers.add_parser("session-summary", help="Show session progress and summary.", parents=[shared, agent_session])

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    env = FlightDelayEnvironment(data_root=args.data_root, state_root=args.state_root)

    try:
        if args.command == "list-scenarios":
            return _print_json({"status": "success", "data": env.list_scenarios()})

        if args.command in {"prepare-rollout", "create-session"}:
            session_id = getattr(args, "session_id", None) or os.getenv(FLIGHT_DELAY_SESSION_ID_ENV, "").strip()
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
                    FLIGHT_DELAY_SESSION_ID_ENV: session_id,
                    FLIGHT_DELAY_STATE_ROOT_ENV: str(env.store.state_root),
                    FLIGHT_DELAY_SCENARIO_ID_ENV: scenario_id,
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

        if args.command == "list-flights":
            data = env.list_flights(
                session_id,
                query=args.query,
                status=args.status,
                airline=args.airline,
                limit=args.limit,
            )
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "get-flight":
            data = env.get_flight(session_id, args.flight_id)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "check-flight-status":
            data = env.check_flight_status(session_id, args.flight_id)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "detect-delayed-flights":
            data = env.detect_delayed_flights(session_id)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "get-affected-connections":
            data = env.get_affected_connections(session_id, args.flight_id)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "list-hotel-bookings":
            data = env.list_hotel_bookings(
                session_id,
                query=args.query,
                status=args.status,
                guest_name=args.guest_name,
                limit=args.limit,
            )
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "get-hotel-booking":
            data = env.get_hotel_booking(session_id, args.booking_id)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "create-hotel-booking":
            data = env.create_hotel_booking(
                session_id,
                hotel_id=args.hotel_id,
                hotel_name=args.hotel_name,
                check_in=args.check_in,
                check_out=args.check_out,
                guest_name=args.guest_name,
                guest_count=args.guest_count,
                room_type=args.room_type,
                special_requests=args.special_requests,
                linked_flight_id=args.linked_flight_id,
            )
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "adjust-hotel-booking":
            data = env.adjust_hotel_booking(
                session_id,
                booking_id=args.booking_id,
                new_check_in=args.new_check_in,
                new_check_out=args.new_check_out,
            )
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "cancel-hotel-booking":
            data = env.cancel_hotel_booking(
                session_id,
                booking_id=args.booking_id,
                cancellation_reason=args.cancellation_reason,
            )
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "list-transport-bookings":
            data = env.list_transport_bookings(
                session_id,
                query=args.query,
                status=args.status,
                transport_type=args.transport_type,
                limit=args.limit,
            )
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "get-transport-booking":
            data = env.get_transport_booking(session_id, args.booking_id)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "create-transport-booking":
            data = env.create_transport_booking(
                session_id,
                transport_type=args.transport_type,
                service_provider=args.service_provider,
                passenger_name=args.passenger_name,
                passenger_phone=args.passenger_phone,
                pickup_location=args.pickup_location,
                dropoff_location=args.dropoff_location,
                pickup_time=args.pickup_time,
                vehicle_type=args.vehicle_type,
                passengers_count=args.passengers_count,
                special_requests=args.special_requests,
                linked_flight_id=args.linked_flight_id,
            )
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "reschedule-transport-booking":
            data = env.reschedule_transport_booking(
                session_id,
                booking_id=args.booking_id,
                new_pickup_time=args.new_pickup_time,
            )
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "cancel-transport-booking":
            data = env.cancel_transport_booking(
                session_id,
                booking_id=args.booking_id,
                cancellation_reason=args.cancellation_reason,
            )
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "list-notifications":
            data = env.list_notifications(
                session_id,
                query=args.query,
                notification_type=args.notification_type,
                status=args.status,
                recipient_email=args.recipient_email,
                limit=args.limit,
            )
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "get-notification":
            data = env.get_notification(session_id, args.notification_id)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "compose-delay-notification":
            data = env.compose_delay_notification(
                session_id,
                flight_id=args.flight_id,
                recipient_name=args.recipient_name,
                recipient_email=args.recipient_email,
            )
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "send-notification":
            data = env.send_notification(session_id, args.notification_id)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "list-conferences":
            data = env.list_conferences(
                session_id,
                query=args.query,
                status=args.status,
                location=args.location,
                limit=args.limit,
            )
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "get-conference":
            data = env.get_conference(session_id, args.conference_id)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "list-attendees":
            data = env.list_attendees(
                session_id,
                args.conference_id,
                attending=args.attending,
                query=args.query,
            )
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "notification-stats":
            data = env.get_notification_stats(session_id)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "session-summary":
            return _print_json({"status": "success", "data": _agent_payload(env.session_summary(session_id))})

    except Exception as exc:
        return _print_json({"status": "error", "message": _agent_error_message(exc)}, exit_code=1)

    return _print_json({"status": "error", "message": f"Unknown command: {args.command}"}, exit_code=1)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
