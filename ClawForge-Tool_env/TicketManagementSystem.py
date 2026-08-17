from copy import deepcopy
from typing import Dict, List, Optional, Any, Union

DEFAULT_STATE = {
    "ticket_queue": [],
    "ticket_counter": 1,
    "current_user": None,
}

# Predefined users and roles (username -> {"password": ..., "role": ...})
_USERS = {
    "admin":   {"password": "password123", "role": "admin"},
    "user1":   {"password": "password",    "role": "user"},
    "user2":   {"password": "password",    "role": "user"},
    "user3":   {"password": "password",    "role": "user"},
    "user4":   {"password": "password",    "role": "user"},
    "user5":   {"password": "password",    "role": "user"},
    "user6":   {"password": "password",    "role": "user"},
    "userA":   {"password": "password",    "role": "user"},
    "userB":   {"password": "password",    "role": "user"},
}

_VALID_STATUSES = {"Open", "In Progress", "Resolved", "Closed"}


def _deepcopy_ticket(ticket: dict) -> dict:
    return deepcopy(ticket)


def _deepcopy_tickets(tickets: list) -> list:
    return [deepcopy(t) for t in tickets]


class TicketAPI:
    """
    A class representing the Ticket API for managing support tickets.

    Provides methods for creating, retrieving, and managing
    support tickets within a ticketing system. It maintains a queue of
    tickets and handles ticket-related operations such as creation,
    status updates, and retrieval.

    Attributes:
        ticket_queue (List[Dict]): A list of ticket dictionaries.
        ticket_counter (int): A counter for generating unique ticket IDs.
        current_user (Optional[str]): The currently authenticated user.
    """

    def __init__(self):
        self.ticket_queue: List[Dict[str, Any]] = []
        self.ticket_counter: int = 1
        self.current_user: Optional[str] = None
        self._api_description = "This tool belongs to the ticketing system that is part of a company, which allows users to create, view, and manage support business tickets."

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _find_ticket_ref(self, ticket_id: int) -> Optional[Dict]:
        """Return the actual ticket object from the internal queue (no copy)."""
        for ticket in self.ticket_queue:
            if ticket["id"] == ticket_id:
                return ticket
        return None

    def _find_ticket(self, ticket_id: int) -> Optional[Dict]:
        """Return a deep copy of the ticket (for external use)."""
        ref = self._find_ticket_ref(ticket_id)
        return _deepcopy_ticket(ref) if ref else None

    def _require_auth(self) -> bool:
        """Return True if a user is logged in.  Otherwise False."""
        return self.current_user is not None

    def _error_response(self, msg: str) -> Dict:
        return {"success": False, "error": msg}

    def _success_response(self, data: Any = None) -> Dict:
        if data is None:
            return {"success": True}
        if isinstance(data, dict):
            data["success"] = True
            return data
        # For non-dict data (e.g., list), wrap it
        return {"success": True, "data": data}

    # ------------------------------------------------------------------
    # Scenario loading & state
    # ------------------------------------------------------------------
    def _load_scenario(self, scenario: dict, long_context: bool = False) -> None:
        """Load a scenario into the ticket queue (deep‑copied)."""
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_STATE)

        # Deep copy the provided data
        self.ticket_queue = _deepcopy_tickets(scenario.get("ticket_queue", DEFAULT_STATE_COPY["ticket_queue"]))
        self.ticket_counter = scenario.get("ticket_counter", DEFAULT_STATE_COPY["ticket_counter"])
        self.current_user = scenario.get("current_user", DEFAULT_STATE_COPY["current_user"])

        # Calibrate counter to avoid ID collision with existing tickets
        max_id = max((t.get("id", 0) for t in self.ticket_queue), default=0)
        if self.ticket_counter <= max_id:
            self.ticket_counter = max_id + 1

    def get_env_state(self) -> Dict:
        """Return a deep‑copied snapshot of the internal state."""
        return {
            "ticket_queue": _deepcopy_tickets(self.ticket_queue),
            "ticket_counter": self.ticket_counter,
            "current_user": self.current_user,
            "success": True,
        }

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------
    def ticket_login(self, username: str, password: str) -> Dict[str, Union[bool, str]]:
        """
        Authenticate a user.

        Args:
            username: Username.
            password: Password.

        Returns:
            {"success": bool, "error": str?}
        """
        user_info = _USERS.get(username)
        if user_info and user_info["password"] == password:
            self.current_user = username
            return {"success": True}
        return {"success": False, "error": "Invalid username or password."}

    def ticket_get_login_status(self) -> Dict[str, bool]:
        """Return whether a user is currently logged in."""
        return {"username": bool(self.current_user), "success": True}

    def logout(self) -> Dict[str, Union[bool, str]]:
        """Log out the current user."""
        if self.current_user:
            self.current_user = None
            return {"success": True}
        return {"success": False, "error": "No user is currently logged in."}

    # ------------------------------------------------------------------
    # Core ticket operations
    # ------------------------------------------------------------------
    def create_ticket(
        self, title: str, description: str = "", priority: int = 1
    ) -> Dict:
        """Create a new ticket."""
        if not self._require_auth():
            return self._error_response("User not authenticated. Please log in to create a ticket.")
        if not title:
            return self._error_response("Title cannot be empty or None.")
        if not isinstance(priority, int) or isinstance(priority, bool):
            return self._error_response("Priority must be an integer.")
        if priority < 1 or priority > 5:
            return self._error_response("Invalid priority. Priority must be between 1 and 5.")

        ticket = {
            "id": self.ticket_counter,
            "title": title,
            "description": description,
            "status": "Open",
            "priority": priority,
            "created_by": self.current_user,
        }
        self.ticket_queue.append(ticket)
        self.ticket_counter += 1
        return self._success_response(_deepcopy_ticket(ticket))

    def get_ticket(self, ticket_id: int) -> Dict:
        """Retrieve a ticket by ID (deep copy)."""
        if not self._require_auth():
            return self._error_response("User not authenticated. Please log in.")
        ticket = self._find_ticket(ticket_id)
        if not ticket:
            return self._error_response(f"Ticket with ID {ticket_id} not found.")
        return self._success_response(ticket)

    def close_ticket(self, ticket_id: int) -> Dict:
        """Close a ticket."""
        if not self._require_auth():
            return self._error_response("User not authenticated. Please log in.")
        ref = self._find_ticket_ref(ticket_id)
        if not ref:
            return self._error_response(f"Ticket with ID {ticket_id} not found.")
        if ref["status"] == "Closed":
            return self._error_response(f"Ticket with ID {ticket_id} is already closed.")
        ref["status"] = "Closed"
        return self._success_response({"status": f"Ticket {ticket_id} has been closed successfully."})

    def resolve_ticket(self, ticket_id: int, resolution: str) -> Dict:
        """Resolve a ticket."""
        if not self._require_auth():
            return self._error_response("User not authenticated. Please log in.")
        ref = self._find_ticket_ref(ticket_id)
        if not ref:
            return self._error_response(f"Ticket with ID {ticket_id} not found.")
        if ref["status"] == "Resolved":
            return self._error_response(f"Ticket with ID {ticket_id} is already resolved.")
        if ref["status"] not in ("Open", "In Progress"):
            return self._error_response(f"Ticket with ID {ticket_id} can only be resolved from 'Open' or 'In Progress' state.")
        ref["status"] = "Resolved"
        ref["resolution"] = resolution
        return self._success_response({"status": f"Ticket {ticket_id} has been resolved successfully."})

    def edit_ticket(
        self, ticket_id: int, updates: Dict[str, Optional[Union[str, int]]]
    ) -> Dict:
        """Modify an existing ticket."""
        if not self._require_auth():
            return self._error_response("User not authenticated. Please log in.")
        ref = self._find_ticket_ref(ticket_id)
        if not ref:
            return self._error_response(f"Ticket with ID {ticket_id} not found.")

        valid_fields = {"title", "description", "status", "priority"}
        invalid_fields = set(updates.keys()) - valid_fields
        if invalid_fields:
            return self._error_response(f"Invalid fields for update: {', '.join(invalid_fields)}")

        for key, value in updates.items():
            if value is not None:
                if key == "priority":
                    if not isinstance(value, int) or isinstance(value, bool):
                        return self._error_response("Priority must be an integer.")
                    if value < 1 or value > 5:
                        return self._error_response("Invalid priority. Priority must be between 1 and 5.")
                    ref[key] = value
                elif key == "status":
                    # Normalize case to match valid statuses
                    normalized = None
                    for valid in _VALID_STATUSES:
                        if valid.lower() == str(value).lower():
                            normalized = valid
                            break
                    if normalized is None:
                        return self._error_response(f"Invalid status '{value}'. Valid statuses: {', '.join(sorted(_VALID_STATUSES))}")
                    ref[key] = normalized
                else:
                    ref[key] = value

        return self._success_response({"status": f"Ticket {ticket_id} has been updated successfully."})

    def reopen_ticket(self, ticket_id: int, reason: str) -> Dict:
        """Reopen a closed or resolved ticket."""
        if not self._require_auth():
            return self._error_response("User not authenticated. Please log in.")
        if not reason:
            return self._error_response("Reason cannot be empty.")

        ref = self._find_ticket_ref(ticket_id)
        if not ref:
            return self._error_response(f"Ticket with ID {ticket_id} not found.")
        if ref["status"] not in ("Closed", "Resolved"):
            return self._error_response(f"Ticket with ID {ticket_id} is not in a closed or resolved state.")
        ref["status"] = "Open"
        if "reopen_reasons" not in ref:
            ref["reopen_reasons"] = ""
        ref["reopen_reasons"] += f"{reason}\n"
        return self._success_response({"status": f"Ticket {ticket_id} has been reopened."})

    # ------------------------------------------------------------------
    # User-specific operations
    # ------------------------------------------------------------------
    def get_user_tickets(
        self, status: Optional[str] = None
    ) -> Dict:
        """Get tickets created by the current user, optionally filtered by status."""
        if not self._require_auth():
            return self._error_response("User not authenticated. Please log in to view tickets.")

        user_tickets = [
            ticket
            for ticket in self.ticket_queue
            if ticket["created_by"] == self.current_user
        ]

        if status:
            status_lower = status.lower()
            user_tickets = [
                ticket
                for ticket in user_tickets
                if ticket["status"].lower() == status_lower
            ]

        # Return deep copies
        return self._success_response(_deepcopy_tickets(user_tickets))

    def add_ticket_comment(self, ticket_id: int, comment: str) -> Dict:
        """Add a comment to a ticket."""
        if not self._require_auth():
            return self._error_response("User not authenticated. Please log in to comment.")
        if not comment:
            return self._error_response("Comment cannot be empty.")

        ref = self._find_ticket_ref(ticket_id)
        if not ref:
            return self._error_response(f"Ticket with ID {ticket_id} not found.")

        if "comments" not in ref:
            ref["comments"] = ""
        ref["comments"] += f"[{self.current_user}]: {comment}\n"
        return self._success_response({"status": f"Comment added to ticket {ticket_id} successfully."})

    def assign_ticket(self, ticket_id: int, assignee: str) -> Dict:
        """Assign a ticket to a user."""
        if not self._require_auth():
            return self._error_response("User not authenticated. Please log in.")
        if not assignee:
            return self._error_response("Assignee cannot be empty.")

        ref = self._find_ticket_ref(ticket_id)
        if not ref:
            return self._error_response(f"Ticket with ID {ticket_id} not found.")

        ref["assignee"] = assignee
        return self._success_response({"status": f"Ticket {ticket_id} has been assigned to {assignee}."})

    def search_all_tickets(
        self, keyword: Optional[str] = None, priority: Optional[int] = None
    ) -> Dict:
        """Search all tickets by keyword and/or priority."""
        results = self.ticket_queue

        if priority is not None:
            if not isinstance(priority, int) or isinstance(priority, bool):
                return self._error_response("Priority must be an integer.")
            results = [t for t in results if t.get("priority") == priority]

        if keyword is not None:
            keyword_lower = keyword.lower()
            results = [
                t
                for t in results
                if keyword_lower in str(t.get("title", "")).lower()
                or keyword_lower in str(t.get("description", "")).lower()
            ]

        return self._success_response(_deepcopy_tickets(results))


