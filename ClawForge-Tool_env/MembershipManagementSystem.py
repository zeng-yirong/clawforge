"""
Membership Management System Environment API

A stateful environment for managing member records, including registration,
status tracking, identifier mapping, and audit logging.
"""

from copy import deepcopy
from typing import Dict, List, Optional, Any
from datetime import datetime


DEFAULT_STATE: Dict[str, Any] = {
    # Members table - core member records
    "members": {
        "MEM001": {
            "member_id": "MEM001",
            "external_id": "EXT-A100",
            "first_name": "Alice",
            "last_name": "Johnson",
            "email": "alice.johnson@example.com",
            "phone": "+1-555-0101",
            "membership_status": "active",
            "join_date": "2023-01-15T10:00:00",
            "last_updated": "2024-01-10T14:30:00"
        },
        "MEM002": {
            "member_id": "MEM002",
            "external_id": "EXT-B200",
            "first_name": "Bob",
            "last_name": "Smith",
            "email": "bob.smith@example.com",
            "phone": "+1-555-0102",
            "membership_status": "suspended",
            "join_date": "2022-06-20T09:00:00",
            "last_updated": "2024-02-01T11:00:00"
        },
        "MEM003": {
            "member_id": "MEM003",
            "external_id": "EXT-C300",
            "first_name": "Carol",
            "last_name": "Williams",
            "email": "carol.williams@example.com",
            "phone": "+1-555-0103",
            "membership_status": "expired",
            "join_date": "2021-03-10T08:00:00",
            "last_updated": "2023-12-01T16:45:00"
        }
    },
    
    # Membership status logs - audit trail for status changes
    "membership_status_logs": [
        {
            "log_id": "LOG001",
            "member_id": "MEM001",
            "status": "active",
            "timestamp": "2023-01-15T10:00:00",
            "source": "registration"
        },
        {
            "log_id": "LOG002",
            "member_id": "MEM002",
            "status": "active",
            "timestamp": "2022-06-20T09:00:00",
            "source": "registration"
        },
        {
            "log_id": "LOG003",
            "member_id": "MEM002",
            "status": "suspended",
            "timestamp": "2024-02-01T11:00:00",
            "source": "admin_action"
        },
        {
            "log_id": "LOG004",
            "member_id": "MEM003",
            "status": "active",
            "timestamp": "2021-03-10T08:00:00",
            "source": "registration"
        },
        {
            "log_id": "LOG005",
            "member_id": "MEM003",
            "status": "expired",
            "timestamp": "2023-12-01T16:45:00",
            "source": "system_expiration"
        }
    ],
    
    # Identifier mappings - internal to external ID relationships
    "identifier_mappings": {
        "MEM001": {
            "internal_id": "MEM001",
            "external_id": "EXT-A100",
            "system_source": "partner_portal",
            "sync_timestamp": "2023-01-15T10:00:00"
        },
        "MEM002": {
            "internal_id": "MEM002",
            "external_id": "EXT-B200",
            "system_source": "partner_portal",
            "sync_timestamp": "2022-06-20T09:00:00"
        },
        "MEM003": {
            "internal_id": "MEM003",
            "external_id": "EXT-C300",
            "system_source": "legacy_system",
            "sync_timestamp": "2021-03-10T08:00:00"
        }
    },
    
    # External ID index for quick lookups
    "external_id_index": {
        "EXT-A100": "MEM001",
        "EXT-B200": "MEM002",
        "EXT-C300": "MEM003"
    },
    
    # Counters for generating unique IDs
    "next_member_id": 4,
    "next_log_id": 6,
    
    # Current user context
    "current_user": "system_admin",
    
    # Valid membership statuses
    "valid_statuses": ["active", "suspended", "expired", "canceled"]
}


