"""
CRM System Environment API

A centralized environment for managing an organization's interactions with
current and potential customers, including customer profiles, communication logs,
sales opportunities, and service tickets.
"""

from copy import deepcopy
from typing import Dict, List, Optional, Any
from datetime import datetime


DEFAULT_STATE: Dict[str, Any] = {
    # Current user context
    "current_user_id": "user_001",
    
    # Customers
    "customers": {
        "cust_001": {
            "customer_id": "cust_001",
            "name": "Alice Johnson",
            "email": "alice.johnson@techcorp.com",
            "phone": "+1-555-0101",
            "company": "TechCorp Inc.",
            "created_date": "2023-01-15T09:00:00",
            "last_contact_date": "2024-06-10T14:30:00",
            "status": "active"
        },
        "cust_002": {
            "customer_id": "cust_002",
            "name": "Bob Smith",
            "email": "bob.smith@globalsoft.com",
            "phone": "+1-555-0102",
            "company": "GlobalSoft LLC",
            "created_date": "2023-03-20T11:00:00",
            "last_contact_date": "2024-05-28T10:15:00",
            "status": "active"
        },
        "cust_003": {
            "customer_id": "cust_003",
            "name": "Carol White",
            "email": "carol.white@innovate.io",
            "phone": "+1-555-0103",
            "company": "Innovate.io",
            "created_date": "2022-11-05T08:30:00",
            "last_contact_date": "2024-04-15T16:45:00",
            "status": "inactive"
        },
        "cust_004": {
            "customer_id": "cust_004",
            "name": "David Brown",
            "email": "david.brown@startup.net",
            "phone": "+1-555-0104",
            "company": "Startup Networks",
            "created_date": "2024-01-10T10:00:00",
            "last_contact_date": "2024-06-20T09:00:00",
            "status": "active"
        }
    },
    
    # Communication Logs
    "communication_logs": {
        "log_001": {
            "log_id": "log_001",
            "customer_id": "cust_001",
            "type": "email",
            "timestamp": "2024-06-10T14:30:00",
            "subject": "Product Demo Follow-up",
            "content": "Following up on the product demonstration scheduled for next week.",
            "user_id": "user_002"
        },
        "log_002": {
            "log_id": "log_002",
            "customer_id": "cust_001",
            "type": "call",
            "timestamp": "2024-06-05T11:00:00",
            "subject": "Initial Contact",
            "content": "Discussed customer requirements and scheduled a demo.",
            "user_id": "user_002"
        },
        "log_003": {
            "log_id": "log_003",
            "customer_id": "cust_002",
            "type": "meeting",
            "timestamp": "2024-05-28T10:15:00",
            "subject": "Quarterly Review",
            "content": "Reviewed Q1 performance and discussed expansion plans.",
            "user_id": "user_001"
        },
        "log_004": {
            "log_id": "log_004",
            "customer_id": "cust_003",
            "type": "email",
            "timestamp": "2024-04-15T16:45:00",
            "subject": "Re-engagement Campaign",
            "content": "Sent promotional offer to re-engage inactive customer.",
            "user_id": "user_003"
        }
    },
    
    # Sales Opportunities
    "sales_opportunities": {
        "opp_001": {
            "opportunity_id": "opp_001",
            "customer_id": "cust_001",
            "stage": "negotiation",
            "value": 50000.00,
            "expected_close_date": "2024-07-15",
            "owner_id": "user_002"
        },
        "opp_002": {
            "opportunity_id": "opp_002",
            "customer_id": "cust_002",
            "stage": "prospecting",
            "value": 25000.00,
            "expected_close_date": "2024-08-30",
            "owner_id": "user_002"
        },
        "opp_003": {
            "opportunity_id": "opp_003",
            "customer_id": "cust_004",
            "stage": "closed_won",
            "value": 15000.00,
            "expected_close_date": "2024-06-01",
            "owner_id": "user_001"
        }
    },
    
    # Service Tickets
    "service_tickets": {
        "ticket_001": {
            "ticket_id": "ticket_001",
            "customer_id": "cust_001",
            "issue": "Unable to access dashboard after recent update",
            "status": "open",
            "priority": "high",
            "assigned_to": "user_003",
            "created_date": "2024-06-18T08:00:00"
        },
        "ticket_002": {
            "ticket_id": "ticket_002",
            "customer_id": "cust_002",
            "issue": "Request for additional user licenses",
            "status": "resolved",
            "priority": "medium",
            "assigned_to": "user_003",
            "created_date": "2024-05-20T14:00:00"
        },
        "ticket_003": {
            "ticket_id": "ticket_003",
            "customer_id": "cust_003",
            "issue": "Billing discrepancy on last invoice",
            "status": "open",
            "priority": "low",
            "assigned_to": "user_001",
            "created_date": "2024-04-10T09:30:00"
        }
    },
    
    # Users (Internal Employees)
    "users": {
        "user_001": {
            "user_id": "user_001",
            "name": "John Admin",
            "role": "admin",
            "department": "Management"
        },
        "user_002": {
            "user_id": "user_002",
            "name": "Sarah Sales",
            "role": "sales_rep",
            "department": "Sales"
        },
        "user_003": {
            "user_id": "user_003",
            "name": "Mike Support",
            "role": "support_agent",
            "department": "Customer Support"
        },
        "user_004": {
            "user_id": "user_004",
            "name": "Emma Viewer",
            "role": "viewer",
            "department": "Marketing"
        }
    },
    
    # System configuration
    "system_config": {
        "cascade_delete_logs": True,
        "require_archive_before_delete": True,
        "authorized_delete_roles": ["admin", "manager"]
    }
}


