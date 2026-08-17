from copy import deepcopy
from typing import Dict, List, Optional, Any

DEFAULT_STATE = {
    "policies": {},
    "flights": {},
    "approvals": {},
    "bookings": {},
    "policy_counter": 1,
    "flight_counter": 1,
    "approval_counter": 1,
    "booking_counter": 1,
    "state_machines": [],
    "entities": {},
    "transition_log": [],
    "sm_counter": 1,
    "entity_counter": 1,
}


class TravelComplianceStateMachineEnv:
    """
    A state-machine-based environment for travel compliance and booking workflow.

    This class models travel requests that transition through compliance checking,
    approval workflows, and booking states. It validates requests against company
    policies, compares flight prices across platforms, triggers approval flows,
    and completes bookings based on guard conditions.

    Attributes:
        policies (Dict[str, Dict]): Company travel policies keyed by policy_id.
        flights (Dict[str, Dict]): Available flights keyed by flight_id.
        approvals (Dict[str, Dict]): Approval records keyed by approval_id.
        bookings (Dict[str, Dict]): Booking records keyed by booking_id.
        policy_counter (int): Auto-incrementing policy ID counter.
        flight_counter (int): Auto-incrementing flight ID counter.
        approval_counter (int): Auto-incrementing approval ID counter.
        booking_counter (int): Auto-incrementing booking ID counter.
        state_machines (List[Dict]): Defined state machine templates.
        entities (Dict[str, Dict]): Active travel request entities keyed by entity_id.
        transition_log (List[Dict]): History of all state transitions and events.
        sm_counter (int): Auto-incrementing state machine ID counter.
        entity_counter (int): Auto-incrementing entity ID counter.
    """

    def __init__(self):
        self.policies: Dict[str, Dict[str, Any]]
        self.flights: Dict[str, Dict[str, Any]]
        self.approvals: Dict[str, Dict[str, Any]]
        self.bookings: Dict[str, Dict[str, Any]]
        self.policy_counter: int
        self.flight_counter: int
        self.approval_counter: int
        self.booking_counter: int
        self.state_machines: List[Dict[str, Any]]
        self.entities: Dict[str, Dict[str, Any]]
        self.transition_log: List[Dict[str, Any]]
        self.sm_counter: int
        self.entity_counter: int
        self._api_description = (
            "This tool manages travel compliance and booking workflows with policy validation, "
            "multi-platform flight comparison, approval flows, and automated booking completion."
        )

    def _load_scenario(self, scenario: dict, long_context=False) -> None:
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_STATE)
        self.policies = scenario.get("policies", DEFAULT_STATE_COPY["policies"])
        self.flights = scenario.get("flights", DEFAULT_STATE_COPY["flights"])
        self.approvals = scenario.get("approvals", DEFAULT_STATE_COPY["approvals"])
        self.bookings = scenario.get("bookings", DEFAULT_STATE_COPY["bookings"])
        self.policy_counter = scenario.get("policy_counter", DEFAULT_STATE_COPY["policy_counter"])
        self.flight_counter = scenario.get("flight_counter", DEFAULT_STATE_COPY["flight_counter"])
        self.approval_counter = scenario.get("approval_counter", DEFAULT_STATE_COPY["approval_counter"])
        self.booking_counter = scenario.get("booking_counter", DEFAULT_STATE_COPY["booking_counter"])
        self.state_machines = scenario.get("state_machines", DEFAULT_STATE_COPY["state_machines"])
        self.entities = scenario.get("entities", DEFAULT_STATE_COPY["entities"])
        self.transition_log = scenario.get("transition_log", DEFAULT_STATE_COPY["transition_log"])
        self.sm_counter = scenario.get("sm_counter", DEFAULT_STATE_COPY["sm_counter"])
        self.entity_counter = scenario.get("entity_counter", DEFAULT_STATE_COPY["entity_counter"])

    def get_env_state(self) -> dict:
        """
        Return the current internal state of the environment.

        Returns:
            dict: All environment state variables including policies, flights, approvals,
                bookings, state machines, entities, and transition logs.
        """
        return {
            "policies": self.policies,
            "flights": self.flights,
            "approvals": self.approvals,
            "bookings": self.bookings,
            "policy_counter": self.policy_counter,
            "flight_counter": self.flight_counter,
            "approval_counter": self.approval_counter,
            "booking_counter": self.booking_counter,
            "state_machines": self.state_machines,
            "entities": self.entities,
            "transition_log": self.transition_log,
            "sm_counter": self.sm_counter,
            "entity_counter": self.entity_counter,
        }

    # ── Policy Management ────────────────────────────────────────────────

    def upload_policy(
        self,
        name: str,
        rules: Dict[str, Any],
        effective_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Upload a company travel policy with compliance rules.

        Args:
            name (str): Policy name (e.g. 'domestic_travel_2024', 'executive_policy').
            rules (Dict[str, Any]): Policy rules as key-value pairs, e.g.
                {"max_flight_price": 2000, "cabin_class": "economy", "advance_days": 7}.
            effective_date (str): [Optional] Policy effective date in ISO format.

        Returns:
            policy_id (str): Unique policy identifier.
            policy (Dict): The created policy record.
        """
        if not name.strip():
            return {"error": "Policy name is required."}
        if not rules:
            return {"error": "Policy rules cannot be empty."}

        policy_id = str(self.policy_counter)
        self.policy_counter += 1

        policy = {
            "policy_id": policy_id,
            "name": name,
            "rules": rules,
            "effective_date": effective_date or f"t+{policy_id}",
            "status": "active",
        }
        self.policies[policy_id] = policy
        self._log("policy_uploaded", {"policy_id": policy_id, "name": name})
        return {"policy_id": policy_id, "policy": policy}

    def get_policy(self, policy_id: str) -> Dict[str, Any]:
        """
        Retrieve a policy by ID.

        Args:
            policy_id (str): Policy ID.

        Returns:
            policy (Dict): The policy record.
        """
        policy = self.policies.get(policy_id)
        if not policy:
            return {"error": f"Policy '{policy_id}' not found."}
        return {"policy": policy}

    def list_policies(self, status: Optional[str] = None) -> Dict[str, Any]:
        """
        List all policies, optionally filtered by status.

        Args:
            status (str): [Optional] Filter by status ('active', 'archived').

        Returns:
            policies (List[Dict]): Matching policy summaries.
        """
        policies = list(self.policies.values())
        if status:
            policies = [p for p in policies if p["status"] == status]
        summaries = [{"policy_id": p["policy_id"], "name": p["name"], "status": p["status"]} for p in policies]
        return {"policies": summaries}

    # ── Flight Management ────────────────────────────────────────────────

    def add_flight(
        self,
        platform: str,
        origin: str,
        destination: str,
        price: float,
        cabin_class: str,
        departure_time: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Add a flight option from a booking platform.

        Args:
            platform (str): Platform name (e.g. 'ctrip', 'qunar', 'fliggy').
            origin (str): Departure city or airport code.
            destination (str): Arrival city or airport code.
            price (float): Flight price in local currency.
            cabin_class (str): Cabin class (e.g. 'economy', 'business', 'first').
            departure_time (str): Departure time in ISO format.
            metadata (Dict): [Optional] Additional flight details (airline, duration, etc.).

        Returns:
            flight_id (str): Unique flight identifier.
            flight (Dict): The created flight record.
        """
        if not platform.strip():
            return {"error": "Platform name is required."}
        if not origin.strip() or not destination.strip():
            return {"error": "Origin and destination are required."}
        if price is None or price <= 0:
            return {"error": "Price must be a positive number."}

        flight_id = str(self.flight_counter)
        self.flight_counter += 1

        flight = {
            "flight_id": flight_id,
            "platform": platform,
            "origin": origin,
            "destination": destination,
            "price": price,
            "cabin_class": cabin_class,
            "departure_time": departure_time,
            "metadata": metadata or {},
            "status": "available",
        }
        self.flights[flight_id] = flight
        self._log("flight_added", {"flight_id": flight_id, "platform": platform, "price": price})
        return {"flight_id": flight_id, "flight": flight}

    def search_flights(
        self,
        origin: Optional[str] = None,
        destination: Optional[str] = None,
        max_price: Optional[float] = None,
        cabin_class: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Search for flights matching criteria.

        Args:
            origin (str): [Optional] Filter by origin.
            destination (str): [Optional] Filter by destination.
            max_price (float): [Optional] Maximum price threshold.
            cabin_class (str): [Optional] Filter by cabin class.

        Returns:
            flights (List[Dict]): Matching flight records sorted by price.
        """
        flights = list(self.flights.values())
        if origin:
            flights = [f for f in flights if f["origin"] == origin]
        if destination:
            flights = [f for f in flights if f["destination"] == destination]
        if max_price is not None:
            flights = [f for f in flights if f["price"] <= max_price]
        if cabin_class:
            flights = [f for f in flights if f["cabin_class"] == cabin_class]
        flights.sort(key=lambda x: x["price"])
        return {"flights": flights}

    # ── State Machine Definition ─────────────────────────────────────────

    def define_travel_workflow(
        self,
        name: str,
        initial_state: str = "draft",
        terminal_states: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Define a travel request workflow state machine.

        Args:
            name (str): Workflow name (e.g. 'standard_travel', 'executive_travel').
            initial_state (str): Starting state for travel requests. Defaults to 'draft'.
            terminal_states (List[str]): [Optional] States marking workflow completion
                (e.g. ['booked', 'cancelled', 'rejected']).

        Returns:
            sm_id (int): Unique state machine identifier.
            state_machine (Dict): The created state machine definition.
        """
        if not name.strip():
            return {"error": "Workflow name is required."}

        sm_id = self.sm_counter
        self.sm_counter += 1

        sm = {
            "sm_id": sm_id,
            "name": name,
            "states": [{"name": initial_state, "on_enter": None, "on_exit": None}],
            "transitions": [],
            "initial_state": initial_state,
            "terminal_states": terminal_states or ["booked", "cancelled", "rejected"],
            "entity_count": 0,
        }
        self.state_machines.append(sm)
        self._log("workflow_defined", {"sm_id": sm_id, "name": name, "initial_state": initial_state})
        return {"sm_id": sm_id, "state_machine": sm}

    def add_workflow_state(self, sm_id: int, name: str) -> Dict[str, Any]:
        """
        Add a new state to a travel workflow.

        Args:
            sm_id (int): State machine ID.
            name (str): State name (e.g. 'compliance_check', 'pending_approval', 'approved').

        Returns:
            sm_id (int): State machine ID.
            state (Dict): The added state entry.
        """
        sm = self._find_sm(sm_id)
        if not sm:
            return {"error": f"Workflow ID {sm_id} not found."}
        if any(s["name"] == name for s in sm["states"]):
            return {"error": f"State '{name}' already exists in workflow {sm_id}."}

        state = {"name": name, "on_enter": None, "on_exit": None}
        sm["states"].append(state)
        self._log("workflow_state_added", {"sm_id": sm_id, "state": name})
        return {"sm_id": sm_id, "state": state}

    def add_workflow_transition(
        self,
        sm_id: int,
        from_state: str,
        to_state: str,
        guard: Optional[Dict[str, Any]] = None,
        trigger: str = "auto",
    ) -> Dict[str, Any]:
        """
        Define a transition between workflow states with optional guard conditions.

        Args:
            sm_id (int): State machine ID.
            from_state (str): Source state name.
            to_state (str): Target state name.
            guard (Dict): [Optional] Guard condition as {field: {op: value}}.
                Supported operators: eq, neq, gt, lt, gte, lte, contains.
                Example: {"compliant": {"eq": True}, "price": {"lte": 2000}}.
            trigger (str): Trigger mode — 'auto' or 'manual'. Defaults to 'auto'.

        Returns:
            sm_id (int): State machine ID.
            transition (Dict): The created transition definition.
        """
        sm = self._find_sm(sm_id)
        if not sm:
            return {"error": f"Workflow ID {sm_id} not found."}
        if trigger not in ("auto", "manual"):
            return {"error": f"Invalid trigger '{trigger}'. Must be 'auto' or 'manual'."}

        state_names = {s["name"] for s in sm["states"]}
        if from_state not in state_names:
            return {"error": f"Source state '{from_state}' not found in workflow {sm_id}."}
        if to_state not in state_names:
            return {"error": f"Target state '{to_state}' not found in workflow {sm_id}."}

        transition = {
            "from": from_state,
            "to": to_state,
            "guard": guard or {},
            "trigger": trigger,
        }
        sm["transitions"].append(transition)
        self._log("workflow_transition_added", {"sm_id": sm_id, "from": from_state, "to": to_state})
        return {"sm_id": sm_id, "transition": transition}

    # ── Travel Request Management ────────────────────────────────────────

    def create_travel_request(
        self,
        sm_id: int,
        traveler: str,
        origin: str,
        destination: str,
        departure_date: str,
        policy_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new travel request entity governed by a workflow state machine.

        Args:
            sm_id (int): Workflow state machine ID.
            traveler (str): Traveler name or employee ID.
            origin (str): Departure city or airport code.
            destination (str): Arrival city or airport code.
            departure_date (str): Departure date in ISO format.
            policy_id (str): [Optional] Policy ID to validate against.
            metadata (Dict): [Optional] Additional request details (purpose, cost center, etc.).

        Returns:
            request_id (str): Unique travel request identifier.
            request (Dict): The created travel request entity.
        """
        sm = self._find_sm(sm_id)
        if not sm:
            return {"error": f"Workflow ID {sm_id} not found."}
        if not traveler.strip():
            return {"error": "Traveler name is required."}
        if not origin.strip() or not destination.strip():
            return {"error": "Origin and destination are required."}

        request_id = str(self.entity_counter)
        self.entity_counter += 1

        request = {
            "entity_id": request_id,
            "sm_id": sm_id,
            "current_state": sm["initial_state"],
            "data": {
                "traveler": traveler,
                "origin": origin,
                "destination": destination,
                "departure_date": departure_date,
                "policy_id": policy_id,
                "selected_flight_id": None,
                "approval_id": None,
                "booking_id": None,
                "compliant": None,
                "metadata": metadata or {},
            },
            "history": [{"state": sm["initial_state"], "timestamp": f"t+{request_id}"}],
            "status": "active",
        }
        self.entities[request_id] = request
        sm["entity_count"] += 1
        self._log("travel_request_created", {"request_id": request_id, "traveler": traveler, "sm_id": sm_id})
        return {"request_id": request_id, "request": request}

    def check_compliance(self, request_id: str) -> Dict[str, Any]:
        """
        Check if a travel request complies with the associated policy.

        Validates the selected flight against policy rules. Updates the request's
        'compliant' field based on validation results.

        Args:
            request_id (str): Travel request ID.

        Returns:
            request_id (str): The request ID.
            compliant (bool): Whether the request is compliant.
            violations (List[str]): List of policy violations if non-compliant.
        """
        request = self._find_entity(request_id)
        if not request:
            return {"error": f"Travel request '{request_id}' not found."}

        policy_id = request["data"].get("policy_id")
        if not policy_id:
            return {"error": "No policy associated with this request."}

        policy = self.policies.get(policy_id)
        if not policy:
            return {"error": f"Policy '{policy_id}' not found."}

        flight_id = request["data"].get("selected_flight_id")
        if not flight_id:
            return {"error": "No flight selected for compliance check."}

        flight = self.flights.get(flight_id)
        if not flight:
            return {"error": f"Flight '{flight_id}' not found."}

        violations = []
        rules = policy["rules"]

        if "max_flight_price" in rules and flight["price"] > rules["max_flight_price"]:
            violations.append(f"Price {flight['price']} exceeds limit {rules['max_flight_price']}")

        if "cabin_class" in rules and flight["cabin_class"] != rules["cabin_class"]:
            violations.append(f"Cabin class '{flight['cabin_class']}' not allowed, must be '{rules['cabin_class']}'")

        compliant = len(violations) == 0
        request["data"]["compliant"] = compliant

        self._log("compliance_checked", {"request_id": request_id, "compliant": compliant, "violations": violations})
        return {"request_id": request_id, "compliant": compliant, "violations": violations}

    def select_flight(self, request_id: str, flight_id: str) -> Dict[str, Any]:
        """
        Select a flight for a travel request.

        Args:
            request_id (str): Travel request ID.
            flight_id (str): Flight ID to select.

        Returns:
            request_id (str): The request ID.
            flight_id (str): The selected flight ID.
        """
        request = self._find_entity(request_id)
        if not request:
            return {"error": f"Travel request '{request_id}' not found."}

        flight = self.flights.get(flight_id)
        if not flight:
            return {"error": f"Flight '{flight_id}' not found."}

        request["data"]["selected_flight_id"] = flight_id
        self._log("flight_selected", {"request_id": request_id, "flight_id": flight_id})
        return {"request_id": request_id, "flight_id": flight_id}

    def initiate_approval(self, request_id: str, approver: str) -> Dict[str, Any]:
        """
        Initiate an approval flow for a travel request.

        Args:
            request_id (str): Travel request ID.
            approver (str): Approver name or employee ID.

        Returns:
            approval_id (str): Unique approval identifier.
            approval (Dict): The created approval record.
        """
        request = self._find_entity(request_id)
        if not request:
            return {"error": f"Travel request '{request_id}' not found."}

        approval_id = str(self.approval_counter)
        self.approval_counter += 1

        approval = {
            "approval_id": approval_id,
            "request_id": request_id,
            "approver": approver,
            "status": "pending",
            "decision": None,
            "comments": None,
            "timestamp": f"t+{approval_id}",
        }
        self.approvals[approval_id] = approval
        request["data"]["approval_id"] = approval_id

        self._log("approval_initiated", {"approval_id": approval_id, "request_id": request_id, "approver": approver})
        return {"approval_id": approval_id, "approval": approval}

    def process_approval(
        self,
        approval_id: str,
        decision: str,
        comments: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Process an approval decision.

        Args:
            approval_id (str): Approval ID.
            decision (str): Approval decision ('approved' or 'rejected').
            comments (str): [Optional] Approver comments.

        Returns:
            approval_id (str): The approval ID.
            decision (str): The approval decision.
        """
        approval = self.approvals.get(approval_id)
        if not approval:
            return {"error": f"Approval '{approval_id}' not found."}

        if decision not in ("approved", "rejected"):
            return {"error": f"Invalid decision '{decision}'. Must be 'approved' or 'rejected'."}

        approval["status"] = "completed"
        approval["decision"] = decision
        approval["comments"] = comments

        request_id = approval["request_id"]
        request = self._find_entity(request_id)
        if request:
            request["data"]["approval_decision"] = decision

        self._log("approval_processed", {"approval_id": approval_id, "decision": decision})
        return {"approval_id": approval_id, "decision": decision}

    def complete_booking(self, request_id: str) -> Dict[str, Any]:
        """
        Complete the booking for an approved travel request.

        Args:
            request_id (str): Travel request ID.

        Returns:
            booking_id (str): Unique booking identifier.
            booking (Dict): The created booking record.
        """
        request = self._find_entity(request_id)
        if not request:
            return {"error": f"Travel request '{request_id}' not found."}

        if request["data"].get("approval_decision") != "approved":
            return {"error": "Request must be approved before booking."}

        flight_id = request["data"].get("selected_flight_id")
        if not flight_id:
            return {"error": "No flight selected for booking."}

        booking_id = str(self.booking_counter)
        self.booking_counter += 1

        booking = {
            "booking_id": booking_id,
            "request_id": request_id,
            "flight_id": flight_id,
            "status": "confirmed",
            "confirmation_code": f"BK{booking_id}",
            "timestamp": f"t+{booking_id}",
        }
        self.bookings[booking_id] = booking
        request["data"]["booking_id"] = booking_id

        self._log("booking_completed", {"booking_id": booking_id, "request_id": request_id, "flight_id": flight_id})
        return {"booking_id": booking_id, "booking": booking}

    # ── State Transition ─────────────────────────────────────────────────

    def transition_request(self, request_id: str, to_state: str) -> Dict[str, Any]:
        """
        Attempt to transition a travel request to a target state.

        Validates that a transition exists from the current state to the target
        state, and that all guard conditions are satisfied against the request's data.

        Args:
            request_id (str): Travel request ID.
            to_state (str): Desired target state.

        Returns:
            request_id (str): The request ID.
            from_state (str): Previous state.
            to_state (str): New state after transition.
            result (str): 'transitioned', 'blocked_by_guard', or 'no_transition'.
        """
        request = self._find_entity(request_id)
        if not request:
            return {"error": f"Travel request '{request_id}' not found."}
        if request["status"] != "active":
            return {"error": f"Travel request '{request_id}' is {request['status']}."}

        sm = self._find_sm(request["sm_id"])
        if not sm:
            return {"error": f"Workflow {request['sm_id']} not found."}

        current = request["current_state"]

        matching = [t for t in sm["transitions"] if t["from"] == current and t["to"] == to_state]
        if not matching:
            return {
                "request_id": request_id,
                "from_state": current,
                "to_state": to_state,
                "result": "no_transition",
                "available": [t["to"] for t in sm["transitions"] if t["from"] == current],
            }

        transition = matching[0]
        if not self._validate_guard(transition.get("guard", {}), request["data"]):
            return {
                "request_id": request_id,
                "from_state": current,
                "to_state": to_state,
                "result": "blocked_by_guard",
                "failed_guard": transition["guard"],
            }

        request["current_state"] = to_state
        request["history"].append({"state": to_state, "timestamp": f"t+{self.entity_counter}"})
        self.transition_log.append({
            "entity_id": request_id,
            "from": current,
            "to": to_state,
            "timestamp": f"t+{self.entity_counter}",
        })

        if to_state in sm["terminal_states"]:
            request["status"] = "completed"

        self._log("request_transitioned", {"request_id": request_id, "from": current, "to": to_state})
        return {
            "request_id": request_id,
            "from_state": current,
            "to_state": to_state,
            "result": "transitioned",
        }

    def get_travel_request(self, request_id: str) -> Dict[str, Any]:
        """
        Get the full state and history of a travel request.

        Args:
            request_id (str): Travel request ID.

        Returns:
            request (Dict): Full travel request entity with state and history.
        """
        request = self._find_entity(request_id)
        if not request:
            return {"error": f"Travel request '{request_id}' not found."}
        return {"request": request}

    def list_travel_requests(
        self,
        sm_id: Optional[int] = None,
        state: Optional[str] = None,
        traveler: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        List travel requests, optionally filtered by workflow, state, or traveler.

        Args:
            sm_id (int): [Optional] Filter by workflow state machine ID.
            state (str): [Optional] Filter by current state.
            traveler (str): [Optional] Filter by traveler name.

        Returns:
            requests (List[Dict]): Matching travel request summaries.
        """
        requests = list(self.entities.values())
        if sm_id is not None:
            requests = [r for r in requests if r["sm_id"] == sm_id]
        if state:
            requests = [r for r in requests if r["current_state"] == state]
        if traveler:
            requests = [r for r in requests if r["data"].get("traveler") == traveler]
        summaries = [
            {
                "request_id": r["entity_id"],
                "traveler": r["data"].get("traveler"),
                "current_state": r["current_state"],
                "status": r["status"],
            }
            for r in requests
        ]
        return {"requests": summaries}

    # ── Helpers ───────────────────────────────────────────────────────────

    def _find_sm(self, sm_id: int) -> Optional[Dict[str, Any]]:
        for sm in self.state_machines:
            if sm["sm_id"] == sm_id:
                return sm
        return None

    def _find_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        return self.entities.get(entity_id)

    @staticmethod
    def _validate_guard(guard: Dict, data: Dict) -> bool:
        """Evaluate guard conditions against entity data. Returns True if all pass."""
        if not guard:
            return True
        ops = {
            "eq": lambda a, b: a == b,
            "neq": lambda a, b: a != b,
            "gt": lambda a, b: a > b,
            "lt": lambda a, b: a < b,
            "gte": lambda a, b: a >= b,
            "lte": lambda a, b: a <= b,
            "contains": lambda a, b: b in a if hasattr(a, '__contains__') else False,
        }
        for field, condition in guard.items():
            actual = data.get(field)
            if actual is None:
                return False
            for op, expected in condition.items():
                if op not in ops:
                    continue
                if not ops[op](actual, expected):
                    return False
        return True

    def _log(self, event: str, detail: Dict) -> None:
        self.transition_log.append({"event": event, "detail": detail, "timestamp": f"t+{self.entity_counter}"})