"""
Nutrition Tracking Application User Profile System Environment

A nutrition tracking application user profile system that maintains personalized
account information for each user, including dietary preferences and restrictions.
"""

from copy import deepcopy
from typing import Dict, List, Optional, Any
from datetime import datetime


# 固定的模拟时间戳（保证可复现性）
_FIXED_TIMESTAMP = "2025-03-01T12:00:00"


DEFAULT_STATE: Dict[str, Any] = {
    "users": {
        "admin_001": {
            "_id": "admin_001",
            "name": "System Admin",
            "email": "admin@example.com",
            "dietary_restrictions": [],
            "role": "admin"
        },
        "user_001": {
            "_id": "user_001",
            "name": "Alice Johnson",
            "email": "alice.johnson@example.com",
            "dietary_restrictions": ["vegan", "gluten-free"],
            "role": "user"
        },
        "user_002": {
            "_id": "user_002",
            "name": "Bob Smith",
            "email": "bob.smith@example.com",
            "dietary_restrictions": ["low-sodium"],
            "role": "user"
        },
        "user_003": {
            "_id": "user_003",
            "name": "Carol Davis",
            "email": "carol.davis@example.com",
            "dietary_restrictions": [],
            "role": "user"
        }
    },
    "dietary_restrictions": {
        "vegan": {
            "restriction_name": "vegan",
            "description": "Excludes all animal products including meat, dairy, eggs, and honey.",
            "category": "lifestyle"
        },
        "vegetarian": {
            "restriction_name": "vegetarian",
            "description": "Excludes meat and fish but may include dairy and eggs.",
            "category": "lifestyle"
        },
        "gluten-free": {
            "restriction_name": "gluten-free",
            "description": "Excludes foods containing gluten, a protein found in wheat, barley, and rye.",
            "category": "allergy"
        },
        "dairy-free": {
            "restriction_name": "dairy-free",
            "description": "Excludes all dairy products including milk, cheese, and yogurt.",
            "category": "allergy"
        },
        "low-sodium": {
            "restriction_name": "low-sodium",
            "description": "Limits sodium intake, typically to less than 2300mg per day.",
            "category": "health"
        },
        "low-fat": {
            "restriction_name": "low-fat",
            "description": "Limits fat intake, focusing on lean proteins and reduced oil usage.",
            "category": "health"
        },
        "nut-free": {
            "restriction_name": "nut-free",
            "description": "Excludes all tree nuts and peanuts due to allergy concerns.",
            "category": "allergy"
        },
        "keto": {
            "restriction_name": "keto",
            "description": "High-fat, low-carbohydrate diet that limits carbs to typically under 50g per day.",
            "category": "lifestyle"
        }
    },
    "current_user_id": "admin_001",
    "last_updated": None
}