class MembershipManagementSystem:
    """
    A membership management system environment that maintains member records,
    tracks status changes, and manages identifier mappings between internal
    and external systems.
    
    This environment supports operations for member registration, lookup,
    status management, and audit logging with full compliance to business
    constraints including unique external IDs and single active status per member.
    """
    
    def __init__(self) -> None:
        """
        Initialize the MembershipManagementSystem environment.
        
        Declares all state attributes with type hints and sets the API description.
        State is not populated here; use _load_scenario to initialize from a scenario.
        
        Args:
            None
        
        Returns:
            None
        """
        self.members: Dict[str, Dict[str, Any]] = {}
        self.membership_status_logs: List[Dict[str, Any]] = []
        self.identifier_mappings: Dict[str, Dict[str, Any]] = {}
        self.external_id_index: Dict[str, str] = {}
        self.next_member_id: int = 1
        self.next_log_id: int = 1
        self.current_user: str = ""
        self.valid_statuses: List[str] = []
        
        self._api_description: str = (
            "A membership management system for storing, organizing, and retrieving "
            "member information including personal details, membership status, and "
            "identifier mappings with support for lookup, update, and audit operations."
        )
    
    def _load_scenario(self, scenario: dict, long_context: bool = False) -> None:
        """
        Load initial state from a scenario dictionary.
        
        Populates all state attributes from the provided scenario. If a key is
        not present in the scenario, falls back to DEFAULT_STATE values.
        
        Args:
            scenario: A dictionary containing initial state values for the environment.
            long_context: Flag for extended context scenarios (reserved for future use).
        
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
        Retrieve the current state of the environment.
        
        Returns a dictionary containing all internal state variables, useful
        for debugging, testing, and state inspection.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: A dictionary with the following keys:
                - members: Dict of all member records keyed by internal ID
                - membership_status_logs: List of all status change log entries
                - identifier_mappings: Dict of internal-to-external ID mappings
                - external_id_index: Dict mapping external IDs to internal IDs
                - next_member_id: Counter for generating new member IDs
                - next_log_id: Counter for generating new log IDs
                - current_user: The current user context
                - valid_statuses: List of valid membership status values
        """
        return {
            "members": deepcopy(self.members),
            "membership_status_logs": deepcopy(self.membership_status_logs),
            "identifier_mappings": deepcopy(self.identifier_mappings),
            "external_id_index": deepcopy(self.external_id_index),
            "next_member_id": self.next_member_id,
            "next_log_id": self.next_log_id,
            "current_user": self.current_user,
            "valid_statuses": deepcopy(self.valid_statuses)
        }
    
    def _timestamp(self) -> str:
        """
        Generate a unified ISO format timestamp string.
        
        Args:
            None
        
        Returns:
            str: Current timestamp in ISO format (YYYY-MM-DDTHH:MM:SS).
        """
        return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    
    def _generate_member_id(self) -> str:
        """
        Generate a unique internal member ID.
        
        Args:
            None
        
        Returns:
            str: A new unique member ID in format 'MEMxxx'.
        """
        member_id = f"MEM{self.next_member_id:03d}"
        self.next_member_id += 1
        return member_id
    
    def _generate_log_id(self) -> str:
        """
        Generate a unique log entry ID.
        
        Args:
            None
        
        Returns:
            str: A new unique log ID in format 'LOGxxx'.
        """
        log_id = f"LOG{self.next_log_id:03d}"
        self.next_log_id += 1
        return log_id
    
    # ==================== QUERY OPERATIONS ====================
    
    def get_member_by_external_id(self, external_id: str) -> Dict[str, Any]:
        """
        Retrieve member details using an external ID.
        
        Resolves the external ID to an internal ID via identifier mapping,
        then returns the full member record.
        
        Args:
            external_id: The external identifier to look up.
        
        Returns:
            Dict[str, Any]: The member record if found, or an error dict if
                the external ID does not exist in the system.
        """
        if not external_id:
            return {"error": "external_id is required"}
        
        internal_id = self.external_id_index.get(external_id)
        if not internal_id:
            return {"error": f"External ID '{external_id}' not found in the system"}
        
        member = self.members.get(internal_id)
        if not member:
            return {"error": f"Member with internal ID '{internal_id}' not found"}
        
        return {"member": deepcopy(member)}
    
    def get_member_by_internal_id(self, member_id: str) -> Dict[str, Any]:
        """
        Retrieve member details directly using the internal member_id.
        
        Args:
            member_id: The internal member identifier to look up.
        
        Returns:
            Dict[str, Any]: The member record if found, or an error dict if
                the member ID does not exist.
        """
        if not member_id:
            return {"error": "member_id is required"}
        
        member = self.members.get(member_id)
        if not member:
            return {"error": f"Member with ID '{member_id}' not found"}
        
        return {"member": deepcopy(member)}
    
    def batch_lookup_members_by_external_id(
        self, external_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Retrieve multiple members given a list of external IDs.
        
        Args:
            external_ids: List of external identifiers to look up.
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - found: List of member records that were successfully retrieved
                - not_found: List of external IDs that could not be resolved
        """
        if not external_ids:
            return {"error": "external_ids list is required"}
        
        if not isinstance(external_ids, list):
            return {"error": "external_ids must be a list"}
        
        found = []
        not_found = []
        
        for ext_id in external_ids:
            internal_id = self.external_id_index.get(ext_id)
            if internal_id and internal_id in self.members:
                found.append(deepcopy(self.members[internal_id]))
            else:
                not_found.append(ext_id)
        
        return {"found": found, "not_found": not_found}
    
    def validate_identifier_type(self, identifier: str) -> Dict[str, Any]:
        """
        Confirm whether a given ID corresponds to a valid external or internal
        identifier in the system.
        
        Args:
            identifier: The identifier string to validate.
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - valid: Boolean indicating if the identifier exists
                - identifier_type: 'internal', 'external', or 'unknown'
                - resolved_member_id: The internal member ID if found
        """
        if not identifier:
            return {"error": "identifier is required"}
        
        # Check if it's an internal ID
        if identifier in self.members:
            return {
                "valid": True,
                "identifier_type": "internal",
                "resolved_member_id": identifier
            }
        
        # Check if it's an external ID
        if identifier in self.external_id_index:
            return {
                "valid": True,
                "identifier_type": "external",
                "resolved_member_id": self.external_id_index[identifier]
            }
        
        return {
            "valid": False,
            "identifier_type": "unknown",
            "resolved_member_id": None
        }
    
    def check_membership_status(self, member_id: str) -> Dict[str, Any]:
        """
        Return the current membership status of a member.
        
        Args:
            member_id: The internal member ID to check.
        
        Returns:
            Dict[str, Any]: A dictionary containing the member_id and their
                current membership_status, or an error if not found.
        """
        if not member_id:
            return {"error": "member_id is required"}
        
        member = self.members.get(member_id)
        if not member:
            return {"error": f"Member with ID '{member_id}' not found"}
        
        return {
            "member_id": member_id,
            "membership_status": member["membership_status"]
        }
    
    def get_membership_status_history(self, member_id: str) -> Dict[str, Any]:
        """
        Retrieve the chronological log of status changes for a member.
        
        Args:
            member_id: The internal member ID to get history for.
        
        Returns:
            Dict[str, Any]: A dictionary containing the member_id and a list
                of status log entries sorted by timestamp.
        """
        if not member_id:
            return {"error": "member_id is required"}
        
        if member_id not in self.members:
            return {"error": f"Member with ID '{member_id}' not found"}
        
        history = [
            deepcopy(log) for log in self.membership_status_logs
            if log["member_id"] == member_id
        ]
        
        # Sort by timestamp
        history.sort(key=lambda x: x["timestamp"])
        
        return {"member_id": member_id, "status_history": history}
    
    def list_all_external_identifiers(self) -> Dict[str, Any]:
        """
        List all currently registered external IDs in the system.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - external_ids: List of all registered external identifiers
                - count: Total number of external identifiers
        """
        external_ids = list(self.external_id_index.keys())
        return {"external_ids": external_ids, "count": len(external_ids)}
    
    def get_identifier_mapping(self, member_id: str) -> Dict[str, Any]:
        """
        Retrieve the mapping between internal and external IDs for a given member.
        
        Args:
            member_id: The internal member ID to get mapping for.
        
        Returns:
            Dict[str, Any]: The identifier mapping record or an error if not found.
        """
        if not member_id:
            return {"error": "member_id is required"}
        
        mapping = self.identifier_mappings.get(member_id)
        if not mapping:
            return {"error": f"No identifier mapping found for member '{member_id}'"}
        
        return {"mapping": deepcopy(mapping)}
    
    def list_members(self, status_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        List all members, optionally filtered by status.
        
        Args:
            status_filter: Optional status to filter by.
        
        Returns:
            Dict[str, Any]: List of members matching the filter.
        """
        if status_filter:
            if status_filter not in self.valid_statuses:
                return {
                    "error": f"Invalid status_filter '{status_filter}'. "
                             f"Valid statuses are: {', '.join(self.valid_statuses)}"
                }
            filtered_members = [
                deepcopy(mdata) for mdata in self.members.values()
                if mdata["membership_status"] == status_filter
            ]
        else:
            filtered_members = [deepcopy(mdata) for mdata in self.members.values()]
        
        return {
            "members": filtered_members,
            "total_count": len(filtered_members),
            "filter_applied": status_filter
        }
    
    # ==================== STATE CHANGE OPERATIONS ====================
    
    def register_new_member(
        self,
        external_id: str,
        first_name: str,
        last_name: str,
        email: str,
        phone: Optional[str] = None,
        system_source: str = "direct_registration"
    ) -> Dict[str, Any]:
        """
        Add a new member to the system with a unique internal ID and external ID.
        
        Enforces external ID uniqueness as per system constraints.
        
        Args:
            external_id: Unique external identifier for the new member.
            first_name: Member's first name.
            last_name: Member's last name.
            email: Member's email address.
            phone: Optional phone number.
            system_source: Source system for the registration.
        
        Returns:
            Dict[str, Any]: The newly created member record or an error if
                the external ID already exists.
        """
        # Validate required fields
        if not external_id:
            return {"error": "external_id is required"}
        if not first_name:
            return {"error": "first_name is required"}
        if not last_name:
            return {"error": "last_name is required"}
        if not email:
            return {"error": "email is required"}
        
        # Constraint: Each external_id must be unique
        if external_id in self.external_id_index:
            return {"error": f"External ID '{external_id}' already exists in the system"}
        
        timestamp = self._timestamp()
        member_id = self._generate_member_id()
        
        # Create member record
        new_member = {
            "member_id": member_id,
            "external_id": external_id,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": phone or "",
            "membership_status": "active",
            "join_date": timestamp,
            "last_updated": timestamp
        }
        
        # Create identifier mapping
        mapping = {
            "internal_id": member_id,
            "external_id": external_id,
            "system_source": system_source,
            "sync_timestamp": timestamp
        }
        
        # Create initial status log
        log_entry = {
            "log_id": self._generate_log_id(),
            "member_id": member_id,
            "status": "active",
            "timestamp": timestamp,
            "source": "registration"
        }
        
        # Update state
        self.members[member_id] = new_member
        self.external_id_index[external_id] = member_id
        self.identifier_mappings[member_id] = mapping
        self.membership_status_logs.append(log_entry)
        
        return {"success": True, "member": deepcopy(new_member)}
    
    def update_member_details(
        self,
        member_id: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Modify personal information for an existing member.
        
        Only provided fields will be updated; None values are ignored.
        
        Args:
            member_id: The internal ID of the member to update.
            first_name: New first name (optional).
            last_name: New last name (optional).
            email: New email address (optional).
            phone: New phone number (optional).
        
        Returns:
            Dict[str, Any]: The updated member record or an error if not found.
        """
        if not member_id:
            return {"error": "member_id is required"}
        
        member = self.members.get(member_id)
        if not member:
            return {"error": f"Member with ID '{member_id}' not found"}
        
        # Update provided fields
        if first_name is not None:
            member["first_name"] = first_name
        if last_name is not None:
            member["last_name"] = last_name
        if email is not None:
            member["email"] = email
        if phone is not None:
            member["phone"] = phone
        
        member["last_updated"] = self._timestamp()
        
        return {"success": True, "member": deepcopy(member)}
    
    def update_membership_status(
        self,
        member_id: str,
        new_status: str,
        source: str = "admin_action"
    ) -> Dict[str, Any]:
        """
        Change a member's status and log the change.
        
        Ensures only one active status exists and validates the new status.
        
        Args:
            member_id: The internal ID of the member to update.
            new_status: The new membership status (active, suspended, expired, canceled).
            source: The source of the status change for audit logging.
        
        Returns:
            Dict[str, Any]: Success status with old and new status, or an error.
        """
        if not member_id:
            return {"error": "member_id is required"}
        if not new_status:
            return {"error": "new_status is required"}
        
        member = self.members.get(member_id)
        if not member:
            return {"error": f"Member with ID '{member_id}' not found"}
        
        # Validate status value
        if new_status not in self.valid_statuses:
            return {
                "error": f"Invalid status '{new_status}'. "
                         f"Valid statuses are: {', '.join(self.valid_statuses)}"
            }
        
        old_status = member["membership_status"]
        timestamp = self._timestamp()
        
        # Update member status
        member["membership_status"] = new_status
        member["last_updated"] = timestamp
        
        # Log the status change
        log_entry = {
            "log_id": self._generate_log_id(),
            "member_id": member_id,
            "status": new_status,
            "timestamp": timestamp,
            "source": source
        }
        self.membership_status_logs.append(log_entry)
        
        return {
            "success": True,
            "member_id": member_id,
            "old_status": old_status,
            "new_status": new_status
        }
    
    def log_status_change(
        self,
        member_id: str,
        status: str,
        source: str
    ) -> Dict[str, Any]:
        """
        Record a membership status transition in the status logs.
        
        This is a standalone logging operation that does not modify member status.
        Use update_membership_status for combined status change and logging.
        
        Args:
            member_id: The internal ID of the member.
            status: The status value to log.
            source: The source or reason for the status change.
        
        Returns:
            Dict[str, Any]: The created log entry or an error.
        """
        if not member_id:
            return {"error": "member_id is required"}
        if not status:
            return {"error": "status is required"}
        if not source:
            return {"error": "source is required"}
        
        if member_id not in self.members:
            return {"error": f"Member with ID '{member_id}' not found"}
        
        if status not in self.valid_statuses:
            return {
                "error": f"Invalid status '{status}'. "
                         f"Valid statuses are: {', '.join(self.valid_statuses)}"
            }
        
        log_entry = {
            "log_id": self._generate_log_id(),
            "member_id": member_id,
            "status": status,
            "timestamp": self._timestamp(),
            "source": source
        }
        self.membership_status_logs.append(log_entry)
        
        return {"success": True, "log_entry": deepcopy(log_entry)}
    
    def sync_identifier_mapping(
        self,
        internal_id: str,
        external_id: str,
        system_source: str
    ) -> Dict[str, Any]:
        """
        Update or create a mapping between an internal ID and an external ID.
        
        Args:
            internal_id: The internal member ID.
            external_id: The external identifier from a partner system.
            system_source: The name of the partner system.
        
        Returns:
            Dict[str, Any]: The updated or created mapping, or an error.
        """
        if not internal_id:
            return {"error": "internal_id is required"}
        if not external_id:
            return {"error": "external_id is required"}
        if not system_source:
            return {"error": "system_source is required"}
        
        # Verify member exists
        if internal_id not in self.members:
            return {"error": f"Member with ID '{internal_id}' not found"}
        
        # Check if external_id is already used by another member
        existing_internal = self.external_id_index.get(external_id)
        if existing_internal and existing_internal != internal_id:
            return {
                "error": f"External ID '{external_id}' is already assigned to "
                         f"member '{existing_internal}'"
            }
        
        timestamp = self._timestamp()
        
        # Remove old external ID mapping if member had a different one
        member = self.members[internal_id]
        old_external_id = member.get("external_id")
        if old_external_id and old_external_id != external_id:
            if old_external_id in self.external_id_index:
                del self.external_id_index[old_external_id]
        
        # Update member's external_id
        member["external_id"] = external_id
        member["last_updated"] = timestamp
        
        # Update or create mapping
        mapping = {
            "internal_id": internal_id,
            "external_id": external_id,
            "system_source": system_source,
            "sync_timestamp": timestamp
        }
        self.identifier_mappings[internal_id] = mapping
        self.external_id_index[external_id] = internal_id
        
        return {"success": True, "mapping": deepcopy(mapping)}
    
    def deactivate_member(
        self,
        member_id: str,
        deactivation_type: str = "canceled",
        source: str = "admin_action"
    ) -> Dict[str, Any]:
        """
        Set membership status to "canceled" or "expired" with audit logging.
        
        Args:
            member_id: The internal ID of the member to deactivate.
            deactivation_type: Either "canceled" or "expired".
            source: The source of the deactivation for audit logging.
        
        Returns:
            Dict[str, Any]: Success status or an error.
        """
        if not member_id:
            return {"error": "member_id is required"}
        
        member = self.members.get(member_id)
        if not member:
            return {"error": f"Member with ID '{member_id}' not found"}
        
        valid_deactivation_types = ["canceled", "expired"]
        if deactivation_type not in valid_deactivation_types:
            return {
                "error": f"Invalid deactivation_type '{deactivation_type}'. "
                         f"Must be one of: {', '.join(valid_deactivation_types)}"
            }
        
        # Check if already deactivated
        if member["membership_status"] in valid_deactivation_types:
            return {
                "error": f"Member is already deactivated with status "
                         f"'{member['membership_status']}'"
            }
        
        old_status = member["membership_status"]
        timestamp = self._timestamp()
        
        # Update status
        member["membership_status"] = deactivation_type
        member["last_updated"] = timestamp
        
        # Log the change
        log_entry = {
            "log_id": self._generate_log_id(),
            "member_id": member_id,
            "status": deactivation_type,
            "timestamp": timestamp,
            "source": source
        }
        self.membership_status_logs.append(log_entry)
        
        return {
            "success": True,
            "member_id": member_id,
            "old_status": old_status,
            "new_status": deactivation_type
        }
    
    def reactivate_member(
        self,
        member_id: str,
        source: str = "admin_action"
    ) -> Dict[str, Any]:
        """
        Restore a deactivated member's status to "active".
        
        Only members with "canceled", "expired", or "suspended" status can be reactivated.
        
        Args:
            member_id: The internal ID of the member to reactivate.
            source: The source of the reactivation for audit logging.
        
        Returns:
            Dict[str, Any]: Success status or an error if reactivation is not allowed.
        """
        if not member_id:
            return {"error": "member_id is required"}
        
        member = self.members.get(member_id)
        if not member:
            return {"error": f"Member with ID '{member_id}' not found"}
        
        current_status = member["membership_status"]
        
        # Check if already active
        if current_status == "active":
            return {"error": "Member is already active"}
        
        # Reactivation allowed from these statuses
        reactivatable_statuses = ["canceled", "expired", "suspended"]
        if current_status not in reactivatable_statuses:
            return {
                "error": f"Cannot reactivate member with status '{current_status}'"
            }
        
        timestamp = self._timestamp()
        
        # Update status
        member["membership_status"] = "active"
        member["last_updated"] = timestamp
        
        # Log the change
        log_entry = {
            "log_id": self._generate_log_id(),
            "member_id": member_id,
            "status": "active",
            "timestamp": timestamp,
            "source": source
        }
        self.membership_status_logs.append(log_entry)
        
        return {
            "success": True,
            "member_id": member_id,
            "old_status": current_status,
            "new_status": "active",
            "timestamp": timestamp,
            "log_id": log_entry["log_id"]
        }
    
    def get_membership_history(self, member_id: str) -> dict:
        """Get the membership status history for a member."""
        if member_id not in self.members:
            return {"error": "Member not found"}
        
        history = [
            log for log in self.membership_status_logs
            if log["member_id"] == member_id
        ]
        
        return {
            "member_id": member_id,
            "history": sorted(history, key=lambda x: x["timestamp"]),
            "total_entries": len(history)
        }
    
    def get_members_by_status(self, status: str) -> list:
        """Get all members with a specific status."""
        return [
            {"member_id": mid, **data}
            for mid, data in self.members.items()
            if data.get("membership_status") == status
        ]
    
    def _timestamp(self) -> str:
        """Generate current timestamp."""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"
    
    def _generate_log_id(self) -> str:
        """Generate a unique log ID."""
        import uuid
        return f"log_{uuid.uuid4().hex[:12]}"


__TEST_CASES__ = [
    {
        "name": "test_reactivate_suspended_member",
        "setup": lambda mgr: (
            mgr.members.update({"M001": {"membership_status": "suspended", "name": "John"}}),
        ),
        "input": {"member_id": "M001", "source": "admin"},
        "method": "reactivate_membership",
        "expected_keys": ["success", "member_id", "old_status", "new_status", "timestamp", "log_id"],
        "expected_values": {"success": True, "old_status": "suspended", "new_status": "active"}
    },
    {
        "name": "test_reactivate_expired_member",
        "setup": lambda mgr: (
            mgr.members.update({"M002": {"membership_status": "expired", "name": "Jane"}}),
        ),
        "input": {"member_id": "M002", "source": "renewal"},
        "method": "reactivate_membership",
        "expected_keys": ["success", "member_id", "old_status", "new_status", "timestamp", "log_id"],
        "expected_values": {"success": True, "old_status": "expired", "new_status": "active"}
    },
    {
        "name": "test_reactivate_nonexistent_member",
        "setup": lambda mgr: None,
        "input": {"member_id": "M999", "source": "admin"},
        "method": "reactivate_membership",
        "expected_keys": ["error"],
        "expected_values": {"error": "Member not found"}
    },
    {
        "name": "test_reactivate_already_active_member",
        "setup": lambda mgr: (
            mgr.members.update({"M003": {"membership_status": "active", "name": "Bob"}}),
        ),
        "input": {"member_id": "M003", "source": "admin"},
        "method": "reactivate_membership",
        "expected_keys": ["error"],
        "expected_values": {}
    },
    {
        "name": "test_get_membership_history",
        "setup": lambda mgr: (
            mgr.members.update({"M004": {"membership_status": "active", "name": "Alice"}}),
            mgr.membership_status_logs.extend([
                {"log_id": "log_001", "member_id": "M004", "status": "active", "timestamp": "2024-01-01T00:00:00Z", "source": "signup"},
                {"log_id": "log_002", "member_id": "M004", "status": "suspended", "timestamp": "2024-02-01T00:00:00Z", "source": "admin"}
            ]),
        ),
        "input": {"member_id": "M004"},
        "method": "get_membership_history",
        "expected_keys": ["member_id", "history", "total_entries"],
        "expected_values": {"member_id": "M004", "total_entries": 2}
    },
    {
        "name": "test_get_members_by_status",
        "setup": lambda mgr: (
            mgr.members.update({
                "M005": {"membership_status": "active", "name": "Tom"},
                "M006": {"membership_status": "suspended", "name": "Jerry"},
                "M007": {"membership_status": "active", "name": "Spike"}
            }),
        ),
        "input": {"status": "active"},
        "method": "get_members_by_status",
        "expected_length": 2
    }
]