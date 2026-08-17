"""
Reimbursement Claims Management System Environment API

A reimbursement claims management system designed to record, process, and track claims
submitted by users seeking financial reimbursement for eligible expenses.
"""

from copy import deepcopy
from typing import Dict, List, Optional, Any
from datetime import datetime


DEFAULT_STATE: Dict[str, Any] = {
    "claims": {
        "CLM001": {
            "claim_id": "CLM001",
            "user_id": "USR001",
            "amount": 150.00,
            "submission_date": "2024-01-15T10:30:00",
            "status": "submitted",
            "documentation": ["receipt_001.pdf", "invoice_001.pdf"],
            "review_notes": "",
            "decision_date": None
        },
        "CLM002": {
            "claim_id": "CLM002",
            "user_id": "USR002",
            "amount": 500.00,
            "submission_date": "2024-01-10T14:00:00",
            "status": "approved",
            "documentation": ["receipt_002.pdf"],
            "review_notes": "Verified with finance department",
            "decision_date": "2024-01-12T09:00:00"
        },
        "CLM003": {
            "claim_id": "CLM003",
            "user_id": "USR001",
            "amount": 75.50,
            "submission_date": None,
            "status": "draft",
            "documentation": [],
            "review_notes": "",
            "decision_date": None
        },
        "CLM004": {
            "claim_id": "CLM004",
            "user_id": "USR003",
            "amount": 1200.00,
            "submission_date": "2024-01-08T11:15:00",
            "status": "under review",
            "documentation": ["expense_report.pdf", "approval_email.pdf"],
            "review_notes": "Pending manager approval",
            "decision_date": None
        }
    },
    "users": {
        "USR001": {
            "user_id": "USR001",
            "name": "Alice Johnson",
            "department": "Engineering",
            "role": "employee"
        },
        "USR002": {
            "user_id": "USR002",
            "name": "Bob Smith",
            "department": "Marketing",
            "role": "employee"
        },
        "USR003": {
            "user_id": "USR003",
            "name": "Carol Davis",
            "department": "Finance",
            "role": "manager"
        },
        "USR004": {
            "user_id": "USR004",
            "name": "David Wilson",
            "department": "HR",
            "role": "admin"
        }
    },
    "claim_review_logs": [
        {
            "log_id": "LOG001",
            "claim_id": "CLM001",
            "updated_by": "USR003",
            "old_status": "draft",
            "new_status": "submitted",
            "timestamp": "2024-01-15T10:30:00",
            "comment": "Claim submitted for review"
        },
        {
            "log_id": "LOG002",
            "claim_id": "CLM002",
            "updated_by": "USR003",
            "old_status": "submitted",
            "new_status": "approved",
            "timestamp": "2024-01-12T09:00:00",
            "comment": "Approved after verification"
        },
        {
            "log_id": "LOG003",
            "claim_id": "CLM004",
            "updated_by": "USR003",
            "old_status": "submitted",
            "new_status": "under review",
            "timestamp": "2024-01-09T08:00:00",
            "comment": "Assigned for detailed review"
        }
    ],
    "current_user": "USR003",
    "next_claim_id": 5,
    "next_log_id": 4
}

VALID_STATUSES = ["draft", "submitted", "under review", "approved", "denied", "paid"]


