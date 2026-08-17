import os
import json
import random
import itertools

def build_env():
    # 创建目录
    os.makedirs("data/platforms", exist_ok=True)
    os.makedirs("data/policies", exist_ok=True)
    os.makedirs("data/accounts", exist_ok=True)
    os.makedirs("data/flights", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # ---- 平台数据 ----
    # SkyBook: 活跃，费率 5% 交易费 + 2% 服务费
    platforms = {
        "skybook": {
            "platform_id": "skybook",
            "name": "SkyBook",
            "region": "North America",
            "is_active": True,
            "transaction_fee_rate": 0.05,
            "service_fee_rate": 0.02,
            "payment_methods": ["credit_card", "wire_transfer"],
            "cancellation_policy": "no_refund",
            "discounts": [],
            "promotions": [],
            "loyalty_program": {"tier": "silver", "points": 1500}
        },
        "aerocheap": {
            "platform_id": "aerocheap",
            "name": "AeroCheap",
            "region": "North America",
            "is_active": True,
            "transaction_fee_rate": 0.03,
            "service_fee_rate": 0.01,
            "payment_methods": ["credit_card"],
            "cancellation_policy": "24h_free",
            "discounts": [{"code": "BULK10", "percent": 10, "min_passengers": 3}],
            "promotions": [],
            "loyalty_program": {"tier": "basic", "points": 0}
        },
        "flightpro": {
            "platform_id": "flightpro",
            "name": "FlightPro",
            "region": "Europe",
            "is_active": False,  # 不活跃，应排除
            "transaction_fee_rate": 0.04,
            "service_fee_rate": 0.01,
            "payment_methods": ["credit_card"],
            "cancellation_policy": "free",
            "discounts": [],
            "promotions": [],
            "loyalty_program": {"tier": "gold", "points": 5000}
        }
    }
    for pid, data in platforms.items():
        with open(f"data/platforms/{pid}.json", "w") as f:
            json.dump(data, f)

    # ---- 政策数据 ----
    # 正版：Acme Corp Business Travel Policy v2.0
    policies = {
        "BP001": {
            "policy_id": "BP001",
            "name": "Acme Corp Business Travel Policy",
            "version": "2.0",
            "max_cost_per_booking": 8000,
            "max_single_booking_cost": 8000,
            "allowed_cabin_classes": ["economy", "business", "first"],
            "min_advance_booking_days": 3,
            "requires_approval_above": 2000,
            "preferred_vendors": ["skybook", "aerocheap"],
            "restricted_routes": [],
            "required_documents": ["passport"],
            "no_refund_cabin_classes": ["business", "first"]
        },
        "XP002": {  # 干扰：旧版本，不允许商务舱
            "policy_id": "XP002",
            "name": "Acme Corp Executive Travel Policy",
            "version": "1.0",
            "max_cost_per_booking": 12000,
            "max_single_booking_cost": 12000,
            "allowed_cabin_classes": ["first"],
            "min_advance_booking_days": 7,
            "requires_approval_above": 5000,
            "preferred_vendors": ["flightpro"],
            "restricted_routes": ["JFK-LHR"],
            "required_documents": ["passport", "visa"],
            "no_refund_cabin_classes": ["first"]
        }
    }
    for pid, data in policies.items():
        with open(f"data/policies/{pid}.json", "w") as f:
            json.dump(data, f)

    # ---- 账户数据 ----
    accounts = [
        {
            "account_id": "ACC001",
            "company_name": "Acme Corp",
            "travel_budget": 10000,
            "currency": "USD",
            "approvers": ["manager@acme.com", "director@acme.com"]
        },
        {  # 干扰：其他公司，不适用
            "account_id": "ACC002",
            "company_name": "Beta Inc",
            "travel_budget": 20000,
            "currency": "USD",
            "approvers": ["bmanager@beta.com"]
        }
    ]
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f)

    # ---- 航班报价 ----
    # 我们在搜索后得到的结果，用 JSON 列表表示每个平台的可用航班
    # 航线 JFK->LHR，日期 2026-06-15，商务舱1人
    base_flight = {
        "origin": "JFK",
        "destination": "LHR",
        "departure_date": "2026-06-15",
        "cabin_class": "business",
        "passengers": 1
    }

    # SkyBook 航班：票价7500（基础），总成本 = 7500 * (1+0.05+0.02) = 8025 → 超预算！不符合
    skybook_flights = [
        {
            "flight_id": "SK100",
            "airline": "SkyBook Airways",
            "base_price": 7500,
            "currency": "USD",
            **base_flight
        },
        {
            "flight_id": "SK200",
            "airline": "SkyBook Connect",
            "base_price": 6800,
            "currency": "USD",
            **base_flight
        }
    ]
    # AeroCheap 航班：票价7100，总成本 = 7100 * (1+0.03+0.01) = 7384，低于8000，符合
    aerocheap_flights = [
        {
            "flight_id": "AC301",
            "airline": "AeroCheap Direct",
            "base_price": 7100,
            "currency": "USD",
            **base_flight
        },
        {
            "flight_id": "AC302",
            "airline": "AeroCheap Express",
            "base_price": 6900,
            "currency": "USD",
            "cabin_class": "economy",  # 舱位不对，干扰
            **{k:v for k,v in base_flight.items() if k != "cabin_class"}
        }
    ]
    # FlightPro 不活跃，但仍有报价，应排除
    flightpro_flights = [
        {
            "flight_id": "FP001",
            "airline": "FlightPro Luxury",
            "base_price": 6200,
            "currency": "USD",
            **base_flight
        }
    ]

    # 写入 flight 结果（模拟搜索输出）
    with open("data/flights/skybook_search.json", "w") as f:
        json.dump({"platform_id":"skybook", "flights": skybook_flights}, f)
    with open("data/flights/aerocheap_search.json", "w") as f:
        json.dump({"platform_id":"aerocheap", "flights": aerocheap_flights}, f)
    with open("data/flights/flightpro_search.json", "w") as f:
        json.dump({"platform_id":"flightpro", "flights": flightpro_flights}, f)

    # 额外干扰：一个 csv 格式的过期报价（不相关）
    with open("data/flights/old_offers.csv", "w") as f:
        f.write("origin,destination,date,price\nJFK,LHR,2025-12-01,5000\n")

if __name__ == "__main__":
    build_env()
