from copy import deepcopy
from typing import Dict, List, Optional, Any
from datetime import datetime
import random

DEFAULT_STATE = {
    "policies": {
        "default_policy": {
            "source": "company_travel_policy_v3.pdf",
            "type": "pdf",
            "active": True,
            "rules": {
                "max_domestic_price": 1500,
                "max_international_price": 8000,
                "allowed_cabin_domestic": ["economy", "premium_economy"],
                "allowed_cabin_international": ["economy", "premium_economy", "business"],
                "advance_booking_days": 3,
                "require_approval_above": 1000,
                "require_manager_approval_above": 5000,
            },
            "parsed_at": None,
        }
    },
    "platforms": {
        "ctrip": {"type": "ota", "description": "携程旅行 — 国内最大OTA平台", "active": True},
        "qunar": {"type": "ota", "description": "去哪儿网 — 机票比价聚合平台", "active": True},
        "fliggy": {"type": "ota", "description": "飞猪旅行 — 阿里系OTA平台", "active": True},
        "meituan_travel": {"type": "ota", "description": "美团旅行 — 本地生活延伸差旅", "active": True},
        "airline_direct": {"type": "direct", "description": "航空公司官网直销渠道", "active": True},
    },
    "jobs": [],
    "approvals": [],
    "bookings": [],
    "outputs": [],
    "processing_log": [],
    "job_counter": 1,
    "approval_counter": 1,
    "booking_counter": 1,
    "output_counter": 1,
    "step_counter": 1,
}

VALID_JOB_TYPES = ("parse_policy", "search_flights", "check_compliance")
VALID_JOB_STATUSES = ("pending", "processing", "completed", "failed")
VALID_APPROVAL_STATUSES = ("pending", "approved", "rejected", "escalated")
VALID_BOOKING_STATUSES = ("pending", "confirmed", "cancelled", "failed")
VALID_OUTPUT_FORMATS = ("markdown", "bullet", "json", "mermaid")
VALID_CABIN_CLASSES = ("economy", "premium_economy", "business", "first")
VALID_DATA_TYPES = ("policy_pdf", "policy_url", "flight_query", "compliance_check")


