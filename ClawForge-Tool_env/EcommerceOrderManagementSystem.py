"""
E-commerce Order Management System Environment API

This environment simulates an e-commerce platform supporting user accounts,
product catalogs, shopping carts, and order management operations.
"""

from copy import deepcopy
from typing import Dict, List, Optional, Any
from datetime import datetime


DEFAULT_STATE: Dict[str, Any] = {
    # User entities
    "users": [
        {"_id": "user_001", "name": "Alice", "account_status": "active"},
        {"_id": "user_002", "name": "Bob", "account_status": "active"},
        {"_id": "user_003", "name": "Charlie", "account_status": "suspended"},
    ],
    # Product entities
    "products": [
        {
            "product_id": "prod_001",
            "name": "Wireless Mouse",
            "category": "Electronics",
            "price": 29.99,
            "stock_quantity": 100,
        },
        {
            "product_id": "prod_002",
            "name": "Mechanical Keyboard",
            "category": "Electronics",
            "price": 89.99,
            "stock_quantity": 50,
        },
        {
            "product_id": "prod_003",
            "name": "USB-C Hub",
            "category": "Electronics",
            "price": 45.00,
            "stock_quantity": 75,
        },
        {
            "product_id": "prod_004",
            "name": "Monitor Stand",
            "category": "Accessories",
            "price": 35.00,
            "stock_quantity": 30,
        },
    ],
    # Cart entities
    "carts": [
        {
            "cart_id": "cart_001",
            "user_id": "user_001",
            "created_at": "2024-01-15T10:00:00",
            "updated_at": "2024-01-15T10:00:00",
        },
        {
            "cart_id": "cart_002",
            "user_id": "user_002",
            "created_at": "2024-01-16T14:30:00",
            "updated_at": "2024-01-16T15:45:00",
        },
        {
            "cart_id": "cart_003",
            "user_id": "user_003",
            "created_at": "2024-01-17T09:00:00",
            "updated_at": "2024-01-17T09:00:00",
        },
    ],
    # CartItem entities
    "cart_items": [
        {"cart_id": "cart_001", "product_id": "prod_001", "quantity": 2},
        {"cart_id": "cart_001", "product_id": "prod_002", "quantity": 1},
        {"cart_id": "cart_002", "product_id": "prod_003", "quantity": 3},
    ],
    # Auxiliary state
    "current_user": None,
    "next_cart_id": 4,
}