class NutritionTrackingUserProfileSystem:
    """
    A nutrition tracking application user profile system API.

    This system maintains personalized account information for users including
    dietary preferences and restrictions. It supports operations for adding,
    removing, and viewing dietary requirements to help tailor meal and product
    recommendations based on user constraints.
    """

    def __init__(self) -> None:
        """
        Initialize the NutritionTrackingUserProfileSystem.

        Declares all state attributes with type hints and sets up the API description.

        Args:
            None

        Returns:
            None
        """
        self.users: Dict[str, Dict[str, Any]] = {}
        self.dietary_restrictions: Dict[str, Dict[str, Any]] = {}
        self.current_user_id: Optional[str] = None
        self.last_updated: Optional[str] = None

        self._api_description: str = (
            "A nutrition tracking user profile system that manages dietary "
            "preferences and restrictions for personalized meal recommendations."
        )

    def _timestamp(self) -> str:
        """
        Generate a consistent ISO format timestamp string (fixed for reproducibility).

        Args:
            None

        Returns:
            str: Fixed timestamp in ISO format.
        """
        return _FIXED_TIMESTAMP

    def _load_scenario(self, scenario: dict, long_context: bool = False) -> None:
        """
        Load initial state from a scenario dictionary.

        Args:
            scenario: Dictionary containing initial state data. If keys are missing,
                     defaults from DEFAULT_STATE are used.
            long_context: Flag for long context scenarios (unused in basic implementation).

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
        # 确保当前用户存在，否则置为 None
        if self.current_user_id is not None and self.current_user_id not in self.users:
            self.current_user_id = None

    def get_env_state(self) -> Dict[str, Any]:
        """
        Retrieve the current state of the environment.

        Returns a dictionary containing all internal state variables of the
        nutrition tracking user profile system.

        Args:
            None

        Returns:
            Dict[str, Any]: A dictionary with the following keys:
                - users: Dictionary of all user profiles keyed by user ID
                - dietary_restrictions: Dictionary of all predefined dietary restrictions
                - current_user_id: The currently active user ID or None
                - last_updated: Timestamp of the last state modification or None
        """
        return {
            "users": deepcopy(self.users),
            "dietary_restrictions": deepcopy(self.dietary_restrictions),
            "current_user_id": self.current_user_id,
            "last_updated": self.last_updated
        }

    # ========== Identity & Permission ==========

    def login(self, user_id: str) -> Dict[str, Any]:
        """
        Log in as a user. Sets the current user context.

        Args:
            user_id: The unique identifier of the user to log in as.

        Returns:
            Dict[str, Any]: Success (with current user info) or error.
        """
        if not user_id:
            return {"success": False, "error": "User ID is required."}
        if user_id not in self.users:
            return {"success": False, "error": f"User with ID '{user_id}' not found."}
        self.current_user_id = user_id
        return {
            "success": True,
            "data": {
                "user_id": user_id,
                "role": self.users[user_id].get("role", "user")
            }
        }

    def logout(self) -> Dict[str, Any]:
        """
        Log out the current user. Clears the user context.

        Args:
            None

        Returns:
            Dict[str, Any]: Success confirmation.
        """
        self.current_user_id = None
        return {"success": True, "data": {"message": "Logged out successfully."}}

    def _check_permission(self, target_user_id: str) -> bool:
        """
        Check if the current session has permission to access/modify the target user.

        - No current user → deny
        - Current user is admin → allow any
        - Current user == target user → allow
        - Otherwise → deny

        Args:
            target_user_id: The user ID to check access against.

        Returns:
            bool: True if permitted, False otherwise.
        """
        if self.current_user_id is None:
            return False
        current_user = self.users.get(self.current_user_id)
        if current_user is None:
            return False
        if current_user.get("role") == "admin":
            return True
        return self.current_user_id == target_user_id

    def _check_admin(self) -> bool:
        """
        Check if the current user has admin role.

        Returns:
            bool: True if current user is admin.
        """
        if self.current_user_id is None:
            return False
        current_user = self.users.get(self.current_user_id)
        if current_user is None:
            return False
        return current_user.get("role") == "admin"

    # ========== Query Operations ==========

    def get_user_by_id(self, user_id: str) -> Dict[str, Any]:
        """
        Retrieve user profile information by unique user ID.

        Args:
            user_id: The unique identifier of the user to retrieve.

        Returns:
            Dict[str, Any]: User profile data or error.
        """
        if not user_id:
            return {"success": False, "error": "User ID is required."}
        if not self._check_permission(user_id):
            return {"success": False, "error": "Permission denied: cannot view this user's profile."}
        if user_id not in self.users:
            return {"success": False, "error": f"User with ID '{user_id}' not found."}
        return {
            "success": True,
            "user": deepcopy(self.users[user_id])
        }

    def get_user_dietary_restrictions(self, user_id: str) -> Dict[str, Any]:
        """
        Retrieve the list of dietary restrictions currently set for a user.

        Args:
            user_id: The unique identifier of the user.

        Returns:
            Dict[str, Any]: Dictionary containing the list of dietary restrictions
                           for the user, or an error.
        """
        if not user_id:
            return {"success": False, "error": "User ID is required."}
        if not self._check_permission(user_id):
            return {"success": False, "error": "Permission denied: cannot view this user's restrictions."}
        if user_id not in self.users:
            return {"success": False, "error": f"User with ID '{user_id}' not found."}
        restrictions = self.users[user_id].get("dietary_restrictions", [])
        return {
            "success": True,
            "user_id": user_id,
            "dietary_restrictions": deepcopy(restrictions)
        }

    def list_all_dietary_restrictions(self) -> Dict[str, Any]:
        """
        Retrieve all predefined dietary restrictions available in the system.

        Args:
            None

        Returns:
            Dict[str, Any]: Dictionary containing a list of all available
                           dietary restriction objects.
        """
        restrictions_list = list(deepcopy(self.dietary_restrictions).values())
        return {
            "success": True,
            "dietary_restrictions": restrictions_list,
            "count": len(restrictions_list)
        }

    def get_dietary_restriction_info(self, restriction_name: str) -> Dict[str, Any]:
        """
        Retrieve detailed information for a specific restriction by name.

        Args:
            restriction_name: The name of the dietary restriction to look up.

        Returns:
            Dict[str, Any]: Dictionary containing restriction details, or error.
        """
        if not restriction_name:
            return {"success": False, "error": "Restriction name is required."}
        restriction_key = restriction_name.lower()
        if restriction_key not in self.dietary_restrictions:
            return {"success": False, "error": f"Dietary restriction '{restriction_name}' not found."}
        return {
            "success": True,
            "restriction": deepcopy(self.dietary_restrictions[restriction_key])
        }

    def check_restriction_exists(self, restriction_name: str) -> Dict[str, Any]:
        """
        Check whether a given restriction name is a valid predefined restriction.

        Args:
            restriction_name: The name of the dietary restriction to check.

        Returns:
            Dict[str, Any]: Dictionary with 'exists' boolean indicating whether
                           the restriction is valid.
        """
        if not restriction_name:
            return {"success": False, "error": "Restriction name is required."}
        restriction_key = restriction_name.lower()
        exists = restriction_key in self.dietary_restrictions
        return {
            "success": True,
            "restriction_name": restriction_name,
            "exists": exists
        }

    def check_user_has_restriction(self, user_id: str, restriction_name: str) -> Dict[str, Any]:
        """
        Determine if a user already has a specific dietary restriction in their profile.

        Args:
            user_id: The unique identifier of the user.
            restriction_name: The name of the dietary restriction to check.

        Returns:
            Dict[str, Any]: Dictionary with 'has_restriction' boolean, or error.
        """
        if not user_id:
            return {"success": False, "error": "User ID is required."}
        if not restriction_name:
            return {"success": False, "error": "Restriction name is required."}
        if not self._check_permission(user_id):
            return {"success": False, "error": "Permission denied: cannot view this user's restrictions."}
        if user_id not in self.users:
            return {"success": False, "error": f"User with ID '{user_id}' not found."}
        restriction_key = restriction_name.lower()
        user_restrictions = self.users[user_id].get("dietary_restrictions", [])
        has_restriction = restriction_key in [r.lower() for r in user_restrictions]
        return {
            "success": True,
            "user_id": user_id,
            "restriction_name": restriction_name,
            "has_restriction": has_restriction
        }

    # ========== State Change Operations ==========

    def add_dietary_restriction_to_user(self, user_id: str, restriction_name: str) -> Dict[str, Any]:
        """
        Add a valid dietary restriction to a user's profile if not already present.

        Args:
            user_id: The unique identifier of the user.
            restriction_name: The name of the dietary restriction to add.

        Returns:
            Dict[str, Any]: Success status with updated restrictions list, or error.
        """
        if not user_id:
            return {"success": False, "error": "User ID is required."}
        if not restriction_name:
            return {"success": False, "error": "Restriction name is required."}
        if not self._check_permission(user_id):
            return {"success": False, "error": "Permission denied: cannot modify this user's restrictions."}
        if user_id not in self.users:
            return {"success": False, "error": f"User with ID '{user_id}' not found."}
        restriction_key = restriction_name.lower()
        if restriction_key not in self.dietary_restrictions:
            return {"success": False, "error": f"Dietary restriction '{restriction_name}' is not a valid predefined restriction."}
        user_restrictions = self.users[user_id].get("dietary_restrictions", [])
        existing_lower = [r.lower() for r in user_restrictions]
        if restriction_key in existing_lower:
            return {"success": False, "error": f"User already has the dietary restriction '{restriction_name}'."}
        self.users[user_id]["dietary_restrictions"].append(restriction_key)
        self.last_updated = self._timestamp()
        return {
            "success": True,
            "message": f"Added '{restriction_key}' to user '{user_id}'.",
            "dietary_restrictions": deepcopy(self.users[user_id]["dietary_restrictions"])
        }

    def remove_dietary_restriction_from_user(self, user_id: str, restriction_name: str) -> Dict[str, Any]:
        """
        Remove a dietary restriction from a user's profile if it exists.

        Args:
            user_id: The unique identifier of the user.
            restriction_name: The name of the dietary restriction to remove.

        Returns:
            Dict[str, Any]: Success status with updated restrictions list, or error.
        """
        if not user_id:
            return {"success": False, "error": "User ID is required."}
        if not restriction_name:
            return {"success": False, "error": "Restriction name is required."}
        if not self._check_permission(user_id):
            return {"success": False, "error": "Permission denied: cannot modify this user's restrictions."}
        if user_id not in self.users:
            return {"success": False, "error": f"User with ID '{user_id}' not found."}
        restriction_key = restriction_name.lower()
        user_restrictions = self.users[user_id].get("dietary_restrictions", [])
        existing_lower = [r.lower() for r in user_restrictions]
        if restriction_key not in existing_lower:
            return {"success": False, "error": f"User does not have the dietary restriction '{restriction_name}'."}
        self.users[user_id]["dietary_restrictions"] = [
            r for r in user_restrictions if r.lower() != restriction_key
        ]
        self.last_updated = self._timestamp()
        return {
            "success": True,
            "message": f"Removed '{restriction_name}' from user '{user_id}'.",
            "dietary_restrictions": deepcopy(self.users[user_id]["dietary_restrictions"])
        }

    def update_user_dietary_restrictions(self, user_id: str, restrictions: List[str]) -> Dict[str, Any]:
        """
        Replace the entire list of dietary restrictions for a user in a single operation.

        Args:
            user_id: The unique identifier of the user.
            restrictions: The new list of dietary restrictions to set.

        Returns:
            Dict[str, Any]: Success status with the new restrictions list, or error.
        """
        if not user_id:
            return {"success": False, "error": "User ID is required."}
        if restrictions is None:
            return {"success": False, "error": "Restrictions list is required."}
        if not self._check_permission(user_id):
            return {"success": False, "error": "Permission denied: cannot modify this user's restrictions."}
        if user_id not in self.users:
            return {"success": False, "error": f"User with ID '{user_id}' not found."}
        normalized_restrictions = []
        seen = set()
        for restriction in restrictions:
            restriction_key = restriction.lower()
            if restriction_key not in self.dietary_restrictions:
                return {"success": False, "error": f"Dietary restriction '{restriction}' is not a valid predefined restriction."}
            if restriction_key in seen:
                return {"success": False, "error": f"Duplicate restriction '{restriction}' found in the list."}
            seen.add(restriction_key)
            normalized_restrictions.append(restriction_key)
        self.users[user_id]["dietary_restrictions"] = normalized_restrictions
        self.last_updated = self._timestamp()
        return {
            "success": True,
            "message": f"Updated dietary restrictions for user '{user_id}'.",
            "dietary_restrictions": deepcopy(self.users[user_id]["dietary_restrictions"])
        }

    def clear_all_dietary_restrictions(self, user_id: str) -> Dict[str, Any]:
        """
        Remove all dietary restrictions from a user's profile.

        Args:
            user_id: The unique identifier of the user.

        Returns:
            Dict[str, Any]: Success status confirming all restrictions were cleared, or error.
        """
        if not user_id:
            return {"success": False, "error": "User ID is required."}
        if not self._check_permission(user_id):
            return {"success": False, "error": "Permission denied: cannot modify this user's restrictions."}
        if user_id not in self.users:
            return {"success": False, "error": f"User with ID '{user_id}' not found."}
        previous_count = len(self.users[user_id].get("dietary_restrictions", []))
        self.users[user_id]["dietary_restrictions"] = []
        self.last_updated = self._timestamp()
        return {
            "success": True,
            "message": f"Cleared all dietary restrictions for user '{user_id}'.",
            "restrictions_removed": previous_count,
            "dietary_restrictions": []
        }

    def add_new_dietary_restriction_type(
        self,
        restriction_name: str,
        description: str,
        category: str
    ) -> Dict[str, Any]:
        """
        Register a new dietary restriction type in the system.

        This is an admin-level operation to expand available restriction options.

        Args:
            restriction_name: The unique name for the new restriction.
            description: A detailed description of the dietary restriction.
            category: The category of the restriction (e.g., 'lifestyle', 'allergy', 'health').

        Returns:
            Dict[str, Any]: Success status with the new restriction details, or error.
        """
        if not restriction_name:
            return {"success": False, "error": "Restriction name is required."}
        if not description:
            return {"success": False, "error": "Description is required."}
        if not category:
            return {"success": False, "error": "Category is required."}
        if not self._check_admin():
            return {"success": False, "error": "Permission denied: only admin can add new restriction types."}
        restriction_key = restriction_name.lower()
        if restriction_key in self.dietary_restrictions:
            return {"success": False, "error": f"Dietary restriction '{restriction_name}' already exists."}
        valid_categories = ["lifestyle", "allergy", "health", "religious", "medical"]
        if category.lower() not in valid_categories:
            return {
                "success": False,
                "error": f"Invalid category '{category}'. Must be one of: {', '.join(valid_categories)}."
            }
        new_restriction = {
            "restriction_name": restriction_key,
            "description": description,
            "category": category.lower()
        }
        self.dietary_restrictions[restriction_key] = new_restriction
        self.last_updated = self._timestamp()
        return {
            "success": True,
            "message": f"Added new dietary restriction '{restriction_key}'.",
            "restriction": deepcopy(new_restriction)
        }


__TEST_CASES__: List[Dict[str, Any]] = [
    {
        "name": "Add and verify dietary restriction for existing user",
        "steps": [
            {"tool_call": "get_user_by_id(user_id='user_003')", "expect_success": True},
            {"tool_call": "check_restriction_exists(restriction_name='low-fat')", "expect_success": True},
            {"tool_call": "add_dietary_restriction_to_user(user_id='user_003', restriction_name='low-fat')", "expect_success": True},
            {"tool_call": "get_user_dietary_restrictions(user_id='user_003')", "expect_success": True},
            {"tool_call": "check_user_has_restriction(user_id='user_003', restriction_name='low-fat')", "expect_success": True}
        ]
    },
    {
        "name": "Attempt to add duplicate dietary restriction",
        "steps": [
            {"tool_call": "get_user_dietary_restrictions(user_id='user_001')", "expect_success": True},
            {"tool_call": "add_dietary_restriction_to_user(user_id='user_001', restriction_name='vegan')", "expect_success": False},
        ]
    },
    {
        "name": "Remove dietary restriction and clear all",
        "steps": [
            {"tool_call": "get_user_dietary_restrictions(user_id='user_001')", "expect_success": True},
            {"tool_call": "remove_dietary_restriction_from_user(user_id='user_001', restriction_name='gluten-free')", "expect_success": True},
            {"tool_call": "get_user_dietary_restrictions(user_id='user_001')", "expect_success": True},
            {"tool_call": "clear_all_dietary_restrictions(user_id='user_001')", "expect_success": True},
            {"tool_call": "get_user_dietary_restrictions(user_id='user_001')", "expect_success": True}
        ]
    },
    {
        "name": "Add invalid restriction and non-existent user operations",
        "steps": [
            {"tool_call": "add_dietary_restriction_to_user(user_id='user_001', restriction_name='invalid-restriction')", "expect_success": False},
            {"tool_call": "get_user_by_id(user_id='nonexistent_user')", "expect_success": False},
            {"tool_call": "add_dietary_restriction_to_user(user_id='nonexistent_user', restriction_name='vegan')", "expect_success": False}
        ]
    },
    {
        "name": "Admin adds new dietary restriction type and user adopts it",
        "steps": [
            {"tool_call": "list_all_dietary_restrictions()", "expect_success": True},
            {"tool_call": "add_new_dietary_restriction_type(restriction_name='halal', description='Food prepared according to Islamic dietary laws.', category='religious')", "expect_success": True},
            {"tool_call": "check_restriction_exists(restriction_name='halal')", "expect_success": True},
            {"tool_call": "get_dietary_restriction_info(restriction_name='halal')", "expect_success": True},
            {"tool_call": "add_dietary_restriction_to_user(user_id='user_002', restriction_name='halal')", "expect_success": True}
        ]
    }
]