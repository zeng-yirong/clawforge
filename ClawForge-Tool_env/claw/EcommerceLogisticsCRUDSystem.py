from copy import deepcopy
from typing import Dict, List, Optional, Union
from datetime import datetime

DEFAULT_STATE = {
    "shipments": [],
    "return_orders": [],
    "inventory_logs": [],
    "shipment_counter": 1,
    "return_counter": 1,
    "inventory_log_counter": 1,
    "current_user": None,
    "inventory": {
        "electronics": {"quantity": 100, "last_updated": None},
        "clothing": {"quantity": 200, "last_updated": None},
        "home_appliances": {"quantity": 50, "last_updated": None},
        "other": {"quantity": 0, "last_updated": None},
    },
}


class EcommerceLogisticsAPI:
    """
    A class for managing e-commerce logistics, including shipment tracking,
    return/exchange processing, and inventory reconciliation.

    This class provides a comprehensive API for handling shipment status queries,
    managing return/exchange orders, and maintaining inventory logs with reconciliation
    capabilities. It supports user authentication, role-based permissions, and
    complete audit trails for all operations.

    Attributes:
        shipments (List[Dict]): List of all shipment records.
        return_orders (List[Dict]): List of all return/exchange orders.
        inventory_logs (List[Dict]): List of all inventory reconciliation logs.
        shipment_counter (int): Counter for generating unique shipment IDs.
        return_counter (int): Counter for generating unique return order IDs.
        inventory_log_counter (int): Counter for generating unique log IDs.
        current_user (Optional[str]): Currently authenticated user.
        inventory (Dict[str, Dict[str, Union[int, str]]]): Current inventory status.
    """

    def __init__(self):
        """
        Initialize the EcommerceLogisticsAPI instance.
        """
        self.shipments: List[Dict[str, Union[int, str, List[str]]]]
        self.return_orders: List[Dict[str, Union[int, str, List[str]]]]
        self.inventory_logs: List[Dict[str, Union[int, str, float]]]
        self.shipment_counter: int
        self.return_counter: int
        self.inventory_log_counter: int
        self.current_user: Optional[str]
        self.inventory: Dict[str, Dict[str, Union[int, str]]]
        self._api_description = "This tool manages e-commerce logistics operations including shipment tracking, return/exchange processing, and inventory reconciliation."
        self._load_scenario({})

    def _load_scenario(self, scenario: dict, long_context=False) -> None:
        """
        Load a scenario into the e-commerce logistics environment.

        Args:
            scenario (Dict): A dictionary containing initial environment data.
            long_context (bool): Flag for long context handling (future use).
        """
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_STATE)
        self.shipments = scenario.get("shipments", DEFAULT_STATE_COPY["shipments"])
        self.return_orders = scenario.get(
            "return_orders", DEFAULT_STATE_COPY["return_orders"]
        )
        self.inventory_logs = scenario.get(
            "inventory_logs", DEFAULT_STATE_COPY["inventory_logs"]
        )
        self.shipment_counter = scenario.get(
            "shipment_counter", DEFAULT_STATE_COPY["shipment_counter"]
        )
        self.return_counter = scenario.get(
            "return_counter", DEFAULT_STATE_COPY["return_counter"]
        )
        self.inventory_log_counter = scenario.get(
            "inventory_log_counter", DEFAULT_STATE_COPY["inventory_log_counter"]
        )
        self.current_user = scenario.get(
            "current_user", DEFAULT_STATE_COPY["current_user"]
        )
        self.inventory = scenario.get("inventory", DEFAULT_STATE_COPY["inventory"])

    def get_env_state(self) -> dict:
        """
        Return the current internal state of the environment.

        Returns:
            dict: All environment state variables including shipments,
                return_orders, inventory_logs, counters, current_user, and inventory.
        """
        return {
            "shipments": self.shipments,
            "return_orders": self.return_orders,
            "inventory_logs": self.inventory_logs,
            "shipment_counter": self.shipment_counter,
            "return_counter": self.return_counter,
            "inventory_log_counter": self.inventory_log_counter,
            "current_user": self.current_user,
            "inventory": self.inventory,
        }

    def login(self, username: str, password: str) -> Dict[str, bool]:
        """
        Authenticate a user for the logistics system.

        Args:
            username (str): Username of the user.
            password (str): Password of the user.

        Returns:
            success (bool): True if login was successful, False otherwise.
        """
        if not username or not isinstance(username, str):
            return {"success": False}
        if not password or len(str(password)) < 4:
            return {"success": False}
        self.current_user = username
        return {"success": True}

    def logout(self) -> Dict[str, bool]:
        """
        Log out the current user.

        Returns:
            success (bool): True if logout was successful, False otherwise.
        """
        if self.current_user:
            self.current_user = None
            return {"success": True}
        return {"success": False}

    def get_login_status(self) -> Dict[str, bool]:
        """
        Get the authentication status of the current user.

        Returns:
            logged_in (bool): True if a user is logged in, False otherwise.
        """
        return {"logged_in": bool(self.current_user)}

    def create_shipment(
        self,
        order_id: str,
        products: List[str],
        destination: str,
        customer_name: str,
        priority: int = 1,
    ) -> Dict[str, Union[int, str, List[str]]]:
        """
        Create a new shipment record.

        Args:
            order_id (str): Original order ID.
            products (List[str]): List of product names in shipment.
            destination (str): Shipping destination address.
            customer_name (str): Name of the customer.
            priority (int): Shipping priority from 1-3 (1=standard, 2=express, 3=urgent).
                Defaults to 1.

        Returns:
            shipment_id (int): Unique identifier of the shipment.
            order_id (str): Original order ID.
            products (List[str]): List of product names.
            status (str): Current shipment status.
            priority (int): Shipping priority level.
            tracking_history (List[str]): Initial tracking entry.
        """
        if not self.current_user:
            return {"error": "User not authenticated. Please log in to create shipments."}

        if priority < 1 or priority > 3:
            return {"error": "Invalid priority. Priority must be between 1 and 3."}

        shipment = {
            "shipment_id": self.shipment_counter,
            "order_id": order_id,
            "products": products,
            "destination": destination,
            "customer_name": customer_name,
            "status": "Processing",
            "priority": priority,
            "created_by": self.current_user,
            "created_at": datetime.now().isoformat(),
            "tracking_history": [f"Shipment created by {self.current_user} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"],
        }

        self.shipments.append(shipment)
        self.shipment_counter += 1

        # Update inventory
        for product in products:
            category = self._get_product_category(product)
            if category in self.inventory:
                self.inventory[category]["quantity"] -= 1
                self.inventory[category]["last_updated"] = datetime.now().isoformat()

        return shipment

    def get_shipment_status(self, shipment_id: int) -> Dict[str, Union[int, str, List[str]]]:
        """
        Get the current status and tracking history of a shipment.

        Args:
            shipment_id (int): ID of the shipment to retrieve.

        Returns:
            shipment_id (int): Unique identifier of the shipment.
            order_id (str): Original order ID.
            status (str): Current shipment status.
            tracking_history (List[str]): Complete tracking history.
            last_updated (str): Timestamp of last status update.
        """
        shipment = self._find_shipment(shipment_id)
        if not shipment:
            return {"error": f"Shipment with ID {shipment_id} not found."}

        return {
            "shipment_id": shipment["shipment_id"],
            "order_id": shipment["order_id"],
            "status": shipment["status"],
            "tracking_history": shipment["tracking_history"],
            "last_updated": shipment.get("last_updated", ""),
        }

    def update_shipment_status(
        self, shipment_id: int, new_status: str, notes: str = ""
    ) -> Dict[str, str]:
        """
        Update the status of a shipment and add to tracking history.

        Args:
            shipment_id (int): ID of the shipment to update.
            new_status (str): New status for the shipment.
            notes (str): Optional notes about the status update.

        Returns:
            status (str): Status message of the update operation.
        """
        if not self.current_user:
            return {"error": "User not authenticated. Please log in to update shipments."}

        shipment = self._find_shipment(shipment_id)
        if not shipment:
            return {"error": f"Shipment with ID {shipment_id} not found."}

        valid_statuses = ["Processing", "Shipped", "In Transit", "Out for Delivery", "Delivered", "Delayed", "Cancelled"]
        if new_status not in valid_statuses:
            return {"error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"}

        shipment["status"] = new_status
        shipment["last_updated"] = datetime.now().isoformat()
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        note_text = f" - {notes}" if notes else ""
        tracking_entry = f"[{timestamp}] Status updated to '{new_status}' by {self.current_user}{note_text}"
        
        shipment["tracking_history"].append(tracking_entry)

        return {"status": f"Shipment {shipment_id} status updated to '{new_status}'."}

    def create_return_order(
        self,
        order_id: str,
        product_name: str,
        reason: str,
        return_type: str = "refund",
        condition: str = "unopened",
    ) -> Dict[str, Union[int, str]]:
        """
        Create a new return/exchange order.

        Args:
            order_id (str): Original order ID.
            product_name (str): Name of the product being returned.
            reason (str): Reason for return.
            return_type (str): Type of return - "refund" or "exchange". Defaults to "refund".
            condition (str): Condition of returned item - "unopened", "used", or "damaged".
                Defaults to "unopened".

        Returns:
            return_id (int): Unique identifier of the return order.
            order_id (str): Original order ID.
            product_name (str): Name of returned product.
            status (str): Current return status.
            return_type (str): Type of return.
            condition (str): Condition of item.
        """
        if not self.current_user:
            return {"error": "User not authenticated. Please log in to create return orders."}

        if return_type not in ["refund", "exchange"]:
            return {"error": "Invalid return type. Must be 'refund' or 'exchange'."}

        if condition not in ["unopened", "used", "damaged"]:
            return {"error": "Invalid condition. Must be 'unopened', 'used', or 'damaged'."}

        return_order = {
            "return_id": self.return_counter,
            "order_id": order_id,
            "product_name": product_name,
            "reason": reason,
            "status": "Pending Review",
            "return_type": return_type,
            "condition": condition,
            "created_by": self.current_user,
            "created_at": datetime.now().isoformat(),
            "actions": [],
        }

        self.return_orders.append(return_order)
        self.return_counter += 1

        return return_order

    def process_return_order(
        self, return_id: int, action: str, notes: str = ""
    ) -> Dict[str, str]:
        """
        Process a return order (approve, reject, or complete).

        Args:
            return_id (int): ID of the return order to process.
            action (str): Action to take - "approve", "reject", or "complete".
            notes (str): Optional notes about the processing decision.

        Returns:
            status (str): Status message of the processing operation.
        """
        if not self.current_user:
            return {"error": "User not authenticated. Please log in to process returns."}

        return_order = self._find_return_order(return_id)
        if not return_order:
            return {"error": f"Return order with ID {return_id} not found."}

        valid_actions = ["approve", "reject", "complete"]
        if action not in valid_actions:
            return {"error": f"Invalid action. Must be one of: {', '.join(valid_actions)}"}

        if action == "approve":
            if return_order["status"] != "Pending Review":
                return {"error": "Only return orders in 'Pending Review' can be approved."}
            return_order["status"] = "Approved"
            
        elif action == "reject":
            if return_order["status"] != "Pending Review":
                return {"error": "Only return orders in 'Pending Review' can be rejected."}
            return_order["status"] = "Rejected"
            
        elif action == "complete":
            if return_order["status"] not in ["Approved", "Pending Refund"]:
                return {"error": "Only approved return orders can be completed."}
            return_order["status"] = "Completed"
            
            # Restock inventory if condition is unopened
            if return_order["condition"] == "unopened":
                category = self._get_product_category(return_order["product_name"])
                if category in self.inventory:
                    self.inventory[category]["quantity"] += 1
                    self.inventory[category]["last_updated"] = datetime.now().isoformat()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        note_text = f" - {notes}" if notes else ""
        action_entry = f"[{timestamp}] {action.capitalize()} by {self.current_user}{note_text}"
        
        return_order["actions"].append(action_entry)
        return_order["last_updated"] = datetime.now().isoformat()

        return {"status": f"Return order {return_id} {action} action completed successfully."}

    def get_inventory_status(self, category: Optional[str] = None) -> Dict[str, Union[Dict, List[Dict]]]:
        """
        Get current inventory status, optionally filtered by category.

        Args:
            category (str, optional): Specific product category to query.
                If None, returns all inventory.

        Returns:
            inventory (Union[Dict, List[Dict]]): Inventory status for specified category
                or list of all categories with status.
        """
        if not self.current_user:
            return {"error": "User not authenticated. Please log in to view inventory."}

        if category:
            if category not in self.inventory:
                return {"error": f"Category '{category}' not found in inventory."}
            return {category: self.inventory[category]}

        return {"inventory": self.inventory}

    def reconcile_inventory(
        self, category: str, actual_quantity: int, notes: str = ""
    ) -> Dict[str, Union[int, str]]:
        """
        Reconcile inventory by comparing recorded vs actual quantities.

        Args:
            category (str): Product category to reconcile.
            actual_quantity (int): Physically counted quantity.
            notes (str): Optional notes about the reconciliation.

        Returns:
            log_id (int): Unique identifier of the reconciliation log.
            category (str): Reconciled product category.
            recorded_quantity (int): Previously recorded quantity.
            actual_quantity (int): Physically counted quantity.
            discrepancy (int): Difference between recorded and actual.
            adjusted_to (int): New inventory quantity after adjustment.
        """
        if not self.current_user:
            return {"error": "User not authenticated. Please log in to reconcile inventory."}

        if category not in self.inventory:
            return {"error": f"Category '{category}' not found in inventory."}

        recorded_quantity = self.inventory[category]["quantity"]
        discrepancy = actual_quantity - recorded_quantity

        # Update inventory
        self.inventory[category]["quantity"] = actual_quantity
        self.inventory[category]["last_updated"] = datetime.now().isoformat()

        # Create reconciliation log
        log_entry = {
            "log_id": self.inventory_log_counter,
            "category": category,
            "recorded_quantity": recorded_quantity,
            "actual_quantity": actual_quantity,
            "discrepancy": discrepancy,
            "adjusted_to": actual_quantity,
            "reconciled_by": self.current_user,
            "notes": notes,
            "timestamp": datetime.now().isoformat(),
        }

        self.inventory_logs.append(log_entry)
        self.inventory_log_counter += 1

        return log_entry

    def get_reconciliation_history(
        self, category: Optional[str] = None
    ) -> List[Dict[str, Union[int, str]]]:
        """
        Get inventory reconciliation history, optionally filtered by category.

        Args:
            category (str, optional): Product category to filter logs.
                If None, returns all reconciliation logs.

        Returns:
            List[Dict]: List of reconciliation log entries.
        """
        if not self.current_user:
            return {"error": "User not authenticated. Please log in to view reconciliation history."}

        if category:
            return [log for log in self.inventory_logs if log["category"] == category]

        return self.inventory_logs

    def get_user_shipments(self) -> List[Dict[str, Union[int, str, List[str]]]]:
        """
        Get all shipments created by the current user.

        Returns:
            List[Dict]: List of shipment records created by current user.
        """
        if not self.current_user:
            return {"error": "User not authenticated. Please log in to view your shipments."}

        return [
            shipment
            for shipment in self.shipments
            if shipment["created_by"] == self.current_user
        ]

    def get_pending_returns(self) -> List[Dict[str, Union[int, str]]]:
        """
        Get all return orders pending review.

        Returns:
            List[Dict]: List of return orders with status "Pending Review".
        """
        if not self.current_user:
            return {"error": "User not authenticated. Please log in to view pending returns."}

        return [
            return_order
            for return_order in self.return_orders
            if return_order["status"] == "Pending Review"
        ]

    def _find_shipment(self, shipment_id: int) -> Optional[Dict[str, Union[int, str, List[str]]]]:
        """
        Find a shipment by its ID.

        Args:
            shipment_id (int): ID of the shipment to find.

        Returns:
            shipment (Dict): Shipment record if found, None otherwise.
        """
        for shipment in self.shipments:
            if shipment["shipment_id"] == shipment_id:
                return shipment
        return None

    def _find_return_order(self, return_id: int) -> Optional[Dict[str, Union[int, str]]]:
        """
        Find a return order by its ID.

        Args:
            return_id (int): ID of the return order to find.

        Returns:
            return_order (Dict): Return order record if found, None otherwise.
        """
        for return_order in self.return_orders:
            if return_order["return_id"] == return_id:
                return return_order
        return None

    def _get_product_category(self, product_name: str) -> str:
        """
        Determine product category from product name (simplified mapping).

        Args:
            product_name (str): Name of the product.

        Returns:
            str: Product category.
        """
        # This is a simplified mapping - in production, this would be more sophisticated
        product_lower = product_name.lower()
        
        if any(keyword in product_lower for keyword in ["laptop", "phone", "tablet", "camera"]):
            return "electronics"
        elif any(keyword in product_lower for keyword in ["shirt", "pants", "dress", "jacket"]):
            return "clothing"
        elif any(keyword in product_lower for keyword in ["blender", "microwave", "vacuum", "toaster"]):
            return "home_appliances"
        else:
            return "other"

    def _log(self, event: str, detail: Dict) -> None:
        """Log environment events."""
        if not hasattr(self, '_event_log'):
            self._event_log: List[Dict[str, Any]] = []
        self._event_log.append({
            "event": event,
            "detail": detail,
            "timestamp": datetime.now().isoformat()
        })