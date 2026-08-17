"""
Insurance Policy Management System Environment API

This environment is a digital insurance policy management system used by insurers and their customers.
It maintains stateful records of individual policies, including coverage details, insured parties,
limits, exclusions, and active dates.
"""

from copy import deepcopy
from typing import Dict, List, Optional, Any
from datetime import datetime, date


DEFAULT_STATE: Dict[str, Any] = {
    # Current user context
    "current_user_account_id": "user_001",
    "current_date": "2024-06-15",
    
    # Insured Parties
    "insured_parties": [
        {
            "insured_party_id": "ip_001",
            "name": "John Smith",
            "contact_info": {"email": "john.smith@email.com", "phone": "555-0101"},
            "user_account_id": "user_001"
        },
        {
            "insured_party_id": "ip_002",
            "name": "Jane Doe",
            "contact_info": {"email": "jane.doe@email.com", "phone": "555-0102"},
            "user_account_id": "user_002"
        },
        {
            "insured_party_id": "ip_003",
            "name": "Acme Corporation",
            "contact_info": {"email": "insurance@acme.com", "phone": "555-0103"},
            "user_account_id": "user_003"
        }
    ],
    
    # Policies
    "policies": [
        {
            "policy_id": "pol_001",
            "policy_number": "HLT-2024-001",
            "coverage_details": "Comprehensive health insurance coverage",
            "exclusions": ["exc_001", "exc_002"],
            "coverage_limits": {"annual_max": 500000, "per_incident": 50000},
            "active_dates": {"start": "2024-01-01", "end": "2024-12-31"},
            "insured_party_id": "ip_001",
            "type": "health",
            "status": "active",
            "beneficiaries": []
        },
        {
            "policy_id": "pol_002",
            "policy_number": "AUT-2024-002",
            "coverage_details": "Full auto insurance with collision and liability",
            "exclusions": ["exc_003"],
            "coverage_limits": {"annual_max": 100000, "per_incident": 25000},
            "active_dates": {"start": "2024-03-01", "end": "2025-02-28"},
            "insured_party_id": "ip_002",
            "type": "auto",
            "status": "active",
            "beneficiaries": []
        },
        {
            "policy_id": "pol_003",
            "policy_number": "BUS-2024-003",
            "coverage_details": "Business liability insurance",
            "exclusions": ["exc_004"],
            "coverage_limits": {"annual_max": 1000000, "per_incident": 100000},
            "active_dates": {"start": "2023-06-01", "end": "2024-05-31"},
            "insured_party_id": "ip_003",
            "type": "business",
            "status": "expired",
            "beneficiaries": []
        }
    ],
    
    # Coverage Items
    "coverage_items": [
        {
            "coverage_item_id": "cov_001",
            "policy_id": "pol_001",
            "expense_type": "hospitalization",
            "coverage_limit": 100000,
            "deductible": 500,
            "active": True
        },
        {
            "coverage_item_id": "cov_002",
            "policy_id": "pol_001",
            "expense_type": "prescription_drugs",
            "coverage_limit": 10000,
            "deductible": 100,
            "active": True
        },
        {
            "coverage_item_id": "cov_003",
            "policy_id": "pol_001",
            "expense_type": "dental",
            "coverage_limit": 5000,
            "deductible": 200,
            "active": True
        },
        {
            "coverage_item_id": "cov_004",
            "policy_id": "pol_002",
            "expense_type": "collision",
            "coverage_limit": 50000,
            "deductible": 1000,
            "active": True
        },
        {
            "coverage_item_id": "cov_005",
            "policy_id": "pol_002",
            "expense_type": "liability",
            "coverage_limit": 100000,
            "deductible": 0,
            "active": True
        },
        {
            "coverage_item_id": "cov_006",
            "policy_id": "pol_003",
            "expense_type": "general_liability",
            "coverage_limit": 500000,
            "deductible": 5000,
            "active": True
        }
    ],
    
    # Exclusions
    "exclusions": [
        {
            "exclusion_id": "exc_001",
            "policy_id": "pol_001",
            "excluded_expense_type": "cosmetic_surgery",
            "exclusion_details": "Elective cosmetic procedures not medically necessary"
        },
        {
            "exclusion_id": "exc_002",
            "policy_id": "pol_001",
            "excluded_expense_type": "experimental_treatment",
            "exclusion_details": "Treatments not approved by regulatory authorities"
        },
        {
            "exclusion_id": "exc_003",
            "policy_id": "pol_002",
            "excluded_expense_type": "racing",
            "exclusion_details": "Damage incurred during racing or speed contests"
        },
        {
            "exclusion_id": "exc_004",
            "policy_id": "pol_003",
            "excluded_expense_type": "intentional_acts",
            "exclusion_details": "Liability from intentional harmful acts"
        }
    ],
    
    # ID counters for new records
    "next_coverage_item_id": 7,
    "next_exclusion_id": 5
}