class CRMSystem:
    """
    CRM System Environment API for managing customer relationships.
    
    This class provides a complete API for managing customer records,
    communication logs, sales opportunities, and service tickets in a
    CRM environment. It enforces business rules and constraints while
    providing RL-friendly error handling.
    """
    
    def __init__(self) -> None:
        """
        Initialize the CRM System environment.
        
        Declares all state attributes with type hints and sets up the
        API description for the environment.
        
        Args:
            None
        
        Returns:
            None
        """
        self._api_description: str = "CRM system for managing customer relationships, communications, sales opportunities, and service tickets."
        
        # State attributes
        self.current_user_id: str = ""
        self.customers: Dict[str, Dict[str, Any]] = {}
        self.communication_logs: Dict[str, Dict[str, Any]] = {}
        self.sales_opportunities: Dict[str, Dict[str, Any]] = {}
        self.service_tickets: Dict[str, Dict[str, Any]] = {}
        self.users: Dict[str, Dict[str, Any]] = {}
        self.system_config: Dict[str, Any] = {}
        
        # Injected timestamp for testing
        self._injected_timestamp: Optional[str] = None
    
    def _timestamp(self) -> str:
        """
        Generate a consistent ISO format timestamp.
        
        Args:
            None
        
        Returns:
            str: ISO format timestamp string.
        """
        if self._injected_timestamp:
            return self._injected_timestamp
        return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
    
    def _load_scenario(self, scenario: dict, long_context: bool = False) -> None:
        """
        Load initial state from a scenario dictionary.
        
        Args:
            scenario: Dictionary containing initial state values.
            long_context: Flag for long context scenarios (unused but required).
        
        Returns:
            None
        """
        if not scenario:
            return
        for key in DEFAULT_STATE:
            if key in scenario:
                setattr(self, key, deepcopy(scenario[key]))
            else:
                setattr(self, key, deepcopy(DEFAULT_STATE[key]))
    
    def get_env_state(self) -> Dict[str, Any]:
        """
        Return the current state of the CRM environment.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: A dictionary containing all current environment
                state variables including customers, communication_logs,
                sales_opportunities, service_tickets, users, current_user_id,
                and system_config.
        """
        return {
            "current_user_id": self.current_user_id,
            "customers": deepcopy(self.customers),
            "communication_logs": deepcopy(self.communication_logs),
            "sales_opportunities": deepcopy(self.sales_opportunities),
            "service_tickets": deepcopy(self.service_tickets),
            "users": deepcopy(self.users),
            "system_config": deepcopy(self.system_config)
        }
    
    # ==================== Query Operations ====================
    
    def get_customer_by_id(self, customer_id: str) -> Dict[str, Any]:
        """
        Retrieve full customer record using customer_id.
        
        Args:
            customer_id: The unique identifier of the customer.
        
        Returns:
            Dict[str, Any]: The customer record if found, or an error dict.
        """
        if customer_id not in self.customers:
            return {"error": f"Customer with id '{customer_id}' not found"}
        return {"customer": deepcopy(self.customers[customer_id])}
    
    def get_customer_by_email(self, email: str) -> Dict[str, Any]:
        """
        Find a customer by their email address.
        
        Args:
            email: The email address to search for.
        
        Returns:
            Dict[str, Any]: The customer record if found, or an error dict.
        """
        for customer in self.customers.values():
            if customer.get("email", "").lower() == email.lower():
                return {"customer": deepcopy(customer)}
        return {"error": f"Customer with email '{email}' not found"}
    
    def list_all_customers(self) -> Dict[str, Any]:
        """
        Retrieve a list of all customer records in the system.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: A dict containing list of all customers.
        """
        return {"customers": list(deepcopy(self.customers).values())}
    
    def search_customers_by_status(self, status: str) -> Dict[str, Any]:
        """
        Filter and list customers based on status.
        
        Args:
            status: The status to filter by (e.g., active, inactive, archived).
        
        Returns:
            Dict[str, Any]: A dict containing list of matching customers.
        """
        matching = [
            deepcopy(c) for c in self.customers.values()
            if c.get("status", "").lower() == status.lower()
        ]
        return {"customers": matching, "count": len(matching)}
    
    def get_customer_service_tickets(self, customer_id: str) -> Dict[str, Any]:
        """
        Retrieve all service tickets associated with a given customer.
        
        Args:
            customer_id: The unique identifier of the customer.
        
        Returns:
            Dict[str, Any]: A dict containing list of service tickets.
        """
        if customer_id not in self.customers:
            return {"error": f"Customer with id '{customer_id}' not found"}
        
        tickets = [
            deepcopy(t) for t in self.service_tickets.values()
            if t.get("customer_id") == customer_id
        ]
        return {"tickets": tickets, "count": len(tickets)}
    
    def get_customer_sales_opportunities(self, customer_id: str) -> Dict[str, Any]:
        """
        Retrieve all sales opportunities linked to a customer.
        
        Args:
            customer_id: The unique identifier of the customer.
        
        Returns:
            Dict[str, Any]: A dict containing list of sales opportunities.
        """
        if customer_id not in self.customers:
            return {"error": f"Customer with id '{customer_id}' not found"}
        
        opportunities = [
            deepcopy(o) for o in self.sales_opportunities.values()
            if o.get("customer_id") == customer_id
        ]
        return {"opportunities": opportunities, "count": len(opportunities)}
    
    def get_customer_communication_logs(self, customer_id: str) -> Dict[str, Any]:
        """
        Retrieve all communication logs for a specific customer.
        
        Args:
            customer_id: The unique identifier of the customer.
        
        Returns:
            Dict[str, Any]: A dict containing list of communication logs.
        """
        if customer_id not in self.customers:
            return {"error": f"Customer with id '{customer_id}' not found"}
        
        logs = [
            deepcopy(log) for log in self.communication_logs.values()
            if log.get("customer_id") == customer_id
        ]
        return {"logs": logs, "count": len(logs)}
    
    def check_customer_has_open_tickets(self, customer_id: str) -> Dict[str, Any]:
        """
        Determine if a customer has any service tickets with status "open".
        
        Args:
            customer_id: The unique identifier of the customer.
        
        Returns:
            Dict[str, Any]: A dict indicating whether open tickets exist.
        """
        if customer_id not in self.customers:
            return {"error": f"Customer with id '{customer_id}' not found"}
        
        open_tickets = [
            t for t in self.service_tickets.values()
            if t.get("customer_id") == customer_id and t.get("status", "").lower() == "open"
        ]
        return {
            "has_open_tickets": len(open_tickets) > 0,
            "open_ticket_count": len(open_tickets),
            "open_ticket_ids": [t["ticket_id"] for t in open_tickets]
        }
    
    def check_customer_has_active_opportunities(self, customer_id: str) -> Dict[str, Any]:
        """
        Determine if a customer has any sales opportunities in active stages.
        
        Active stages include: prospecting, qualification, proposal, negotiation.
        
        Args:
            customer_id: The unique identifier of the customer.
        
        Returns:
            Dict[str, Any]: A dict indicating whether active opportunities exist.
        """
        if customer_id not in self.customers:
            return {"error": f"Customer with id '{customer_id}' not found"}
        
        active_stages = {"prospecting", "qualification", "proposal", "negotiation"}
        active_opps = [
            o for o in self.sales_opportunities.values()
            if o.get("customer_id") == customer_id and o.get("stage", "").lower() in active_stages
        ]
        return {
            "has_active_opportunities": len(active_opps) > 0,
            "active_opportunity_count": len(active_opps),
            "active_opportunity_ids": [o["opportunity_id"] for o in active_opps]
        }
    
    def get_user_role(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve the role of a user to check permissions.
        
        Args:
            user_id: The user ID to check. Defaults to current user if None.
        
        Returns:
            Dict[str, Any]: A dict containing the user's role information.
        """
        uid = user_id if user_id else self.current_user_id
        if uid not in self.users:
            return {"error": f"User with id '{uid}' not found"}
        
        user = self.users[uid]
        return {
            "user_id": uid,
            "role": user.get("role", "unknown"),
            "name": user.get("name", "")
        }
    
    def get_user_by_id(self, user_id: str) -> Dict[str, Any]:
        """
        Retrieve internal user (agent) information by user_id.
        
        Args:
            user_id: The unique identifier of the user.
        
        Returns:
            Dict[str, Any]: The user record if found, or an error dict.
        """
        if user_id not in self.users:
            return {"error": f"User with id '{user_id}' not found"}
        return {"user": deepcopy(self.users[user_id])}
    
    # ==================== State Change Operations ====================
    
    def update_customer_status(self, customer_id: str, new_status: str) -> Dict[str, Any]:
        """
        Modify the status of a customer.
        
        Args:
            customer_id: The unique identifier of the customer.
            new_status: The new status value (e.g., active, inactive, archived, deleted).
        
        Returns:
            Dict[str, Any]: Success confirmation or error dict.
        """
        if customer_id not in self.customers:
            return {"error": f"Customer with id '{customer_id}' not found"}
        
        valid_statuses = {"active", "inactive", "archived", "deleted"}
        if new_status.lower() not in valid_statuses:
            return {"error": f"Invalid status '{new_status}'. Valid statuses: {valid_statuses}"}
        
        old_status = self.customers[customer_id].get("status")
        self.customers[customer_id]["status"] = new_status.lower()
        
        return {
            "success": True,
            "customer_id": customer_id,
            "old_status": old_status,
            "new_status": new_status.lower()
        }
    
    def resolve_service_ticket(self, ticket_id: str) -> Dict[str, Any]:
        """
        Update a service ticket's status to "resolved".
        
        Args:
            ticket_id: The unique identifier of the service ticket.
        
        Returns:
            Dict[str, Any]: Success confirmation or error dict.
        """
        if ticket_id not in self.service_tickets:
            return {"error": f"Service ticket with id '{ticket_id}' not found"}
        
        ticket = self.service_tickets[ticket_id]
        if ticket.get("status", "").lower() == "resolved":
            return {"error": f"Ticket '{ticket_id}' is already resolved"}
        
        old_status = ticket.get("status")
        self.service_tickets[ticket_id]["status"] = "resolved"
        
        return {
            "success": True,
            "ticket_id": ticket_id,
            "old_status": old_status,
            "new_status": "resolved"
        }
    
    def delete_service_ticket(self, ticket_id: str) -> Dict[str, Any]:
        """
        Remove a service ticket associated with a customer.
        
        Args:
            ticket_id: The unique identifier of the service ticket.
        
        Returns:
            Dict[str, Any]: Success confirmation or error dict.
        """
        if ticket_id not in self.service_tickets:
            return {"error": f"Service ticket with id '{ticket_id}' not found"}
        
        deleted_ticket = self.service_tickets.pop(ticket_id)
        return {
            "success": True,
            "deleted_ticket_id": ticket_id,
            "customer_id": deleted_ticket.get("customer_id")
        }
    
    def close_sales_opportunity(self, opportunity_id: str, outcome: str) -> Dict[str, Any]:
        """
        Update a sales opportunity to a closed stage.
        
        Args:
            opportunity_id: The unique identifier of the sales opportunity.
            outcome: The closing outcome (e.g., "won", "lost").
        
        Returns:
            Dict[str, Any]: Success confirmation or error dict.
        """
        if opportunity_id not in self.sales_opportunities:
            return {"error": f"Sales opportunity with id '{opportunity_id}' not found"}
        
        valid_outcomes = {"won", "lost", "closed_won", "closed_lost"}
        outcome_lower = outcome.lower()
        if outcome_lower not in valid_outcomes:
            return {"error": f"Invalid outcome '{outcome}'. Valid outcomes: {valid_outcomes}"}
        
        # Normalize outcome
        if outcome_lower == "won":
            outcome_lower = "closed_won"
        elif outcome_lower == "lost":
            outcome_lower = "closed_lost"
        
        opp = self.sales_opportunities[opportunity_id]
        old_stage = opp.get("stage")
        self.sales_opportunities[opportunity_id]["stage"] = outcome_lower
        
        return {
            "success": True,
            "opportunity_id": opportunity_id,
            "old_stage": old_stage,
            "new_stage": outcome_lower
        }
    
    def delete_sales_opportunity(self, opportunity_id: str) -> Dict[str, Any]:
        """
        Remove a sales opportunity linked to a customer.
        
        Args:
            opportunity_id: The unique identifier of the sales opportunity.
        
        Returns:
            Dict[str, Any]: Success confirmation or error dict.
        """
        if opportunity_id not in self.sales_opportunities:
            return {"error": f"Sales opportunity with id '{opportunity_id}' not found"}
        
        deleted_opp = self.sales_opportunities.pop(opportunity_id)
        return {
            "success": True,
            "deleted_opportunity_id": opportunity_id,
            "customer_id": deleted_opp.get("customer_id")
        }
    
    def archive_communication_logs(self, customer_id: str) -> Dict[str, Any]:
        """
        Mark communication logs as archived prior to customer deletion.
        
        Args:
            customer_id: The unique identifier of the customer.
        
        Returns:
            Dict[str, Any]: Success confirmation with count of archived logs.
        """
        if customer_id not in self.customers:
            return {"error": f"Customer with id '{customer_id}' not found"}
        
        archived_count = 0
        archived_ids = []
        for log_id, log in self.communication_logs.items():
            if log.get("customer_id") == customer_id:
                log["archived"] = True
                log["archived_date"] = self._timestamp()
                archived_count += 1
                archived_ids.append(log_id)
        
        return {
            "success": True,
            "customer_id": customer_id,
            "archived_log_count": archived_count,
            "archived_log_ids": archived_ids
        }
    
    def delete_communication_logs_by_customer(self, customer_id: str) -> Dict[str, Any]:
        """
        Remove all communication logs associated with a given customer.
        
        Args:
            customer_id: The unique identifier of the customer.
        
        Returns:
            Dict[str, Any]: Success confirmation with count of deleted logs.
        """
        if customer_id not in self.customers:
            return {"error": f"Customer with id '{customer_id}' not found"}
        
        logs_to_delete = [
            log_id for log_id, log in self.communication_logs.items()
            if log.get("customer_id") == customer_id
        ]
        
        for log_id in logs_to_delete:
            del self.communication_logs[log_id]
        
        return {
            "success": True,
            "customer_id": customer_id,
            "deleted_log_count": len(logs_to_delete),
            "deleted_log_ids": logs_to_delete
        }
    
    def delete_customer(self, customer_id: str) -> Dict[str, Any]:
        """
        Remove the customer record from the system.
        
        Subject to constraints:
        - Cannot delete if customer has open service tickets
        - Cannot delete if customer has active sales opportunities
        - Only users with authorized roles can delete
        - Customer status must be archived/deleted before final deletion (if configured)
        
        Args:
            customer_id: The unique identifier of the customer.
        
        Returns:
            Dict[str, Any]: Success confirmation or error dict.
        """
        # Check customer exists
        if customer_id not in self.customers:
            return {"error": f"Customer with id '{customer_id}' not found"}
        
        customer = self.customers[customer_id]
        
        # Check user authorization
        current_user = self.users.get(self.current_user_id, {})
        user_role = current_user.get("role", "")
        authorized_roles = self.system_config.get("authorized_delete_roles", ["admin"])
        
        if user_role not in authorized_roles:
            return {
                "error": f"User role '{user_role}' is not authorized to delete customers. "
                         f"Authorized roles: {authorized_roles}"
            }
        
        # Check for open service tickets
        open_tickets_check = self.check_customer_has_open_tickets(customer_id)
        if open_tickets_check.get("has_open_tickets"):
            return {
                "error": f"Cannot delete customer '{customer_id}': has {open_tickets_check['open_ticket_count']} "
                         f"open service ticket(s). Resolve or delete them first.",
                "open_ticket_ids": open_tickets_check.get("open_ticket_ids", [])
            }
        
        # Check for active sales opportunities
        active_opps_check = self.check_customer_has_active_opportunities(customer_id)
        if active_opps_check.get("has_active_opportunities"):
            return {
                "error": f"Cannot delete customer '{customer_id}': has {active_opps_check['active_opportunity_count']} "
                         f"active sales opportunity(ies). Close or delete them first.",
                "active_opportunity_ids": active_opps_check.get("active_opportunity_ids", [])
            }
        
        # Check if archive before delete is required
        if self.system_config.get("require_archive_before_delete", False):
            if customer.get("status") not in ["archived", "deleted"]:
                return {
                    "error": f"Cannot delete customer '{customer_id}': customer status must be "
                             f"'archived' or 'deleted' before deletion. Current status: '{customer.get('status')}'"
                }
        
        # Handle cascade deletion of communication logs
        deleted_logs = []
        if self.system_config.get("cascade_delete_logs", False):
            logs_to_delete = [
                log_id for log_id, log in self.communication_logs.items()
                if log.get("customer_id") == customer_id
            ]
            for log_id in logs_to_delete:
                del self.communication_logs[log_id]
                deleted_logs.append(log_id)
        
        # Delete the customer
        del self.customers[customer_id]
        
        return {
            "success": True,
            "deleted_customer_id": customer_id,
            "cascade_deleted_logs": deleted_logs,
            "cascade_deleted_log_count": len(deleted_logs)
        }
    
    def bulk_archive_customers(self, customer_ids: List[str]) -> Dict[str, Any]:
        """
        Mark multiple customers as "archived" in preparation for deletion.
        
        Args:
            customer_ids: List of customer IDs to archive.
        
        Returns:
            Dict[str, Any]: Success confirmation with results for each customer.
        """
        if not customer_ids:
            return {"error": "No customer IDs provided"}
        
        results = {
            "archived": [],
            "failed": [],
            "not_found": []
        }
        
        for customer_id in customer_ids:
            if customer_id not in self.customers:
                results["not_found"].append(customer_id)
                continue
            
            customer = self.customers[customer_id]
            if customer.get("status") == "archived":
                results["failed"].append({
                    "customer_id": customer_id,
                    "reason": "Already archived"
                })
                continue
            
            self.customers[customer_id]["status"] = "archived"
            results["archived"].append(customer_id)
        
        return {
            "success": True,
            "archived_count": len(results["archived"]),
            "archived_ids": results["archived"],
            "failed": results["failed"],
            "not_found": results["not_found"]
        }
    
    def restore_customer(self, customer_id: str) -> Dict[str, Any]:
        """
        Restore a deleted/archived customer and associated records.
        
        Args:
            customer_id: The unique identifier of the customer to restore.
        
        Returns:
            Dict[str, Any]: Success confirmation or error dict.
        """
        if customer_id not in self.customers:
            return {"error": f"Customer with id '{customer_id}' not found"}
        
        customer = self.customers[customer_id]
        current_status = customer.get("status", "")
        
        if current_status not in ["archived", "deleted"]:
            return {
                "error": f"Customer '{customer_id}' cannot be restored: "
                         f"current status is '{current_status}', expected 'archived' or 'deleted'"
            }
        
        # Restore customer status to active
        self.customers[customer_id]["status"] = "active"
        self.customers[customer_id]["last_contact_date"] = self._timestamp()
        
        # Restore archived communication logs
        restored_logs = []
        for log_id, log in self.communication_logs.items():
            if log.get("customer_id") == customer_id and log.get("archived"):
                log["archived"] = False
                if "archived_date" in log:
                    del log["archived_date"]
                restored_logs.append(log_id)
        
        return {
            "success": True,
            "customer_id": customer_id,
            "old_status": current_status,
            "new_status": "active",
            "restored_log_count": len(restored_logs),
            "restored_log_ids": restored_logs
        }


__TEST_CASES__ = [
    {
        "name": "Query customer and their related data",
        "steps": [
            {"tool_call": "get_customer_by_id(customer_id='cust_001')", "expect_success": True},
            {"tool_call": "get_communication_logs(customer_id='cust_001')", "expect_success": True},
            {"tool_call": "get_sales_opportunities(customer_id='cust_001')", "expect_success": True}
        ]
    },
    {
        "name": "Create and update customer lifecycle",
        "steps": [
            {"tool_call": "create_customer(name='Test Corp', email='test@corp.com', phone='555-0100')", "expect_success": True},
            {"tool_call": "update_customer(customer_id='cust_002', updates={'status': 'active', 'industry': 'Technology'})", "expect_success": True},
            {"tool_call": "get_customer_by_id(customer_id='cust_002')", "expect_success": True}
        ]
    },
    {
        "name": "Communication log management",
        "steps": [
            {"tool_call": "add_communication_log(customer_id='cust_001', log_type='email', subject='Follow-up', content='Thank you for your interest')", "expect_success": True},
            {"tool_call": "add_communication_log(customer_id='cust_001', log_type='call', subject='Sales Call', content='Discussed pricing options', duration_minutes=30)", "expect_success": True},
            {"tool_call": "get_communication_logs(customer_id='cust_001')", "expect_success": True}
        ]
    },
    {
        "name": "Sales opportunity workflow",
        "steps": [
            {"tool_call": "create_sales_opportunity(customer_id='cust_001', title='Enterprise License', value=50000.0, stage='qualification')", "expect_success": True},
            {"tool_call": "update_opportunity_stage(opportunity_id='opp_001', new_stage='proposal')", "expect_success": True},
            {"tool_call": "update_opportunity_stage(opportunity_id='opp_001', new_stage='negotiation')", "expect_success": True},
            {"tool_call": "update_opportunity_stage(opportunity_id='opp_001', new_stage='closed_won')", "expect_success": True}
        ]
    },
    {
        "name": "Task management for customers",
        "steps": [
            {"tool_call": "create_task(customer_id='cust_001', title='Send proposal', due_date='2024-12-31', priority='high')", "expect_success": True},
            {"tool_call": "get_tasks(customer_id='cust_001')", "expect_success": True},
            {"tool_call": "complete_task(task_id='task_001')", "expect_success": True}
        ]
    },
    {
        "name": "Customer search and filtering",
        "steps": [
            {"tool_call": "search_customers(query='Corp')", "expect_success": True},
            {"tool_call": "search_customers(status='active')", "expect_success": True},
            {"tool_call": "search_customers(industry='Technology')", "expect_success": True}
        ]
    },
    {
        "name": "Archive and restore customer",
        "steps": [
            {"tool_call": "archive_customer(customer_id='cust_001')", "expect_success": True},
            {"tool_call": "get_customer_by_id(customer_id='cust_001')", "expect_success": True},
            {"tool_call": "restore_customer(customer_id='cust_001')", "expect_success": True}
        ]
    },
    {
        "name": "Bulk operations",
        "steps": [
            {"tool_call": "bulk_update_customers(customer_ids=['cust_001', 'cust_002'], updates={'status': 'active'})", "expect_success": True},
            {"tool_call": "bulk_delete_customers(customer_ids=['cust_003', 'cust_004'])", "expect_success": True}
        ]
    },
    {
        "name": "Error handling - invalid customer",
        "steps": [
            {"tool_call": "get_customer_by_id(customer_id='invalid_id')", "expect_success": False},
            {"tool_call": "update_customer(customer_id='invalid_id', updates={'name': 'New Name'})", "expect_success": False},
            {"tool_call": "archive_customer(customer_id='invalid_id')", "expect_success": False}
        ]
    },
    {
        "name": "Error handling - invalid opportunity stage",
        "steps": [
            {"tool_call": "create_sales_opportunity(customer_id='cust_001', title='Test Deal', value=1000.0, stage='invalid_stage')", "expect_success": False},
            {"tool_call": "update_opportunity_stage(opportunity_id='opp_001', new_stage='invalid_stage')", "expect_success": False}
        ]
    },
    {
        "name": "Analytics and reporting",
        "steps": [
            {"tool_call": "get_customer_summary(customer_id='cust_001')", "expect_success": True},
            {"tool_call": "get_pipeline_report()", "expect_success": True},
            {"tool_call": "get_activity_report(start_date='2024-01-01', end_date='2024-12-31')", "expect_success": True}
        ]
    }
]


__AVAILABLE_TOOLS__ = [
    "get_customer_by_id",
    "create_customer",
    "update_customer",
    "delete_customer",
    "archive_customer",
    "restore_customer",
    "search_customers",
    "bulk_update_customers",
    "bulk_delete_customers",
    "add_communication_log",
    "get_communication_logs",
    "delete_communication_log",
    "create_sales_opportunity",
    "get_sales_opportunities",
    "update_opportunity_stage",
    "delete_opportunity",
    "create_task",
    "get_tasks",
    "update_task",
    "complete_task",
    "delete_task",
    "get_customer_summary",
    "get_pipeline_report",
    "get_activity_report"
]