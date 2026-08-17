from copy import deepcopy
from typing import Dict, List, Optional, Union

DEFAULT_STATE = {
    "products": {
        "P1001": {"name": "Wireless Mouse", "price": 25.99, "stock": 50, "category": "Electronics", "rating": 4.5},
        "P1002": {"name": "Mechanical Keyboard", "price": 89.50, "stock": 15, "category": "Electronics", "rating": 4.8},
        "P1003": {"name": "Coffee Beans 1kg", "price": 18.00, "stock": 100, "category": "Groceries", "rating": 4.2},
        "P1004": {"name": "Ergonomic Chair", "price": 199.99, "stock": 5, "category": "Furniture", "rating": 4.6},
    },
    "cart": {},
    "orders": {},
    "order_counter": 5001,
    "discount_codes": {
        "SAVE10": {"discount_percent": 10, "is_active": True},
        "FREESHIP": {"discount_percent": 5, "is_active": True},
        "EXPIRED20": {"discount_percent": 20, "is_active": False}
    },
    "current_user": None,
    "users": {
        "alice": {"balance": 500.00, "vip_status": True},
        "bob": {"balance": 50.00, "vip_status": False}
    },
    "active_discount": None
}


class ShopAPI:
    """
    A class representing an advanced Shop API for an e-commerce platform.

    Attributes:
        products (Dict): Available products with details including stock and rating.
        cart (Dict): Current user's shopping cart.
        orders (Dict): History of orders keyed by order_id.
        order_counter (int): Counter for unique order IDs.
        discount_codes (Dict): Available promotional codes.
        current_user (Optional[str]): Currently authenticated user.
        users (Dict): Database of user accounts and balances.
        active_discount (Optional[str]): Currently applied discount code.
    """

    def __init__(self):
        self.products: Dict[str, Dict[str, Union[str, float, int]]]
        self.cart: Dict[str, int]
        self.orders: Dict[int, Dict[str, Union[int, str, float, dict]]]
        self.order_counter: int
        self.discount_codes: Dict[str, Dict[str, Union[int, bool]]]
        self.current_user: Optional[str]
        self.users: Dict[str, Dict[str, Union[float, bool]]]
        self.active_discount: Optional[str] = None
        self._api_description = "Advanced E-commerce platform tool supporting cart management, discounts, and order lifecycle."

    def _load_scenario(self, scenario: dict, long_context: bool = False) -> None:
        """
        Load a specific scenario into the environment.

        Args:
            scenario (dict): The scenario to load.
            long_context (bool): Whether to use long context.
        """
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_STATE)
        self.products = scenario.get("products", DEFAULT_STATE_COPY["products"])
        self.cart = scenario.get("cart", DEFAULT_STATE_COPY["cart"])
        self.orders = scenario.get("orders", DEFAULT_STATE_COPY["orders"])
        self.order_counter = scenario.get("order_counter", DEFAULT_STATE_COPY["order_counter"])
        self.discount_codes = scenario.get("discount_codes", DEFAULT_STATE_COPY["discount_codes"])
        self.current_user = scenario.get("current_user", DEFAULT_STATE_COPY["current_user"])
        self.users = scenario.get("users", DEFAULT_STATE_COPY["users"])
        self.active_discount = scenario.get("active_discount", DEFAULT_STATE_COPY["active_discount"])

    def get_env_state(self) -> Dict[str, Union[dict, str, int, None]]:
        """
        Get the current environment state.

        Returns:
            Dict[str, Union[dict, str, int, None]]: Current state of products, cart, orders, etc.
        """
        return {
            "products": self.products,
            "cart": self.cart,
            "orders": self.orders,
            "order_counter": self.order_counter,
            "discount_codes": self.discount_codes,
            "current_user": self.current_user,
            "users": self.users,
            "active_discount": self.active_discount
        }

    def login(self, username: str) -> Dict[str, str]:
        """
        Log in a user by username.

        Args:
            username (str): The username to log in.

        Returns:
            Dict[str, str]: Status or error message.
        """
        if username not in self.users:
            return {"error": f"User {username} does not exist."}
        self.current_user = username
        self.cart = {}
        self.active_discount = None
        return {"status": f"Logged in as {username}."}

    def logout(self) -> Dict[str, str]:
        """
        Log out the current user.

        Returns:
            Dict[str, str]: Status message.
        """
        self.current_user = None
        self.cart = {}
        self.active_discount = None
        return {"status": "Logged out successfully."}

    def get_products(self, min_price: float = 0.0, max_price: float = 9999.0) -> Dict[str, dict]:
        """
        Get products filtered by price range.

        Args:
            min_price (float): Minimum price filter.
            max_price (float): Maximum price filter.

        Returns:
            Dict[str, dict]: Filtered products.
        """
        filtered = {
            pid: details for pid, details in self.products.items()
            if min_price <= details["price"] <= max_price
        }
        return {"products": filtered}

    def search_products(self, keyword: str = None, category: str = None) -> Dict[str, Union[str, dict]]:
        """
        Search for products by keyword in the name or by category.

        Args:
            keyword (str, optional): A keyword to search for in product names. Defaults to None.
            category (str, optional): The category to filter products by. Defaults to None.

        Returns:
            Dict[str, Union[str, dict]]: A dictionary of matched products.
        """
        results = {}
        for pid, details in self.products.items():
            match = True
            if keyword is not None and keyword.lower() not in str(details.get("name", "")).lower():
                match = False
            if category is not None and category.lower() != str(details.get("category", "")).lower():
                match = False
            if match:
                results[pid] = details
        return {"products": results}

    def manage_cart(self, action: str, product_id: str, quantity: int = 1) -> Dict[str, Union[str, int, dict]]:
        """
        Add, remove, or update items in the cart.

        Args:
            action (str): 'add', 'remove', or 'update'.
            product_id (str): ID of the product.
            quantity (int): Quantity to apply.

        Returns:
            Dict[str, Union[str, int, dict]]: Status message and current cart, or error message.
        """
        if not self.current_user:
            return {"error": "Authentication required."}
        if product_id not in self.products:
            return {"error": f"Product {product_id} not found."}

        if action == "add":
            if quantity <= 0:
                return {"error": "Quantity to add must be greater than zero."}
            if self.products[product_id]["stock"] < (self.cart.get(product_id, 0) + quantity):
                return {"error": "Insufficient stock."}
            self.cart[product_id] = self.cart.get(product_id, 0) + quantity
        elif action == "update":
            if quantity <= 0:
                self.cart.pop(product_id, None)
            else:
                if self.products[product_id]["stock"] < quantity:
                    return {"error": "Insufficient stock for update."}
                self.cart[product_id] = quantity
        elif action == "remove":
            self.cart.pop(product_id, None)
        else:
            return {"error": "Invalid action. Use 'add', 'update', or 'remove'."}

        return {"status": "Cart updated.", "cart": self.cart}

    def view_cart_summary(self) -> Dict[str, Union[str, float, dict]]:
        """
        Preview the checkout summary including subtotal, discounts, and total cost.

        Returns:
            Dict[str, Union[str, float, dict]]: Summary details or an error message.
        """
        if not self.current_user:
            return {"error": "Authentication required."}

        subtotal = 0.0
        items_summary = {}
        for pid, qty in self.cart.items():
            if pid in self.products:
                price = float(self.products[pid]["price"])
                subtotal += price * qty
                items_summary[pid] = {"name": self.products[pid]["name"], "quantity": qty, "price": price}

        discount_percent = 0
        if self.active_discount and self.active_discount in self.discount_codes:
            if self.discount_codes[self.active_discount]["is_active"]:
                discount_percent = self.discount_codes[self.active_discount]["discount_percent"]

        total_cost = subtotal * (1 - (discount_percent / 100))

        return {
            "items": items_summary,
            "subtotal": subtotal,
            "discount_percent": discount_percent,
            "total_cost": total_cost
        }

    def apply_discount(self, code: str) -> Dict[str, str]:
        """
        Apply a promotional code to the current session.

        Args:
            code (str): The discount code.

        Returns:
            Dict[str, str]: Status or error message.
        """
        if not self.current_user:
            return {"error": "Authentication required."}
        if code not in self.discount_codes:
            return {"error": "Invalid discount code."}
        if not self.discount_codes[code]["is_active"]:
            return {"error": "Discount code is expired."}

        self.active_discount = code
        return {"status": f"Discount code {code} applied successfully."}

    def checkout(self) -> Dict[str, Union[str, int, float]]:
        """
        Process checkout, calculate discounts, deduct balance, and create order.

        Returns:
            Dict[str, Union[str, int, float]]: Status, order ID, and total paid, or error message.
        """
        if not self.current_user:
            return {"error": "Authentication required."}
        if not self.cart:
            return {"error": "Cart is empty."}

        subtotal = 0.0
        for pid, qty in self.cart.items():
            if self.products[pid]["stock"] < qty:
                return {"error": f"Stock changed for {pid}. Checkout aborted."}
            subtotal += self.products[pid]["price"] * qty

        discount_percent = 0
        if self.active_discount:
            discount_percent = self.discount_codes[self.active_discount]["discount_percent"]

        total_cost = subtotal * (1 - (discount_percent / 100))
        user_balance = self.users[self.current_user]["balance"]

        if user_balance < total_cost:
            return {"error": f"Insufficient balance. Total: {total_cost:.2f}, Balance: {user_balance:.2f}"}

        # Commit transaction
        for pid, qty in self.cart.items():
            self.products[pid]["stock"] -= qty

        self.users[self.current_user]["balance"] -= total_cost

        order_id = self.order_counter
        self.orders[order_id] = {
            "order_id": order_id,
            "user": self.current_user,
            "items": deepcopy(self.cart),
            "subtotal": subtotal,
            "discount_applied": self.active_discount,
            "total_paid": total_cost,
            "status": "Processing"
        }

        self.order_counter += 1
        self.cart = {}
        self.active_discount = None

        return {"status": "Order placed successfully.", "order_id": order_id, "total_paid": total_cost}

    def cancel_order(self, order_id: int) -> Dict[str, str]:
        """
        Cancel an order and refund the user if status is 'Processing'.

        Args:
            order_id (int): The ID of the order to cancel.

        Returns:
            Dict[str, str]: Status or error message.
        """
        if not self.current_user:
            return {"error": "Authentication required."}
        if order_id not in self.orders:
            return {"error": "Order not found."}

        order = self.orders[order_id]
        if order["user"] != self.current_user:
            return {"error": "Unauthorized access to order."}
        if order["status"] != "Processing":
            return {"error": f"Cannot cancel order with status '{order['status']}'."}

        # Refund and restock
        self.users[self.current_user]["balance"] += order["total_paid"]
        for pid, qty in order["items"].items():
            self.products[pid]["stock"] += qty

        order["status"] = "Cancelled"
        return {"status": f"Order {order_id} cancelled. {order['total_paid']:.2f} refunded."}

    def get_order_history(self) -> Dict[str, Union[str, dict]]:
        """
        Retrieve the history of orders for the currently authenticated user.

        Returns:
            Dict[str, Union[str, dict]]: A dictionary of user's orders or an error message.
        """
        if not self.current_user:
            return {"error": "Authentication required."}

        user_orders = {
            order_id: details
            for order_id, details in self.orders.items()
            if details["user"] == self.current_user
        }
        return {"orders": user_orders}

    def add_balance(self, amount: float) -> Dict[str, Union[str, float]]:
        """
        Add funds to the currently logged-in user's balance.

        Args:
            amount (float): The amount to add.

        Returns:
            Dict[str, Union[str, float]]: Status message and the new balance, or error message.
        """
        if not self.current_user:
            return {"error": "Authentication required."}
        if amount <= 0:
            return {"error": "Amount to add must be greater than zero."}

        self.users[self.current_user]["balance"] += float(amount)
        return {"status": "Balance added successfully.", "new_balance": self.users[self.current_user]["balance"]}

    def rate_product(self, product_id: str, rating: float) -> Dict[str, Union[str, float]]:
        """
        Rate a product that the user has previously purchased and not cancelled.

        Args:
            product_id (str): The ID of the product.
            rating (float): Rating value, ideally between 1.0 and 5.0.

        Returns:
            Dict[str, Union[str, float]]: Status message and new average rating, or an error message.
        """
        if not self.current_user:
            return {"error": "Authentication required."}
        if product_id not in self.products:
            return {"error": f"Product {product_id} not found."}
        if not (1.0 <= rating <= 5.0):
            return {"error": "Rating must be between 1.0 and 5.0."}

        # Verify purchase
        has_purchased = False
        for order in self.orders.values():
            if order["user"] == self.current_user and order["status"] != "Cancelled":
                if product_id in order["items"]:
                    has_purchased = True
                    break

        if not has_purchased:
            return {"error": "You can only rate products you have purchased."}

        old_rating = float(self.products[product_id].get("rating", rating))
        new_rating = round((old_rating + rating) / 2.0, 1)
        self.products[product_id]["rating"] = new_rating

        return {"status": "Product rated successfully.", "new_rating": new_rating}

