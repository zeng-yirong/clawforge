import os
import json
import datetime

def build_env():
    # Create directory structure
    dirs = ["data/platforms", "data/policies", "data/accounts", "ops"]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # --- Platforms ---
    platforms = [
        {
            "platform_id": "AC001",
            "name": "AeroCheap",
            "region": "North America",
            "is_active": True,
            "transaction_fee": 25.00,
            "service_fee": 10.00,
            "payment_methods": ["credit_card", "paypal"],
            "cancellation_policy": "non-refundable",
            "discounts": [],
            "promotions": [],
            "loyalty_program": {"program": "AeroPoints", "tier": "Silver"},
            "price": 2800.00
        },
        {
            "platform_id": "FP002",
            "name": "FlightPro",
            "region": "Europe",
            "is_active": True,
            "transaction_fee": 30.00,
            "service_fee": 15.00,
            "payment_methods": ["credit_card", "bank_transfer"],
            "cancellation_policy": "refundable_with_fee",
            "discounts": [{"code": "EARLY10", "percent": 10}],
            "promotions": [],
            "loyalty_program": {"program": "ProMiles", "tier": "Gold"},
            "price": 3100.00
        },
        {
            "platform_id": "SB003",
            "name": "SkyBook",
            "region": "North America",
            "is_active": False,   # retired platform – should be ignored
            "transaction_fee": 20.00,
            "service_fee": 12.00,
            "payment_methods": ["credit_card"],
            "cancellation_policy": "non-refundable",
            "discounts": [],
            "promotions": [],
            "loyalty_program": {"program": "SkyRewards", "tier": "Silver"},
            "price": 2950.00
        },
        {
            "platform_id": "XZ099",
            "name": "AirElite",
            "region": "North America",
            "is_active": True,
            "transaction_fee": 40.00,
            "service_fee": 20.00,
            "payment_methods": ["credit_card", "wire"],
            "cancellation_policy": "fully_refundable",
            "discounts": [],
            "promotions": [],
            "loyalty_program": {"program": "EliteClub", "tier": "Platinum"},
            "price": 4200.00   # exceeds max_single_booking_cost but not the cheapest
        }
    ]
    for p in platforms:
        path = f"data/platforms/{p['platform_id']}.json"
        with open(path, "w") as f:
            json.dump(p, f, indent=2)

    # --- Policies ---
    # Two policy versions, only the newer one (v2) is active
    policies = [
        {
            "policy_id": "ACME_2025",
            "name": "Acme Corp Business Travel Policy",
            "version": "1.0",
            "effective_date": "2025-01-01",
            "expiry_date": "2025-12-31",
            "is_active": False,
            "max_cost_per_booking": 4000,
            "max_single_booking_cost": 3500,
            "allowed_cabin_classes": ["economy", "premium_economy"],
            "min_advance_booking_days": 7,
            "requires_approval_above": 5000,
            "preferred_vendors": ["AeroCheap"],
            "restricted_routes": [],
            "required_documents": [],
            "no_refund_cabin_classes": ["economy"]
        },
        {
            "policy_id": "ACME_2026",
            "name": "Acme Corp Business Travel Policy",
            "version": "2.1",
            "effective_date": "2026-01-01",
            "expiry_date": "2026-12-31",
            "is_active": True,
            "max_cost_per_booking": 5000,
            "max_single_booking_cost": 3000,
            "allowed_cabin_classes": ["business", "economy"],
            "min_advance_booking_days": 14,
            "requires_approval_above": 3000,
            "preferred_vendors": ["AeroCheap", "FlightPro"],
            "restricted_routes": [],
            "required_documents": [],
            "no_refund_cabin_classes": ["economy", "premium_economy"]
        }
    ]
    for pol in policies:
        path = f"data/policies/{pol['policy_id']}.json"
        with open(path, "w") as f:
            json.dump(pol, f, indent=2)

    # --- Accounts ---
    accounts = [
        {
            "account_id": "ACC001",
            "company_name": "Acme Corp",
            "travel_budget": 10000,
            "currency": "USD",
            "approvers": [
                {"name": "Sarah Chen", "email": "sarah.chen@acme.com", "role": "VP Sales"},
                {"name": "Mike Johnson", "email": "mike.j@acme.com", "role": "Finance Director"}
            ]
        }
    ]
    with open("data/accounts/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # --- Distractor files (logs, backups) ---
    os.makedirs("logs", exist_ok=True)
    with open("logs/audit_2026_05.log", "w") as f:
        f.write("INFO: No active sessions\n")
    os.makedirs("backups", exist_ok=True)
    with open("backups/policy_old.yml", "w") as f:
        f.write("policy_version: 1.0\nmax_cost: 4000\n")

if __name__ == "__main__":
    build_env()