class ReimbursementClaimsManagementSystem:
    """
    A reimbursement claims management system API for recording, processing,
    and tracking claims submitted by users seeking financial reimbursement.
    
    This system maintains claim records with identifiers, amounts, supporting
    documentation, and status indicators. It supports searching, updating,
    and reporting functions for efficient claim handling.
    """
    
    def __init__(self):
        """
        Initialize the Reimbursement Claims Management System.
        
        Declares all state attributes and sets up the API description.
        
        Returns:
            None
        """
        self.claims: Dict[str, Dict[str, Any]] = {}
        self.users: Dict[str, Dict[str, Any]] = {}
        self.claim_review_logs: List[Dict[str, Any]] = []
        self.current_user: str = ""
        self.next_claim_id: int = 1
        self.next_log_id: int = 1
        
        self._api_description = (
            "A reimbursement claims management system for recording, processing, "
            "and tracking expense reimbursement claims with full audit trail support."
        )
    
    def _timestamp(self) -> str:
        """
        Generate a standardized ISO format timestamp string.
        
        Args:
            None
        
        Returns:
            str: Current timestamp in ISO format (YYYY-MM-DDTHH:MM:SS).
        """
        return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    
    def _load_scenario(self, scenario: dict, long_context: bool = False) -> None:
        """
        Load initial state from a scenario dictionary.
        
        Args:
            scenario: Dictionary containing initial state values.
            long_context: Flag for extended context scenarios (not used currently).
        
        Returns:
            None
        """
        if not scenario:
            scenario = {}
        for key in DEFAULT_STATE:
            if key in scenario:
                setattr(self, key, deepcopy(scenario[key]))
            else:
                setattr(self, key, deepcopy(DEFAULT_STATE[key]))
    
    def get_env_state(self) -> Dict[str, Any]:
        """
        Return the complete current state of the environment.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: A dictionary containing all internal state variables:
                - claims: All claim records indexed by claim_id
                - users: All user records indexed by user_id
                - claim_review_logs: List of all status change audit logs
                - current_user: The currently active user ID
                - next_claim_id: Counter for generating new claim IDs
                - next_log_id: Counter for generating new log IDs
        """
        return {
            "claims": deepcopy(self.claims),
            "users": deepcopy(self.users),
            "claim_review_logs": deepcopy(self.claim_review_logs),
            "current_user": self.current_user,
            "next_claim_id": self.next_claim_id,
            "next_log_id": self.next_log_id
        }
    
    # ==================== QUERY OPERATIONS ====================
    
    def get_claim_by_id(self, claim_id: str) -> Dict[str, Any]:
        """
        Retrieve full details of a claim using its unique claim_id.
        
        Args:
            claim_id: The unique identifier of the claim to retrieve.
        
        Returns:
            Dict[str, Any]: The complete claim record including status, amount,
                documentation, and all other fields, or an error dictionary
                if the claim is not found.
        """
        if claim_id not in self.claims:
            return {"error": f"Claim with ID '{claim_id}' not found"}
        return {"claim": deepcopy(self.claims[claim_id])}
    
    def get_claim_status(self, claim_id: str) -> Dict[str, Any]:
        """
        Return only the current status of a claim for quick user inquiries.
        
        Args:
            claim_id: The unique identifier of the claim.
        
        Returns:
            Dict[str, Any]: Dictionary containing claim_id and current status,
                or an error dictionary if the claim is not found.
        """
        if claim_id not in self.claims:
            return {"error": f"Claim with ID '{claim_id}' not found"}
        return {
            "claim_id": claim_id,
            "status": self.claims[claim_id]["status"]
        }
    
    def list_claims_by_user(
        self, user_id: str, status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieve all claims submitted by a specific user, optionally filtered by status.
        
        Args:
            user_id: The unique identifier of the user.
            status: Optional status filter (e.g., "submitted", "approved").
        
        Returns:
            Dict[str, Any]: Dictionary containing a list of matching claims,
                or an error dictionary if the user is not found or status is invalid.
        """
        if user_id not in self.users:
            return {"error": f"User with ID '{user_id}' not found"}
        
        if status is not None and status not in VALID_STATUSES:
            return {"error": f"Invalid status '{status}'. Must be one of: {VALID_STATUSES}"}
        
        claims = []
        for claim in self.claims.values():
            if claim["user_id"] == user_id:
                if status is None or claim["status"] == status:
                    claims.append(deepcopy(claim))
        
        return {"user_id": user_id, "claims": claims, "count": len(claims)}
    
    def list_claims_by_status(self, status: str) -> Dict[str, Any]:
        """
        Retrieve all claims with a specific status for batch processing or reporting.
        
        Args:
            status: The status to filter by (e.g., "submitted", "approved").
        
        Returns:
            Dict[str, Any]: Dictionary containing a list of matching claims,
                or an error dictionary if the status is invalid.
        """
        if status not in VALID_STATUSES:
            return {"error": f"Invalid status '{status}'. Must be one of: {VALID_STATUSES}"}
        
        claims = [
            deepcopy(claim) for claim in self.claims.values()
            if claim["status"] == status
        ]
        
        return {"status": status, "claims": claims, "count": len(claims)}
    
    def get_claim_review_history(self, claim_id: str) -> Dict[str, Any]:
        """
        Retrieve the audit log entries for a given claim.
        
        Args:
            claim_id: The unique identifier of the claim.
        
        Returns:
            Dict[str, Any]: Dictionary containing list of status transitions
                and reviewer comments, or an error dictionary if claim not found.
        """
        if claim_id not in self.claims:
            return {"error": f"Claim with ID '{claim_id}' not found"}
        
        logs = [
            deepcopy(log) for log in self.claim_review_logs
            if log["claim_id"] == claim_id
        ]
        
        return {"claim_id": claim_id, "history": logs, "count": len(logs)}
    
    def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """
        Retrieve user details by user_id for claim association and access control.
        
        Args:
            user_id: The unique identifier of the user.
        
        Returns:
            Dict[str, Any]: Dictionary containing user details (name, department, role),
                or an error dictionary if the user is not found.
        """
        if user_id not in self.users:
            return {"error": f"User with ID '{user_id}' not found"}
        return {"user": deepcopy(self.users[user_id])}
    
    def list_all_users(self) -> Dict[str, Any]:
        """
        Retrieve a list of all registered users in the system.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: Dictionary containing a list of all user records
                and the total count.
        """
        users = [deepcopy(user) for user in self.users.values()]
        return {"users": users, "count": len(users)}
    
    def search_claims_by_date_range(
        self, start_date: str, end_date: str
    ) -> Dict[str, Any]:
        """
        Retrieve claims submitted within a specific date range.
        
        Args:
            start_date: Start of the date range (ISO format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS).
            end_date: End of the date range (ISO format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS).
        
        Returns:
            Dict[str, Any]: Dictionary containing matching claims within the date range,
                or an error dictionary if dates are invalid.
        """
        try:
            if "T" not in start_date:
                start_date = f"{start_date}T00:00:00"
            if "T" not in end_date:
                end_date = f"{end_date}T23:59:59"
            start_dt = datetime.fromisoformat(start_date)
            end_dt = datetime.fromisoformat(end_date)
        except ValueError as e:
            return {"error": f"Invalid date format: {str(e)}. Use ISO format (YYYY-MM-DD)"}
        
        if start_dt > end_dt:
            return {"error": "Start date must be before or equal to end date"}
        
        claims = []
        for claim in self.claims.values():
            if claim["submission_date"] is not None:
                claim_dt = datetime.fromisoformat(claim["submission_date"])
                if start_dt <= claim_dt <= end_dt:
                    claims.append(deepcopy(claim))
        
        return {
            "start_date": start_date,
            "end_date": end_date,
            "claims": claims,
            "count": len(claims)
        }
    
    def get_total_approved_amount(self) -> Dict[str, Any]:
        """
        Sum the total amount of all claims with "approved" status.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: Dictionary containing the total approved amount
                and the count of approved claims.
        """
        total = 0.0
        count = 0
        for claim in self.claims.values():
            if claim["status"] == "approved":
                total += claim["amount"]
                count += 1
        
        return {
            "total_approved_amount": round(total, 2),
            "approved_claims_count": count
        }
    
    # ==================== STATE CHANGE OPERATIONS ====================
    
    def create_new_claim(self, user_id: str, amount: float) -> Dict[str, Any]:
        """
        Initialize a new claim in "draft" status with a unique claim_id.
        
        Args:
            user_id: The user ID of the claim submitter.
            amount: The initial claim amount (must be positive).
        
        Returns:
            Dict[str, Any]: Dictionary containing the new claim details,
                or an error dictionary if validation fails.
        """
        if user_id not in self.users:
            return {"error": f"User with ID '{user_id}' not found"}
        
        if not isinstance(amount, (int, float)) or amount <= 0:
            return {"error": "Amount must be a positive number"}
        
        claim_id = f"CLM{self.next_claim_id:03d}"
        self.next_claim_id += 1
        
        new_claim = {
            "claim_id": claim_id,
            "user_id": user_id,
            "amount": float(amount),
            "submission_date": None,
            "status": "draft",
            "documentation": [],
            "review_notes": "",
            "decision_date": None
        }
        
        self.claims[claim_id] = new_claim
        
        return {"success": True, "claim": deepcopy(new_claim)}
    
    def update_claim_amount(self, claim_id: str, new_amount: float) -> Dict[str, Any]:
        """
        Modify the claim amount, ensuring it remains a positive number.
        
        Args:
            claim_id: The unique identifier of the claim.
            new_amount: The new amount to set (must be positive).
        
        Returns:
            Dict[str, Any]: Dictionary confirming the update with old and new amounts,
                or an error dictionary if validation fails.
        """
        if claim_id not in self.claims:
            return {"error": f"Claim with ID '{claim_id}' not found"}
        
        if not isinstance(new_amount, (int, float)) or new_amount <= 0:
            return {"error": "Amount must be a positive number"}
        
        claim = self.claims[claim_id]
        
        if claim["status"] not in ["draft", "submitted"]:
            return {"error": f"Cannot update amount for claim with status '{claim['status']}'"}
        
        old_amount = claim["amount"]
        claim["amount"] = float(new_amount)
        
        return {
            "success": True,
            "claim_id": claim_id,
            "old_amount": old_amount,
            "new_amount": float(new_amount)
        }
    
    def attach_documentation(
        self, claim_id: str, documents: List[str]
    ) -> Dict[str, Any]:
        """
        Add one or more documents to a claim's documentation list.
        
        Args:
            claim_id: The unique identifier of the claim.
            documents: List of document names/paths to attach.
        
        Returns:
            Dict[str, Any]: Dictionary confirming attachment with updated documentation list,
                or an error dictionary if validation fails.
        """
        if claim_id not in self.claims:
            return {"error": f"Claim with ID '{claim_id}' not found"}
        
        if not documents or not isinstance(documents, list):
            return {"error": "Documents must be a non-empty list"}
        
        claim = self.claims[claim_id]
        
        if claim["status"] not in ["draft", "submitted"]:
            return {"error": f"Cannot attach documents to claim with status '{claim['status']}'"}
        
        for doc in documents:
            if doc not in claim["documentation"]:
                claim["documentation"].append(doc)
        
        return {
            "success": True,
            "claim_id": claim_id,
            "documentation": deepcopy(claim["documentation"])
        }
    
    def submit_claim(self, claim_id: str) -> Dict[str, Any]:
        """
        Transition a claim from "draft" to "submitted".
        
        Documentation must be attached and amount must be positive before submission.
        
        Args:
            claim_id: The unique identifier of the claim.
        
        Returns:
            Dict[str, Any]: Dictionary confirming submission with timestamp,
                or an error dictionary if validation fails.
        """
        if claim_id not in self.claims:
            return {"error": f"Claim with ID '{claim_id}' not found"}
        
        claim = self.claims[claim_id]
        
        if claim["status"] != "draft":
            return {"error": f"Only claims with 'draft' status can be submitted. Current status: '{claim['status']}'"}
        
        if not claim["documentation"]:
            return {"error": "Documentation must be attached before submitting a claim"}
        
        if claim["amount"] <= 0:
            return {"error": "Claim amount must be positive before submission"}
        
        old_status = claim["status"]
        claim["status"] = "submitted"
        claim["submission_date"] = self._timestamp()
        
        self._log_status_change(
            claim_id=claim_id,
            old_status=old_status,
            new_status="submitted",
            comment="Claim submitted for review"
        )
        
        return {
            "success": True,
            "claim_id": claim_id,
            "status": "submitted",
            "submission_date": claim["submission_date"]
        }
    
    def update_claim_status(
        self, claim_id: str, new_status: str, comment: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Change the claim status with validation and logging.
        
        Args:
            claim_id: The unique identifier of the claim.
            new_status: The target status to transition to.
            comment: Optional comment explaining the status change.
        
        Returns:
            Dict[str, Any]: Dictionary confirming the status change,
                or an error dictionary if validation fails.
        """
        if claim_id not in self.claims:
            return {"error": f"Claim with ID '{claim_id}' not found"}
        
        if new_status not in VALID_STATUSES:
            return {"error": f"Invalid status '{new_status}'. Must be one of: {VALID_STATUSES}"}
        
        claim = self.claims[claim_id]
        old_status = claim["status"]
        
        valid_transitions = {
            "draft": ["submitted"],
            "submitted": ["under review", "approved", "denied"],
            "under review": ["approved", "denied"],
            "approved": ["paid"],
            "denied": [],
            "paid": []
        }
        
        if new_status not in valid_transitions.get(old_status, []):
            return {
                "error": f"Invalid status transition from '{old_status}' to '{new_status}'. "
                         f"Allowed transitions: {valid_transitions.get(old_status, [])}"
            }
        
        if old_status == "draft" and new_status == "submitted":
            if not claim["documentation"]:
                return {"error": "Documentation must be attached before submitting"}
        
        claim["status"] = new_status
        
        if new_status in ["approved", "denied"]:
            claim["decision_date"] = self._timestamp()
        
        self._log_status_change(
            claim_id=claim_id,
            old_status=old_status,
            new_status=new_status,
            comment=comment or f"Status changed to {new_status}"
        )
        
        return {
            "success": True,
            "claim_id": claim_id,
            "old_status": old_status,
            "new_status": new_status
        }
    
    def approve_claim(
        self, claim_id: str, comment: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Set claim status to "approved" if current status is valid.
        
        Args:
            claim_id: The unique identifier of the claim.
            comment: Optional comment explaining the approval.
        
        Returns:
            Dict[str, Any]: Dictionary confirming approval with decision date,
                or an error dictionary if validation fails.
        """
        if claim_id not in self.claims:
            return {"error": f"Claim with ID '{claim_id}' not found"}
        
        claim = self.claims[claim_id]
        
        if claim["status"] not in ["submitted", "under review"]:
            return {
                "error": f"Cannot approve claim with status '{claim['status']}'. "
                         "Only 'submitted' or 'under review' claims can be approved"
            }
        
        old_status = claim["status"]
        claim["status"] = "approved"
        claim["decision_date"] = self._timestamp()
        
        self._log_status_change(
            claim_id=claim_id,
            old_status=old_status,
            new_status="approved",
            comment=comment or "Claim approved"
        )
        
        return {
            "success": True,
            "claim_id": claim_id,
            "status": "approved",
            "decision_date": claim["decision_date"]
        }
    
    def deny_claim(self, claim_id: str, comment: str) -> Dict[str, Any]:
        """
        Set claim status to "denied" with a required comment.
        
        Args:
            claim_id: The unique identifier of the claim.
            comment: Required comment explaining the denial reason.
        
        Returns:
            Dict[str, Any]: Dictionary confirming denial with decision date,
                or an error dictionary if validation fails.
        """
        if claim_id not in self.claims:
            return {"error": f"Claim with ID '{claim_id}' not found"}
        
        if not comment or not comment.strip():
            return {"error": "A comment is required when denying a claim"}
        
        claim = self.claims[claim_id]
        
        if claim["status"] not in ["submitted", "under review"]:
            return {
                "error": f"Cannot deny claim with status '{claim['status']}'. "
                         "Only 'submitted' or 'under review' claims can be denied"
            }
        
        old_status = claim["status"]
        claim["status"] = "denied"
        claim["decision_date"] = self._timestamp()
        claim["review_notes"] = comment
        
        self._log_status_change(
            claim_id=claim_id,
            old_status=old_status,
            new_status="denied",
            comment=comment
        )
        
        return {
            "success": True,
            "claim_id": claim_id,
            "status": "denied",
            "decision_date": claim["decision_date"],
            "reason": comment
        }
    
    def mark_claim_as_paid(self, claim_id: str) -> Dict[str, Any]:
        """
        Update status to "paid" only if the claim was previously "approved".
        
        Args:
            claim_id: The unique identifier of the claim.
        
        Returns:
            Dict[str, Any]: Dictionary confirming payment status,
                or an error dictionary if validation fails.
        """
        if claim_id not in self.claims:
            return {"error": f"Claim with ID '{claim_id}' not found"}
        
        claim = self.claims[claim_id]
        
        if claim["status"] != "approved":
            return {
                "error": f"Cannot mark claim as paid with status '{claim['status']}'. "
                         "Only 'approved' claims can be marked as paid"
            }
        
        old_status = claim["status"]
        claim["status"] = "paid"
        
        self._log_status_change(
            claim_id=claim_id,
            old_status=old_status,
            new_status="paid",
            comment="Payment processed"
        )
        
        return {
            "success": True,
            "claim_id": claim_id,
            "status": "paid",
            "payment_timestamp": self._timestamp()
        }
    
    def add_review_notes(self, claim_id: str, notes: str) -> Dict[str, Any]:
        """
        Append or update reviewer notes during claim evaluation.
        
        Args:
            claim_id: The unique identifier of the claim.
            notes: The review notes to add.
        
        Returns:
            Dict[str, Any]: Dictionary confirming notes were added,
                or an error dictionary if validation fails.
        """
        if claim_id not in self.claims:
            return {"error": f"Claim with ID '{claim_id}' not found"}
        
        if not notes or not notes.strip():
            return {"error": "Notes cannot be empty"}
        
        claim = self.claims[claim_id]
        
        if claim["review_notes"]:
            claim["review_notes"] = f"{claim['review_notes']}\n{notes}"
        else:
            claim["review_notes"] = notes
        
        return {
            "success": True,
            "claim_id": claim_id,
            "review_notes": claim["review_notes"]
        }
    
    def log_status_change(
        self,
        claim_id: str,
        old_status: str,
        new_status: str,
        comment: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Manually record a status transition in the ClaimReviewLog.
        
        Args:
            claim_id: The unique identifier of the claim.
            old_status: The previous status before the change.
            new_status: The new status after the change.
            comment: Optional comment describing the change.
        
        Returns:
            Dict[str, Any]: Dictionary confirming the log entry was created,
                or an error dictionary if validation fails.
        """
        if claim_id not in self.claims:
            return {"error": f"Claim with ID '{claim_id}' not found"}
        
        if old_status not in VALID_STATUSES:
            return {"error": f"Invalid old_status '{old_status}'"}
        
        if new_status not in VALID_STATUSES:
            return {"error": f"Invalid new_status '{new_status}'"}
        
        log_entry = self._log_status_change(claim_id, old_status, new_status, comment)
        
        return {"success": True, "log_entry": log_entry}
    
    def _log_status_change(
        self,
        claim_id: str,
        old_status: str,
        new_status: str,
        comment: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Internal method to record a status transition in the ClaimReviewLog.
        
        Args:
            claim_id: The unique identifier of the claim.
            old_status: The previous status before the change.
            new_status: The new status after the change.
            comment: Optional comment describing the change.
        
        Returns:
            Dict[str, Any]: The created log entry.
        """
        log_id = f"LOG{self.next_log_id:03d}"
        self.next_log_id += 1
        
        log_entry = {
            "log_id": log_id,
            "claim_id": claim_id,
            "updated_by": self.current_user,
            "old_status": old_status,
            "new_status": new_status,
            "timestamp": self._timestamp(),
            "comment": comment or ""
        }
        
        self.claim_review_logs.append(log_entry)
        
        return log_entry


__TEST_CASES__ = [
    {
        "name": "Complete claim lifecycle: create, document, submit, approve, and pay",
        "steps": [
            {"tool_call": "create_new_claim(user_id='USR001', amount=250.00)", "expect_success": True},
            {"tool_call": "attach_documentation(claim_id='CLM005', documents=['receipt.pdf'])", "expect_success": True},
            {"tool_call": "submit_claim(claim_id='CLM005')", "expect_success": True},
            {"tool_call": "approve_claim(claim_id='CLM005', comment='Expenses verified')", "expect_success": True},
            {"tool_call": "mark_claim_as_paid(claim_id='CLM005')", "expect_success": True},
            {"tool_call": "get_claim_review_history(claim_id='CLM005')", "expect_success": True}
        ]
    },
    {
        "name": "Query operations test",
        "steps": [
            {"tool_call": "get_claim_by_id(claim_id='CLM001')", "expect_success": True},
            {"tool_call": "get_claim_status(claim_id='CLM002')", "expect_success": True},
            {"tool_call": "list_claims_by_user(user_id='USR001')", "expect_success": True},
            {"tool_call": "list_claims_by_status(status='approved')", "expect_success": True},
            {"tool_call": "get_total_approved_amount()", "expect_success": True},
            {"tool_call": "list_all_users()", "expect_success": True}
        ]
    },
    {
        "name": "Claim rejection and resubmission flow",
        "steps": [
            {"tool_call": "create_new_claim(user_id='USR002', amount=5000.00)", "expect_success": True},
            {"tool_call": "attach_documentation(claim_id='CLM006', documents=['invoice.pdf'])", "expect_success": True},
            {"tool_call": "submit_claim(claim_id='CLM006')", "expect_success": True},
            {"tool_call": "reject_claim(claim_id='CLM006', reason='Amount exceeds policy limit')", "expect_success": True},
            {"tool_call": "update_claim_amount(claim_id='CLM006', new_amount=1500.00)", "expect_success": True},
            {"tool_call": "submit_claim(claim_id='CLM006')", "expect_success": True},
            {"tool_call": "approve_claim(claim_id='CLM006', comment='Revised amount approved')", "expect_success": True}
        ]
    },
    {
        "name": "Error handling: invalid operations",
        "steps": [
            {"tool_call": "get_claim_by_id(claim_id='CLM999')", "expect_success": False},
            {"tool_call": "submit_claim(claim_id='CLM999')", "expect_success": False},
            {"tool_call": "approve_claim(claim_id='CLM001', comment='Test')", "expect_success": False},
            {"tool_call": "create_new_claim(user_id='USR001', amount=-100.00)", "expect_success": False},
            {"tool_call": "mark_claim_as_paid(claim_id='CLM001')", "expect_success": False}
        ]
    },
    {
        "name": "Documentation management",
        "steps": [
            {"tool_call": "create_new_claim(user_id='USR003', amount=300.00)", "expect_success": True},
            {"tool_call": "attach_documentation(claim_id='CLM007', documents=['receipt1.pdf', 'receipt2.pdf'])", "expect_success": True},
            {"tool_call": "get_claim_documents(claim_id='CLM007')", "expect_success": True},
            {"tool_call": "remove_documentation(claim_id='CLM007', document='receipt1.pdf')", "expect_success": True},
            {"tool_call": "get_claim_documents(claim_id='CLM007')", "expect_success": True}
        ]
    },
    {
        "name": "Bulk operations and reporting",
        "steps": [
            {"tool_call": "get_claims_summary()", "expect_success": True},
            {"tool_call": "list_pending_claims()", "expect_success": True},
            {"tool_call": "get_user_total_claims(user_id='USR001')", "expect_success": True},
            {"tool_call": "export_claims_report(format='json')", "expect_success": True}
        ]
    },
    {
        "name": "Claim cancellation flow",
        "steps": [
            {"tool_call": "create_new_claim(user_id='USR001', amount=150.00)", "expect_success": True},
            {"tool_call": "cancel_claim(claim_id='CLM008', reason='Duplicate submission')", "expect_success": True},
            {"tool_call": "get_claim_status(claim_id='CLM008')", "expect_success": True}
        ]
    }
]