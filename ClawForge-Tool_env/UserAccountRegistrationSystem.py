"""
User Account Registration System Environment API

A user account registration system manages the creation and authentication of user identities
within a digital platform. It maintains a persistent state of registered usernames, passwords,
and associated user data, and supports operations such as username availability checks,
account creation, and login validation.
"""

from copy import deepcopy
from typing import Dict, List, Any
from datetime import datetime
import hashlib
import re


# Default initial state with sample data
DEFAULT_STATE: Dict[str, Any] = {
    "users": {
        "john_doe": {
            "name": "john_doe",
            "password_hash": "5e884898da28047d9169e1c3b5cd1c4a0c1fbd2edfb6ce07c8f7b12345678901",
            "registration_date": "2024-01-15T10:30:00",
            "email": "john.doe@example.com",
            "is_verified": True
        },
        "jane_smith": {
            "name": "jane_smith",
            "password_hash": "8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92",
            "registration_date": "2024-02-20T14:45:00",
            "email": "jane.smith@example.com",
            "is_verified": True
        },
        "bob_wilson": {
            "name": "bob_wilson",
            "password_hash": "ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f",
            "registration_date": "2024-03-10T09:15:00",
            "email": "bob.wilson@example.com",
            "is_verified": False
        }
    },
    "registered_emails": [
        "john.doe@example.com",
        "jane.smith@example.com",
        "bob.wilson@example.com"
    ]
}


