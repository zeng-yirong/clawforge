import json
import random
from copy import deepcopy
from typing import Dict, List, Optional

# 自定义初始状态
DEFAULT_STATE = {
    "users": {
        "sara_doe_496": {
            "user_id": "sara_doe_496",
            "email": "sara.doe@example.com",
            "name": {"first_name": "Sara", "last_name": "Doe"},
            "address": {
                "address1": "123 Main St",
                "address2": "Apt 4B",
                "city": "San Francisco",
                "state": "CA",
                "country": "USA",
                "zip": "94105"
            },
            "payment_methods": {
                "credit_card_123": {"payment_method_id": "credit_card_123", "type": "credit_card"},
                "gift_card_456": {"payment_method_id": "gift_card_456", "type": "gift_card", "balance": 150.00},
            }
        }
    },
    "products": {
        "6086499569": {
            "product_id": "6086499569",
            "name": "Classic Cotton T-Shirt",
            "variants": {
                "1008292230": {"variant_id": "1008292230", "price": 25.00, "available": True,
                               "options": ["Size: M", "Color: White"]},
                "1008292231": {"variant_id": "1008292231", "price": 25.00, "available": True,
                               "options": ["Size: L", "Color: Black"]}
            }
        }
    },
    "orders": {
        "#W0000000": {
            "order_id": "#W0000000",
            "user_id": "sara_doe_496",
            "status": "pending",
            "items": [
                {"item_id": "1008292230", "product_id": "6086499569", "price": 25.00,
                 "options": ["Size: M", "Color: White"]}
            ],
            "payment_history": [
                {"transaction_type": "payment", "amount": 25.00, "payment_method_id": "credit_card_123"}
            ],
            "address": {
                "address1": "123 Main St", "address2": "Apt 4B", "city": "San Francisco",
                "state": "CA", "country": "USA", "zip": "94105"
            },
            "cancel_reason": None
        },
        "#W0000001": {
            "order_id": "#W0000001",
            "user_id": "sara_doe_496",
            "status": "delivered",
            "items": [
                {"item_id": "1008292231", "product_id": "6086499569", "price": 25.00,
                 "options": ["Size: L", "Color: Black"]}
            ],
            "payment_history": [
                {"transaction_type": "payment", "amount": 25.00, "payment_method_id": "gift_card_456"}
            ],
            "address": {
                "address1": "123 Main St", "address2": "Apt 4B", "city": "San Francisco",
                "state": "CA", "country": "USA", "zip": "94105"
            }
        }
    }
}