# Keep the original __TEST_CASES__ unchanged (as required)
__TEST_CASES__ = [
    {
        'name': 'Normal path and state change for login, create, get, and logout',
        'steps': [
            {'expect_success': True, 'tool_call': "env['ticket_api'].ticket_login(username='admin', password='password123')"},
            {'expect_success': True, 'tool_call': "env['ticket_api'].ticket_get_login_status()"},
            {'expect_success': True, 'tool_call': "env['ticket_api'].create_ticket(title='First Ticket', description='Need help', priority=3)"},
            {'expect_success': True, 'tool_call': "env['ticket_api'].get_ticket(ticket_id=1)"},
            {'expect_success': True, 'tool_call': "env['ticket_api'].get_env_state()"},
            {'expect_success': True, 'tool_call': "env['ticket_api'].logout()"}
        ]
    },
    {
        'name': 'Cross-method workflow chaining create, edit, resolve, close, and get',
        'steps': [
            {'expect_success': True, 'tool_call': "env['ticket_api'].ticket_login(username='user1', password='password')"},
            {'expect_success': True, 'tool_call': "env['ticket_api'].create_ticket(title='Workflow Ticket', description='Testing workflow', priority=2)"},
            {'expect_success': True, 'tool_call': "env['ticket_api'].edit_ticket(ticket_id=1, updates={'priority': 5, 'title': 'Updated Workflow Ticket'})"},
            {'expect_success': True, 'tool_call': "env['ticket_api'].resolve_ticket(ticket_id=1, resolution='Issue has been fixed')"},
            {'expect_success': True, 'tool_call': "env['ticket_api'].close_ticket(ticket_id=1)"},
            {'expect_success': True, 'tool_call': "env['ticket_api'].get_ticket(ticket_id=1)"}
        ]
    },
    {
        'name': 'Boundary values for ticket creation (invalid priorities and long strings)',
        'steps': [
            {'expect_success': True, 'tool_call': "env['ticket_api'].ticket_login(username='user2', password='password')"},
            {'expect_success': False, 'tool_call': "env['ticket_api'].create_ticket(title='Low Priority', description='Too low', priority=0)"},
            {'expect_success': False, 'tool_call': "env['ticket_api'].create_ticket(title='High Priority', description='Too high', priority=6)"},
            {'expect_success': False, 'tool_call': "env['ticket_api'].create_ticket(title='Negative Priority', description='Negative', priority=-1)"},
            {'expect_success': True, 'tool_call': "env['ticket_api'].create_ticket(title='LongTitleLongTitleLongTitleLongTitleLongTitle', description='LongDescriptionLongDescriptionLongDescription', priority=5)"}
        ]
    },
    {
        'name': 'Error paths for non-existent ticket IDs',
        'steps': [
            {'expect_success': False, 'tool_call': "env['ticket_api'].get_ticket(ticket_id=9999)"},
            {'expect_success': False, 'tool_call': "env['ticket_api'].close_ticket(ticket_id=9999)"},
            {'expect_success': False, 'tool_call': "env['ticket_api'].resolve_ticket(ticket_id=9999, resolution='Done')"},
            {'expect_success': False, 'tool_call': "env['ticket_api'].edit_ticket(ticket_id=9999, updates={'title': 'New Title'})"}
        ]
    },
    {
        'name': 'Error paths for invalid parameters and wrong types',
        'steps': [
            {'expect_success': True, 'tool_call': "env['ticket_api'].ticket_login(username='user3', password='password')"},
            {'expect_success': False, 'tool_call': "env['ticket_api'].create_ticket(title=None, description='Missing title', priority=1)"},
            {'expect_success': False, 'tool_call': "env['ticket_api'].create_ticket(title='Wrong priority type', description='Desc', priority='high')"},
            {'expect_success': True, 'tool_call': "env['ticket_api'].create_ticket(title='Valid Ticket', description='Desc', priority=1)"},
            {'expect_success': False, 'tool_call': "env['ticket_api'].edit_ticket(ticket_id=1, updates={'priority': 'urgent'})"}
        ]
    },
    {
        'name': 'Normal path for getting user tickets with and without status filters',
        'steps': [
            {'expect_success': True, 'tool_call': "env['ticket_api'].ticket_login(username='user4', password='password')"},
            {'expect_success': True, 'tool_call': "env['ticket_api'].create_ticket(title='User4 Ticket 1', description='Desc 1', priority=2)"},
            {'expect_success': True, 'tool_call': "env['ticket_api'].create_ticket(title='User4 Ticket 2', description='Desc 2', priority=3)"},
            {'expect_success': True, 'tool_call': "env['ticket_api'].get_user_tickets(status=None)"},
            {'expect_success': True, 'tool_call': "env['ticket_api'].get_user_tickets(status='open')"}
        ]
    },
    {
        'name': 'State-change verification by editing ticket status directly',
        'steps': [
            {'expect_success': True, 'tool_call': "env['ticket_api'].ticket_login(username='user5', password='password')"},
            {'expect_success': True, 'tool_call': "env['ticket_api'].create_ticket(title='State Change Ticket', description='Desc', priority=2)"},
            {'expect_success': True, 'tool_call': "env['ticket_api'].edit_ticket(ticket_id=1, updates={'status': 'in_progress'})"},
            {'expect_success': True, 'tool_call': "env['ticket_api'].get_ticket(ticket_id=1)"}
        ]
    },
    {
        'name': 'Error paths for unauthenticated operations',
        'steps': [
            {'expect_success': True, 'tool_call': "env['ticket_api'].logout()"},
            {'expect_success': False, 'tool_call': "env['ticket_api'].get_user_tickets(status=None)"}
        ]
    },
    {
        'name': 'Boundary values for editing ticket with empty updates and empty strings',
        'steps': [
            {'expect_success': True, 'tool_call': "env['ticket_api'].ticket_login(username='user6', password='password')"},
            {'expect_success': True, 'tool_call': "env['ticket_api'].create_ticket(title='Empty Edit Ticket', description='Desc', priority=2)"},
            {'expect_success': True, 'tool_call': "env['ticket_api'].edit_ticket(ticket_id=1, updates={})"},
            {'expect_success': True, 'tool_call': "env['ticket_api'].edit_ticket(ticket_id=1, updates={'title': '', 'description': ''})"}
        ]
    },
    {
        'name': 'Cross-method workflow with multiple users interacting with the same ticket',
        'steps': [
            {'expect_success': True, 'tool_call': "env['ticket_api'].ticket_login(username='userA', password='password')"},
            {'expect_success': True, 'tool_call': "env['ticket_api'].create_ticket(title='Shared Ticket', description='Desc', priority=1)"},
            {'expect_success': True, 'tool_call': "env['ticket_api'].logout()"},
            {'expect_success': True, 'tool_call': "env['ticket_api'].ticket_login(username='userB', password='password')"},
            {'expect_success': True, 'tool_call': "env['ticket_api'].get_ticket(ticket_id=1)"},
            {'expect_success': True, 'tool_call': "env['ticket_api'].edit_ticket(ticket_id=1, updates={'priority': 2})"},
            {'expect_success': True, 'tool_call': "env['ticket_api'].get_user_tickets(status=None)"}
        ]
    },
    {
        'name': 'Adding comments and assigning tickets',
        'steps': [
            {'expect_success': True, 'tool_call': "env['ticket_api'].ticket_login(username='user1', password='pw')"},
            {'expect_success': True, 'tool_call': "env['ticket_api'].create_ticket(title='Comment Ticket', description='Needs comment', priority=1)"},
            {'expect_success': True, 'tool_call': "env['ticket_api'].add_ticket_comment(ticket_id=1, comment='First comment')"},
            {'expect_success': False, 'tool_call': "env['ticket_api'].add_ticket_comment(ticket_id=1, comment='')"},
            {'expect_success': True, 'tool_call': "env['ticket_api'].assign_ticket(ticket_id=1, assignee='agent1')"},
            {'expect_success': False, 'tool_call': "env['ticket_api'].assign_ticket(ticket_id=1, assignee='')"},
            {'expect_success': True, 'tool_call': "env['ticket_api'].get_ticket(ticket_id=1)"}
        ]
    },
    {
        'name': 'Searching all tickets by keyword and priority',
        'steps': [
            {'expect_success': True, 'tool_call': "env['ticket_api'].ticket_login(username='user1', password='pw')"},
            {'expect_success': True, 'tool_call': "env['ticket_api'].create_ticket(title='Network Issue', description='Cannot connect to WiFi', priority=4)"},
            {'expect_success': True, 'tool_call': "env['ticket_api'].create_ticket(title='Hardware Issue', description='Mouse is broken', priority=2)"},
            {'expect_success': True, 'tool_call': "env['ticket_api'].search_all_tickets(keyword='WiFi')"},
            {'expect_success': True, 'tool_call': "env['ticket_api'].search_all_tickets(priority=2)"},
            {'expect_success': False, 'tool_call': "env['ticket_api'].search_all_tickets(priority='high')"}
        ]
    },
    {
        'name': 'Reopening a resolved/closed ticket',
        'steps': [
            {'expect_success': True, 'tool_call': "env['ticket_api'].ticket_login(username='user1', password='pw')"},
            {'expect_success': True, 'tool_call': "env['ticket_api'].create_ticket(title='Fix it', description='Needs fix', priority=3)"},
            {'expect_success': False, 'tool_call': "env['ticket_api'].reopen_ticket(ticket_id=1, reason='Still broken')"},
            {'expect_success': True, 'tool_call': "env['ticket_api'].resolve_ticket(ticket_id=1, resolution='Fixed')"},
            {'expect_success': False, 'tool_call': "env['ticket_api'].reopen_ticket(ticket_id=1, reason='')"},
            {'expect_success': True, 'tool_call': "env['ticket_api'].reopen_ticket(ticket_id=1, reason='Still broken')"},
            {'expect_success': True, 'tool_call': "env['ticket_api'].get_ticket(ticket_id=1)"}
        ]
    }
]