class TravelCompliancePipelineEnv:
    """
    A travel compliance and booking pipeline environment.

    Models the full closed-loop workflow: ingest company PDF travel policy →
    parse compliance rules → search multi-platform flight prices →
    check compliance → submit approval flow → confirm booking →
    aggregate results and generate structured reports.

    Attributes:
        policies (Dict): Registry of ingested and parsed travel policy documents.
        platforms (Dict): Registry of flight booking platforms available for search.
        jobs (List[Dict]): All pipeline processing jobs (parse, search, compliance check).
        approvals (List[Dict]): Approval requests and their current status.
        bookings (List[Dict]): Confirmed or pending flight bookings.
        outputs (List[Dict]): Generated output reports and summaries.
        processing_log (List[Dict]): Audit log of all pipeline operations.
        job_counter (int): Auto-incrementing job ID counter.
        approval_counter (int): Auto-incrementing approval ID counter.
        booking_counter (int): Auto-incrementing booking ID counter.
        output_counter (int): Auto-incrementing output ID counter.
    """

    def __init__(self):
        self.policies: Dict[str, Dict[str, Any]]
        self.platforms: Dict[str, Dict[str, Any]]
        self.jobs: List[Dict[str, Any]]
        self.approvals: List[Dict[str, Any]]
        self.bookings: List[Dict[str, Any]]
        self.outputs: List[Dict[str, Any]]
        self.processing_log: List[Dict[str, Any]]
        self.job_counter: int
        self.approval_counter: int
        self.booking_counter: int
        self.output_counter: int
        self.step_counter: int
        self._api_description = (
            "This tool provides a travel compliance and booking pipeline that covers "
            "PDF policy ingestion and parsing, multi-platform flight price search, "
            "policy compliance checking, approval workflow submission, and booking confirmation."
        )

    def _load_scenario(self, scenario: dict, long_context: bool = False) -> None:
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_STATE)
        self.policies = scenario.get("policies", DEFAULT_STATE_COPY["policies"])
        self.platforms = scenario.get("platforms", DEFAULT_STATE_COPY["platforms"])
        self.jobs = scenario.get("jobs", DEFAULT_STATE_COPY["jobs"])
        self.approvals = scenario.get("approvals", DEFAULT_STATE_COPY["approvals"])
        self.bookings = scenario.get("bookings", DEFAULT_STATE_COPY["bookings"])
        self.outputs = scenario.get("outputs", DEFAULT_STATE_COPY["outputs"])
        self.processing_log = scenario.get("processing_log", DEFAULT_STATE_COPY["processing_log"])
        self.job_counter = scenario.get("job_counter", DEFAULT_STATE_COPY["job_counter"])
        self.approval_counter = scenario.get("approval_counter", DEFAULT_STATE_COPY["approval_counter"])
        self.booking_counter = scenario.get("booking_counter", DEFAULT_STATE_COPY["booking_counter"])
        self.output_counter = scenario.get("output_counter", DEFAULT_STATE_COPY["output_counter"])
        self.step_counter = scenario.get("step_counter", DEFAULT_STATE_COPY["step_counter"])

    def get_env_state(self) -> dict:
        """
        Return the current internal state of the environment.

        Returns:
            dict: All environment state variables including policies, platforms,
                  jobs, approvals, bookings, outputs, processing log, and counters.
        """
        return {
            "policies": self.policies,
            "platforms": self.platforms,
            "jobs": self.jobs,
            "approvals": self.approvals,
            "bookings": self.bookings,
            "outputs": self.outputs,
            "processing_log": self.processing_log,
            "job_counter": self.job_counter,
            "approval_counter": self.approval_counter,
            "booking_counter": self.booking_counter,
            "output_counter": self.output_counter,
            "step_counter": self.step_counter,
        }

    # ── Policy management ────────────────────────────────────────────────

    def ingest_policy(self, name: str, source: str, data_type: str = "policy_pdf") -> Dict[str, Any]:
        """
        Ingest a company travel policy document into the pipeline.

        Registers the policy document as a pending parse job. The document
        must be processed via process_policy() before its rules become active.

        Args:
            name (str): Unique policy identifier (e.g. 'q3_travel_policy').
            source (str): File path or URL of the policy document (e.g. 'policy_v4.pdf').
            data_type (str): Type of policy source. Must be one of: policy_pdf, policy_url.
                             Defaults to 'policy_pdf'.

        Returns:
            job_id (int): Job ID for the parse job created for this policy.
            policy (Dict): The registered policy entry with status 'pending'.
        """
        if data_type not in ("policy_pdf", "policy_url"):
            return {"error": f"Invalid data_type '{data_type}'. Must be one of: policy_pdf, policy_url."}
        if name in self.policies:
            return {"error": f"Policy '{name}' already exists. Use a different name or remove the existing one first."}

        job_id = self.job_counter
        self.job_counter += 1

        job = {
            "job_id": job_id,
            "data": source,
            "data_type": data_type,
            "job_type": "parse_policy",
            "policy_name": name,
            "status": "pending",
            "result": None,
            "processed_at": None,
        }
        self.jobs.append(job)

        self.policies[name] = {
            "source": source,
            "type": data_type,
            "active": False,
            "rules": {},
            "parse_job_id": job_id,
            "parsed_at": None,
        }

        self._log("policy_ingested", {"name": name, "source": source, "job_id": job_id})
        return {"job_id": job_id, "policy": {"name": name, **self.policies[name]}}

    def process_policy(self, job_id: int) -> Dict[str, Any]:
        """
        Parse an ingested policy document to extract compliance rules.

        Simulates PDF/URL parsing to extract structured travel rules such as
        price caps, allowed cabin classes, advance booking requirements, and
        approval thresholds. Activates the policy upon successful parsing.

        Args:
            job_id (int): The job ID returned by ingest_policy().

        Returns:
            job_id (int): The processed job ID.
            status (str): Processing status ('completed' or 'failed').
            rules (Dict): Extracted compliance rules from the policy document.
        """
        job = self._find_job(job_id)
        if not job:
            return {"error": f"Job ID {job_id} not found."}
        if job["job_type"] != "parse_policy":
            return {"error": f"Job {job_id} is not a parse_policy job (type={job['job_type']})."}
        if job["status"] not in ("pending", "failed"):
            return {"error": f"Job {job_id} is already {job['status']}. Re-ingest the policy to reprocess."}

        job["status"] = "processing"
        self._log("policy_processing_started", {"job_id": job_id})

        rules = self._simulate_policy_parse(job["data"], job["data_type"])
        job["status"] = "completed"
        job["result"] = rules
        job["processed_at"] = f"t+{job_id}"

        policy_name = job.get("policy_name")
        if policy_name and policy_name in self.policies:
            self.policies[policy_name]["rules"] = rules
            self.policies[policy_name]["active"] = True
            self.policies[policy_name]["parsed_at"] = f"t+{job_id}"

        self._log("policy_processing_completed", {"job_id": job_id, "policy_name": policy_name, "rule_count": len(rules)})
        return {"job_id": job_id, "status": "completed", "rules": rules}

    def list_policies(self, active_only: bool = False) -> Dict[str, List[Dict[str, Any]]]:
        """
        List all registered travel policy documents.

        Args:
            active_only (bool): If True, return only successfully parsed and active policies.
                                Defaults to False.

        Returns:
            policies (List[Dict]): Policy summaries with name, source, active status,
                                   and number of extracted rules.
        """
        result = []
        for name, meta in self.policies.items():
            if active_only and not meta.get("active"):
                continue
            result.append({
                "name": name,
                "source": meta["source"],
                "type": meta["type"],
                "active": meta["active"],
                "rule_count": len(meta.get("rules", {})),
                "parsed_at": meta.get("parsed_at"),
            })
        return {"policies": result}

    def add_platform(self, name: str, platform_type: str, description: str = "") -> Dict[str, Any]:
        """
        Register a new flight booking platform for price search.

        Args:
            name (str): Unique platform identifier (e.g. 'tongcheng').
            platform_type (str): Platform category (e.g. 'ota', 'direct', 'corporate').
            description (str): Human-readable description of the platform. Defaults to ''.

        Returns:
            platform (Dict): The registered platform entry.
        """
        if name in self.platforms:
            return {"error": f"Platform '{name}' already exists."}
        self.platforms[name] = {"type": platform_type, "description": description, "active": True}
        self._log("platform_added", {"name": name, "platform_type": platform_type})
        return {"platform": {"name": name, **self.platforms[name]}}

    def list_platforms(self, platform_type: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        List registered flight booking platforms, optionally filtered by type.

        Args:
            platform_type (str): [Optional] Filter by platform type (e.g. 'ota', 'direct').

        Returns:
            platforms (List[Dict]): Matching platform entries with name, type, and active status.
        """
        result = []
        for name, meta in self.platforms.items():
            if platform_type and meta["type"] != platform_type:
                continue
            result.append({"name": name, "type": meta["type"], "description": meta["description"], "active": meta["active"]})
        return {"platforms": result}

    # ── Flight search ────────────────────────────────────────────────────

    def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        cabin_class: str = "economy",
        platforms: Optional[List[str]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Search for flight prices across multiple booking platforms.

        Creates a search job and immediately executes it, returning ranked
        flight options from all specified platforms. Results include price,
        cabin class, airline, and platform source for downstream compliance checking.

        Args:
            origin (str): IATA departure airport code (e.g. 'PEK', 'SHA').
            destination (str): IATA arrival airport code (e.g. 'CAN', 'CTU').
            departure_date (str): Departure date in YYYY-MM-DD format.
            cabin_class (str): Requested cabin class. Must be one of:
                               economy, premium_economy, business, first.
                               Defaults to 'economy'.
            platforms (List[str]): [Optional] Platform names to search. Defaults to all active platforms.
            params (Dict): [Optional] Additional search parameters:
                - max_results (int): Max results per platform. Defaults to 5.
                - return_date (str): Return date for round-trip search.
                - passengers (int): Number of passengers. Defaults to 1.

        Returns:
            job_id (int): Job ID for this search, usable in check_compliance() and aggregate().
            status (str): 'completed' if search succeeded.
            result (Dict): Search results with flight options ranked by price.
        """
        if cabin_class not in VALID_CABIN_CLASSES:
            return {"error": f"Invalid cabin_class '{cabin_class}'. Must be one of: {', '.join(VALID_CABIN_CLASSES)}."}

        target_platforms = platforms or [n for n, m in self.platforms.items() if m["active"]]
        invalid = [p for p in target_platforms if p not in self.platforms]
        if invalid:
            return {"error": f"Unknown platforms: {', '.join(invalid)}. Register them first with add_platform()."}

        if not origin or not destination:
            return {"error": "Both 'origin' and 'destination' airport codes are required."}
        if not departure_date:
            return {"error": "'departure_date' is required in YYYY-MM-DD format."}

        job_id = self.job_counter
        self.job_counter += 1
        params = params or {}

        job = {
            "job_id": job_id,
            "data": f"{origin}->{destination} on {departure_date}",
            "data_type": "flight_query",
            "job_type": "search_flights",
            "origin": origin,
            "destination": destination,
            "departure_date": departure_date,
            "cabin_class": cabin_class,
            "platforms": target_platforms,
            "status": "processing",
            "result": None,
            "processed_at": None,
        }
        self.jobs.append(job)
        self._log("flight_search_started", {"job_id": job_id, "route": job["data"], "cabin_class": cabin_class})

        result = self._simulate_flight_search(origin, destination, departure_date, cabin_class, target_platforms, params)
        job["status"] = "completed"
        job["result"] = result
        job["processed_at"] = f"t+{job_id}"

        self._log("flight_search_completed", {"job_id": job_id, "total_options": result.get("total_options", 0)})
        return {"job_id": job_id, "status": "completed", "result": result}

    # ── Compliance checking ──────────────────────────────────────────────

    def check_compliance(
        self,
        job_id: int,
        policy_name: str,
        traveler_id: str,
        trip_purpose: str = "",
    ) -> Dict[str, Any]:
        """
        Check flight search results against the active travel policy rules.

        Evaluates each flight option from a completed search job against the
        specified policy's rules (price caps, cabin restrictions, advance booking
        requirements). Tags each option as compliant or non-compliant with reasons.
        Creates a compliance-check job for downstream approval and booking steps.

        Args:
            job_id (int): Job ID of a completed search_flights job.
            policy_name (str): Name of the active policy to check against.
            traveler_id (str): Employee or traveler identifier (e.g. 'EMP-001').
            trip_purpose (str): Business purpose of the trip (e.g. 'client meeting Q3').
                                Defaults to ''.

        Returns:
            compliance_job_id (int): New job ID for this compliance check result.
            status (str): 'completed' if check succeeded.
            result (Dict): Compliance evaluation with compliant and non-compliant options,
                           recommended option, and required approval level.
        """
        search_job = self._find_job(job_id)
        if not search_job:
            return {"error": f"Job ID {job_id} not found."}
        if search_job["job_type"] != "search_flights":
            return {"error": f"Job {job_id} is not a search_flights job (type={search_job['job_type']})."}
        if search_job["status"] != "completed":
            return {"error": f"Job {job_id} is not completed (status={search_job['status']}). Run search_flights first."}

        if policy_name not in self.policies:
            return {"error": f"Policy '{policy_name}' not found. Ingest and process it first."}
        if not self.policies[policy_name]["active"]:
            return {"error": f"Policy '{policy_name}' is not active. Process it with process_policy() first."}

        if not traveler_id:
            return {"error": "'traveler_id' is required for compliance checking."}

        compliance_job_id = self.job_counter
        self.job_counter += 1

        compliance_job = {
            "job_id": compliance_job_id,
            "data": f"compliance check for job {job_id}",
            "data_type": "compliance_check",
            "job_type": "check_compliance",
            "search_job_id": job_id,
            "policy_name": policy_name,
            "traveler_id": traveler_id,
            "trip_purpose": trip_purpose,
            "status": "processing",
            "result": None,
            "processed_at": None,
        }
        self.jobs.append(compliance_job)
        self._log("compliance_check_started", {"compliance_job_id": compliance_job_id, "search_job_id": job_id, "policy_name": policy_name})

        rules = self.policies[policy_name]["rules"]
        flight_options = search_job["result"].get("options", [])
        result = self._simulate_compliance_check(flight_options, rules, traveler_id, trip_purpose)

        compliance_job["status"] = "completed"
        compliance_job["result"] = result
        compliance_job["processed_at"] = f"t+{compliance_job_id}"

        self._log("compliance_check_completed", {
            "compliance_job_id": compliance_job_id,
            "compliant_count": result.get("compliant_count", 0),
            "approval_required": result.get("approval_required"),
        })
        return {"compliance_job_id": compliance_job_id, "status": "completed", "result": result}

    # ── Approval workflow ────────────────────────────────────────────────

    def submit_approval(
        self,
        compliance_job_id: int,
        selected_option_id: str,
        approver_id: str,
        notes: str = "",
    ) -> Dict[str, Any]:
        """
        Submit an approval request for a selected flight option.

        Creates an approval record based on the compliance check result.
        If the selected option is fully compliant and below the approval threshold,
        the request may be auto-approved. Otherwise it enters the approval queue
        for the designated approver.

        Args:
            compliance_job_id (int): Job ID of a completed check_compliance job.
            selected_option_id (str): The flight option ID chosen by the traveler
                                      (from compliance check result options).
            approver_id (str): Employee ID of the designated approver (e.g. 'MGR-042').
            notes (str): Optional justification or notes for the approval request.
                         Defaults to ''.

        Returns:
            approval_id (int): Unique approval request identifier.
            approval (Dict): The created approval record with status and approval level.
        """
        compliance_job = self._find_job(compliance_job_id)
        if not compliance_job:
            return {"error": f"Job ID {compliance_job_id} not found."}
        if compliance_job["job_type"] != "check_compliance":
            return {"error": f"Job {compliance_job_id} is not a check_compliance job."}
        if compliance_job["status"] != "completed":
            return {"error": f"Compliance job {compliance_job_id} is not completed. Run check_compliance first."}

        if not selected_option_id:
            return {"error": "'selected_option_id' is required."}
        if not approver_id:
            return {"error": "'approver_id' is required."}

        result = compliance_job["result"]
        all_options = result.get("compliant_options", []) + result.get("non_compliant_options", [])
        selected = next((o for o in all_options if o.get("option_id") == selected_option_id), None)
        if not selected:
            return {"error": f"Option ID '{selected_option_id}' not found in compliance check results."}

        approval_id = self.approval_counter
        self.approval_counter += 1

        approval_level = result.get("approval_required", "none")
        is_compliant = selected.get("compliant", False)
        price = selected.get("price", 0)

        auto_approve_threshold = result.get("auto_approve_threshold", 1000)
        auto_approved = is_compliant and price <= auto_approve_threshold

        approval = {
            "approval_id": approval_id,
            "compliance_job_id": compliance_job_id,
            "traveler_id": compliance_job.get("traveler_id"),
            "selected_option_id": selected_option_id,
            "selected_option": selected,
            "approver_id": approver_id,
            "approval_level": approval_level,
            "is_compliant": is_compliant,
            "notes": notes,
            "status": "approved" if auto_approved else "pending",
            "auto_approved": auto_approved,
            "created_at": f"t+{approval_id}",
            "resolved_at": f"t+{approval_id}" if auto_approved else None,
        }
        self.approvals.append(approval)
        self._log("approval_submitted", {
            "approval_id": approval_id,
            "auto_approved": auto_approved,
            "approval_level": approval_level,
        })
        return {"approval_id": approval_id, "approval": approval}

    def resolve_approval(
        self,
        approval_id: int,
        decision: str,
        resolver_id: str,
        reason: str = "",
    ) -> Dict[str, Any]:
        """
        Resolve a pending approval request with an approve or reject decision.

        Only pending approvals can be resolved. Approved requests become eligible
        for booking via book_flight(). Rejected requests terminate the workflow.

        Args:
            approval_id (int): The approval ID returned by submit_approval().
            decision (str): Resolution decision. Must be one of: 'approved', 'rejected', 'escalated'.
            resolver_id (str): Employee ID of the person resolving the approval.
            reason (str): Explanation for the decision. Defaults to ''.

        Returns:
            approval_id (int): The resolved approval ID.
            status (str): New approval status after resolution.
            approval (Dict): Updated approval record.
        """
        if decision not in ("approved", "rejected", "escalated"):
            return {"error": f"Invalid decision '{decision}'. Must be one of: approved, rejected, escalated."}

        approval = self._find_approval(approval_id)
        if not approval:
            return {"error": f"Approval ID {approval_id} not found."}
        if approval["status"] != "pending":
            return {"error": f"Approval {approval_id} is already {approval['status']} and cannot be resolved again."}
        if not resolver_id:
            return {"error": "'resolver_id' is required."}

        approval["status"] = decision
        approval["resolver_id"] = resolver_id
        approval["resolution_reason"] = reason
        approval["resolved_at"] = f"t+{approval_id}"

        self._log("approval_resolved", {"approval_id": approval_id, "decision": decision, "resolver_id": resolver_id})
        return {"approval_id": approval_id, "status": decision, "approval": approval}

    def list_approvals(self, status: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        List all approval requests, optionally filtered by status.

        Args:
            status (str): [Optional] Filter by approval status.
                          Must be one of: pending, approved, rejected, escalated.

        Returns:
            approvals (List[Dict]): Approval summaries with id, traveler, option, level, and status.
        """
        if status and status not in VALID_APPROVAL_STATUSES:
            return {"error": f"Invalid status '{status}'. Must be one of: {', '.join(VALID_APPROVAL_STATUSES)}."}
        approvals = self.approvals
        if status:
            approvals = [a for a in approvals if a["status"] == status]
        summaries = [
            {
                "approval_id": a["approval_id"],
                "traveler_id": a.get("traveler_id"),
                "selected_option_id": a.get("selected_option_id"),
                "approval_level": a.get("approval_level"),
                "is_compliant": a.get("is_compliant"),
                "auto_approved": a.get("auto_approved"),
                "status": a["status"],
            }
            for a in approvals
        ]
        return {"approvals": summaries}

    # ── Booking ──────────────────────────────────────────────────────────

    def book_flight(
        self,
        approval_id: int,
        passenger_name: str,
        passenger_id: str,
        contact_email: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Confirm a flight booking for an approved travel request.

        Executes the booking against the platform specified in the approved
        flight option. Only approvals with status 'approved' can proceed to booking.
        Generates a booking confirmation record with PNR and ticket details.

        Args:
            approval_id (int): The approval ID with status 'approved'.
            passenger_name (str): Full name of the passenger as on ID document.
            passenger_id (str): Passport or national ID number of the passenger.
            contact_email (str): Contact email for booking confirmation and itinerary.
            params (Dict): [Optional] Additional booking parameters:
                - seat_preference (str): Preferred seat type (e.g. 'window', 'aisle').
                - meal_preference (str): Meal preference code (e.g. 'VGML', 'HNML').
                - loyalty_number (str): Frequent flyer number.

        Returns:
            booking_id (int): Unique booking identifier.
            booking (Dict): Booking confirmation record with PNR, ticket number,
                            flight details, and booking status.
        """
        approval = self._find_approval(approval_id)
        if not approval:
            return {"error": f"Approval ID {approval_id} not found."}
        if approval["status"] != "approved":
            return {"error": f"Approval {approval_id} is not approved (status={approval['status']}). Resolve the approval first."}

        existing_booking = next((b for b in self.bookings if b.get("approval_id") == approval_id), None)
        if existing_booking:
            return {"error": f"Approval {approval_id} has already been booked (booking_id={existing_booking['booking_id']})."}

        if not passenger_name:
            return {"error": "'passenger_name' is required for booking."}
        if not passenger_id:
            return {"error": "'passenger_id' is required for booking."}
        if not contact_email:
            return {"error": "'contact_email' is required for booking."}

        params = params or {}
        booking_id = self.booking_counter
        self.booking_counter += 1

        selected_option = approval.get("selected_option", {})
        booking = self._simulate_booking(booking_id, approval_id, selected_option, passenger_name, passenger_id, contact_email, params)
        self.bookings.append(booking)

        self._log("flight_booked", {
            "booking_id": booking_id,
            "approval_id": approval_id,
            "pnr": booking.get("pnr"),
            "platform": selected_option.get("platform"),
        })
        return {"booking_id": booking_id, "booking": booking}

    def cancel_booking(self, booking_id: int, reason: str = "") -> Dict[str, Any]:
        """
        Cancel a confirmed flight booking.

        Args:
            booking_id (int): The booking ID to cancel.
            reason (str): Reason for cancellation. Defaults to ''.

        Returns:
            booking_id (int): The cancelled booking ID.
            status (str): New booking status ('cancelled').
            refund_eligible (bool): Whether the booking qualifies for a refund.
        """
        booking = self._find_booking(booking_id)
        if not booking:
            return {"error": f"Booking ID {booking_id} not found."}

        booking["status"] = "cancelled"
        booking["cancelled_at"] = f"t{self.step_counter}"
        booking["cancellation_reason"] = reason
        self.step_counter += 1
        return {"booking_id": booking_id, "status": "cancelled", "refund_eligible": True}

    # ── Helper methods ────────────────────────────────────────────────────

    def _find_job(self, job_id: int) -> Optional[Dict[str, Any]]:
        """Find a job by its job_id. Returns None if not found."""
        for job in self.jobs:
            if job["job_id"] == job_id:
                return job
        return None

    def _simulate_policy_parse(self, data: str, data_type: str) -> Dict[str, Any]:
        """Simulate parsing a policy document to extract compliance rules."""
        return {
            "max_domestic_price": 1500,
            "max_international_price": 8000,
            "allowed_cabin_domestic": ["economy", "premium_economy"],
            "allowed_cabin_international": ["economy", "premium_economy", "business"],
            "advance_booking_days": 3,
            "require_approval_above": 1000,
            "require_manager_approval_above": 5000,
            "parse_source": data,
            "parse_type": data_type,
        }

    def _simulate_flight_search(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        cabin_class: str,
        target_platforms: List[str],
        params: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Simulate searching for flights across multiple platforms."""
        options = []
        option_counter = 0
        max_results = params.get("max_results", 5)
        for platform in target_platforms:
            for _ in range(random.randint(2, max_results)):
                option_counter += 1
                price = random.randint(600, 12000)
                options.append({
                    "option_id": f"OPT-{option_counter:03d}",
                    "platform": platform,
                    "airline": random.choice(["CA", "MU", "CZ", "HU", "3U", "MF"]),
                    "flight_number": f"CA{random.randint(1000, 9999)}",
                    "price": price,
                    "cabin_class": cabin_class,
                    "departure_time": f"{departure_date} {random.randint(6, 22):02d}:{random.choice(['00', '15', '30', '45'])}",
                    "arrival_time": f"{departure_date} {random.randint(6, 22):02d}:{random.choice(['00', '15', '30', '45'])}",
                    "duration": f"{random.randint(1, 8)}h {random.choice(['00', '15', '30', '45'])}m",
                    "stops": random.choice([0, 0, 0, 1, 2]),
                })
        options.sort(key=lambda o: o["price"])
        return {
            "total_options": len(options),
            "options": options,
            "search_params": {
                "origin": origin,
                "destination": destination,
                "departure_date": departure_date,
                "cabin_class": cabin_class,
                "platforms_searched": target_platforms,
            },
        }

    def _simulate_compliance_check(
        self,
        flight_options: List[Dict[str, Any]],
        rules: Dict[str, Any],
        traveler_id: str,
        trip_purpose: str,
    ) -> Dict[str, Any]:
        """Simulate checking flight options against compliance rules."""
        compliant_options = []
        non_compliant_options = []
        max_price = rules.get("max_domestic_price", 1500)
        allowed_cabins = rules.get("allowed_cabin_domestic", ["economy", "premium_economy"])
        require_approval_above = rules.get("require_approval_above", 1000)
        require_manager_approval_above = rules.get("require_manager_approval_above", 5000)

        for option in flight_options:
            cabin = option.get("cabin_class", "economy")
            price = option.get("price", 0)
            reasons = []
            if price > max_price:
                reasons.append(f"Price {price} exceeds max {max_price}")
            if cabin not in allowed_cabins:
                reasons.append(f"Cabin class '{cabin}' not in allowed: {allowed_cabins}")
            if reasons:
                non_compliant_options.append({
                    **option,
                    "compliant": False,
                    "non_compliance_reasons": reasons,
                })
            else:
                compliant_options.append({
                    **option,
                    "compliant": True,
                    "non_compliance_reasons": [],
                })

        approval_required = "none"
        if compliant_options:
            cheapest = min(o["price"] for o in compliant_options)
            if cheapest >= require_manager_approval_above:
                approval_required = "manager"
            elif cheapest >= require_approval_above:
                approval_required = "standard"

        return {
            "compliant_options": compliant_options,
            "non_compliant_options": non_compliant_options,
            "compliant_count": len(compliant_options),
            "non_compliant_count": len(non_compliant_options),
            "total_checked": len(flight_options),
            "approval_required": approval_required,
            "auto_approve_threshold": require_approval_above,
            "traveler_id": traveler_id,
            "trip_purpose": trip_purpose,
        }

    def _find_approval(self, approval_id: int) -> Optional[Dict[str, Any]]:
        """Find an approval by its approval_id. Returns None if not found."""
        for approval in self.approvals:
            if approval["approval_id"] == approval_id:
                return approval
        return None

    def _simulate_booking(
        self,
        booking_id: int,
        approval_id: int,
        selected_option: Dict[str, Any],
        passenger_name: str,
        passenger_id: str,
        contact_email: str,
        params: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Simulate creating a flight booking."""
        return {
            "booking_id": booking_id,
            "approval_id": approval_id,
            "pnr": f"{random.choice(['PN', 'XB', 'YZ'])}{random.randint(100000, 999999)}",
            "ticket_number": f"999-{random.randint(1000000000, 9999999999)}",
            "passenger_name": passenger_name,
            "passenger_id": passenger_id,
            "contact_email": contact_email,
            "option": selected_option,
            "status": "confirmed",
            "booked_at": f"t+{booking_id}",
            "seat_preference": params.get("seat_preference", ""),
            "meal_preference": params.get("meal_preference", ""),
            "loyalty_number": params.get("loyalty_number", ""),
        }

    def _find_booking(self, booking_id: int) -> Optional[Dict[str, Any]]:
        """Find a booking by its booking_id. Returns None if not found."""
        for booking in self.bookings:
            if booking["booking_id"] == booking_id:
                return booking
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