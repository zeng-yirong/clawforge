import os
import json

def build_env():
    # data/platforms/
    os.makedirs("data/platforms", exist_ok=True)
    platforms = [
        {
            "platform_id": "skybook_001",
            "name": "SkyBook",
            "region": "Europe",
            "is_active": True,
            "transaction_fee": 20.0,
            "service_fee": 30.0,
            "payment_methods": ["credit_card"],
            "cancellation_policy": "flexible",
            "discounts": [],
            "promotions": [],
            "loyalty_program": {"level": "silver"}
        },
        {
            "platform_id": "aero_cheap_002",
            "name": "AeroCheap",
            "region": "Asia Pacific",
            "is_active": True,
            "transaction_fee": 15.0,
            "service_fee": 25.0,
            "payment_methods": ["credit_card", "paypal"],
            "cancellation_policy": "non-refundable",
            "discounts": [{"type": "fixed", "amount": 0}],
            "promotions": [],
            "loyalty_program": {"level": "basic"}
        },
        {
            "platform_id": "flight_pro_003",
            "name": "FlightPro",
            "region": "North America",
            "is_active": True,
            "transaction_fee": 10.0,
            "service_fee": 20.0,
            "payment_methods": ["credit_card", "debit_card"],
            "cancellation_policy": "moderate",
            "discounts": [],
            "promotions": [],
            "loyalty_program": {"level": "gold"}
        },
        {
            "platform_id": "skybook_002",
            "name": "SkyBook (Old)",
            "region": "Europe",
            "is_active": False,
            "transaction_fee": 10.0,
            "service_fee": 15.0,
            "payment_methods": ["credit_card"],
            "cancellation_policy": "flexible",
            "discounts": [],
            "promotions": [],
            "loyalty_program": {"level": "silver"}
        }
    ]
    for p in platforms:
        with open(f"data/platforms/{p['platform_id']}.json", "w") as f:
            json.dump(p, f, indent=2)

    # data/price_comparison.json
    comparison = {
        "origin": "JFK",
        "destination": "LHR",
        "date": "2026-06-15",
        "cabin_class": "business",
        "results": [
            {"platform_id": "skybook_001", "base_price": 1100.0},
            {"platform_id": "aero_cheap_002", "base_price": 1150.0},
            {"platform_id": "flight_pro_003", "base_price": 1200.0},
            {"platform_id": "skybook_002", "base_price": 1000.0}
        ]
    }
    with open("data/price_comparison.json", "w") as f:
        json.dump(comparison, f, indent=2)

    # data/policies/
    os.makedirs("data/policies", exist_ok=True)
    policies = [
        {
            "policy_id": "travel_policy_acme_business",
            "name": "Acme Corp Business Travel Policy",
            "version": "2.0",
            "max_cost_per_booking": 2500,
            "max_single_booking_cost": 2000,
            "allowed_cabin_classes": ["business"],
            "min_advance_booking_days": 7,
            "requires_approval_above": 1500,
            "preferred_vendors": ["SkyBook"],
            "restricted_routes": [],
            "required_documents": ["passport"],
            "no_refund_cabin_classes": []
        },
        {
            "policy_id": "travel_policy_acme_executive",
            "name": "Acme Corp Executive Travel Policy",
            "version": "1.0",
            "max_cost_per_booking": 5000,
            "max_single_booking_cost": 4000,
            "allowed_cabin_classes": ["first"],
            "min_advance_booking_days": 14,
            "requires_approval_above": 3000,
            "preferred_vendors": ["FlightPro"],
            "restricted_routes": ["JFK-LHR"],
            "required_documents": ["passport", "visa"],
            "no_refund_cabin_classes": ["first"]
        }
    ]
    for pol in policies:
        fn = pol["name"].lower().replace(" ", "_").replace("acme_corp_", "") + ".json"
        with open(f"data/policies/{fn}", "w") as f:
            json.dump(pol, f, indent=2)

    # data/accounts.json
    accounts = {
        "accounts": [
            {
                "account_id": "acme_corp",
                "company_name": "Acme Corp",
                "travel_budget": 10000,
                "currency": "USD",
                "approvers": ["alice@acme.com"]
            }
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # bookings/
    os.makedirs("bookings", exist_ok=True)
    bookings = [
        {"booking_id": "B001", "platform_id": "skybook_002", "total_cost": 1500.0},
        {"booking_id": "B002", "platform_id": "aero_cheap_003", "total_cost": 500.0}
    ]
    for b in bookings:
        with open(f"bookings/{b['booking_id'].lower()}.json", "w") as f:
            json.dump(b, f, indent=2)

    # 当前日期文件（可选，用于检查提前天数）
    with open("data/current_date.txt", "w") as f:
        f.write("2026-06-01")
