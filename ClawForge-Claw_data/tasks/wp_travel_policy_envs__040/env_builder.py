import json
import os

def build_env():
    # 创建目录结构
    os.makedirs("data/platforms", exist_ok=True)
    os.makedirs("data/policies", exist_ok=True)
    # ops 目录暂时不创建，让 agent 创建

    # 1. 出差请求
    trip_request = {
        "employee": "Bob",
        "origin": "JFK",
        "destination": "LHR",
        "departure_date": "2026-06-15",
        "cabin_class": "business",
        "passengers": 1
    }
    with open("data/trip_request.json", "w") as f:
        json.dump(trip_request, f, indent=2)

    # 2. 账户信息
    accounts = [
        {
            "account_id": "acme_corp",
            "company_name": "Acme Corp",
            "travel_budget": 500000,
            "currency": "USD",
            "approvers": ["Carol (CFO)", "Dave (VP Finance)"]
        },
        {
            "account_id": "bobs_account",
            "company_name": "Acme Corp",
            "travel_budget": 10000,
            "currency": "USD",
            "approvers": []
        }
    ]
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # 3. 政策文件
    policies = [
        {
            "policy_id": "biz_travel",
            "name": "Acme Corp Business Travel Policy",
            "version": "v2.1",
            "max_cost_per_booking": 3000,
            "max_single_booking_cost": 3000,
            "allowed_cabin_classes": ["economy", "business"],
            "min_advance_booking_days": 3,
            "requires_approval_above": 2000,
            "preferred_vendors": ["AeroCheap", "SkyBook"],
            "restricted_routes": [],
            "required_documents": ["passport"],
            "no_refund_cabin_classes": ["business"]
        },
        {
            "policy_id": "exec_travel",
            "name": "Acme Corp Executive Travel Policy",
            "version": "v1.0",
            "max_cost_per_booking": 5000,
            "max_single_booking_cost": 5000,
            "allowed_cabin_classes": ["first", "business"],
            "min_advance_booking_days": 1,
            "requires_approval_above": 4000,
            "preferred_vendors": ["FlightPro"],
            "restricted_routes": [],
            "required_documents": ["visa"],
            "no_refund_cabin_classes": []
        }
    ]
    for i, pol in enumerate(policies):
        with open(f"data/policies/policy_{i+1}.json", "w") as f:
            json.dump(pol, f, indent=2)

    # 4. 平台航班数据（每个平台一个文件）
    # 设计唯一的正确答案：AeroCheap 的 AC-102 商务舱 2350 美元 + 交易费50 + 服务费50 = 2450 美元，符合政策(<=3000)，需审批(>2000)。
    # 干扰项：其他平台有更低的商务舱但超出政策max_cost? 或者有更便宜的经济舱，或座位不足。
    platforms = {
        "AeroCheap": {
            "platform_id": "aero_cheap",
            "name": "AeroCheap",
            "region": "North America",
            "is_active": True,
            "transaction_fee": 50.0,
            "service_fee": 50.0,
            "payment_methods": ["credit_card", "paypal"],
            "cancellation_policy": "non-refundable",
            "discounts": [],
            "promotions": [],
            "loyalty_program": {"tier": "silver", "points": 1000},
            "flights": [
                {"flight_id": "AC-101", "airline": "AeroJet", "departure_time": "08:00", "price": 1800.0, "cabin": "economy", "seats_available": 5},
                {"flight_id": "AC-102", "airline": "AeroJet", "departure_time": "14:30", "price": 2350.0, "cabin": "business", "seats_available": 2},
                {"flight_id": "AC-103", "airline": "AeroJet", "departure_time": "20:00", "price": 2600.0, "cabin": "business", "seats_available": 0}
            ]
        },
        "FlightPro": {
            "platform_id": "flight_pro",
            "name": "FlightPro",
            "region": "Europe",
            "is_active": True,
            "transaction_fee": 75.0,
            "service_fee": 25.0,
            "payment_methods": ["bank_transfer"],
            "cancellation_policy": "refundable_with_fee",
            "discounts": [{"code": "WELCOME10", "percent": 10}],
            "promotions": [],
            "loyalty_program": {"tier": "gold", "points": 5000},
            "flights": [
                {"flight_id": "FP-201", "airline": "EuroWings", "departure_time": "09:15", "price": 2200.0, "cabin": "business", "seats_available": 1},
                {"flight_id": "FP-202", "airline": "EuroWings", "departure_time": "16:45", "price": 2450.0, "cabin": "business", "seats_available": 0}
            ]
        },
        "SkyBook": {
            "platform_id": "sky_book",
            "name": "SkyBook",
            "region": "North America",
            "is_active": True,
            "transaction_fee": 30.0,
            "service_fee": 20.0,
            "payment_methods": ["credit_card", "debit_card", "crypto"],
            "cancellation_policy": "non-refundable",
            "discounts": [],
            "promotions": [{"code": "FLASH50", "discount_flat": 50}],
            "loyalty_program": {"tier": "platinum", "points": 20000},
            "flights": [
                {"flight_id": "SB-301", "airline": "SkyHigh", "departure_time": "07:30", "price": 1999.0, "cabin": "economy", "seats_available": 3},
                {"flight_id": "SB-302", "airline": "SkyHigh", "departure_time": "12:00", "price": 2500.0, "cabin": "business", "seats_available": 4}
            ]
        }
    }
    for platform_name, data in platforms.items():
        filename = f"data/platforms/{platform_name.lower()}.json"
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)

    # 5. 额外干扰文件（非 JSON，诱饵）
    with open("data/platforms/note.txt", "w") as f:
        f.write("This is a note, ignore.")
    with open("data/policies/old_policy.txt", "w") as f:
        f.write("This is an outdated policy draft.")

if __name__ == "__main__":
    build_env()
