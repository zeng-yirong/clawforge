from copy import deepcopy
from typing import Dict, List, Optional, Union, Any, Tuple
from datetime import datetime, timedelta
import random

# ===== Default state definition =====
DEFAULT_STATE = {
    "warehouses": {
        "WH001": {
            "name": "South China Central Warehouse",
            "location": "Guangzhou",
            "capacity": 10000,
            "current_stock": 7500,
            "status": "operational",
            "products": {
                "P001": {"name": "Phone", "quantity": 1200, "threshold": 100},
                "P002": {"name": "Laptop", "quantity": 800, "threshold": 50},
                "P003": {"name": "Headphones", "quantity": 3000, "threshold": 200},
            }
        },
        "WH002": {
            "name": "East China Sub-warehouse",
            "location": "Shanghai",
            "capacity": 8000,
            "current_stock": 6000,
            "status": "operational",
            "products": {
                "P001": {"name": "Phone", "quantity": 900, "threshold": 100},
                "P002": {"name": "Laptop", "quantity": 500, "threshold": 50},
                "P004": {"name": "Tablet", "quantity": 1000, "threshold": 80},
            }
        }
    },
    "orders": {
        "ORD001": {
            "order_id": "ORD001",
            "customer_id": "C001",
            "products": [
                {"product_id": "P001", "name": "Phone", "quantity": 2, "price": 2999},
                {"product_id": "P003", "name": "Headphones", "quantity": 1, "price": 299},
            ],
            "total_amount": 6297,
            "status": "shipped",
            "created_at": "2024-05-20 10:30:00",
            "warehouse": "WH001"
        },
        "ORD002": {
            "order_id": "ORD002",
            "customer_id": "C002",
            "products": [
                {"product_id": "P002", "name": "Laptop", "quantity": 1, "price": 8999},
            ],
            "total_amount": 8999,
            "status": "delivered",
            "created_at": "2024-05-19 14:20:00",
            "warehouse": "WH002"
        }
    },
    "shipments": {
        "SH001": {
            "shipment_id": "SH001",
            "order_id": "ORD001",
            "carrier": "SF Express",
            "tracking_number": "SF123456789",
            "status": "in_transit",
            "from_warehouse": "WH001",
            "to_address": "Science Park, Nanshan District, Shenzhen, Guangdong",
            "estimated_delivery": "2024-05-22 18:00:00",
            "actual_delivery": None,
            "checkpoints": [
                {"time": "2024-05-20 14:30:00", "location": "Guangzhou Sorting Center", "status": "Picked up"},
                {"time": "2024-05-21 09:15:00", "location": "Shenzhen Transfer Center", "status": "In transit"},
            ]
        },
        "SH002": {
            "shipment_id": "SH002",
            "order_id": "ORD002",
            "carrier": "JD Logistics",
            "tracking_number": "JD987654321",
            "status": "delivered",
            "from_warehouse": "WH002",
            "to_address": "Zhangjiang Hi-Tech Park, Pudong New District, Shanghai",
            "estimated_delivery": "2024-05-21 16:00:00",
            "actual_delivery": "2024-05-21 15:30:00",
            "checkpoints": [
                {"time": "2024-05-19 16:45:00", "location": "Shanghai Sorting Center", "status": "Picked up"},
                {"time": "2024-05-20 11:20:00", "location": "Pudong Distribution Station", "status": "In transit"},
                {"time": "2024-05-21 15:30:00", "location": "Pudong New District, Shanghai", "status": "Delivered"},
            ]
        }
    },
    "return_tickets": {
        "RT001": {
            "ticket_id": "RT001",
            "order_id": "ORD002",
            "customer_id": "C002",
            "products": [
                {"product_id": "P002", "name": "Laptop", "quantity": 1, "reason": "Dead pixels on screen"}
            ],
            "status": "processing",
            "type": "return",  # return, exchange
            "requested_at": "2024-05-22 09:15:00",
            "resolution": None,
            "refund_amount": None
        }
    },
    "inventory_audits": [],
    "processing_log": [],
    "counter": {
        "order_counter": 3,
        "shipment_counter": 3,
        "ticket_counter": 2,
        "audit_counter": 1
    }
}

VALID_SHIPMENT_STATUSES = ("pending", "ready_for_pickup", "in_transit", "out_for_delivery", "delivered", "delayed", "cancelled")
VALID_TICKET_STATUSES = ("pending", "processing", "approved", "rejected", "completed", "cancelled")
VALID_TICKET_TYPES = ("return", "exchange")
VALID_AUDIT_TYPES = ("daily", "weekly", "monthly", "spot", "reconciliation")
VALID_WAREHOUSE_STATUSES = ("operational", "maintenance", "closed", "full")


