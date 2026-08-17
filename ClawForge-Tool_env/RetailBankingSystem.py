"""
Retail Banking System Environment API

A retail banking system that manages customer financial accounts, including checking
and savings accounts, loans, and transactions. It maintains persistent data such as
account numbers, balances, and customer identities.
"""

from copy import deepcopy
from typing import Dict, List, Optional, Any
from datetime import datetime


DEFAULT_STATE: Dict[str, Any] = {
    "customers": {
        "CUST001": {
            "customer_id": "CUST001",
            "name": "John Smith",
            "contact_info": {
                "email": "john.smith@email.com",
                "phone": "+1-555-0101",
                "address": "123 Main St, New York, NY 10001"
            },
            "identification_detail": {
                "type": "SSN",
                "number": "***-**-1234",
                "verified": True
            }
        },
        "CUST002": {
            "customer_id": "CUST002",
            "name": "Jane Doe",
            "contact_info": {
                "email": "jane.doe@email.com",
                "phone": "+1-555-0102",
                "address": "456 Oak Ave, Los Angeles, CA 90001"
            },
            "identification_detail": {
                "type": "SSN",
                "number": "***-**-5678",
                "verified": True
            }
        },
        "CUST003": {
            "customer_id": "CUST003",
            "name": "Bob Johnson",
            "contact_info": {
                "email": "bob.johnson@email.com",
                "phone": "+1-555-0103",
                "address": "789 Pine Rd, Chicago, IL 60601"
            },
            "identification_detail": {
                "type": "Passport",
                "number": "P12345678",
                "verified": True
            }
        }
    },
    "accounts": {
        "ACC001": {
            "account_id": "ACC001",
            "customer_id": "CUST001",
            "account_type": "checking",
            "balance": 5000.00,
            "currency": "USD",
            "status": "active",
            "opening_date": "2023-01-15T10:30:00",
            "overdraft_allowed": True,
            "overdraft_limit": 500.00
        },
        "ACC002": {
            "account_id": "ACC002",
            "customer_id": "CUST001",
            "account_type": "savings",
            "balance": 15000.00,
            "currency": "USD",
            "status": "active",
            "opening_date": "2023-01-15T10:35:00",
            "overdraft_allowed": False,
            "overdraft_limit": 0.00
        },
        "ACC003": {
            "account_id": "ACC003",
            "customer_id": "CUST002",
            "account_type": "checking",
            "balance": 2500.00,
            "currency": "USD",
            "status": "active",
            "opening_date": "2023-02-20T14:00:00",
            "overdraft_allowed": False,
            "overdraft_limit": 0.00
        },
        "ACC004": {
            "account_id": "ACC004",
            "customer_id": "CUST002",
            "account_type": "loan",
            "balance": -10000.00,
            "currency": "USD",
            "status": "active",
            "opening_date": "2023-03-01T09:00:00",
            "overdraft_allowed": False,
            "overdraft_limit": 0.00
        },
        "ACC005": {
            "account_id": "ACC005",
            "customer_id": "CUST003",
            "account_type": "savings",
            "balance": 0.00,
            "currency": "USD",
            "status": "frozen",
            "opening_date": "2022-06-10T11:00:00",
            "overdraft_allowed": False,
            "overdraft_limit": 0.00
        }
    },
    "current_user": {
        "user_id": "CUST001",
        "authenticated": True,
        "role": "customer",
        "authorized_accounts": ["ACC001", "ACC002"]
    },
    "session": {
        "session_id": "SESSION001",
        "created_at": "2024-01-15T08:00:00",
        "expires_at": "2024-01-15T20:00:00"
    }
}


