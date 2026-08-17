import os
import json
import random

def build_env():
    # 确保 data/ 目录存在
    os.makedirs("data", exist_ok=True)

    # ----- returns.json -----
    returns = [
        {
            "return_id": "ret_001",
            "order_id": "ord_101",
            "customer_id": "cust_01",
            "reason": "defective",
            "requested_at": "2025-02-10T08:00:00Z",
            "status": "pending_review",
            "items": [{"sku": "SKU-1001", "qty": 1, "name": "Widget A"}],
            "refund_amount": 49.99,
            "return_tracking_number": "RET001",
            "inspection_notes": "",
            "resolution": ""
        },
        {
            "return_id": "ret_002",
            "order_id": "ord_102",
            "customer_id": "cust_02",
            "reason": "changed_mind",
            "requested_at": "2025-02-09T12:00:00Z",
            "status": "rejected",
            "items": [{"sku": "SKU-1002", "qty": 1, "name": "Widget B"}],
            "refund_amount": 35.00,
            "return_tracking_number": "RET002",
            "inspection_notes": "Past 30-day window",
            "resolution": "rejected - past 30-day return window"
        },
        {
            "return_id": "ret_003",
            "order_id": "ord_103",
            "customer_id": "cust_03",
            "reason": "wrong item",
            "requested_at": "2025-02-10T09:00:00Z",
            "status": "pending_inspection",
            "items": [{"sku": "SKU-1003", "qty": 1, "name": "Widget C"}],
            "refund_amount": 0.0,
            "return_tracking_number": "RET003",
            "inspection_notes": "",
            "resolution": ""
        },
        {
            "return_id": "ret_004",
            "order_id": "ord_104",
            "customer_id": "cust_04",
            "reason": "defective",
            "requested_at": "2025-02-08T10:00:00Z",
            "status": "approved",
            "items": [{"sku": "SKU-1001", "qty": 2, "name": "Widget A"}],
            "refund_amount": 99.98,
            "return_tracking_number": "RET004",
            "inspection_notes": "Approved - item defective",
            "resolution": "refund_approved"
        }
    ]
    with open("data/returns.json", "w") as f:
        json.dump({"returns": returns}, f, indent=2)

    # ----- shipments.json -----
    shipments = [
        {
            "shipment_id": "ship_004",
            "order_id": "ord_104",
            "carrier": "UPS",
            "tracking_number": "UPS987654321",
            "status": "delivered",
            "shipped_at": "2025-02-07T16:00:00Z",
            "delivered_at": "2025-02-09T11:00:00Z",
            "current_location": "Delivered to recipient",
            "events": []
        },
        {
            "shipment_id": "ship_005",
            "order_id": "ord_105",
            "carrier": "FedEx",
            "tracking_number": "FX654987321",
            "status": "processing",
            "shipped_at": "",
            "delivered_at": "",
            "current_location": "Warehouse - LA",
            "events": []
        },
        {
            "shipment_id": "ship_006",
            "order_id": "ord_106",
            "carrier": "FedEx",
            "tracking_number": "FX456789123",
            "status": "in_transit",
            "shipped_at": "2025-02-10T14:00:00Z",
            "delivered_at": "",
            "current_location": "Ontario, CA",
            "events": []
        }
    ]
    with open("data/shipments.json", "w") as f:
        json.dump({"shipments": shipments}, f, indent=2)

    # ----- inventory.json -----
    inventory = [
        {
            "sku": "SKU-1001",
            "name": "Widget A",
            "category": "electronics",
            "unit_cost": 10.00,
            "list_price": 20.00,
            "stock_level": 50,
            "reserved": 5,
            "available": 45,
            "reorder_point": 10,
            "warehouse_id": "wh_001"
        },
        {
            "sku": "SKU-1002",
            "name": "Widget B",
            "category": "parts",
            "unit_cost": 12.50,
            "list_price": 25.00,
            "stock_level": 20,
            "reserved": 5,
            "available": 15,
            "reorder_point": 10,
            "warehouse_id": "wh_001"
        },
        {
            "sku": "SKU-1003",
            "name": "Widget C",
            "category": "accessories",
            "unit_cost": 5.00,
            "list_price": 15.00,
            "stock_level": 30,
            "reserved": 2,
            "available": 28,
            "reorder_point": 10,
            "warehouse_id": "wh_001"
        },
        {
            "sku": "SKU-1001",
            "name": "Widget A",
            "category": "electronics",
            "unit_cost": 10.00,
            "list_price": 20.00,
            "stock_level": 100,
            "reserved": 10,
            "available": 90,
            "reorder_point": 15,
            "warehouse_id": "wh_002"
        }
    ]
    with open("data/inventory.json", "w") as f:
        json.dump({"inventory": inventory}, f, indent=2)

    # ----- warehouses.json (干扰项) -----
    warehouses = [
        {"warehouse_id": "wh_001", "name": "East Distribution Center", "location": "Newark, NJ", "capacity": 5000, "current_utilization": 3200},
        {"warehouse_id": "wh_002", "name": "West Distribution Center", "location": "Los Angeles, CA", "capacity": 4000, "current_utilization": 2800}
    ]
    with open("data/warehouses.json", "w") as f:
        json.dump({"warehouses": warehouses}, f, indent=2)

    # 创建 ops/ 目录（让 agent 写入）
    os.makedirs("ops", exist_ok=True)

if __name__ == "__main__":
    build_env()