__TEST_CASES__ = [
    {
        'name': 'Cross-method workflow: Happy path for login, get products, add to cart, checkout, and logout',
        'steps': [
            {'expect_success': True, 'tool_call': "env['shopping'].login(username='alice')"},
            {'expect_success': True, 'tool_call': "env['shopping'].get_products(min_price=10.0, max_price=100.0)"},
            {'expect_success': True, 'tool_call': "env['shopping'].manage_cart(action='add', product_id='P1001', quantity=2)"},
            {'expect_success': True, 'tool_call': "env['shopping'].checkout()"},
            {'expect_success': True, 'tool_call': "env['shopping'].logout()"}
        ]
    },
    {
        'name': 'State-change verification: Create order and then cancel it',
        'steps': [
            {'expect_success': True, 'tool_call': "env['shopping'].login(username='alice')"},
            {'expect_success': True, 'tool_call': "env['shopping'].manage_cart(action='add', product_id='P1002', quantity=1)"},
            {'expect_success': True, 'tool_call': "env['shopping'].checkout()"},
            {'expect_success': True, 'tool_call': "env['shopping'].cancel_order(order_id=5001)"},
            {'expect_success': True, 'tool_call': "env['shopping'].get_env_state()"}
        ]
    },
    {
        'name': 'Error path: Attempt to manage cart and checkout without logging in',
        'steps': [
            {'expect_success': False, 'tool_call': "env['shopping'].manage_cart(action='add', product_id='P1001', quantity=1)"},
            {'expect_success': False, 'tool_call': "env['shopping'].checkout()"}
        ]
    },
    {
        'name': 'Error path: Invalid product ID and invalid action in manage_cart',
        'steps': [
            {'expect_success': True, 'tool_call': "env['shopping'].login(username='bob')"},
            {'expect_success': False, 'tool_call': "env['shopping'].manage_cart(action='add', product_id='P9999', quantity=1)"},
            {'expect_success': False, 'tool_call': "env['shopping'].manage_cart(action='invalid_action', product_id='P1001', quantity=1)"}
        ]
    },
    {
        'name': 'Boundary values: Adding 0 or negative quantity to cart',
        'steps': [
            {'expect_success': True, 'tool_call': "env['shopping'].login(username='bob')"},
            {'expect_success': False, 'tool_call': "env['shopping'].manage_cart(action='add', product_id='P1001', quantity=0)"},
            {'expect_success': False, 'tool_call': "env['shopping'].manage_cart(action='add', product_id='P1001', quantity=-5)"}
        ]
    },
    {
        'name': 'Boundary values: Attempt to add more items than available in stock',
        'steps': [
            {'expect_success': True, 'tool_call': "env['shopping'].login(username='alice')"},
            {'expect_success': False, 'tool_call': "env['shopping'].manage_cart(action='add', product_id='P1004', quantity=10)"}
        ]
    },
    {
        'name': 'Error path: Checkout with insufficient balance',
        'steps': [
            {'expect_success': True, 'tool_call': "env['shopping'].login(username='bob')"},
            {'expect_success': True, 'tool_call': "env['shopping'].manage_cart(action='add', product_id='P1004', quantity=1)"},
            {'expect_success': False, 'tool_call': "env['shopping'].checkout()"}
        ]
    },
    {
        'name': 'Normal path: Update and remove items from cart',
        'steps': [
            {'expect_success': True, 'tool_call': "env['shopping'].login(username='alice')"},
            {'expect_success': True, 'tool_call': "env['shopping'].manage_cart(action='add', product_id='P1003', quantity=2)"},
            {'expect_success': True, 'tool_call': "env['shopping'].manage_cart(action='update', product_id='P1003', quantity=5)"},
            {'expect_success': True, 'tool_call': "env['shopping'].manage_cart(action='remove', product_id='P1003', quantity=5)"},
            {'expect_success': False, 'tool_call': "env['shopping'].checkout()"}
        ]
    },
    {
        'name': 'Error path: Apply invalid discount code and cancel non-existent/negative order',
        'steps': [
            {'expect_success': True, 'tool_call': "env['shopping'].login(username='alice')"},
            {'expect_success': False, 'tool_call': "env['shopping'].apply_discount(code='INVALID_CODE')"},
            {'expect_success': False, 'tool_call': "env['shopping'].cancel_order(order_id=9999)"},
            {'expect_success': False, 'tool_call': "env['shopping'].cancel_order(order_id=-1)"}
        ]
    },
    {
        'name': 'Boundary values: Empty strings, excessively long inputs, and invalid price ranges',
        'steps': [
            {'expect_success': False, 'tool_call': "env['shopping'].login(username='')"},
            {'expect_success': False, 'tool_call': "env['shopping'].login(username='superlongusernameexceedingnormalcharacterlimitsbyalot1234567890')"},
            {'expect_success': True, 'tool_call': "env['shopping'].get_products(min_price=-50.0, max_price=-10.0)"},
            {'expect_success': True, 'tool_call': "env['shopping'].get_products(min_price=100.0, max_price=50.0)"}
        ]
    },
    {
        'name': 'New Feature: Search products by keyword and category',
        'steps': [
            {'expect_success': True, 'tool_call': "env['shopping'].search_products(keyword='mouse')"},
            {'expect_success': True, 'tool_call': "env['shopping'].search_products(category='Electronics')"},
            {'expect_success': True, 'tool_call': "env['shopping'].search_products(keyword='unknown')"}
        ]
    },
    {
        'name': 'New Feature: View cart summary',
        'steps': [
            {'expect_success': True, 'tool_call': "env['shopping'].login(username='alice')"},
            {'expect_success': True, 'tool_call': "env['shopping'].manage_cart(action='add', product_id='P1001', quantity=1)"},
            {'expect_success': True, 'tool_call': "env['shopping'].apply_discount(code='SAVE10')"},
            {'expect_success': True, 'tool_call': "env['shopping'].view_cart_summary()"}
        ]
    },
    {
        'name': 'New Feature: Add balance to account',
        'steps': [
            {'expect_success': False, 'tool_call': "env['shopping'].add_balance(amount=100.0)"},
            {'expect_success': True, 'tool_call': "env['shopping'].login(username='bob')"},
            {'expect_success': False, 'tool_call': "env['shopping'].add_balance(amount=-50.0)"},
            {'expect_success': True, 'tool_call': "env['shopping'].add_balance(amount=1000.0)"}
        ]
    },
    {
        'name': 'New Feature: Order history and rate product',
        'steps': [
            {'expect_success': True, 'tool_call': "env['shopping'].login(username='alice')"},
            {'expect_success': True, 'tool_call': "env['shopping'].manage_cart(action='add', product_id='P1001', quantity=1)"},
            {'expect_success': True, 'tool_call': "env['shopping'].checkout()"},
            {'expect_success': True, 'tool_call': "env['shopping'].get_order_history()"},
            {'expect_success': True, 'tool_call': "env['shopping'].rate_product(product_id='P1001', rating=5.0)"},
            {'expect_success': False, 'tool_call': "env['shopping'].rate_product(product_id='P1002', rating=4.0)"},
            {'expect_success': False, 'tool_call': "env['shopping'].rate_product(product_id='P1001', rating=6.0)"}
        ]
    }
]