class UserAccountRegistrationSystem:
    """
    A user account registration system that manages user identities within a digital platform.
    
    This system maintains a persistent state of registered usernames, passwords, and associated
    user data. It supports operations such as username availability checks, account creation,
    email verification, and account management while enforcing uniqueness constraints and
    registration policies.
    """
    
    def __init__(self) -> None:
        """
        Initialize the User Account Registration System.
        
        Declares all state attributes with type hints and sets up the API description.
        
        Args:
            None
            
        Returns:
            None
        """
        self.users: Dict[str, Dict[str, Any]] = {}
        self.registered_emails: List[str] = []
        
        self._api_description: str = (
            "A user account registration system that manages user creation, authentication, "
            "and account operations within a digital platform."
        )
    
    def _timestamp(self) -> str:
        """
        Generate a unified timestamp string.
        
        Args:
            None
        
        Returns:
            str: ISO format timestamp string.
        """
        return datetime.now().isoformat(timespec='seconds')
    
    def _hash_password(self, password: str) -> str:
        """
        Hash a password using SHA-256.
        
        Args:
            password: The plain text password to hash.
            
        Returns:
            str: The hashed password as a hexadecimal string.
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _is_valid_email(self, email: str) -> bool:
        """
        Validate email format using a simple regex pattern.
        
        Args:
            email: The email address to validate.
            
        Returns:
            bool: True if the email format is valid, False otherwise.
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def _load_scenario(self, scenario: dict, long_context: bool = False) -> None:
        """
        Load initial state from a scenario dictionary.
        
        If a key is not present in the scenario, falls back to DEFAULT_STATE values.
        
        Args:
            scenario: A dictionary containing the initial state configuration.
            long_context: Flag for extended context loading (reserved for future use).
            
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
        Retrieve the current environment state.
        
        Returns a dictionary containing all internal state variables of the system,
        including the users registry and registered emails list.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - users: Dict of all registered user accounts with their details
                - registered_emails: List of all registered email addresses
        """
        return {
            "users": deepcopy(self.users),
            "registered_emails": deepcopy(self.registered_emails)
        }
    
    # ==================== Query Operations ====================
    
    def is_username_available(self, username: str) -> Dict[str, Any]:
        """
        Check whether a given username is not already taken.
        
        Verifies if the username does not exist in the system, making it available
        for registration.
        
        Args:
            username: The username to check for availability.
            
        Returns:
            Dict[str, Any]: A dictionary containing:
                - available: Boolean indicating if the username is available
                - username: The username that was checked
                Or an error dictionary if validation fails.
        """
        if not username or not isinstance(username, str):
            return {"error": "Invalid username provided. Username must be a non-empty string."}
        
        is_available = username not in self.users
        return {
            "available": is_available,
            "username": username
        }
    
    def is_email_available(self, email: str) -> Dict[str, Any]:
        """
        Verify that a given email address is not associated with any existing account.
        
        Checks if the email is not already registered in the system.
        
        Args:
            email: The email address to check for availability.
            
        Returns:
            Dict[str, Any]: A dictionary containing:
                - available: Boolean indicating if the email is available
                - email: The email that was checked
                Or an error dictionary if validation fails.
        """
        if not email or not isinstance(email, str):
            return {"error": "Invalid email provided. Email must be a non-empty string."}
        
        if not self._is_valid_email(email):
            return {"error": "Invalid email format provided."}
        
        is_available = email.lower() not in [e.lower() for e in self.registered_emails]
        return {
            "available": is_available,
            "email": email
        }
    
    def get_user_info(self, username: str) -> Dict[str, Any]:
        """
        Retrieve full user information by username, excluding sensitive data.
        
        Returns user details such as name, registration date, email, and verification
        status. Password hash is excluded for security purposes.
        
        Args:
            username: The username of the account to retrieve information for.
            
        Returns:
            Dict[str, Any]: A dictionary containing user information (excluding password_hash)
                or an error dictionary if the user is not found.
        """
        if not username or not isinstance(username, str):
            return {"error": "Invalid username provided. Username must be a non-empty string."}
        
        if username not in self.users:
            return {"error": f"User '{username}' not found in the system."}
        
        user = self.users[username]
        return {
            "name": user["name"],
            "registration_date": user["registration_date"],
            "email": user["email"],
            "is_verified": user["is_verified"]
        }
    
    def check_account_verification_status(self, username: str) -> Dict[str, Any]:
        """
        Return whether a user's email has been verified.
        
        Args:
            username: The username of the account to check verification status for.
            
        Returns:
            Dict[str, Any]: A dictionary containing:
                - username: The username checked
                - is_verified: Boolean indicating verification status
                Or an error dictionary if the user is not found.
        """
        if not username or not isinstance(username, str):
            return {"error": "Invalid username provided. Username must be a non-empty string."}
        
        if username not in self.users:
            return {"error": f"User '{username}' not found in the system."}
        
        return {
            "username": username,
            "is_verified": self.users[username]["is_verified"]
        }
    
    def list_all_usernames(self) -> Dict[str, Any]:
        """
        Retrieve the list of all registered usernames in the system.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - usernames: List of all registered usernames
                - count: Total number of registered users
        """
        return {
            "usernames": list(self.users.keys()),
            "count": len(self.users)
        }
    
    # ==================== State Change Operations ====================
    
    def register_user(self, username: str, password: str, email: str) -> Dict[str, Any]:
        """
        Create a new user account with username, hashed password, and email.
        
        The account is created with is_verified set to False. Enforces username
        uniqueness, email uniqueness, and valid email format constraints.
        
        Args:
            username: The desired username for the new account.
            password: The plain text password (will be hashed before storage).
            email: The email address for the account.
            
        Returns:
            Dict[str, Any]: A dictionary containing success status and user details,
                or an error dictionary if constraints are violated.
        """
        # Validate username
        if not username or not isinstance(username, str):
            return {"error": "Invalid username provided. Username must be a non-empty string."}
        
        if len(username) < 3:
            return {"error": "Username must be at least 3 characters long."}
        
        if username in self.users:
            return {"error": f"Username '{username}' is already taken. Please choose a different username."}
        
        # Validate password
        if not password or not isinstance(password, str):
            return {"error": "Invalid password provided. Password must be a non-empty string."}
        
        if len(password) < 6:
            return {"error": "Password must be at least 6 characters long."}
        
        # Validate email
        if not email or not isinstance(email, str):
            return {"error": "Invalid email provided. Email must be a non-empty string."}
        
        if not self._is_valid_email(email):
            return {"error": "Invalid email format provided."}
        
        if email.lower() in [e.lower() for e in self.registered_emails]:
            return {"error": f"Email '{email}' is already associated with an existing account."}
        
        # Create user account
        password_hash = self._hash_password(password)
        registration_date = self._timestamp()
        
        self.users[username] = {
            "name": username,
            "password_hash": password_hash,
            "registration_date": registration_date,
            "email": email,
            "is_verified": False
        }
        self.registered_emails.append(email)
        
        return {
            "success": True,
            "message": f"User '{username}' registered successfully.",
            "user": {
                "name": username,
                "email": email,
                "registration_date": registration_date,
                "is_verified": False
            }
        }
    
    def verify_email(self, username: str) -> Dict[str, Any]:
        """
        Update the is_verified flag to True for a user after email confirmation.
        
        Args:
            username: The username of the account to verify.
            
        Returns:
            Dict[str, Any]: A dictionary containing success status,
                or an error dictionary if the user is not found or already verified.
        """
        if not username or not isinstance(username, str):
            return {"error": "Invalid username provided. Username must be a non-empty string."}
        
        if username not in self.users:
            return {"error": f"User '{username}' not found in the system."}
        
        if self.users[username]["is_verified"]:
            return {"error": f"User '{username}' is already verified."}
        
        self.users[username]["is_verified"] = True
        
        return {
            "success": True,
            "message": f"Email verified successfully for user '{username}'.",
            "username": username,
            "is_verified": True
        }
    
    def update_password(self, username: str, new_password: str) -> Dict[str, Any]:
        """
        Change a user's password by securely hashing and updating the password_hash field.
        
        Args:
            username: The username of the account to update.
            new_password: The new plain text password (will be hashed before storage).
            
        Returns:
            Dict[str, Any]: A dictionary containing success status,
                or an error dictionary if the user is not found or password is invalid.
        """
        if not username or not isinstance(username, str):
            return {"error": "Invalid username provided. Username must be a non-empty string."}
        
        if username not in self.users:
            return {"error": f"User '{username}' not found in the system."}
        
        if not new_password or not isinstance(new_password, str):
            return {"error": "Invalid password provided. Password must be a non-empty string."}
        
        if len(new_password) < 6:
            return {"error": "Password must be at least 6 characters long."}
        
        new_password_hash = self._hash_password(new_password)
        self.users[username]["password_hash"] = new_password_hash
        
        return {
            "success": True,
            "message": f"Password updated successfully for user '{username}'.",
            "username": username
        }
    
    def delete_account(self, username: str) -> Dict[str, Any]:
        """
        Remove a user account from the system given the username.
        
        Args:
            username: The username of the account to delete.
            
        Returns:
            Dict[str, Any]: A dictionary containing success status,
                or an error dictionary if the user is not found.
        """
        if not username or not isinstance(username, str):
            return {"error": "Invalid username provided. Username must be a non-empty string."}
        
        if username not in self.users:
            return {"error": f"User '{username}' not found in the system."}
        
        # Remove email from registered emails list
        user_email = self.users[username]["email"]
        if user_email in self.registered_emails:
            self.registered_emails.remove(user_email)
        
        # Remove user
        del self.users[username]
        
        return {
            "success": True,
            "message": f"User account '{username}' has been deleted successfully.",
            "deleted_username": username
        }
    
    def change_username(self, current_username: str, new_username: str) -> Dict[str, Any]:
        """
        Allow a user to change their username if the new one is available.
        
        Args:
            current_username: The current username of the account.
            new_username: The desired new username.
            
        Returns:
            Dict[str, Any]: A dictionary containing success status and updated info,
                or an error dictionary if constraints are violated.
        """
        if not current_username or not isinstance(current_username, str):
            return {"error": "Invalid current username provided. Username must be a non-empty string."}
        
        if not new_username or not isinstance(new_username, str):
            return {"error": "Invalid new username provided. Username must be a non-empty string."}
        
        if current_username not in self.users:
            return {"error": f"User '{current_username}' not found in the system."}
        
        if len(new_username) < 3:
            return {"error": "New username must be at least 3 characters long."}
        
        if new_username in self.users:
            return {"error": f"Username '{new_username}' is already taken. Please choose a different username."}
        
        # Transfer user data to new username
        user_data = self.users[current_username]
        user_data["name"] = new_username
        self.users[new_username] = user_data
        del self.users[current_username]
        
        return {
            "success": True,
            "message": f"Username changed from '{current_username}' to '{new_username}' successfully.",
            "old_username": current_username,
            "new_username": new_username
        }


