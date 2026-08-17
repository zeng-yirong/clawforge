import os
import json
import datetime

def build_env():
    # 创建目录
    for d in ["data/policies", "data/platforms", "data/bookings", "ops"]:
        os.makedirs(d, exist_ok=True)

    # 政策文件 - 两个版本: v1 (旧), v2 (新)
    policy_v1 = {
        "policy_id": "acme_business_policy_v1",
        "name": "Acme Corp Business Travel Policy",
        "version": "1.0",
        "max_cost_per_booking": 2500,
        "max_single_booking_cost": 2500,
        "allowed_cabin_classes": ["economy", "business", "first"],
        "min_advance_booking_days": 3,
        "requires_approval_above": 2000,
        "preferred_vendors": ["SkyBook", "FlightPro"],
        "restricted_routes": [],
        "required_documents": [],
        "no_refund_cabin_classes": ["first"]
    }
    policy_v2 = {
        "policy_id": "acme_business_policy_v2",
        "name": "Acme Corp Business Travel Policy",
        "version": "2.0",
        "max_cost_per_booking": 2000,
        "max_single_booking_cost": 2000,
        "allowed_cabin_classes": ["economy", "business"],
        "min_advance_booking_days": 7,
        "requires_approval_above": 1500,
        "preferred_vendors": ["SkyBook"],
        "restricted_routes": ["JFK-LHR"],
        "required_documents": ["passport", "visa"],
        "no_refund_cabin_classes": ["business"]
    }
    # Executive政策 - 干扰
    policy_exec = {
        "policy_id": "acme_exec_policy_v1",
        "name": "Acme Corp Executive Travel Policy",
        "version": "1.0",
        "max_cost_per_booking": 5000,
        "max_single_booking_cost": 5000,
        "allowed_cabin_classes": ["business", "first"],
        "min_advance_booking_days": 1,
        "requires_approval_above": 3000,
        "preferred_vendors": ["AeroCheap", "SkyBook"],
        "restricted_routes": [],
        "required_documents": ["passport"],
        "no_refund_cabin_classes": ["first"]
    }
    with open("data/policies/acme_business_v1.json", "w") as f:
        json.dump(policy_v1, f, indent=2)
    with open("data/policies/acme_business_v2.json", "w") as f:
        json.dump(policy_v2, f, indent=2)
    with open("data/policies/executive_v1.json", "w") as f:
        json.dump(policy_exec, f, indent=2)

    # 平台文件 - 提供三个平台，其中一个不活跃作为诱饵
    platforms = {
        "skybook": {
            "platform_id": "skybook",
            "name": "SkyBook",
            "region": "North America",
            "is_active": True,
            "transaction_fee": 15.0,
            "service_fee": 10.0,
            "payment_methods": ["credit_card", "invoice"],
            "cancellation_policy": "free within 24h",
            "discounts": [{"code": "CORP10", "percent": 10}],
            "promotions": [],
            "loyalty_program": {"tier": "gold", "points": 5000}
        },
        "flightpro": {
            "platform_id": "flightpro",
            "name": "FlightPro",
            "region": "Europe",
            "is_active": True,
            "transaction_fee": 20.0,
            "service_fee": 5.0,
            "payment_methods": ["credit_card"],
            "cancellation_policy": "non-refundable after booking",
            "discounts": [],
            "promotions": [{"code": "WINTER20", "percent": 20}],
            "loyalty_program": {"tier": "silver", "points": 1200}
        },
        "aerocheap": {
            "platform_id": "aerocheap",
            "name": "AeroCheap",
            "region": "Asia Pacific",
            "is_active": False,
            "transaction_fee": 5.0,
            "service_fee": 2.0,
            "payment_methods": ["credit_card", "paypal"],
            "cancellation_policy": "no cancellations",
            "discounts": [],
            "promotions": [],
            "loyalty_program": {"tier": "bronze", "points": 200}
        }
    }
    for pid, pdata in platforms.items():
        with open(f"data/platforms/{pid}.json", "w") as f:
            json.dump(pdata, f, indent=2)

    # 预订记录 - 共7条，其中3条违规（根据v2），4条合规
    bookings = [
        {
            "booking_id": "BK-001",
            "platform_id": "skybook",
            "route": "JFK-LHR",
            "cabin_class": "business",
            "total_cost": 1800,
            "booking_date": "2026-05-10",
            "passenger": "Alice"
        },
        {
            "booking_id": "BK-002",
            "platform_id": "flightpro",
            "route": "LHR-CDG",
            "cabin_class": "economy",
            "total_cost": 350,
            "booking_date": "2026-05-12",
            "passenger": "Bob"
        },
        {
            "booking_id": "BK-003",  # 违规：成本2500 > 2000
            "platform_id": "skybook",
            "route": "JFK-LHR",
            "cabin_class": "business",
            "total_cost": 2500,
            "booking_date": "2026-05-15",
            "passenger": "Charlie"
        },
        {
            "booking_id": "BK-004",  # 违规：first class不允许
            "platform_id": "flightpro",
            "route": "CDG-JFK",
            "cabin_class": "first",
            "total_cost": 4000,
            "booking_date": "2026-05-18",
            "passenger": "Diana"
        },
        {
            "booking_id": "BK-005",
            "platform_id": "skybook",
            "route": "JFK-LHR",
            "cabin_class": "economy",
            "total_cost": 500,
            "booking_date": "2026-05-20",
            "passenger": "Eve"
        },
        {
            "booking_id": "BK-006",  # 违规：成本2100 > 2000
            "platform_id": "skybook",
            "route": "LHR-JFK",
            "cabin_class": "business",
            "total_cost": 2100,
            "booking_date": "2026-05-22",
            "passenger": "Frank"
        },
        {
            "booking_id": "BK-007",
            "platform_id": "flightpro",
            "route": "JFK-CDG",
            "cabin_class": "business",
            "total_cost": 1900,
            "booking_date": "2026-05-25",
            "passenger": "Grace"
        }
    ]
    with open("data/bookings/records.json", "w") as f:
        json.dump(bookings, f, indent=2)

    # 额外干扰：一个格式错误的文本文件
    with open("data/bookings/old_export.csv", "w") as f:
        f.write("booking_id,cost\nBK-099,3000\n")

if __name__ == "__main__":
    build_env()
