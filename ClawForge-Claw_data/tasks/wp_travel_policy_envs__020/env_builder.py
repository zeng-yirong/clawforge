import os
import json

def build_env():
    # Create directory structure
    os.makedirs("data/policies", exist_ok=True)
    os.makedirs("data/platforms", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # Policy v1 (older, lower limit)
    policy_v1 = {
        "policy_id": "acme_business",
        "name": "Acme Corp Business Travel Policy",
        "version": "1.0",
        "max_cost_per_booking": 2500,
        "max_single_booking_cost": 2000,
        "allowed_cabin_classes": ["business"],
        "min_advance_booking_days": 7,
        "requires_approval_above": 1500,
        "preferred_vendors": ["SkyBook"],
        "restricted_routes": [],
        "required_documents": ["passport"],
        "no_refund_cabin_classes": ["economy"]
    }
    # Policy v2 (current)
    policy_v2 = {
        "policy_id": "acme_business",
        "name": "Acme Corp Business Travel Policy",
        "version": "2.0",
        "max_cost_per_booking": 3000,
        "max_single_booking_cost": 2500,
        "allowed_cabin_classes": ["business"],
        "min_advance_booking_days": 7,
        "requires_approval_above": 2000,
        "preferred_vendors": ["SkyBook", "FlightPro"],
        "restricted_routes": [],
        "required_documents": ["passport"],
        "no_refund_cabin_classes": ["economy"]
    }
    with open("data/policies/acme_business_v1.json", "w") as f:
        json.dump(policy_v1, f, indent=2)
    with open("data/policies/acme_business_v2.json", "w") as f:
        json.dump(policy_v2, f, indent=2)

    # Platform: SkyBook (compliant, cheapest)
    skybook = {
        "platform_id": "skybook",
        "name": "SkyBook",
        "region": "Europe",
        "is_active": True,
        "current_offer": {"base_fare": 1900, "taxes": 250},
        "transaction_fee": 30,
        "service_fee": 20,
        "payment_methods": ["credit_card", "paypal"],
        "cancellation_policy": "24h free cancellation",
        "discounts": [],
        "promotions": [],
        "loyalty_program": {"points": 100}
    }
    # Platform: AeroCheap (compliant but more expensive)
    aero_cheap = {
        "platform_id": "aero_cheap",
        "name": "AeroCheap",
        "region": "Europe",
        "is_active": True,
        "current_offer": {"base_fare": 2000, "taxes": 300},
        "transaction_fee": 50,
        "service_fee": 20,
        "payment_methods": ["credit_card"],
        "cancellation_policy": "non-refundable",
        "discounts": [],
        "promotions": [],
        "loyalty_program": {"points": 50}
    }
    # Platform: FlightPro (exceeds max_single_booking_cost)
    flight_pro = {
        "platform_id": "flight_pro",
        "name": "FlightPro",
        "region": "Europe",
        "is_active": True,
        "current_offer": {"base_fare": 2200, "taxes": 300},
        "transaction_fee": 40,
        "service_fee": 30,
        "payment_methods": ["credit_card", "bank_transfer"],
        "cancellation_policy": "free cancellation up to 48h",
        "discounts": [],
        "promotions": [],
        "loyalty_program": {"points": 200}
    }
    # Platform: ExpiredAir (inactive)
    expired_air = {
        "platform_id": "expired_air",
        "name": "ExpiredAir",
        "region": "Europe",
        "is_active": False,
        "current_offer": {"base_fare": 1800, "taxes": 200},
        "transaction_fee": 10,
        "service_fee": 10,
        "payment_methods": ["credit_card"],
        "cancellation_policy": "non-refundable",
        "discounts": [],
        "promotions": [],
        "loyalty_program": {"points": 0}
    }
    # Distractor: inactive budget platform
    distractor = {
        "platform_id": "bugdet_jet",
        "name": "BudgetJet",
        "region": "Asia Pacific",
        "is_active": False,
        "current_offer": {"base_fare": 1500, "taxes": 200},
        "transaction_fee": 100,
        "service_fee": 50,
        "payment_methods": ["credit_card"],
        "cancellation_policy": "non-refundable",
        "discounts": [],
        "promotions": [],
        "loyalty_program": {"points": 10}
    }
    # Write platform files
    platforms = [
        ("skybook.json", skybook),
        ("aero_cheap.json", aero_cheap),
        ("flight_pro.json", flight_pro),
        ("expired_air.json", expired_air),
        ("budget_jet_backup.json", distractor)
    ]
    for filename, data in platforms:
        with open(f"data/platforms/{filename}", "w") as f:
            json.dump(data, f, indent=2)

    # Also create an unrelated text file as noise
    with open("data/platforms/readme.txt", "w") as f:
        f.write("This directory contains platform data.\n")

    # Create a dummy ops placeholder
    with open("ops/.gitkeep", "w") as f:
        pass

if __name__ == "__main__":
    build_env()
