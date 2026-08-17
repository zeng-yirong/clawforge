import os
import json
import datetime

def build_env():
    # 确保工作区基础目录（cwd 已经是 .）
    os.makedirs("data/flights", exist_ok=True)
    os.makedirs("data/policies", exist_ok=True)
    os.makedirs("data/platforms", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # --- policy ---
    policy = {
        "policy_id": "acme_business_2026",
        "name": "Acme Corp Business Travel Policy",
        "version": "v2.1",
        "max_cost_per_booking": 2000,
        "max_single_booking_cost": 2000,
        "allowed_cabin_classes": ["business"],
        "min_advance_booking_days": 7,
        "requires_approval_above": 1500,
        "preferred_vendors": ["SkyBook", "AeroCheap"],
        "restricted_routes": [],
        "required_documents": ["passport", "visa"],
        "no_refund_cabin_classes": ["economy"]
    }
    with open("data/policies/acme_business_2026.json", "w") as f:
        json.dump(policy, f, indent=2)

    # --- platforms ---
    platforms = [
        {
            "platform_id": "skybook",
            "name": "SkyBook",
            "region": "North America",
            "is_active": True,
            "transaction_fee": 20.0,
            "service_fee": 30.0,
            "payment_methods": ["credit_card", "paypal"],
            "cancellation_policy": "free_24h",
            "discounts": [{"code": "WELCOME10", "percent": 10}],
            "promotions": [],
            "loyalty_program": {"name": "SkyPoints", "tiers": ["Silver", "Gold", "Platinum"]}
        },
        {
            "platform_id": "aerocheap",
            "name": "AeroCheap",
            "region": "Europe",
            "is_active": True,
            "transaction_fee": 15.0,
            "service_fee": 25.0,
            "payment_methods": ["credit_card", "debit_card"],
            "cancellation_policy": "non_refundable",
            "discounts": [],
            "promotions": [{"code": "SUMMER2026", "percent": 5}],
            "loyalty_program": {"name": "AeroMiles", "tiers": ["Basic", "Premium"]}
        },
        {
            "platform_id": "flightpro",
            "name": "FlightPro",
            "region": "North America",
            "is_active": True,
            "transaction_fee": 25.0,
            "service_fee": 40.0,
            "payment_methods": ["credit_card", "bank_transfer"],
            "cancellation_policy": "partial_refund",
            "discounts": [],
            "promotions": [],
            "loyalty_program": {"name": "ProRewards", "tiers": ["Standard", "Elite"]}
        }
    ]
    for p in platforms:
        with open(f"data/platforms/{p['platform_id']}.json", "w") as f:
            json.dump(p, f, indent=2)

    # --- accounts (干扰) ---
    accounts = {
        "accounts": [
            {"account_id": "acme_corp", "company_name": "Acme Corp", "travel_budget": 50000, "currency": "USD", "approvers": ["alice@acme.com", "bob@acme.com"]}
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # --- flights (含干扰项) ---
    # 符合政策的最优解：SkyBook 商务舱 1800
    flights = [
        # 合格：SkyBook，商务舱，1800 ≤ 2000，且在优选供应商列表
        {"flight_id": "SB-20260615-001", "platform_id": "skybook", "origin": "JFK", "destination": "LHR",
         "departure_date": "2026-06-15", "cabin_class": "business", "price": 1800.0, "currency": "USD", "seats_available": 5},
        # 干扰：AeroCheap 商务舱 1950，但价格 ≤ 2000，也在优选列表，但更贵，所以不是最优解
        {"flight_id": "AC-20260615-001", "platform_id": "aerocheap", "origin": "JFK", "destination": "LHR",
         "departure_date": "2026-06-15", "cabin_class": "business", "price": 1950.0, "currency": "USD", "seats_available": 3},
        # 干扰：FlightPro 商务舱 2100，超过 max_cost_per_booking
        {"flight_id": "FP-20260615-001", "platform_id": "flightpro", "origin": "JFK", "destination": "LHR",
         "departure_date": "2026-06-15", "cabin_class": "business", "price": 2100.0, "currency": "USD", "seats_available": 7},
        # 干扰：FlightPro 经济舱 1200，舱位不在 allowed_cabin_classes 中
        {"flight_id": "FP-20260615-002", "platform_id": "flightpro", "origin": "JFK", "destination": "LHR",
         "departure_date": "2026-06-15", "cabin_class": "economy", "price": 1200.0, "currency": "USD", "seats_available": 10},
        # 干扰：过期报价（日期已过，但政策没有日期约束？我们不管，但可以通过 departure_date 提前量判断，
        # 但为了简单，这个干扰只是文件命名不同）
        {"flight_id": "OLD-20260501-001", "platform_id": "skybook", "origin": "JFK", "destination": "LHR",
         "departure_date": "2026-05-01", "cabin_class": "business", "price": 1500.0, "currency": "USD", "seats_available": 0}
    ]
    for flight in flights:
        # 用 flight_id 作为文件名
        filename = flight["flight_id"] + ".json"
        with open(f"data/flights/{filename}", "w") as f:
            json.dump(flight, f, indent=2)

    # 额外干扰：非 JSON 文件
    with open("data/flights/readme.txt", "w") as f:
        f.write("This directory contains flight quotes.\n")

    # 干扰目录
    os.makedirs("data/logs", exist_ok=True)
    with open("data/logs/server.log", "w") as f:
        f.write("2026-06-01 10:00:00 INFO Starting flight search...\n")

    print("Environment built successfully. Expected answer: flight_id = SB-20260615-001, price = 1800.0, platform = skybook")

if __name__ == "__main__":
    build_env()
