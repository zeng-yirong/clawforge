import os
import json

def build_env():
    # 创建目录结构
    os.makedirs("data/inventory", exist_ok=True)
    os.makedirs("ops", exist_ok=True)          # 提前创建空目录，agent 可以覆盖
    os.makedirs("reports", exist_ok=True)

    # ====== data/returns.json ======
    returns = [
        {
            "return_id": "ret_001",
            "order_id": "ord_1001",
            "customer_id": "cust_001",
            "reason": "defective",
            "requested_at": "2025-03-10T08:30:00",
            "status": "pending_review",
            "items": [{"sku": "SKU-1001", "qty": 1}],
            "refund_amount": 29.99,
            "return_tracking_number": "RET001",
            "inspection_notes": "",
            "resolution": ""
        },
        {
            "return_id": "ret_002",
            "order_id": "ord_1002",
            "customer_id": "cust_002",
            "reason": "changed mind",
            "requested_at": "2025-03-11T10:15:00",
            "status": "approved",
            "items": [{"sku": "SKU-1002", "qty": 2}],
            "refund_amount": 59.98,
            "return_tracking_number": "RET002",
            "inspection_notes": "All good, refund issued",
            "resolution": "refund_approved"
        },
        {
            "return_id": "ret_003",
            "order_id": "ord_1003",
            "customer_id": "cust_003",
            "reason": "wrong item",
            "requested_at": "2025-03-12T09:00:00",
            "status": "pending_inspection",
            "items": [{"sku": "SKU-2001", "qty": 1}],
            "refund_amount": 49.99,
            "return_tracking_number": "RET003",
            "inspection_notes": "",
            "resolution": ""
        },
        {
            "return_id": "ret_004",
            "order_id": "ord_1004",
            "customer_id": "cust_004",
            "reason": "no longer needed",
            "requested_at": "2025-03-08T14:00:00",
            "status": "rejected",
            "items": [{"sku": "SKU-1003", "qty": 1}],
            "refund_amount": 39.99,
            "return_tracking_number": "RET004",
            "inspection_notes": "Past 30-day window",
            "resolution": "rejected - past 30-day return window"
        },
        {
            "return_id": "ret_005",
            "order_id": "ord_1005",
            "customer_id": "cust_005",
            "reason": "damaged",
            "requested_at": "2025-03-13T11:30:00",
            "status": "received",
            "items": [{"sku": "SKU-1004", "qty": 1}],
            "refund_amount": 24.99,
            "return_tracking_number": "RET005",
            "inspection_notes": "Box crushed",
            "resolution": ""
        }
    ]
    with open("data/returns.json", "w") as f:
        json.dump({"returns": returns}, f, indent=2)

    # ====== data/shipments.json ======
    shipments = [
        {
            "shipment_id": "ship_001",
            "order_id": "ord_1001",
            "carrier": "UPS",
            "tracking_number": "UPS123456789",
            "status": "delivered",
            "shipped_at": "2025-03-09T16:00:00",
            "delivered_at": "2025-03-11T10:30:00",
            "current_location": "Delivered to recipient",
            "events": [{"timestamp": "2025-03-09T16:00:00", "location": "Warehouse - LA", "status": "shipped"}]
        },
        {
            "shipment_id": "ship_002",
            "order_id": "ord_1002",
            "carrier": "FedEx",
            "tracking_number": "FX321654987",
            "status": "out_for_delivery",
            "shipped_at": "2025-03-12T08:00:00",
            "delivered_at": "",
            "current_location": "Newark, NJ",
            "events": []
        },
        {
            "shipment_id": "ship_003",
            "order_id": "ord_1003",
            "carrier": "FedEx",
            "tracking_number": "FX654987321",
            "status": "processing",
            "shipped_at": "",
            "delivered_at": "",
            "current_location": "Warehouse - LA",
            "events": []
        },
        {
            "shipment_id": "ship_004",
            "order_id": "ord_1004",
            "carrier": "UPS",
            "tracking_number": "UPS456123789",
            "status": "in_transit",
            "shipped_at": "2025-03-11T09:00:00",
            "delivered_at": "",
            "current_location": "Denver, CO",
            "events": []
        },
        {
            "shipment_id": "ship_005",
            "order_id": "ord_1005",
            "carrier": "FedEx",
            "tracking_number": "FX654987321",
            "status": "in_transit",
            "shipped_at": "2025-03-13T12:00:00",
            "delivered_at": "",
            "current_location": "Ontario, CA",
            "events": [{"timestamp": "2025-03-13T12:00:00", "location": "Ontario, CA", "status": "in_transit"}]
        },
        {
            "shipment_id": "ship_006",
            "order_id": "ord_1006",
            "carrier": "UPS",
            "tracking_number": "UPS987654321",
            "status": "delivered",
            "shipped_at": "2025-03-10T14:00:00",
            "delivered_at": "2025-03-12T09:00:00",
            "current_location": "Delivered to recipient",
            "events": []
        }
    ]
    with open("data/shipments.json", "w") as f:
        json.dump({"shipments": shipments}, f, indent=2)

    # ====== data/inventory/inventory.json ======
    inventory_items = [
        {"sku": "SKU-1001", "name": "Widget A", "category": "parts", "unit_cost": 5.0, "list_price": 12.0,
         "stock_level": 20, "reserved": 5, "available": 15, "reorder_point": 10, "warehouse_id": "wh_001"},
        {"sku": "SKU-1002", "name": "Widget B", "category": "parts", "unit_cost": 8.0, "list_price": 18.0,
         "stock_level": 50, "reserved": 10, "available": 40, "reorder_point": 15, "warehouse_id": "wh_001"},
        {"sku": "SKU-1003", "name": "Gadget X", "category": "electronics", "unit_cost": 20.0, "list_price": 45.0,
         "stock_level": 30, "reserved": 2, "available": 28, "reorder_point": 5, "warehouse_id": "wh_001"},
        {"sku": "SKU-2001", "name": "Bolt M8", "category": "accessories", "unit_cost": 0.5, "list_price": 1.5,
         "stock_level": 100, "reserved": 0, "available": 100, "reorder_point": 50, "warehouse_id": "wh_002"},
        {"sku": "SKU-2002", "name": "Washer Set", "category": "accessories", "unit_cost": 2.0, "list_price": 5.0,
         "stock_level": 200, "reserved": 5, "available": 195, "reorder_point": 100, "warehouse_id": "wh_002"}
    ]
    with open("data/inventory/inventory.json", "w") as f:
        json.dump({"inventory": inventory_items}, f, indent=2)

    # ====== data/warehouses.json ======
    warehouses = [
        {"warehouse_id": "wh_001", "name": "Central Fulfillment Hub", "location": "Chicago, IL",
         "capacity": 500, "current_utilization": 80},
        {"warehouse_id": "wh_002", "name": "East Distribution Center", "location": "Newark, NJ",
         "capacity": 300, "current_utilization": 10},
        {"warehouse_id": "wh_003", "name": "West Distribution Center", "location": "Los Angeles, CA",
         "capacity": 400, "current_utilization": 5}
    ]
    with open("data/warehouses.json", "w") as f:
        json.dump({"warehouses": warehouses}, f, indent=2)

if __name__ == "__main__":
    build_env()
