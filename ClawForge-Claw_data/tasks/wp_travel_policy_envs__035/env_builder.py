import os
import json
import random

def build_env():
    # 创建目录结构
    os.makedirs("data/platforms", exist_ok=True)
    os.makedirs("data/policies", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # ---- 平台数据 ----
    platforms = [
        {
            "platform_id": "skybook",
            "name": "SkyBook",
            "region": "North America",
            "is_active": True,
            "transaction_fee": 50.0,
            "service_fee": 100.0,
            "payment_methods": ["credit_card", "paypal"],
            "cancellation_policy": "refundable",
            "discounts": [{"type": "percentage", "value": 0.05}],
            "promotions": [],
            "loyalty_program": {"tier": "silver", "points": 1200},
            "base_price": 4500.0
        },
        {
            "platform_id": "aerocheap",
            "name": "AeroCheap",
            "region": "Europe",
            "is_active": True,
            "transaction_fee": 45.0,
            "service_fee": 90.0,
            "payment_methods": ["credit_card"],
            "cancellation_policy": "non_refundable",
            "discounts": [],
            "promotions": [{"code": "WELCOME10", "value": 100.0}],
            "loyalty_program": {"tier": "bronze", "points": 300},
            "base_price": 4800.0
        },
        {
            "platform_id": "flightpro",
            "name": "FlightPro",
            "region": "North America",
            "is_active": False,  # 停用
            "transaction_fee": 40.0,
            "service_fee": 80.0,
            "payment_methods": ["credit_card", "bank_transfer"],
            "cancellation_policy": "refundable",
            "discounts": [{"type": "fixed", "value": 200.0}],
            "promotions": [],
            "loyalty_program": {"tier": "gold", "points": 5000},
            "base_price": 4200.0
        }
    ]
    for p in platforms:
        with open(f"data/platforms/{p['platform_id']}.json", "w") as f:
            json.dump(p, f, indent=2)

    # ---- 政策数据 ----
    policies = [
        {
            "policy_id": "acme_business_v1",
            "name": "Acme Corp Business Travel Policy",
            "version": "1.0",
            "max_cost_per_booking": 6000,
            "max_single_booking_cost": 5000,
            "allowed_cabin_classes": ["Economy", "Premium Economy", "Business"],
            "min_advance_booking_days": 3,
            "requires_approval_above": 4000,
            "preferred_vendors": ["SkyBook"],
            "restricted_routes": [],
            "required_documents": ["passport"],
            "no_refund_cabin_classes": ["Economy"]
        },
        {
            "policy_id": "acme_business_v2",
            "name": "Acme Corp Business Travel Policy",
            "version": "2.0",
            "max_cost_per_booking": 5000,
            "max_single_booking_cost": 4500,
            "allowed_cabin_classes": ["Economy", "Premium Economy", "Business"],
            "min_advance_booking_days": 5,
            "requires_approval_above": 3000,
            "preferred_vendors": ["SkyBook", "AeroCheap"],
            "restricted_routes": [],
            "required_documents": ["passport", "visa"],
            "no_refund_cabin_classes": ["Economy"]
        },
        {
            "policy_id": "acme_executive_v1",
            "name": "Acme Corp Executive Travel Policy",
            "version": "1.0",
            "max_cost_per_booking": 10000,
            "max_single_booking_cost": 8000,
            "allowed_cabin_classes": ["Business", "First"],
            "min_advance_booking_days": 1,
            "requires_approval_above": 7000,
            "preferred_vendors": ["FlightPro"],
            "restricted_routes": [],
            "required_documents": ["passport"],
            "no_refund_cabin_classes": []
        }
    ]
    for pol in policies:
        with open(f"data/policies/{pol['policy_id']}.json", "w") as f:
            json.dump(pol, f, indent=2)

    # ---- 账户数据 ----
    accounts = [
        {
            "account_id": "acme001",
            "company_name": "Acme Corp",
            "travel_budget": 100000,
            "currency": "USD",
            "approvers": ["alice@acme.com", "bob@acme.com"]
        }
    ]
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # ---- 预订请求 ----
    booking_request = {
        "origin": "JFK",
        "destination": "LHR",
        "departure_date": "2026-06-15",
        "cabin_class": "Business",
        "passengers": 1,
        "account_id": "acme001"
    }
    with open("ops/booking_request.json", "w") as f:
        json.dump(booking_request, f, indent=2)

    # ---- 干扰文件（过期的日志、临时文件） ----
    os.makedirs("logs", exist_ok=True)
    with open("logs/old_system.log", "w") as f:
        f.write("2025-12-01 10:00:00 ERROR: connection timeout\n2025-12-01 10:01:00 INFO: retry succeeded\n")
    with open("old_booking_decision_backup.json", "w") as f:
        json.dump({"platform": "flightpro", "cost": 4200, "approved": True}, f)

if __name__ == "__main__":
    build_env()
