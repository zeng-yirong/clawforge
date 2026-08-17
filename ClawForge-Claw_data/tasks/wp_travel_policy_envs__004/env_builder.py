import os
import json
from datetime import date

def build_env():
    # 当前日期文件，供 agent 参考
    with open("current_date.txt", "w") as f:
        f.write("2026-06-01")

    # === accounts ===
    os.makedirs("accounts", exist_ok=True)
    accounts = {
        "account_id": "acme_001",
        "company_name": "Acme Corp",
        "travel_budget": 50000,
        "currency": "USD",
        "approvers": [
            {"name": "Alice", "email": "alice@acme.com"}
        ]
    }
    with open("accounts/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # === policies ===
    os.makedirs("policies", exist_ok=True)
    policy_001 = {
        "policy_id": "travel_policy_001",
        "name": "Acme Corp Business Travel Policy",
        "version": "v2.1",
        "max_cost_per_booking": 3000,
        "max_single_booking_cost": 3000,
        "allowed_cabin_classes": ["economy", "business"],
        "min_advance_booking_days": 14,
        "requires_approval_above": 2000,
        "preferred_vendors": [],
        "restricted_routes": [],
        "required_documents": ["passport"],
        "no_refund_cabin_classes": ["first"]
    }
    with open("policies/travel_policy_001.json", "w") as f:
        json.dump(policy_001, f, indent=2)

    # 干扰：高管政策（路线限制）
    policy_002 = {
        "policy_id": "travel_policy_002",
        "name": "Acme Corp Executive Travel Policy",
        "version": "v1.0",
        "max_cost_per_booking": 5000,
        "max_single_booking_cost": 5000,
        "allowed_cabin_classes": ["business"],
        "min_advance_booking_days": 7,
        "requires_approval_above": 4000,
        "preferred_vendors": ["SkyBook"],
        "restricted_routes": ["JFK-LHR"],
        "required_documents": ["passport", "executive_clearance"],
        "no_refund_cabin_classes": ["first"]
    }
    with open("policies/travel_policy_002.json", "w") as f:
        json.dump(policy_002, f, indent=2)

    # 干扰：旧版本政策
    old_policy = policy_001.copy()
    old_policy["version"] = "v1.0"
    old_policy["max_cost_per_booking"] = 4000
    with open("policies/old_travel_policy_001_v1.json", "w") as f:
        json.dump(old_policy, f, indent=2)

    # === raw_data 航班 ===
    os.makedirs("raw_data", exist_ok=True)
    flights = [
        # FL001 – 经济舱，2500，提前19天，合规，但不是最便宜
        {
            "flight_id": "FL001",
            "platform": "AeroCheap",
            "origin": "JFK",
            "destination": "LHR",
            "departure_date": "2026-06-20",
            "cabin_class": "economy",
            "base_price": 2200,
            "taxes": 300,
            "total_cost": 2500,
            "currency": "USD"
        },
        # FL002 – 商务舱，3000，提前17天，合规，但价格高
        {
            "flight_id": "FL002",
            "platform": "FlightPro",
            "origin": "JFK",
            "destination": "LHR",
            "departure_date": "2026-06-18",
            "cabin_class": "business",
            "base_price": 2600,
            "taxes": 400,
            "total_cost": 3000,
            "currency": "USD"
        },
        # FL003 – 经济舱，2000，提前9天 <14，违规（提前天数不足）
        {
            "flight_id": "FL003",
            "platform": "SkyBook",
            "origin": "JFK",
            "destination": "LHR",
            "departure_date": "2026-06-10",
            "cabin_class": "economy",
            "base_price": 1800,
            "taxes": 200,
            "total_cost": 2000,
            "currency": "USD"
        },
        # FL004 – 头等舱，4500，违规（舱位不允许且价格超标）
        {
            "flight_id": "FL004",
            "platform": "AeroCheap",
            "origin": "JFK",
            "destination": "LHR",
            "departure_date": "2026-06-25",
            "cabin_class": "first",
            "base_price": 4000,
            "taxes": 500,
            "total_cost": 4500,
            "currency": "USD"
        },
        # FL005 – 商务舱，3100，违规（价格超过3000）
        {
            "flight_id": "FL005",
            "platform": "CheapAir",
            "origin": "JFK",
            "destination": "LHR",
            "departure_date": "2026-06-22",
            "cabin_class": "business",
            "base_price": 2900,
            "taxes": 200,
            "total_cost": 3100,
            "currency": "USD"
        },
        # FL006 – 经济舱，2300，提前23天，最便宜且完全合规
        {
            "flight_id": "FL006",
            "platform": "SkyBook",
            "origin": "JFK",
            "destination": "LHR",
            "departure_date": "2026-06-24",
            "cabin_class": "economy",
            "base_price": 2100,
            "taxes": 200,
            "total_cost": 2300,
            "currency": "USD"
        }
    ]
    for flight in flights:
        fname = f"raw_data/{flight['flight_id']}.json"
        with open(fname, "w") as f:
            json.dump(flight, f, indent=2)

    # 干扰：非标准文件
    with open("raw_data/README.txt", "w") as f:
        f.write("These are flight search results from various platforms.")
    with open("raw_data/.DS_Store", "w") as f:
        f.write("")

    # 干扰：多余目录
    os.makedirs("ops", exist_ok=True)
    with open("ops/audit_log.txt", "w") as f:
        f.write("2026-05-31 23:59:59 INFO: Policy check triggered.\n")

if __name__ == "__main__":
    build_env()
