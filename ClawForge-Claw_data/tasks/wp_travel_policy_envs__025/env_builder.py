import json, os

def build_env():
    # 核心目录
    os.makedirs("ops/prices", exist_ok=True)
    os.makedirs("ops/archived", exist_ok=True)  # 干扰

    # ====== 差旅政策 ======
    policy = {
        "policy_id": "acme_business_2026",
        "name": "Acme Corp Business Travel Policy",
        "version": "v1.0.2026",
        "max_cost_per_booking": 3000,
        "max_single_booking_cost": 2500,
        "allowed_cabin_classes": ["business", "premium_economy", "economy"],
        "min_advance_booking_days": 14,
        "requires_approval_above": 2000,
        "preferred_vendors": ["SkyBook", "AeroCheap"],
        "restricted_routes": [],
        "required_documents": ["passport", "visa"],
        "no_refund_cabin_classes": ["economy"]
    }
    with open("ops/policy.json", "w") as f:
        json.dump(policy, f, indent=2)

    # ====== 审批人列表 ======
    with open("ops/approvers.txt", "w") as f:
        f.write("mike.li@acme-corp.com (部门经理)\n")
        f.write("carol.wang@acme-corp.com (副总裁)\n")
        f.write("alex.chen@acme-corp.com (财务总监)\n")

    # ====== 价格数据（带有干扰项） ======
    # 有效航班：SkyBook 商务舱 $1750
    flights = {
        "skybook": {
            "platform_id": "skybook_001",
            "name": "SkyBook",
            "region": "North America",
            "is_active": True,
            "flights": [
                {
                    "flight_id": "SB-20260615-JFK-LHR-001",
                    "origin": "JFK",
                    "destination": "LHR",
                    "departure_date": "2026-06-15",
                    "cabin_class": "business",
                    "passengers": 1,
                    "base_fare": 1600.00,
                    "taxes": 100.00,
                    "service_fee": 50.00,
                    "total": 1750.00
                },
                {
                    "flight_id": "SB-20260615-JFK-LHR-002",
                    "origin": "JFK",
                    "destination": "LHR",
                    "departure_date": "2026-06-16",  # 日期不匹配
                    "cabin_class": "business",
                    "passengers": 1,
                    "base_fare": 1550.00,
                    "taxes": 100.00,
                    "service_fee": 50.00,
                    "total": 1700.00
                }
            ]
        },
        "aerocheap": {
            "platform_id": "ac_002",
            "name": "AeroCheap",
            "region": "North America",
            "is_active": False,  # 平台不活跃
            "flights": [
                {
                    "flight_id": "AC-20260615-JFK-LHR-101",
                    "origin": "JFK",
                    "destination": "LHR",
                    "departure_date": "2026-06-15",
                    "cabin_class": "economy",  # 舱位不符政策（政策允许商务舱但此处是经济舱，且非preferred）
                    "passengers": 1,
                    "total": 1200.00
                }
            ]
        },
        "flightpro": {
            "platform_id": "fp_003",
            "name": "FlightPro",
            "region": "Europe",
            "is_active": True,
            "flights": [
                {
                    "flight_id": "FP-20260615-JFK-LHR-201",
                    "origin": "JFK",
                    "destination": "LHR",
                    "departure_date": "2026-06-15",
                    "cabin_class": "business",
                    "passengers": 1,
                    "total": 2100.00
                }
            ]
        }
    }

    for key, data in flights.items():
        with open(f"ops/prices/{key}.json", "w") as f:
            json.dump(data, f, indent=2)

    # 干扰：旧版存档
    archived_old = {
        "platform_id": "skybook_old",
        "is_active": True,
        "flights": [
            {
                "flight_id": "SB-20250615-JFK-LHR-OLD",
                "departure_date": "2025-06-15",
                "total": 1500.00
            }
        ]
    }
    with open("ops/archived/skybook_2025.json", "w") as f:
        json.dump(archived_old, f, indent=2)

    # 干扰：不相关 readme
    with open("ops/README.md", "w") as f:
        f.write("# Ops Directory\nContains flight price snapshots and policy files.\n")

if __name__ == "__main__":
    build_env()
