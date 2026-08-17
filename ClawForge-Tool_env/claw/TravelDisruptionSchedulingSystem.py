from copy import deepcopy
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

DEFAULT_STATE = {
    "flights": [],
    "hotels": [],
    "pickups": [],
    "meetings": [],
    "notifications": [],
    "disruption_log": [],
    "flight_counter": 1,
    "hotel_counter": 1,
    "pickup_counter": 1,
    "meeting_counter": 1,
    "notification_counter": 1,
}

VALID_FLIGHT_STATUSES = ("scheduled", "delayed", "cancelled", "arrived")
VALID_HOTEL_STATUSES = ("confirmed", "modified", "cancelled")
VALID_PICKUP_STATUSES = ("scheduled", "modified", "cancelled", "completed")
VALID_MEETING_STATUSES = ("scheduled", "delayed", "cancelled", "completed")
VALID_NOTIFICATION_TYPES = ("delay", "reschedule", "cancellation", "reminder")


class TravelDisruptionSchedulingEnv:
    """
    A travel itinerary disruption management environment with dynamic optimization.

    This class models a travel coordination system where flight delays trigger
    cascading adjustments to hotel bookings, airport pickups, and meeting schedules.
    Automatic notifications are sent to affected participants. The core pattern
    follows time-slot scheduling with constraint resolution adapted for travel logistics.

    Attributes:
        flights (List[Dict]): Registered flight records.
        hotels (List[Dict]): Hotel booking records.
        pickups (List[Dict]): Airport pickup arrangements.
        meetings (List[Dict]): Meeting schedules linked to travel.
        notifications (List[Dict]): Sent notification records.
        disruption_log (List[Dict]): History of disruptions and resolutions.
        flight_counter (int): Auto-incrementing flight ID counter.
        hotel_counter (int): Auto-incrementing hotel booking ID counter.
        pickup_counter (int): Auto-incrementing pickup ID counter.
        meeting_counter (int): Auto-incrementing meeting ID counter.
        notification_counter (int): Auto-incrementing notification ID counter.
    """

    def __init__(self):
        self.flights: List[Dict[str, Any]]
        self.hotels: List[Dict[str, Any]]
        self.pickups: List[Dict[str, Any]]
        self.meetings: List[Dict[str, Any]]
        self.notifications: List[Dict[str, Any]]
        self.disruption_log: List[Dict[str, Any]]
        self.flight_counter: int
        self.hotel_counter: int
        self.pickup_counter: int
        self.meeting_counter: int
        self.notification_counter: int
        self._api_description = (
            "This tool manages travel itinerary disruptions with dynamic optimization. "
            "Monitor flight delays, automatically adjust hotel bookings and airport pickups, "
            "and send delay notifications to meeting participants."
        )

    def _load_scenario(self, scenario: dict, long_context=False) -> None:
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_STATE)
        self.flights = scenario.get("flights", DEFAULT_STATE_COPY["flights"])
        self.hotels = scenario.get("hotels", DEFAULT_STATE_COPY["hotels"])
        self.pickups = scenario.get("pickups", DEFAULT_STATE_COPY["pickups"])
        self.meetings = scenario.get("meetings", DEFAULT_STATE_COPY["meetings"])
        self.notifications = scenario.get("notifications", DEFAULT_STATE_COPY["notifications"])
        self.disruption_log = scenario.get("disruption_log", DEFAULT_STATE_COPY["disruption_log"])
        self.flight_counter = scenario.get("flight_counter", DEFAULT_STATE_COPY["flight_counter"])
        self.hotel_counter = scenario.get("hotel_counter", DEFAULT_STATE_COPY["hotel_counter"])
        self.pickup_counter = scenario.get("pickup_counter", DEFAULT_STATE_COPY["pickup_counter"])
        self.meeting_counter = scenario.get("meeting_counter", DEFAULT_STATE_COPY["meeting_counter"])
        self.notification_counter = scenario.get("notification_counter", DEFAULT_STATE_COPY["notification_counter"])

    def get_env_state(self) -> dict:
        """
        Return the current internal state of the environment.

        Returns:
            dict: All environment state variables including flights, hotels,
                  pickups, meetings, notifications, disruption_log, and counters.
        """
        return {
            "flights": self.flights,
            "hotels": self.hotels,
            "pickups": self.pickups,
            "meetings": self.meetings,
            "notifications": self.notifications,
            "disruption_log": self.disruption_log,
            "flight_counter": self.flight_counter,
            "hotel_counter": self.hotel_counter,
            "pickup_counter": self.pickup_counter,
            "meeting_counter": self.meeting_counter,
            "notification_counter": self.notification_counter,
        }

    # ── Flight management ────────────────────────────────────────────────

    def register_flight(
        self,
        flight_number: str,
        departure_time: str,
        arrival_time: str,
        origin: str,
        destination: str,
        passenger_name: str,
        passenger_email: str,
    ) -> Dict[str, Any]:
        """
        Register a flight in the itinerary for monitoring.

        Args:
            flight_number (str): Flight number (e.g. 'CA1234').
            departure_time (str): Scheduled departure in ISO format (e.g. '2026-06-15T08:00').
            arrival_time (str): Scheduled arrival in ISO format.
            origin (str): Departure airport code (e.g. 'PEK').
            destination (str): Arrival airport code (e.g. 'SHA').
            passenger_name (str): Passenger's full name.
            passenger_email (str): Passenger's email for notifications.

        Returns:
            flight_id (int): Unique flight identifier.
            flight (Dict): The created flight record.
        """
        if not flight_number.strip():
            return {"error": "Flight number is required."}
        if not passenger_name.strip():
            return {"error": "Passenger name is required."}
        if departure_time >= arrival_time:
            return {"error": "departure_time must be before arrival_time."}

        flight_id = self.flight_counter
        self.flight_counter += 1

        flight = {
            "flight_id": flight_id,
            "flight_number": flight_number,
            "departure_time": departure_time,
            "arrival_time": arrival_time,
            "origin": origin,
            "destination": destination,
            "passenger_name": passenger_name,
            "passenger_email": passenger_email,
            "status": "scheduled",
            "delay_minutes": 0,
            "linked_hotels": [],
            "linked_pickups": [],
            "linked_meetings": [],
        }
        self.flights.append(flight)
        self._log("flight_registered", {"flight_id": flight_id, "flight_number": flight_number})
        return {"flight_id": flight_id, "flight": flight}

    def report_flight_delay(
        self,
        flight_id: int,
        delay_minutes: int,
        new_arrival_time: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Report a flight delay and trigger cascading adjustments.

        This automatically modifies linked hotel check-ins, pickup times,
        and sends delay notifications to meeting participants.

        Args:
            flight_id (int): The delayed flight ID.
            delay_minutes (int): Delay duration in minutes.
            new_arrival_time (str): [Optional] New arrival time. If not provided,
                                    calculated from original arrival + delay.

        Returns:
            flight_id (int): The flight ID.
            delay_minutes (int): Applied delay.
            adjustments (Dict): Summary of cascading adjustments made.
        """
        flight = self._find_flight(flight_id)
        if not flight:
            return {"error": f"Flight ID {flight_id} not found."}
        if delay_minutes <= 0:
            return {"error": "delay_minutes must be positive."}

        flight["status"] = "delayed"
        flight["delay_minutes"] = delay_minutes

        if new_arrival_time:
            flight["arrival_time"] = new_arrival_time
        else:
            flight["arrival_time"] = self._add_minutes(flight["arrival_time"], delay_minutes)

        adjustments = {
            "hotels_modified": [],
            "pickups_modified": [],
            "notifications_sent": [],
        }

        # Adjust linked hotels
        for hotel_id in flight["linked_hotels"]:
            hotel = self._find_hotel(hotel_id)
            if hotel and hotel["status"] == "confirmed":
                old_checkin = hotel["check_in_time"]
                hotel["check_in_time"] = self._add_minutes(old_checkin, delay_minutes)
                hotel["status"] = "modified"
                hotel["modification_reason"] = f"Flight {flight['flight_number']} delayed by {delay_minutes} minutes"
                adjustments["hotels_modified"].append({
                    "hotel_id": hotel_id,
                    "old_checkin": old_checkin,
                    "new_checkin": hotel["check_in_time"],
                })

        # Adjust linked pickups
        for pickup_id in flight["linked_pickups"]:
            pickup = self._find_pickup(pickup_id)
            if pickup and pickup["status"] == "scheduled":
                old_time = pickup["pickup_time"]
                pickup["pickup_time"] = self._add_minutes(old_time, delay_minutes)
                pickup["status"] = "modified"
                pickup["modification_reason"] = f"Flight {flight['flight_number']} delayed"
                adjustments["pickups_modified"].append({
                    "pickup_id": pickup_id,
                    "old_time": old_time,
                    "new_time": pickup["pickup_time"],
                })

        # Send notifications to meeting participants
        for meeting_id in flight["linked_meetings"]:
            meeting = self._find_meeting(meeting_id)
            if meeting and meeting["status"] == "scheduled":
                for participant in meeting["participants"]:
                    notif_id = self._send_notification(
                        recipient_email=participant["email"],
                        recipient_name=participant["name"],
                        notification_type="delay",
                        subject=f"Meeting Delay: {meeting['title']}",
                        message=(
                            f"Due to flight {flight['flight_number']} delay of {delay_minutes} minutes, "
                            f"{flight['passenger_name']} will arrive late. "
                            f"The meeting '{meeting['title']}' scheduled at {meeting['start_time']} may be affected."
                        ),
                        related_flight_id=flight_id,
                        related_meeting_id=meeting_id,
                    )
                    adjustments["notifications_sent"].append({
                        "notification_id": notif_id,
                        "recipient": participant["email"],
                        "meeting_id": meeting_id,
                    })

        self._log("flight_delay_reported", {
            "flight_id": flight_id,
            "delay_minutes": delay_minutes,
            "adjustments": adjustments,
        })

        return {
            "flight_id": flight_id,
            "delay_minutes": delay_minutes,
            "new_arrival_time": flight["arrival_time"],
            "adjustments": adjustments,
        }

    def check_flight_status(self, flight_id: int) -> Dict[str, Any]:
        """
        Check the current status of a flight and its linked items.

        Args:
            flight_id (int): Flight ID to check.

        Returns:
            flight (Dict): Flight details with status.
            linked_items (Dict): Summary of linked hotels, pickups, and meetings.
        """
        flight = self._find_flight(flight_id)
        if not flight:
            return {"error": f"Flight ID {flight_id} not found."}

        linked_items = {
            "hotels": [self._find_hotel(hid) for hid in flight["linked_hotels"]],
            "pickups": [self._find_pickup(pid) for pid in flight["linked_pickups"]],
            "meetings": [self._find_meeting(mid) for mid in flight["linked_meetings"]],
        }

        return {"flight": flight, "linked_items": linked_items}

    def list_flights(
        self,
        status: Optional[str] = None,
        date: Optional[str] = None,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        List all flights, optionally filtered by status or date.

        Args:
            status (str): [Optional] Filter by flight status.
            date (str): [Optional] Filter by departure date prefix (e.g. '2026-06-15').

        Returns:
            flights (List[Dict]): Matching flight summaries.
        """
        if status and status not in VALID_FLIGHT_STATUSES:
            return {"error": f"Invalid status '{status}'. Must be one of: {', '.join(VALID_FLIGHT_STATUSES)}"}

        flights = self.flights
        if status:
            flights = [f for f in flights if f["status"] == status]
        if date:
            flights = [f for f in flights if f["departure_time"].startswith(date)]

        summaries = [{
            "flight_id": f["flight_id"],
            "flight_number": f["flight_number"],
            "departure_time": f["departure_time"],
            "arrival_time": f["arrival_time"],
            "status": f["status"],
            "delay_minutes": f["delay_minutes"],
        } for f in flights]

        return {"flights": summaries}

    # ── Hotel booking management ─────────────────────────────────────────

    def book_hotel(
        self,
        flight_id: int,
        hotel_name: str,
        check_in_time: str,
        check_out_time: str,
        room_type: str = "standard",
        confirmation_number: str = "",
    ) -> Dict[str, Any]:
        """
        Book a hotel and link it to a flight for automatic adjustment.

        Args:
            flight_id (int): Associated flight ID.
            hotel_name (str): Hotel name.
            check_in_time (str): Check-in time in ISO format.
            check_out_time (str): Check-out time in ISO format.
            room_type (str): Room type. Defaults to 'standard'.
            confirmation_number (str): Hotel confirmation number.

        Returns:
            hotel_id (int): Unique hotel booking identifier.
            hotel (Dict): The created hotel booking record.
        """
        flight = self._find_flight(flight_id)
        if not flight:
            return {"error": f"Flight ID {flight_id} not found."}
        if not hotel_name.strip():
            return {"error": "Hotel name is required."}
        if check_in_time >= check_out_time:
            return {"error": "check_in_time must be before check_out_time."}

        hotel_id = self.hotel_counter
        self.hotel_counter += 1

        hotel = {
            "hotel_id": hotel_id,
            "flight_id": flight_id,
            "hotel_name": hotel_name,
            "check_in_time": check_in_time,
            "check_out_time": check_out_time,
            "room_type": room_type,
            "confirmation_number": confirmation_number,
            "status": "confirmed",
            "modification_reason": "",
        }

        self.hotels.append(hotel)
        flight["linked_hotels"].append(hotel_id)
        self._log("hotel_booked", {"hotel_id": hotel_id, "flight_id": flight_id})

        return {"hotel_id": hotel_id, "hotel": hotel}

    def modify_hotel_booking(
        self,
        hotel_id: int,
        new_check_in: Optional[str] = None,
        new_check_out: Optional[str] = None,
        reason: str = "",
    ) -> Dict[str, Any]:
        """
        Manually modify a hotel booking.

        Args:
            hotel_id (int): Hotel booking ID.
            new_check_in (str): [Optional] New check-in time.
            new_check_out (str): [Optional] New check-out time.
            reason (str): Reason for modification.

        Returns:
            hotel_id (int): The hotel booking ID.
            hotel (Dict): Updated hotel booking record.
        """
        hotel = self._find_hotel(hotel_id)
        if not hotel:
            return {"error": f"Hotel ID {hotel_id} not found."}

        if new_check_in:
            hotel["check_in_time"] = new_check_in
        if new_check_out:
            hotel["check_out_time"] = new_check_out
        if reason:
            hotel["modification_reason"] = reason

        hotel["status"] = "modified"
        self._log("hotel_modified", {"hotel_id": hotel_id, "reason": reason})

        return {"hotel_id": hotel_id, "hotel": hotel}

    def cancel_hotel_booking(self, hotel_id: int, reason: str = "") -> Dict[str, Any]:
        """
        Cancel a hotel booking.

        Args:
            hotel_id (int): Hotel booking ID.
            reason (str): Cancellation reason.

        Returns:
            hotel_id (int): The hotel booking ID.
            status (str): New status.
        """
        hotel = self._find_hotel(hotel_id)
        if not hotel:
            return {"error": f"Hotel ID {hotel_id} not found."}

        hotel["status"] = "cancelled"
        hotel["modification_reason"] = reason
        self._log("hotel_cancelled", {"hotel_id": hotel_id, "reason": reason})

        return {"hotel_id": hotel_id, "status": "cancelled"}

    def list_hotels(
        self,
        flight_id: Optional[int] = None,
        status: Optional[str] = None,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        List hotel bookings, optionally filtered.

        Args:
            flight_id (int): [Optional] Filter by associated flight.
            status (str): [Optional] Filter by booking status.

        Returns:
            hotels (List[Dict]): Matching hotel booking summaries.
        """
        if status and status not in VALID_HOTEL_STATUSES:
            return {"error": f"Invalid status '{status}'. Must be one of: {', '.join(VALID_HOTEL_STATUSES)}"}

        hotels = self.hotels
        if flight_id is not None:
            hotels = [h for h in hotels if h["flight_id"] == flight_id]
        if status:
            hotels = [h for h in hotels if h["status"] == status]

        return {"hotels": hotels}

    # ── Pickup arrangement management ────────────────────────────────────

    def arrange_pickup(
        self,
        flight_id: int,
        pickup_time: str,
        pickup_location: str,
        driver_name: str = "",
        driver_phone: str = "",
        vehicle_info: str = "",
    ) -> Dict[str, Any]:
        """
        Arrange airport pickup linked to a flight.

        Args:
            flight_id (int): Associated flight ID.
            pickup_time (str): Scheduled pickup time in ISO format.
            pickup_location (str): Pickup location (e.g. 'Terminal 2 Exit B').
            driver_name (str): Driver's name.
            driver_phone (str): Driver's contact phone.
            vehicle_info (str): Vehicle description.

        Returns:
            pickup_id (int): Unique pickup arrangement identifier.
            pickup (Dict): The created pickup record.
        """
        flight = self._find_flight(flight_id)
        if not flight:
            return {"error": f"Flight ID {flight_id} not found."}
        if not pickup_location.strip():
            return {"error": "Pickup location is required."}

        pickup_id = self.pickup_counter
        self.pickup_counter += 1

        pickup = {
            "pickup_id": pickup_id,
            "flight_id": flight_id,
            "pickup_time": pickup_time,
            "pickup_location": pickup_location,
            "driver_name": driver_name,
            "driver_phone": driver_phone,
            "vehicle_info": vehicle_info,
            "status": "scheduled",
            "modification_reason": "",
        }

        self.pickups.append(pickup)
        flight["linked_pickups"].append(pickup_id)
        self._log("pickup_arranged", {"pickup_id": pickup_id, "flight_id": flight_id})

        return {"pickup_id": pickup_id, "pickup": pickup}

    def modify_pickup(
        self,
        pickup_id: int,
        new_pickup_time: Optional[str] = None,
        new_location: Optional[str] = None,
        reason: str = "",
    ) -> Dict[str, Any]:
        """
        Manually modify a pickup arrangement.

        Args:
            pickup_id (int): Pickup arrangement ID.
            new_pickup_time (str): [Optional] New pickup time.
            new_location (str): [Optional] New pickup location.
            reason (str): Reason for modification.

        Returns:
            pickup_id (int): The pickup ID.
            pickup (Dict): Updated pickup record.
        """
        pickup = self._find_pickup(pickup_id)
        if not pickup:
            return {"error": f"Pickup ID {pickup_id} not found."}

        if new_pickup_time:
            pickup["pickup_time"] = new_pickup_time
        if new_location:
            pickup["pickup_location"] = new_location
        if reason:
            pickup["modification_reason"] = reason

        pickup["status"] = "modified"
        self._log("pickup_modified", {"pickup_id": pickup_id, "reason": reason})

        return {"pickup_id": pickup_id, "pickup": pickup}

    def cancel_pickup(self, pickup_id: int, reason: str = "") -> Dict[str, Any]:
        """
        Cancel a pickup arrangement.

        Args:
            pickup_id (int): Pickup arrangement ID.
            reason (str): Cancellation reason.

        Returns:
            pickup_id (int): The pickup ID.
            status (str): New status.
        """
        pickup = self._find_pickup(pickup_id)
        if not pickup:
            return {"error": f"Pickup ID {pickup_id} not found."}

        pickup["status"] = "cancelled"
        pickup["modification_reason"] = reason
        self._log("pickup_cancelled", {"pickup_id": pickup_id, "reason": reason})

        return {"pickup_id": pickup_id, "status": "cancelled"}

    def list_pickups(
        self,
        flight_id: Optional[int] = None,
        status: Optional[str] = None,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        List pickup arrangements, optionally filtered.

        Args:
            flight_id (int): [Optional] Filter by associated flight.
            status (str): [Optional] Filter by pickup status.

        Returns:
            pickups (List[Dict]): Matching pickup summaries.
        """
        if status and status not in VALID_PICKUP_STATUSES:
            return {"error": f"Invalid status '{status}'. Must be one of: {', '.join(VALID_PICKUP_STATUSES)}"}

        pickups = self.pickups
        if flight_id is not None:
            pickups = [p for p in pickups if p["flight_id"] == flight_id]
        if status:
            pickups = [p for p in pickups if p["status"] == status]

        return {"pickups": pickups}

    # ── Meeting management ───────────────────────────────────────────────

    def schedule_meeting(
        self,
        flight_id: int,
        title: str,
        start_time: str,
        end_time: str,
        location: str,
        participants: List[Dict[str, str]],
        priority: int = 5,
    ) -> Dict[str, Any]:
        """
        Schedule a meeting linked to a flight for delay notifications.

        Args:
            flight_id (int): Associated flight ID (traveler's flight).
            title (str): Meeting title.
            start_time (str): Meeting start time in ISO format.
            end_time (str): Meeting end time in ISO format.
            location (str): Meeting location or virtual link.
            participants (List[Dict]): List of participants with 'name' and 'email' keys.
            priority (int): Meeting priority 1-10. Defaults to 5.

        Returns:
            meeting_id (int): Unique meeting identifier.
            meeting (Dict): The created meeting record.
        """
        flight = self._find_flight(flight_id)
        if not flight:
            return {"error": f"Flight ID {flight_id} not found."}
        if not title.strip():
            return {"error": "Meeting title is required."}
        if start_time >= end_time:
            return {"error": "start_time must be before end_time."}
        if priority < 1 or priority > 10:
            return {"error": "Priority must be between 1 and 10."}
        if not participants:
            return {"error": "At least one participant is required."}

        for p in participants:
            if "name" not in p or "email" not in p:
                return {"error": "Each participant must have 'name' and 'email' keys."}

        meeting_id = self.meeting_counter
        self.meeting_counter += 1

        meeting = {
            "meeting_id": meeting_id,
            "flight_id": flight_id,
            "title": title,
            "start_time": start_time,
            "end_time": end_time,
            "location": location,
            "participants": participants,
            "priority": priority,
            "status": "scheduled",
            "delay_notified": False,
        }

        self.meetings.append(meeting)
        flight["linked_meetings"].append(meeting_id)
        self._log("meeting_scheduled", {"meeting_id": meeting_id, "flight_id": flight_id})

        return {"meeting_id": meeting_id, "meeting": meeting}

    def reschedule_meeting(
        self,
        meeting_id: int,
        new_start_time: str,
        new_end_time: str,
        notify_participants: bool = True,
    ) -> Dict[str, Any]:
        """
        Reschedule a meeting and optionally notify participants.

        Args:
            meeting_id (int): Meeting ID.
            new_start_time (str): New start time.
            new_end_time (str): New end time.
            notify_participants (bool): Whether to send reschedule notifications.

        Returns:
            meeting_id (int): The meeting ID.
            meeting (Dict): Updated meeting record.
            notifications_sent (List): Notification details if sent.
        """
        meeting = self._find_meeting(meeting_id)
        if not meeting:
            return {"error": f"Meeting ID {meeting_id} not found."}
        if new_start_time >= new_end_time:
            return {"error": "new_start_time must be before new_end_time."}

        old_start = meeting["start_time"]
        meeting["start_time"] = new_start_time
        meeting["end_time"] = new_end_time

        notifications_sent = []
        if notify_participants:
            for participant in meeting["participants"]:
                notif_id = self._send_notification(
                    recipient_email=participant["email"],
                    recipient_name=participant["name"],
                    notification_type="reschedule",
                    subject=f"Meeting Rescheduled: {meeting['title']}",
                    message=(
                        f"The meeting '{meeting['title']}' has been rescheduled "
                        f"from {old_start} to {new_start_time}."
                    ),
                    related_meeting_id=meeting_id,
                )
                notifications_sent.append({
                    "notification_id": notif_id,
                    "recipient": participant["email"],
                })

        self._log("meeting_rescheduled", {
            "meeting_id": meeting_id,
            "old_start": old_start,
            "new_start": new_start_time,
        })

        return {
            "meeting_id": meeting_id,
            "meeting": meeting,
            "notifications_sent": notifications_sent,
        }

    def cancel_meeting(
        self,
        meeting_id: int,
        reason: str = "",
        notify_participants: bool = True,
    ) -> Dict[str, Any]:
        """
        Cancel a meeting and optionally notify participants.

        Args:
            meeting_id (int): Meeting ID.
            reason (str): Cancellation reason.
            notify_participants (bool): Whether to send cancellation notifications.

        Returns:
            meeting_id (int): The meeting ID.
            status (str): New status.
            notifications_sent (List): Notification details if sent.
        """
        meeting = self._find_meeting(meeting_id)
        if not meeting:
            return {"error": f"Meeting ID {meeting_id} not found."}

        meeting["status"] = "cancelled"

        notifications_sent = []
        if notify_participants:
            for participant in meeting["participants"]:
                notif_id = self._send_notification(
                    recipient_email=participant["email"],
                    recipient_name=participant["name"],
                    notification_type="cancellation",
                    subject=f"Meeting Cancelled: {meeting['title']}",
                    message=f"The meeting '{meeting['title']}' has been cancelled. Reason: {reason or 'Not specified'}",
                    related_meeting_id=meeting_id,
                )
                notifications_sent.append({
                    "notification_id": notif_id,
                    "recipient": participant["email"],
                })

        self._log("meeting_cancelled", {"meeting_id": meeting_id, "reason": reason})

        return {
            "meeting_id": meeting_id,
            "status": "cancelled",
            "notifications_sent": notifications_sent,
        }

    def list_meetings(
        self,
        flight_id: Optional[int] = None,
        status: Optional[str] = None,
        date: Optional[str] = None,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        List meetings, optionally filtered.

        Args:
            flight_id (int): [Optional] Filter by associated flight.
            status (str): [Optional] Filter by meeting status.
            date (str): [Optional] Filter by date prefix.

        Returns:
            meetings (List[Dict]): Matching meeting summaries.
        """
        if status and status not in VALID_MEETING_STATUSES:
            return {"error": f"Invalid status '{status}'. Must be one of: {', '.join(VALID_MEETING_STATUSES)}"}

        meetings = self.meetings
        if flight_id is not None:
            meetings = [m for m in meetings if m["flight_id"] == flight_id]
        if status:
            meetings = [m for m in meetings if m["status"] == status]
        if date:
            meetings = [m for m in meetings if m["start_time"].startswith(date)]

        summaries = [{
            "meeting_id": m["meeting_id"],
            "title": m["title"],
            "start_time": m["start_time"],
            "end_time": m["end_time"],
            "status": m["status"],
            "participant_count": len(m["participants"]),
        } for m in meetings]

        return {"meetings": summaries}

    # ── Notification management ──────────────────────────────────────────

    def send_custom_notification(
        self,
        recipient_email: str,
        recipient_name: str,
        subject: str,
        message: str,
        notification_type: str = "reminder",
    ) -> Dict[str, Any]:
        """
        Send a custom notification to a recipient.

        Args:
            recipient_email (str): Recipient's email address.
            recipient_name (str): Recipient's name.
            subject (str): Notification subject.
            message (str): Notification message body.
            notification_type (str): Type of notification (reminder, alert, update).

        Returns:
            notification_id (str): The created notification ID.
        """
        notification_id = f"ntf_{self.notification_counter}"
        self.notification_counter += 1
        notification = {
            "notification_id": notification_id,
            "recipient_email": recipient_email,
            "recipient_name": recipient_name,
            "subject": subject,
            "message": message,
            "type": notification_type,
            "status": "sent",
            "sent_at": datetime.now().isoformat(),
        }
        self.notifications.append(notification)
        return {"notification_id": notification_id, "notification": notification}

    # ── Private helper methods ─────────────────────────────────────────────

    def _find_flight(self, flight_id: int) -> Optional[Dict[str, Any]]:
        """Find a flight by ID in the flights list."""
        for flight in self.flights:
            if flight.get("flight_id") == flight_id:
                return flight
        return None

    def _find_hotel(self, hotel_id: int) -> Optional[Dict[str, Any]]:
        """Find a hotel booking by ID in the hotels list."""
        for hotel in self.hotels:
            if hotel.get("hotel_id") == hotel_id:
                return hotel
        return None

    def _find_pickup(self, pickup_id: int) -> Optional[Dict[str, Any]]:
        """Find a pickup arrangement by ID in the pickups list."""
        for pickup in self.pickups:
            if pickup.get("pickup_id") == pickup_id:
                return pickup
        return None

    def _find_meeting(self, meeting_id: int) -> Optional[Dict[str, Any]]:
        """Find a meeting by ID in the meetings list."""
        for meeting in self.meetings:
            if meeting.get("meeting_id") == meeting_id:
                return meeting
        return None

    def _add_minutes(self, time_str: str, minutes: int) -> str:
        """Add minutes to an ISO format time string and return the new ISO time string."""
        dt = datetime.fromisoformat(time_str)
        dt = dt + timedelta(minutes=minutes)
        return dt.isoformat()

    def _send_notification(
        self,
        recipient_email: str,
        recipient_name: str,
        subject: str,
        message: str,
        notification_type: str,
        **kwargs,
    ) -> str:
        """Create a notification entry, append to self.notifications, and return the notification_id."""
        notification_id = f"ntf_{self.notification_counter}"
        self.notification_counter += 1
        notification = {
            "notification_id": notification_id,
            "recipient_email": recipient_email,
            "recipient_name": recipient_name,
            "subject": subject,
            "message": message,
            "type": notification_type,
            "status": "sent",
            "sent_at": datetime.now().isoformat(),
        }
        notification.update(kwargs)
        self.notifications.append(notification)
        return notification_id

    def _log(self, event: str, detail: Dict) -> None:
        """Log environment events."""
        if not hasattr(self, '_event_log'):
            self._event_log: List[Dict[str, Any]] = []
        self._event_log.append({
            "event": event,
            "detail": detail,
            "timestamp": datetime.now().isoformat()
        })