class InsurancePolicyManagementSystem:
    """
    A digital insurance policy management system environment API.
    
    This system allows authorized users to view, modify, and query insurance policies,
    including coverage details, exclusions, limits, and active dates.
    """
    
    def __init__(self) -> None:
        """
        Initialize the Insurance Policy Management System.
        
        Declares all state attributes and sets the API description.
        
        Returns:
            None
        """
        self._api_description: str = "Insurance policy management system for viewing and managing insurance coverage, exclusions, and policy details."
        
        # User context
        self.current_user_account_id: str = ""
        self.current_date: str = ""
        
        # Entity collections
        self.insured_parties: List[Dict[str, Any]] = []
        self.policies: List[Dict[str, Any]] = []
        self.coverage_items: List[Dict[str, Any]] = []
        self.exclusions: List[Dict[str, Any]] = []
        
        # ID counters
        self.next_coverage_item_id: int = 1
        self.next_exclusion_id: int = 1
    
    def _timestamp(self) -> str:
        """
        Generate a standardized ISO format timestamp string.
        
        Args:
            None
        
        Returns:
            str: Current timestamp in ISO format.
        """
        return datetime.now().isoformat()
    
    def _get_current_date(self) -> date:
        """
        Parse and return the current date from state.
        
        Args:
            None
        
        Returns:
            date: The current date object.
        """
        return datetime.strptime(self.current_date, "%Y-%m-%d").date()
    
    def _load_scenario(self, scenario: dict, long_context: bool = False) -> None:
        """
        Load initial state from a scenario dictionary.
        
        Args:
            scenario: Dictionary containing initial state values.
            long_context: Flag for long context scenarios (unused in this implementation).
        
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
            Dict[str, Any]: A dictionary containing all internal state variables including
                current_user_account_id, current_date, insured_parties, policies,
                coverage_items, exclusions, and ID counters.
        """
        return {
            "current_user_account_id": self.current_user_account_id,
            "current_date": self.current_date,
            "insured_parties": deepcopy(self.insured_parties),
            "policies": deepcopy(self.policies),
            "coverage_items": deepcopy(self.coverage_items),
            "exclusions": deepcopy(self.exclusions),
            "next_coverage_item_id": self.next_coverage_item_id,
            "next_exclusion_id": self.next_exclusion_id
        }
    
    # ==================== QUERY OPERATIONS ====================
    
    def get_policy_by_policy_number(self, policy_number: str) -> Dict[str, Any]:
        """
        Retrieve policy details using a policy number.
        
        Args:
            policy_number: The unique policy number to search for.
        
        Returns:
            Dict[str, Any]: The policy details if found, or an error dictionary.
        """
        for policy in self.policies:
            if policy["policy_number"] == policy_number:
                # Check authorization
                auth_check = self.is_authorized_user_for_policy(policy["policy_id"])
                if auth_check.get("authorized", False):
                    return {"policy": deepcopy(policy)}
                else:
                    return {"error": "User not authorized to view this policy"}
        return {"error": f"Policy with number '{policy_number}' not found"}
    
    def get_policies_by_user_account(self, user_account_id: str) -> Dict[str, Any]:
        """
        Retrieve all policies associated with a user account.
        
        Args:
            user_account_id: The user account ID to search policies for.
        
        Returns:
            Dict[str, Any]: A dictionary containing list of policies or an error.
        """
        # Find insured party for this user
        insured_party_ids = []
        for ip in self.insured_parties:
            if ip["user_account_id"] == user_account_id:
                insured_party_ids.append(ip["insured_party_id"])
        
        if not insured_party_ids:
            return {"policies": []}
        
        user_policies = []
        for policy in self.policies:
            if policy["insured_party_id"] in insured_party_ids:
                user_policies.append(deepcopy(policy))
        
        return {"policies": user_policies}
    
    def check_policy_active(self, policy_id: str) -> Dict[str, Any]:
        """
        Determine if a policy is currently active by comparing today's date to active_dates.
        
        Args:
            policy_id: The ID of the policy to check.
        
        Returns:
            Dict[str, Any]: Dictionary with 'active' boolean status or an error.
        """
        policy = None
        for p in self.policies:
            if p["policy_id"] == policy_id:
                policy = p
                break
        
        if not policy:
            return {"error": f"Policy with ID '{policy_id}' not found"}
        
        current = self._get_current_date()
        start_date = datetime.strptime(policy["active_dates"]["start"], "%Y-%m-%d").date()
        end_date = datetime.strptime(policy["active_dates"]["end"], "%Y-%m-%d").date()
        
        is_active = start_date <= current <= end_date
        return {"active": is_active, "policy_id": policy_id}
    
    def is_authorized_user_for_policy(self, policy_id: str, user_account_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Verify if a user account is authorized to view or edit a specific policy.
        
        Args:
            policy_id: The ID of the policy to check authorization for.
            user_account_id: The user account to verify. If None, uses current user.
        
        Returns:
            Dict[str, Any]: Dictionary with 'authorized' boolean or an error.
        """
        if user_account_id is None:
            user_account_id = self.current_user_account_id
        
        # Find the policy
        policy = None
        for p in self.policies:
            if p["policy_id"] == policy_id:
                policy = p
                break
        
        if not policy:
            return {"error": f"Policy with ID '{policy_id}' not found"}
        
        # Find the insured party for this policy
        insured_party = None
        for ip in self.insured_parties:
            if ip["insured_party_id"] == policy["insured_party_id"]:
                insured_party = ip
                break
        
        if not insured_party:
            return {"error": "Insured party not found for this policy"}
        
        # Check if user is the insured party
        authorized = insured_party["user_account_id"] == user_account_id
        return {"authorized": authorized, "policy_id": policy_id, "user_account_id": user_account_id}
    
    def get_coverage_items_for_policy(self, policy_id: str) -> Dict[str, Any]:
        """
        Retrieve all coverage items for a given policy.
        
        Args:
            policy_id: The ID of the policy.
        
        Returns:
            Dict[str, Any]: Dictionary with list of coverage items or an error.
        """
        # Check authorization
        auth_check = self.is_authorized_user_for_policy(policy_id)
        if "error" in auth_check:
            return auth_check
        if not auth_check.get("authorized", False):
            return {"error": "User not authorized to view this policy"}
        
        items = []
        for item in self.coverage_items:
            if item["policy_id"] == policy_id:
                items.append(deepcopy(item))
        
        return {"coverage_items": items, "policy_id": policy_id}
    
    def get_exclusions_for_policy(self, policy_id: str) -> Dict[str, Any]:
        """
        Retrieve all exclusions for a specific policy.
        
        Args:
            policy_id: The ID of the policy.
        
        Returns:
            Dict[str, Any]: Dictionary with list of exclusions or an error.
        """
        # Check authorization
        auth_check = self.is_authorized_user_for_policy(policy_id)
        if "error" in auth_check:
            return auth_check
        if not auth_check.get("authorized", False):
            return {"error": "User not authorized to view this policy"}
        
        policy_exclusions = []
        for exc in self.exclusions:
            if exc["policy_id"] == policy_id:
                policy_exclusions.append(deepcopy(exc))
        
        return {"exclusions": policy_exclusions, "policy_id": policy_id}
    
    def get_covered_expenses_filtered(self, policy_id: str) -> Dict[str, Any]:
        """
        Return a list of expense types genuinely covered by the policy, excluding those in exclusions.
        
        Args:
            policy_id: The ID of the policy.
        
        Returns:
            Dict[str, Any]: Dictionary with list of covered expense types or an error.
        """
        # Check authorization
        auth_check = self.is_authorized_user_for_policy(policy_id)
        if "error" in auth_check:
            return auth_check
        if not auth_check.get("authorized", False):
            return {"error": "User not authorized to view this policy"}
        
        # Check if policy is active
        active_check = self.check_policy_active(policy_id)
        if "error" in active_check:
            return active_check
        if not active_check.get("active", False):
            return {"error": "Policy is not currently active", "covered_expenses": []}
        
        # Get excluded expense types
        excluded_types = set()
        for exc in self.exclusions:
            if exc["policy_id"] == policy_id:
                excluded_types.add(exc["excluded_expense_type"])
        
        # Get covered expenses filtering out excluded ones
        covered_expenses = []
        for item in self.coverage_items:
            if item["policy_id"] == policy_id and item["active"]:
                if item["expense_type"] not in excluded_types:
                    covered_expenses.append(item["expense_type"])
        
        return {"covered_expenses": covered_expenses, "policy_id": policy_id}
    
    def get_coverage_limits_and_deductibles(self, policy_id: str) -> Dict[str, Any]:
        """
        For a given policy, provide coverage limits and deductibles for each expense type.
        
        Args:
            policy_id: The ID of the policy.
        
        Returns:
            Dict[str, Any]: Dictionary with coverage limits and deductibles per expense type.
        """
        # Check authorization
        auth_check = self.is_authorized_user_for_policy(policy_id)
        if "error" in auth_check:
            return auth_check
        if not auth_check.get("authorized", False):
            return {"error": "User not authorized to view this policy"}
        
        limits_deductibles = []
        for item in self.coverage_items:
            if item["policy_id"] == policy_id:
                limits_deductibles.append({
                    "expense_type": item["expense_type"],
                    "coverage_limit": item["coverage_limit"],
                    "deductible": item["deductible"],
                    "active": item["active"]
                })
        
        return {"coverage_limits_and_deductibles": limits_deductibles, "policy_id": policy_id}
    
    def get_policy_details(self, policy_id: str) -> Dict[str, Any]:
        """
        View full details of a policy including coverage, exclusions, limits, active dates, insured party.
        
        Args:
            policy_id: The ID of the policy.
        
        Returns:
            Dict[str, Any]: Complete policy details or an error.
        """
        # Check authorization
        auth_check = self.is_authorized_user_for_policy(policy_id)
        if "error" in auth_check:
            return auth_check
        if not auth_check.get("authorized", False):
            return {"error": "User not authorized to view this policy"}
        
        # Find policy
        policy = None
        for p in self.policies:
            if p["policy_id"] == policy_id:
                policy = deepcopy(p)
                break
        
        if not policy:
            return {"error": f"Policy with ID '{policy_id}' not found"}
        
        # Get insured party
        insured_party = None
        for ip in self.insured_parties:
            if ip["insured_party_id"] == policy["insured_party_id"]:
                insured_party = deepcopy(ip)
                break
        
        # Get coverage items
        coverage_items = []
        for item in self.coverage_items:
            if item["policy_id"] == policy_id:
                coverage_items.append(deepcopy(item))
        
        # Get exclusions
        policy_exclusions = []
        for exc in self.exclusions:
            if exc["policy_id"] == policy_id:
                policy_exclusions.append(deepcopy(exc))
        
        # Check if active
        active_check = self.check_policy_active(policy_id)
        
        return {
            "policy": policy,
            "insured_party": insured_party,
            "coverage_items": coverage_items,
            "exclusions": policy_exclusions,
            "is_active": active_check.get("active", False)
        }
    
    def get_insured_party_by_user_account_id(self, user_account_id: str) -> Dict[str, Any]:
        """
        Return the insured party entity associated with a user account.
        
        Args:
            user_account_id: The user account ID.
        
        Returns:
            Dict[str, Any]: The insured party details or an error.
        """
        for ip in self.insured_parties:
            if ip["user_account_id"] == user_account_id:
                return {"insured_party": deepcopy(ip)}
        
        return {"error": f"No insured party found for user account '{user_account_id}'"}
    
    def get_policy_active_dates(self, policy_id: str) -> Dict[str, Any]:
        """
        Query the start and end date of the policy's active period.
        
        Args:
            policy_id: The ID of the policy.
        
        Returns:
            Dict[str, Any]: Dictionary with active dates or an error.
        """
        # Check authorization
        auth_check = self.is_authorized_user_for_policy(policy_id)
        if "error" in auth_check:
            return auth_check
        if not auth_check.get("authorized", False):
            return {"error": "User not authorized to view this policy"}
        
        for policy in self.policies:
            if policy["policy_id"] == policy_id:
                return {
                    "policy_id": policy_id,
                    "active_dates": deepcopy(policy["active_dates"])
                }
        
        return {"error": f"Policy with ID '{policy_id}' not found"}
    
    # ==================== STATE CHANGE OPERATIONS ====================
    
    def add_coverage_item_to_policy(
        self,
        policy_id: str,
        expense_type: str,
        coverage_limit: float,
        deductible: float
    ) -> Dict[str, Any]:
        """
        Add a new covered expense to a policy.
        
        Args:
            policy_id: The ID of the policy.
            expense_type: The type of expense to cover.
            coverage_limit: The maximum coverage amount.
            deductible: The deductible amount.
        
        Returns:
            Dict[str, Any]: The created coverage item or an error.
        """
        # Check authorization
        auth_check = self.is_authorized_user_for_policy(policy_id)
        if "error" in auth_check:
            return auth_check
        if not auth_check.get("authorized", False):
            return {"error": "User not authorized to modify this policy"}
        
        # Check policy exists
        policy_exists = False
        for p in self.policies:
            if p["policy_id"] == policy_id:
                policy_exists = True
                break
        
        if not policy_exists:
            return {"error": f"Policy with ID '{policy_id}' not found"}
        
        # Check if expense type already exists for this policy
        for item in self.coverage_items:
            if item["policy_id"] == policy_id and item["expense_type"] == expense_type:
                return {"error": f"Coverage item for expense type '{expense_type}' already exists in this policy"}
        
        # Create new coverage item
        new_item = {
            "coverage_item_id": f"cov_{self.next_coverage_item_id:03d}",
            "policy_id": policy_id,
            "expense_type": expense_type,
            "coverage_limit": coverage_limit,
            "deductible": deductible,
            "active": True
        }
        
        self.coverage_items.append(new_item)
        self.next_coverage_item_id += 1
        
        return {"success": True, "coverage_item": deepcopy(new_item), "timestamp": self._timestamp()}
    
    def remove_coverage_item_from_policy(self, coverage_item_id: str) -> Dict[str, Any]:
        """
        Remove a coverage item from a policy.
        
        Args:
            coverage_item_id: The ID of the coverage item to remove.
        
        Returns:
            Dict[str, Any]: Success status or an error.
        """
        # Find the coverage item
        item_index = None
        item = None
        for i, ci in enumerate(self.coverage_items):
            if ci["coverage_item_id"] == coverage_item_id:
                item_index = i
                item = ci
                break
        
        if item is None:
            return {"error": f"Coverage item with ID '{coverage_item_id}' not found"}
        
        # Check authorization
        auth_check = self.is_authorized_user_for_policy(item["policy_id"])
        if "error" in auth_check:
            return auth_check
        if not auth_check.get("authorized", False):
            return {"error": "User not authorized to modify this policy"}
        
        # Remove the item
        removed_item = self.coverage_items.pop(item_index)
        
        return {"success": True, "removed_item": deepcopy(removed_item), "timestamp": self._timestamp()}
    
    def add_exclusion_to_policy(
        self,
        policy_id: str,
        excluded_expense_type: str,
        exclusion_details: str
    ) -> Dict[str, Any]:
        """
        Add a new exclusion to a policy.
        
        Args:
            policy_id: The ID of the policy.
            excluded_expense_type: The expense type to exclude.
            exclusion_details: Description of the exclusion.
        
        Returns:
            Dict[str, Any]: The created exclusion or an error.
        """
        # Check authorization
        auth_check = self.is_authorized_user_for_policy(policy_id)
        if "error" in auth_check:
            return auth_check
        if not auth_check.get("authorized", False):
            return {"error": "User not authorized to modify this policy"}
        
        # Check policy exists
        policy = None
        for p in self.policies:
            if p["policy_id"] == policy_id:
                policy = p
                break
        
        if not policy:
            return {"error": f"Policy with ID '{policy_id}' not found"}
        
        # Check if exclusion already exists
        for exc in self.exclusions:
            if exc["policy_id"] == policy_id and exc["excluded_expense_type"] == excluded_expense_type:
                return {"error": f"Exclusion for expense type '{excluded_expense_type}' already exists in this policy"}
        
        # Create new exclusion
        new_exclusion = {
            "exclusion_id": f"exc_{self.next_exclusion_id:03d}",
            "policy_id": policy_id,
            "excluded_expense_type": excluded_expense_type,
            "exclusion_details": exclusion_details
        }
        
        self.exclusions.append(new_exclusion)
        self.next_exclusion_id += 1
        
        # Update policy's exclusion list
        policy["exclusions"].append(new_exclusion["exclusion_id"])
        
        return {"success": True, "exclusion": deepcopy(new_exclusion), "timestamp": self._timestamp()}
    
    def remove_exclusion_from_policy(self, exclusion_id: str) -> Dict[str, Any]:
        """
        Delete an exclusion from a policy.
        
        Args:
            exclusion_id: The ID of the exclusion to remove.
        
        Returns:
            Dict[str, Any]: Success status or an error.
        """
        # Find the exclusion
        exc_index = None
        exclusion = None
        for i, exc in enumerate(self.exclusions):
            if exc["exclusion_id"] == exclusion_id:
                exc_index = i
                exclusion = exc
                break
        
        if exclusion is None:
            return {"error": f"Exclusion with ID '{exclusion_id}' not found"}
        
        # Check authorization
        auth_check = self.is_authorized_user_for_policy(exclusion["policy_id"])
        if "error" in auth_check:
            return auth_check
        if not auth_check.get("authorized", False):
            return {"error": "User not authorized to modify this policy"}
        
        # Remove from exclusions list
        removed_exclusion = self.exclusions.pop(exc_index)
        
        # Update policy's exclusion list
        for policy in self.policies:
            if policy["policy_id"] == exclusion["policy_id"]:
                if exclusion_id in policy["exclusions"]:
                    policy["exclusions"].remove(exclusion_id)
                break
        
        return {"success": True, "removed_exclusion": deepcopy(removed_exclusion), "timestamp": self._timestamp()}
    
    def update_coverage_limit_or_deductible(
        self,
        coverage_item_id: str,
        coverage_limit: Optional[float] = None,
        deductible: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Modify the coverage limit or deductible for a specific coverage item.
        
        Args:
            coverage_item_id: The ID of the coverage item to update.
            coverage_limit: New coverage limit (optional).
            deductible: New deductible amount (optional).
        
        Returns:
            Dict[str, Any]: Updated coverage item or an error.
        """
        if coverage_limit is None and deductible is None:
            return {"error": "At least one of coverage_limit or deductible must be provided"}
        
        # Find the coverage item
        item = None
        for ci in self.coverage_items:
            if ci["coverage_item_id"] == coverage_item_id:
                item = ci
                break
        
        if item is None:
            return {"error": f"Coverage item with ID '{coverage_item_id}' not found"}
        
        # Check authorization
        auth_check = self.is_authorized_user_for_policy(item["policy_id"])
        if "error" in auth_check:
            return auth_check
        if not auth_check.get("authorized", False):
            return {"error": "User not authorized to modify this policy"}
        
        # Update values
        if coverage_limit is not None:
            if coverage_limit < 0:
                return {"error": "Coverage limit cannot be negative"}
            item["coverage_limit"] = coverage_limit
        
        if deductible is not None:
            if deductible < 0:
                return {"error": "Deductible cannot be negative"}
            item["deductible"] = deductible
        
        return {"success": True, "coverage_item": deepcopy(item), "timestamp": self._timestamp()}
    
    def update_policy_active_dates(
        self,
        policy_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Change the active period of a policy.
        
        Args:
            policy_id: The ID of the policy.
            start_date: New start date in YYYY-MM-DD format (optional).
            end_date: New end date in YYYY-MM-DD format (optional).
        
        Returns:
            Dict[str, Any]: Updated policy dates or an error.
        """
        if start_date is None and end_date is None:
            return {"error": "At least one of start_date or end_date must be provided"}
        
        # Check authorization
        auth_check = self.is_authorized("update_policy", policy_id)
        if not auth_check:
            return {"error": "Unauthorized to update policy dates", "policy_id": policy_id}
        
        policy = self._get_policy(policy_id)
        if policy is None:
            return {"error": "Policy not found", "policy_id": policy_id}
        
        # Validate date formats
        if start_date is not None:
            if not self._validate_date_format(start_date):
                return {"error": "Invalid start_date format. Use YYYY-MM-DD", "policy_id": policy_id}
        
        if end_date is not None:
            if not self._validate_date_format(end_date):
                return {"error": "Invalid end_date format. Use YYYY-MM-DD", "policy_id": policy_id}
        
        # Validate date range
        new_start = start_date if start_date is not None else policy.get("start_date")
        new_end = end_date if end_date is not None else policy.get("end_date")
        
        if new_start and new_end and new_start > new_end:
            return {"error": "start_date cannot be after end_date", "policy_id": policy_id}
        
        # Update the policy
        updates = {}
        if start_date is not None:
            updates["start_date"] = start_date
            policy["start_date"] = start_date
        if end_date is not None:
            updates["end_date"] = end_date
            policy["end_date"] = end_date
        
        policy["updated_at"] = self._timestamp()
        
        return {
            "success": True,
            "policy_id": policy_id,
            "updated_dates": updates,
            "current_dates": {
                "start_date": policy.get("start_date"),
                "end_date": policy.get("end_date")
            },
            "timestamp": self._timestamp()
        }
    
    def _get_policy(self, policy_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a policy by ID from the data store."""
        return self._policies.get(policy_id)
    
    def _validate_date_format(self, date_str: str) -> bool:
        """Validate that a date string is in YYYY-MM-DD format."""
        import re
        pattern = r'^\d{4}-\d{2}-\d{2}$'
        if not re.match(pattern, date_str):
            return False
        try:
            year, month, day = map(int, date_str.split('-'))
            if month < 1 or month > 12:
                return False
            if day < 1 or day > 31:
                return False
            return True
        except ValueError:
            return False
    
    def _timestamp(self) -> str:
        """Generate a current timestamp string."""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"


__TEST_CASES__ = [
    {
        "name": "update_both_dates_success",
        "input": {
            "policy_id": "POL001",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31"
        },
        "expected_keys": ["success", "policy_id", "updated_dates", "current_dates", "timestamp"],
        "expected_values": {"success": True, "policy_id": "POL001"}
    },
    {
        "name": "update_start_date_only",
        "input": {
            "policy_id": "POL001",
            "start_date": "2024-02-15",
            "end_date": None
        },
        "expected_keys": ["success", "policy_id", "updated_dates"],
        "expected_values": {"success": True}
    },
    {
        "name": "update_end_date_only",
        "input": {
            "policy_id": "POL001",
            "start_date": None,
            "end_date": "2025-06-30"
        },
        "expected_keys": ["success", "policy_id", "updated_dates"],
        "expected_values": {"success": True}
    },
    {
        "name": "no_dates_provided_error",
        "input": {
            "policy_id": "POL001",
            "start_date": None,
            "end_date": None
        },
        "expected_keys": ["error"],
        "expected_values": {"error": "At least one of start_date or end_date must be provided"}
    },
    {
        "name": "invalid_start_date_format",
        "input": {
            "policy_id": "POL001",
            "start_date": "01-01-2024",
            "end_date": None
        },
        "expected_keys": ["error", "policy_id"],
        "expected_values": {"error": "Invalid start_date format. Use YYYY-MM-DD"}
    },
    {
        "name": "invalid_end_date_format",
        "input": {
            "policy_id": "POL001",
            "start_date": None,
            "end_date": "2024/12/31"
        },
        "expected_keys": ["error", "policy_id"],
        "expected_values": {"error": "Invalid end_date format. Use YYYY-MM-DD"}
    },
    {
        "name": "start_date_after_end_date_error",
        "input": {
            "policy_id": "POL001",
            "start_date": "2025-01-01",
            "end_date": "2024-12-31"
        },
        "expected_keys": ["error", "policy_id"],
        "expected_values": {"error": "start_date cannot be after end_date"}
    },
    {
        "name": "policy_not_found_error",
        "input": {
            "policy_id": "INVALID_ID",
            "start_date": "2024-01-01",
            "end_date": None
        },
        "expected_keys": ["error", "policy_id"],
        "expected_values": {"error": "Policy not found", "policy_id": "INVALID_ID"}
    },
    {
        "name": "unauthorized_update_error",
        "input": {
            "policy_id": "POL002",
            "start_date": "2024-01-01",
            "end_date": None
        },
        "expected_keys": ["error", "policy_id"],
        "expected_values": {"error": "Unauthorized to update policy dates"}
    }
]