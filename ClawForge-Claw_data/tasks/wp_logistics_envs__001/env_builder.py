import os
import json
import shutil

def build_env():
    # 创建主目录（当前工作目录已是 .）
    os.makedirs("returns", exist_ok=True)
    os.makedirs("returns/backup", exist_ok=True)
    os.makedirs("shipments", exist_ok=True)
    os.makedirs("shipments/old", exist_ok=True)
    os.makedirs("inventory", exist_ok=True)

    # ===== 退货单 =====
    # ret_001：需批准（缺陷）
    ret_001 = {
        "return_id": "ret_001",
        "order_id": "ord_101",
        "customer_id": "cust_001",
        "reason": "defective",
        "requested_at": "2025-03-20T10:00:00Z",
        "status": "pending_review",
        "items": [{"sku": "SKU-1001", "qty": 1}],
        "refund_amount": 25.0,
        "return_tracking_number": "RET001",
        "inspection_notes": "",
        "resolution": ""
    }
    with open("returns/ret_001.json", "w", encoding="utf-8") as f:
        json.dump(ret_001, f, indent=2)

    # ret_002：已批准（干扰，不应重复处理）
    ret_002 = {
        "return_id": "ret_002",
        "order_id": "ord_102",
        "customer_id": "cust_002",
        "reason": "wrong item",
        "requested_at": "2025-03-18T08:00:00Z",
        "status": "approved",
        "items": [{"sku": "SKU-1003", "qty": 1}],
        "refund_amount": 15.0,
        "return_tracking_number": "RET002",
        "inspection_notes": "Customer sent back wrong item",
        "resolution": "refund_approved"
    }
    with open("returns/ret_002.json", "w", encoding="utf-8") as f:
        json.dump(ret_002, f, indent=2)

    # ret_003：需检查（错误物品，换货）
    ret_003 = {
        "return_id": "ret_003",
        "order_id": "ord_103",
        "customer_id": "cust_003",
        "reason": "wrong item",
        "requested_at": "2025-03-21T14:00:00Z",
        "status": "pending_inspection",
        "items": [{"sku": "SKU-1004", "qty": 1}],
        "refund_amount": 30.0,
        "return_tracking_number": "RET003",
        "inspection_notes": "",
        "resolution": ""
    }
    with open("returns/ret_003.json", "w", encoding="utf-8") as f:
        json.dump(ret_003, f, indent=2)

    # 干扰：非 JSON 文件
    with open("returns/ret_004.invalid", "w", encoding="utf-8") as f:
        f.write("This is not a valid JSON file\n")

    # 旧备份（干扰）：ret_001 的旧状态
    ret_001_backup = ret_001.copy()
    ret_001_backup["status"] = "received"
    with open("returns/backup/ret_001.json", "w", encoding="utf-8") as f:
        json.dump(ret_001_backup, f, indent=2)

    # ===== 发运单 =====
    # ship_005：需更新为 shipped
    ship_005 = {
        "shipment_id": "ship_005",
        "order_id": "ord_201",
        "carrier": "FedEx",
        "tracking_number": "FX789456123",
        "status": "processing",
        "shipped_at": "",
        "delivered_at": "",
        "current_location": "Warehouse - LA",
        "events": []
    }
    with open("shipments/ship_005.json", "w", encoding="utf-8") as f:
        json.dump(ship_005, f, indent=2)

    # ship_006：已发货（干扰）
    ship_006 = {
        "shipment_id": "ship_006",
        "order_id": "ord_202",
        "carrier": "UPS",
        "tracking_number": "UPS987654321",
        "status": "shipped",
        "shipped_at": "2025-03-19T11:00:00Z",
        "delivered_at": "",
        "current_location": "In transit",
        "events": [{"timestamp": "2025-03-19T11:00:00Z", "location": "Warehouse - LA"}]
    }
    with open("shipments/ship_006.json", "w", encoding="utf-8") as f:
        json.dump(ship_006, f, indent=2)

    # 旧备份（干扰）：ship_005 的旧状态
    ship_005_old = ship_005.copy()
    ship_005_old["status"] = "out_for_delivery"
    with open("shipments/old/ship_005.json", "w", encoding="utf-8") as f:
        json.dump(ship_005_old, f, indent=2)

    # ===== 库存 =====
    inventory_data = {
        "warehouses": [
            {
                "warehouse_id": "wh_001",
                "items": [
                    {"sku": "SKU-1001", "name": "Widget A", "category": "parts",
                     "unit_cost": 5.0, "list_price": 10.0,
                     "stock_level": 50, "reserved": 5, "available": 45, "reorder_point": 10},
                    {"sku": "SKU-1002", "name": "Widget B", "category": "parts",
                     "unit_cost": 8.0, "list_price": 16.0,
                     "stock_level": 20, "reserved": 10, "available": 10, "reorder_point": 5},
                    {"sku": "SKU-1003", "name": "Gadget X", "category": "electronics",
                     "unit_cost": 25.0, "list_price": 60.0,
                     "stock_level": 5, "reserved": 0, "available": 5, "reorder_point": 2}
                ]
            },
            {
                "warehouse_id": "wh_002",
                "items": [
                    {"sku": "SKU-1002", "name": "Widget B", "category": "parts",
                     "unit_cost": 8.0, "list_price": 16.0,
                     "stock_level": 30, "reserved": 5, "available": 25, "reorder_point": 5},
                    {"sku": "SKU-1005", "name": "Component Y", "category": "accessories",
                     "unit_cost": 3.0, "list_price": 7.0,
                     "stock_level": 100, "reserved": 20, "available": 80, "reorder_point": 30}
                ]
            }
        ]
    }
    with open("inventory/inventory.json", "w", encoding="utf-8") as f:
        json.dump(inventory_data, f, indent=2)

    # ===== 额外干扰文件 =====
    with open("operations_log.txt", "w", encoding="utf-8") as f:
        f.write("2025-03-22 08:00:00 - System startup\n")
        f.write("2025-03-22 08:05:00 - Returns queue checked\n")

if __name__ == "__main__":
    build_env()
