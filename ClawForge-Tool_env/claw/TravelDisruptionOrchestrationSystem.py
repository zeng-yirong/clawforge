from copy import deepcopy
from typing import Dict, List, Optional, Any
from datetime import datetime

DEFAULT_STATE = {
    "pipelines": {},
    "workers": {},
    "flights": {},
    "hotel_bookings": {},
    "airport_pickups": {},
    "meeting_participants": {},
    "notifications": [],
    "execution_log": [],
    "pipeline_counter": 1,
    "worker_counter": 1,
    "flight_counter": 1,
    "booking_counter": 1,
    "pickup_counter": 1,
    "participant_counter": 1,
    "notification_counter": 1,
}

VALID_PIPELINE_STATUSES = ("pending", "in_progress", "awaiting_approval", "completed", "failed", "cancelled", "rolled_back")
VALID_STAGE_STATUSES = ("pending", "in_progress", "completed", "failed", "skipped", "rolled_back")
VALID_EXEC_MODES = ("sequential", "parallel")
VALID_FAILURE_POLICIES = ("abort", "skip", "retry")
VALID_WORKER_STATUSES = ("idle", "busy", "offline", "error")
VALID_FLIGHT_STATUSES = ("scheduled", "delayed", "cancelled", "departed", "arrived")
VALID_BOOKING_STATUSES = ("confirmed", "modified", "cancelled", "pending")
VALID_PICKUP_STATUSES = ("scheduled", "modified", "cancelled", "completed")
VALID_NOTIFICATION_STATUSES = ("pending", "sent", "failed", "delivered")


