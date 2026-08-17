import os
import json
import random
import string

def random_id(prefix="", length=6):
    return prefix + ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def build_env():
    # Create directory structure
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    os.makedirs("backups", exist_ok=True)

    # --- returns.json (with multiple records including target ones) ---
    returns = [
        {
            "return_id": "ret_001",
            "order_id": "ord_023",
            "customer_id": "cust_011",
            "reason": "defective",
            "requested_at": "2025-02-10T14:30:00Z",
            "status": "pending_review",
            "items": [{"sku": "SKU-1001", "qty": 1}],
            "refund_amount": 49.99,
            "return_tracking_number": "RET001",
            "inspection_notes": "",
            "resolution": ""
        },
        {
            "return_id": "ret_002",
            "order_id": "ord_045",
            "customer_id": "cust_022",
            "reason": "change_of_mind",
            "requested_at": "2025-02-11T09:15:00Z",
            "status": "received",
            "items": [{"sku": "SKU-2001", "qty": 1}],
            "refund_amount": 89.99,
            "return_tracking_number": "RET002",
            "inspection_notes": "Item looks unused",
            "resolution": "refund_approved"
        },
        {
            "return_id": "ret_003",
            "order_id": "ord_067",
            "customer_id": "cust_033",
            "reason": "wrong_item",
            "requested_at": "2025-02-12T11:00:00Z",
            "status": "pending_review",
            "items": [{"sku": "SKU-3002", "qty": 1}],
            "refund_amount": 125.00,
            "return_tracking_number": "RET003",
            "inspection_notes": "",
            "resolution": ""
        },
        {
            "return_id": "ret_004",
            "order_id": "ord_089",
            "customer_id": "cust_044",
            "reason": "defective",
            "requested_at": "2025-02-13T08:45:00Z",
            "status": "pending_inspection",
            "items": [{"sku": "SKU-4001", "qty": 1}],
            "refund_amount": 199.99,
            "return_tracking_number": "RET004",
            "inspection_notes": "Screen cracked",
            "resolution": ""
        }
    ]
    with open("data/returns.json", "w") as f:
        json.dump({"returns": returns}, f, indent=2)

    # --- shipments.json ---
    shipments = [
        {
            "shipment_id": "ship_001",
            "order_id": "ord_001",
            "carrier": "FedEx",
            "tracking_number": "FX123456789",
            "status": "delivered",
            "shipped_at": "2025-02-01T10:00:00Z",
            "delivered_at": "2025-02-03T14:00:00Z",
            "current_location": "Delivered to recipient",
            "events": []
        },
        {
            "shipment_id": "ship_002",
            "order_id": "ord_002",
            "carrier": "UPS",
            "tracking_number": "UPS987654321",
            "status": "in_transit",
            "shipped_at": "2025-02-10T08:00:00Z",
            "delivered_at": "",
            "current_location": "Denver, CO",
            "events": []
        },
        {
            "shipment_id": "ship_003",
            "order_id": "ord_003",
            "carrier": "FedEx",
            "tracking_number": "FX456123789",
            "status": "out_for_delivery",
            "shipped_at": "2025-02-12T09:00:00Z",
            "delivered_at": "",
            "current_location": "Indianapolis, IN",
            "events": []
        },
        {
            "shipment_id": "ship_004",
            "order_id": "ord_004",
            "carrier": "UPS",
            "tracking_number": "UPS123456789",
            "status": "processing",
            "shipped_at": "",
            "delivered_at": "",
            "current_location": "Warehouse - LA",
            "events": []
        },
        {
            "shipment_id": "ship_005",
            "order_id": "ord_005",
            "carrier": "UPS",
            "tracking_number": "UPS456123789",
            "status": "processing",
            "shipped_at": "",
            "delivered_at": "",
            "current_location": "Warehouse - LA",
            "events": []
        }
    ]
    with open("data/shipments.json", "w") as f:
        json.dump({"shipments": shipments}, f, indent=2)

    # --- inventory.json ---
    inventory = [
        {
            "sku": "SKU-1002",
            "name": "Widget Pro",
            "category": "parts",
            "unit_cost": 12.50,
            "list_price": 29.99,
            "stock_level": 20,
            "reserved": 5,
            "available": 15,
            "reorder_point": 10,
            "warehouse_id": "wh_001"
        },
        {
            "sku": "SKU-1001",
            "name": "Basic Widget",
            "category": "parts",
            "unit_cost": 5.00,
            "list_price": 14.99,
            "stock_level": 50,
            "reserved": 10,
            "available": 40,
            "reorder_point": 20,
            "warehouse_id": "wh_001"
        },
        {
            "sku": "SKU-2001",
            "name": "Premium Cover",
            "category": "accessories",
            "unit_cost": 8.00,
            "list_price": 24.99,
            "stock_level": 100,
            "reserved": 20,
            "available": 80,
            "reorder_point": 30,
            "warehouse_id": "wh_002"
        }
    ]
    with open("data/inventory.json", "w") as f:
        json.dump({"inventory": inventory}, f, indent=2)

    # --- Distractors: orders.json, contacts.json, warehouses.json ---
    orders = [
        {"order_id": "ord_005", "customer_id": "cust_011", "status": "processing", "created_at": "2025-02-14T10:00:00Z", "updated_at": "2025-02-14T10:00:00Z", "items": [{"sku": "SKU-1002", "qty": 1}], "total_amount": 29.99, "shipping_address": "123 Oak St, Newark, NJ 07102", "warehouse_id": "wh_001"},
    ]
    with open("data/orders.json", "w") as f:
        json.dump({"orders": orders}, f, indent=2)

    contacts = [
        {"contact_id": "c001", "name": "Alice Chen", "email": "alice.chen@email.com", "phone": "+1-555-0101", "type": "warehouse_manager"},
        {"contact_id": "c002", "name": "Bob Martinez", "email": "bob.martinez@email.com", "phone": "+1-555-0102", "type": "customer"},
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    warehouses = [
        {"warehouse_id": "wh_001", "name": "Central Fulfillment Hub", "location": "Chicago, IL", "capacity": 5000, "current_utilization": 3200},
        {"warehouse_id": "wh_002", "name": "West Distribution Center", "location": "Los Angeles, CA", "capacity": 4000, "current_utilization": 2800},
    ]
    with open("data/warehouses.json", "w") as f:
        json.dump({"warehouses": warehouses}, f, indent=2)

    # --- Stale/old backup files to confuse ---
    with open("backups/returns_20250201.json", "w") as f:
        json.dump({"returns": [{"return_id": "ret_001", "status": "rejected", "reason": "past_window"}]}, f, indent=2)

    with open("backups/action_plan_old.json", "w") as f:
        json.dump({"actions": [{"type": "ignore"}]}, f, indent=2)

    with open("reports/inventory_snapshot_old.csv", "w") as f:
        f.write("sku,stock_level\nSKU-1002,18\nSKU-1001,50\n")

    # --- Empty ops directory ready ---
    # Ensure it's empty
    for f in os.listdir("ops"):
        os.remove(os.path.join("ops", f))

if __name__ == "__main__":
    build_env()
