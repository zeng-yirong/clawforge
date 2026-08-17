import os
import json
import shutil

def build_env():
    # Clean old worktree
    if os.path.exists("data"):
        shutil.rmtree("data")
    if os.path.exists("new_bookings"):
        shutil.rmtree("new_bookings")
    if os.path.exists("ops"):
        shutil.rmtree("ops")

    # --- Platforms (decoy) ---
    os.makedirs("data/platforms", exist_ok=True)
    platform_ac = {
        "platform_id": "ac_line",
        "name": "AeroCheap",
        "region": "North America",
        "is_active": True,
        "transaction_fee": 15.0,
        "service_fee": 0.0,
        "payment_methods": ["credit_card", "paypal"],
        "cancellation_policy": "non-refundable",
        "discounts": [],
        "promotions": [],
        "loyalty_program": {"level": "silver", "points": 1200}
    }
    with open("data/platforms/ac_line.json", "w") as f:
        json.dump(platform_ac, f, indent=2)

    platform_ff = {
        "platform_id": "flyfast",
        "name": "FlightPro",
        "region": "Europe",
        "is_active": False,
        "transaction_fee": 20.0,
        "service_fee": 5.0,
        "payment_methods": ["credit_card"],
        "cancellation_policy": "refundable with fee",
        "discounts": [{"code": "WELCOME10", "rate": 0.1}],
        "promotions": ["free_upgrade"],
        "loyalty_program": {"level": "gold", "points": 3400}
    }
    with open("data/platforms/flyfast.json", "w") as f:
        json.dump(platform_ff, f, indent=2)

    platform_sk = {
        "platform_id": "skybook",
        "name": "SkyBook",
        "region": "Asia Pacific",
        "is_active": True,
        "transaction_fee": 10.0,
        "service_fee": 8.0,
        "payment_methods": ["credit_card", "bank_transfer", "wechat"],
        "cancellation_policy": "full refund within 24h",
        "discounts": [{"code": "CORP20", "rate": 0.2}],
        "promotions": ["seat_selection_free"],
        "loyalty_program": {"level": "platinum", "points": 8700}
    }
    with open("data/platforms/skybook.json", "w") as f:
        json.dump(platform_sk, f, indent=2)

    # --- Policies (one old, one current) ---
    os.makedirs("data/policies", exist_ok=True)
    policy_v1 = {
        "policy_id": "acme_travel_v1",
        "name": "Acme Corp Business Travel Policy",
        "version": "1.0",
        "max_cost_per_booking": 15000,
        "max_single_booking_cost": 15000,
        "allowed_cabin_classes": ["economy", "business"],
        "min_advance_booking_days": 3,
        "requires_approval_above": 15000,
        "preferred_vendors": ["AeroCheap"],
        "restricted_routes": [["JFK", "LHR"]],
        "required_documents": ["passport"],
        "no_refund_cabin_classes": ["business"]
    }
    with open("data/policies/v1.json", "w") as f:
        json.dump(policy_v1, f, indent=2)

    policy_v2 = {
        "policy_id": "acme_travel_v2",
        "name": "Acme Corp Business Travel Policy",
        "version": "2.0",
        "max_cost_per_booking": 20000,
        "max_single_booking_cost": 20000,
        "allowed_cabin_classes": ["economy", "business"],
        "min_advance_booking_days": 5,
        "requires_approval_above": 10000,
        "preferred_vendors": ["AeroCheap", "SkyBook"],
        "restricted_routes": [["JFK", "LHR"]],
        "required_documents": ["passport", "visa"],
        "no_refund_cabin_classes": ["business"]
    }
    with open("data/policies/v2.json", "w") as f:
        json.dump(policy_v2, f, indent=2)

    # --- Account ---
    os.makedirs("data", exist_ok=True)
    account = {
        "account_id": "acme_corp",
        "company_name": "Acme Corp",
        "travel_budget": 100000,
        "currency": "USD",
        "approvers": ["jeff@acme.com", "anna@acme.com"]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(account, f, indent=2)

    # --- Bookings (one target, two decoys) ---
    os.makedirs("new_bookings", exist_ok=True)

    # Decoy A: already approved, low amount
    decoy_a = {
        "booking_id": "BK-20250315-A",
        "account_id": "acme_corp",
        "platform_id": "ac_line",
        "base_price": 7800.0,
        "taxes": 150.0,
        "fees": 50.0,
        "total_cost": 8000.0,
        "cabin_class": "economy",
        "departure_date": "2026-06-16",
        "approved": True
    }
    with open("new_bookings/booking_20250315_a.json", "w") as f:
        json.dump(decoy_a, f, indent=2)

    # Target B: business class, total 12500, needs approval per v2
    target_b = {
        "booking_id": "BK-20250315-B",
        "account_id": "acme_corp",
        "platform_id": "skybook",
        "base_price": 11000.0,
        "taxes": 1000.0,
        "fees": 500.0,
        "total_cost": 12500.0,
        "cabin_class": "business",
        "departure_date": "2026-06-14",
        "approved": False
    }
    with open("new_bookings/booking_20250315_b.json", "w") as f:
        json.dump(target_b, f, indent=2)

    # Decoy C: uses old policy (v1) and high amount, but different account
    decoy_c = {
        "booking_id": "BK-20250315-C",
        "account_id": "beta_inc",
        "platform_id": "flyfast",
        "base_price": 17000.0,
        "taxes": 800.0,
        "fees": 200.0,
        "total_cost": 18000.0,
        "cabin_class": "business",
        "departure_date": "2026-06-10",
        "approved": False
    }
    with open("new_bookings/booking_20250315_c.json", "w") as f:
        json.dump(decoy_c, f, indent=2)

    # Create empty ops directory
    os.makedirs("ops", exist_ok=True)

if __name__ == "__main__":
    build_env()