class EcommerceOrderManagementSystem:
    """
    E-commerce Order Management System Environment API.

    This class provides an interface for managing an e-commerce platform
    with user accounts, product catalogs, shopping carts, and cart items.
    It supports query operations for retrieving data and state-change
    operations for modifying the platform state.
    """

    def __init__(self) -> None:
        """
        Initialize the E-commerce Order Management System.

        Declares all state attributes with type hints and sets the API description.

        Args:
            None

        Returns:
            None
        """
        self.users: List[Dict[str, Any]] = []
        self.products: List[Dict[str, Any]] = []
        self.carts: List[Dict[str, Any]] = []
        self.cart_items: List[Dict[str, Any]] = []
        self.current_user: Optional[str] = None
        self.next_cart_id: int = 4

        self._api_description: str = (
            "E-commerce platform API for managing users, products, shopping carts, "
            "and cart items with inventory tracking."
        )

    def _timestamp(self) -> str:
        """
        Generate a unified ISO format timestamp string.

        This method centralizes timestamp generation for consistent formatting
        and easier testing with injectable fixed times.

        Args:
            None

        Returns:
            str: Current timestamp in ISO format (YYYY-MM-DDTHH:MM:SS).
        """
        return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    def _load_scenario(self, scenario: Dict[str, Any], long_context: bool = False) -> None:
        """
        Load initial state from the provided scenario dictionary.

        If a key is missing from the scenario, falls back to DEFAULT_STATE values.

        Args:
            scenario: Dictionary containing initial state data to load.
            long_context: Flag for extended context handling (reserved for future use).

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
        Return a dictionary containing all current environment state variables.

        This method provides a complete snapshot of the environment's internal
        state for inspection, debugging, or state persistence purposes.

        Args:
            None

        Returns:
            Dict[str, Any]: A dictionary containing:
                - users: List of user records
                - products: List of product records
                - carts: List of cart records
                - cart_items: List of cart item records
                - current_user: Currently active user ID or None
                - next_cart_id: Counter for generating new cart IDs
        """
        return {
            "users": deepcopy(self.users),
            "products": deepcopy(self.products),
            "carts": deepcopy(self.carts),
            "cart_items": deepcopy(self.cart_items),
            "current_user": self.current_user,
            "next_cart_id": self.next_cart_id,
        }

    # ==================== Query Operations ====================

    def get_user_by_name(self, name: str) -> Dict[str, Any]:
        """
        Retrieve user record using the user's name.

        Args:
            name: The name of the user to search for.

        Returns:
            Dict[str, Any]: User record if found, or error dictionary if not found.
        """
        for user in self.users:
            if user.get("name") == name:
                return {"user": deepcopy(user)}
        return {"error": f"User with name '{name}' not found"}

    def get_cart_by_user_id(self, user_id: str) -> Dict[str, Any]:
        """
        Retrieve the current cart associated with a given user.

        Args:
            user_id: The unique identifier of the user.

        Returns:
            Dict[str, Any]: Cart record if found, or error dictionary if not found.
        """
        for cart in self.carts:
            if cart.get("user_id") == user_id:
                return {"cart": deepcopy(cart)}
        return {"error": f"Cart for user '{user_id}' not found"}

    def get_product_by_name(self, name: str) -> Dict[str, Any]:
        """
        Locate product details in the catalog using its name.

        Args:
            name: The name of the product to search for.

        Returns:
            Dict[str, Any]: Product record if found, or error dictionary if not found.
        """
        for product in self.products:
            if product.get("name") == name:
                return {"product": deepcopy(product)}
        return {"error": f"Product with name '{name}' not found"}

    def get_product_by_id(self, product_id: str) -> Dict[str, Any]:
        """
        Get product details (including stock) by product_id.

        Args:
            product_id: The unique identifier of the product.

        Returns:
            Dict[str, Any]: Product record if found, or error dictionary if not found.
        """
        for product in self.products:
            if product.get("product_id") == product_id:
                return {"product": deepcopy(product)}
        return {"error": f"Product with ID '{product_id}' not found"}

    def check_product_in_catalog(self, product_id: str) -> Dict[str, Any]:
        """
        Verify whether a specified product exists in the catalog.

        Args:
            product_id: The unique identifier of the product to check.

        Returns:
            Dict[str, Any]: Dictionary with 'exists' boolean and product info if found.
        """
        for product in self.products:
            if product.get("product_id") == product_id:
                return {"exists": True, "product_id": product_id}
        return {"exists": False, "product_id": product_id}

    def get_product_stock_quantity(self, product_id: str) -> Dict[str, Any]:
        """
        Get current inventory (stock_quantity) for a product.

        Args:
            product_id: The unique identifier of the product.

        Returns:
            Dict[str, Any]: Stock quantity if product found, or error dictionary.
        """
        for product in self.products:
            if product.get("product_id") == product_id:
                return {
                    "product_id": product_id,
                    "stock_quantity": product.get("stock_quantity", 0),
                }
        return {"error": f"Product with ID '{product_id}' not found"}

    def list_cart_items(self, cart_id: str) -> Dict[str, Any]:
        """
        List all products and quantities present in a user's cart.

        Args:
            cart_id: The unique identifier of the cart.

        Returns:
            Dict[str, Any]: Dictionary containing list of cart items or error.
        """
        # Verify cart exists
        cart_exists = any(cart.get("cart_id") == cart_id for cart in self.carts)
        if not cart_exists:
            return {"error": f"Cart with ID '{cart_id}' not found"}

        items = [
            deepcopy(item)
            for item in self.cart_items
            if item.get("cart_id") == cart_id
        ]
        return {"cart_id": cart_id, "items": items}

    def check_product_in_cart(self, cart_id: str, product_id: str) -> Dict[str, Any]:
        """
        Check if a product already exists as a cart item for specific cart.

        Args:
            cart_id: The unique identifier of the cart.
            product_id: The unique identifier of the product.

        Returns:
            Dict[str, Any]: Dictionary with 'in_cart' boolean and item details if found.
        """
        for item in self.cart_items:
            if item.get("cart_id") == cart_id and item.get("product_id") == product_id:
                return {
                    "in_cart": True,
                    "cart_id": cart_id,
                    "product_id": product_id,
                    "quantity": item.get("quantity", 0),
                }
        return {"in_cart": False, "cart_id": cart_id, "product_id": product_id}

    # ==================== State Change Operations ====================

    def add_product_to_cart(
        self, cart_id: str, product_id: str, quantity: int
    ) -> Dict[str, Any]:
        """
        Add a product to the cart. If present, increment quantity; else create new item.

        Validates constraints:
        - Product must exist in catalog
        - Stock quantity must be sufficient
        - Cart must exist

        Args:
            cart_id: The unique identifier of the cart.
            product_id: The unique identifier of the product to add.
            quantity: The quantity to add (must be positive).

        Returns:
            Dict[str, Any]: Success status or error dictionary.
        """
        # Validate quantity
        if quantity <= 0:
            return {"error": "Quantity must be greater than zero"}

        # Constraint: Only products listed in the catalog can be added
        product = None
        for p in self.products:
            if p.get("product_id") == product_id:
                product = p
                break
        if product is None:
            return {"error": f"Product '{product_id}' not found in catalog"}

        # Verify cart exists
        cart = None
        for c in self.carts:
            if c.get("cart_id") == cart_id:
                cart = c
                break
        if cart is None:
            return {"error": f"Cart '{cart_id}' not found"}

        # Check existing quantity in cart
        existing_item = None
        for item in self.cart_items:
            if item.get("cart_id") == cart_id and item.get("product_id") == product_id:
                existing_item = item
                break

        current_cart_qty = existing_item.get("quantity", 0) if existing_item else 0
        total_requested = current_cart_qty + quantity

        # Constraint: Stock quantity must be >= quantity being added
        if product.get("stock_quantity", 0) < total_requested:
            return {
                "error": f"Insufficient stock. Available: {product.get('stock_quantity', 0)}, "
                f"Requested total: {total_requested}"
            }

        # Constraint: Same product can only appear once per cart (aggregated quantity)
        if existing_item:
            existing_item["quantity"] = total_requested
        else:
            self.cart_items.append({
                "cart_id": cart_id,
                "product_id": product_id,
                "quantity": quantity,
            })

        # Update cart timestamp
        cart["updated_at"] = self._timestamp()

        return {
            "success": True,
            "cart_id": cart_id,
            "product_id": product_id,
            "quantity": total_requested,
        }

    def update_cart_item_quantity(
        self, cart_id: str, product_id: str, quantity: int
    ) -> Dict[str, Any]:
        """
        Update the quantity for an existing cart item in the cart.

        Args:
            cart_id: The unique identifier of the cart.
            product_id: The unique identifier of the product.
            quantity: The new quantity to set (must be positive).

        Returns:
            Dict[str, Any]: Success status or error dictionary.
        """
        if quantity <= 0:
            return {"error": "Quantity must be greater than zero"}

        # Verify cart exists
        cart = None
        for c in self.carts:
            if c.get("cart_id") == cart_id:
                cart = c
                break
        if cart is None:
            return {"error": f"Cart '{cart_id}' not found"}

        # Find cart item
        cart_item = None
        for item in self.cart_items:
            if item.get("cart_id") == cart_id and item.get("product_id") == product_id:
                cart_item = item
                break
        if cart_item is None:
            return {
                "error": f"Product '{product_id}' not found in cart '{cart_id}'"
            }

        # Constraint: Check stock availability
        product = None
        for p in self.products:
            if p.get("product_id") == product_id:
                product = p
                break
        if product is None:
            return {"error": f"Product '{product_id}' not found in catalog"}

        if product.get("stock_quantity", 0) < quantity:
            return {
                "error": f"Insufficient stock. Available: {product.get('stock_quantity', 0)}, "
                f"Requested: {quantity}"
            }

        # Update quantity
        cart_item["quantity"] = quantity
        cart["updated_at"] = self._timestamp()

        return {
            "success": True,
            "cart_id": cart_id,
            "product_id": product_id,
            "new_quantity": quantity,
        }

    def remove_product_from_cart(
        self, cart_id: str, product_id: str
    ) -> Dict[str, Any]:
        """
        Delete a product entry from the cart.

        Args:
            cart_id: The unique identifier of the cart.
            product_id: The unique identifier of the product to remove.

        Returns:
            Dict[str, Any]: Success status or error dictionary.
        """
        # Verify cart exists
        cart = None
        for c in self.carts:
            if c.get("cart_id") == cart_id:
                cart = c
                break
        if cart is None:
            return {"error": f"Cart '{cart_id}' not found"}

        # Find and remove cart item
        for i, item in enumerate(self.cart_items):
            if item.get("cart_id") == cart_id and item.get("product_id") == product_id:
                self.cart_items.pop(i)
                cart["updated_at"] = self._timestamp()
                return {
                    "success": True,
                    "cart_id": cart_id,
                    "removed_product_id": product_id,
                }

        return {"error": f"Product '{product_id}' not found in cart '{cart_id}'"}

    def create_cart_for_user(self, user_id: str) -> Dict[str, Any]:
        """
        Create a new cart instance for the user if none exists.

        Validates constraints:
        - User must exist
        - Each cart is associated with one user (no duplicate carts)

        Args:
            user_id: The unique identifier of the user.

        Returns:
            Dict[str, Any]: New cart details or error dictionary.
        """
        # Verify user exists
        user_exists = any(user.get("_id") == user_id for user in self.users)
        if not user_exists:
            return {"error": f"User '{user_id}' not found"}

        # Constraint: Each cart is associated with one user (check if cart exists)
        for cart in self.carts:
            if cart.get("user_id") == user_id:
                return {
                    "error": f"Cart already exists for user '{user_id}'",
                    "existing_cart_id": cart.get("cart_id"),
                }

        # Create new cart
        new_cart_id = f"cart_{self.next_cart_id:03d}"
        self.next_cart_id += 1
        timestamp = self._timestamp()

        new_cart = {
            "cart_id": new_cart_id,
            "user_id": user_id,
            "created_at": timestamp,
            "updated_at": timestamp,
        }
        self.carts.append(new_cart)

        return {"success": True, "cart": deepcopy(new_cart)}

    def decrement_product_stock_quantity(
        self, product_id: str, quantity: int
    ) -> Dict[str, Any]:
        """
        Decrease catalog stock_quantity after successful cart addition.

        Used when the system reserves inventory immediately upon cart addition.

        Args:
            product_id: The unique identifier of the product.
            quantity: The quantity to decrement (must be positive).

        Returns:
            Dict[str, Any]: Updated stock info or error dictionary.
        """
        if quantity <= 0:
            return {"error": "Quantity must be greater than zero"}

        # Find product
        product = None
        for p in self.products:
            if p.get("product_id") == product_id:
                product = p
                break
        if product is None:
            return {"error": f"Product '{product_id}' not found in catalog"}

        current_stock = product.get("stock_quantity", 0)
        if current_stock < quantity:
            return {
                "error": f"Insufficient stock to decrement. "
                f"Current: {current_stock}, Requested: {quantity}"
            }

        product["stock_quantity"] = current_stock - quantity
        return {
            "success": True,
            "product_id": product_id,
            "previous_stock": current_stock,
            "new_stock": product["stock_quantity"],
        }

    def clear_cart(self, cart_id: str) -> Dict[str, Any]:
        """
        Remove all items from a user's cart, resetting it.

        Args:
            cart_id: The unique identifier of the cart to clear.

        Returns:
            Dict[str, Any]: Success status with count of removed items or error.
        """
        # Verify cart exists
        cart = None
        for c in self.carts:
            if c.get("cart_id") == cart_id:
                cart = c
                break
        if cart is None:
            return {"error": f"Cart '{cart_id}' not found"}

        # Count items to remove
        items_to_remove = [
            item for item in self.cart_items if item.get("cart_id") == cart_id
        ]
        removed_count = len(items_to_remove)

        # Keep only items not belonging to this cart
        self.cart_items = [
            item for item in self.cart_items if item.get("cart_id") != cart_id
        ]

        cart["updated_at"] = self._timestamp()

        return {
            "success": True,
            "cart_id": cart_id,
            "items_removed": removed_count,
        }

    def set_cart_updated_time(self, cart_id: str) -> Dict[str, Any]:
        """
        Update the cart's updated_at timestamp after modification.

        Args:
            cart_id: The unique identifier of the cart.

        Returns:
            Dict[str, Any]: Success status with new timestamp or error dictionary.
        """
        # Find cart
        for cart in self.carts:
            if cart.get("cart_id") == cart_id:
                new_timestamp = self._timestamp()
                cart["updated_at"] = new_timestamp
                return {
                    "success": True,
                    "cart_id": cart_id,
                    "updated_at": new_timestamp,
                }

        return {"error": f"Cart '{cart_id}' not found"}


