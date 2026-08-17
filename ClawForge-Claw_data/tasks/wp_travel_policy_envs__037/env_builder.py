import os
import json
import datetime

def build_env():
    # Ensure base directories exist
    os.makedirs("data/platforms", exist_ok=True)
    os.makedirs("data/policies", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("logs", exist_ok=True)  # distraction
    os.makedirs("backups", exist_ok=True)  # distraction

    # ===== Policy =====
    policy = {
        "policy_id": "travel_policy_001",
        "name": "Acme Corp Business Travel Policy",
        "version": "3.0",
        "max_cost_per_booking": 3000,
        "max_single_booking_cost": 3000,
        "allowed_cabin_classes": ["business"],
        "min_advance_booking_days": 7,
        "requires_approval_above": 2000,
        "preferred_vendors": ["FlightPro", "SkyBook"],
        "restricted_routes": [],
        "required_documents": ["passport"],
        "no_refund_cabin_classes": ["economy"]
    }
    with open("data/policies/travel_policy_001.json", "w") as f:
        json.dump(policy, f, indent=2)

    # ===== Platforms with flights =====
    platforms = [
        {
            "platform_id": "AC01",
            "name": "AeroCheap",
            "region": "North America",
            "is_active": True,
            "transaction_fee": 20,
            "service_fee": 10,
            "payment_methods": ["credit_card", "paypal"],
            "cancellation_policy": "non-refundable",
            "discounts": [],
            "promotions": [],
            "loyalty_program": {},
            "flights": [
                {"flight_id": "flight_ac101", "origin": "JFK", "destination": "LHR",
                 "departure_date": "2026-06-15", "cabin_class": "economy", "price": 1500},
                {"flight_id": "flight_ac102", "origin": "JFK", "destination": "LHR",
                 "departure_date": "2026-06-15", "cabin_class": "economy", "price": 1400}  # no business class
            ]
        },
        {
            "platform_id": "FP01",
            "name": "FlightPro",
            "region": "North America",
            "is_active": True,
            "transaction_fee": 30,
            "service_fee": 15,
            "payment_methods": ["credit_card", "bank_transfer"],
            "cancellation_policy": "refundable with fee",
            "discounts": [{"type": "corporate", "value": 50}],
            "promotions": [],
            "loyalty_program": {"tier": "silver", "points": 0},
            "flights": [
                {"flight_id": "flight_fp201", "origin": "JFK", "destination": "LHR",
                 "departure_date": "2026-06-15", "cabin_class": "business", "price": 2200},
                {"flight_id": "flight_fp202", "origin": "JFK", "destination": "LHR",
                 "departure_date": "2026-06-15", "cabin_class": "economy", "price": 1800}
            ]
        },
        {
            "platform_id": "SB01",
            "name": "SkyBook",
            "region": "North America",
            "is_active": True,
            "transaction_fee": 25,
            "service_fee": 20,
            "payment_methods": ["credit_card", "apple_pay"],
            "cancellation_policy": "fully refundable within 24h",
            "discounts": [],
            "promotions": [{"code": "SUMMER2026", "discount": 100, "eligible_platforms": ["SkyBook"]}],
            "loyalty_program": {"tier": "gold", "points": 5000},
            "flights": [
                {"flight_id": "flight_sb301", "origin": "JFK", "destination": "LHR",
                 "departure_date": "2026-06-15", "cabin_class": "business", "price": 2100},
                {"flight_id": "flight_sb302", "origin": "JFK", "destination": "LHR",
                 "departure_date": "2026-06-15", "cabin_class": "economy", "price": 1600}
            ]
        },
        {
            "platform_id": "OA99",
            "name": "OldAir",
            "region": "Europe",
            "is_active": False,
            "transaction_fee": 10,
            "service_fee": 5,
            "payment_methods": ["credit_card"],
            "cancellation_policy": "non-refundable",
            "discounts": [],
            "promotions": [],
            "loyalty_program": {},
            "flights": [
                {"flight_id": "flight_oa901", "origin": "JFK", "destination": "LHR",
                 "departure_date": "2026-06-15", "cabin_class": "business", "price": 1900}
            ]
        }
    ]
    for p in platforms:
        with open(f"data/platforms/{p['platform_id']}.json", "w") as f:
            json.dump(p, f, indent=2)

    # ===== Accounts =====
    accounts = [
        {
            "account_id": "ACC-ACME-001",
            "company_name": "Acme Corp",
            "travel_budget": 50000,
            "currency": "USD",
            "approvers": [
                {"name": "John Doe", "email": "john.doe@acme.com", "role": "Travel Manager"},
                {"name": "Jane Smith", "email": "jane.smith@acme.com", "role": "Finance Director"}
            ]
        }
    ]
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # ===== Distractions =====
    # Old log files
    with open("logs/audit_2025.log", "w") as f:
        f.write("2025-12-01 10:00:00 INFO Booking completed\n")
    with open("backups/accounts_old.json", "w") as f:
        json.dump([{"account_id": "OLD", "company_name": "Old Corp", "travel_budget": 0, "currency": "USD", "approvers": []}], f)

if __name__ == "__main__":
    build_env()
