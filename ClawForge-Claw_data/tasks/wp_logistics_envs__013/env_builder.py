import os
import json
import random
from datetime import datetime, timedelta

def build_env():
    # Clean slate, ensure we start from scratch
    base_dirs = ["data", "data/inventory", "data/orders", "data/backup", "logs", "ops"]
    for d in base_dirs:
        os.makedirs(d, exist_ok=True)

    # --- Helper to write JSON ---
    def write_json(rel_path, obj):
        with open(rel_path, "w") as f:
            json.dump(obj, f, indent=2)

    # ---------- Returns ----------
    returns = {
        "returns": [
            {
                "return_id": "ret_001",
                "order_id": "ord_001",
                "customer_id": "cust_001",
                "reason": "defective",
                "requested_at": "2025-03-15T10:00:00Z",
                "status": "pending_review",
                "items": [{"sku": "SKU-1002", "qty": 1}],
                "refund_amount": 29.99,
                "return_tracking_number": "RET001",
                "inspection_notes": "",
                "resolution": ""
            },
            {
                "return_id": "ret_002",
                "order_id": "ord_005",
                "customer_id": "cust_002",
                "reason": "past_30_day_window",
                "requested_at": "2025-03-20T14:30:00Z",
                "status": "rejected",
                "items": [{"sku": "SKU-2001", "qty": 1}],
                "refund_amount": 0.0,
                "return_tracking_number": "RET002",
                "inspection_notes": "Return window expired",
                "resolution": "rejected - past 30-day return window"
            },
            {
                "return_id": "ret_003",
                "order_id": "ord_004",
                "customer_id": "cust_003",
                "reason": "wrong item",
                "requested_at": "2025-03-22T09:15:00Z",
                "status": "pending_inspection",
                "items": [{"sku": "SKU-3001", "qty": 1}],
                "refund_amount": 0.0,
                "return_tracking_number": "RET003",
                "inspection_notes": "",
                "resolution": ""
            },
            {
                "return_id": "ret_004",
                "order_id": "ord_002",
                "customer_id": "cust_004",
                "reason": "no_reason",
                "requested_at": "2025-03-25T16:45:00Z",
                "status": "pending_review",
                "items": [{"sku": "SKU-1002", "qty": 1}],
                "refund_amount": 0.0,
                "return_tracking_number": "RET004",
                "inspection_notes": "",
                "resolution": ""
            }
        ]
    }
    write_json("data/returns.json", returns)

    # ---------- Shipments ----------
    shipments = {
        "shipments": [
            {
                "shipment_id": "ship_005",
                "order_id": "ord_003",
                "carrier": "FedEx",
                "tracking_number": "FX654987321",
                "status": "processing",
                "shipped_at": "",
                "delivered_at": "",
                "current_location": "Warehouse - LA",
                "events": []
            },
            {
                "shipment_id": "ship_001",
                "order_id": "ord_001",
                "carrier": "UPS",
                "tracking_number": "UPS123456789",
                "status": "delivered",
                "shipped_at": "2025-03-10T08:00:00Z",
                "delivered_at": "2025-03-14T14:22:00Z",
                "current_location": "Delivered to recipient",
                "events": [{"timestamp": "2025-03-10T08:00:00Z", "location": "Warehouse - LA", "status": "shipped"}]
            },
            {
                "shipment_id": "ship_002",
                "order_id": "ord_005",
                "carrier": "FedEx",
                "tracking_number": "FX456789123",
                "status": "in_transit",
                "shipped_at": "2025-03-18T12:00:00Z",
                "delivered_at": "",
                "current_location": "Denver, CO",
                "events": []
            }
        ]
    }
    write_json("data/shipments.json", shipments)

    # ---------- Inventory ----------
    inventory_items = [
        # wh_001
        {"sku": "SKU-1002", "name": "Widget Alpha", "category": "parts", "unit_cost": 2.50, "list_price": 5.99,
         "stock_level": 20, "reserved": 5, "available": 15, "reorder_point": 10, "warehouse_id": "wh_001"},
        {"sku": "SKU-2001", "name": "Gadget Beta", "category": "electronics", "unit_cost": 15.00, "list_price": 34.99,
         "stock_level": 20, "reserved": 5, "available": 15, "reorder_point": 10, "warehouse_id": "wh_001"},
        {"sku": "SKU-3001", "name": "Accessory Gamma", "category": "accessories", "unit_cost": 1.20, "list_price": 3.49,
         "stock_level": 50, "reserved": 10, "available": 40, "reorder_point": 20, "warehouse_id": "wh_001"},
        # wh_002 (East)
        {"sku": "SKU-1002", "name": "Widget Alpha", "category": "parts", "unit_cost": 2.50, "list_price": 5.99,
         "stock_level": 10, "reserved": 2, "available": 8, "reorder_point": 5, "warehouse_id": "wh_002"},
        {"sku": "SKU-4001", "name": "Dongle Delta", "category": "accessories", "unit_cost": 0.80, "list_price": 1.99,
         "stock_level": 100, "reserved": 0, "available": 100, "reorder_point": 50, "warehouse_id": "wh_002"},
    ]
    inventory = {"inventory": inventory_items}
    write_json("data/inventory/inventory.json", inventory)

    # ---------- Physical Count (for reconciliation) ----------
    physical_count = {
        "physical_counts": [
            {"sku": "SKU-2001", "warehouse": "wh_001", "physical_qty": 15}
        ]
    }
    write_json("data/inventory/physical_count.json", physical_count)

    # ---------- Orders (decoration, not used in task) ----------
    orders = {
        "orders": [
            {"order_id": "ord_001", "customer_id": "cust_001", "status": "delivered", "created_at": "2025-03-10T08:00:00Z",
             "updated_at": "2025-03-14T14:22:00Z", "items": [{"sku": "SKU-1002", "qty": 1}],
             "total_amount": 5.99, "shipping_address": "123 Oak St, Newark, NJ 07102", "warehouse_id": "wh_001"},
            {"order_id": "ord_003", "customer_id": "cust_003", "status": "processing", "created_at": "2025-03-19T10:00:00Z",
             "updated_at": "2025-03-19T10:00:00Z", "items": [{"sku": "SKU-3001", "qty": 2}],
             "total_amount": 6.98, "shipping_address": "456 Pine Ave, Los Angeles, CA 90001", "warehouse_id": "wh_001"},
        ]
    }
    write_json("data/orders/orders.json", orders)

    # ---------- Warehouses (decoration) ----------
    warehouses = {
        "warehouses": [
            {"warehouse_id": "wh_001", "name": "West Distribution Center", "location": "Los Angeles, CA",
             "capacity": 50000, "current_utilization": 32000},
            {"warehouse_id": "wh_002", "name": "East Distribution Center", "location": "Newark, NJ",
             "capacity": 40000, "current_utilization": 15000},
        ]
    }
    write_json("data/warehouses.json", warehouses)

    # ---------- Distractor files ----------
    # Old backup with stale data
    write_json("data/backup/returns_backup_old.json", {"returns": []})
    write_json("data/backup/inventory_backup.json", {"inventory": []})
    # A log file
    with open("logs/system_audit.log", "w") as f:
        f.write("2025-03-26 00:00:00 INFO: audit initialized\n")
        f.write("2025-03-26 00:00:01 WARN: inventory snapshot taken\n")

    # A CSV file (irrelevant)
    with open("data/shipping_rates.csv", "w") as f:
        f.write("zone,rate_per_lb\n1,2.50\n2,3.75\n")

    # ops directory already created, leave empty for agent output

if __name__ == "__main__":
    build_env()
