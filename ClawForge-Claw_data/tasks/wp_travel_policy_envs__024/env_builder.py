import os
import json

def build_env():
    # === 创建目录结构 ===
    os.makedirs("data/policies", exist_ok=True)
    os.makedirs("data/platforms", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # === 写入政策文件 (最新版) ===
    policy = {
        "policy_id": "acme_2026",
        "name": "Acme Corp Business Travel Policy 2026",
        "version": "2.1",
        "max_cost_per_booking": 5000,
        "max_single_booking_cost": 5000,
        "allowed_cabin_classes": ["business", "first"],
        "min_advance_booking_days": 3,
        "requires_approval_above": 4000,
        "preferred_vendors": ["FlightPro", "SkyBook"],
        "restricted_routes": [],
        "required_documents": ["passport"],
        "no_refund_cabin_classes": ["economy"]
    }
    with open("data/policies/policy.json", "w") as f:
        json.dump(policy, f, indent=2)

    # === 写入旧版政策（干扰） ===
    old_policy = {
        "policy_id": "acme_2025",
        "name": "Acme Corp Business Travel Policy 2025",
        "version": "1.0",
        "max_cost_per_booking": 3000,
        "allowed_cabin_classes": ["economy", "business"],
        "requires_approval_above": 2000
    }
    with open("data/policies/old_policy.json", "w") as f:
        json.dump(old_policy, f, indent=2)

    # === 写入平台报价 ===
    # AeroCheap 有两个航班
    aero = [
        {"flight_id": "AC101", "platform_id": "aero_cheap", "origin": "JFK", "destination": "LHR",
         "departure_date": "2026-06-15", "cabin_class": "business", "price": 4800, "currency": "USD"},
        {"flight_id": "AC202", "platform_id": "aero_cheap", "origin": "JFK", "destination": "LHR",
         "departure_date": "2026-06-15", "cabin_class": "economy", "price": 1200, "currency": "USD"}
    ]
    with open("data/platforms/aero_cheap.json", "w") as f:
        json.dump(aero, f, indent=2)

    # FlightPro 有两个航班（其中一个是最优解）
    flightpro = [
        {"flight_id": "FP303", "platform_id": "flight_pro", "origin": "JFK", "destination": "LHR",
         "departure_date": "2026-06-15", "cabin_class": "business", "price": 3200, "currency": "USD"},
        {"flight_id": "FP404", "platform_id": "flight_pro", "origin": "JFK", "destination": "LHR",
         "departure_date": "2026-06-15", "cabin_class": "first", "price": 6000, "currency": "USD"}
    ]
    with open("data/platforms/flight_pro.json", "w") as f:
        json.dump(flightpro, f, indent=2)

    # SkyBook 有两个航班
    sky = [
        {"flight_id": "SB505", "platform_id": "sky_book", "origin": "JFK", "destination": "LHR",
         "departure_date": "2026-06-15", "cabin_class": "business", "price": 3500, "currency": "USD"},
        {"flight_id": "SB606", "platform_id": "sky_book", "origin": "JFK", "destination": "LHR",
         "departure_date": "2026-06-15", "cabin_class": "economy", "price": 1000, "currency": "USD"}
    ]
    with open("data/platforms/sky_book.json", "w") as f:
        json.dump(sky, f, indent=2)

    # === 额外干扰项：账户信息（不关键，但增加复杂度） ===
    accounts = {
        "acme_corp": {
            "account_id": "acme001",
            "company_name": "Acme Corp",
            "travel_budget": 200000,
            "currency": "USD",
            "approvers": ["sarah@acme.com", "john@acme.com"]
        }
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

if __name__ == "__main__":
    build_env()
