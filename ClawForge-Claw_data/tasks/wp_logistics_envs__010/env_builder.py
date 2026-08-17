import os
import json

def build_env():
    # 创建 data 目录结构
    os.makedirs("data/returns", exist_ok=True)
    os.makedirs("data/shipments", exist_ok=True)
    os.makedirs("data/inventory", exist_ok=True)

    # 退货数据 (包含干扰项: ret_002 已处理, ret_004 已拒绝)
    returns = [
        {
            "return_id": "ret_001",
            "order_id": "ord_001",
            "customer_id": "cust_001",
            "reason": "defective",
            "requested_at": "2025-03-20T10:00:00Z",
            "status": "pending_review",
            "items": [{"sku": "SKU-1001", "qty": 1}],
            "refund_amount": 49.99,
            "return_tracking_number": "RET001",
            "inspection_notes": "Customer reported item arrived with cracked screen.",
            "resolution": ""
        },
        {
            "return_id": "ret_002",
            "order_id": "ord_002",
            "customer_id": "cust_002",
            "reason": "no longer needed",
            "requested_at": "2025-03-19T14:00:00Z",
            "status": "approved",
            "items": [{"sku": "SKU-1003", "qty": 2}],
            "refund_amount": 89.98,
            "return_tracking_number": "RET002",
            "inspection_notes": "Approved, refund initiated.",
            "resolution": "refund_approved"
        },
        {
            "return_id": "ret_003",
            "order_id": "ord_003",
            "customer_id": "cust_003",
            "reason": "wrong item",
            "requested_at": "2025-03-21T09:30:00Z",
            "status": "pending_inspection",
            "items": [{"sku": "SKU-1005", "qty": 1}],
            "refund_amount": 0.0,
            "return_tracking_number": "RET003",
            "inspection_notes": "Customer received SKU-1006 instead of SKU-1005.",
            "resolution": ""
        },
        {
            "return_id": "ret_004",
            "order_id": "ord_004",
            "customer_id": "cust_004",
            "reason": "damaged in transit",
            "requested_at": "2025-03-18T16:00:00Z",
            "status": "rejected",
            "items": [{"sku": "SKU-1004", "qty": 1}],
            "refund_amount": 0.0,
            "return_tracking_number": "RET004",
            "inspection_notes": "Rejected - past 30-day return window.",
            "resolution": "rejected - past 30-day return window"
        }
    ]

    with open("data/returns/returns.json", "w") as f:
        json.dump({"returns": returns}, f, indent=2)

    # 发货数据 (干扰项: ship_003 已送达, ship_006 在途)
    shipments = [
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
        },
        {
            "shipment_id": "ship_003",
            "order_id": "ord_003",
            "carrier": "UPS",
            "tracking_number": "UPS123456789",
            "status": "delivered",
            "shipped_at": "2025-03-15T08:00:00Z",
            "delivered_at": "2025-03-17T12:00:00Z",
            "current_location": "Delivered to recipient",
            "events": []
        },
        {
            "shipment_id": "ship_006",
            "order_id": "ord_006",
            "carrier": "FedEx",
            "tracking_number": "FX456789123",
            "status": "in_transit",
            "shipped_at": "2025-03-22T10:00:00Z",
            "delivered_at": "",
            "current_location": "Denver, CO",
            "events": []
        }
    ]

    with open("data/shipments/shipments.json", "w") as f:
        json.dump({"shipments": shipments}, f, indent=2)

    # 库存数据 (干扰: wh_001 有其他 SKU, wh_002 也有 SKU-1002)
    inventory_wh001 = [
        {
            "sku": "SKU-1002",
            "name": "Wireless Mouse",
            "category": "electronics",
            "unit_cost": 12.50,
            "list_price": 25.00,
            "stock_level": 50,
            "reserved": 5,
            "available": 45,
            "reorder_point": 10,
            "warehouse_id": "wh_001"
        },
        {
            "sku": "SKU-1001",
            "name": "USB-C Cable",
            "category": "accessories",
            "unit_cost": 3.20,
            "list_price": 9.99,
            "stock_level": 200,
            "reserved": 10,
            "available": 190,
            "reorder_point": 50,
            "warehouse_id": "wh_001"
        },
        {
            "sku": "SKU-1003",
            "name": "Keyboard",
            "category": "electronics",
            "unit_cost": 45.00,
            "list_price": 89.99,
            "stock_level": 30,
            "reserved": 2,
            "available": 28,
            "reorder_point": 15,
            "warehouse_id": "wh_001"
        }
    ]
    inventory_wh002 = [
        {
            "sku": "SKU-1002",
            "name": "Wireless Mouse",
            "category": "electronics",
            "unit_cost": 12.50,
            "list_price": 25.00,
            "stock_level": 10,
            "reserved": 0,
            "available": 10,
            "reorder_point": 5,
            "warehouse_id": "wh_002"
        }
    ]
    inventory = {
        "wh_001": inventory_wh001,
        "wh_002": inventory_wh002
    }

    with open("data/inventory/inventory.json", "w") as f:
        json.dump({"inventory": inventory}, f, indent=2)

    # 创建 ops 目录（agent 写入位置）
    os.makedirs("ops", exist_ok=True)

if __name__ == "__main__":
    build_env()
