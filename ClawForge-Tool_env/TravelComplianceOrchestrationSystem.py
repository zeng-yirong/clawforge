from copy import deepcopy
from typing import Dict, List, Optional, Any
from datetime import datetime

# ---------------------------------------------------------------------------
# Default initial state
# ---------------------------------------------------------------------------

DEFAULT_STATE = {
    "policies": {},                  # policy_id -> policy record
    "flight_offers": {},             # search_id -> list of offer records
    "booking_requests": [],          # all booking request records
    "approvers": {},                 # approver_id -> approver record
    "bookings": {},                  # booking_id -> confirmed booking record
    "execution_log": [],             # audit trail of every operation
    "policy_counter": 1,
    "search_counter": 1,
    "request_counter": 1,
    "booking_counter": 1,
    "approver_counter": 1,
}

# ---------------------------------------------------------------------------
# Valid status constants
# ---------------------------------------------------------------------------

VALID_POLICY_CLASSES = ("economy", "business", "first")
VALID_REQUEST_STATUSES = (
    "draft", "pending_compliance", "pending_approval",
    "approved", "rejected", "booked", "cancelled",
)
VALID_APPROVER_STATUSES = ("idle", "busy", "offline")
VALID_APPROVAL_DECISIONS = ("approve", "reject")
VALID_CABIN_CLASSES = ("economy", "business", "first")


# ---------------------------------------------------------------------------
# Environment class
# ---------------------------------------------------------------------------

