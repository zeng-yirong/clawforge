import os
import json
import random

def build_env():
    # 基础目录
    os.makedirs("data/raw_searches", exist_ok=True)
    os.makedirs("policies", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # 用于agent输出

    # ========== 1. 有效搜索记录：SkyBook，商务舱，JFK->LHR，2026-06-15 ==========
    skybook_valid = {
        "platform": "SkyBook",
        "is_active": True,
        "search_date": "2026-06-14",
        "origin": "JFK",
        "destination": "LHR",
        "departure_date": "2026-06-15",
        "cabin_class": "business",
        "flights": [
            {
                "flight_no": "SKY101",
                "departure": "08:00",
                "arrival": "20:30",
                "base_fare": 3200.00,
                "transaction_fee": 45.00,
                "service_fee": 30.00,
                "currency": "USD",
                "seats_available": 3
            },
            {
                "flight_no": "SKY203",
                "departure": "14:00",
                "arrival": "02:30+1",
                "base_fare": 2800.00,
                "transaction_fee": 40.00,
                "service_fee": 25.00,
                "currency": "USD",
                "seats_available": 1
            }
        ]
    }
    with open("data/raw_searches/skybook_jfk_lhr_20260615.json", "w") as f:
        json.dump(skybook_valid, f, indent=2)

    # ========== 2. 有效搜索记录：AeroCheap，商务舱，JFK->LHR ==========
    aerocheap_valid = {
        "platform": "AeroCheap",
        "is_active": True,
        "search_date": "2026-06-14",
        "origin": "JFK",
        "destination": "LHR",
        "departure_date": "2026-06-15",
        "cabin_class": "business",
        "flights": [
            {
                "flight_no": "AC501",
                "departure": "10:30",
                "arrival": "22:45",
                "base_fare": 3500.00,
                "transaction_fee": 50.00,
                "service_fee": 20.00,
                "currency": "USD",
                "seats_available": 2
            }
        ]
    }
    with open("data/raw_searches/aerocheap_jfk_lhr_20260615.json", "w") as f:
        json.dump(aerocheap_valid, f, indent=2)

    # ========== 3. 无效干扰：FlightPro 已停用 ==========
    flightpro_inactive = {
        "platform": "FlightPro",
        "is_active": False,  # 停用
        "search_date": "2026-06-14",
        "origin": "JFK",
        "destination": "LHR",
        "departure_date": "2026-06-15",
        "cabin_class": "business",
        "flights": [
            {
                "flight_no": "FP777",
                "departure": "06:00",
                "arrival": "18:15",
                "base_fare": 2500.00,
                "transaction_fee": 35.00,
                "service_fee": 15.00,
                "currency": "USD",
                "seats_available": 5
            }
        ]
    }
    with open("data/raw_searches/flightpro_jfk_lhr_20260615_inactive.json", "w") as f:
        json.dump(flightpro_inactive, f, indent=2)

    # ========== 4. 干扰：其他目的地，商务舱 ==========
    others = [
        {"platform": "SkyBook", "is_active": True, "origin": "JFK", "destination": "CDG", "departure_date": "2026-06-15", "cabin_class": "business", "flights": [{"flight_no": "SKY444", "base_fare": 3000, "transaction_fee": 40, "service_fee": 20}]},
        {"platform": "AeroCheap", "is_active": True, "origin": "LAX", "destination": "LHR", "departure_date": "2026-06-15", "cabin_class": "business", "flights": [{"flight_no": "AC888", "base_fare": 3800, "transaction_fee": 55, "service_fee": 30}]},
        {"platform": "SkyBook", "is_active": True, "origin": "JFK", "destination": "LHR", "departure_date": "2026-06-16", "cabin_class": "business", "flights": [{"flight_no": "SKY666", "base_fare": 3100, "transaction_fee": 42, "service_fee": 28}]},  # 日期不对
        {"platform": "FlightPro", "is_active": True, "origin": "JFK", "destination": "LHR", "departure_date": "2026-06-15", "cabin_class": "economy", "flights": [{"flight_no": "FP123", "base_fare": 800, "transaction_fee": 10, "service_fee": 5}]}  # 舱位不对
    ]
    for i, item in enumerate(others):
        with open(f"data/raw_searches/decoys_{i}.json", "w") as f:
            json.dump(item, f, indent=2)

    # ========== 5. 政策文件（唯一有效政策） ==========
    valid_policy = {
        "policy_id": "travel_policy_business_v3",
        "name": "Acme Corp Business Travel Policy",
        "version": "3.2",
        "max_cost_per_booking": 5000,          # 单次预订最大总成本
        "max_single_booking_cost": 3500,       # 单张票最大基础票价（实际含义可忽略，但用上）
        "allowed_cabin_classes": ["economy", "premium_economy", "business"],
        "min_advance_booking_days": 1,         # 至少提前1天（今天是14日，15日出发，符合）
        "requires_approval_above": 3000,       # 超过3000需要审批
        "preferred_vendors": ["SkyBook", "AeroCheap"],
        "restricted_routes": [],
        "required_documents": ["passport"],
        "no_refund_cabin_classes": ["business"]
    }
    with open("policies/acme_business_travel_policy_v3.json", "w") as f:
        json.dump(valid_policy, f, indent=2)

    # ========== 6. 干扰政策：过时版本 ==========
    old_policy = {
        "policy_id": "travel_policy_business_v2",
        "name": "Acme Corp Business Travel Policy",
        "version": "2.0",
        "max_cost_per_booking": 4000,
        "requires_approval_above": 2500,
        "allowed_cabin_classes": ["economy", "business"],
        "min_advance_booking_days": 3,  # 更严格，但版本旧
        "preferred_vendors": ["FlightPro"]
    }
    with open("policies/old_acme_business_policy_v2.json", "w") as f:
        json.dump(old_policy, f, indent=2)

    # ========== 7. 账户信息 ==========
    accounts = {
        "account_id": "acme_corp_main",
        "company_name": "Acme Corp",
        "travel_budget": 50000,
        "currency": "USD",
        "approvers": [
            {"name": "Lucy Chen", "email": "lucy.chen@acmecorp.com", "level": "manager"},
            {"name": "John Smith", "email": "john.smith@acmecorp.com", "level": "director"}
        ]
    }
    with open("accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # ========== 8. 其他干扰文件：文本笔记、旧日志 ==========
    with open("data/note.txt", "w") as f:
        f.write("Quick note: remember to check the CEO's preferred airline (British Airways).\n")
    with open("data/old_quotes.csv", "w") as f:
        f.write("platform,origin,dest,date,fare\n")
        f.write("SkyBook,JFK,LHR,2026-05-01,2900\n")
        f.write("AeroCheap,JFK,LHR,2026-05-01,3100\n")

    print("Environment built successfully.")

if __name__ == "__main__":
    build_env()
