import os, json

def build_env():
    # accounts
    os.makedirs("ops", exist_ok=True)
    accounts = {
        "account_id": "alice_01",
        "company_name": "Acme Corp",
        "travel_budget": 2500,
        "currency": "USD",
        "approvers": ["manager@acme.com", "finance@acme.com"]
    }
    with open("accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # policies
    os.makedirs("policies", exist_ok=True)
    # latest policy (v1.0)
    policy_v1 = {
        "policy_id": "acme_biz",
        "name": "Acme Corp Business Travel Policy",
        "version": "1.0",
        "max_cost_per_booking": 2500,
        "max_single_booking_cost": 2000,
        "allowed_cabin_classes": ["business"],
        "min_advance_booking_days": 7,
        "requires_approval_above": 1300,
        "preferred_vendors": ["skybook"],
        "enforce_preferred_vendors": True,
        "restricted_routes": [],
        "required_documents": [],
        "no_refund_cabin_classes": ["economy"]
    }
    with open("policies/pol_biz_v1.json", "w") as f:
        json.dump(policy_v1, f, indent=2)

    # old policy (v0.9) – distractor, lower limits
    policy_v0 = {
        "policy_id": "acme_biz",
        "name": "Acme Corp Business Travel Policy",
        "version": "0.9",
        "max_cost_per_booking": 2000,
        "max_single_booking_cost": 1500,
        "allowed_cabin_classes": ["business"],
        "min_advance_booking_days": 14,
        "requires_approval_above": 1200,
        "preferred_vendors": ["skybook", "aerocheap"],
        "enforce_preferred_vendors": False,
        "restricted_routes": [],
        "required_documents": [],
        "no_refund_cabin_classes": ["economy"]
    }
    with open("policies/pol_biz_v0.json", "w") as f:
        json.dump(policy_v0, f, indent=2)

    # platforms
    os.makedirs("platforms", exist_ok=True)

    skybook = {
        "platform_id": "skybook",
        "name": "SkyBook",
        "region": "North America",
        "is_active": True,
        "transaction_fee": 5.0,
        "service_fee": 10.0,
        "payment_methods": ["credit_card"],
        "cancellation_policy": "flexible",
        "discounts": [],
        "promotions": [],
        "loyalty_program": {},
        "flights": [
            {
                "flight_id": "flight_sky_001",
                "origin": "JFK",
                "destination": "LHR",
                "departure_date": "2026-06-15",
                "cabin_class": "business",
                "price": 1400.00,
                "availability": 5
            }
        ]
    }
    with open("platforms/skybook.json", "w") as f:
        json.dump(skybook, f, indent=2)

    aerocheap = {
        "platform_id": "aerocheap",
        "name": "AeroCheap",
        "region": "Europe",
        "is_active": True,
        "transaction_fee": 3.0,
        "service_fee": 8.0,
        "payment_methods": ["credit_card", "paypal"],
        "cancellation_policy": "non-refundable",
        "discounts": [],
        "promotions": [],
        "loyalty_program": {},
        "flights": [
            {
                "flight_id": "flight_aero_001",
                "origin": "JFK",
                "destination": "LHR",
                "departure_date": "2026-06-15",
                "cabin_class": "business",
                "price": 1350.00,
                "availability": 3
            }
        ]
    }
    with open("platforms/aerocheap.json", "w") as f:
        json.dump(aerocheap, f, indent=2)

    flightpro = {
        "platform_id": "flightpro",
        "name": "FlightPro",
        "region": "North America",
        "is_active": False,  # inactive – should be ignored
        "transaction_fee": 7.0,
        "service_fee": 12.0,
        "payment_methods": ["credit_card"],
        "cancellation_policy": "flexible",
        "discounts": [],
        "promotions": [],
        "loyalty_program": {},
        "flights": [
            {
                "flight_id": "flight_pro_001",
                "origin": "JFK",
                "destination": "LHR",
                "departure_date": "2026-06-15",
                "cabin_class": "business",
                "price": 1200.00,
                "availability": 2
            }
        ]
    }
    with open("platforms/flightpro.json", "w") as f:
        json.dump(flightpro, f, indent=2)

if __name__ == "__main__":
    build_env()