class TravelDisruptionOrchestrationEnv:
    """
    A unified orchestration environment for travel disruption dynamic optimization.

    This environment monitors flight delays and automatically orchestrates adjustments
    to hotel bookings, airport pickups, and sends delay notification emails to meeting
    participants. It uses a pipeline-based approach where each adjustment action is
    a stage that can be executed by registered workers (automated systems or human agents).

    The system supports:
    - Flight status monitoring and delay detection
    - Automatic hotel booking modifications based on new arrival times
    - Airport pickup rescheduling
    - Batch notification to meeting participants
    - Rollback capabilities for all adjustments
    - Sequential and parallel execution modes

    Attributes:
        pipelines (Dict[str, Dict]): All defined adjustment pipelines with their stage definitions.
        workers (Dict[str, Dict]): Registered workers (systems/agents) keyed by worker_id.
        flights (Dict[str, Dict]): Tracked flights with their status and schedule.
        hotel_bookings (Dict[str, Dict]): Hotel bookings linked to flights.
        airport_pickups (Dict[str, Dict]): Airport pickup reservations.
        meeting_participants (Dict[str, Dict]): Meeting participants to notify.
        notifications (List[Dict]): Sent notification records.
        execution_log (List[Dict]): History of every stage execution and status change.
        pipeline_counter (int): Auto-incrementing pipeline ID counter.
        worker_counter (int): Auto-incrementing worker ID counter.
        flight_counter (int): Auto-incrementing flight ID counter.
        booking_counter (int): Auto-incrementing booking ID counter.
        pickup_counter (int): Auto-incrementing pickup ID counter.
        participant_counter (int): Auto-incrementing participant ID counter.
        notification_counter (int): Auto-incrementing notification ID counter.
    """

    def __init__(self):
        self.pipelines: Dict[str, Dict[str, Any]]
        self.workers: Dict[str, Dict[str, Any]]
        self.flights: Dict[str, Dict[str, Any]]
        self.hotel_bookings: Dict[str, Dict[str, Any]]
        self.airport_pickups: Dict[str, Dict[str, Any]]
        self.meeting_participants: Dict[str, Dict[str, Any]]
        self.notifications: List[Dict[str, Any]]
        self.execution_log: List[Dict[str, Any]]
        self.pipeline_counter: int
        self.worker_counter: int
        self.flight_counter: int
        self.booking_counter: int
        self.pickup_counter: int
        self.participant_counter: int
        self.notification_counter: int
        self._api_description = (
            "This tool orchestrates travel disruption responses: monitors flight delays, "
            "automatically adjusts hotel bookings and airport pickups, and sends delay "
            "notifications to meeting participants through a unified pipeline system."
        )

    def _load_scenario(self, scenario: dict, long_context=False) -> None:
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_STATE)
        self.pipelines = scenario.get("pipelines", DEFAULT_STATE_COPY["pipelines"])
        self.workers = scenario.get("workers", DEFAULT_STATE_COPY["workers"])
        self.flights = scenario.get("flights", DEFAULT_STATE_COPY["flights"])
        self.hotel_bookings = scenario.get("hotel_bookings", DEFAULT_STATE_COPY["hotel_bookings"])
        self.airport_pickups = scenario.get("airport_pickups", DEFAULT_STATE_COPY["airport_pickups"])
        self.meeting_participants = scenario.get("meeting_participants", DEFAULT_STATE_COPY["meeting_participants"])
        self.notifications = scenario.get("notifications", DEFAULT_STATE_COPY["notifications"])
        self.execution_log = scenario.get("execution_log", DEFAULT_STATE_COPY["execution_log"])
        self.pipeline_counter = scenario.get("pipeline_counter", DEFAULT_STATE_COPY["pipeline_counter"])
        self.worker_counter = scenario.get("worker_counter", DEFAULT_STATE_COPY["worker_counter"])
        self.flight_counter = scenario.get("flight_counter", DEFAULT_STATE_COPY["flight_counter"])
        self.booking_counter = scenario.get("booking_counter", DEFAULT_STATE_COPY["booking_counter"])
        self.pickup_counter = scenario.get("pickup_counter", DEFAULT_STATE_COPY["pickup_counter"])
        self.participant_counter = scenario.get("participant_counter", DEFAULT_STATE_COPY["participant_counter"])
        self.notification_counter = scenario.get("notification_counter", DEFAULT_STATE_COPY["notification_counter"])

    def get_env_state(self) -> dict:
        """
        Return the current internal state of the environment.

        Returns:
            dict: All environment state variables including pipelines, workers,
                  flights, hotel bookings, airport pickups, meeting participants,
                  notifications, execution log, and all counters.
        """
        return {
            "pipelines": self.pipelines,
            "workers": self.workers,
            "flights": self.flights,
            "hotel_bookings": self.hotel_bookings,
            "airport_pickups": self.airport_pickups,
            "meeting_participants": self.meeting_participants,
            "notifications": self.notifications,
            "execution_log": self.execution_log,
            "pipeline_counter": self.pipeline_counter,
            "worker_counter": self.worker_counter,
            "flight_counter": self.flight_counter,
            "booking_counter": self.booking_counter,
            "pickup_counter": self.pickup_counter,
            "participant_counter": self.participant_counter,
            "notification_counter": self.notification_counter,
        }

    # ── Worker management ─────────────────────────────────────────────────

    def register_worker(
        self,
        name: str,
        role: str,
        capabilities: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Register a new worker that can execute pipeline stages.

        Workers can be automated systems (hotel API, pickup service, email system)
        or human agents for manual interventions.

        Args:
            name (str): Display name for the worker.
            role (str): Functional role (e.g. 'hotel_modifier', 'pickup_scheduler', 'notifier').
            capabilities (List[str]): [Optional] List of action types this worker can perform.

        Returns:
            dict: Contains worker_id (str) and worker (Dict) record, or error dict.
        """
        if not name.strip() or not role.strip():
            return {"error": "Worker name and role must both be non-empty."}

        worker_id = str(self.worker_counter)
        self.worker_counter += 1

        worker = {
            "worker_id": worker_id,
            "name": name,
            "role": role,
            "capabilities": capabilities or [],
            "status": "idle",
            "task_count": 0,
            "completed_count": 0,
        }
        self.workers[worker_id] = worker
        self._log("worker_registered", {"worker_id": worker_id, "role": role})
        return {"worker_id": worker_id, "worker": worker}

    def unregister_worker(self, worker_id: str) -> Dict[str, str]:
        """
        Remove a worker from the orchestration system.

        Args:
            worker_id (str): Worker ID to remove.

        Returns:
            dict: Status confirmation or error dict.
        """
        if worker_id not in self.workers:
            return {"error": f"Worker '{worker_id}' not found."}
        if self.workers[worker_id]["status"] == "busy":
            return {"error": f"Worker '{worker_id}' is currently busy. Wait for task completion first."}
        del self.workers[worker_id]
        return {"status": f"Worker '{worker_id}' unregistered."}

    def list_workers(
        self, role: Optional[str] = None, status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List registered workers, optionally filtered by role or status.

        Args:
            role (str): [Optional] Filter by role.
            status (str): [Optional] Filter by status.

        Returns:
            dict: Contains workers (List[Dict]) matching the criteria, or error dict.
        """
        if status and status not in VALID_WORKER_STATUSES:
            return {"error": f"Invalid status '{status}'. Must be one of: {', '.join(VALID_WORKER_STATUSES)}"}
        workers = list(self.workers.values())
        if role:
            workers = [w for w in workers if w["role"] == role]
        if status:
            workers = [w for w in workers if w["status"] == status]
        return {"workers": workers}

    # ── Flight management ─────────────────────────────────────────────────

    def register_flight(
        self,
        flight_number: str,
        departure_time: str,
        arrival_time: str,
        origin: str,
        destination: str,
        traveler_name: str,
    ) -> Dict[str, Any]:
        """
        Register a flight to be monitored for delays.

        Args:
            flight_number (str): Airline flight number (e.g. 'AA1234').
            departure_time (str): Scheduled departure time (ISO format).
            arrival_time (str): Scheduled arrival time (ISO format).
            origin (str): Departure airport code.
            destination (str): Arrival airport code.
            traveler_name (str): Name of the traveler.

        Returns:
            dict: Contains flight_id (str) and flight (Dict) record, or error dict.
        """
        if not flight_number.strip():
            return {"error": "Flight number cannot be empty."}
        if not traveler_name.strip():
            return {"error": "Traveler name cannot be empty."}

        flight_id = str(self.flight_counter)
        self.flight_counter += 1

        flight = {
            "flight_id": flight_id,
            "flight_number": flight_number,
            "departure_time": departure_time,
            "arrival_time": arrival_time,
            "origin": origin,
            "destination": destination,
            "traveler_name": traveler_name,
            "status": "scheduled",
            "delay_minutes": 0,
            "new_arrival_time": None,
            "linked_bookings": [],
            "linked_pickups": [],
            "linked_participants": [],
        }
        self.flights[flight_id] = flight
        self._log("flight_registered", {"flight_id": flight_id, "flight_number": flight_number})
        return {"flight_id": flight_id, "flight": flight}

    def update_flight_status(
        self,
        flight_id: str,
        status: str,
        delay_minutes: Optional[int] = None,
        new_arrival_time: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Update the status of a monitored flight.

        When a delay is detected, this triggers the need for downstream adjustments.

        Args:
            flight_id (str): Flight ID to update.
            status (str): New status ('scheduled', 'delayed', 'cancelled', 'departed', 'arrived').
            delay_minutes (int): [Optional] Delay duration in minutes.
            new_arrival_time (str): [Optional] New expected arrival time.

        Returns:
            dict: Contains flight_id and updated flight record, or error dict.
        """
        if flight_id not in self.flights:
            return {"error": f"Flight '{flight_id}' not found."}
        if status not in VALID_FLIGHT_STATUSES:
            return {"error": f"Invalid status '{status}'. Must be one of: {', '.join(VALID_FLIGHT_STATUSES)}"}

        flight = self.flights[flight_id]
        flight["status"] = status
        if delay_minutes is not None:
            flight["delay_minutes"] = delay_minutes
        if new_arrival_time is not None:
            flight["new_arrival_time"] = new_arrival_time

        self._log("flight_status_updated", {
            "flight_id": flight_id,
            "status": status,
            "delay_minutes": delay_minutes,
        })
        return {"flight_id": flight_id, "flight": flight}

    def get_flight(self, flight_id: str) -> Dict[str, Any]:
        """
        Retrieve the full state of a flight.

        Args:
            flight_id (str): Flight ID.

        Returns:
            dict: Contains flight (Dict) record, or error dict.
        """
        if flight_id not in self.flights:
            return {"error": f"Flight '{flight_id}' not found."}
        return {"flight": self.flights[flight_id]}

    def list_flights(self, status: Optional[str] = None) -> Dict[str, Any]:
        """
        List all monitored flights, optionally filtered by status.

        Args:
            status (str): [Optional] Filter by flight status.

        Returns:
            dict: Contains flights (List[Dict]) matching the criteria, or error dict.
        """
        if status and status not in VALID_FLIGHT_STATUSES:
            return {"error": f"Invalid status '{status}'. Must be one of: {', '.join(VALID_FLIGHT_STATUSES)}"}
        flights = list(self.flights.values())
        if status:
            flights = [f for f in flights if f["status"] == status]
        return {"flights": flights}

    # ── Hotel booking management ──────────────────────────────────────────

    def create_hotel_booking(
        self,
        flight_id: str,
        hotel_name: str,
        check_in_date: str,
        check_out_date: str,
        confirmation_number: str,
    ) -> Dict[str, Any]:
        """
        Create a hotel booking linked to a flight.

        Args:
            flight_id (str): Associated flight ID.
            hotel_name (str): Name of the hotel.
            check_in_date (str): Check-in date (ISO format).
            check_out_date (str): Check-out date (ISO format).
            confirmation_number (str): Hotel confirmation number.

        Returns:
            dict: Contains booking_id (str) and booking (Dict) record, or error dict.
        """
        if flight_id not in self.flights:
            return {"error": f"Flight '{flight_id}' not found."}
        if not hotel_name.strip():
            return {"error": "Hotel name cannot be empty."}

        booking_id = str(self.booking_counter)
        self.booking_counter += 1

        booking = {
            "booking_id": booking_id,
            "flight_id": flight_id,
            "hotel_name": hotel_name,
            "check_in_date": check_in_date,
            "check_out_date": check_out_date,
            "original_check_in_date": check_in_date,
            "confirmation_number": confirmation_number,
            "status": "confirmed",
            "modification_history": [],
        }
        self.hotel_bookings[booking_id] = booking
        self.flights[flight_id]["linked_bookings"].append(booking_id)
        self._log("hotel_booking_created", {"booking_id": booking_id, "flight_id": flight_id})
        return {"booking_id": booking_id, "booking": booking}

    def modify_hotel_booking(
        self,
        booking_id: str,
        new_check_in_date: Optional[str] = None,
        new_check_out_date: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Modify a hotel booking due to flight delay.

        Args:
            booking_id (str): Booking ID to modify.
            new_check_in_date (str): [Optional] New check-in date.
            new_check_out_date (str): [Optional] New check-out date.
            reason (str): [Optional] Reason for modification.

        Returns:
            dict: Contains booking_id and updated booking record, or error dict.
        """
        if booking_id not in self.hotel_bookings:
            return {"error": f"Booking '{booking_id}' not found."}

        booking = self.hotel_bookings[booking_id]
        if booking["status"] == "cancelled":
            return {"error": f"Booking '{booking_id}' is cancelled and cannot be modified."}

        modification = {
            "timestamp": f"t+{self.pipeline_counter}",
            "previous_check_in": booking["check_in_date"],
            "previous_check_out": booking["check_out_date"],
            "reason": reason or "flight_delay",
        }

        if new_check_in_date:
            booking["check_in_date"] = new_check_in_date
        if new_check_out_date:
            booking["check_out_date"] = new_check_out_date

        modification["new_check_in"] = booking["check_in_date"]
        modification["new_check_out"] = booking["check_out_date"]
        booking["modification_history"].append(modification)
        booking["status"] = "modified"

        self._log("hotel_booking_modified", {"booking_id": booking_id, "modification": modification})
        return {"booking_id": booking_id, "booking": booking}

    def get_hotel_booking(self, booking_id: str) -> Dict[str, Any]:
        """
        Retrieve a hotel booking record.

        Args:
            booking_id (str): Booking ID.

        Returns:
            dict: Contains booking (Dict) record, or error dict.
        """
        if booking_id not in self.hotel_bookings:
            return {"error": f"Booking '{booking_id}' not found."}
        return {"booking": self.hotel_bookings[booking_id]}

    def list_hotel_bookings(
        self, flight_id: Optional[str] = None, status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List hotel bookings, optionally filtered by flight or status.

        Args:
            flight_id (str): [Optional] Filter by associated flight.
            status (str): [Optional] Filter by booking status.

        Returns:
            dict: Contains bookings (List[Dict]) matching the criteria, or error dict.
        """
        if status and status not in VALID_BOOKING_STATUSES:
            return {"error": f"Invalid status '{status}'. Must be one of: {', '.join(VALID_BOOKING_STATUSES)}"}
        bookings = list(self.hotel_bookings.values())
        if flight_id:
            bookings = [b for b in bookings if b["flight_id"] == flight_id]
        if status:
            bookings = [b for b in bookings if b["status"] == status]
        return {"bookings": bookings}

    # ── Airport pickup management ─────────────────────────────────────────

    def create_airport_pickup(
        self,
        flight_id: str,
        pickup_time: str,
        pickup_location: str,
        driver_name: Optional[str] = None,
        vehicle_info: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create an airport pickup reservation linked to a flight.

        Args:
            flight_id (str): Associated flight ID.
            pickup_time (str): Scheduled pickup time (ISO format).
            pickup_location (str): Pickup location at the airport.
            driver_name (str): [Optional] Driver name.
            vehicle_info (str): [Optional] Vehicle description.

        Returns:
            dict: Contains pickup_id (str) and pickup (Dict) record, or error dict.
        """
        if flight_id not in self.flights:
            return {"error": f"Flight '{flight_id}' not found."}
        if not pickup_location.strip():
            return {"error": "Pickup location cannot be empty."}

        pickup_id = str(self.pickup_counter)
        self.pickup_counter += 1

        pickup = {
            "pickup_id": pickup_id,
            "flight_id": flight_id,
            "pickup_time": pickup_time,
            "original_pickup_time": pickup_time,
            "pickup_location": pickup_location,
            "driver_name": driver_name,
            "vehicle_info": vehicle_info,
            "status": "scheduled",
            "modification_history": [],
        }
        self.airport_pickups[pickup_id] = pickup
        self.flights[flight_id]["linked_pickups"].append(pickup_id)
        self._log("airport_pickup_created", {"pickup_id": pickup_id, "flight_id": flight_id})
        return {"pickup_id": pickup_id, "pickup": pickup}

    def modify_airport_pickup(
        self,
        pickup_id: str,
        new_pickup_time: Optional[str] = None,
        new_pickup_location: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Modify an airport pickup due to flight delay.

        Args:
            pickup_id (str): Pickup ID to modify.
            new_pickup_time (str): [Optional] New pickup time.
            new_pickup_location (str): [Optional] New pickup location.
            reason (str): [Optional] Reason for modification.

        Returns:
            dict: Contains pickup_id and updated pickup record, or error dict.
        """
        if pickup_id not in self.airport_pickups:
            return {"error": f"Pickup '{pickup_id}' not found."}

        pickup = self.airport_pickups[pickup_id]
        if pickup["status"] == "cancelled":
            return {"error": f"Pickup '{pickup_id}' is cancelled and cannot be modified."}

        modification = {
            "timestamp": f"t+{self.pipeline_counter}",
            "previous_pickup_time": pickup["pickup_time"],
            "previous_location": pickup["pickup_location"],
            "reason": reason or "flight_delay",
        }

        if new_pickup_time:
            pickup["pickup_time"] = new_pickup_time
        if new_pickup_location:
            pickup["pickup_location"] = new_pickup_location

        modification["new_pickup_time"] = pickup["pickup_time"]
        modification["new_location"] = pickup["pickup_location"]
        pickup["modification_history"].append(modification)
        pickup["status"] = "modified"

        self._log("airport_pickup_modified", {"pickup_id": pickup_id, "modification": modification})
        return {"pickup_id": pickup_id, "pickup": pickup}

    def get_airport_pickup(self, pickup_id: str) -> Dict[str, Any]:
        """
        Retrieve an airport pickup record.

        Args:
            pickup_id (str): Pickup ID.

        Returns:
            dict: Contains pickup (Dict) record, or error dict.
        """
        if pickup_id not in self.airport_pickups:
            return {"error": f"Pickup '{pickup_id}' not found."}
        return {"pickup": self.airport_pickups[pickup_id]}

    def list_airport_pickups(
        self, flight_id: Optional[str] = None, status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List airport pickups, optionally filtered by flight or status.

        Args:
            flight_id (str): [Optional] Filter by associated flight.
            status (str): [Optional] Filter by pickup status.

        Returns:
            dict: Contains pickups (List[Dict]) matching the criteria, or error dict.
        """
        if status and status not in VALID_PICKUP_STATUSES:
            return {"error": f"Invalid status '{status}'. Must be one of: {', '.join(VALID_PICKUP_STATUSES)}"}
        pickups = list(self.airport_pickups.values())
        if flight_id:
            pickups = [p for p in pickups if p["flight_id"] == flight_id]
        if status:
            pickups = [p for p in pickups if p["status"] == status]
        return {"pickups": pickups}

    # ── Meeting participant management ────────────────────────────────────

    def register_meeting_participant(
        self,
        flight_id: str,
        name: str,
        email: str,
        meeting_title: str,
        meeting_time: str,
    ) -> Dict[str, Any]:
        """
        Register a meeting participant who should be notified of flight delays.

        Args:
            flight_id (str): Associated flight ID of the traveler.
            name (str): Participant name.
            email (str): Participant email address.
            meeting_title (str): Title of the meeting.
            meeting_time (str): Scheduled meeting time (ISO format).

        Returns:
            dict: Contains participant_id (str) and participant (Dict) record, or error dict.
        """
        if flight_id not in self.flights:
            return {"error": f"Flight '{flight_id}' not found."}
        if not name.strip() or not email.strip():
            return {"error": "Participant name and email cannot be empty."}

        participant_id = str(self.participant_counter)
        self.participant_counter += 1

        participant = {
            "participant_id": participant_id,
            "flight_id": flight_id,
            "name": name,
            "email": email,
            "meeting_title": meeting_title,
            "meeting_time": meeting_time,
            "notified": False,
            "notification_history": [],
        }
        self.meeting_participants[participant_id] = participant
        self.flights[flight_id]["linked_participants"].append(participant_id)
        self._log("participant_registered", {"participant_id": participant_id, "flight_id": flight_id})
        return {"participant_id": participant_id, "participant": participant}

    def list_meeting_participants(
        self, flight_id: Optional[str] = None, notified: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        List meeting participants, optionally filtered by flight or notification status.

        Args:
            flight_id (str): [Optional] Filter by associated flight.
            notified (bool): [Optional] Filter by notification status.

        Returns:
            dict: Contains participants (List[Dict]) matching the criteria.
        """
        participants = list(self.meeting_participants.values())
        if flight_id:
            participants = [p for p in participants if p["flight_id"] == flight_id]
        if notified is not None:
            participants = [p for p in participants if p["notified"] == notified]
        return {"participants": participants}

    # ── Notification management ───────────────────────────────────────────

    def send_delay_notification(
        self,
        participant_id: str,
        delay_minutes: int,
        new_arrival_time: str,
        custom_message: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send a delay notification email to a meeting participant.

        Args:
            participant_id (str): Participant ID to notify.
            delay_minutes (int): Delay duration in minutes.
            new_arrival_time (str): New expected arrival time.
            custom_message (str): [Optional] Custom message to include.

        Returns:
            dict: Contains notification_id (str) and notification (Dict) record, or error dict.
        """
        if participant_id not in self.meeting_participants:
            return {"error": f"Participant '{participant_id}' not found."}

        participant = self.meeting_participants[participant_id]
        flight = self.flights.get(participant["flight_id"])

        notification_id = str(self.notification_counter)
        self.notification_counter += 1

        notification = {
            "notification_id": notification_id,
            "participant_id": participant_id,
            "participant_name": participant["name"],
            "participant_email": participant["email"],
            "flight_id": participant["flight_id"],
            "flight_number": flight["flight_number"] if flight else "Unknown",
            "traveler_name": flight["traveler_name"] if flight else "Unknown",
            "delay_minutes": delay_minutes,
            "new_arrival_time": new_arrival_time,
            "meeting_title": participant["meeting_title"],
            "meeting_time": participant["meeting_time"],
            "custom_message": custom_message,
            "status": "sent",
            "sent_at": f"t+{self.pipeline_counter}",
        }

        self.notifications.append(notification)
        participant["notified"] = True
        participant["notification_history"].append({
            "notification_id": notification_id,
            "sent_at": notification["sent_at"],
        })

        self._log("notification_sent", {
            "notification_id": notification_id,
            "participant_id": participant_id,
            "email": participant["email"],
        })
        return {"notification_id": notification_id, "notification": notification}

    def list_notifications(
        self, flight_id: Optional[str] = None, status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List sent notifications, optionally filtered by flight or status.

        Args:
            flight_id (str): [Optional] Filter by associated flight.
            status (str): [Optional] Filter by notification status.

        Returns:
            dict: Contains notifications (List[Dict]) matching the criteria, or error dict.
        """
        if status and status not in VALID_NOTIFICATION_STATUSES:
            return {"error": f"Invalid status '{status}'. Must be one of: {', '.join(VALID_NOTIFICATION_STATUSES)}"}
        notifications = self.notifications
        if flight_id:
            notifications = [n for n in notifications if n["flight_id"] == flight_id]
        if status:
            notifications = [n for n in notifications if n["status"] == status]
        return {"notifications": notifications}

    # ── Pipeline definition ───────────────────────────────────────────────

    def define_pipeline(
        self,
        name: str,
        stages: List[Dict[str, Any]],
        mode: str = "sequential",
        flight_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Define a new disruption response pipeline with an ordered list of stages.

        A typical pipeline for flight delay response includes stages for:
        - Detecting/confirming the delay
        - Modifying hotel bookings
        - Rescheduling airport pickups
        - Sending notifications to meeting participants

        Args:
            name (str): Pipeline name.
            stages (List[Dict]): Ordered list of stage definitions. Each stage requires:
                - stage_id (str): Unique stage identifier within this pipeline.
                - name (str): Human-readable stage name.
                - action (str): Action type ('modify_hotel', 'modify_pickup', 'send_notification').

        Returns:
            pipeline_id (str): The created pipeline ID.
        """
        pipeline_id = f"pl_{self.pipeline_counter}"
        self.pipeline_counter += 1
        pipeline = {
            "pipeline_id": pipeline_id,
            "name": name,
            "stages": stages,
            "mode": mode,
            "flight_id": flight_id,
            "status": "pending",
            "created_at": f"t{self.pipeline_counter}",
        }
        self.pipelines[pipeline_id] = pipeline
        return {"pipeline_id": pipeline_id, "pipeline": pipeline}

    def _log(self, event: str, detail: Dict) -> None:
        """Log environment events."""
        if not hasattr(self, '_event_log'):
            self._event_log: List[Dict[str, Any]] = []
        self._event_log.append({
            "event": event,
            "detail": detail,
            "timestamp": datetime.now().isoformat()
        })