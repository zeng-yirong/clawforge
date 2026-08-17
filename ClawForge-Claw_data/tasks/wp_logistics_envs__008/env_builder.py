import os
import json

def build_env():
    # --- Returns ---
    os.makedirs("data/returns", exist_ok=True)
    returns = [
        {
            "return_id": "ret_001",
            "order_id": "ord_001",
            "customer_id": "cust_001",
            "reason": "defective",
            "requested_at": "2025-01-10T08:00:00Z",
            "status": "pending_review",
            "items": [{"sku": "SKU-1001", "qty": 1}],
            "refund_amount": 29.99,
            "return_tracking_number": "RET001",
            "inspection_notes": "",
            "resolution": ""
        },
        {
            "return_id": "ret_002",
            "order_id": "ord_002",
            "customer_id": "cust_002",
            "reason": "no longer needed",
            "requested_at": "2025-01-09T14:00:00Z",
            "status": "pending_review",
            "items": [{"sku": "SKU-1002", "qty": 2}],
            "refund_amount": 59.99,
            "return_tracking_number": "RET002",
            "inspection_notes": "",
            "resolution": ""
        },
        {
            "return_id": "ret_003",
            "order_id": "ord_003",
            "customer_id": "cust_003",
            "reason": "wrong item",
            "requested_at": "2025-01-11T09:00:00Z",
            "status": "pending_inspection",
            "items": [{"sku": "SKU-1003", "qty": 1}],
            "refund_amount": 49.99,
            "return_tracking_number": "RET003",
            "inspection_notes": "",
            "resolution": ""
        },
        {
            "return_id": "ret_004",
            "order_id": "ord_004",
            "customer_id": "cust_004",
            "reason": "arrived damaged",
            "requested_at": "2025-01-12T10:30:00Z",
            "status": "received",
            "items": [{"sku": "SKU-1004", "qty": 1}],
            "refund_amount": 19.99,
            "return_tracking_number": "RET004",
            "inspection_notes": "box crushed, item broken",
            "resolution": "refund_approved"
        }
    ]
    with open("data/returns/returns.json", "w") as f:
        json.dump(returns, f, indent=2)

    # --- Shipments ---
    os.makedirs("data/shipments", exist_ok=True)
    shipments = [
        {
            "shipment_id": "ship_001",
            "order_id": "ord_001",
            "carrier": "UPS",
            "tracking_number": "UPS123456789",
            "status": "delivered",
            "shipped_at": "2025-01-08T12:00:00Z",
            "delivered_at": "2025-01-10T15:00:00Z",
            "current_location": "Delivered to recipient",
            "events": []
        },
        {
            "shipment_id": "ship_002",
            "order_id": "ord_002",
            "carrier": "FedEx",
            "tracking_number": "FX654987321",
            "status": "in_transit",
            "shipped_at": "2025-01-09T08:00:00Z",
            "delivered_at": "",
            "current_location": "Denver, CO",
            "events": []
        },
        {
            "shipment_id": "ship_005",
            "order_id": "ord_005",
            "carrier": "",
            "tracking_number": "FX321654987",
            "status": "processing",
            "shipped_at": "",
            "delivered_at": "",
            "current_location": "Warehouse - LA",
            "events": []
        }
    ]
    with open("data/shipments/shipments.json", "w") as f:
        json.dump(shipments, f, indent=2)

    # --- Inventory ---
    os.makedirs("data/inventory", exist_ok=True)
    inventory = [
        {
            "sku": "SKU-1001",
            "name": "Widget A",
            "category": "parts",
            "unit_cost": 5.00,
            "list_price": 12.00,
            "stock_level": 200,
            "reserved": 20,
            "available": 180,
            "reorder_point": 50,
            "warehouse_id": "wh_001"
        },
        {
            "sku": "SKU-1002",
            "name": "Gadget B",
            "category": "electronics",
            "unit_cost": 15.00,
            "list_price": 35.00,
            "stock_level": 100,
            "reserved": 10,
            "available": 90,
            "reorder_point": 30,
            "warehouse_id": "wh_001"
        },
        {
            "sku": "SKU-1003",
            "name": "Doohickey C",
            "category": "accessories",
            "unit_cost": 3.00,
            "list_price": 8.00,
            "stock_level": 500,
            "reserved": 50,
            "available": 450,
            "reorder_point": 100,
            "warehouse_id": "wh_001"
        },
        {
            "sku": "SKU-1002",
            "name": "Gadget B",
            "category": "electronics",
            "unit_cost": 15.00,
            "list_price": 35.00,
            "stock_level": 50,
            "reserved": 5,
            "available": 45,
            "reorder_point": 20,
            "warehouse_id": "wh_002"
        }
    ]
    with open("data/inventory/inventory.json", "w") as f:
        json.dump(inventory, f, indent=2)

    # --- Distractor file ---
    os.makedirs("ops", exist_ok=True)
    # create an empty ops directory; agent will place report here

if __name__ == "__main__":
    build_env()
