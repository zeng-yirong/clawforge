import os
import json

def build_env():
    # 创建数据目录
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # ========== 退货数据 ==========
    returns = [
        {
            "return_id": "ret_001",
            "order_id": "ord_011",
            "customer_id": "cust_101",
            "reason": "defective",
            "requested_at": "2025-03-10T08:00:00Z",
            "status": "pending_review",
            "items": [{"sku": "SKU-1002", "qty": 1}],
            "refund_amount": 45.0,
            "return_tracking_number": "RET001",
            "inspection_notes": "",
            "resolution": ""
        },
        {
            "return_id": "ret_002",
            "order_id": "ord_012",
            "customer_id": "cust_102",
            "reason": "damaged",
            "requested_at": "2025-03-11T09:00:00Z",
            "status": "rejected",
            "items": [{"sku": "SKU-2001", "qty": 2}],
            "refund_amount": 80.0,
            "return_tracking_number": "RET002",
            "inspection_notes": "past window",
            "resolution": "rejected - past 30-day return window"
        },
        {
            "return_id": "ret_003",
            "order_id": "ord_013",
            "customer_id": "cust_103",
            "reason": "wrong item",
            "requested_at": "2025-03-12T10:00:00Z",
            "status": "pending_inspection",
            "items": [{"sku": "SKU-1002", "qty": 1}],
            "refund_amount": 45.0,
            "return_tracking_number": "RET003",
            "inspection_notes": "",
            "resolution": ""
        },
        {
            "return_id": "ret_004",
            "order_id": "ord_014",
            "customer_id": "cust_104",
            "reason": "defective",
            "requested_at": "2025-03-13T11:00:00Z",
            "status": "approved",
            "items": [{"sku": "SKU-3001", "qty": 1}],
            "refund_amount": 120.0,
            "return_tracking_number": "RET004",
            "inspection_notes": "confirmed defective",
            "resolution": "refund_approved"
        }
    ]
    with open("data/returns.json", "w") as f:
        json.dump(returns, f, indent=2)

    # 干扰：旧版本退货数据
    os.makedirs("data/archive", exist_ok=True)
    old_returns = [
        {
            "return_id": "ret_001",
            "reason": "defective",
            "status": "pending_review",
            "resolution": ""
        }
    ]
    with open("data/archive/returns_2024.json", "w") as f:
        json.dump(old_returns, f, indent=2)

    # ========== 发货数据 ==========
    shipments = [
        {
            "shipment_id": "ship_005",
            "order_id": "ord_015",
            "carrier": "FedEx",
            "tracking_number": "FX321654987",
            "status": "processing",
            "shipped_at": "",
            "delivered_at": "",
            "current_location": "Warehouse - LA",
            "events": [{"timestamp": "2025-03-14T12:00:00Z", "location": "Warehouse - LA", "status": "label_created"}]
        },
        {
            "shipment_id": "ship_006",
            "order_id": "ord_016",
            "carrier": "UPS",
            "tracking_number": "UPS987654321",
            "status": "delivered",
            "shipped_at": "2025-03-12T08:00:00Z",
            "delivered_at": "2025-03-14T14:00:00Z",
            "current_location": "Delivered to recipient",
            "events": [{"timestamp": "2025-03-12T08:00:00Z", "location": "Newark, NJ", "status": "shipped"}]
        },
        {
            "shipment_id": "ship_007",
            "order_id": "ord_017",
            "carrier": "FedEx",
            "tracking_number": "FX456789123",
            "status": "in_transit",
            "shipped_at": "2025-03-13T09:00:00Z",
            "delivered_at": "",
            "current_location": "Denver, CO",
            "events": [{"timestamp": "2025-03-13T09:00:00Z", "location": "Chicago, IL", "status": "shipped"}]
        }
    ]
    with open("data/shipments.json", "w") as f:
        json.dump(shipments, f, indent=2)

    # 干扰：错误格式的发货文件
    with open("data/shipments_old.csv", "w") as f:
        f.write("shipment_id,carrier,status\nship_005,FedEx,processing\n")

    # ========== 库存数据 ==========
    os.makedirs("data/inventory", exist_ok=True)
    inventory = [
        {
            "sku": "SKU-1002",
            "name": "Widget A",
            "category": "parts",
            "unit_cost": 5.0,
            "list_price": 12.0,
            "stock_level": 100,
            "reserved": 0,
            "available": 100,
            "reorder_point": 20,
            "warehouse_id": "wh_001"
        },
        {
            "sku": "SKU-2001",
            "name": "Gadget B",
            "category": "electronics",
            "unit_cost": 25.0,
            "list_price": 60.0,
            "stock_level": 50,
            "reserved": 5,
            "available": 45,
            "reorder_point": 10,
            "warehouse_id": "wh_001"
        },
        {
            "sku": "SKU-3001",
            "name": "Accessory C",
            "category": "accessories",
            "unit_cost": 10.0,
            "list_price": 25.0,
            "stock_level": 200,
            "reserved": 10,
            "available": 190,
            "reorder_point": 30,
            "warehouse_id": "wh_002"
        },
        {
            "sku": "SKU-1002",
            "name": "Widget A",
            "category": "parts",
            "unit_cost": 5.0,
            "list_price": 12.0,
            "stock_level": 80,
            "reserved": 0,
            "available": 80,
            "reorder_point": 20,
            "warehouse_id": "wh_002"
        }
    ]
    with open("data/inventory/inventory.json", "w") as f:
        json.dump(inventory, f, indent=2)

    # 干扰：备份库存（旧数据）
    with open("data/inventory/inventory_backup.json", "w") as f:
        json.dump([
            {"sku": "SKU-1002", "stock_level": 95, "warehouse_id": "wh_001"}
        ], f, indent=2)

if __name__ == "__main__":
    build_env()