class RetailBankingSystem:
    """
    A retail banking system environment that manages customer financial accounts.
    
    This environment provides secure, stateful management of customer accounts
    including checking, savings, and loan accounts. It supports operations like
    balance inquiries, fund transfers, account management, and statement generation.
    """

    def __init__(self) -> None:
        """
        Initialize the RetailBankingSystem environment.
        
        Declares all state attributes with type hints and sets the API description.
        
        Args:
            None
        
        Returns:
            None
        """
        self.customers: Dict[str, Dict[str, Any]] = {}
        self.accounts: Dict[str, Dict[str, Any]] = {}
        self.current_user: Dict[str, Any] = {}
        self.session: Dict[str, Any] = {}
        
        self._api_description: str = (
            "A retail banking system API for managing customer accounts, "
            "balances, and banking operations with secure authentication."
        )

    def _timestamp(self) -> str:
        """
        Generate a standardized ISO format timestamp.
        
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
            scenario: Dictionary containing initial state values for the environment.
            long_context: Flag for long context scenarios (reserved for future use).
        
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
        Return the current state of the banking environment.
        
        Provides a complete snapshot of all internal state variables including
        customers, accounts, current user session, and authentication state.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - customers: All customer records indexed by customer_id
                - accounts: All account records indexed by account_id
                - current_user: Current authenticated user information
                - session: Current session details
        """
        return {
            "customers": deepcopy(self.customers),
            "accounts": deepcopy(self.accounts),
            "current_user": deepcopy(self.current_user),
            "session": deepcopy(self.session)
        }

    def _is_authorized_for_account(self, account_id: str) -> bool:
        """
        Check if the current user is authorized to access a specific account.
        
        Args:
            account_id: The account ID to check authorization for.
        
        Returns:
            bool: True if authorized, False otherwise.
        """
        if not self.current_user.get("authenticated", False):
            return False
        
        if self.current_user.get("role") == "admin":
            return True
        
        return account_id in self.current_user.get("authorized_accounts", [])

    def _is_authorized_for_customer(self, customer_id: str) -> bool:
        """
        Check if the current user is authorized to access a specific customer's data.
        
        Args:
            customer_id: The customer ID to check authorization for.
        
        Returns:
            bool: True if authorized, False otherwise.
        """
        if not self.current_user.get("authenticated", False):
            return False
        
        if self.current_user.get("role") == "admin":
            return True
        
        return self.current_user.get("user_id") == customer_id

    # ==================== QUERY OPERATIONS ====================

    def get_customer_by_id(self, customer_id: str) -> Dict[str, Any]:
        """
        Retrieve customer information using customer_id.
        
        Args:
            customer_id: The unique identifier of the customer to retrieve.
        
        Returns:
            Dict[str, Any]: Customer information including name, contact info,
                and identification details, or an error dictionary if not found
                or unauthorized.
        """
        if not self._is_authorized_for_customer(customer_id):
            return {"error": "Unauthorized access to customer data"}
        
        if customer_id not in self.customers:
            return {"error": f"Customer with ID '{customer_id}' not found"}
        
        customer = deepcopy(self.customers[customer_id])
        return {"success": True, "customer": customer}

    def get_customer_by_name(self, name: str) -> Dict[str, Any]:
        """
        Search for customers by name.
        
        Args:
            name: The name to search for (case-insensitive partial match).
        
        Returns:
            Dict[str, Any]: List of matching customers or error if unauthorized.
        """
        if not self.current_user.get("authenticated", False):
            return {"error": "Authentication required to search customers"}
        
        matching_customers = []
        search_name = name.lower()
        
        for customer_id, customer in self.customers.items():
            if search_name in customer["name"].lower():
                if self._is_authorized_for_customer(customer_id):
                    matching_customers.append(deepcopy(customer))
        
        return {"success": True, "customers": matching_customers, "count": len(matching_customers)}

    def list_customer_accounts(self, customer_id: str) -> Dict[str, Any]:
        """
        List all accounts associated with a given customer_id.
        
        Args:
            customer_id: The customer ID whose accounts to list.
        
        Returns:
            Dict[str, Any]: List of accounts belonging to the customer,
                or error if unauthorized or customer not found.
        """
        if not self._is_authorized_for_customer(customer_id):
            return {"error": "Unauthorized access to customer accounts"}
        
        if customer_id not in self.customers:
            return {"error": f"Customer with ID '{customer_id}' not found"}
        
        customer_accounts = []
        for account in self.accounts.values():
            if account["customer_id"] == customer_id:
                customer_accounts.append(deepcopy(account))
        
        return {"success": True, "accounts": customer_accounts, "count": len(customer_accounts)}

    def get_account_by_id(self, account_id: str) -> Dict[str, Any]:
        """
        Retrieve full details of an account by account_id.
        
        Only active accounts can be queried for full details.
        
        Args:
            account_id: The unique identifier of the account.
        
        Returns:
            Dict[str, Any]: Account details or error if not found,
                inactive, or unauthorized.
        """
        if not self._is_authorized_for_account(account_id):
            return {"error": "Unauthorized access to account data"}
        
        if account_id not in self.accounts:
            return {"error": f"Account with ID '{account_id}' not found"}
        
        account = self.accounts[account_id]
        
        if account["status"] != "active":
            return {"error": f"Account '{account_id}' is not active (status: {account['status']})"}
        
        return {"success": True, "account": deepcopy(account)}

    def get_account_balance(self, account_id: str) -> Dict[str, Any]:
        """
        Return the current balance of an active account.
        
        Only accessible to authorized users for active accounts.
        
        Args:
            account_id: The account ID to query balance for.
        
        Returns:
            Dict[str, Any]: Current balance and currency, or error if
                unauthorized, not found, or inactive.
        """
        if not self._is_authorized_for_account(account_id):
            return {"error": "Unauthorized access to account balance"}
        
        if account_id not in self.accounts:
            return {"error": f"Account with ID '{account_id}' not found"}
        
        account = self.accounts[account_id]
        
        if account["status"] != "active":
            return {"error": f"Cannot query balance for inactive account (status: {account['status']})"}
        
        return {
            "success": True,
            "account_id": account_id,
            "balance": account["balance"],
            "currency": account["currency"]
        }

    def list_accounts_by_type(self, customer_id: str, account_type: str) -> Dict[str, Any]:
        """
        Retrieve all accounts of a specific type for a customer.
        
        Args:
            customer_id: The customer whose accounts to filter.
            account_type: The type of accounts to retrieve (checking, savings, loan).
        
        Returns:
            Dict[str, Any]: List of matching accounts or error if unauthorized.
        """
        if not self._is_authorized_for_customer(customer_id):
            return {"error": "Unauthorized access to customer accounts"}
        
        if customer_id not in self.customers:
            return {"error": f"Customer with ID '{customer_id}' not found"}
        
        valid_types = ["checking", "savings", "loan"]
        if account_type not in valid_types:
            return {"error": f"Invalid account type. Must be one of: {valid_types}"}
        
        matching_accounts = []
        for account in self.accounts.values():
            if account["customer_id"] == customer_id and account["account_type"] == account_type:
                matching_accounts.append(deepcopy(account))
        
        return {"success": True, "accounts": matching_accounts, "count": len(matching_accounts)}

    def get_active_accounts(self, customer_id: str) -> Dict[str, Any]:
        """
        List all accounts with status 'active' for a given customer.
        
        Args:
            customer_id: The customer whose active accounts to list.
        
        Returns:
            Dict[str, Any]: List of active accounts or error if unauthorized.
        """
        if not self._is_authorized_for_customer(customer_id):
            return {"error": "Unauthorized access to customer accounts"}
        
        if customer_id not in self.customers:
            return {"error": f"Customer with ID '{customer_id}' not found"}
        
        active_accounts = []
        for account in self.accounts.values():
            if account["customer_id"] == customer_id and account["status"] == "active":
                active_accounts.append(deepcopy(account))
        
        return {"success": True, "accounts": active_accounts, "count": len(active_accounts)}

    def check_account_status(self, account_id: str) -> Dict[str, Any]:
        """
        Query the status (active, closed, frozen) of a specific account.
        
        Args:
            account_id: The account ID to check status for.
        
        Returns:
            Dict[str, Any]: Account status or error if not found or unauthorized.
        """
        if not self._is_authorized_for_account(account_id):
            return {"error": "Unauthorized access to account status"}
        
        if account_id not in self.accounts:
            return {"error": f"Account with ID '{account_id}' not found"}
        
        account = self.accounts[account_id]
        return {
            "success": True,
            "account_id": account_id,
            "status": account["status"]
        }

    def get_account_details(self, account_id: str) -> Dict[str, Any]:
        """
        Retrieve comprehensive details of a customer's account.
        
        Includes account number, type, balance, currency, and opening date.
        
        Args:
            account_id: The account ID to get details for.
        
        Returns:
            Dict[str, Any]: Comprehensive account details or error if
                not found or unauthorized.
        """
        if not self._is_authorized_for_account(account_id):
            return {"error": "Unauthorized access to account details"}
        
        if account_id not in self.accounts:
            return {"error": f"Account with ID '{account_id}' not found"}
        
        account = self.accounts[account_id]
        
        return {
            "success": True,
            "account_details": {
                "account_id": account["account_id"],
                "account_type": account["account_type"],
                "balance": account["balance"],
                "currency": account["currency"],
                "status": account["status"],
                "opening_date": account["opening_date"],
                "overdraft_allowed": account.get("overdraft_allowed", False),
                "overdraft_limit": account.get("overdraft_limit", 0.00)
            }
        }

    def authenticate_user(self, user_id: str, role: str = "customer") -> Dict[str, Any]:
        """
        Simulate authentication to verify if a user has access to account data.
        
        Args:
            user_id: The user ID attempting to authenticate.
            role: The role of the user (customer or admin).
        
        Returns:
            Dict[str, Any]: Authentication result with session info or error.
        """
        valid_roles = ["customer", "admin"]
        if role not in valid_roles:
            return {"error": f"Invalid role. Must be one of: {valid_roles}"}
        
        if role == "customer" and user_id not in self.customers:
            return {"error": f"User '{user_id}' not found in customer records"}
        
        authorized_accounts = []
        if role == "customer":
            for account_id, account in self.accounts.items():
                if account["customer_id"] == user_id:
                    authorized_accounts.append(account_id)
        elif role == "admin":
            authorized_accounts = list(self.accounts.keys())
        
        self.current_user = {
            "user_id": user_id,
            "authenticated": True,
            "role": role,
            "authorized_accounts": authorized_accounts
        }
        
        timestamp_str = self._timestamp().replace(':', '').replace('-', '')
        self.session = {
            "session_id": f"SESSION_{user_id}_{timestamp_str}",
            "created_at": self._timestamp(),
            "expires_at": self._timestamp()
        }
        
        return {
            "success": True,
            "message": f"User '{user_id}' authenticated successfully",
            "role": role,
            "authorized_accounts": authorized_accounts,
            "session_id": self.session["session_id"]
        }

    # ==================== STATE CHANGE OPERATIONS ====================

    def open_account(
        self,
        customer_id: str,
        account_type: str,
        initial_balance: float = 0.0,
        currency: str = "USD"
    ) -> Dict[str, Any]:
        """
        Create a new account for a customer.
        
        Args:
            customer_id: The customer to create the account for.
            account_type: Type of account (checking, savings, loan).
            initial_balance: Starting balance (default 0.0).
            currency: Currency code (default USD).
        
        Returns:
            Dict[str, Any]: New account details or error if validation fails.
        """
        if customer_id not in self.customers:
            return {"error": f"Customer with ID '{customer_id}' not found. Account must be linked to a valid customer."}
        
        valid_types = ["checking", "savings", "loan"]
        if account_type not in valid_types:
            return {"error": f"Invalid account type. Must be one of: {valid_types}"}
        
        if account_type != "loan" and initial_balance < 0:
            return {"error": "Initial balance must be non-negative for checking and savings accounts"}
        
        account_number = len(self.accounts) + 1
        account_id = f"ACC{account_number:03d}"
        while account_id in self.accounts:
            account_number += 1
            account_id = f"ACC{account_number:03d}"
        
        new_account = {
            "account_id": account_id,
            "customer_id": customer_id,
            "account_type": account_type,
            "balance": initial_balance,
            "currency": currency,
            "status": "active",
            "opening_date": self._timestamp(),
            "overdraft_allowed": False,
            "overdraft_limit": 0.00
        }
        
        self.accounts[account_id] = new_account
        
        if self.current_user.get("user_id") == customer_id:
            if "authorized_accounts" not in self.current_user:
                self.current_user["authorized_accounts"] = []
            self.current_user["authorized_accounts"].append(account_id)
        
        return {
            "success": True,
            "message": f"Account '{account_id}' created successfully",
            "account": deepcopy(new_account)
        }

    def close_account(self, account_id: str) -> Dict[str, Any]:
        """
        Change an account's status to 'closed'.
        
        Account must be active and have zero balance to be closed.
        
        Args:
            account_id: The account ID to close.
        
        Returns:
            Dict[str, Any]: Success confirmation or error if validation fails.
        """
        if not self._is_authorized_for_account(account_id):
            return {"error": "Unauthorized to close this account"}
        
        if account_id not in self.accounts:
            return {"error": f"Account with ID '{account_id}' not found"}
        
        account = self.accounts[account_id]
        
        if account["status"] != "active":
            return {"error": f"Cannot close account. Account status is '{account['status']}', must be 'active'"}
        
        if account["balance"] != 0:
            return {"error": f"Cannot close account. Balance must be zero (current balance: {account['balance']})"}
        
        self.accounts[account_id]["status"] = "closed"
        
        return {
            "success": True,
            "message": f"Account '{account_id}' has been closed",
            "account_id": account_id,
            "new_status": "closed"
        }

    def freeze_account(self, account_id: str, reason: str = "Security concern") -> Dict[str, Any]:
        """
        Set account status to 'frozen' in response to security concerns.
        
        Args:
            account_id: The account ID to freeze.
            reason: Reason for freezing the account.
        
        Returns:
            Dict[str, Any]: Success confirmation or error if validation fails.
        """
        if not self._is_authorized_for_account(account_id):
            return {"error": "Unauthorized to freeze this account"}
        
        if account_id not in self.accounts:
            return {"error": f"Account with ID '{account_id}' not found"}
        
        account = self.accounts[account_id]
        
        if account["status"] == "closed":
            return {"error": "Cannot freeze a closed account"}
        
        if account["status"] == "frozen":
            return {"error": "Account is already frozen"}
        
        self.accounts[account_id]["status"] = "frozen"
        
        return {
            "success": True,
            "message": f"Account '{account_id}' has been frozen",
            "account_id": account_id,
            "reason": reason,
            "new_status": "frozen"
        }

    def reactivate_account(self, account_id: str) -> Dict[str, Any]:
        """
        Restore a frozen account to 'active' status after verification.
        
        Args:
            account_id: The account ID to reactivate.
        
        Returns:
            Dict[str, Any]: Success confirmation or error if validation fails.
        """
        if not self._is_authorized_for_account(account_id):
            return {"error": "Unauthorized to reactivate this account"}
        
        if account_id not in self.accounts:
            return {"error": f"Account with ID '{account_id}' not found"}
        
        account = self.accounts[account_id]
        
        if account["status"] != "frozen":
            return {"error": f"Cannot reactivate account. Account status is '{account['status']}', must be 'frozen'"}
        
        self.accounts[account_id]["status"] = "active"
        
        return {
            "success": True,
            "message": f"Account '{account_id}' has been reactivated",
            "account_id": account_id,
            "new_status": "active"
        }

    def update_account_balance(
        self,
        account_id: str,
        amount: float,
        operation: str = "deposit"
    ) -> Dict[str, Any]:
        """
        Modify the balance of an account (deposit or withdrawal).
        
        Enforces non-negative balance rules unless overdraft is allowed.
        
        Args:
            account_id: The account ID to update.
            amount: The amount to deposit or withdraw (must be positive).
            operation: Either 'deposit' or 'withdrawal'.
        
        Returns:
            Dict[str, Any]: Updated balance info or error if validation fails.
        """
        if not self._is_authorized_for_account(account_id):
            return {"error": "Unauthorized to update this account balance"}
        
        if account_id not in self.accounts:
            return {"error": f"Account with ID '{account_id}' not found"}
        
        account = self.accounts[account_id]
        
        if account["status"] != "active":
            return {"error": f"Cannot update balance. Account status is '{account['status']}', must be 'active'"}
        
        if amount <= 0:
            return {"error": "Amount must be a positive value"}
        
        valid_operations = ["deposit", "withdrawal"]
        if operation not in valid_operations:
            return {"error": f"Invalid operation. Must be one of: {valid_operations}"}
        
        old_balance = account["balance"]
        
        if operation == "deposit":
            new_balance = old_balance + amount
        else:
            new_balance = old_balance - amount
            
            if new_balance < 0:
                if not account.get("overdraft_allowed", False):
                    return {
                        "error": f"Insufficient funds. Current balance: {old_balance}, withdrawal amount: {amount}"
                    }
                
                overdraft_limit = account.get("overdraft_limit", 0)
                if abs(new_balance) > overdraft_limit:
                    return {
                        "error": f"Withdrawal exceeds overdraft limit. Overdraft limit: {overdraft_limit}, "
                                f"would result in balance: {new_balance}"
                    }
        
        self.accounts[account_id]["balance"] = new_balance
        
        return {
            "success": True,
            "message": f"{operation.capitalize()} of {amount} {account['currency']} completed",
            "account_id": account_id,
            "previous_balance": old_balance,
            "new_balance": new_balance,
            "currency": account["currency"]
        }

    def update_account_contact(
        self,
        account_id: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        address: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update contact information linked to an account via customer record.
        
        Args:
            account_id: The account ID whose customer contact to update.
            email: New email address (optional).
            phone: New phone number (optional).
            address: New address (optional).
        
        Returns:
            Dict[str, Any]: Updated contact info or error if validation fails.
        """
        if not self._is_authorized_for_account(account_id):
            return {"error": "Unauthorized to update contact information"}
        
        if account_id not in self.accounts:
            return {"error": f"Account with ID '{account_id}' not found"}
        
        if email is None and phone is None and address is None:
            return {"error": "At least one contact field (email, phone, or address) must be provided"}
        
        account = self.accounts[account_id]
        customer_id = account["customer_id"]
        
        if customer_id not in self.customers:
            return {"error": f"Customer record not found for account '{account_id}'"}
        
        updated_fields = []
        
        if email is not None:
            self.customers[customer_id]["contact_info"]["email"] = email
            updated_fields.append("email")
        
        if phone is not None:
            self.customers[customer_id]["contact_info"]["phone"] = phone
            updated_fields.append("phone")
        
        if address is not None:
            self.customers[customer_id]["contact_info"]["address"] = address
            updated_fields.append("address")
        
        return {
            "success": True,
            "message": f"Contact information updated for customer '{customer_id}'",
            "updated_fields": updated_fields,
            "contact_info": deepcopy(self.customers[customer_id]["contact_info"])
        }

    def set_overdraft_permission(
        self,
        account_id: str,
        allowed: bool,
        limit: float = 0.0
    ) -> Dict[str, Any]:
        """
        Enable or disable overdraft capability for a checking account.
        
        Args:
            account_id: The account ID to modify.
            allowed: Whether overdraft is allowed.
            limit: Maximum overdraft amount if allowed.
        
        Returns:
            Dict[str, Any]: Updated overdraft settings or error if validation fails.
        """
        if not self._is_authorized_for_account(account_id):
            return {"error": "Unauthorized to modify overdraft settings"}
        
        if account_id not in self.accounts:
            return {"error": f"Account with ID '{account_id}' not found"}
        
        account = self.accounts[account_id]
        
        if account["account_type"] != "checking":
            return {"error": "Overdraft permission can only be set for checking accounts"}
        
        if account["status"] != "active":
            return {"error": f"Cannot modify overdraft settings. Account status is '{account['status']}'"}
        
        if allowed and limit < 0:
            return {"error": "Overdraft limit must be non-negative"}
        
        self.accounts[account_id]["overdraft_allowed"] = allowed
        self.accounts[account_id]["overdraft_limit"] = limit if allowed else 0.0
        
        return {
            "success": True,
            "message": f"Overdraft settings updated for account '{account_id}'",
            "account_id": account_id,
            "overdraft_allowed": allowed,
            "overdraft_limit": self.accounts[account_id]["overdraft_limit"]
        }


__TEST_CASES__ = [
    {
        "name": "Customer authentication and account balance inquiry flow",
        "steps": [
            {"tool_call": "authenticate_user(user_id='CUST001', role='customer')", "expect_success": True},
            {"tool_call": "get_customer_by_id(customer_id='CUST001')", "expect_success": True},
            {"tool_call": "list_customer_accounts(customer_id='CUST001')", "expect_success": True},
            {"tool_call": "get_account_balance(account_id='ACC001')", "expect_success": True}
        ]
    },
    {
        "name": "Account deposit and withdrawal flow",
        "steps": [
            {"tool_call": "authenticate_user(user_id='TELLER001', role='teller')", "expect_success": True},
            {"tool_call": "deposit(account_id='ACC001', amount=500.0, description='Cash deposit')", "expect_success": True},
            {"tool_call": "withdraw(account_id='ACC001', amount=200.0, description='ATM withdrawal')", "expect_success": True},
            {"tool_call": "get_account_balance(account_id='ACC001')", "expect_success": True}
        ]
    },
    {
        "name": "Fund transfer between accounts",
        "steps": [
            {"tool_call": "authenticate_user(user_id='CUST001', role='customer')", "expect_success": True},
            {"tool_call": "transfer(from_account_id='ACC001', to_account_id='ACC002', amount=100.0, description='Transfer to savings')", "expect_success": True},
            {"tool_call": "get_transaction_history(account_id='ACC001', limit=5)", "expect_success": True}
        ]
    },
    {
        "name": "New customer onboarding flow",
        "steps": [
            {"tool_call": "authenticate_user(user_id='MANAGER001', role='manager')", "expect_success": True},
            {"tool_call": "create_customer(first_name='John', last_name='Doe', email='john.doe@email.com', phone='555-0123', address='123 Main St', date_of_birth='1985-06-15')", "expect_success": True},
            {"tool_call": "open_account(customer_id='CUST_NEW', account_type='checking', initial_deposit=1000.0)", "expect_success": True},
            {"tool_call": "open_account(customer_id='CUST_NEW', account_type='savings', initial_deposit=500.0)", "expect_success": True}
        ]
    },
    {
        "name": "Loan application and approval flow",
        "steps": [
            {"tool_call": "authenticate_user(user_id='CUST001', role='customer')", "expect_success": True},
            {"tool_call": "apply_for_loan(customer_id='CUST001', loan_type='personal', amount=10000.0, term_months=36, purpose='Home improvement')", "expect_success": True},
            {"tool_call": "authenticate_user(user_id='MANAGER001', role='manager')", "expect_success": True},
            {"tool_call": "review_loan_application(loan_id='LOAN_NEW', decision='approved', notes='Good credit history')", "expect_success": True}
        ]
    },
    {
        "name": "Account closure flow",
        "steps": [
            {"tool_call": "authenticate_user(user_id='MANAGER001', role='manager')", "expect_success": True},
            {"tool_call": "get_account_balance(account_id='ACC003')", "expect_success": True},
            {"tool_call": "withdraw(account_id='ACC003', amount=0.0, description='Balance withdrawal before closure')", "expect_success": True},
            {"tool_call": "close_account(account_id='ACC003', reason='Customer request')", "expect_success": True}
        ]
    },
    {
        "name": "Overdraft protection setup",
        "steps": [
            {"tool_call": "authenticate_user(user_id='MANAGER001', role='manager')", "expect_success": True},
            {"tool_call": "set_overdraft_permission(account_id='ACC001', allowed=True, limit=500.0)", "expect_success": True},
            {"tool_call": "get_account_details(account_id='ACC001')", "expect_success": True}
        ]
    },
    {
        "name": "Failed withdrawal due to insufficient funds",
        "steps": [
            {"tool_call": "authenticate_user(user_id='CUST001', role='customer')", "expect_success": True},
            {"tool_call": "get_account_balance(account_id='ACC001')", "expect_success": True},
            {"tool_call": "withdraw(account_id='ACC001', amount=999999.0, description='Large withdrawal')", "expect_success": False}
        ]
    },
    {
        "name": "Unauthorized access attempt",
        "steps": [
            {"tool_call": "authenticate_user(user_id='CUST002', role='customer')", "expect_success": True},
            {"tool_call": "get_account_balance(account_id='ACC001')", "expect_success": False},
            {"tool_call": "withdraw(account_id='ACC001', amount=100.0, description='Unauthorized withdrawal')", "expect_success": False}
        ]
    },
    {
        "name": "Customer profile update flow",
        "steps": [
            {"tool_call": "authenticate_user(user_id='CUST001', role='customer')", "expect_success": True},
            {"tool_call": "update_customer_info(customer_id='CUST001', email='newemail@email.com', phone='555-9999')", "expect_success": True},
            {"tool_call": "get_customer_by_id(customer_id='CUST001')", "expect_success": True}
        ]
    },
    {
        "name": "Bill payment flow",
        "steps": [
            {"tool_call": "authenticate_user(user_id='CUST001', role='customer')", "expect_success": True},
            {"tool_call": "schedule_bill_payment(account_id='ACC001', payee='Electric Company', amount=150.0, payment_date='2024-02-01')", "expect_success": True},
            {"tool_call": "list_scheduled_payments(account_id='ACC001')", "expect_success": True},
            {"tool_call": "cancel_scheduled_payment(payment_id='PAY001')", "expect_success": True}
        ]
    },
    {
        "name": "Account statement generation",
        "steps": [
            {"tool_call": "authenticate_user(user_id='CUST001', role='customer')", "expect_success": True},
            {"tool_call": "generate_account_statement(account_id='ACC001', start_date='2024-01-01', end_date='2024-01-31')", "expect_success": True}
        ]
    },
    {
        "name": "Interest calculation for savings account",
        "steps": [
            {"tool_call": "authenticate_user(user_id='MANAGER001', role='manager')", "expect_success": True},
            {"tool_call": "calculate_interest(account_id='ACC002', period_days=30)", "expect_success": True},
            {"tool_call": "apply_interest(account_id='ACC002')", "expect_success": True}
        ]
    },
    {
        "name": "Account freeze and unfreeze flow",
        "steps": [
            {"tool_call": "authenticate_user(user_id='MANAGER001', role='manager')", "expect_success": True},
            {"tool_call": "freeze_account(account_id='ACC001', reason='Suspicious activity')", "expect_success": True},
            {"tool_call": "withdraw(account_id='ACC001', amount=100.0, description='Test withdrawal')", "expect_success": False},
            {"tool_call": "unfreeze_account(account_id='ACC001', reason='Investigation complete')", "expect_success": True}
        ]
    },
    {
        "name": "Credit card application flow",
        "steps": [
            {"tool_call": "authenticate_user(user_id='CUST001', role='customer')", "expect_success": True},
            {"tool_call": "apply_for_credit_card(customer_id='CUST001', card_type='rewards', requested_limit=5000.0)", "expect_success": True},
            {"tool_call": "authenticate_user(user_id='MANAGER001', role='manager')", "expect_success": True},
            {"tool_call": "review_credit_card_application(application_id='CC_APP001', decision='approved', approved_limit=4000.0)", "expect_success": True}
        ]
    }
]


def get_environment():
    """Returns the RetailBankingSystem environment instance."""
    return RetailBankingSystem()