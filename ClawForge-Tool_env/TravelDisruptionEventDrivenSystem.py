from copy import deepcopy
from typing import Dict, List, Optional, Any
from datetime import datetime
import re

DEFAULT_STATE = {
    "rules": [],
    "event_log": [],
    "action_log": [],
    "monitored_sources": {},
    "itineraries": {},
    "hotel_bookings": {},
    "pickup_reservations": {},
    "notification_log": [],
    "rule_counter": 1,
    "event_counter": 1,
    "booking_counter": 1,
    "pickup_counter": 1,
}

VALID_TRIGGER_TYPES = (
    "flight_delay",
    "flight_cancel",
    "flight_update",
    "gate_change",
    "baggage_alert",
    "weather_disruption",
    "connection_risk",
)

VALID_CONDITION_OPS = ("eq", "neq", "gt", "lt", "gte", "lte", "contains", "matches")

VALID_ACTION_TYPES = (
    "modify_hotel_checkin",
    "cancel_hotel_booking",
    "reschedule_pickup",
    "cancel_pickup",
    "send_delay_notification",
    "send_cancellation_notification",
    "update_itinerary",
    "log_alert",
)


class TravelDisruptionEventDrivenEnv:
    """
    An event-driven environment for dynamic travel itinerary adjustment.

    When flight disruptions (delays, cancellations, gate changes, etc.) are detected,
    this environment automatically evaluates configured rules and executes corrective
    actions such as modifying hotel check-in times, rescheduling airport pickups, and
    sending delay notification emails to meeting participants.

    Attributes:
        rules (List[Dict]): Configured automation rules (trigger + condition → actions).
        event_log (List[Dict]): History of all injected disruption events.
        action_log (List[Dict]): History of all executed actions.
        monitored_sources (Dict): Registered flight/travel data sources.
        itineraries (Dict): Stored travel itineraries keyed by itinerary_id.
        hotel_bookings (Dict): Hotel booking records keyed by booking_id.
        pickup_reservations (Dict): Airport pickup records keyed by pickup_id.
        notification_log (List[Dict]): History of all sent notifications.
        rule_counter (int): Auto-incrementing rule ID counter.
        event_counter (int): Auto-incrementing event ID counter.
        booking_counter (int): Auto-incrementing hotel booking ID counter.
        pickup_counter (int): Auto-incrementing pickup reservation ID counter.
    """

    def __init__(self):
        self.rules: List[Dict[str, Any]]
        self.event_log: List[Dict[str, Any]]
        self.action_log: List[Dict[str, Any]]
        self.monitored_sources: Dict[str, Dict[str, Any]]
        self.itineraries: Dict[str, Dict[str, Any]]
        self.hotel_bookings: Dict[str, Dict[str, Any]]
        self.pickup_reservations: Dict[str, Dict[str, Any]]
        self.notification_log: List[Dict[str, Any]]
        self.rule_counter: int
        self.event_counter: int
        self.booking_counter: int
        self.pickup_counter: int
        self._api_description = (
            "This tool manages dynamic travel itinerary adjustments triggered by flight "
            "disruptions — automatically modifying hotel bookings, rescheduling airport "
            "pickups, and sending delay notifications to meeting participants."
        )

    def _load_scenario(self, scenario: dict, long_context: bool = False) -> None:
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_STATE)
        self.rules = scenario.get("rules", DEFAULT_STATE_COPY["rules"])
        self.event_log = scenario.get("event_log", DEFAULT_STATE_COPY["event_log"])
        self.action_log = scenario.get("action_log", DEFAULT_STATE_COPY["action_log"])
        self.monitored_sources = scenario.get("monitored_sources", DEFAULT_STATE_COPY["monitored_sources"])
        self.itineraries = scenario.get("itineraries", DEFAULT_STATE_COPY["itineraries"])
        self.hotel_bookings = scenario.get("hotel_bookings", DEFAULT_STATE_COPY["hotel_bookings"])
        self.pickup_reservations = scenario.get("pickup_reservations", DEFAULT_STATE_COPY["pickup_reservations"])
        self.notification_log = scenario.get("notification_log", DEFAULT_STATE_COPY["notification_log"])
        self.rule_counter = scenario.get("rule_counter", DEFAULT_STATE_COPY["rule_counter"])
        self.event_counter = scenario.get("event_counter", DEFAULT_STATE_COPY["event_counter"])
        self.booking_counter = scenario.get("booking_counter", DEFAULT_STATE_COPY["booking_counter"])
        self.pickup_counter = scenario.get("pickup_counter", DEFAULT_STATE_COPY["pickup_counter"])

    def get_env_state(self) -> dict:
        """
        Return the current internal state of the environment.

        Returns:
            dict: All environment state variables including rules, event_log,
                action_log, monitored_sources, itineraries, hotel_bookings,
                pickup_reservations, notification_log, and all counters.
        """
        return {
            "rules": self.rules,
            "event_log": self.event_log,
            "action_log": self.action_log,
            "monitored_sources": self.monitored_sources,
            "itineraries": self.itineraries,
            "hotel_bookings": self.hotel_bookings,
            "pickup_reservations": self.pickup_reservations,
            "notification_log": self.notification_log,
            "rule_counter": self.rule_counter,
            "event_counter": self.event_counter,
            "booking_counter": self.booking_counter,
            "pickup_counter": self.pickup_counter,
        }

    # ── Source management ──────────────────────────────────────────────

    def register_source(self, name: str, source_type: str) -> Dict[str, Any]:
        """
        Register a new flight or travel data source to monitor.

        Args:
            name (str): Unique name for the source (e.g., 'airline_api_CA', 'airport_flightradar').
            source_type (str): Type of events this source emits. Must be one of the
                valid trigger types: flight_delay, flight_cancel, flight_update,
                gate_change, baggage_alert, weather_disruption, connection_risk.

        Returns:
            success (bool): Whether registration succeeded.
            source (Dict): The registered source metadata including name, type,
                active status, and event count.
        """
        if source_type not in VALID_TRIGGER_TYPES:
            return {
                "error": (
                    f"Invalid source_type '{source_type}'. "
                    f"Must be one of: {', '.join(VALID_TRIGGER_TYPES)}"
                )
            }
        if name in self.monitored_sources:
            return {"error": f"Source '{name}' is already registered."}
        self.monitored_sources[name] = {
            "type": source_type,
            "active": True,
            "event_count": 0,
        }
        return {"success": True, "source": {"name": name, **self.monitored_sources[name]}}

    def list_sources(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        List all registered travel data sources and their current status.

        Returns:
            sources (List[Dict]): All registered sources, each containing name,
                type, active status, and total event count received.
        """
        return {
            "sources": [{"name": k, **v} for k, v in self.monitored_sources.items()]
        }

    def deactivate_source(self, name: str) -> Dict[str, Any]:
        """
        Deactivate a registered source so its events are no longer processed.

        Args:
            name (str): Name of the source to deactivate.

        Returns:
            success (bool): Whether deactivation succeeded.
            source (Dict): Updated source metadata.
        """
        if name not in self.monitored_sources:
            return {"error": f"Source '{name}' is not registered."}
        self.monitored_sources[name]["active"] = False
        return {"success": True, "source": {"name": name, **self.monitored_sources[name]}}

    # ── Itinerary management ───────────────────────────────────────────

    def create_itinerary(
        self,
        itinerary_id: str,
        traveler_name: str,
        flight_number: str,
        origin: str,
        destination: str,
        scheduled_departure: str,
        scheduled_arrival: str,
        participant_emails: List[str],
    ) -> Dict[str, Any]:
        """
        Create a travel itinerary record to be monitored for disruptions.

        Args:
            itinerary_id (str): Unique identifier for this itinerary (e.g., 'ITIN-2024-001').
            traveler_name (str): Full name of the traveler.
            flight_number (str): Flight number (e.g., 'CA1234').
            origin (str): IATA code of the departure airport (e.g., 'PEK').
            destination (str): IATA code of the arrival airport (e.g., 'SHA').
            scheduled_departure (str): Scheduled departure time (e.g., '2024-06-15T08:00').
            scheduled_arrival (str): Scheduled arrival time (e.g., '2024-06-15T10:30').
            participant_emails (List[str]): Email addresses of meeting participants
                who should be notified of any disruptions.

        Returns:
            success (bool): Whether creation succeeded.
            itinerary (Dict): The created itinerary record.
        """
        if itinerary_id in self.itineraries:
            return {"error": f"Itinerary '{itinerary_id}' already exists."}
        if not participant_emails:
            return {"error": "At least one participant email is required."}
        if not flight_number:
            return {"error": "flight_number cannot be empty."}

        itinerary = {
            "itinerary_id": itinerary_id,
            "traveler_name": traveler_name,
            "flight_number": flight_number,
            "origin": origin,
            "destination": destination,
            "scheduled_departure": scheduled_departure,
            "scheduled_arrival": scheduled_arrival,
            "actual_departure": None,
            "actual_arrival": None,
            "delay_minutes": 0,
            "status": "on_time",
            "participant_emails": participant_emails,
        }
        self.itineraries[itinerary_id] = itinerary
        return {"success": True, "itinerary": itinerary}

    def get_itinerary(self, itinerary_id: str) -> Dict[str, Any]:
        """
        Retrieve a specific itinerary by its ID.

        Args:
            itinerary_id (str): The unique itinerary identifier.

        Returns:
            itinerary (Dict): The itinerary record, or an error if not found.
        """
        itinerary = self.itineraries.get(itinerary_id)
        if not itinerary:
            return {"error": f"Itinerary '{itinerary_id}' not found."}
        return {"itinerary": itinerary}

    def list_itineraries(self, status: Optional[str] = None) -> Dict[str, Any]:
        """
        List all stored itineraries, optionally filtered by status.

        Args:
            status (str): [Optional] Filter by itinerary status.
                Valid values: on_time, delayed, cancelled, completed.

        Returns:
            itineraries (List[Dict]): Matching itinerary records.
            total (int): Total number of matching itineraries.
        """
        valid_statuses = ("on_time", "delayed", "cancelled", "completed")
        if status and status not in valid_statuses:
            return {
                "error": (
                    f"Invalid status '{status}'. "
                    f"Must be one of: {', '.join(valid_statuses)}"
                )
            }
        result = list(self.itineraries.values())
        if status:
            result = [i for i in result if i["status"] == status]
        return {"itineraries": result, "total": len(result)}

    # ── Hotel booking management ───────────────────────────────────────

    def create_hotel_booking(
        self,
        itinerary_id: str,
        hotel_name: str,
        checkin_time: str,
        checkout_time: str,
        room_type: str,
        confirmation_number: str,
    ) -> Dict[str, Any]:
        """
        Create a hotel booking record linked to a travel itinerary.

        Args:
            itinerary_id (str): The itinerary this booking belongs to.
            hotel_name (str): Name of the hotel (e.g., 'Marriott Shanghai').
            checkin_time (str): Scheduled check-in time (e.g., '2024-06-15T15:00').
            checkout_time (str): Scheduled check-out time (e.g., '2024-06-17T12:00').
            room_type (str): Room category (e.g., 'Deluxe King', 'Standard Twin').
            confirmation_number (str): Hotel confirmation/reservation number.

        Returns:
            success (bool): Whether creation succeeded.
            booking (Dict): The created hotel booking record including booking_id.
        """
        if itinerary_id not in self.itineraries:
            return {"error": f"Itinerary '{itinerary_id}' not found."}

        booking_id = f"HTL-{self.booking_counter:04d}"
        self.booking_counter += 1

        booking = {
            "booking_id": booking_id,
            "itinerary_id": itinerary_id,
            "hotel_name": hotel_name,
            "checkin_time": checkin_time,
            "checkout_time": checkout_time,
            "room_type": room_type,
            "confirmation_number": confirmation_number,
            "status": "confirmed",
            "original_checkin_time": checkin_time,
            "modification_history": [],
        }
        self.hotel_bookings[booking_id] = booking
        return {"success": True, "booking": booking}

    def modify_hotel_checkin(
        self,
        booking_id: str,
        new_checkin_time: str,
        reason: str,
    ) -> Dict[str, Any]:
        """
        Modify the check-in time of an existing hotel booking.

        Args:
            booking_id (str): The hotel booking ID to modify (e.g., 'HTL-0001').
            new_checkin_time (str): The new check-in time (e.g., '2024-06-15T19:00').
            reason (str): Reason for the modification (e.g., 'Flight CA1234 delayed by 240 min').

        Returns:
            success (bool): Whether modification succeeded.
            booking (Dict): The updated booking record.
        """
        booking = self.hotel_bookings.get(booking_id)
        if not booking:
            return {"error": f"Hotel booking '{booking_id}' not found."}
        if booking["status"] == "cancelled":
            return {"error": f"Cannot modify a cancelled booking '{booking_id}'."}

        old_checkin = booking["checkin_time"]
        booking["modification_history"].append({
            "field": "checkin_time",
            "old_value": old_checkin,
            "new_value": new_checkin_time,
            "reason": reason,
        })
        booking["checkin_time"] = new_checkin_time
        return {"success": True, "booking": booking}

    def cancel_hotel_booking(self, booking_id: str, reason: str) -> Dict[str, Any]:
        """
        Cancel an existing hotel booking.

        Args:
            booking_id (str): The hotel booking ID to cancel.
            reason (str): Reason for cancellation.

        Returns:
            success (bool): Whether cancellation succeeded.
            booking (Dict): The updated booking record with status 'cancelled'.
        """
        booking = self.hotel_bookings.get(booking_id)
        if not booking:
            return {"error": f"Hotel booking '{booking_id}' not found."}
        if booking["status"] == "cancelled":
            return {"error": f"Booking '{booking_id}' is already cancelled."}

        booking["status"] = "cancelled"
        booking["modification_history"].append({
            "field": "status",
            "old_value": "confirmed",
            "new_value": "cancelled",
            "reason": reason,
        })
        return {"success": True, "booking": booking}

    def list_hotel_bookings(self, itinerary_id: Optional[str] = None) -> Dict[str, Any]:
        """
        List hotel bookings, optionally filtered by itinerary.

        Args:
            itinerary_id (str): [Optional] Filter bookings by itinerary ID.

        Returns:
            bookings (List[Dict]): Matching hotel booking records.
            total (int): Total number of matching bookings.
        """
        bookings = list(self.hotel_bookings.values())
        if itinerary_id:
            bookings = [b for b in bookings if b["itinerary_id"] == itinerary_id]
        return {"bookings": bookings, "total": len(bookings)}

    # ── Pickup reservation management ─────────────────────────────────

    def create_pickup_reservation(
        self,
        itinerary_id: str,
        driver_name: str,
        vehicle_type: str,
        pickup_location: str,
        pickup_time: str,
        dropoff_location: str,
        contact_phone: str,
    ) -> Dict[str, Any]:
        """
        Create an airport pickup reservation linked to a travel itinerary.

        Args:
            itinerary_id (str): The itinerary this pickup belongs to.
            driver_name (str): Name of the assigned driver or service provider.
            vehicle_type (str): Type of vehicle (e.g., 'Sedan', 'SUV', 'Van').
            pickup_location (str): Pickup point (e.g., 'PVG Terminal 2 Arrivals').
            pickup_time (str): Scheduled pickup time (e.g., '2024-06-15T11:00').
            dropoff_location (str): Drop-off destination (e.g., 'Marriott Shanghai').
            contact_phone (str): Driver or service contact phone number.

        Returns:
            success (bool): Whether creation succeeded.
            reservation (Dict): The created pickup reservation including pickup_id.
        """
        if itinerary_id not in self.itineraries:
            return {"error": f"Itinerary '{itinerary_id}' not found."}

        pickup_id = f"PKP-{self.pickup_counter:04d}"
        self.pickup_counter += 1

        reservation = {
            "pickup_id": pickup_id,
            "itinerary_id": itinerary_id,
            "driver_name": driver_name,
            "vehicle_type": vehicle_type,
            "pickup_location": pickup_location,
            "pickup_time": pickup_time,
            "dropoff_location": dropoff_location,
            "contact_phone": contact_phone,
            "status": "confirmed",
            "original_pickup_time": pickup_time,
            "modification_history": [],
        }
        self.pickup_reservations[pickup_id] = reservation
        return {"success": True, "reservation": reservation}

    def reschedule_pickup(
        self,
        pickup_id: str,
        new_pickup_time: str,
        reason: str,
    ) -> Dict[str, Any]:
        """
        Reschedule an existing airport pickup reservation to a new time.

        Args:
            pickup_id (str): The pickup reservation ID to reschedule (e.g., 'PKP-0001').
            new_pickup_time (str): The new pickup time (e.g., '2024-06-15T15:30').
            reason (str): Reason for rescheduling (e.g., 'Flight CA1234 delayed by 240 min').

        Returns:
            success (bool): Whether rescheduling succeeded.
            reservation (Dict): The updated pickup reservation record.
        """
        reservation = self.pickup_reservations.get(pickup_id)
        if not reservation:
            return {"error": f"Pickup reservation '{pickup_id}' not found."}
        if reservation["status"] == "cancelled":
            return {"error": f"Cannot reschedule a cancelled pickup '{pickup_id}'."}

        old_time = reservation["pickup_time"]
        reservation["modification_history"].append({
            "field": "pickup_time",
            "old_value": old_time,
            "new_value": new_pickup_time,
            "reason": reason,
        })
        reservation["pickup_time"] = new_pickup_time
        return {"success": True, "reservation": reservation}

    def cancel_pickup(self, pickup_id: str, reason: str) -> Dict[str, Any]:
        """
        Cancel an existing airport pickup reservation.

        Args:
            pickup_id (str): The pickup reservation ID to cancel.
            reason (str): Reason for cancellation.

        Returns:
            success (bool): Whether cancellation succeeded.
            reservation (Dict): The updated reservation record with status 'cancelled'.
        """
        reservation = self.pickup_reservations.get(pickup_id)
        if not reservation:
            return {"error": f"Pickup reservation '{pickup_id}' not found."}
        if reservation["status"] == "cancelled":
            return {"error": f"Pickup '{pickup_id}' is already cancelled."}

        reservation["status"] = "cancelled"
        reservation["modification_history"].append({
            "field": "status",
            "old_value": "confirmed",
            "new_value": "cancelled",
            "reason": reason,
        })
        return {"success": True, "reservation": reservation}

    def list_pickup_reservations(self, itinerary_id: Optional[str] = None) -> Dict[str, Any]:
        """
        List pickup reservations, optionally filtered by itinerary.

        Args:
            itinerary_id (str): [Optional] Filter reservations by itinerary ID.

        Returns:
            reservations (List[Dict]): Matching pickup reservation records.
            total (int): Total number of matching reservations.
        """
        reservations = list(self.pickup_reservations.values())
        if itinerary_id:
            reservations = [r for r in reservations if r["itinerary_id"] == itinerary_id]
        return {"reservations": reservations, "total": len(reservations)}

    # ── Notification management ────────────────────────────────────────

    def send_delay_notification(
        self,
        itinerary_id: str,
        subject: str,
        message: str,
        recipient_emails: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Send a delay notification email to meeting participants of an itinerary.

        If recipient_emails is not provided, the notification is sent to all
        participant_emails stored in the itinerary record.

        Args:
            itinerary_id (str): The itinerary whose participants should be notified.
            subject (str): Email subject line.
            message (str): Email body content describing the disruption and impact.
            recipient_emails (List[str]): [Optional] Override recipient list. If omitted,
                uses the participant_emails from the itinerary.

        Returns:
            success (bool): Whether the notification was dispatched.
            notification (Dict): The notification record including recipients,
                subject, message, and notification_id.
        """
        itinerary = self.itineraries.get(itinerary_id)
        if not itinerary:
            return {"error": f"Itinerary '{itinerary_id}' not found."}

        recipients = recipient_emails if recipient_emails else itinerary["participant_emails"]
        if not recipients:
            return {"error": "No recipient emails available for notification."}

        notification_id = f"NOTIF-{len(self.notification_log) + 1:04d}"
        notification = {
            "notification_id": notification_id,
            "itinerary_id": itinerary_id,
            "type": "delay_notification",
            "recipients": recipients,
            "subject": subject,
            "message": message,
            "status": "sent",
        }
        self.notification_log.append(notification)
        return {"success": True, "notification": notification}

    def get_notification_log(
        self,
        itinerary_id: Optional[str] = None,
        limit: int = 50,
    ) -> Dict[str, Any]:
        """
        Retrieve the history of sent notifications.

        Args:
            itinerary_id (str): [Optional] Filter notifications by itinerary ID.
            limit (int): Maximum number of notifications to return. Defaults to 50.

        Returns:
            notifications (List[Dict]): Matching notification records, newest first.
            total (int): Total number of matching notifications.
        """
        log = self.notification_log
        if itinerary_id:
            log = [n for n in log if n["itinerary_id"] == itinerary_id]
        log = list(reversed(log))[:limit]
        return {"notifications": log, "total": len(log)}

    # ── Rule management ────────────────────────────────────────────────

    def create_rule(
        self,
        name: str,
        trigger_type: str,
        condition_field: str,
        condition_op: str,
        condition_value: str,
        actions: List[Dict[str, Any]],
        source_filter: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create an automation rule that responds to travel disruption events.

        When an event matching trigger_type (and optionally source_filter) is injected,
        the environment evaluates the condition against the event payload. If the condition
        is met, all listed actions are executed in order.

        Args:
            name (str): Human-readable rule name (e.g., 'Delay >2h: modify hotel checkin').
            trigger_type (str): Event type that activates this rule. Must be one of:
                flight_delay, flight_cancel, flight_update, gate_change,
                baggage_alert, weather_disruption, connection_risk.
            condition_field (str): Field in the event payload to evaluate
                (e.g., 'delay_minutes', 'flight_number', 'severity').
            condition_op (str): Comparison operator — eq, neq, gt, lt, gte, lte,
                contains, matches.
            condition_value (str): Value to compare against (e.g., '120' for 2 hours).
            actions (List[Dict]): Ordered list of actions to execute when condition is met.
                Each action must have 'type' (one of the valid action types) and 'params' dict.
                Valid action types: modify_hotel_checkin, cancel_hotel_booking,
                reschedule_pickup, cancel_pickup, send_delay_notification,
                send_cancellation_notification, update_itinerary, log_alert.
            source_filter (str): [Optional] Only trigger from this specific registered source.

        Returns:
            rule_id (int): Unique rule identifier.
            rule (Dict): The created rule with all fields including trigger, condition,
                actions, source_filter, enabled status, and match_count.
        """
        if trigger_type not in VALID_TRIGGER_TYPES:
            return {
                "error": (
                    f"Invalid trigger_type '{trigger_type}'. "
                    f"Must be one of: {', '.join(VALID_TRIGGER_TYPES)}"
                )
            }
        if condition_op not in VALID_CONDITION_OPS:
            return {
                "error": (
                    f"Invalid condition_op '{condition_op}'. "
                    f"Must be one of: {', '.join(VALID_CONDITION_OPS)}"
                )
            }
        if not actions:
            return {"error": "At least one action is required."}
        if source_filter and source_filter not in self.monitored_sources:
            return {"error": f"Source filter '{source_filter}' is not a registered source."}

        invalid_action_types = [
            a.get("type") for a in actions
            if a.get("type") not in VALID_ACTION_TYPES
        ]
        if invalid_action_types:
            return {
                "error": (
                    f"Invalid action type(s): {', '.join(str(t) for t in invalid_action_types)}. "
                    f"Must be one of: {', '.join(VALID_ACTION_TYPES)}"
                )
            }

        rule_id = self.rule_counter
        self.rule_counter += 1

        rule = {
            "rule_id": rule_id,
            "name": name,
            "enabled": True,
            "trigger_type": trigger_type,
            "condition": {
                "field": condition_field,
                "op": condition_op,
                "value": condition_value,
            },
            "actions": actions,
            "source_filter": source_filter,
            "match_count": 0,
        }
        self.rules.append(rule)
        return {"rule_id": rule_id, "rule": rule}

    def update_rule(self, rule_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update fields of an existing automation rule.

        Args:
            rule_id (int): ID of the rule to update.
            updates (Dict): Fields to change. Allowed keys:
                name, enabled, trigger_type, condition, actions, source_filter.

        Returns:
            success (bool): Whether the update succeeded.
            rule (Dict): The updated rule record.
        """
        rule = self._find_rule(rule_id)
        if not rule:
            return {"error": f"Rule ID {rule_id} not found."}

        allowed_fields = {"name", "enabled", "trigger_type", "condition", "actions", "source_filter"}
        invalid = set(updates.keys()) - allowed_fields
        if invalid:
            return {"error": f"Invalid update fields: {', '.join(invalid)}"}

        for key, value in updates.items():
            if key == "trigger_type" and value not in VALID_TRIGGER_TYPES:
                return {
                    "error": (
                        f"Invalid trigger_type '{value}'. "
                        f"Must be one of: {', '.join(VALID_TRIGGER_TYPES)}"
                    )
                }
            rule[key] = value

        return {"success": True, "rule": rule}

    def delete_rule(self, rule_id: int) -> Dict[str, Any]:
        """
        Delete an automation rule permanently.

        Args:
            rule_id (int): ID of the rule to delete.

        Returns:
            status (str): Deletion confirmation message.
        """
        rule = self._find_rule(rule_id)
        if not rule:
            return {"error": f"Rule ID {rule_id} not found."}
        self.rules.remove(rule)
        return {"rule_id": rule_id, "status": "deleted"}

    def _find_rule(self, rule_id: int) -> Optional[Dict[str, Any]]:
        """Find a rule by its rule_id."""
        for rule in self.rules:
            if rule.get("rule_id") == rule_id:
                return rule
        return None

    def _log(self, event: str, detail: Dict) -> None:
        """Log environment events."""
        if not hasattr(self, '_event_log'):
            self._event_log: List[Dict[str, Any]] = []
        self._event_log.append({
            "event": event,
            "detail": detail,
            "timestamp": datetime.now().isoformat()
        })