# Test cases for the User Account Registration System
__TEST_CASES__ = [
    {
        "name": "Complete user registration and verification flow",
        "steps": [
            {"tool_call": "is_username_available(username='new_user')", "expect_success": True},
            {"tool_call": "is_email_available(email='new_user@example.com')", "expect_success": True},
            {"tool_call": "register_user(username='new_user', password='securepass123', email='new_user@example.com')", "expect_success": True},
            {"tool_call": "check_account_verification_status(username='new_user')", "expect_success": True},
            {"tool_call": "verify_email(username='new_user')", "expect_success": True},
            {"tool_call": "check_account_verification_status(username='new_user')", "expect_success": True}
        ]
    },
    {
        "name": "Query existing user information",
        "steps": [
            {"tool_call": "list_all_usernames()", "expect_success": True},
            {"tool_call": "get_user_info(username='john_doe')", "expect_success": True},
            {"tool_call": "check_account_verification_status(username='jane_smith')", "expect_success": True},
            {"tool_call": "is_username_available(username='john_doe')", "expect_success": True}
        ]
    },
    {
        "name": "Update password and change username",
        "steps": [
            {"tool_call": "update_password(username='bob_wilson', new_password='newpassword123')", "expect_success": True},
            {"tool_call": "change_username(current_username='bob_wilson', new_username='robert_wilson')", "expect_success": True},
            {"tool_call": "get_user_info(username='robert_wilson')", "expect_success": True}
        ]
    },
    {
        "name": "Error handling - duplicate username and email registration",
        "steps": [
            {"tool_call": "is_username_available(username='john_doe')", "expect_success": True},
            {"tool_call": "register_user(username='john_doe', password='password123', email='another@example.com')", "expect_success": False},
            {"tool_call": "register_user(username='unique_user', password='password123', email='john.doe@example.com')", "expect_success": False}
        ]
    },
    {
        "name": "Error handling - invalid operations and inputs",
        "steps": [
            {"tool_call": "get_user_info(username='nonexistent_user')", "expect_success": False},
            {"tool_call": "verify_email(username='john_doe')", "expect_success": False},
            {"tool_call": "register_user(username='ab', password='validpass123', email='valid@example.com')", "expect_success": False},
            {"tool_call": "register_user(username='validuser', password='short', email='valid@example.com')", "expect_success": False},
            {"tool_call": "is_email_available(email='invalid-email')", "expect_success": False},
            {"tool_call": "delete_account(username='unknown_user')", "expect_success": False},
            {"tool_call": "change_username(current_username='john_doe', new_username='jane_smith')", "expect_success": False}
        ]
    }
]