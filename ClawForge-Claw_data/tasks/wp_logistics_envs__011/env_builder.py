import json, os

def build_env():
    # 确保目录存在
    os.makedirs("data/orders", exist_ok=True)
    os.makedirs("data/inventory", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 退货数据
    returns = [
        {
            "return_id": "ret_001",
            "order_id": "ord_007",
            "customer_id": "cust_003",
            "reason": "defective",
            "requested_at": "2025-03-10T09:15:00Z",
            "status": "pending_review",
            "items": [{"sku": "SKU-1001", "qty": 1}],
            "refund_amount": 29.99,
            "return_tracking_number": "RET001",
            "inspection_notes": "Customer reported screen flickering",
            "resolution": "pending"
        },
        {
            "return_id": "ret_002",
            "order_id": "ord_012",
            "customer_id": "cust_001",
            "reason": "no_longer_needed",
            "requested_at": "2025-03-12T14:30:00Z",
            "status": "approved",
            "items": [{"sku": "SKU-2001", "qty": 2}],
            "refund_amount": 59.98,
            "return_tracking_number": "RET002",
            "inspection_notes": "Unopened box",
            "resolution": "refund_approved"
        },
        {
            "return_id": "ret_003",
            "order_id": "ord_019",
            "customer_id": "cust_005",
            "reason": "wrong item",
            "requested_at": "2025-03-13T08:45:00Z",
            "status": "received",
            "items": [{"sku": "SKU-3005", "qty": 1}],
            "refund_amount": 89.99,
            "return_tracking_number": "RET003",
            "inspection_notes": "Received SKU-3005 instead of SKU-3002",
            "resolution": "pending"
        },
        {
            "return_id": "ret_004",
            "order_id": "ord_022",
            "customer_id": "cust_002",
            "reason": "damaged",
            "requested_at": "2025-03-11T11:00:00Z",
            "status": "rejected",
            "items": [{"sku": "SKU-1007", "qty": 1}],
            "refund_amount": 0.00,
            "return_tracking_number": "RET005",
            "inspection_notes": "Past 30-day window",
            "resolution": "rejected - past 30-day return window"
        },
        {
            "return_id": "ret_005",
            "order_id": "ord_031",
            "customer_id": "cust_006",
            "reason": "other",
            "requested_at": "2025-03-14T16:20:00Z",
            "status": "pending_review",
            "items": [{"sku": "SKU-4001", "qty": 1}],
            "refund_amount": 45.00,
            "return_tracking_number": "RET006",
            "inspection_notes": "Customer just changed mind",
            "resolution": "pending"
        }
    ]
    with open("data/returns.json", "w") as f:
        json.dump({"returns": returns}, f, indent=2)

    # 发货数据
    shipments = [
        {"shipment_id": "ship_001", "order_id": "ord_001", "carrier": "FedEx", "tracking_number": "FX321654987", "status": "delivered", "shipped_at": "2025-03-05T10:00:00Z", "delivered_at": "2025-03-08T14:30:00Z", "current_location": "Delivered to recipient", "events": []},
        {"shipment_id": "ship_002", "order_id": "ord_004", "carrier": "UPS", "tracking_number": "UPS123456789", "status": "in_transit", "shipped_at": "2025-03-15T09:00:00Z", "delivered_at": "", "current_location": "Denver, CO", "events": []},
        {"shipment_id": "ship_003", "order_id": "ord_008", "carrier": "FedEx", "tracking_number": "FX456789123", "status": "out_for_delivery", "shipped_at": "2025-03-16T08:00:00Z", "delivered_at": "", "current_location": "Indianapolis, IN", "events": []},
        {"shipment_id": "ship_004", "order_id": "ord_010", "carrier": "UPS", "tracking_number": "UPS456123789", "status": "delivered", "shipped_at": "2025-03-12T11:00:00Z", "delivered_at": "2025-03-14T16:00:00Z", "current_location": "Delivered to recipient", "events": []},
        {"shipment_id": "ship_005", "order_id": "ord_015", "carrier": "FedEx", "tracking_number": "FX654987321", "status": "processing", "shipped_at": "", "delivered_at": "", "current_location": "Warehouse - LA", "events": []},
        {"shipment_id": "ship_006", "order_id": "ord_020", "carrier": "UPS", "tracking_number": "UPS987654321", "status": "processing", "shipped_at": "", "delivered_at": "", "current_location": "Warehouse - NY", "events": []}
    ]
    with open("data/shipments.json", "w") as f:
        json.dump({"shipments": shipments}, f, indent=2)

    # 库存数据
    inventory_list = [
        {"sku": "SKU-1001", "name": "Widget A", "category": "electronics", "unit_cost": 12.50, "list_price": 29.99, "stock_level": 45, "reserved": 10, "available": 35, "reorder_point": 20, "warehouse_id": "wh_001"},
        {"sku": "SKU-1002", "name": "Gadget B", "category": "electronics", "unit_cost": 35.00, "list_price": 79.99, "stock_level": 20, "reserved": 5, "available": 15, "reorder_point": 10, "warehouse_id": "wh_001"},
        {"sku": "SKU-1003", "name": "Cable C", "category": "accessories", "unit_cost": 2.50, "list_price": 9.99, "stock_level": 200, "reserved": 20, "available": 180, "reorder_point": 50, "warehouse_id": "wh_001"},
        {"sku": "SKU-2001", "name": "Tool D", "category": "parts", "unit_cost": 18.00, "list_price": 29.99, "stock_level": 12, "reserved": 2, "available": 10, "reorder_point": 15, "warehouse_id": "wh_002"},
        {"sku": "SKU-3005", "name": "Sensor E", "category": "electronics", "unit_cost": 60.00, "list_price": 89.99, "stock_level": 8, "reserved": 2, "available": 6, "reorder_point": 10, "warehouse_id": "wh_001"},
    ]
    with open("data/inventory/inventory.json", "w") as f:
        json.dump({"inventory": inventory_list}, f, indent=2)

    # 创建干扰文件
    with open("data/orders/orders.json", "w") as f:
        json.dump({"orders": []}, f)
    with open("data/warehouses.json", "w") as f:
        json.dump({"warehouses": []}, f)
    with open("ops/old_report.json", "w") as f:
        json.dump({"dummy": True}, f)
    with open("readme.txt", "w") as f:
        f.write("Ignore me.\n")

if __name__ == "__main__":
    build_env()