# ==================== Test Cases ====================

__TEST_CASES__ = [
    {
        "name": "Complete shopping flow - add items and update quantity",
        "steps": [
            {"tool_call": "get_user_by_name(name='Alice')", "expect_success": True},
            {"tool_call": "get_cart_by_user_id(user_id='user_001')", "expect_success": True},
            {"tool_call": "get_product_by_name(name='USB-C Hub')", "expect_success": True},
            {"tool_call": "check_product_in_catalog(product_id='prod_003')", "expect_success": True},
            {"tool_call": "add_product_to_cart(cart_id='cart_001', product_id='prod_003', quantity=2)", "expect_success": True},
            {"tool_call": "list_cart_items(cart_id='cart_001')", "expect_success": True},
            {"tool_call": "update_cart_item_quantity(cart_id='cart_001', product_id='prod_003', quantity=5)", "expect_success": True},
        ]
    },
    {
        "name": "Cart management - remove items and clear cart",
        "steps": [
            {"tool_call": "list_cart_items(cart_id='cart_002')", "expect_success": True},
            {"tool_call": "check_product_in_cart(cart_id='cart_002', product_id='prod_003')", "expect_success": True},
            {"tool_call": "remove_product_from_cart(cart_id='cart_002', product_id='prod_003')", "expect_success": True},
            {"tool_call": "list_cart_items(cart_id='cart_002')", "expect_success": True},
            {"tool_call": "add_product_to_cart(cart_id='cart_002', product_id='prod_001', quantity=1)", "expect_success": True},
            {"tool_call": "clear_cart(cart_id='cart_002')", "expect_success": True},
        ]
    },
    {
        "name": "Inventory management - check and decrement stock",
        "steps": [
            {"tool_call": "get_product_by_id(product_id='prod_004')", "expect_success": True},
            {"tool_call": "get_product_stock_quantity(product_id='prod_004')", "expect_success": True},
            {"tool_call": "decrement_product_stock_quantity(product_id='prod_004', quantity=5)", "expect_success": True},
            {"tool_call": "get_product_stock_quantity(product_id='prod_004')", "expect_success": True},
        ]
    },
    {
        "name": "Error handling - invalid operations",
        "steps": [
            {"tool_call": "get_user_by_name(name='NonExistentUser')", "expect_success": False},
            {"tool_call": "add_product_to_cart(cart_id='cart_001', product_id='invalid_product', quantity=1)", "expect_success": False},
            {"tool_call": "add_product_to_cart(cart_id='cart_001', product_id='prod_001', quantity=9999)", "expect_success": False},
            {"tool_call": "remove_product_from_cart(cart_id='cart_001', product_id='prod_999')", "expect_success": False},
            {"tool_call": "create_cart_for_user(user_id='user_001')", "expect_success": False},
            {"tool_call": "decrement_product_stock_quantity(product_id='prod_001', quantity=0)", "expect_success": False},
            {"tool_call": "update_cart_item_quantity(cart_id='cart_001', product_id='prod_001', quantity=-1)", "expect_success": False},
        ]
    },
    {
        "name": "Cart creation and timestamp update",
        "steps": [
            {"tool_call": "get_user_by_name(name='Charlie')", "expect_success": True},
            {"tool_call": "get_cart_by_user_id(user_id='user_003')", "expect_success": True},
            {"tool_call": "set_cart_updated_time(cart_id='cart_003')", "expect_success": True},
            {"tool_call": "add_product_to_cart(cart_id='cart_003', product_id='prod_002', quantity=1)", "expect_success": True},
            {"tool_call": "list_cart_items(cart_id='cart_003')", "expect_success": True},
        ]
    },
]