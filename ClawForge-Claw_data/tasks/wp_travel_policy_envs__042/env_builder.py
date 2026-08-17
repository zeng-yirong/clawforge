import os
import json

def build_env():
    # 创建目录结构
    os.makedirs("db_dumps/platforms", exist_ok=True)
    os.makedirs("db_dumps/policies", exist_ok=True)
    os.makedirs("db_dumps/flights", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # --- 平台信息 (只有 skybook 和 flightpro 是 active) ---
    platforms = {
        "skybook.json": {
            "platform_id": "skybook",
            "name": "SkyBook",
            "is_active": True,
            "region": "Europe",
            "transaction_fee": 50.0,
            "service_fee": 30.0
        },
        "flightpro.json": {
            "platform_id": "flightpro",
            "name": "FlightPro",
            "is_active": True,
            "region": "Europe",
            "transaction_fee": 60.0,
            "service_fee": 25.0
        },
        "aero_cheap.json": {
            "platform_id": "aero_cheap",
            "name": "AeroCheap",
            "is_active": False,          # 停用平台，干扰项
            "region": "Europe",
            "transaction_fee": 40.0,
            "service_fee": 20.0
        }
    }
    for fname, content in platforms.items():
        with open(f"db_dumps/platforms/{fname}", "w") as f:
            json.dump(content, f, indent=2)

    # --- 政策文件 (最新版 v2，旧版 v1 为干扰) ---
    policies = {
        "acme_corp_v2.json": {
            "policy_id": "acme_corp_v2",
            "name": "Acme Corp Business Travel Policy",
            "version": "2",
            "max_cost_per_booking": 5000,
            "max_single_booking_cost": 5000,
            "allowed_cabin_classes": ["business"],
            "min_advance_booking_days": 0,
            "requires_approval_above": 3000,
            "preferred_vendors": [],
            "restricted_routes": [],
            "required_documents": [],
            "no_refund_cabin_classes": []
        },
        "acme_corp_v1.json": {
            "policy_id": "acme_corp_v1",
            "name": "Acme Corp Business Travel Policy",
            "version": "1",
            "max_cost_per_booking": 4000,       # 旧版上限低，但不应被使用
            "max_single_booking_cost": 4000,
            "allowed_cabin_classes": ["business", "economy"],
            "min_advance_booking_days": 2,
            "requires_approval_above": 2000,
            "preferred_vendors": [],
            "restricted_routes": [],
            "required_documents": [],
            "no_refund_cabin_classes": []
        }
    }
    for fname, content in policies.items():
        with open(f"db_dumps/policies/{fname}", "w") as f:
            json.dump(content, f, indent=2)

    # --- 各平台的航班数据 (商务舱 + 干扰舱位/平台) ---
    flights = {
        "skybook_flights.json": [
            {"flight_id": "SKB-001", "platform_id": "skybook", "cabin_class": "business", "price": 3200},
            {"flight_id": "SKB-002", "platform_id": "skybook", "cabin_class": "economy",  "price": 1500},
            {"flight_id": "SKB-003", "platform_id": "skybook", "cabin_class": "business", "price": 3500}   # 更贵，不影响答案
        ],
        "flightpro_flights.json": [
            {"flight_id": "FLP-001", "platform_id": "flightpro", "cabin_class": "business", "price": 4800},
            {"flight_id": "FLP-002", "platform_id": "flightpro", "cabin_class": "economy",  "price": 1200},
            {"flight_id": "FLP-003", "platform_id": "flightpro", "cabin_class": "business", "price": 5100}   # 超出预算上限
        ],
        "aero_cheap_flights.json": [
            {"flight_id": "ACH-001", "platform_id": "aero_cheap", "cabin_class": "business", "price": 2000},  # 平台 inactive，不能选
            {"flight_id": "ACH-002", "platform_id": "aero_cheap", "cabin_class": "economy",  "price": 800}
        ]
    }
    for fname, content in flights.items():
        with open(f"db_dumps/flights/{fname}", "w") as f:
            json.dump(content, f, indent=2)

if __name__ == "__main__":
    build_env()
