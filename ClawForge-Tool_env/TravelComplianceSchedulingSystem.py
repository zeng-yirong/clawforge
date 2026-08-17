from copy import deepcopy
from typing import Dict, List, Optional, Any
from datetime import datetime

DEFAULT_STATE = {
    "policies": [],
    "flight_results": [],
    "approval_requests": [],
    "bookings": [],
    "audit_log": [],
    "policy_counter": 1,
    "search_counter": 1,
    "approval_counter": 1,
    "booking_counter": 1,
}

VALID_CABIN_CLASSES = ("economy", "premium_economy", "business", "first")
VALID_APPROVAL_STATUSES = ("pending", "approved", "rejected", "cancelled")
VALID_BOOKING_STATUSES = ("confirmed", "cancelled", "pending_payment", "failed")
VALID_COMPLIANCE_LEVELS = ("compliant", "warning", "violation")
PLATFORMS = ("ctrip", "fliggy", "qunar", "direct")


class TravelComplianceSchedulingEnv:
    """
    A travel compliance and booking lifecycle management environment.

    This class models a corporate travel booking system where agents load company
    travel policies (parsed from PDF documents), search and compare flight prices
    across multiple platforms, validate compliance against policy rules, submit
    approval workflows, and complete bookings — forming a closed-loop process.

    Attributes:
        policies (List[Dict]): Loaded company travel policy documents.
        flight_results (List[Dict]): Flight search results from multiple platforms.
        approval_requests (List[Dict]): Approval workflow records.
        bookings (List[Dict]): Confirmed or pending booking records.
        audit_log (List[Dict]): Full audit trail of all operations.
        policy_counter (int): Auto-incrementing policy ID counter.
        search_counter (int): Auto-incrementing search session ID counter.
        approval_counter (int): Auto-incrementing approval request ID counter.
        booking_counter (int): Auto-incrementing booking ID counter.
    """

    def __init__(self):
        self.policies: List[Dict[str, Any]]
        self.flight_results: List[Dict[str, Any]]
        self.approval_requests: List[Dict[str, Any]]
        self.bookings: List[Dict[str, Any]]
        self.audit_log: List[Dict[str, Any]]
        self.policy_counter: int
        self.search_counter: int
        self.approval_counter: int
        self.booking_counter: int
        self._api_description = (
            "This tool manages corporate travel compliance and booking lifecycle: "
            "load company PDF travel policies, compare flight prices across platforms, "
            "validate compliance, submit approval workflows, and complete bookings end-to-end."
        )

    def _load_scenario(self, scenario: dict, long_context: bool = False) -> None:
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_STATE)
        self.policies = scenario.get("policies", DEFAULT_STATE_COPY["policies"])
        self.flight_results = scenario.get("flight_results", DEFAULT_STATE_COPY["flight_results"])
        self.approval_requests = scenario.get("approval_requests", DEFAULT_STATE_COPY["approval_requests"])
        self.bookings = scenario.get("bookings", DEFAULT_STATE_COPY["bookings"])
        self.audit_log = scenario.get("audit_log", DEFAULT_STATE_COPY["audit_log"])
        self.policy_counter = scenario.get("policy_counter", DEFAULT_STATE_COPY["policy_counter"])
        self.search_counter = scenario.get("search_counter", DEFAULT_STATE_COPY["search_counter"])
        self.approval_counter = scenario.get("approval_counter", DEFAULT_STATE_COPY["approval_counter"])
        self.booking_counter = scenario.get("booking_counter", DEFAULT_STATE_COPY["booking_counter"])

    def get_env_state(self) -> dict:
        """
        Return the current internal state of the environment.

        Returns:
            policies (List[Dict]): All loaded travel policy documents.
            flight_results (List[Dict]): All flight search result sessions.
            approval_requests (List[Dict]): All approval workflow records.
            bookings (List[Dict]): All booking records.
            audit_log (List[Dict]): Full audit trail of operations.
            policy_counter (int): Next policy ID to be assigned.
            search_counter (int): Next search session ID to be assigned.
            approval_counter (int): Next approval request ID to be assigned.
            booking_counter (int): Next booking ID to be assigned.
        """
        return {
            "policies": self.policies,
            "flight_results": self.flight_results,
            "approval_requests": self.approval_requests,
            "bookings": self.bookings,
            "audit_log": self.audit_log,
            "policy_counter": self.policy_counter,
            "search_counter": self.search_counter,
            "approval_counter": self.approval_counter,
            "booking_counter": self.booking_counter,
        }

    # ── Policy management ────────────────────────────────────────────────

    def load_policy(
        self,
        document_name: str,
        max_economy_fare: float,
        max_business_fare: float,
        allowed_cabin_classes: List[str],
        advance_booking_days: int = 3,
        max_trip_duration_days: int = 30,
        requires_approval_above: float = 0.0,
        approver_roles: Optional[List[str]] = None,
        notes: str = "",
    ) -> Dict[str, Any]:
        """
        Load and register a company travel policy (simulating PDF document parsing).

        Args:
            document_name (str): Source document name, e.g. '2024_travel_policy.pdf'.
            max_economy_fare (float): Maximum allowed fare (CNY) for economy class tickets.
            max_business_fare (float): Maximum allowed fare (CNY) for business class tickets.
            allowed_cabin_classes (List[str]): Permitted cabin classes, subset of
                ['economy', 'premium_economy', 'business', 'first'].
            advance_booking_days (int): Minimum days in advance required for booking.
                Defaults to 3.
            max_trip_duration_days (int): Maximum allowed trip duration in days.
                Defaults to 30.
            requires_approval_above (float): Fare threshold (CNY) above which manager
                approval is mandatory. 0.0 means approval always required. Defaults to 0.0.
            approver_roles (List[str]): [Optional] Roles authorized to approve requests,
                e.g. ['line_manager', 'finance_director'].
            notes (str): Additional policy notes or special conditions.

        Returns:
            policy_id (int): Unique policy identifier.
            policy (Dict): The registered policy record.
        """
        if not document_name.strip():
            return {"error": "document_name is required."}
        if any(v is None or v <= 0 for v in (max_economy_fare, max_business_fare)):
            return {"error": "max_economy_fare and max_business_fare must be positive values."}
        if max_business_fare < max_economy_fare:
            return {"error": "max_business_fare must be greater than or equal to max_economy_fare."}
        if advance_booking_days is None or advance_booking_days < 0:
            return {"error": "advance_booking_days must be non-negative."}
        if max_trip_duration_days is None or max_trip_duration_days <= 0:
            return {"error": "max_trip_duration_days must be a positive integer."}

        invalid_cabins = [c for c in allowed_cabin_classes if c not in VALID_CABIN_CLASSES]
        if invalid_cabins:
            return {"error": f"Invalid cabin class(es): {invalid_cabins}. Must be one of: {list(VALID_CABIN_CLASSES)}"}
        if not allowed_cabin_classes:
            return {"error": "allowed_cabin_classes must contain at least one cabin class."}

        policy_id = self.policy_counter
        self.policy_counter += 1

        policy = {
            "policy_id": policy_id,
            "document_name": document_name,
            "max_economy_fare": max_economy_fare,
            "max_business_fare": max_business_fare,
            "allowed_cabin_classes": allowed_cabin_classes,
            "advance_booking_days": advance_booking_days,
            "max_trip_duration_days": max_trip_duration_days,
            "requires_approval_above": requires_approval_above,
            "approver_roles": approver_roles or ["line_manager"],
            "notes": notes,
        }
        self.policies.append(policy)
        self._log("policy_loaded", {"policy_id": policy_id, "document_name": document_name})
        return {"policy_id": policy_id, "policy": policy}

    def list_policies(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        List all loaded travel policies.

        Returns:
            policies (List[Dict]): Summary of all registered policy documents.
        """
        summaries = [
            {
                "policy_id": p["policy_id"],
                "document_name": p["document_name"],
                "max_economy_fare": p["max_economy_fare"],
                "max_business_fare": p["max_business_fare"],
                "allowed_cabin_classes": p["allowed_cabin_classes"],
                "requires_approval_above": p["requires_approval_above"],
            }
            for p in self.policies
        ]
        return {"policies": summaries}

    # ── Flight search & comparison ───────────────────────────────────────

    def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        cabin_class: str = "economy",
        traveler_name: str = "",
        platforms: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Search and compare flight prices across multiple booking platforms.

        Args:
            origin (str): Departure city or airport code, e.g. 'PEK' or 'Beijing'.
            destination (str): Arrival city or airport code, e.g. 'SHA' or 'Shanghai'.
            departure_date (str): Departure date in 'YYYY-MM-DD' format.
            cabin_class (str): Desired cabin class. One of 'economy', 'premium_economy',
                'business', 'first'. Defaults to 'economy'.
            traveler_name (str): Name of the traveler for this search session.
            platforms (List[str]): [Optional] Platforms to query. Subset of
                ['ctrip', 'fliggy', 'qunar', 'direct']. Defaults to all platforms.

        Returns:
            search_id (int): Unique search session identifier.
            origin (str): Departure location.
            destination (str): Arrival location.
            departure_date (str): Queried departure date.
            cabin_class (str): Queried cabin class.
            results (List[Dict]): Flight options with platform, price, flight_no,
                departure_time, arrival_time, and duration_minutes.
        """
        if not origin.strip() or not destination.strip():
            return {"error": "origin and destination are required."}
        if origin.strip().lower() == destination.strip().lower():
            return {"error": "origin and destination must be different."}
        if cabin_class not in VALID_CABIN_CLASSES:
            return {"error": f"Invalid cabin_class '{cabin_class}'. Must be one of: {list(VALID_CABIN_CLASSES)}"}
        if not departure_date or len(departure_date) != 10 or departure_date[4] != "-" or departure_date[7] != "-":
            return {"error": "Invalid departure_date format. Expected 'YYYY-MM-DD'."}

        target_platforms = platforms or list(PLATFORMS)
        invalid_platforms = [p for p in target_platforms if p not in PLATFORMS]
        if invalid_platforms:
            return {"error": f"Invalid platform(s): {invalid_platforms}. Must be one of: {list(PLATFORMS)}"}

        search_id = self.search_counter
        self.search_counter += 1

        # Simulate platform-specific flight results with deterministic pricing
        base_prices = {"economy": 800, "premium_economy": 1400, "business": 3200, "first": 6500}
        base = base_prices[cabin_class]
        platform_multipliers = {"ctrip": 1.00, "fliggy": 0.97, "qunar": 0.95, "direct": 1.03}
        platform_flight_nos = {"ctrip": "CA1234", "fliggy": "MU5678", "qunar": "CZ9012", "direct": "CA1234"}
        platform_dep_times = {"ctrip": "08:00", "fliggy": "10:30", "qunar": "14:00", "direct": "08:00"}
        platform_arr_times = {"ctrip": "10:30", "fliggy": "13:00", "qunar": "16:30", "direct": "10:30"}
        platform_durations = {"ctrip": 150, "fliggy": 150, "qunar": 150, "direct": 150}

        results = []
        for platform in target_platforms:
            price = round(base * platform_multipliers[platform], 2)
            results.append({
                "platform": platform,
                "flight_no": platform_flight_nos[platform],
                "price": price,
                "currency": "CNY",
                "cabin_class": cabin_class,
                "departure_time": f"{departure_date}T{platform_dep_times[platform]}",
                "arrival_time": f"{departure_date}T{platform_arr_times[platform]}",
                "duration_minutes": platform_durations[platform],
                "seats_available": 9,
            })

        results_sorted = sorted(results, key=lambda r: r["price"])

        search_record = {
            "search_id": search_id,
            "origin": origin,
            "destination": destination,
            "departure_date": departure_date,
            "cabin_class": cabin_class,
            "traveler_name": traveler_name,
            "results": results_sorted,
        }
        self.flight_results.append(search_record)
        self._log("flights_searched", {"search_id": search_id, "route": f"{origin}->{destination}", "date": departure_date})

        return {
            "search_id": search_id,
            "origin": origin,
            "destination": destination,
            "departure_date": departure_date,
            "cabin_class": cabin_class,
            "results": results_sorted,
        }

    def get_search_results(self, search_id: int) -> Dict[str, Any]:
        """
        Retrieve a previous flight search session by ID.

        Args:
            search_id (int): The search session ID returned by search_flights.

        Returns:
            search_id (int): The search session ID.
            origin (str): Departure location.
            destination (str): Arrival location.
            departure_date (str): Queried departure date.
            cabin_class (str): Queried cabin class.
            traveler_name (str): Traveler name associated with the search.
            results (List[Dict]): All flight options found.
        """
        record = self._find_search(search_id)
        if not record:
            return {"error": f"Search ID {search_id} not found."}
        return record

    # ── Compliance check ─────────────────────────────────────────────────

    def check_compliance(
        self,
        policy_id: int,
        search_id: int,
        selected_platform: str,
        booking_date: str,
    ) -> Dict[str, Any]:
        """
        Validate a selected flight option against the company travel policy.

        Checks fare limits, cabin class restrictions, and advance booking requirements.
        Returns a compliance level and detailed violation or warning messages.

        Args:
            policy_id (int): The policy to validate against.
            search_id (int): The flight search session containing the selected option.
            selected_platform (str): The platform whose offer to validate
                (e.g. 'ctrip', 'fliggy', 'qunar', 'direct').
            booking_date (str): The date the booking is being made ('YYYY-MM-DD'),
                used to compute advance booking days.

        Returns:
            policy_id (int): The policy used for validation.
            search_id (int): The search session validated.
            selected_platform (str): The platform validated.
            compliance_level (str): One of 'compliant', 'warning', 'violation'.
            fare (float): The fare of the selected option in CNY.
            cabin_class (str): The cabin class of the selected option.
            issues (List[str]): List of compliance issues found (empty if compliant).
            requires_approval (bool): Whether this booking requires manager approval.
            cheapest_compliant_platform (str): Platform offering the lowest compliant fare.
            cheapest_compliant_fare (float): The lowest compliant fare available.
        """
        policy = self._find_policy(policy_id)
        if not policy:
            return {"error": f"Policy ID {policy_id} not found."}

        search = self._find_search(search_id)
        if not search:
            return {"error": f"Search ID {search_id} not found."}

        if selected_platform not in PLATFORMS:
            return {"error": f"Invalid platform '{selected_platform}'. Must be one of: {list(PLATFORMS)}"}

        if not booking_date or len(booking_date) != 10:
            return {"error": "Invalid booking_date format. Expected 'YYYY-MM-DD'."}

        selected_result = next((r for r in search["results"] if r["platform"] == selected_platform), None)
        if not selected_result:
            return {"error": f"No result found for platform '{selected_platform}' in search {search_id}."}

        fare = selected_result["price"]
        cabin_class = selected_result["cabin_class"]
        issues = []
        compliance_level = "compliant"

        # Check cabin class restriction
        if cabin_class not in policy["allowed_cabin_classes"]:
            issues.append(
                f"Cabin class '{cabin_class}' is not permitted by policy. "
                f"Allowed: {policy['allowed_cabin_classes']}."
            )
            compliance_level = "violation"

        # Check fare limit
        fare_limit = policy["max_business_fare"] if cabin_class in ("business", "first") else policy["max_economy_fare"]
        if fare > fare_limit:
            issues.append(
                f"Fare CNY {fare} exceeds policy limit of CNY {fare_limit} for {cabin_class} class."
            )
            compliance_level = "violation"
        elif fare > fare_limit * 0.9 and compliance_level != "violation":
            issues.append(
                f"Fare CNY {fare} is within 10% of the policy limit (CNY {fare_limit}). Consider a cheaper option."
            )
            compliance_level = "warning"

        # Check advance booking requirement
        advance_days = self._date_diff_days(booking_date, search["departure_date"])
        if advance_days < policy["advance_booking_days"]:
            issues.append(
                f"Booking is only {advance_days} day(s) in advance; policy requires at least "
                f"{policy['advance_booking_days']} day(s)."
            )
            if compliance_level == "compliant":
                compliance_level = "warning"

        # Determine if approval is required
        requires_approval = fare > policy["requires_approval_above"] or compliance_level in ("warning", "violation")

        # Find cheapest compliant option
        cheapest_platform = None
        cheapest_fare = float("inf")
        for r in search["results"]:
            r_cabin = r["cabin_class"]
            r_fare = r["price"]
            r_limit = policy["max_business_fare"] if r_cabin in ("business", "first") else policy["max_economy_fare"]
            if r_cabin in policy["allowed_cabin_classes"] and r_fare <= r_limit:
                if r_fare < cheapest_fare:
                    cheapest_fare = r_fare
                    cheapest_platform = r["platform"]

        self._log(
            "compliance_checked",
            {
                "policy_id": policy_id,
                "search_id": search_id,
                "platform": selected_platform,
                "compliance_level": compliance_level,
                "fare": fare,
            },
        )

        return {
            "policy_id": policy_id,
            "search_id": search_id,
            "selected_platform": selected_platform,
            "compliance_level": compliance_level,
            "fare": fare,
            "cabin_class": cabin_class,
            "issues": issues,
            "requires_approval": requires_approval,
            "cheapest_compliant_platform": cheapest_platform,
            "cheapest_compliant_fare": cheapest_fare if cheapest_platform else None,
        }

    # ── Approval workflow ────────────────────────────────────────────────

    def submit_approval(
        self,
        policy_id: int,
        search_id: int,
        selected_platform: str,
        traveler_name: str,
        requester_name: str,
        business_justification: str,
        approver: str,
    ) -> Dict[str, Any]:
        """
        Submit a travel booking approval request to the designated approver.

        Should be called after check_compliance indicates approval is required,
        or as a mandatory step before booking when policy mandates it.

        Args:
            policy_id (int): The policy governing this booking.
            search_id (int): The flight search session for the trip.
            selected_platform (str): The platform and fare being requested for approval.
            traveler_name (str): Full name of the traveler.
            requester_name (str): Name of the person submitting the request
                (may differ from traveler, e.g. an assistant).
            business_justification (str): Reason for the trip and any policy exceptions.
            approver (str): Name or role of the designated approver.

        Returns:
            approval_id (int): Unique approval request identifier.
            approval_request (Dict): The full approval request record.
            status (str): Initial status, always 'pending'.
        """
        if not traveler_name.strip():
            return {"error": "traveler_name is required."}
        if not requester_name.strip():
            return {"error": "requester_name is required."}
        if not business_justification.strip():
            return {"error": "business_justification is required."}
        if not approver.strip():
            return {"error": "approver is required."}

        policy = self._find_policy(policy_id)
        if not policy:
            return {"error": f"Policy ID {policy_id} not found."}

        search = self._find_search(search_id)
        if not search:
            return {"error": f"Search ID {search_id} not found."}

        if selected_platform not in PLATFORMS:
            return {"error": f"Invalid platform '{selected_platform}'. Must be one of: {list(PLATFORMS)}"}

        selected_result = next((r for r in search["results"] if r["platform"] == selected_platform), None)
        if not selected_result:
            return {"error": f"No result found for platform '{selected_platform}' in search {search_id}."}

        approval_id = self.approval_counter
        self.approval_counter += 1

        approval_request = {
            "approval_id": approval_id,
            "policy_id": policy_id,
            "search_id": search_id,
            "selected_platform": selected_platform,
            "flight_no": selected_result["flight_no"],
            "fare": selected_result["price"],
            "cabin_class": selected_result["cabin_class"],
            "departure_time": selected_result["departure_time"],
            "origin": search["origin"],
            "destination": search["destination"],
            "traveler_name": traveler_name,
            "requester_name": requester_name,
            "business_justification": business_justification,
            "approver": approver,
            "status": "pending",
            "approver_comment": "",
        }
        self.approval_requests.append(approval_request)
        self._log("approval_submitted", {"approval_id": approval_id, "traveler": traveler_name, "approver": approver, "fare": selected_result["price"]})

        return {"approval_id": approval_id, "approval_request": approval_request, "status": "pending"}

    def process_approval(
        self,
        approval_id: int,
        decision: str,
        approver_comment: str = "",
    ) -> Dict[str, Any]:
        """
        Process (approve or reject) a pending travel approval request.

        Args:
            approval_id (int): The approval request ID to process.
            decision (str): Approval decision: 'approved' or 'rejected'.
            approver_comment (str): [Optional] Comment or reason from the approver.

        Returns:
            approval_id (int): The processed approval request ID.
            decision (str): The decision applied.
            status (str): Updated approval status.
            approver_comment (str): The approver's comment.
        """
        if decision not in ("approved", "rejected"):
            return {"error": f"Invalid decision '{decision}'. Must be 'approved' or 'rejected'."}

        approval = self._find_approval(approval_id)
        if not approval:
            return {"error": f"Approval ID {approval_id} not found."}

        if approval["status"] != "pending":
            return {"error": f"Approval ID {approval_id} is already '{approval['status']}' and cannot be processed again."}

        approval["status"] = decision
        approval["approver_comment"] = approver_comment

        self._log("approval_processed", {"approval_id": approval_id, "decision": decision})
        return {
            "approval_id": approval_id,
            "decision": decision,
            "status": approval["status"],
            "approver_comment": approver_comment,
        }

    def list_approvals(
        self,
        status: Optional[str] = None,
        traveler_name: Optional[str] = None,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        List approval requests, optionally filtered by status or traveler.

        Args:
            status (str): [Optional] Filter by approval status.
                One of 'pending', 'approved', 'rejected', 'cancelled'.
            traveler_name (str): [Optional] Filter by traveler name (case-insensitive).

        Returns:
            approvals (List[Dict]): Matching approval request summaries.
        """
        if status and status not in VALID_APPROVAL_STATUSES:
            return {"error": f"Invalid status '{status}'. Must be one of: {list(VALID_APPROVAL_STATUSES)}"}

        approvals = self.approval_requests
        if status:
            approvals = [a for a in approvals if a["status"] == status]
        if traveler_name:
            approvals = [a for a in approvals if a["traveler_name"].lower() == traveler_name.lower()]

        summaries = [
            {
                "approval_id": a["approval_id"],
                "traveler_name": a["traveler_name"],
                "origin": a["origin"],
                "destination": a["destination"],
                "fare": a["fare"],
                "cabin_class": a["cabin_class"],
                "selected_platform": a["selected_platform"],
                "status": a["status"],
                "approver": a["approver"],
            }
            for a in approvals
        ]
        return {"approvals": summaries}

    # ── Booking ──────────────────────────────────────────────────────────

    def book_flight(
        self,
        approval_id: int,
        contact_email: str,
        contact_phone: str,
        payment_method: str = "corporate_account",
        special_requests: str = "",
    ) -> Dict[str, Any]:
        """
        Complete a flight booking after approval has been granted.

        Validates that the linked approval is in 'approved' status before
        proceeding. Creates a booking record and marks the approval as consumed.

        Args:
            approval_id (int): The approved approval request ID to book against.
            contact_email (str): Traveler contact email for booking confirmation.
            contact_phone (str): Traveler contact phone number.
            payment_method (str): Payment method to use. Defaults to 'corporate_account'.
            special_requests (str): Any special service requests (e.g. meal preference).

        Returns:
            booking_id (int): Unique booking identifier.
            booking (Dict): The full booking record including PNR and ticket details.
            status (str): Booking status, 'confirmed' on success.
        """
        if not contact_email.strip() or "@" not in contact_email:
            return {"error": "A valid contact_email is required."}
        if not contact_phone.strip():
            return {"error": "contact_phone is required."}

        approval = self._find_approval(approval_id)
        if not approval:
            return {"error": f"Approval ID {approval_id} not found."}

        if approval["status"] == "pending":
            return {"error": f"Approval ID {approval_id} is still pending. Booking requires an approved request."}
        if approval["status"] == "rejected":
            return {"error": f"Approval ID {approval_id} was rejected. Booking cannot proceed."}
        if approval["status"] == "cancelled":
            return {"error": f"Approval ID {approval_id} has been cancelled. Booking cannot proceed."}

        # Check if a booking already exists for this approval
        existing = next((b for b in self.bookings if b["approval_id"] == approval_id and b["status"] != "cancelled"), None)
        if existing:
            return {"error": f"A booking (ID {existing['booking_id']}) already exists for approval ID {approval_id}."}

        booking_id = self.booking_counter
        self.booking_counter += 1

        # Generate a deterministic PNR for simulation
        pnr = f"PNR{booking_id:04d}{approval['flight_no'].replace(' ', '')}"

        booking = {
            "booking_id": booking_id,
            "approval_id": approval_id,
            "policy_id": approval["policy_id"],
            "traveler_name": approval["traveler_name"],
            "flight_no": approval["flight_no"],
            "origin": approval["origin"],
            "destination": approval["destination"],
            "departure_time": approval["departure_time"],
            "cabin_class": approval["cabin_class"],
            "fare": approval["fare"],
            "platform": approval["selected_platform"],
            "pnr": pnr,
            "contact_email": contact_email,
            "contact_phone": contact_phone,
            "payment_method": payment_method,
            "special_requests": special_requests,
            "status": "confirmed",
        }
        self.bookings.append(booking)
        self._log("booking_confirmed", {"booking_id": booking_id, "pnr": pnr, "traveler": approval["traveler_name"], "fare": approval["fare"]})

        return {"booking_id": booking_id, "booking": booking, "status": "confirmed"}

    def cancel_booking(
        self,
        booking_id: int,
        reason: str = "",
    ) -> Dict[str, Any]:
        """
        Cancel an existing confirmed booking.

        Args:
            booking_id (int): The booking ID to cancel.
            reason (str): [Optional] Reason for cancellation.

        Returns:
            booking_id (int): The cancelled booking ID.
            status (str): New status ('cancelled').
        """
        booking = self._find_booking(booking_id)
        if not booking:
            return {"error": f"Booking ID {booking_id} not found."}

        booking["status"] = "cancelled"
        booking["cancelled_at"] = f"t{self.booking_counter}"
        booking["cancellation_reason"] = reason
        return {"booking_id": booking_id, "status": "cancelled"}

    # ── Helper Methods ──────────────────────────────────────────────────────

    def _find_search(self, search_id: int) -> Optional[Dict[str, Any]]:
        """Find a flight search record by its search_id."""
        for s in self.flight_results:
            if s["search_id"] == search_id:
                return s
        return None

    def _find_policy(self, policy_id: int) -> Optional[Dict[str, Any]]:
        """Find a travel policy by its policy_id."""
        for p in self.policies:
            if p["policy_id"] == policy_id:
                return p
        return None

    def _find_approval(self, approval_id: int) -> Optional[Dict[str, Any]]:
        """Find an approval request by its approval_id."""
        for a in self.approval_requests:
            if a["approval_id"] == approval_id:
                return a
        return None

    def _find_booking(self, booking_id: int) -> Optional[Dict[str, Any]]:
        """Find a booking by its booking_id."""
        for b in self.bookings:
            if b["booking_id"] == booking_id:
                return b
        return None

    def _date_diff_days(self, date1_str: str, date2_str: str) -> int:
        """Return the absolute difference in days between two 'YYYY-MM-DD' date strings."""
        d1 = datetime.strptime(date1_str, "%Y-%m-%d")
        d2 = datetime.strptime(date2_str, "%Y-%m-%d")
        return abs((d2 - d1).days)

    def _log(self, event: str, detail: Dict) -> None:
        """Log environment events."""
        if not hasattr(self, '_event_log'):
            self._event_log: List[Dict[str, Any]] = []
        self._event_log.append({
            "event": event,
            "detail": detail,
            "timestamp": datetime.now().isoformat()
        })