class EcommerceLogisticsEnv:
    """
    E-commerce and logistics management environment: automated logistics status querying, return/exchange ticket processing, and inventory reconciliation.

    This environment follows a pipeline processing design pattern: Data ingestion (orders/tickets) -> Processing (logistics query/ticket review) ->
    Aggregation (cross-warehouse inventory analysis) -> Structured output (logistics reports/inventory reports/reconciliation statements).

    Attributes:
        warehouses (Dict): Warehouse registry containing inventory and capacity information
        orders (Dict): Order records
        shipments (Dict): Logistics shipment records
        return_tickets (Dict): Return/exchange tickets
        inventory_audits (List): Inventory audit logs
        processing_log (List): Environment operation audit log
        counter (Dict): Various ID counters
    """
    
    def __init__(self):
        """
        Initialize environment state attributes.
        """
        self.warehouses: Dict[str, Dict[str, Any]]
        self.orders: Dict[str, Dict[str, Any]]
        self.shipments: Dict[str, Dict[str, Any]]
        self.return_tickets: Dict[str, Dict[str, Any]]
        self.inventory_audits: List[Dict[str, Any]]
        self.processing_log: List[Dict[str, Any]]
        self.counter: Dict[str, int]
        self._api_description = (
            "This tool provides automated e-commerce logistics management, including logistics status tracking, "
            "return/exchange ticket processing, inventory audit reconciliation, and more, "
            "supporting multi-warehouse collaborative management and data analysis report generation."
        )
        self._load_scenario({})

    def _load_scenario(self, scenario: dict, long_context=False) -> None:
        """
        Load initial state from scenario configuration.

        Args:
            scenario (dict): Scenario configuration dictionary containing environment initial state
            long_context (bool): Whether to enable long context mode (reserved parameter, for prototype compatibility)

        Returns:
            None
        """
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_STATE)
        self.warehouses = scenario.get("warehouses", DEFAULT_STATE_COPY["warehouses"])
        self.orders = scenario.get("orders", DEFAULT_STATE_COPY["orders"])
        self.shipments = scenario.get("shipments", DEFAULT_STATE_COPY["shipments"])
        self.return_tickets = scenario.get("return_tickets", DEFAULT_STATE_COPY["return_tickets"])
        self.inventory_audits = scenario.get("inventory_audits", DEFAULT_STATE_COPY["inventory_audits"])
        self.processing_log = scenario.get("processing_log", DEFAULT_STATE_COPY["processing_log"])
        self.counter = scenario.get("counter", DEFAULT_STATE_COPY["counter"])
    
    def get_env_state(self) -> dict:
        """
        Return the complete internal state of the current environment.

        Returns:
            dict: Dictionary containing all environment state variables, including:
                - warehouses: Warehouse state
                - orders: Order records
                - shipments: Logistics records
                - return_tickets: Return/exchange tickets
                - inventory_audits: Inventory audits
                - processing_log: Operation log
                - counter: Counters
        """
        return {
            "warehouses": self.warehouses,
            "orders": self.orders,
            "shipments": self.shipments,
            "return_tickets": self.return_tickets,
            "inventory_audits": self.inventory_audits,
            "processing_log": self.processing_log,
            "counter": self.counter
        }
    
    # ── Warehouse management ──────────────────────────────────────────────────────────
    
    def register_warehouse(
        self,
        warehouse_id: str,
        name: str,
        location: str,
        capacity: int
    ) -> Dict[str, Any]:
        """
        Register a new warehouse.
        
        Args:
            warehouse_id (str): Unique warehouse identifier
            name (str): Warehouse name
            location (str): Warehouse location (city)
            capacity (int): Total warehouse capacity (in units)

        Returns:
            Dict: Registered warehouse information or error message
        """
        if warehouse_id in self.warehouses:
            return {"error": f"Warehouse '{warehouse_id}' already exists."}
        
        self.warehouses[warehouse_id] = {
            "name": name,
            "location": location,
            "capacity": capacity,
            "current_stock": 0,
            "status": "operational",
            "products": {}
        }
        self._log("warehouse_registered", {
            "warehouse_id": warehouse_id,
            "name": name,
            "location": location
        })
        return {
            "success": True,
            "warehouse_id": warehouse_id,
            "warehouse": self.warehouses[warehouse_id]
        }
    
    def list_warehouses(
        self,
        status: Optional[str] = None,
        location: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List warehouses, with filtering by status and location.

        Args:
            status (str, optional): Filter by warehouse status
            location (str, optional): Filter by warehouse location

        Returns:
            Dict: List of matching warehouses
        """
        result = []
        for wh_id, wh_info in self.warehouses.items():
            if status and wh_info["status"] != status:
                continue
            if location and wh_info["location"] != location:
                continue
            
            result.append({
                "warehouse_id": wh_id,
                "name": wh_info["name"],
                "location": wh_info["location"],
                "capacity": wh_info["capacity"],
                "current_stock": wh_info["current_stock"],
                "status": wh_info["status"],
                "product_count": len(wh_info["products"])
            })
        
        return {"warehouses": result}
    
    # ── Inventory management ──────────────────────────────────────────────────────────
    
    def add_product_to_warehouse(
        self,
        warehouse_id: str,
        product_id: str,
        name: str,
        quantity: int,
        threshold: int = 10
    ) -> Dict[str, Any]:
        """
        Add product to warehouse or update inventory.

        Args:
            warehouse_id (str): Warehouse ID
            product_id (str): Product ID
            name (str): Product name
            quantity (int): Quantity
            threshold (int): Inventory alert threshold

        Returns:
            Dict: Operation result
        """
        if warehouse_id not in self.warehouses:
            return {"error": f"Warehouse '{warehouse_id}' does not exist."}

        warehouse = self.warehouses[warehouse_id]

        # Check capacity
        if warehouse["current_stock"] + quantity > warehouse["capacity"]:
            return {"error": f"Warehouse '{warehouse_id}' has insufficient capacity. Current: {warehouse['current_stock']}, Capacity: {warehouse['capacity']}"}

        # Update inventory
        if product_id in warehouse["products"]:
            warehouse["products"][product_id]["quantity"] += quantity
        else:
            warehouse["products"][product_id] = {
                "name": name,
                "quantity": quantity,
                "threshold": threshold
            }
        
        warehouse["current_stock"] += quantity
        
        self._log("product_added", {
            "warehouse_id": warehouse_id,
            "product_id": product_id,
            "quantity": quantity
        })
        
        return {
            "success": True,
            "warehouse_id": warehouse_id,
            "product_id": product_id,
            "current_quantity": warehouse["products"][product_id]["quantity"]
        }
    
    def check_low_stock(self, threshold_percentage: float = 0.2) -> Dict[str, Any]:
        """
        Check all warehouses for low stock products.

        Args:
            threshold_percentage (float): Alert threshold percentage

        Returns:
            Dict: List of low stock products
        """
        low_stock_items = []
        
        for wh_id, wh_info in self.warehouses.items():
            for prod_id, prod_info in wh_info["products"].items():
                # Use custom threshold or percentage threshold
                if prod_info["quantity"] <= prod_info["threshold"]:
                    low_stock_items.append({
                        "warehouse_id": wh_id,
                        "warehouse_name": wh_info["name"],
                        "product_id": prod_id,
                        "product_name": prod_info["name"],
                        "current_quantity": prod_info["quantity"],
                        "threshold": prod_info["threshold"],
                        "warning_type": "custom_threshold"
                    })
                elif prod_info["quantity"] / wh_info["capacity"] < threshold_percentage:
                    low_stock_items.append({
                        "warehouse_id": wh_id,
                        "warehouse_name": wh_info["name"],
                        "product_id": prod_id,
                        "product_name": prod_info["name"],
                        "current_quantity": prod_info["quantity"],
                        "capacity_percentage": round(prod_info["quantity"] / wh_info["capacity"] * 100, 2),
                        "warning_type": "capacity_percentage"
                    })
        
        self._log("low_stock_checked", {
            "threshold_percentage": threshold_percentage,
            "low_stock_count": len(low_stock_items)
        })
        
        return {"low_stock_items": low_stock_items, "count": len(low_stock_items)}
    
    # ── Order processing pipeline ──────────────────────────────────────────────────────
    
    def create_order(
        self,
        customer_id: str,
        products: List[Dict[str, Any]],
        shipping_address: str
    ) -> Dict[str, Any]:
        """
        Create a new order.

        Args:
            customer_id (str): Customer ID
            products (List[Dict]): Product list, each product contains:
                - product_id: Product ID
                - name: Product name
                - quantity: Quantity
                - price: Unit price
            shipping_address (str): Shipping address

        Returns:
            Dict: Order creation result
        """
        # Generate order ID
        order_id = f"ORD{str(self.counter['order_counter']).zfill(3)}"
        self.counter['order_counter'] += 1

        # Calculate total amount
        total_amount = sum(p['quantity'] * p['price'] for p in products)

        # Select shipping warehouse (simple strategy: pick the warehouse with most stock)
        selected_warehouse = None
        for wh_id, wh_info in self.warehouses.items():
            if wh_info['status'] != 'operational':
                continue

            # Check if all products are in stock at this warehouse
            has_all_products = True
            for p in products:
                prod_info = wh_info['products'].get(p['product_id'])
                if not prod_info or prod_info['quantity'] < p['quantity']:
                    has_all_products = False
                    break

            if has_all_products:
                selected_warehouse = wh_id
                break

        if not selected_warehouse:
            return {"error": "No warehouse has sufficient stock to fulfill this order."}

        # Create order record
        order = {
            "order_id": order_id,
            "customer_id": customer_id,
            "products": deepcopy(products),
            "total_amount": total_amount,
            "status": "pending",
            "created_at": self._current_time(),
            "warehouse": selected_warehouse,
            "shipping_address": shipping_address
        }

        self.orders[order_id] = order

        # Reserve inventory
        for p in products:
            self.warehouses[selected_warehouse]["products"][p["product_id"]]["quantity"] -= p["quantity"]
            self.warehouses[selected_warehouse]["current_stock"] -= p["quantity"]
        
        self._log("order_created", {
            "order_id": order_id,
            "customer_id": customer_id,
            "warehouse": selected_warehouse,
            "total_amount": total_amount
        })
        
        return {
            "success": True,
            "order_id": order_id,
            "order": order
        }
    
    def ship_order(self, order_id: str, carrier: str) -> Dict[str, Any]:
        """
        Create a logistics shipment record for an order.

        Args:
            order_id (str): Order ID
            carrier (str): Logistics carrier

        Returns:
            Dict: Logistics record information
        """
        if order_id not in self.orders:
            return {"error": f"Order '{order_id}' does not exist."}

        order = self.orders[order_id]

        if order["status"] not in ("pending", "processing"):
            return {"error": f"Order '{order_id}' with status '{order['status']}' cannot be shipped."}

        # Generate shipment ID
        shipment_id = f"SH{str(self.counter['shipment_counter']).zfill(3)}"
        self.counter['shipment_counter'] += 1

        # Generate tracking number
        tracking_number = self._generate_tracking_number(carrier)

        # Create logistics record
        shipment = {
            "shipment_id": shipment_id,
            "order_id": order_id,
            "carrier": carrier,
            "tracking_number": tracking_number,
            "status": "ready_for_pickup",
            "from_warehouse": order["warehouse"],
            "to_address": order["shipping_address"],
            "estimated_delivery": self._future_time(2),  # Default 2 days later
            "actual_delivery": None,
            "checkpoints": [
                {
                    "time": self._current_time(),
                    "location": self.warehouses[order["warehouse"]]["name"],
                    "status": "Order confirmed"
                }
            ]
        }
        
        self.shipments[shipment_id] = shipment
        
        # Update order status
        order["status"] = "shipped"
        
        self._log("order_shipped", {
            "order_id": order_id,
            "shipment_id": shipment_id,
            "carrier": carrier
        })
        
        return {
            "success": True,
            "shipment_id": shipment_id,
            "tracking_number": tracking_number,
            "shipment": shipment
        }
    
    # ── Logistics status query pipeline ──────────────────────────────────────────────────
    
    def track_shipment(
        self,
        identifier: str,
        use_tracking_number: bool = False
    ) -> Dict[str, Any]:
        """
        Query logistics status.

        Args:
            identifier (str): Shipment ID or tracking number
            use_tracking_number (bool): Whether to use tracking number for query

        Returns:
            Dict: Logistics status information
        """
        shipment = None

        if use_tracking_number:
            # Find by tracking number
            for s in self.shipments.values():
                if s["tracking_number"] == identifier:
                    shipment = s
                    break
        else:
            # Find by shipment ID
            shipment = self.shipments.get(identifier)

        if not shipment:
            return {"error": f"Logistics record not found: {identifier}"}

        # Simulate logistics status update
        self._simulate_shipment_progress(shipment)
        
        self._log("shipment_tracked", {
            "shipment_id": shipment["shipment_id"],
            "status": shipment["status"]
        })
        
        return {
            "shipment_id": shipment["shipment_id"],
            "order_id": shipment["order_id"],
            "carrier": shipment["carrier"],
            "tracking_number": shipment["tracking_number"],
            "status": shipment["status"],
            "current_location": shipment["checkpoints"][-1]["location"] if shipment["checkpoints"] else "Unknown",
            "estimated_delivery": shipment["estimated_delivery"],
            "actual_delivery": shipment["actual_delivery"],
            "checkpoints": shipment["checkpoints"],
            "is_delayed": shipment["status"] == "delayed"
        }
    
    def track_order_shipments(self, order_id: str) -> Dict[str, Any]:
        """
        Query all logistics records for an order.

        Args:
            order_id (str): Order ID

        Returns:
            Dict: All logistics statuses for the order
        """
        if order_id not in self.orders:
            return {"error": f"Order '{order_id}' does not exist."}

        order_shipments = []
        for shipment in self.shipments.values():
            if shipment["order_id"] == order_id:
                # Simulate status update
                self._simulate_shipment_progress(shipment)
                order_shipments.append(shipment)
        
        if not order_shipments:
            return {"error": f"Order '{order_id}' has no logistics records."}
        
        order = self.orders[order_id]
        
        return {
            "order_id": order_id,
            "order_status": order["status"],
            "shipments": order_shipments,
            "total_shipments": len(order_shipments)
        }
    
    # ── Return/exchange ticket processing pipeline ──────────────────────────────────────────────
    
    def create_return_ticket(
        self,
        order_id: str,
        customer_id: str,
        products: List[Dict[str, Any]],
        reason: str,
        ticket_type: str = "return"
    ) -> Dict[str, Any]:
        """
        Create a return/exchange ticket.

        Args:
            order_id (str): Original order ID
            customer_id (str): Customer ID
            products (List[Dict]): List of products to return/exchange, containing:
                - product_id: Product ID
                - name: Product name
                - quantity: Quantity
                - reason: Return/exchange reason
            reason (str): Overall return/exchange reason
            ticket_type (str): Ticket type (return or exchange)

        Returns:
            Dict: Created ticket information
        """
        if ticket_type not in VALID_TICKET_TYPES:
            return {"error": f"Invalid ticket type '{ticket_type}'. Must be: {', '.join(VALID_TICKET_TYPES)}"}

        if order_id not in self.orders:
            return {"error": f"Order '{order_id}' does not exist."}

        # Check if a pending ticket already exists for the same order
        for ticket in self.return_tickets.values():
            if ticket["order_id"] == order_id and ticket["status"] in ("pending", "processing"):
                return {"error": f"Order '{order_id}' already has a pending return/exchange ticket: {ticket['ticket_id']}"}

        # Generate ticket ID
        ticket_id = f"RT{str(self.counter['ticket_counter']).zfill(3)}"
        self.counter['ticket_counter'] += 1

        # Calculate refund amount
        order = self.orders[order_id]
        refund_amount = 0
        for p in products:
            for op in order['products']:
                if op['product_id'] == p['product_id']:
                    refund_amount += op['price'] * p['quantity']
                    break
        
        # Create ticket
        ticket = {
            "ticket_id": ticket_id,
            "order_id": order_id,
            "customer_id": customer_id,
            "products": deepcopy(products),
            "status": "pending",
            "type": ticket_type,
            "reason": reason,
            "requested_at": self._current_time(),
            "resolution": None,
            "refund_amount": refund_amount if ticket_type == "return" else 0,
            "processed_by": None,
            "processed_at": None
        }
        
        self.return_tickets[ticket_id] = ticket
        
        self._log("return_ticket_created", {
            "ticket_id": ticket_id,
            "order_id": order_id,
            "type": ticket_type,
            "refund_amount": refund_amount
        })
        
        return {
            "success": True,
            "ticket_id": ticket_id,
            "ticket": ticket
        }
    
    def process_return_ticket(
        self,
        ticket_id: str,
        action: str,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a return/exchange ticket.

        Args:
            ticket_id (str): Ticket ID
            action (str): Processing action (approve, reject, cancel)
            notes (str, optional): Processing notes

        Returns:
            Dict: Processing result
        """
        if ticket_id not in self.return_tickets:
            return {"error": f"Ticket '{ticket_id}' does not exist."}

        ticket = self.return_tickets[ticket_id]

        if ticket["status"] not in ("pending", "processing"):
            return {"error": f"Ticket '{ticket_id}' with status '{ticket['status']}' cannot be processed."}

        if action == "approve":
            ticket["status"] = "approved"
            ticket["resolution"] = "approved"

            # If it's a return, update inventory
            if ticket["type"] == "return":
                order = self.orders.get(ticket["order_id"])
                if order:
                    warehouse_id = order["warehouse"]
                    for p in ticket["products"]:
                        if p["product_id"] in self.warehouses[warehouse_id]["products"]:
                            self.warehouses[warehouse_id]["products"][p["product_id"]]["quantity"] += p["quantity"]
                            self.warehouses[warehouse_id]["current_stock"] += p["quantity"]
            
            # If it's an exchange, create a new order (simplified handling)
            elif ticket["type"] == "exchange":
                # This can be extended to automatically create an exchange order
                pass
                
        elif action == "reject":
            ticket["status"] = "rejected"
            ticket["resolution"] = "rejected"
            ticket["refund_amount"] = 0
            
        elif action == "cancel":
            ticket["status"] = "cancelled"
            ticket["resolution"] = "cancelled_by_customer"
            
        else:
            return {"error": f"Invalid processing action '{action}'. Must be: approve, reject, cancel"}
        
        ticket["processed_at"] = self._current_time()
        ticket["processed_by"] = "system"
        if notes:
            ticket["notes"] = notes
        
        self._log("return_ticket_processed", {
            "ticket_id": ticket_id,
            "action": action,
            "status": ticket["status"]
        })
        
        return {
            "success": True,
            "ticket_id": ticket_id,
            "status": ticket["status"],
            "resolution": ticket["resolution"],
            "refund_amount": ticket.get("refund_amount", 0)
        }
    
    def list_return_tickets(
        self,
        status: Optional[str] = None,
        ticket_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List return/exchange tickets.

        Args:
            status (str, optional): Filter by ticket status
            ticket_type (str, optional): Filter by ticket type

        Returns:
            Dict: Ticket list
        """
        if status and status not in VALID_TICKET_STATUSES:
            return {"error": f"Invalid ticket status '{status}'."}

        if ticket_type and ticket_type not in VALID_TICKET_TYPES:
            return {"error": f"Invalid ticket type '{ticket_type}'."}
        
        tickets = []
        for ticket_id, ticket_info in self.return_tickets.items():
            if status and ticket_info["status"] != status:
                continue
            if ticket_type and ticket_info["type"] != ticket_type:
                continue
            
            tickets.append({
                "ticket_id": ticket_id,
                "order_id": ticket_info["order_id"],
                "customer_id": ticket_info["customer_id"],
                "type": ticket_info["type"],
                "status": ticket_info["status"],
                "reason": ticket_info.get("reason", ""),
                "refund_amount": ticket_info.get("refund_amount", 0),
                "requested_at": ticket_info["requested_at"]
            })
        
        return {"tickets": tickets, "count": len(tickets)}
    
    # ── Inventory reconciliation pipeline ──────────────────────────────────────────────────
    
    def perform_inventory_audit(
        self,
        warehouse_id: str,
        audit_type: str = "spot",
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Perform an inventory audit.

        Args:
            warehouse_id (str): Warehouse ID
            audit_type (str): Audit type
            notes (str, optional): Audit notes

        Returns:
            Dict: Audit result
        """
        if warehouse_id not in self.warehouses:
            return {"error": f"Warehouse '{warehouse_id}' does not exist."}

        if audit_type not in VALID_AUDIT_TYPES:
            return {"error": f"Invalid audit type '{audit_type}'. Must be: {', '.join(VALID_AUDIT_TYPES)}"}

        warehouse = self.warehouses[warehouse_id]

        # Generate audit ID
        audit_id = f"AUD{str(self.counter['audit_counter']).zfill(3)}"
        self.counter['audit_counter'] += 1

        # Simulate actual inventory (add some random discrepancy)
        actual_counts = {}
        discrepancies = []

        for prod_id, prod_info in warehouse["products"].items():
            # Simulate actual inventory (90% chance to match, 10% chance of discrepancy)
            if random.random() > 0.1:
                actual_count = prod_info["quantity"]
            else:
                # Discrepancy within ±5% range
                diff_range = int(prod_info["quantity"] * 0.05)
                actual_count = prod_info["quantity"] + random.randint(-diff_range, diff_range)
            
            actual_counts[prod_id] = actual_count
            
            if actual_count != prod_info["quantity"]:
                discrepancies.append({
                    "product_id": prod_id,
                    "product_name": prod_info["name"],
                    "recorded_quantity": prod_info["quantity"],
                    "actual_quantity": actual_count,
                    "difference": actual_count - prod_info["quantity"]
                })
        
        # Create audit record
        audit_record = {
            "audit_id": audit_id,
            "warehouse_id": warehouse_id,
            "warehouse_name": warehouse["name"],
            "audit_type": audit_type,
            "performed_at": self._current_time(),
            "performed_by": "system",
            "recorded_total": warehouse["current_stock"],
            "actual_total": sum(actual_counts.values()),
            "product_count": len(warehouse["products"]),
            "actual_counts": actual_counts,
            "discrepancies": discrepancies,
            "discrepancy_count": len(discrepancies),
            "notes": notes or "",
            "status": "completed"
        }
        
        self.inventory_audits.append(audit_record)
        
        self._log("inventory_audit_performed", {
            "audit_id": audit_id,
            "warehouse_id": warehouse_id,
            "discrepancy_count": len(discrepancies)
        })
        
        return {
            "success": True,
            "audit_id": audit_id,
            "audit_record": audit_record,
            "has_discrepancies": len(discrepancies) > 0
        }
    
    def reconcile_inventory(
        self,
        audit_id: str,
        auto_adjust: bool = False
    ) -> Dict[str, Any]:
        """
        Reconcile and adjust inventory.

        Args:
            audit_id (str): Audit record ID
            auto_adjust (bool): Whether to automatically adjust inventory

        Returns:
            Dict: Reconciliation result
        """
        # Find audit record
        audit_record = None
        for audit in self.inventory_audits:
            if audit["audit_id"] == audit_id:
                audit_record = audit
                break

        if not audit_record:
            return {"error": f"Audit record '{audit_id}' does not exist."}

        if audit_record["status"] != "completed":
            return {"error": f"Audit record '{audit_id}' has status '{audit_record['status']}', cannot reconcile."}

        warehouse_id = audit_record["warehouse_id"]
        warehouse = self.warehouses[warehouse_id]

        adjustments = []

        if auto_adjust:
            # Automatically adjust inventory
            for disc in audit_record["discrepancies"]:
                prod_id = disc["product_id"]
                if prod_id in warehouse["products"]:
                    old_qty = warehouse["products"][prod_id]["quantity"]
                    new_qty = disc["actual_quantity"]

                    warehouse["products"][prod_id]["quantity"] = new_qty

                    # Update total warehouse inventory
                    diff = new_qty - old_qty
                    warehouse["current_stock"] += diff
                    
                    adjustments.append({
                        "product_id": prod_id,
                        "product_name": disc["product_name"],
                        "old_quantity": old_qty,
                        "new_quantity": new_qty,
                        "difference": diff
                    })
        
        audit_record["status"] = "reconciled"
        audit_record["reconciled_at"] = self._current_time()
        audit_record["auto_adjust"] = auto_adjust
        if adjustments:
            audit_record["adjustments"] = adjustments
        
        self._log("inventory_reconciled", {
            "audit_id": audit_id,
            "warehouse_id": warehouse_id,
            "auto_adjust": auto_adjust,
            "adjustments_count": len(adjustments)
        })
        
        return {
            "success": True,
            "audit_id": audit_id,
            "warehouse_id": warehouse_id,
            "auto_adjust": auto_adjust,
            "adjustments": adjustments if adjustments else "Not adjusted, report only",
            "total_adjustments": len(adjustments)
        }
    
    # ── Report generation ──────────────────────────────────────────────────────
    
    def generate_logistics_report(
        self,
        report_type: str = "daily",
        warehouse_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate a logistics operations report.

        Args:
            report_type (str): Report type (daily, weekly, monthly)
            warehouse_ids (List[str], optional): List of warehouse IDs, None means all warehouses

        Returns:
            Dict: Logistics report
        """
        target_warehouses = warehouse_ids or list(self.warehouses.keys())
        
        # Statistics
        orders_today = sum(1 for order in self.orders.values() 
                          if order["created_at"].startswith("2024-05-22"))  # Simplified, assuming today
        
        shipments_in_transit = sum(1 for shipment in self.shipments.values()
                                  if shipment["status"] == "in_transit")
        
        shipments_delivered_today = sum(1 for shipment in self.shipments.values()
                                       if shipment["actual_delivery"] and 
                                       shipment["actual_delivery"].startswith("2024-05-22"))
        
        # Warehouse utilization
        warehouse_stats = []
        for wh_id in target_warehouses:
            if wh_id in self.warehouses:
                wh = self.warehouses[wh_id]
                utilization = (wh["current_stock"] / wh["capacity"]) * 100 if wh["capacity"] > 0 else 0
                warehouse_stats.append({
                    "warehouse_id": wh_id,
                    "name": wh["name"],
                    "utilization_percentage": round(utilization, 2),
                    "current_stock": wh["current_stock"],
                    "capacity": wh["capacity"]
                })
        
        report = {
            "report_id": f"LOG_REPORT_{self._current_time().replace(' ', '_').replace(':', '-')}",
            "report_type": report_type,
            "generated_at": self._current_time(),
            "period": "2024-05-22",  # Simplified
            "summary": {
                "total_orders": len(self.orders),
                "orders_today": orders_today,
                "total_shipments": len(self.shipments),
                "shipments_in_transit": shipments_in_transit,
                "shipments_delivered_today": shipments_delivered_today,
                "return_tickets_pending": sum(1 for t in self.return_tickets.values() 
                                             if t["status"] in ("pending", "processing"))
            },
            "warehouse_statistics": warehouse_stats,
            "performance_metrics": {
                "estimated_on_time_delivery": 92.5,  # Simulated data
                "customer_satisfaction_score": 4.3,
                "return_rate": 2.1
            }
        }
        
        self._log("logistics_report_generated", {
            "report_type": report_type,
            "warehouse_count": len(warehouse_stats)
        })
        
        return {"report": report}
    
    def generate_inventory_report(
        self,
        format: str = "summary"
    ) -> Dict[str, Any]:
        """
        Generate an inventory report.

        Args:
            format (str): Report format (summary, detailed, low_stock)

        Returns:
            Dict: Inventory report
        """
        # Total inventory data
        total_capacity = sum(wh["capacity"] for wh in self.warehouses.values())
        total_current = sum(wh["current_stock"] for wh in self.warehouses.values())
        
        # Summary by product
        product_summary = {}
        for wh_id, wh_info in self.warehouses.items():
            for prod_id, prod_info in wh_info["products"].items():
                if prod_id not in product_summary:
                    product_summary[prod_id] = {
                        "product_id": prod_id,
                        "product_name": prod_info["name"],
                        "total_quantity": 0,
                        "warehouses": []
                    }
                
                product_summary[prod_id]["total_quantity"] += prod_info["quantity"]
                product_summary[prod_id]["warehouses"].append({
                    "warehouse_id": wh_id,
                    "warehouse_name": wh_info["name"],
                    "quantity": prod_info["quantity"],
                    "threshold": prod_info["threshold"]
                })
        
        # Low stock products
        low_stock_products = []
        for prod_id, summary in product_summary.items():
            for wh_info in summary["warehouses"]:
                wh = self.warehouses[wh_info["warehouse_id"]]
                prod_data = wh["products"][prod_id]
                
                if prod_data["quantity"] <= prod_data["threshold"]:
                    low_stock_products.append({
                        "product_id": prod_id,
                        "product_name": prod_data["name"],
                        "warehouse_id": wh_info["warehouse_id"],
                        "warehouse_name": wh_info["warehouse_name"],
                        "current_quantity": prod_data["quantity"],
                        "threshold": prod_data["threshold"],
                        "shortage": prod_data["threshold"] - prod_data["quantity"]
                    })
        
        report = {
            "report_id": f"INV_REPORT_{self._current_time().replace(' ', '_').replace(':', '-')}",
            "generated_at": self._current_time(),
            "overall_summary": {
                "total_warehouses": len(self.warehouses),
                "total_capacity": total_capacity,
                "total_current_stock": total_current,
                "utilization_rate": round((total_current / total_capacity) * 100, 2) if total_capacity > 0 else 0,
                "unique_products": len(product_summary)
            },
            "product_summary": list(product_summary.values()),
            "low_stock_alerts": low_stock_products,
            "recent_audits": self.inventory_audits[-5:] if self.inventory_audits else []
        }
        
        return {"report": report}
    
    # ── Helper methods ──────────────────────────────────────────────────────
    
    def _simulate_shipment_progress(self, shipment: Dict[str, Any]) -> None:
        """
        Simulate logistics progress update.

        Args:
            shipment (Dict): Logistics record

        Returns:
            None
        """
        # If already delivered or cancelled, stop updating
        if shipment["status"] in ("delivered", "cancelled"):
            return

        # Determine next step based on current status
        status_order = ["ready_for_pickup", "in_transit", "out_for_delivery", "delivered"]

        try:
            current_idx = status_order.index(shipment["status"])
        except ValueError:
            current_idx = 0

        # 20% chance of delay
        if random.random() < 0.2 and shipment["status"] != "delayed":
            shipment["status"] = "delayed"
            shipment["estimated_delivery"] = self._future_time(1)  # Delay 1 day

            shipment["checkpoints"].append({
                "time": self._current_time(),
                "location": "En route",
                "status": "Shipment delayed"
            })
        elif random.random() < 0.3 and current_idx < len(status_order) - 1:
            # Update to next status
            shipment["status"] = status_order[current_idx + 1]

            # Add checkpoint
            checkpoint_status = {
                "ready_for_pickup": "Picked up",
                "in_transit": "In transit",
                "out_for_delivery": "Out for delivery",
                "delivered": "Delivered"
            }.get(shipment["status"], "Status update")

            # If delivered, set actual delivery time
            if shipment["status"] == "delivered":
                shipment["actual_delivery"] = self._current_time()
            
            shipment["checkpoints"].append({
                "time": self._current_time(),
                "location": self._get_simulated_location(shipment["from_warehouse"], shipment["to_address"]),
                "status": checkpoint_status
            })
    
    def _get_simulated_location(self, from_warehouse: str, to_address: str) -> str:
        """
        Generate a simulated location based on warehouse and destination.

        Args:
            from_warehouse (str): Origin warehouse ID
            to_address (str): Destination address

        Returns:
            str: Simulated location
        """
        # Simplified implementation
        locations = [
            "Sorting center",
            "Transfer hub",
            "Destination city distribution station",
            "Delivery station",
            "En route"
        ]
        return random.choice(locations)
    
    def _generate_tracking_number(self, carrier: str) -> str:
        """
        Generate a tracking number.

        Args:
            carrier (str): Logistics company

        Returns:
            str: Tracking number
        """
        prefix_map = {
            "SF Express": "SF",
            "JD Logistics": "JD",
            "ZTO Express": "ZT",
            "YTO Express": "YT",
            "Yunda Express": "YD",
            "EMS": "EMS"
        }
        
        prefix = prefix_map.get(carrier, "TR")
        number = ''.join(random.choices('0123456789', k=10))
        return f"{prefix}{number}"
    
    def _current_time(self) -> str:
        """Get current simulated time."""
        # Simplified implementation, using fixed date + random time
        base_date = "2024-05-22"
        hour = random.randint(8, 20)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        return f"{base_date} {hour:02d}:{minute:02d}:{second:02d}"
    
    def _future_time(self, days: int = 1) -> str:
        """Get future simulated time."""
        base_date = "2024-05-22"
        future_date = datetime.strptime(base_date, "%Y-%m-%d") + timedelta(days=days)
        hour = random.randint(9, 18)
        minute = random.randint(0, 59)
        return f"{future_date.strftime('%Y-%m-%d')} {hour:02d}:{minute:02d}:00"
    
    def _log(self, event: str, detail: Dict) -> None:
        """Record operation log."""
        self.processing_log.append({
            "event": event,
            "detail": detail,
            "timestamp": self._current_time()
        })