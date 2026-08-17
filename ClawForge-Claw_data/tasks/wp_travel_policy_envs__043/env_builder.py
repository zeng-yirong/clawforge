import os
import json
import shutil

def build_env():
    # 清理并创建目录
    base_dirs = ["data/platforms", "data/policies", "data/accounts", "ops", "tmp", "logs"]
    for d in base_dirs:
        os.makedirs(d, exist_ok=True)

    # ===== 平台数据 =====
    # 1. SkyBook (首选供应商, 活跃)
    skybook = {
        "platform_id": "skybook",
        "name": "SkyBook",
        "region": "North America",
        "is_active": True,
        "transaction_fee": 50.0,
        "service_fee": 30.0,
        "payment_methods": ["credit_card", "invoice"],
        "cancellation_policy": "free 24h",
        "discounts": [],
        "promotions": [],
        "loyalty_program": {"name": "SkyMiles", "points": 0},
        "flights": [
            {
                "flight_id": "SKY-2026-0615-JFK-LHR-001",
                "origin": "JFK",
                "destination": "LHR",
                "departure_date": "2026-06-15",
                "cabin_class": "business",
                "base_price": 1800.00
            },
            {
                "flight_id": "SKY-2026-0615-JFK-LHR-002",
                "origin": "JFK",
                "destination": "LHR",
                "departure_date": "2026-06-15",
                "cabin_class": "business",
                "base_price": 2600.00
            },
            {
                "flight_id": "SKY-2026-0615-JFK-LHR-003",
                "origin": "JFK",
                "destination": "LHR",
                "departure_date": "2026-06-01",
                "cabin_class": "business",
                "base_price": 1500.00
            }
        ]
    }
    with open("data/platforms/skybook.json", "w") as f:
        json.dump(skybook, f, indent=2)

    # 2. AeroCheap (首选供应商, 活跃)
    acheap = {
        "platform_id": "acheap",
        "name": "AeroCheap",
        "region": "Europe",
        "is_active": True,
        "transaction_fee": 40.0,
        "service_fee": 25.0,
        "payment_methods": ["bank_transfer"],
        "cancellation_policy": "non-refundable",
        "discounts": [],
        "promotions": [],
        "loyalty_program": {"name": "CheapPoints", "points": 0},
        "flights": [
            {
                "flight_id": "ACHEAP-2026-0615-JFK-LHR-001",
                "origin": "JFK",
                "destination": "LHR",
                "departure_date": "2026-06-15",
                "cabin_class": "economy",
                "base_price": 1700.00
            },
            {
                "flight_id": "ACHEAP-2026-0615-JFK-LHR-002",
                "origin": "JFK",
                "destination": "LHR",
                "departure_date": "2026-06-15",
                "cabin_class": "business",
                "base_price": 2100.00
            }
        ]
    }
    with open("data/platforms/acheap.json", "w") as f:
        json.dump(acheap, f, indent=2)

    # 3. FlightPro (非首选, 活跃)
    flightpro = {
        "platform_id": "flightpro",
        "name": "FlightPro",
        "region": "North America",
        "is_active": True,
        "transaction_fee": 60.0,
        "service_fee": 35.0,
        "payment_methods": ["credit_card"],
        "cancellation_policy": "24h notice",
        "discounts": [],
        "promotions": [],
        "loyalty_program": {"name": "ProRewards", "points": 0},
        "flights": [
            {
                "flight_id": "FLPRO-2026-0615-JFK-LHR-001",
                "origin": "JFK",
                "destination": "LHR",
                "departure_date": "2026-06-15",
                "cabin_class": "business",
                "base_price": 2000.00
            },
            {
                "flight_id": "FLPRO-2026-0615-JFK-LHR-002",
                "origin": "JFK",
                "destination": "LHR",
                "departure_date": "2026-06-15",
                "cabin_class": "first",
                "base_price": 3000.00
            }
        ]
    }
    with open("data/platforms/flightpro.json", "w") as f:
        json.dump(flightpro, f, indent=2)

    # 4. 干扰：非活跃平台 (已停用)
    defunct = {
        "platform_id": "oldfly",
        "name": "OldFly",
        "region": "Europe",
        "is_active": False,
        "transaction_fee": 10.0,
        "service_fee": 5.0,
        "payment_methods": [],
        "cancellation_policy": "unknown",
        "discounts": [],
        "promotions": [],
        "loyalty_program": {},
        "flights": [
            {
                "flight_id": "OLD-2026-0615-JFK-LHR-001",
                "origin": "JFK",
                "destination": "LHR",
                "departure_date": "2026-06-15",
                "cabin_class": "business",
                "base_price": 1200.00
            }
        ]
    }
    with open("data/platforms/oldfly.json", "w") as f:
        json.dump(defunct, f, indent=2)

    # ===== 政策数据 =====
    # 当前政策
    current_policy = {
        "policy_id": "acme_travel_policy_v3",
        "name": "Acme Corp Business Travel Policy",
        "version": "3.0",
        "max_cost_per_booking": 2500,
        "max_single_booking_cost": 2500,
        "allowed_cabin_classes": ["business"],
        "min_advance_booking_days": 14,
        "requires_approval_above": 1500,
        "preferred_vendors": ["skybook", "acheap"],
        "restricted_routes": [],
        "required_documents": ["passport"],
        "no_refund_cabin_classes": ["economy"]
    }
    with open("data/policies/current_policy.json", "w") as f:
        json.dump(current_policy, f, indent=2)

    # 干扰：过期政策（版本2）
    old_policy = {
        "policy_id": "acme_travel_policy_v2",
        "name": "Acme Corp Business Travel Policy",
        "version": "2.0",
        "max_cost_per_booking": 3000,
        "max_single_booking_cost": 3000,
        "allowed_cabin_classes": ["business", "first"],
        "min_advance_booking_days": 7,
        "requires_approval_above": 2000,
        "preferred_vendors": ["skybook"],
        "restricted_routes": [],
        "required_documents": [],
        "no_refund_cabin_classes": []
    }
    with open("data/policies/old_policy.json", "w") as f:
        json.dump(old_policy, f, indent=2)

    # ===== 账户数据 =====
    alice = {
        "account_id": "alice_smith",
        "company_name": "Acme Corp",
        "travel_budget": 10000,
        "currency": "USD",
        "approvers": ["manager.bob@acme.com"]
    }
    with open("data/accounts/alice.json", "w") as f:
        json.dump(alice, f, indent=2)

    # ===== 干扰文件 =====
    with open("tmp/notes.txt", "w") as f:
        f.write("Ignore this file\n")
    with open("logs/debug.log", "w") as f:
        f.write("2026-05-25 10:00:00 INFO start\n")

if __name__ == "__main__":
    build_env()
