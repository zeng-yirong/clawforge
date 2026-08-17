from __future__ import annotations

import os
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .conferences import (
    get_conference,
    list_conferences,
    list_attendees,
    get_attendee,
    update_attendee_rsvp,
    check_attendee_schedule_conflicts,
    get_conference_schedule,
    get_conference_travel_info,
    update_conference_session,
    notify_attendees_of_schedule_change,
)
from .evaluator import evaluate_session
from .flights import (
    list_flights,
    get_flight,
    check_flight_status,
    detect_delayed_flights,
    update_flight_status,
    get_affected_connections,
    search_available_hotels,
)
from .hotels import (
    list_hotel_bookings,
    get_hotel_booking,
    create_hotel_booking,
    adjust_hotel_booking,
    cancel_hotel_booking,
    get_hotel_booking_for_flight,
    search_alternative_hotels,
)
from .notifications import (
    list_notifications,
    get_notification,
    create_email_notification,
    send_notification,
    cancel_notification,
    compose_delay_notification,
    create_bulk_notification,
    get_notification_stats,
)
from .repository import DatasetRepository
from .store import SessionStore
from .transports import (
    list_transport_bookings,
    get_transport_booking,
    create_transport_booking,
    reschedule_transport_booking,
    cancel_transport_booking,
    get_transport_booking_for_flight,
    find_alternative_transports,
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _coerce_iso_datetime(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized)


class FlightDelayEnvironment:
    def __init__(
        self,
        *,
        data_root: str | Path | None = None,
        state_root: str | Path | None = None,
    ):
        default_state_root = Path(os.getenv("FLIGHT_DELAY_STATE_ROOT", Path.cwd() / ".flight_delay_state"))
        self.repository = DatasetRepository(data_root)
        self.store = SessionStore(state_root or default_state_root)
        self.accounts = self.repository.load_accounts()
        self.contacts = self.repository.load_contacts()

    def list_scenarios(self) -> dict[str, Any]:
        return {
            "scenarios": [
                {
                    "scenario_id": item["scenario_id"],
                    "title": item["title"],
                    "task_prompt": item["task_prompt"],
                }
                for item in self.repository.list_scenarios()
            ]
        }

    def create_session(self, session_id: str, scenario_id: str, overwrite: bool = False) -> dict[str, Any]:
        scenario = self.repository.load_scenario(scenario_id)
        session_payload = self._build_session_payload(session_id=session_id, scenario=scenario)
        self.store.create_session(session_id, session_payload, overwrite=overwrite)
        return self.session_summary(session_id)

    def reset_session(self, session_id: str) -> dict[str, Any]:
        existing = self.store.load_session(session_id)
        return self.create_session(session_id, existing["scenario_id"], overwrite=True)

    def get_task(self, session_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        scenario = self.repository.load_scenario(session["scenario_id"])
        return {
            "session_id": session_id,
            "scenario_id": session["scenario_id"],
            "title": scenario["title"],
            "task_prompt": scenario["task_prompt"],
            "workspace_account": session["workspace_account"],
            "delayed_flights_count": len([f for f in session.get("flights", []) if f.get("delay_minutes", 0) > 0]),
            "pending_notifications_count": len([n for n in session.get("notifications", []) if n.get("status") == "draft"]),
        }

    def list_flights(
        self,
        session_id: str,
        *,
        query: str = "",
        status: str | None = None,
        airline: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {
            "session_id": session_id,
            "data": list_flights(
                session,
                query=query,
                status=status,
                airline=airline,
                limit=limit,
            ),
        }

    def get_flight(self, session_id: str, flight_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {"session_id": session_id, "data": get_flight(session, flight_id)}

    def check_flight_status(self, session_id: str, flight_id: str) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = check_flight_status(session, flight_id)
            self._record_action(session, action_index, event_at, "check_flight_status", {"flight_id": flight_id, "is_delayed": payload["is_delayed"]})
            self.store.save_session(session_id, session)
            return {"session_id": session_id, "data": payload}

    def detect_delayed_flights(self, session_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {"session_id": session_id, "data": detect_delayed_flights(session)}

    def update_flight_status(
        self,
        session_id: str,
        flight_id: str,
        new_status: str,
        delay_minutes: int | None = None,
    ) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = update_flight_status(
                session, flight_id, new_status, event_at, action_index, delay_minutes=delay_minutes
            )
            self._record_action(session, action_index, event_at, "update_flight_status", {"flight_id": flight_id, "new_status": new_status})
            self.store.save_session(session_id, session)
            return {"session_id": session_id, "data": payload}

    def get_affected_connections(self, session_id: str, flight_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {"session_id": session_id, "data": get_affected_connections(session, flight_id)}

    def list_hotel_bookings(
        self,
        session_id: str,
        *,
        query: str = "",
        status: str | None = None,
        guest_name: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {
            "session_id": session_id,
            "data": list_hotel_bookings(
                session,
                query=query,
                status=status,
                guest_name=guest_name,
                limit=limit,
            ),
        }

    def get_hotel_booking(self, session_id: str, booking_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {"session_id": session_id, "data": get_hotel_booking(session, booking_id)}

    def create_hotel_booking(
        self,
        session_id: str,
        hotel_id: str,
        hotel_name: str,
        check_in: str,
        check_out: str,
        guest_name: str,
        guest_count: int,
        room_type: str,
        special_requests: str | None = None,
        linked_flight_id: str | None = None,
    ) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = create_hotel_booking(
                session,
                hotel_id=hotel_id,
                hotel_name=hotel_name,
                check_in=check_in,
                check_out=check_out,
                guest_name=guest_name,
                guest_count=guest_count,
                room_type=room_type,
                special_requests=special_requests,
                linked_flight_id=linked_flight_id,
                event_at=event_at,
                action_index=action_index,
            )
            self._record_action(session, action_index, event_at, "create_hotel_booking", {"booking_id": payload["booking_id"], "hotel_name": hotel_name})
            self.store.save_session(session_id, session)
            return {"session_id": session_id, "data": payload}

    def adjust_hotel_booking(
        self,
        session_id: str,
        booking_id: str,
        new_check_in: str | None = None,
        new_check_out: str | None = None,
    ) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = adjust_hotel_booking(
                session,
                booking_id=booking_id,
                new_check_in=new_check_in,
                new_check_out=new_check_out,
                event_at=event_at,
                action_index=action_index,
            )
            self._record_action(session, action_index, event_at, "adjust_hotel_booking", {"booking_id": booking_id})
            self.store.save_session(session_id, session)
            return {"session_id": session_id, "data": payload}

    def cancel_hotel_booking(
        self,
        session_id: str,
        booking_id: str,
        cancellation_reason: str,
    ) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = cancel_hotel_booking(
                session,
                booking_id=booking_id,
                cancellation_reason=cancellation_reason,
                event_at=event_at,
                action_index=action_index,
            )
            self._record_action(session, action_index, event_at, "cancel_hotel_booking", {"booking_id": booking_id})
            self.store.save_session(session_id, session)
            return {"session_id": session_id, "data": payload}

    def list_transport_bookings(
        self,
        session_id: str,
        *,
        query: str = "",
        status: str | None = None,
        transport_type: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {
            "session_id": session_id,
            "data": list_transport_bookings(
                session,
                query=query,
                status=status,
                transport_type=transport_type,
                limit=limit,
            ),
        }

    def get_transport_booking(self, session_id: str, booking_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {"session_id": session_id, "data": get_transport_booking(session, booking_id)}

    def create_transport_booking(
        self,
        session_id: str,
        transport_type: str,
        service_provider: str,
        passenger_name: str,
        passenger_phone: str,
        pickup_location: str,
        dropoff_location: str,
        pickup_time: str,
        vehicle_type: str,
        passengers_count: int,
        special_requests: str | None = None,
        linked_flight_id: str | None = None,
    ) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = create_transport_booking(
                session,
                transport_type=transport_type,
                service_provider=service_provider,
                passenger_name=passenger_name,
                passenger_phone=passenger_phone,
                pickup_location=pickup_location,
                dropoff_location=dropoff_location,
                pickup_time=pickup_time,
                vehicle_type=vehicle_type,
                passengers_count=passengers_count,
                special_requests=special_requests,
                linked_flight_id=linked_flight_id,
                event_at=event_at,
                action_index=action_index,
            )
            self._record_action(session, action_index, event_at, "create_transport_booking", {"booking_id": payload["booking_id"], "transport_type": transport_type})
            self.store.save_session(session_id, session)
            return {"session_id": session_id, "data": payload}

    def reschedule_transport_booking(
        self,
        session_id: str,
        booking_id: str,
        new_pickup_time: str,
    ) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = reschedule_transport_booking(
                session,
                booking_id=booking_id,
                new_pickup_time=new_pickup_time,
                event_at=event_at,
                action_index=action_index,
            )
            self._record_action(session, action_index, event_at, "reschedule_transport_booking", {"booking_id": booking_id})
            self.store.save_session(session_id, session)
            return {"session_id": session_id, "data": payload}

    def cancel_transport_booking(
        self,
        session_id: str,
        booking_id: str,
        cancellation_reason: str,
    ) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = cancel_transport_booking(
                session,
                booking_id=booking_id,
                cancellation_reason=cancellation_reason,
                event_at=event_at,
                action_index=action_index,
            )
            self._record_action(session, action_index, event_at, "cancel_transport_booking", {"booking_id": booking_id})
            self.store.save_session(session_id, session)
            return {"session_id": session_id, "data": payload}

    def list_notifications(
        self,
        session_id: str,
        *,
        query: str = "",
        notification_type: str | None = None,
        status: str | None = None,
        recipient_email: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {
            "session_id": session_id,
            "data": list_notifications(
                session,
                query=query,
                notification_type=notification_type,
                status=status,
                recipient_email=recipient_email,
                limit=limit,
            ),
        }

    def get_notification(self, session_id: str, notification_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {"session_id": session_id, "data": get_notification(session, notification_id)}

    def compose_delay_notification(
        self,
        session_id: str,
        flight_id: str,
        recipient_name: str,
        recipient_email: str,
    ) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = compose_delay_notification(
                session,
                flight_id=flight_id,
                recipient_name=recipient_name,
                recipient_email=recipient_email,
                event_at=event_at,
                action_index=action_index,
            )
            self._record_action(session, action_index, event_at, "compose_delay_notification", {"flight_id": flight_id, "recipient_email": recipient_email})
            self.store.save_session(session_id, session)
            return {"session_id": session_id, "data": payload}

    def create_email_notification(
        self,
        session_id: str,
        recipient_name: str,
        recipient_email: str,
        subject: str,
        body: str,
        priority: str,
        linked_flight_id: str | None = None,
        linked_hotel_booking_ids: list[str] | None = None,
        linked_transport_booking_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = create_email_notification(
                session,
                recipient_name=recipient_name,
                recipient_email=recipient_email,
                subject=subject,
                body=body,
                priority=priority,
                linked_flight_id=linked_flight_id,
                linked_hotel_booking_ids=linked_hotel_booking_ids or [],
                linked_transport_booking_ids=linked_transport_booking_ids or [],
                event_at=event_at,
                action_index=action_index,
            )
            self._record_action(session, action_index, event_at, "create_email_notification", {"notification_id": payload["notification_id"]})
            self.store.save_session(session_id, session)
            return {"session_id": session_id, "data": payload}

    def send_notification(self, session_id: str, notification_id: str) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = send_notification(
                session,
                notification_id=notification_id,
                event_at=event_at,
                action_index=action_index,
            )
            self._record_action(session, action_index, event_at, "send_notification", {"notification_id": notification_id})
            self.store.save_session(session_id, session)
            return {"session_id": session_id, "data": payload}

    def cancel_notification(
        self,
        session_id: str,
        notification_id: str,
        cancellation_reason: str,
    ) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = cancel_notification(
                session,
                notification_id=notification_id,
                cancellation_reason=cancellation_reason,
                event_at=event_at,
                action_index=action_index,
            )
            self._record_action(session, action_index, event_at, "cancel_notification", {"notification_id": notification_id})
            self.store.save_session(session_id, session)
            return {"session_id": session_id, "data": payload}

    def list_conferences(
        self,
        session_id: str,
        *,
        query: str = "",
        status: str | None = None,
        location: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {
            "session_id": session_id,
            "data": list_conferences(
                session,
                query=query,
                status=status,
                location=location,
                limit=limit,
            ),
        }

    def get_conference(self, session_id: str, conference_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {"session_id": session_id, "data": get_conference(session, conference_id)}

    def list_attendees(
        self,
        session_id: str,
        conference_id: str,
        *,
        attending: bool | None = None,
        query: str = "",
    ) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {
            "session_id": session_id,
            "data": list_attendees(
                session,
                conference_id,
                attending=attending,
                query=query,
            ),
        }

    def get_attendee(self, session_id: str, conference_id: str, attendee_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {"session_id": session_id, "data": get_attendee(session, conference_id, attendee_id)}

    def update_attendee_rsvp(
        self,
        session_id: str,
        conference_id: str,
        attendee_id: str,
        rsvp_status: str,
    ) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = update_attendee_rsvp(
                session,
                conference_id=conference_id,
                attendee_id=attendee_id,
                rsvp_status=rsvp_status,
                event_at=event_at,
                action_index=action_index,
            )
            self._record_action(session, action_index, event_at, "update_attendee_rsvp", {"attendee_id": attendee_id, "rsvp_status": rsvp_status})
            self.store.save_session(session_id, session)
            return {"session_id": session_id, "data": payload}

    def get_notification_stats(self, session_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {"session_id": session_id, "data": get_notification_stats(session)}

    def session_summary(self, session_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        scenario = self.repository.load_scenario(session["scenario_id"])
        return {
            "session_id": session_id,
            "scenario_id": session["scenario_id"],
            "title": scenario["title"],
            "workspace_account": session["workspace_account"],
            "state_root": str(self.store.state_root),
            "flights_count": len(session.get("flights", [])),
            "delayed_flights_count": len([f for f in session.get("flights", []) if f.get("delay_minutes", 0) > 0]),
            "hotel_bookings_count": len(session.get("hotel_bookings", [])),
            "transport_bookings_count": len(session.get("transport_bookings", [])),
            "notifications_count": len(session.get("notifications", [])),
            "sent_notifications_count": len([n for n in session.get("notifications", []) if n.get("status") == "sent"]),
            "action_count": len(session.get("actions", [])),
        }

    def evaluate_session(self, session_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        scenario = self.repository.load_scenario(session["scenario_id"])
        return evaluate_session(session, scenario)

    def _build_session_payload(self, *, session_id: str, scenario: dict[str, Any]) -> dict[str, Any]:
        all_flights = self.repository.load_flights()
        all_hotels = self.repository.load_hotels()
        all_transports = self.repository.load_transports()
        all_conferences = self.repository.load_conferences()

        flights = [self._hydrate_flight(all_flights[fid]) for fid in scenario["flight_ids"] if fid in all_flights]
        hotel_bookings = [self._hydrate_hotel_booking(all_hotels[hid]) for hid in scenario.get("hotel_booking_ids", []) if hid in all_hotels]
        transport_bookings = [self._hydrate_transport_booking(all_transports[tid]) for tid in scenario.get("transport_booking_ids", []) if tid in all_transports]
        conferences = [self._hydrate_conference(all_conferences[cid]) for cid in scenario.get("conference_ids", []) if cid in all_conferences]

        return {
            "session_id": session_id,
            "scenario_id": scenario["scenario_id"],
            "created_at": _utc_now_iso(),
            "meta": {
                "base_time": scenario["current_time"],
                "action_index": 0,
            },
            "workspace_account": deepcopy(self.accounts[scenario["workspace_account_id"]]),
            "flights": flights,
            "hotel_bookings": hotel_bookings,
            "transport_bookings": transport_bookings,
            "conferences": conferences,
            "available_hotels": list(all_hotels.values()),
            "available_transports": list(all_transports.values()),
            "notifications": [],
            "actions": [],
            "flight_status_changes": [],
            "hotel_adjustments": [],
            "hotel_cancellations": [],
            "transport_reschedules": [],
            "transport_cancellations": [],
            "rsvp_changes": [],
            "schedule_changes": [],
            "sent_notifications": [],
        }

    def _hydrate_flight(self, flight: dict[str, Any]) -> dict[str, Any]:
        hydrated = deepcopy(flight)
        hydrated["last_action_index"] = None
        hydrated["last_updated"] = None
        return hydrated

    def _hydrate_hotel_booking(self, booking: dict[str, Any]) -> dict[str, Any]:
        hydrated = deepcopy(booking)
        hydrated["last_action_index"] = None
        hydrated["last_updated"] = None
        return hydrated

    def _hydrate_transport_booking(self, booking: dict[str, Any]) -> dict[str, Any]:
        hydrated = deepcopy(booking)
        hydrated["last_action_index"] = None
        hydrated["last_updated"] = None
        return hydrated

    def _hydrate_conference(self, conference: dict[str, Any]) -> dict[str, Any]:
        hydrated = deepcopy(conference)
        for attendee in hydrated.get("attendees", []):
            attendee["last_action_index"] = None
        for session_item in hydrated.get("sessions", []):
            session_item["last_action_index"] = None
        return hydrated

    def _next_event(self, session: dict[str, Any]) -> tuple[str, int]:
        action_index = int(session["meta"]["action_index"]) + 1
        session["meta"]["action_index"] = action_index
        event_at = (_coerce_iso_datetime(session["meta"]["base_time"]) + timedelta(minutes=action_index)).isoformat()
        return event_at, action_index

    def _record_action(
        self,
        session: dict[str, Any],
        action_index: int,
        event_at: str,
        action_type: str,
        details: dict[str, Any],
    ) -> None:
        session["actions"].append(
            {
                "action_index": action_index,
                "timestamp": event_at,
                "action_type": action_type,
                "details": details,
            }
        )
