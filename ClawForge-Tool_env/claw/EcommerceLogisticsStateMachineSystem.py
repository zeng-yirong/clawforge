from copy import deepcopy
from typing import Dict, List, Optional, Union, Any, Tuple
from datetime import datetime
import uuid
import random

DEFAULT_STATE = {
    "logistics_tasks": [],           # Logistics query task queue
    "return_tickets": {},            # Return ticket dict, key is ticket_id
    "inventory_records": [],         # Inventory reconciliation records
    "warehouses": {},                # Warehouse info, key is warehouse_id
    "processing_log": [],            # Processing log
    "task_counter": 1,               # Task ID counter
    "ticket_counter": 1,             # Ticket ID counter
    "record_counter": 1,             # Record ID counter
}

VALID_PRIORITIES = ("low", "medium", "high", "urgent")
VALID_TICKET_STATUS = ("pending", "processing", "approved", "rejected", "completed")
VALID_LOGISTICS_STATUS = ("pending", "in_transit", "delivered", "delayed", "lost")
VALID_RECONCILIATION_STATUS = ("pending", "matched", "mismatched", "resolved")


class EcomLogisticsEnv:
    """
    E-commerce logistics automation management environment: handles collaborative operations for logistics status querying, return/exchange tickets, and inventory reconciliation.

    This environment simulates an e-commerce backend operations system, managing three core processes:
    1. Automated logistics status query and tracking
    2. Return/exchange ticket creation, approval, and processing
    3. Warehouse inventory reconciliation and discrepancy handling
    Uses a state machine model to manage entity lifecycles and state transitions.
    """

    def __init__(self):
        self.logistics_tasks: List[Dict[str, Any]]
        self.return_tickets: Dict[str, Dict[str, Any]]
        self.inventory_records: List[Dict[str, Any]]
        self.warehouses: Dict[str, Dict[str, Any]]
        self.processing_log: List[Dict[str, Any]]
        self.task_counter: int
        self.ticket_counter: int
        self.record_counter: int
        self._api_description = (
            "This tool manages three core processes of e-commerce logistics operations: automated logistics query, "
            "return/exchange ticket processing, and inventory reconciliation, "
            "using state machines and guard conditions to automate workflows."
        )
        self._load_scenario({})

    def _load_scenario(self, scenario: dict, long_context=False) -> None:
        """Load initial state from scenario configuration; fall back to defaults for missing keys"""
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_STATE)
        self.logistics_tasks = scenario.get("logistics_tasks", DEFAULT_STATE_COPY["logistics_tasks"])
        self.return_tickets = scenario.get("return_tickets", DEFAULT_STATE_COPY["return_tickets"])
        self.inventory_records = scenario.get("inventory_records", DEFAULT_STATE_COPY["inventory_records"])
        self.warehouses = scenario.get("warehouses", DEFAULT_STATE_COPY["warehouses"])
        self.processing_log = scenario.get("processing_log", DEFAULT_STATE_COPY["processing_log"])
        self.task_counter = scenario.get("task_counter", DEFAULT_STATE_COPY["task_counter"])
        self.ticket_counter = scenario.get("ticket_counter", DEFAULT_STATE_COPY["ticket_counter"])
        self.record_counter = scenario.get("record_counter", DEFAULT_STATE_COPY["record_counter"])

    def get_env_state(self) -> dict:
        """
        Return a complete snapshot of the environment's internal state.

        Returns:
            dict: Dictionary containing all environment state variables, structured as:
                {
                    "logistics_tasks": [...],
                    "return_tickets": {...},
                    "inventory_records": [...],
                    "warehouses": {...},
                    "processing_log": [...],
                    "task_counter": int,
                    "ticket_counter": int,
                    "record_counter": int
                }
        """
        return {
            "logistics_tasks": self.logistics_tasks,
            "return_tickets": self.return_tickets,
            "inventory_records": self.inventory_records,
            "warehouses": self.warehouses,
            "processing_log": self.processing_log,
            "task_counter": self.task_counter,
            "ticket_counter": self.ticket_counter,
            "record_counter": self.record_counter,
        }

    # ── Warehouse management ─────────────────────────────────────────────────────────

    def register_warehouse(
        self,
        name: str,
        location: str,
        capacity: int,
        contact_info: Dict[str, str],
    ) -> Dict[str, Any]:
        """
        Register a new warehouse in the system.

        Args:
            name (str): Warehouse name
            location (str): Warehouse geographic location
            capacity (int): Maximum inventory capacity
            contact_info (Dict): Contact info, e.g. {"manager": "Name", "phone": "Phone"}

        Returns:
            Dict: Dictionary containing warehouse_id and warehouse info,
                  or {"error": "Error description"}
        """
        if not name.strip():
            return {"error": "Warehouse name cannot be empty"}
        if capacity <= 0:
            return {"error": "Warehouse capacity must be a positive number"}

        warehouse_id = f"WH{self.record_counter:06d}"
        self.record_counter += 1

        warehouse = {
            "warehouse_id": warehouse_id,
            "name": name,
            "location": location,
            "capacity": capacity,
            "current_inventory": 0,
            "contact_info": contact_info,
            "created_at": datetime.now().isoformat(),
            "is_active": True,
        }
        self.warehouses[warehouse_id] = warehouse
        self._log("warehouse_registered", {"warehouse_id": warehouse_id, "name": name})
        return {"warehouse_id": warehouse_id, "warehouse": warehouse}

    def update_inventory(
        self,
        warehouse_id: str,
        product_sku: str,
        quantity_change: int,
        reason: str,
    ) -> Dict[str, Any]:
        """
        Update warehouse inventory quantity (inbound/outbound).

        Args:
            warehouse_id (str): Warehouse ID
            product_sku (str): Product SKU
            quantity_change (int): Quantity change, positive means inbound, negative means outbound
            reason (str): Change reason, e.g. "purchase_in", "sale_out", "return_in"

        Returns:
            Dict: Dictionary containing updated inventory info, or error message
        """
        warehouse = self.warehouses.get(warehouse_id)
        if not warehouse:
            return {"error": f"Warehouse {warehouse_id} does not exist"}
        if not warehouse.get("is_active", True):
            return {"error": f"Warehouse {warehouse_id} is deactivated"}

        new_inventory = warehouse["current_inventory"] + quantity_change
        if new_inventory < 0:
            return {"error": f"Insufficient inventory, current: {warehouse['current_inventory']}, required outbound: {-quantity_change}"}
        if new_inventory > warehouse["capacity"]:
            return {"error": f"Inventory exceeds capacity, capacity: {warehouse['capacity']}, projected: {new_inventory}"}

        warehouse["current_inventory"] = new_inventory
        self._log("inventory_updated", {
            "warehouse_id": warehouse_id,
            "product_sku": product_sku,
            "change": quantity_change,
            "new_total": new_inventory,
            "reason": reason,
        })
        return {
            "warehouse_id": warehouse_id,
            "product_sku": product_sku,
            "old_inventory": warehouse["current_inventory"] - quantity_change,
            "new_inventory": new_inventory,
            "timestamp": datetime.now().isoformat(),
        }

    # ── Logistics query task management ────────────────────────────────────────────────

    def create_logistics_task(
        self,
        tracking_number: str,
        order_id: str,
        priority: str = "medium",
        expected_delivery: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a logistics status query task.

        Args:
            tracking_number (str): Logistics tracking number
            order_id (str): Associated order ID
            priority (str): Task priority, options: low/medium/high/urgent
            expected_delivery (str): Expected delivery date, ISO format

        Returns:
            Dict: Dictionary containing task_id and task info
        """
        if priority not in VALID_PRIORITIES:
            return {"error": f"Invalid priority, must be: {', '.join(VALID_PRIORITIES)}"}
        if not tracking_number.strip():
            return {"error": "Tracking number cannot be empty"}

        # Check if a task with the same tracking number already exists
        existing = [t for t in self.logistics_tasks if t.get("tracking_number") == tracking_number and t.get("current_status") != "delivered"]
        if existing:
            return {"error": f"Task for tracking number {tracking_number} already exists, task ID: {existing[0].get('task_id')}"}

        task_id = self.task_counter
        self.task_counter += 1

        task = {
            "task_id": task_id,
            "tracking_number": tracking_number,
            "order_id": order_id,
            "priority": priority,
            "status": "pending",
            "current_status": "pending",
            "expected_delivery": expected_delivery,
            "checkpoints": [],
            "created_at": datetime.now().isoformat(),
            "last_checked": None,
            "retry_count": 0,
            "max_retries": 3,
        }
        self.logistics_tasks.append(task)
        self._log("logistics_task_created", {"task_id": task_id, "tracking_number": tracking_number})
        return {"task_id": task_id, "task": task}

    def query_logistics_status(self, task_id: int) -> Dict[str, Any]:
        """
        Execute logistics status query and update task status.
        Simulates querying a logistics API and updates status based on predefined rules.

        Args:
            task_id (int): Logistics query task ID

        Returns:
            Dict: Dictionary containing query results, including status and checkpoint info
        """
        task = self._find_logistics_task(task_id)
        if not task:
            return {"error": f"Logistics query task {task_id} does not exist"}
        if task["status"] == "delivered":
            return {"error": f"Task {task_id} is already completed (delivered)"}

        # Simulate logistics query result
        status_options = ["pending", "in_transit", "in_transit", "delivered", "delayed"]
        new_status = random.choice(status_options)

        # If currently delayed, 70% chance to stay delayed
        if task["current_status"] == "delayed" and random.random() < 0.7:
            new_status = "delayed"

        task["current_status"] = new_status
        task["last_checked"] = datetime.now().isoformat()
        task["retry_count"] += 1

        # Add checkpoint
        checkpoint = {
            "timestamp": datetime.now().isoformat(),
            "location": self._generate_location(),
            "status": new_status,
            "description": self._generate_status_description(new_status),
        }
        task["checkpoints"].append(checkpoint)

        # Update task status
        if new_status == "delivered":
            task["status"] = "delivered"
        elif task["retry_count"] >= task["max_retries"]:
            task["status"] = "lost"

        self._log("logistics_queried", {"task_id": task_id, "status": new_status})
        return {
            "task_id": task_id,
            "tracking_number": task["tracking_number"],
            "current_status": new_status,
            "checkpoint": checkpoint,
            "retry_count": task["retry_count"],
            "is_completed": new_status == "delivered",
        }

    def _generate_location(self) -> str:
        """Generate random location"""
        locations = [
            "Beijing Sorting Center", "Shanghai Transfer Station", "Guangzhou Logistics Park", "Shenzhen Distribution Center",
            "Hangzhou Warehouse", "Chengdu Hub", "Wuhan Transit Station", "Xi'an Distribution Center"
        ]
        return random.choice(locations)

    def _generate_status_description(self, status: str) -> str:
        """Generate status description"""
        descriptions = {
            "pending": "Package order placed, awaiting pickup",
            "in_transit": "Package in transit",
            "delivered": "Package delivered",
            "delayed": "Package shipment delayed",
            "lost": "Package may be lost",
        }
        return descriptions.get(status, "Status update")

    # ── Return/exchange ticket management ────────────────────────────────────────────────

    def create_return_ticket(
        self,
        order_id: str,
        product_sku: str,
        quantity: int,
        reason: str,
        customer_id: str,
        requested_action: str = "refund",  # refund/exchange
    ) -> Dict[str, Any]:
        """
        Create a return/exchange ticket.

        Args:
            order_id (str): Order ID
            product_sku (str): Product SKU
            quantity (int): Return quantity
            reason (str): Return reason
            customer_id (str): Customer ID
            requested_action (str): Customer requested action: refund/exchange

        Returns:
            Dict: Dictionary containing ticket_id and ticket info
        """
        if quantity <= 0:
            return {"error": "Return quantity must be a positive number"}
        if requested_action not in ["refund", "exchange"]:
            return {"error": "Requested action must be 'refund' or 'exchange'"}

        ticket_id = self.ticket_counter
        self.ticket_counter += 1

        ticket = {
            "ticket_id": ticket_id,
            "order_id": order_id,
            "product_sku": product_sku,
            "quantity": quantity,
            "reason": reason,
            "customer_id": customer_id,
            "requested_action": requested_action,
            "status": "pending",
            "assigned_to": None,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "approval_required": quantity > 5 or "damaged" in reason.lower(),
            "history": [{
                "state": "pending",
                "timestamp": datetime.now().isoformat(),
                "action": "ticket_created",
            }],
            "resolution": None,
        }
        self.return_tickets[str(ticket_id)] = ticket
        self._log("return_ticket_created", {"ticket_id": ticket_id, "order_id": order_id})
        return {"ticket_id": ticket_id, "ticket": ticket}

    def process_return_ticket(
        self,
        ticket_id: int,
        action: str,
        approver_id: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Process a return/exchange ticket, supporting state transitions.
        State machine: pending -> processing -> (approved/rejected) -> completed

        Args:
            ticket_id (int): Ticket ID
            action (str): Action to perform: assign/approve/reject/complete
            approver_id (str): Approver ID (required only for approve/reject)
            notes (str): Processing notes

        Returns:
            Dict: Dictionary containing processing result, formatted as:
                {
                    "ticket_id": int,
                    "from_state": str,
                    "to_state": str,
                    "result": "transitioned"/"blocked_by_guard"/"no_transition",
                    [other relevant information]
                }
        """
        ticket_key = str(ticket_id)
        ticket = self.return_tickets.get(ticket_key)
        if not ticket:
            return {"error": f"Return ticket {ticket_id} does not exist"}

        current_state = ticket["status"]

        # Define state transition rules and guard conditions
        transitions = {
            "pending": {
                "target": "processing",
                "guard": {},  # No extra conditions
            },
            "processing": {
                "target": {
                    "approve": "approved",
                    "reject": "rejected",
                },
                "guard": {
                    "approve": lambda t: t.get("approval_required", False) and approver_id is not None,
                    "reject": lambda t: approver_id is not None,
                }
            },
            "approved": {
                "target": "completed",
                "guard": lambda t: t.get("resolution") is not None,
            },
            "rejected": {
                "target": "completed",
                "guard": {},  # Can be completed directly
            }
        }

        # Handle different actions
        if action == "assign":
            if current_state != "pending":
                return {"error": f"Can only assign tickets in pending status, current status: {current_state}"}
            ticket["status"] = "processing"
            ticket["assigned_to"] = approver_id
            result_state = "processing"

        elif action in ["approve", "reject"]:
            if current_state != "processing":
                return {"error": f"Can only approve/reject tickets in processing status, current status: {current_state}"}

            guard_func = transitions["processing"]["guard"].get(action)
            if guard_func and not guard_func(ticket):
                if action == "approve":
                    return {
                        "ticket_id": ticket_id,
                        "from_state": current_state,
                        "to_state": "approved",
                        "result": "blocked_by_guard",
                        "message": "Approver ID required or this ticket does not need approval"
                    }
                else:
                    return {
                        "ticket_id": ticket_id,
                        "from_state": current_state,
                        "to_state": "rejected",
                        "result": "blocked_by_guard",
                        "message": "Approver ID required"
                    }
            
            result_state = transitions["processing"]["target"][action]
            ticket["status"] = result_state
            
        elif action == "complete":
            if current_state not in ["approved", "rejected"]:
                return {"error": f"Can only complete approved or rejected tickets, current status: {current_state}"}

            guard_func = transitions.get(current_state, {}).get("guard")
            if guard_func and not guard_func(ticket):
                return {
                    "ticket_id": ticket_id,
                    "from_state": current_state,
                    "to_state": "completed",
                    "result": "blocked_by_guard",
                    "message": "Completion conditions not met"
                }
            
            result_state = "completed"
            ticket["status"] = result_state
            
        else:
            return {"error": f"Invalid action: {action}, supported: assign/approve/reject/complete"}

        # Update ticket info
        ticket["updated_at"] = datetime.now().isoformat()
        ticket["history"].append({
            "state": result_state,
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "notes": notes,
            "approver": approver_id,
        })

        if notes:
            ticket["resolution"] = notes

        self._log("return_ticket_processed", {
            "ticket_id": ticket_id,
            "action": action,
            "from_state": current_state,
            "to_state": result_state,
        })

        return {
            "ticket_id": ticket_id,
            "from_state": current_state,
            "to_state": result_state,
            "result": "transitioned",
            "updated_at": ticket["updated_at"],
        }

    def set_return_resolution(
        self,
        ticket_id: int,
        resolution_type: str,
        amount: Optional[float] = None,
        exchange_sku: Optional[str] = None,
        warehouse_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Set ticket resolution.

        Args:
            ticket_id (int): Ticket ID
            resolution_type (str): Resolution type: refund/exchange/credit
            amount (float): Refund amount (required only for refund)
            exchange_sku (str): Exchange product SKU (required only for exchange)
            warehouse_id (str): Processing warehouse ID

        Returns:
            Dict: Dictionary containing resolution information
        """
        ticket_key = str(ticket_id)
        ticket = self.return_tickets.get(ticket_key)
        if not ticket:
            return {"error": f"Return ticket {ticket_id} does not exist"}
        if ticket["status"] not in ["approved", "processing"]:
            return {"error": f"Ticket status {ticket['status']} does not allow setting a resolution"}

        resolution = {
            "type": resolution_type,
            "set_at": datetime.now().isoformat(),
        }

        if resolution_type == "refund":
            if amount is None or amount <= 0:
                return {"error": "Refund amount must be a positive number"}
            resolution["amount"] = amount
            resolution["currency"] = "CNY"

        elif resolution_type == "exchange":
            if not exchange_sku:
                return {"error": "Exchange requires specifying a new product SKU"}
            resolution["exchange_sku"] = exchange_sku
            resolution["warehouse_id"] = warehouse_id

        elif resolution_type == "credit":
            if amount is None or amount <= 0:
                return {"error": "Credit amount must be a positive number"}
            resolution["credit_amount"] = amount
            resolution["expiry_days"] = 30

        else:
            return {"error": f"Invalid resolution type: {resolution_type}"}

        ticket["resolution"] = resolution
        ticket["updated_at"] = datetime.now().isoformat()
        
        self._log("return_resolution_set", {"ticket_id": ticket_id, "resolution_type": resolution_type})
        return {
            "ticket_id": ticket_id,
            "resolution": resolution,
            "status": ticket["status"],
        }

    # ── Inventory reconciliation management ────────────────────────────────────────────────

    def create_inventory_reconciliation(
        self,
        warehouse_id: str,
        product_sku: str,
        system_quantity: int,
        physical_quantity: int,
        counted_by: str,
    ) -> Dict[str, Any]:
        """
        Create an inventory reconciliation record.

        Args:
            warehouse_id (str): Warehouse ID
            product_sku (str): Product SKU
            system_quantity (int): System recorded quantity
            physical_quantity (int): Actual physical count quantity
            counted_by (str): Counter ID

        Returns:
            Dict: Dictionary containing record_id and reconciliation info
        """
        warehouse = self.warehouses.get(warehouse_id)
        if not warehouse:
            return {"error": f"Warehouse {warehouse_id} does not exist"}

        record_id = self.record_counter
        self.record_counter += 1

        discrepancy = physical_quantity - system_quantity
        status = "matched" if discrepancy == 0 else "mismatched"

        reconciliation = {
            "record_id": record_id,
            "warehouse_id": warehouse_id,
            "product_sku": product_sku,
            "system_quantity": system_quantity,
            "physical_quantity": physical_quantity,
            "discrepancy": discrepancy,
            "status": status,
            "counted_by": counted_by,
            "counted_at": datetime.now().isoformat(),
            "resolved_at": None,
            "resolution_notes": None,
            "auto_adjust": abs(discrepancy) <= 5,  # Auto-adjust small discrepancies
        }
        self.inventory_records.append(reconciliation)

        # If discrepancy is small and auto-adjust is allowed, process directly
        if reconciliation["auto_adjust"] and status == "mismatched":
            self._process_auto_adjustment(record_id, reconciliation)

        self._log("reconciliation_created", {
            "record_id": record_id,
            "warehouse_id": warehouse_id,
            "discrepancy": discrepancy,
            "status": status,
        })
        return {"record_id": record_id, "reconciliation": reconciliation}

    def _process_auto_adjustment(self, record_id: int, reconciliation: Dict[str, Any]) -> None:
        """Process automatic inventory adjustment"""
        reconciliation["status"] = "resolved"
        reconciliation["resolved_at"] = datetime.now().isoformat()
        reconciliation["resolution_notes"] = "Auto-adjustment: small discrepancy automatically leveled"

        # Update warehouse inventory
        warehouse = self.warehouses.get(reconciliation["warehouse_id"])
        if warehouse:
            warehouse["current_inventory"] = reconciliation["physical_quantity"]
            
        self._log("inventory_auto_adjusted", {
            "record_id": record_id,
            "warehouse_id": reconciliation["warehouse_id"],
            "adjustment": reconciliation["discrepancy"],
        })

    def resolve_reconciliation(
        self,
        record_id: int,
        resolution: str,
        notes: str,
        resolved_by: str,
        adjust_inventory: bool = True,
    ) -> Dict[str, Any]:
        """
        Resolve inventory discrepancy.

        Args:
            record_id (int): Reconciliation record ID
            resolution (str): Resolution: adjusted/written_off/found
            notes (str): Processing notes
            resolved_by (str): Resolver ID
            adjust_inventory (bool): Whether to adjust system inventory

        Returns:
            Dict: Dictionary containing resolution result
        """
        record = self._find_reconciliation_record(record_id)
        if not record:
            return {"error": f"Reconciliation record {record_id} does not exist"}
        if record["status"] == "resolved":
            return {"error": f"Reconciliation record {record_id} is already resolved"}

        valid_resolutions = ["adjusted", "written_off", "found"]
        if resolution not in valid_resolutions:
            return {"error": f"Invalid resolution, must be: {', '.join(valid_resolutions)}"}

        record["status"] = "resolved"
        record["resolved_at"] = datetime.now().isoformat()
        record["resolution"] = resolution
        record["resolution_notes"] = notes
        record["resolved_by"] = resolved_by

        # If choose to adjust inventory
        if adjust_inventory and resolution == "adjusted":
            warehouse = self.warehouses.get(record["warehouse_id"])
            if warehouse:
                warehouse["current_inventory"] = record["physical_quantity"]

        self._log("reconciliation_resolved", {
            "record_id": record_id,
            "resolution": resolution,
            "discrepancy": record["discrepancy"],
        })
        return {
            "record_id": record_id,
            "status": "resolved",
            "resolution": resolution,
            "inventory_adjusted": adjust_inventory,
            "timestamp": record["resolved_at"],
        }

    # ── Query and report methods ──────────────────────────────────────────────

    def get_logistics_task(self, task_id: int) -> Dict[str, Any]:
        """
        Get logistics query task details.

        Args:
            task_id (int): Task ID

        Returns:
            Dict: Dictionary containing task details
        """
        task = self._find_logistics_task(task_id)
        if not task:
            return {"error": f"Logistics query task {task_id} does not exist"}
        return {"task": task}

    def get_return_ticket(self, ticket_id: int) -> Dict[str, Any]:
        """
        Get return/exchange ticket details.

        Args:
            ticket_id (int): Ticket ID

        Returns:
            Dict: Dictionary containing ticket details
        """
        ticket = self.return_tickets.get(str(ticket_id))
        if not ticket:
            return {"error": f"Return/exchange ticket {ticket_id} does not exist"}
        return {"ticket": ticket}

    def get_reconciliation_record(self, record_id: int) -> Dict[str, Any]:
        """
        Get inventory reconciliation record details.

        Args:
            record_id (int): Record ID

        Returns:
            Dict: Dictionary containing reconciliation record details
        """
        record = self._find_reconciliation_record(record_id)
        if not record:
            return {"error": f"Inventory reconciliation record {record_id} does not exist"}
        return {"reconciliation": record}

    def list_logistics_tasks(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        List logistics query tasks, with status and priority filtering.

        Args:
            status (str): Filter by status: pending/in_transit/delivered/delayed/lost
            priority (str): Filter by priority: low/medium/high/urgent

        Returns:
            Dict: Dictionary containing task list
        """
        tasks = self.logistics_tasks[:]
        if status:
            tasks = [t for t in tasks if t.get("current_status") == status]
        if priority:
            tasks = [t for t in tasks if t.get("priority") == priority]
        
        summaries = [{
            "task_id": t["task_id"],
            "tracking_number": t["tracking_number"],
            "status": t["current_status"],
            "priority": t["priority"],
            "last_checked": t["last_checked"],
        } for t in tasks]
        return {"tasks": summaries, "count": len(summaries)}

    def list_return_tickets(
        self,
        status: Optional[str] = None,
        requested_action: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        List return/exchange tickets, with status and requested action filtering.

        Args:
            status (str): Filter by status: pending/processing/approved/rejected/completed
            requested_action (str): Filter by requested action: refund/exchange

        Returns:
            Dict: Dictionary containing ticket list
        """
        tickets = list(self.return_tickets.values())
        if status:
            tickets = [t for t in tickets if t.get("status") == status]
        if requested_action:
            tickets = [t for t in tickets if t.get("requested_action") == requested_action]
        
        summaries = [{
            "ticket_id": t["ticket_id"],
            "order_id": t["order_id"],
            "status": t["status"],
            "requested_action": t["requested_action"],
            "created_at": t["created_at"],
            "assigned_to": t["assigned_to"],
        } for t in tickets]
        return {"tickets": summaries, "count": len(summaries)}

    def list_reconciliation_records(
        self,
        status: Optional[str] = None,
        warehouse_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        List inventory reconciliation records, with status and warehouse filtering.

        Args:
            status (str): Filter by status: pending/matched/mismatched/resolved
            warehouse_id (str): Filter by warehouse ID

        Returns:
            Dict: Dictionary containing reconciliation record list
        """
        records = self.inventory_records[:]
        if status:
            records = [r for r in records if r.get("status") == status]
        if warehouse_id:
            records = [r for r in records if r.get("warehouse_id") == warehouse_id]
        
        summaries = [{
            "record_id": r["record_id"],
            "warehouse_id": r["warehouse_id"],
            "product_sku": r["product_sku"],
            "discrepancy": r["discrepancy"],
            "status": r["status"],
            "counted_at": r["counted_at"],
        } for r in records]
        return {"records": summaries, "count": len(summaries)}

    def generate_operations_report(self) -> Dict[str, Any]:
        """
        Generate an operations report.

        Returns:
            Dict: Operations report containing various statistics
        """
        # Logistics statistics
        logistics_stats = {
            "total_tasks": len(self.logistics_tasks),
            "by_status": {},
            "delivered_on_time": 0,
            "delayed": 0,
        }
        for task in self.logistics_tasks:
            status = task.get("current_status", "unknown")
            logistics_stats["by_status"][status] = logistics_stats["by_status"].get(status, 0) + 1

            if status == "delivered" and task.get("expected_delivery"):
                # Simple check for on-time delivery
                logistics_stats["delivered_on_time"] += 1
            elif status == "delayed":
                logistics_stats["delayed"] += 1

        # Return/exchange statistics
        return_stats = {
            "total_tickets": len(self.return_tickets),
            "by_status": {},
            "by_action": {},
            "avg_processing_time": 0,
        }
        for ticket in self.return_tickets.values():
            status = ticket.get("status", "unknown")
            action = ticket.get("requested_action", "unknown")
            return_stats["by_status"][status] = return_stats["by_status"].get(status, 0) + 1
            return_stats["by_action"][action] = return_stats["by_action"].get(action, 0) + 1

        # Inventory reconciliation statistics
        inventory_stats = {
            "total_records": len(self.inventory_records),
            "by_status": {},
            "total_discrepancy": 0,
            "auto_adjusted": 0,
        }
        for record in self.inventory_records:
            status = record.get("status", "unknown")
            inventory_stats["by_status"][status] = inventory_stats["by_status"].get(status, 0) + 1
            inventory_stats["total_discrepancy"] += abs(record.get("discrepancy", 0))
            if record.get("auto_adjust", False):
                inventory_stats["auto_adjusted"] += 1

        return {
            "report_timestamp": datetime.now().isoformat(),
            "logistics": logistics_stats,
            "returns": return_stats,
            "inventory": inventory_stats,
            "warehouses": {
                "total": len(self.warehouses),
                "active": sum(1 for w in self.warehouses.values() if w.get("is_active", True)),
                "total_capacity": sum(w.get("capacity", 0) for w in self.warehouses.values()),
                "total_inventory": sum(w.get("current_inventory", 0) for w in self.warehouses.values()),
            }
        }

    # ── Helper methods ─────────────────────────────────────────────────────

    def _find_logistics_task(self, task_id: int) -> Optional[Dict[str, Any]]:
        """Find logistics query task"""
        for task in self.logistics_tasks:
            if task.get("task_id") == task_id:
                return task
        return None

    def _find_reconciliation_record(self, record_id: int) -> Optional[Dict[str, Any]]:
        """Find inventory reconciliation record"""
        for record in self.inventory_records:
            if record.get("record_id") == record_id:
                return record
        return None

    def _log(self, event: str, detail: Dict[str, Any]) -> None:
        """Record operation log"""
        log_entry = {
            "event": event,
            "detail": detail,
            "timestamp": datetime.now().isoformat(),
        }
        self.processing_log.append(log_entry)