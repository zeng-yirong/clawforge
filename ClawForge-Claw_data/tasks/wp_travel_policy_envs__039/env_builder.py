import os
import json
import random

def build_env():
    # 确保数据目录存在
    os.makedirs("data/platforms", exist_ok=True)
    os.makedirs("data/policies", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 1. 账户信息
    accounts = {
        "account_id": "acc_001",
        "company_name": "Acme Corp",
        "travel_budget": 8000,
        "currency": "USD",
        "approvers": ["alice@acme.com", "bob@acme.com"]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # 2. 差旅政策 (两个版本，只有v2是当前有效版本)
    policies = [
        {
            "policy_id": "pol_acme_business_v2",
            "name": "Acme Corp Business Travel Policy",
            "version": "2.0",
            "max_cost_per_booking": 5000,
            "max_single_booking_cost": 5000,
            "allowed_cabin_classes": ["economy", "business"],
            "min_advance_booking_days": 1,
            "requires_approval_above": 3000,
            "preferred_vendors": ["SkyBook"],
            "restricted_routes": [],
            "required_documents": ["passport"],
            "no_refund_cabin_classes": ["economy"]
        },
        {
            "policy_id": "pol_acme_business_v1",
            "name": "Acme Corp Business Travel Policy",
            "version": "1.0",
            "max_cost_per_booking": 4000,
            "max_single_booking_cost": 4000,
            "allowed_cabin_classes": ["economy"],
            "min_advance_booking_days": 2,
            "requires_approval_above": 2000,
            "preferred_vendors": ["FlightPro"],
            "restricted_routes": [],
            "required_documents": ["passport"],
            "no_refund_cabin_classes": ["economy"]
        }
    ]
    # 只保留v2为有效，v1是过期版本（干扰）
    with open("data/policies/current_policy.json", "w") as f:
        json.dump(policies[0], f, indent=2)
    with open("data/policies/old_policy.json", "w") as f:
        json.dump(policies[1], f, indent=2)

    # 3. 平台信息 (三个平台，其中一个是非活跃)
    platforms = [
        {
            "platform_id": "skybook",
            "name": "SkyBook",
            "region": "North America",
            "is_active": True,
            "transaction_fee": 50,
            "service_fee": 20,
            "payment_methods": ["credit_card", "paypal"],
            "cancellation_policy": "free 24h",
            "discounts": [],
            "promotions": [],
            "loyalty_program": {"points_per_dollar": 2}
        },
        {
            "platform_id": "flightpro",
            "name": "FlightPro",
            "region": "Europe",
            "is_active": True,
            "transaction_fee": 30,
            "service_fee": 15,
            "payment_methods": ["credit_card"],
            "cancellation_policy": "non-refundable",
            "discounts": [],
            "promotions": [],
            "loyalty_program": {"points_per_dollar": 1}
        },
        {
            "platform_id": "aerocheap",
            "name": "AeroCheap",
            "region": "Asia Pacific",
            "is_active": False,  # 非活跃平台，干扰
            "transaction_fee": 10,
            "service_fee": 5,
            "payment_methods": ["credit_card", "debit_card"],
            "cancellation_policy": "no refund",
            "discounts": [],
            "promotions": [],
            "loyalty_program": {"points_per_dollar": 3}
        }
    ]
    for p in platforms:
        with open(f"data/platforms/{p['platform_id']}.json", "w") as f:
            json.dump(p, f, indent=2)

    # 4. 每个平台的航班 (按平台ID分别存放，模拟不同数据格式)
    flights = {
        "skybook": [
            {
                "flight_id": "SB-601",
                "origin": "JFK",
                "destination": "LHR",
                "departure_date": "2026-06-15",
                "cabin_class": "business",
                "base_price": 4200,
                "currency": "USD",
                "seats_available": 2
            },
            {
                "flight_id": "SB-602",
                "origin": "JFK",
                "destination": "LHR",
                "departure_date": "2026-06-15",
                "cabin_class": "economy",
                "base_price": 1800,
                "currency": "USD",
                "seats_available": 10
            },
            {
                "flight_id": "SB-603",
                "origin": "JFK",
                "destination": "LHR",
                "departure_date": "2026-06-16",
                "cabin_class": "business",
                "base_price": 4100,
                "currency": "USD",
                "seats_available": 1
            }
        ],
        "flightpro": [
            {
                "flight_id": "FP-101",
                "origin": "JFK",
                "destination": "LHR",
                "departure_date": "2026-06-15",
                "cabin_class": "business",
                "base_price": 4800,
                "currency": "USD",
                "seats_available": 5
            },
            {
                "flight_id": "FP-102",
                "origin": "JFK",
                "destination": "LHR",
                "departure_date": "2026-06-15",
                "cabin_class": "economy",
                "base_price": 2000,
                "currency": "USD",
                "seats_available": 8
            }
        ],
        "aerocheap": [
            {
                "flight_id": "AC-001",
                "origin": "JFK",
                "destination": "LHR",
                "departure_date": "2026-06-15",
                "cabin_class": "business",
                "base_price": 3900,
                "currency": "USD",
                "seats_available": 0   # 无座位，干扰
            }
        ]
    }

    # 每个平台的航班数据写入各自子目录，模拟杂乱结构
    for plat_id, flist in flights.items():
        plat_dir = f"data/platforms/{plat_id}"
        os.makedirs(plat_dir, exist_ok=True)
        for flight in flist:
            fname = f"{flight['flight_id']}.json"
            with open(os.path.join(plat_dir, fname), "w") as f:
                json.dump(flight, f, indent=2)

    # 5. 行程请求
    trip_request = {
        "employee_id": "emp_wang",
        "name": "王总",
        "department": "Product",
        "origin": "JFK",
        "destination": "LHR",
        "departure_date": "2026-06-15",
        "cabin_class": "business",
        "passengers": 1,
        "budget_cents": 500000  # 5000 USD
    }
    with open("data/trip_request.json", "w") as f:
        json.dump(trip_request, f, indent=2)

    # 6. 额外干扰文件：一些无关的日志、旧报告
    with open("data/old_report.txt", "w") as f:
        f.write("This is an old report from Q1, ignore it.\n")
    os.makedirs("data/logs", exist_ok=True)
    with open("data/logs/audit.log", "w") as f:
        f.write("2026-05-01 12:00:00 INFO Policy v1 deprecated\n")

if __name__ == "__main__":
    build_env()
