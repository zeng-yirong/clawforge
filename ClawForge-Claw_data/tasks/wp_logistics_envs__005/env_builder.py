import json, os, random
from datetime import datetime, timedelta

def build_env():
    # 确保目录存在
    for d in ["data", "ops", "data/inventory"]:
        os.makedirs(d, exist_ok=True)

    # ---------- 退货单 ----------
    returns = [
        {
            "return_id": "ret_001",
            "order_id": "ord_001",
            "customer_id": "c001",
            "reason": "defective",
            "requested_at": "2025-03-28T10:30:00Z",
            "status": "pending_review",
            "items": [{"sku": "SKU-1001", "qty": 1, "name": "Wireless Mouse"}],
            "refund_amount": 45.0,
            "return_tracking_number": "RET001",
            "inspection_notes": "",
            "resolution": ""
        },
        {
            "return_id": "ret_002",
            "order_id": "ord_002",
            "customer_id": "c002",
            "reason": "change of mind",
            "requested_at": "2025-03-29T08:15:00Z",
            "status": "pending_review",
            "items": [{"sku": "SKU-2001", "qty": 2, "name": "USB-C Hub"}],
            "refund_amount": 32.0,
            "return_tracking_number": "RET002",
            "inspection_notes": "",
            "resolution": ""
        },
        {
            "return_id": "ret_003",
            "order_id": "ord_003",
            "customer_id": "c003",
            "reason": "wrong item",
            "requested_at": "2025-03-29T09:00:00Z",
            "status": "pending_review",
            "items": [{"sku": "SKU-3001", "qty": 1, "name": "Keyboard"}],
            "refund_amount": 60.0,
            "return_tracking_number": "RET003",
            "inspection_notes": "",
            "resolution": ""
        },
        {
            "return_id": "ret_004",
            "order_id": "ord_004",
            "customer_id": "c004",
            "reason": "defective",
            "requested_at": "2025-03-27T14:00:00Z",
            "status": "approved",
            "items": [{"sku": "SKU-1002", "qty": 1, "name": "Monitor Stand"}],
            "refund_amount": 25.0,
            "return_tracking_number": "RET004",
            "inspection_notes": "Already inspected",
            "resolution": "refund_approved"
        },
        {
            "return_id": "ret_005",
            "order_id": "ord_005",
            "customer_id": "c005",
            "reason": "wrong item",
            "requested_at": "2025-03-26T11:20:00Z",
            "status": "pending_inspection",
            "items": [{"sku": "SKU-4001", "qty": 1, "name": "Webcam"}],
            "refund_amount": 70.0,
            "return_tracking_number": "RET005",
            "inspection_notes": "Item received, pending check",
            "resolution": ""
        }
    ]
    with open("data/returns.json", "w") as f:
        json.dump(returns, f, indent=2)

    # 干扰备份文件
    backup = [
        {"return_id": "ret_backup_1", "reason": "defective", "status": "pending_review"}
    ]
    with open("data/returns_backup.json", "w") as f:
        json.dump(backup, f, indent=2)

    # ---------- 发货单 ----------
    shipments = [
        {
            "shipment_id": "ship_001",
            "order_id": "ord_001",
            "carrier": "UPS",
            "tracking_number": "UPS123456789",
            "status": "delivered",
            "shipped_at": "2025-03-20T08:00:00Z",
            "delivered_at": "2025-03-22T14:30:00Z",
            "current_location": "Delivered to recipient",
            "events": [{"timestamp": "2025-03-20T08:00:00Z", "location": "Warehouse - LA", "description": "Picked up"}]
        },
        {
            "shipment_id": "ship_002",
            "order_id": "ord_002",
            "carrier": "FedEx",
            "tracking_number": "FX456789123",
            "status": "in_transit",
            "shipped_at": "2025-03-28T09:00:00Z",
            "delivered_at": "",
            "current_location": "Denver, CO",
            "events": [{"timestamp": "2025-03-28T09:00:00Z", "location": "Warehouse - LA", "description": "Departed"}]
        },
        {
            "shipment_id": "ship_003",
            "order_id": "ord_003",
            "carrier": "FedEx",
            "tracking_number": "FX654987321",
            "status": "out_for_delivery",
            "shipped_at": "2025-03-27T10:00:00Z",
            "delivered_at": "",
            "current_location": "Newark, NJ",
            "events": []
        },
        {
            "shipment_id": "ship_004",
            "order_id": "ord_004",
            "carrier": "UPS",
            "tracking_number": "UPS456123789",
            "status": "delivered",
            "shipped_at": "2025-03-25T11:00:00Z",
            "delivered_at": "2025-03-27T16:00:00Z",
            "current_location": "Delivered to recipient",
            "events": []
        },
        {
            "shipment_id": "ship_005",
            "order_id": "ord_005",
            "carrier": "FedEx",
            "tracking_number": "FX321654987",
            "status": "processing",
            "shipped_at": "",
            "delivered_at": "",
            "current_location": "Warehouse - LA",
            "events": []
        }
    ]
    with open("data/shipments.json", "w") as f:
        json.dump(shipments, f, indent=2)

    # 干扰旧发货单
    old_shipments = [
        {"shipment_id": "ship_old_1", "status": "processing", "carrier": "FedEx"}
    ]
    with open("data/shipments_old.json", "w") as f:
        json.dump(old_shipments, f, indent=2)

    # ---------- 库存 ----------
    inventory = [
        {"sku": "SKU-1001", "name": "Wireless Mouse", "category": "electronics", "unit_cost": 12.0, "list_price": 25.0, "stock_level": 150, "reserved": 10, "available": 140, "reorder_point": 30, "warehouse_id": "wh_001"},
        {"sku": "SKU-1002", "name": "Monitor Stand", "category": "accessories", "unit_cost": 8.0, "list_price": 20.0, "stock_level": 100, "reserved": 5, "available": 95, "reorder_point": 20, "warehouse_id": "wh_001"},
        {"sku": "SKU-2001", "name": "USB-C Hub", "category": "electronics", "unit_cost": 15.0, "list_price": 32.0, "stock_level": 80, "reserved": 0, "available": 80, "reorder_point": 15, "warehouse_id": "wh_001"},
        {"sku": "SKU-3001", "name": "Keyboard", "category": "electronics", "unit_cost": 30.0, "list_price": 60.0, "stock_level": 60, "reserved": 2, "available": 58, "reorder_point": 10, "warehouse_id": "wh_001"},
        {"sku": "SKU-4001", "name": "Webcam", "category": "electronics", "unit_cost": 35.0, "list_price": 70.0, "stock_level": 45, "reserved": 1, "available": 44, "reorder_point": 8, "warehouse_id": "wh_001"},
        # 其他仓库干扰
        {"sku": "SKU-1002", "name": "Monitor Stand", "category": "accessories", "unit_cost": 8.0, "list_price": 20.0, "stock_level": 200, "reserved": 20, "available": 180, "reorder_point": 40, "warehouse_id": "wh_002"},
        {"sku": "SKU-1002", "name": "Monitor Stand", "category": "accessories", "unit_cost": 8.0, "list_price": 20.0, "stock_level": 50, "reserved": 0, "available": 50, "reorder_point": 10, "warehouse_id": "wh_003"}
    ]
    with open("data/inventory/inventory.json", "w") as f:
        json.dump(inventory, f, indent=2)

if __name__ == "__main__":
    build_env()