class RetailAPI:
    """
    A class representing a Retail API for managing orders, users, and products.
    """

    def __init__(self):
        """
        Initialize the RetailAPI with default structures.
        """
        self.users: Dict[str, dict] = {}
        self.orders: Dict[str, dict] = {}
        self.products: Dict[str, dict] = {}
        self._current_user_id: Optional[str] = None
        self._api_description = "This tool belongs to the Retail API, which is used to manage retail orders, products, and user accounts."

    # ==========================================
    # Authentication methods
    # ==========================================
    def login(self, user_id: str) -> dict:
        """Log in as a user."""
        if user_id not in self.users:
            return {"success": False, "error": "User not found"}
        self._current_user_id = user_id
        return {"success": True, "data": f"Logged in as {user_id}"}

    def logout(self) -> dict:
        """Log out the current user."""
        self._current_user_id = None
        return {"success": True, "data": "Logged out"}

    def _require_auth(self, owner_user_id: str) -> Optional[dict]:
        """Check if current user is authorized to act on behalf of owner_user_id."""
        if self._current_user_id is None:
            return {"success": False, "error": "No user is logged in"}
        if self._current_user_id != owner_user_id:
            return {"success": False, "error": "Unauthorized: cannot act on behalf of another user"}
        return None

    def _load_scenario(self, scenario: dict, long_context: bool = False, **kwargs):
        """
        Load a scenario into the RetailAPI.
        """
        scenario = deepcopy(scenario)
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_STATE)
        self._random = random.Random((scenario.get("random_seed", 42)))

        self.users = scenario.get("users", DEFAULT_STATE_COPY["users"])
        self.orders = scenario.get("orders", DEFAULT_STATE_COPY["orders"])
        self.products = scenario.get("products", DEFAULT_STATE_COPY["products"])

        # Auto-login first user if any
        if self.users:
            self._current_user_id = list(self.users.keys())[0]
        else:
            self._current_user_id = None

    def get_env_state(self) -> dict:
        """
        Return the current state of the environment (deep copy).
        """
        return deepcopy({
            "users": self.users,
            "orders": self.orders,
            "products": self.products
        })

    # ==========================================
    # Internal Helper Methods (return deep copies for safety)
    # ==========================================

    def _get_order(self, order_id: str) -> dict:
        if order_id not in self.orders:
            return {"error": "Order not found"}
        return deepcopy(self.orders[order_id])

    def _get_user(self, user_id: str) -> dict:
        if user_id not in self.users:
            return {"error": "User not found"}
        return deepcopy(self.users[user_id])

    def _get_product(self, product_id: str) -> dict:
        if product_id not in self.products:
            return {"error": "Product not found"}
        return deepcopy(self.products[product_id])

    def _get_variant(self, product_id: str, variant_id: str) -> dict:
        product = self._get_product(product_id)
        if "error" in product:
            return product
        if variant_id not in product["variants"]:
            return {"error": "Variant not found"}
        return deepcopy(product["variants"][variant_id])

    def _get_payment_method(self, user_id: str, payment_method_id: str) -> dict:
        user = self._get_user(user_id)
        if "error" in user:
            return user
        if payment_method_id not in user["payment_methods"]:
            return {"error": "Payment method not found"}
        return deepcopy(user["payment_methods"][payment_method_id])

    def _is_pending_order(self, order: dict) -> bool:
        return order["status"] == "pending"

    # ==========================================
    # Tool Methods
    # ==========================================

    def calculate(self, expression: str) -> str | dict:
        """
        Evaluate a simple mathematical expression.

        Args:
            expression: The mathematical expression to evaluate.
        Returns:
            The string result of the calculation or an error dictionary.
        """
        if not expression:
            return {"error": "Empty expression"}
        if not all(char in "0123456789+-*/(). " for char in expression):
            return {"error": "Invalid characters in expression"}
        try:
            return str(round(float(eval(expression, {"__builtins__": None}, {})), 2))
        except Exception as e:
            return {"error": f"Calculation error: {str(e)}"}

    def cancel_pending_order(self, order_id: str, reason: str) -> dict:
        """
        Cancel a pending order.

        Args:
            order_id: The ID of the order.
            reason: The reason for cancellation.
        Returns:
            The cancelled order or an error dictionary.
        """
        order = self._get_order(order_id)
        if "error" in order:
            return {"success": False, "error": order["error"]}

        # Authorization: order must belong to current user
        auth_err = self._require_auth(order["user_id"])
        if auth_err:
            return auth_err

        if not self._is_pending_order(order):
            return {"success": False, "error": "Non-pending order cannot be cancelled"}

        # Normalize reason to lowercase for broader matching
        valid_reasons = {"no longer needed", "ordered by mistake", "changed mind"}
        if reason.lower() not in valid_reasons:
            return {"success": False, "error": "Invalid reason"}

        net_payments = {}
        for payment in order.get("payment_history", []):
            pm_id = payment["payment_method_id"]
            amt = payment["amount"]
            if payment["transaction_type"] == "payment":
                net_payments[pm_id] = net_payments.get(pm_id, 0.0) + amt
            elif payment["transaction_type"] == "refund":
                net_payments[pm_id] = net_payments.get(pm_id, 0.0) - amt

        refunds = []
        user_id = order["user_id"]
        user = self._get_user(user_id)
        if "error" in user:
            return {"success": False, "error": user["error"]}

        for pm_id, net_amount in net_payments.items():
            if net_amount > 0:
                refund = {
                    "transaction_type": "refund",
                    "amount": round(net_amount, 2),
                    "payment_method_id": pm_id,
                }
                refunds.append(refund)

                # Update payment method balance if gift card
                if pm_id in user["payment_methods"]:
                    pm = user["payment_methods"][pm_id]
                    if pm["type"] == "gift_card":
                        pm["balance"] += net_amount
                        pm["balance"] = round(pm["balance"], 2)

        # Write back user (payment methods updated)
        self.users[user_id] = user

        order["status"] = "cancelled"
        order["cancel_reason"] = reason.lower()
        order.setdefault("payment_history", []).extend(refunds)

        self.orders[order_id] = order
        return {"success": True, "data": order}

    def exchange_delivered_order_items(
            self,
            order_id: str,
            item_ids: List[str],
            new_item_ids: List[str],
            payment_method_id: str,
    ) -> dict:
        """
        Exchange items in a delivered order for new items.

        Args:
            order_id: The ID of the order.
            item_ids: List of item IDs to exchange.
            new_item_ids: List of new item IDs.
            payment_method_id: The ID of the payment method to use for price differences.
        Returns:
            The updated order or an error dictionary.
        """
        order = self._get_order(order_id)
        if "error" in order:
            return {"success": False, "error": order["error"]}

        auth_err = self._require_auth(order["user_id"])
        if auth_err:
            return auth_err

        if order["status"] != "delivered":
            return {"success": False, "error": "Non-delivered order cannot be exchanged"}

        all_item_ids = [item["item_id"] for item in order["items"]]
        for item_id in item_ids:
            if item_ids.count(item_id) > all_item_ids.count(item_id):
                return {"success": False, "error": f"Number of {item_id} not found."}

        if len(item_ids) != len(new_item_ids):
            return {"success": False, "error": "The number of items to be exchanged should match."}

        diff_price = 0
        # Collect old and new prices for each exchange pair
        exchange_details = []
        for item_id, new_item_id in zip(item_ids, new_item_ids):
            item = next((it for it in order["items"] if it["item_id"] == item_id), None)
            if item is None:
                return {"success": False, "error": f"Item {item_id} not found"}

            product_id = item["product_id"]
            variant = self._get_variant(product_id, new_item_id)
            if "error" in variant:
                return {"success": False, "error": variant["error"]}
            if not variant.get("available", False):
                return {"success": False, "error": f"New item {new_item_id} not found or available"}

            old_price = item["price"]
            new_price = variant["price"]
            diff_price += new_price - old_price
            exchange_details.append((item_id, new_item_id, product_id, old_price, new_price))

        diff_price = round(diff_price, 2)

        # Handle payment for price difference
        user_id = order["user_id"]
        user = self._get_user(user_id)
        if "error" in user:
            return {"success": False, "error": user["error"]}

        payment_method = user["payment_methods"].get(payment_method_id)
        if payment_method is None:
            return {"success": False, "error": "Payment method not found"}

        # If diff_price > 0, charge extra; if diff_price < 0, refund
        if diff_price > 0:
            if payment_method["type"] == "gift_card":
                if payment_method.get("balance", 0) < diff_price:
                    return {"success": False, "error": "Insufficient gift card balance to pay for the price difference"}
                payment_method["balance"] -= diff_price
                payment_method["balance"] = round(payment_method["balance"], 2)
            # For credit_card, we just record the payment (no balance)
            order.setdefault("payment_history", []).append({
                "transaction_type": "payment",
                "amount": diff_price,
                "payment_method_id": payment_method_id,
            })
        elif diff_price < 0:
            refund_amount = -diff_price
            # Refund to the given payment method (original payment method or specified)
            if payment_method["type"] == "gift_card":
                payment_method["balance"] += refund_amount
                payment_method["balance"] = round(payment_method["balance"], 2)
            order.setdefault("payment_history", []).append({
                "transaction_type": "refund",
                "amount": refund_amount,
                "payment_method_id": payment_method_id,
            })

        # Write back payment method changes
        self.users[user_id] = user

        # Update order items
        for old_item_id, new_item_id, product_id, old_price, new_price in exchange_details:
            item = next((it for it in order["items"] if it["item_id"] == old_item_id), None)
            if item:
                item["item_id"] = new_item_id
                item["price"] = new_price
                variant = self._get_variant(product_id, new_item_id)
                item["options"] = variant["options"]

        order["status"] = "exchange requested"
        order["exchange_items"] = sorted(item_ids)
        order["exchange_new_items"] = sorted(new_item_ids)
        order["exchange_payment_method_id"] = payment_method_id
        order["exchange_price_difference"] = diff_price

        self.orders[order_id] = order
        return {"success": True, "data": order}

    def find_user_id_by_name_zip(self, first_name: str, last_name: str, zip: str) -> str | dict:
        """
        Find a user ID by their first name, last name, and zip code.

        Args:
            first_name: The user's first name.
            last_name: The user's last name.
            zip: The user's zip code.
        Returns:
            The user ID string or an error dictionary.
        """
        for user_id, user in self.users.items():
            if (
                    user["name"]["first_name"].lower() == first_name.lower()
                    and user["name"]["last_name"].lower() == last_name.lower()
                    and user["address"]["zip"] == zip
            ):
                return user_id
        return {"error": "User not found"}

    def find_user_id_by_email(self, email: str) -> str | dict:
        """
        Find a user ID by their email address.

        Args:
            email: The user's email address.
        Returns:
            The user ID string or an error dictionary.
        """
        for user_id, user in self.users.items():
            if user["email"].lower() == email.lower():
                return user_id
        return {"error": "User not found"}

    def get_order_details(self, order_id: str) -> dict:
        """
        Get the details of an order.

        Args:
            order_id: The ID of the order.
        Returns:
            The order dictionary or an error dictionary.
        """
        return self._get_order(order_id)

    def get_product_details(self, product_id: str) -> dict:
        """
        Get the details of a product.

        Args:
            product_id: The ID of the product.
        Returns:
            The product dictionary or an error dictionary.
        """
        return self._get_product(product_id)

    def get_user_details(self, user_id: str) -> dict:
        """
        Get the details of a user.

        Args:
            user_id: The ID of the user.
        Returns:
            The user dictionary or an error dictionary.
        """
        return self._get_user(user_id)

    def list_all_product_types(self) -> str:
        """
        List all product types available.

        Returns:
            A JSON string containing a mapping of product names to their IDs.
        """
        product_dict = {
            product["name"]: product["product_id"] for product in self.products.values()
        }
        return json.dumps(product_dict, sort_keys=True)

    def modify_pending_order_address(
            self,
            order_id: str,
            address1: str,
            address2: str,
            city: str,
            state: str,
            country: str,
            zip: str,
    ) -> dict:
        """
        Modify the shipping address of a pending order.

        Args:
            order_id: The ID of the order.
            address1: Line 1 of the address.
            address2: Line 2 of the address.
            city: The city.
            state: The state.
            country: The country.
            zip: The zip code.
        Returns:
            The updated order or an error dictionary.
        """
        order = self._get_order(order_id)
        if "error" in order:
            return {"success": False, "error": order["error"]}

        auth_err = self._require_auth(order["user_id"])
        if auth_err:
            return auth_err

        if not self._is_pending_order(order):
            return {"success": False, "error": "Non-pending order cannot be modified"}

        if not address1 or not city or not state or not country or not zip:
            return {"success": False, "error": "Required address fields cannot be empty"}

        order["address"] = {
            "address1": address1,
            "address2": address2,
            "city": city,
            "state": state,
            "country": country,
            "zip": zip,
        }
        self.orders[order_id] = order
        return {"success": True, "data": order}

    def modify_pending_order_items(
            self,
            order_id: str,
            item_ids: List[str],
            new_item_ids: List[str],
            payment_method_id: str,
    ) -> dict:
        """
        Modify the items of a pending order.

        Args:
            order_id: The ID of the order.
            item_ids: The item IDs to be modified.
            new_item_ids: The new item IDs to replace the old ones.
            payment_method_id: The ID of the payment method to cover any price difference.
        Returns:
            The updated order or an error dictionary.
        """
        order = self._get_order(order_id)
        if "error" in order:
            return {"success": False, "error": order["error"]}

        auth_err = self._require_auth(order["user_id"])
        if auth_err:
            return auth_err

        if not self._is_pending_order(order):
            return {"success": False, "error": "Non-pending order cannot be modified"}

        all_item_ids = [item["item_id"] for item in order["items"]]
        for item_id in item_ids:
            if item_ids.count(item_id) > all_item_ids.count(item_id):
                return {"success": False, "error": f"{item_id} not found"}

        if len(item_ids) != len(new_item_ids):
            return {"success": False, "error": "The number of items to be exchanged should match"}

        diff_price = 0
        for item_id, new_item_id in zip(item_ids, new_item_ids):
            if item_id == new_item_id:
                return {"success": False, "error": "The new item id should be different from the old item id"}

            item = next((item for item in order["items"] if item["item_id"] == item_id), None)
            if item is None:
                return {"success": False, "error": f"Item {item_id} not found"}

            product_id = item["product_id"]
            variant = self._get_variant(product_id, new_item_id)
            if "error" in variant:
                return {"success": False, "error": variant["error"]}
            if not variant.get("available", False):
                return {"success": False, "error": f"New item {new_item_id} not found or available"}

            old_price = item["price"]
            new_price = variant["price"]
            diff_price += new_price - old_price

        user_id = order["user_id"]
        user = self._get_user(user_id)
        if "error" in user:
            return {"success": False, "error": user["error"]}

        payment_method = user["payment_methods"].get(payment_method_id)
        if payment_method is None:
            return {"success": False, "error": "Payment method not found"}

        # Handle payment differential
        if diff_price > 0:
            if payment_method["type"] == "gift_card" and payment_method.get("balance", 0) < diff_price:
                return {"success": False, "error": "Insufficient gift card balance to pay for the new item"}
            if payment_method["type"] == "gift_card":
                payment_method["balance"] -= diff_price
                payment_method["balance"] = round(payment_method["balance"], 2)
            order.setdefault("payment_history", []).append({
                "transaction_type": "payment",
                "amount": diff_price,
                "payment_method_id": payment_method_id,
            })
        elif diff_price < 0:
            refund = -diff_price
            if payment_method["type"] == "gift_card":
                payment_method["balance"] += refund
                payment_method["balance"] = round(payment_method["balance"], 2)
            order.setdefault("payment_history", []).append({
                "transaction_type": "refund",
                "amount": refund,
                "payment_method_id": payment_method_id,
            })

        self.users[user_id] = user

        # Update item details
        for item_id, new_item_id in zip(item_ids, new_item_ids):
            item = next((item for item in order["items"] if item["item_id"] == item_id), None)
            if item is None:
                return {"success": False, "error": f"Item {item_id} not found"}
            variant = self._get_variant(item["product_id"], new_item_id)
            if "error" in variant:
                return {"success": False, "error": variant["error"]}
            item["item_id"] = new_item_id
            item["price"] = variant["price"]
            item["options"] = variant["options"]

        order["status"] = "pending (item modified)"
        self.orders[order_id] = order
        return {"success": True, "data": order}

    def modify_pending_order_payment(
            self,
            order_id: str,
            payment_method_id: str,
    ) -> dict:
        """
        Modify the payment method of a pending order.

        Args:
            order_id: The ID of the order.
            payment_method_id: The ID of the new payment method.
        Returns:
            The updated order or an error dictionary.
        """
        order = self._get_order(order_id)
        if "error" in order:
            return {"success": False, "error": order["error"]}

        auth_err = self._require_auth(order["user_id"])
        if auth_err:
            return auth_err

        if not self._is_pending_order(order):
            return {"success": False, "error": "Non-pending order cannot be modified"}

        user_id = order["user_id"]
        user = self._get_user(user_id)
        if "error" in user:
            return {"success": False, "error": user["error"]}

        new_payment_method = user["payment_methods"].get(payment_method_id)
        if new_payment_method is None:
            return {"success": False, "error": "Payment method not found"}

        net_payments = {}
        total_paid = 0.0
        for payment in order.get("payment_history", []):
            pm_id = payment["payment_method_id"]
            amt = payment["amount"]
            if payment["transaction_type"] == "payment":
                net_payments[pm_id] = net_payments.get(pm_id, 0.0) + amt
                total_paid += amt
            elif payment["transaction_type"] == "refund":
                net_payments[pm_id] = net_payments.get(pm_id, 0.0) - amt
                total_paid -= amt

        total_paid = round(total_paid, 2)

        if total_paid <= 0:
            return {"success": False, "error": "No positive payment amount available to modify."}

        if new_payment_method["type"] == "gift_card" and new_payment_method.get("balance", 0) < total_paid:
            return {"success": False, "error": "Insufficient gift card balance to pay for the order"}

        # Refund to old methods
        for pm_id, net_amt in net_payments.items():
            if net_amt > 0:
                order["payment_history"].append({
                    "transaction_type": "refund",
                    "amount": round(net_amt, 2),
                    "payment_method_id": pm_id,
                })
                old_pm = user["payment_methods"].get(pm_id)
                if old_pm and old_pm["type"] == "gift_card":
                    old_pm["balance"] += net_amt
                    old_pm["balance"] = round(old_pm["balance"], 2)

        # Charge to new method
        order["payment_history"].append({
            "transaction_type": "payment",
            "amount": total_paid,
            "payment_method_id": payment_method_id,
        })

        if new_payment_method["type"] == "gift_card":
            new_payment_method["balance"] -= total_paid
            new_payment_method["balance"] = round(new_payment_method["balance"], 2)

        self.users[user_id] = user
        self.orders[order_id] = order
        return {"success": True, "data": order}

    def modify_user_address(
            self,
            user_id: str,
            address1: str,
            address2: str,
            city: str,
            state: str,
            country: str,
            zip: str,
    ) -> dict:
        """
        Modify the address of a user.

        Args:
            user_id: The ID of the user.
            address1: Line 1 of the address.
            address2: Line 2 of the address.
            city: The city.
            state: The state.
            country: The country.
            zip: The zip code.
        Returns:
            The updated user dictionary or an error dictionary.
        """
        user = self._get_user(user_id)
        if "error" in user:
            return {"success": False, "error": user["error"]}

        auth_err = self._require_auth(user_id)
        if auth_err:
            return auth_err

        if not address1 or not city or not state or not country or not zip:
            return {"success": False, "error": "Required address fields cannot be empty"}

        user["address"] = {
            "address1": address1,
            "address2": address2,
            "city": city,
            "state": state,
            "country": country,
            "zip": zip,
        }
        self.users[user_id] = user
        return {"success": True, "data": user}

    def return_delivered_order_items(
            self,
            order_id: str,
            item_ids: List[str],
            payment_method_id: str,
    ) -> dict:
        """
        Initiate a return for delivered order items.

        Args:
            order_id: The ID of the order.
            item_ids: The item IDs to return.
            payment_method_id: The payment method ID for the refund.
        Returns:
            The updated order or an error dictionary.
        """
        order = self._get_order(order_id)
        if "error" in order:
            return {"success": False, "error": order["error"]}

        auth_err = self._require_auth(order["user_id"])
        if auth_err:
            return auth_err

        if order["status"] != "delivered":
            return {"success": False, "error": "Non-delivered order cannot be returned"}

        user_id = order["user_id"]
        user = self._get_user(user_id)
        if "error" in user:
            return {"success": False, "error": user["error"]}

        payment_method = user["payment_methods"].get(payment_method_id)
        if payment_method is None:
            return {"success": False, "error": "Payment method not found"}

        original_payment_method_id = order.get("payment_history", [{}])[0].get("payment_method_id")
        if payment_method["type"] != "gift_card" and payment_method_id != original_payment_method_id:
            return {"success": False, "error": "Payment method should be the original payment method"}

        all_item_ids = [item["item_id"] for item in order["items"]]
        for item_id in item_ids:
            if item_ids.count(item_id) > all_item_ids.count(item_id):
                return {"success": False, "error": "Some item not found"}

        order["status"] = "return requested"
        order["return_items"] = sorted(item_ids)
        order["return_payment_method_id"] = payment_method_id

        self.orders[order_id] = order
        return {"success": True, "data": order}

    # ==========================================
    # Additional lifecycle methods (to complete return/exchange flows)
    # ==========================================
    def process_return(self, order_id: str) -> dict:
        """
        Complete a previously requested return: refund the returned items.
        """
        order = self._get_order(order_id)
        if "error" in order:
            return {"success": False, "error": order["error"]}
        auth_err = self._require_auth(order["user_id"])
        if auth_err:
            return auth_err
        if order["status"] != "return requested":
            return {"success": False, "error": "Return not requested"}
        # Calculate refund amount based on returned items
        return_items = set(order.get("return_items", []))
        refund_amount = sum(item["price"] for item in order["items"] if item["item_id"] in return_items)
        refund_amount = round(refund_amount, 2)
        payment_method_id = order.get("return_payment_method_id")
        if not payment_method_id:
            return {"success": False, "error": "No return payment method set"}

        user_id = order["user_id"]
        user = self._get_user(user_id)
        if "error" in user:
            return {"success": False, "error": user["error"]}
        pm = user["payment_methods"].get(payment_method_id)
        if pm is None:
            return {"success": False, "error": "Payment method not found"}
        if pm["type"] == "gift_card":
            pm["balance"] += refund_amount
            pm["balance"] = round(pm["balance"], 2)
        order["payment_history"].append({
            "transaction_type": "refund",
            "amount": refund_amount,
            "payment_method_id": payment_method_id,
        })
        order["status"] = "returned"
        self.users[user_id] = user
        self.orders[order_id] = order
        return {"success": True, "data": order}

    def process_exchange(self, order_id: str) -> dict:
        """
        Complete a previously requested exchange: update items and finalize.
        """
        order = self._get_order(order_id)
        if "error" in order:
            return {"success": False, "error": order["error"]}
        auth_err = self._require_auth(order["user_id"])
        if auth_err:
            return auth_err
        if order["status"] != "exchange requested":
            return {"success": False, "error": "Exchange not requested"}
        # Payment already handled in exchange request; just finalize status
        order["status"] = "exchanged"
        self.orders[order_id] = order
        return {"success": True, "data": order}

    def transfer_to_human_agents(self, summary: str) -> str:
        """
        Transfer the interaction to a human agent.

        Args:
            summary: A summary of the issue.
        Returns:
            A string indicating successful transfer.
        """
        return "Transfer successful"