class TravelComplianceOrchestrationEnv:
    """
    A unified orchestration environment for corporate travel compliance and booking.

    This class models the end-to-end pipeline of a business travel request:
    loading company travel policies from PDF documents, searching and comparing
    flight prices across multiple platforms, running automated compliance checks,
    routing approval workflows to registered approvers, and finalising bookings —
    all while maintaining a full audit log.

    The design follows the orchestration pattern: each booking request is a
    pipeline whose stages are compliance_check → approval → booking. Workers
    are registered approvers or booking agents. Every state transition is
    recorded in the execution log.

    Attributes:
        policies (Dict[str, Dict]): Loaded travel policy records keyed by policy_id.
        flight_offers (Dict[str, List[Dict]]): Flight search results keyed by search_id.
        booking_requests (List[Dict]): All booking request records with full stage state.
        approvers (Dict[str, Dict]): Registered approvers keyed by approver_id.
        bookings (Dict[str, Dict]): Confirmed booking records keyed by booking_id.
        execution_log (List[Dict]): Immutable audit trail of every operation.
        policy_counter (int): Auto-incrementing policy ID counter.
        search_counter (int): Auto-incrementing search ID counter.
        request_counter (int): Auto-incrementing booking request ID counter.
        booking_counter (int): Auto-incrementing booking ID counter.
        approver_counter (int): Auto-incrementing approver ID counter.
    """

    def __init__(self) -> None:
        self.policies: Dict[str, Dict[str, Any]]
        self.flight_offers: Dict[str, List[Dict[str, Any]]]
        self.booking_requests: List[Dict[str, Any]]
        self.approvers: Dict[str, Dict[str, Any]]
        self.bookings: Dict[str, Dict[str, Any]]
        self.execution_log: List[Dict[str, Any]]
        self.policy_counter: int
        self.search_counter: int
        self.request_counter: int
        self.booking_counter: int
        self.approver_counter: int
        self._api_description = (
            "Manages corporate travel compliance and booking: load PDF travel policies, "
            "compare multi-platform flight prices, run automated compliance checks, "
            "route approval workflows, and finalise bookings with a full audit trail."
        )

    # ------------------------------------------------------------------
    # Core lifecycle methods
    # ------------------------------------------------------------------

    def _load_scenario(self, scenario: dict, long_context: bool = False) -> None:
        """Load environment state from a scenario dictionary."""
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_STATE)
        self.policies = scenario.get("policies", DEFAULT_STATE_COPY["policies"])
        self.flight_offers = scenario.get("flight_offers", DEFAULT_STATE_COPY["flight_offers"])
        self.booking_requests = scenario.get("booking_requests", DEFAULT_STATE_COPY["booking_requests"])
        self.approvers = scenario.get("approvers", DEFAULT_STATE_COPY["approvers"])
        self.bookings = scenario.get("bookings", DEFAULT_STATE_COPY["bookings"])
        self.execution_log = scenario.get("execution_log", DEFAULT_STATE_COPY["execution_log"])
        self.policy_counter = scenario.get("policy_counter", DEFAULT_STATE_COPY["policy_counter"])
        self.search_counter = scenario.get("search_counter", DEFAULT_STATE_COPY["search_counter"])
        self.request_counter = scenario.get("request_counter", DEFAULT_STATE_COPY["request_counter"])
        self.booking_counter = scenario.get("booking_counter", DEFAULT_STATE_COPY["booking_counter"])
        self.approver_counter = scenario.get("approver_counter", DEFAULT_STATE_COPY["approver_counter"])

    def get_env_state(self) -> dict:
        """
        Return the current internal state of the environment.

        Returns:
            dict: All environment state variables including policies,
                  flight_offers, booking_requests, approvers, bookings,
                  execution_log, and all auto-increment counters.
        """
        return {
            "policies": self.policies,
            "flight_offers": self.flight_offers,
            "booking_requests": self.booking_requests,
            "approvers": self.approvers,
            "bookings": self.bookings,
            "execution_log": self.execution_log,
            "policy_counter": self.policy_counter,
            "search_counter": self.search_counter,
            "request_counter": self.request_counter,
            "booking_counter": self.booking_counter,
            "approver_counter": self.approver_counter,
        }

    # ------------------------------------------------------------------
    # Policy management  (PDF policy ingestion & query)
    # ------------------------------------------------------------------

    def load_policy(
        self,
        source_filename: str,
        max_price_economy: float,
        max_price_business: float,
        max_price_first: float,
        allowed_cabin_classes: List[str],
        advance_booking_days: int,
        requires_approval_above: float,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Load and register a corporate travel policy parsed from a PDF document.

        In a production system this method would accept raw PDF bytes and run an
        extraction pipeline; here the caller supplies the already-parsed fields,
        simulating the output of a PDF parser stage.

        Args:
            source_filename (str): Original PDF filename, used as a reference label.
            max_price_economy (float): Maximum allowed ticket price for economy class (CNY).
            max_price_business (float): Maximum allowed ticket price for business class (CNY).
            max_price_first (float): Maximum allowed ticket price for first class (CNY).
            allowed_cabin_classes (List[str]): Permitted cabin classes, e.g. ['economy', 'business'].
            advance_booking_days (int): Minimum days in advance a ticket must be booked.
            requires_approval_above (float): Ticket price threshold above which manager approval is required.
            notes (str): [Optional] Free-text notes or policy summary extracted from the PDF.

        Returns:
            policy_id (str): Unique policy identifier.
            policy (Dict): The registered policy record.
        """
        if not source_filename.strip():
            return {"error": "source_filename must not be empty."}
        if any(v is None or v <= 0 for v in (max_price_economy, max_price_business, max_price_first)):
            return {"error": "All max_price values must be positive numbers."}
        if advance_booking_days is None or advance_booking_days < 0:
            return {"error": "advance_booking_days must be a non-negative integer."}
        if requires_approval_above is None or requires_approval_above < 0:
            return {"error": "requires_approval_above must be a non-negative number."}

        invalid_classes = [c for c in allowed_cabin_classes if c not in VALID_CABIN_CLASSES]
        if invalid_classes:
            return {
                "error": (
                    f"Invalid cabin class(es): {invalid_classes}. "
                    f"Must be one of: {', '.join(VALID_CABIN_CLASSES)}"
                )
            }
        if not allowed_cabin_classes:
            return {"error": "allowed_cabin_classes must contain at least one cabin class."}

        policy_id = str(self.policy_counter)
        self.policy_counter += 1

        policy = {
            "policy_id": policy_id,
            "source_filename": source_filename,
            "max_price": {
                "economy": max_price_economy,
                "business": max_price_business,
                "first": max_price_first,
            },
            "allowed_cabin_classes": allowed_cabin_classes,
            "advance_booking_days": advance_booking_days,
            "requires_approval_above": requires_approval_above,
            "notes": notes or "",
        }
        self.policies[policy_id] = policy
        self._log("policy_loaded", {"policy_id": policy_id, "source": source_filename})
        return {"policy_id": policy_id, "policy": policy}

    def get_policy(self, policy_id: str) -> Dict[str, Any]:
        """
        Retrieve a registered travel policy by its ID.

        Args:
            policy_id (str): Policy ID to look up.

        Returns:
            policy (Dict): The full policy record.
        """
        policy = self.policies.get(policy_id)
        if not policy:
            return {"error": f"Policy '{policy_id}' not found."}
        return {"policy": policy}

    def list_policies(self) -> Dict[str, Any]:
        """
        List all registered travel policies.

        Returns:
            policies (List[Dict]): All policy records with their IDs and source filenames.
        """
        summaries = [
            {
                "policy_id": p["policy_id"],
                "source_filename": p["source_filename"],
                "allowed_cabin_classes": p["allowed_cabin_classes"],
                "requires_approval_above": p["requires_approval_above"],
            }
            for p in self.policies.values()
        ]
        return {"policies": summaries}

    # ------------------------------------------------------------------
    # Flight search & price comparison
    # ------------------------------------------------------------------

    def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        cabin_class: str,
        platforms: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Search for available flights across multiple booking platforms and record the offers.

        Each platform returns a simulated list of flight offers. In production this
        method would call real platform APIs; here it generates deterministic
        simulated results so the RL agent can reason about price comparison.

        Args:
            origin (str): IATA airport code for the departure city, e.g. 'PEK'.
            destination (str): IATA airport code for the arrival city, e.g. 'SHA'.
            departure_date (str): Departure date in YYYY-MM-DD format.
            cabin_class (str): Desired cabin class — 'economy', 'business', or 'first'.
            platforms (List[str]): [Optional] Platform names to query. Defaults to
                ['Ctrip', 'Fliggy', 'Qunar'] if not provided.

        Returns:
            search_id (str): Unique identifier for this search session.
            offers (List[Dict]): All flight offers found, sorted by price ascending.
            cheapest (Dict): The single cheapest offer across all platforms.
        """
        if not origin.strip() or not destination.strip():
            return {"error": "origin and destination must not be empty."}
        if origin.strip().upper() == destination.strip().upper():
            return {"error": "origin and destination must be different airports."}
        if not departure_date.strip():
            return {"error": "departure_date must not be empty."}
        if cabin_class not in VALID_CABIN_CLASSES:
            return {
                "error": (
                    f"Invalid cabin_class '{cabin_class}'. "
                    f"Must be one of: {', '.join(VALID_CABIN_CLASSES)}"
                )
            }

        platforms = platforms or ["Ctrip", "Fliggy", "Qunar"]
        if not platforms:
            return {"error": "platforms list must not be empty."}

        search_id = str(self.search_counter)
        self.search_counter += 1

        # Simulate offers: each platform returns 2 flights with deterministic pricing
        base_prices = {"economy": 800.0, "business": 2400.0, "first": 5000.0}
        base = base_prices[cabin_class]
        offers: List[Dict[str, Any]] = []
        for idx, platform in enumerate(platforms):
            for flight_num in range(1, 3):
                price_multiplier = 1.0 + (idx * 0.08) + (flight_num * 0.05)
                price = round(base * price_multiplier, 2)
                offers.append({
                    "offer_id": f"{search_id}-{platform}-{flight_num}",
                    "platform": platform,
                    "origin": origin.upper(),
                    "destination": destination.upper(),
                    "departure_date": departure_date,
                    "cabin_class": cabin_class,
                    "price": price,
                    "currency": "CNY",
                    "airline": f"Airline-{(idx + flight_num) % 3 + 1}",
                    "flight_number": f"CA{1000 + idx * 10 + flight_num}",
                    "available_seats": 10 - idx,
                })

        offers.sort(key=lambda o: o["price"])
        self.flight_offers[search_id] = offers

        self._log(
            "flights_searched",
            {
                "search_id": search_id,
                "route": f"{origin.upper()}->{destination.upper()}",
                "date": departure_date,
                "cabin_class": cabin_class,
                "platforms": platforms,
                "offer_count": len(offers),
            },
        )
        return {
            "search_id": search_id,
            "offers": offers,
            "cheapest": offers[0] if offers else None,
        }

    def get_search_results(self, search_id: str) -> Dict[str, Any]:
        """
        Retrieve previously fetched flight offers by search ID.

        Args:
            search_id (str): Search session ID returned by search_flights.

        Returns:
            search_id (str): The queried search ID.
            offers (List[Dict]): All flight offers from that search session.
        """
        offers = self.flight_offers.get(search_id)
        if offers is None:
            return {"error": f"Search ID '{search_id}' not found."}
        return {"search_id": search_id, "offers": offers}

    def compare_offers_with_policy(
        self, search_id: str, policy_id: str
    ) -> Dict[str, Any]:
        """
        Compare flight offers from a search session against a loaded travel policy.

        For each offer, this method checks cabin class eligibility, price ceiling,
        and flags whether manager approval will be required.

        Args:
            search_id (str): Search session ID whose offers will be evaluated.
            policy_id (str): Policy ID to use as the compliance baseline.

        Returns:
            search_id (str): The evaluated search ID.
            policy_id (str): The applied policy ID.
            compliant_offers (List[Dict]): Offers that pass all policy checks,
                each annotated with 'needs_approval' (bool).
            non_compliant_offers (List[Dict]): Offers that violate at least one
                policy rule, each annotated with 'violations' (List[str]).
            recommended_offer (Dict | None): The cheapest compliant offer, or None
                if no compliant offers exist.
        """
        offers = self.flight_offers.get(search_id)
        if offers is None:
            return {"error": f"Search ID '{search_id}' not found."}
        policy = self.policies.get(policy_id)
        if not policy:
            return {"error": f"Policy '{policy_id}' not found."}

        compliant: List[Dict[str, Any]] = []
        non_compliant: List[Dict[str, Any]] = []

        for offer in offers:
            violations: List[str] = []
            cabin = offer["cabin_class"]
            price = offer["price"]

            if cabin not in policy["allowed_cabin_classes"]:
                violations.append(
                    f"Cabin class '{cabin}' not in allowed classes "
                    f"{policy['allowed_cabin_classes']}."
                )
            max_price = policy["max_price"].get(cabin, 0)
            if price > max_price:
                violations.append(
                    f"Price {price} CNY exceeds policy ceiling "
                    f"{max_price} CNY for {cabin}."
                )

            annotated = deepcopy(offer)
            if violations:
                annotated["violations"] = violations
                non_compliant.append(annotated)
            else:
                annotated["needs_approval"] = price > policy["requires_approval_above"]
                compliant.append(annotated)

        recommended = compliant[0] if compliant else None  # already sorted by price

        self._log(
            "offers_compared",
            {
                "search_id": search_id,
                "policy_id": policy_id,
                "compliant_count": len(compliant),
                "non_compliant_count": len(non_compliant),
            },
        )
        return {
            "search_id": search_id,
            "policy_id": policy_id,
            "compliant_offers": compliant,
            "non_compliant_offers": non_compliant,
            "recommended_offer": recommended,
        }

    # ------------------------------------------------------------------
    # Approver management
    # ------------------------------------------------------------------

    def register_approver(
        self,
        name: str,
        role: str,
        approval_limit: float,
        department: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Register a manager or delegate who can approve travel booking requests.

        Args:
            name (str): Full name of the approver.
            role (str): Organisational role, e.g. 'line_manager', 'finance_director'.
            approval_limit (float): Maximum ticket price this approver is authorised
                to approve. Requests above this limit must escalate.
            department (str): [Optional] Department the approver belongs to.

        Returns:
            approver_id (str): Unique approver identifier.
            approver (Dict): The registered approver record.
        """
        if not name.strip() or not role.strip():
            return {"error": "Approver name and role must both be non-empty."}
        if approval_limit is None or approval_limit < 0:
            return {"error": "approval_limit must be a non-negative number."}

        approver_id = str(self.approver_counter)
        self.approver_counter += 1

        approver = {
            "approver_id": approver_id,
            "name": name,
            "role": role,
            "approval_limit": approval_limit,
            "department": department or "",
            "status": "idle",
            "reviewed_count": 0,
        }
        self.approvers[approver_id] = approver
        self._log("approver_registered", {"approver_id": approver_id, "role": role})
        return {"approver_id": approver_id, "approver": approver}

    def unregister_approver(self, approver_id: str) -> Dict[str, str]:
        """
        Remove an approver from the system.

        Args:
            approver_id (str): Approver ID to remove.

        Returns:
            status (str): Removal confirmation message.
        """
        if approver_id not in self.approvers:
            return {"error": f"Approver '{approver_id}' not found."}
        if self.approvers[approver_id]["status"] == "busy":
            return {
                "error": (
                    f"Approver '{approver_id}' is currently reviewing a request. "
                    "Wait for completion before unregistering."
                )
            }
        del self.approvers[approver_id]
        return {"status": f"Approver '{approver_id}' unregistered."}

    def list_approvers(
        self,
        role: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        List registered approvers, optionally filtered by role or status.

        Args:
            role (str): [Optional] Filter by organisational role.
            status (str): [Optional] Filter by approver status — 'idle', 'busy', or 'offline'.

        Returns:
            approvers (List[Dict]): Matching approver records.
        """
        if status and status not in VALID_APPROVER_STATUSES:
            return {
                "error": (
                    f"Invalid status '{status}'. "
                    f"Must be one of: {', '.join(VALID_APPROVER_STATUSES)}"
                )
            }
        approvers = list(self.approvers.values())
        if role:
            approvers = [a for a in approvers if a["role"] == role]
        if status:
            approvers = [a for a in approvers if a["status"] == status]
        return {"approvers": approvers}

    # ------------------------------------------------------------------
    # Booking request lifecycle  (the orchestration pipeline)
    # ------------------------------------------------------------------

    def create_booking_request(
        self,
        traveller_name: str,
        offer_id: str,
        search_id: str,
        policy_id: str,
        purpose: str,
        assigned_approver_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a new travel booking request and initialise its compliance pipeline.

        The request is created in 'draft' status. The pipeline stages are:
          1. compliance_check — validate the selected offer against the active policy.
          2. approval         — route to an approver if required by policy.
          3. booking          — finalise the ticket purchase.

        Args:
            traveller_name (str): Full name of the employee travelling.
            offer_id (str): The offer_id of the selected flight from a search session.
            search_id (str): Search session ID that produced the selected offer.
            policy_id (str): Policy ID to apply for compliance checking.
            purpose (str): Business purpose / justification for the trip.
            assigned_approver_id (str): [Optional] Pre-assign an approver for the
                approval stage. Can also be assigned later via assign_approver.

        Returns:
            request_id (str): Unique booking request identifier.
            request (Dict): The full booking request record with initialised stages.
        """
        if not traveller_name.strip():
            return {"error": "traveller_name must not be empty."}
        if not purpose.strip():
            return {"error": "purpose must not be empty."}

        offers = self.flight_offers.get(search_id)
        if offers is None:
            return {"error": f"Search ID '{search_id}' not found."}
        selected_offer = next((o for o in offers if o["offer_id"] == offer_id), None)
        if not selected_offer:
            return {"error": f"Offer '{offer_id}' not found in search '{search_id}'."}

        if policy_id not in self.policies:
            return {"error": f"Policy '{policy_id}' not found."}

        if assigned_approver_id and assigned_approver_id not in self.approvers:
            return {"error": f"Approver '{assigned_approver_id}' not found."}

        request_id = str(self.request_counter)
        self.request_counter += 1

        stages = [
            {
                "stage_id": "compliance_check",
                "name": "Compliance Check",
                "action": "check_policy_compliance",
                "status": "pending",
                "result": None,
                "retry_count": 0,
                "max_retries": 1,
                "on_failure": "abort",
                "depends_on": [],
            },
            {
                "stage_id": "approval",
                "name": "Manager Approval",
                "action": "request_approval",
                "status": "pending",
                "result": None,
                "retry_count": 0,
                "max_retries": 1,
                "on_failure": "abort",
                "depends_on": ["compliance_check"],
                "assigned_approver": assigned_approver_id,
            },
            {
                "stage_id": "booking",
                "name": "Ticket Booking",
                "action": "confirm_booking",
                "status": "pending",
                "result": None,
                "retry_count": 0,
                "max_retries": 2,
                "on_failure": "retry",
                "depends_on": ["approval"],
            },
        ]

        request = {
            "request_id": request_id,
            "traveller_name": traveller_name,
            "offer": deepcopy(selected_offer),
            "search_id": search_id,
            "policy_id": policy_id,
            "purpose": purpose,
            "status": "draft",
            "stages": stages,
            "rollback_log": [],
            "booking_id": None,
        }
        self.booking_requests.append(request)
        self._log(
            "booking_request_created",
            {
                "request_id": request_id,
                "traveller": traveller_name,
                "offer_id": offer_id,
                "policy_id": policy_id,
            },
        )
        return {"request_id": request_id, "request": request}

    def get_booking_request(self, request_id: str) -> Dict[str, Any]:
        """
        Retrieve the full state of a booking request.

        Args:
            request_id (str): Booking request ID.

        Returns:
            request (Dict): Full booking request record including all stage states.
        """
        req = self._find_request(request_id)
        if not req:
            return {"error": f"Booking request '{request_id}' not found."}
        return {"request": req}

    def list_booking_requests(
        self, status: Optional[str] = None, traveller_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List all booking requests, optionally filtered by status or traveller name.

        Args:
            status (str): [Optional] Filter by request status.
            traveller_name (str): [Optional] Filter by exact traveller name.

        Returns:
            requests (List[Dict]): Matching booking request summaries.
        """
        if status and status not in VALID_REQUEST_STATUSES:
            return {
                "error": (
                    f"Invalid status '{status}'. "
                    f"Must be one of: {', '.join(VALID_REQUEST_STATUSES)}"
                )
            }
        reqs = self.booking_requests
        if status:
            reqs = [r for r in reqs if r["status"] == status]
        if traveller_name:
            reqs = [r for r in reqs if r["traveller_name"] == traveller_name]

        summaries = []
        for r in reqs:
            completed = sum(1 for s in r["stages"] if s["status"] == "completed")
            summaries.append({
                "request_id": r["request_id"],
                "traveller_name": r["traveller_name"],
                "status": r["status"],
                "offer_id": r["offer"]["offer_id"],
                "price": r["offer"]["price"],
                "progress": f"{completed}/{len(r['stages'])}",
                "booking_id": r.get("booking_id"),
            })
        return {"requests": summaries}

    # ------------------------------------------------------------------
    # Stage execution
    # ------------------------------------------------------------------

    def assign_approver(
        self, request_id: str, approver_id: str
    ) -> Dict[str, Any]:
        """
        Assign an approver to the approval stage of a booking request.

        Args:
            request_id (str): Booking request ID.
            approver_id (str): Approver ID to assign.

        Returns:
            request_id (str): The updated request ID.
            assigned_approver (str): The assigned approver ID.
        """
        req = self._find_request(request_id)
        if not req:
            return {"error": f"Booking request '{request_id}' not found."}
        if approver_id not in self.approvers:
            return {"error": f"Approver '{approver_id}' not found."}

        approval_stage = self._find_stage(req, "approval")
        if not approval_stage:
            return {"error": "Approval stage not found in this request."}

        approval_stage["assigned_approver"] = approver_id
        self._log(
            "approver_assigned",
            {"request_id": request_id, "approver_id": approver_id},
        )
        return {"request_id": request_id, "assigned_approver": approver_id}

    def run_compliance_check(self, request_id: str) -> Dict[str, Any]:
        """
        Execute the compliance_check stage for a booking request.

        Validates the selected flight offer against the associated travel policy,
        checking cabin class eligibility and price ceiling. On success the stage
        is marked 'completed' and the request advances to 'pending_approval' or
        'pending_approval' (skipped if no approval needed). On failure the request
        is set to 'rejected'.

        Args:
            request_id (str): Booking request ID.

        Returns:
            request_id (str): The evaluated request ID.
            stage_status (str): 'completed' or 'failed'.
            compliant (bool): Whether the offer passed all policy checks.
            violations (List[str]): List of policy violations found (empty if compliant).
            needs_approval (bool): True if the price exceeds the approval threshold.
        """
        req = self._find_request(request_id)
        if not req:
            return {"error": f"Booking request '{request_id}' not found."}
        if req["status"] not in ("draft", "pending_compliance"):
            return {
                "error": (
                    f"Request '{request_id}' is in status '{req['status']}'. "
                    "Compliance check requires 'draft' or 'pending_compliance'."
                )
            }

        stage = self._find_stage(req, "compliance_check")
        if not stage:
            return {"error": "compliance_check stage not found."}
        if stage["status"] not in ("pending", "failed"):
            return {"error": f"compliance_check stage is already '{stage['status']}'."}

        req["status"] = "pending_compliance"
        stage["status"] = "in_progress"
        self._log("compliance_check_started", {"request_id": request_id})

        policy = self.policies.get(req.get("policy_id")) if req.get("policy_id") else None
        if not policy:
            req["status"] = "rejected"
            stage["status"] = "failed"
            return {"request_id": request_id, "status": "rejected", "error": "No policy configured for request."}

        compliant = True
        issues = []
        offer = req.get("offer")
        if offer:
            cabin = offer.get("cabin_class", "")
            price = offer.get("price", 0)
            max_price_map = policy.get("max_price", {})
            max_price = max_price_map.get(cabin, float("inf"))
            if price > max_price:
                compliant = False
                issues.append(
                    f"Price {price} CNY exceeds max {max_price} CNY for {cabin}."
                )
            allowed_classes = policy.get("allowed_cabin_classes", [])
            if cabin and cabin not in allowed_classes:
                compliant = False
                issues.append(
                    f"Cabin class '{cabin}' not in allowed classes {allowed_classes}."
                )

        if compliant:
            req["status"] = "pending_approval"
            stage["status"] = "completed"
        else:
            req["status"] = "rejected"
            stage["status"] = "failed"
        self._log("compliance_check_completed", {"request_id": request_id, "compliant": compliant})
        return {"request_id": request_id, "status": req["status"], "compliant": compliant, "issues": issues}

    def _find_request(self, request_id: str):
        """Find a booking request by request_id. Returns None if not found."""
        for r in self.booking_requests:
            if r["request_id"] == request_id:
                return r
        return None

    def _find_stage(self, req: Dict, stage_id: str):
        """Find a stage within a booking request by stage_id. Returns None if not found."""
        for s in req["stages"]:
            if s["stage_id"] == stage_id:
                return s
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