__TEST_CASES__ = [
    {
        'name': 'Normal path & state change: Modify pending order address',
        'steps': [
            {'expect_success': True, 'tool_call': "env['retail'].modify_pending_order_address(order_id='#W0000000', address1='456 New St', address2='', city='San Jose', state='CA', country='USA', zip='95112')"},
            {'expect_success': True, 'tool_call': "env['retail'].get_order_details(order_id='#W0000000')"}
        ]
    },
    {
        'name': 'Normal path & state change: Modify user address',
        'steps': [
            {'expect_success': True, 'tool_call': "env['retail'].modify_user_address(user_id='sara_doe_496', address1='789 User St', address2='Suite 1', city='Los Angeles', state='CA', country='USA', zip='90001')"},
            {'expect_success': True, 'tool_call': "env['retail'].get_user_details(user_id='sara_doe_496')"}
        ]
    },
    {
        'name': 'Cross-method workflow: Find user by email and name/zip, then get details',
        'steps': [
            {'expect_success': True, 'tool_call': "env['retail'].find_user_id_by_email(email='sara.doe@example.com')"},
            {'expect_success': True, 'tool_call': "env['retail'].find_user_id_by_name_zip(first_name='Sara', last_name='Doe', zip='94105')"},
            {'expect_success': True, 'tool_call': "env['retail'].get_user_details(user_id='sara_doe_496')"}
        ]
    },
    {
        'name': 'Cross-method workflow: Exchange delivered order items',
        'steps': [
            {'expect_success': True, 'tool_call': "env['retail'].exchange_delivered_order_items(order_id='#W0000001', item_ids=['1008292231'], new_item_ids=['1008292230'], payment_method_id='credit_card_123')"},
            {'expect_success': True, 'tool_call': "env['retail'].get_order_details(order_id='#W0000001')"}
        ]
    },
    {
        'name': 'Cross-method workflow: Return delivered order items',
        'steps': [
            {'expect_success': True, 'tool_call': "env['retail'].return_delivered_order_items(order_id='#W0000001', item_ids=['1008292231'], payment_method_id='gift_card_456')"},
            {'expect_success': True, 'tool_call': "env['retail'].get_order_details(order_id='#W0000001')"}
        ]
    },
    {
        'name': 'Cross-method workflow: Modify pending order items, payment, and cancel',
        'steps': [
            {'expect_success': True, 'tool_call': "env['retail'].modify_pending_order_items(order_id='#W0000000', item_ids=['1008292230'], new_item_ids=['1008292231'], payment_method_id='credit_card_123')"},
            {'expect_success': True, 'tool_call': "env['retail'].modify_pending_order_payment(order_id='#W0000000', payment_method_id='gift_card_456')"},
            {'expect_success': True, 'tool_call': "env['retail'].cancel_pending_order(order_id='#W0000000', reason='Changed mind')"},
            {'expect_success': True, 'tool_call': "env['retail'].get_order_details(order_id='#W0000000')"}
        ]
    },
    {
        'name': 'Error paths: Non-existent IDs',
        'steps': [
            {'expect_success': False, 'tool_call': "env['retail'].get_order_details(order_id='INVALID_ORDER')"},
            {'expect_success': False, 'tool_call': "env['retail'].get_user_details(user_id='INVALID_USER')"},
            {'expect_success': False, 'tool_call': "env['retail'].get_product_details(product_id='INVALID_PRODUCT')"},
            {'expect_success': False, 'tool_call': "env['retail'].find_user_id_by_email(email='notfound@example.com')"},
            {'expect_success': False, 'tool_call': "env['retail'].find_user_id_by_name_zip(first_name='Unknown', last_name='User', zip='00000')"}
        ]
    },
    {
        'name': 'Error paths: Invalid state transitions',
        'steps': [
            {'expect_success': False, 'tool_call': "env['retail'].cancel_pending_order(order_id='#W0000001', reason='Already delivered')"},
            {'expect_success': False, 'tool_call': "env['retail'].modify_pending_order_address(order_id='#W0000001', address1='1', address2='2', city='3', state='4', country='5', zip='6')"},
            {'expect_success': False, 'tool_call': "env['retail'].modify_pending_order_items(order_id='#W0000001', item_ids=['1008292231'], new_item_ids=['1008292230'], payment_method_id='credit_card_123')"},
            {'expect_success': False, 'tool_call': "env['retail'].modify_pending_order_payment(order_id='#W0000001', payment_method_id='gift_card_456')"},
            {'expect_success': False, 'tool_call': "env['retail'].return_delivered_order_items(order_id='#W0000000', item_ids=['1008292230'], payment_method_id='credit_card_123')"},
            {'expect_success': False, 'tool_call': "env['retail'].exchange_delivered_order_items(order_id='#W0000000', item_ids=['1008292230'], new_item_ids=['1008292231'], payment_method_id='credit_card_123')"}
        ]
    },
    {
        'name': 'Boundary values: Empty strings, long inputs, zero, negative numbers',
        'steps': [
            {'expect_success': True, 'tool_call': "env['retail'].calculate(expression='0 * -1000')"},
            {'expect_success': True, 'tool_call': "env['retail'].transfer_to_human_agents(summary='A very long summary that exceeds normal length AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')"},
            {'expect_success': False, 'tool_call': "env['retail'].modify_user_address(user_id='sara_doe_496', address1='', address2='', city='', state='', country='', zip='')"},
            {'expect_success': False, 'tool_call': "env['retail'].calculate(expression='')"}
        ]
    },
    {
        'name': 'Normal paths: Read-only and utility methods',
        'steps': [
            {'expect_success': True, 'tool_call': "env['retail'].list_all_product_types()"},
            {'expect_success': True, 'tool_call': "env['retail'].get_product_details(product_id='6086499569')"},
            {'expect_success': True, 'tool_call': "env['retail'].calculate(expression='25.0 * 2')"},
            {'expect_success': True, 'tool_call': "env['retail'].get_env_state()"},
            {'expect_success': True, 'tool_call': "env['retail'].transfer_to_human_agents(summary='Need help with my order')"}
        ]
    }
]