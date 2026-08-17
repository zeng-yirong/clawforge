import os
import json

def build_env():
    # data/policies
    os.makedirs("data/policies", exist_ok=True)
    business_policy = {
        "policy_id": "bp_001",
        "name": "Acme Corp Business Travel Policy",
        "version": "2.0",
        "max_cost_per_booking": 5000,
        "max_single_booking_cost": 3000,
        "allowed_cabin_classes": ["business"],
        "min_advance_booking_days": 7,
        "requires_approval_above": 2000,
        "preferred_vendors": ["SkyBook"],
        "restricted_routes": [],
        "required_documents": ["passport"],
        "no_refund_cabin_classes": ["economy"]
    }
    executive_policy = {
        "policy_id": "ep_001",
        "name": "Acme Corp Executive Travel Policy",
        "version": "1.5",
        "max_cost_per_booking": 10000,
        "max_single_booking_cost": 5000,
        "allowed_cabin_classes": ["first"],
        "min_advance_booking_days": 3,
        "requires_approval_above": 4000,
        "preferred_vendors": [],
        "restricted_routes": [],
        "required_documents": ["passport", "visa"],
        "no_refund_cabin_classes": ["economy"]
    }
    with open("data/policies/business_policy.json", "w") as f:
        json.dump(business_policy, f, indent=2)
    with open("data/policies/executive_policy.json", "w") as f:
        json.dump(executive_policy, f, indent=2)

    # data/platforms
    os.makedirs("data/platforms", exist_ok=True)
    skybook = {
        "platform_id": "skybook",
        "name": "SkyBook",
        "region": "North America",
        "is_active": True,
        "transaction_fee": 10.0,
        "service_fee": 25.0,
        "payment_methods": ["credit_card", "paypal"],
        "cancellation_policy": "free before 24h",
        "discounts": [],
        "promotions": [],
        "loyalty_program": {"tier": "gold", "points": 5000},
        "flights": [
            {
                "flight_id": "SKY001",
                "origin": "JFK",
                "destination": "LHR",
                "departure_date": "2026-06-15",
                "cabin_class": "business",
                "price": 4200,
                "currency": "USD",
                "available_seats": 3
            },
            {
                "flight_id": "SKY002",
                "origin": "JFK",
                "destination": "LHR",
                "departure_date": "2026-06-15",
                "cabin_class": "economy",
                "price": 1200,
                "currency": "USD",
                "available_seats": 10
            }
        ]
    }
    aerocheap = {
        "platform_id": "aerocheap",
        "name": "AeroCheap",
        "region": "Europe",
        "is_active": True,
        "transaction_fee": 5.0,
        "service_fee": 15.0,
        "payment_methods": ["credit_card", "bank_transfer"],
        "cancellation_policy": "non-refundable",
        "discounts": [{"code": "SAVE10", "percent": 10}],
        "promotions": [],
        "loyalty_program": {"tier": "silver", "points": 2000},
        "flights": [
            {
                "flight_id": "AERO101",
                "origin": "JFK",
                "destination": "LHR",
                "departure_date": "2026-06-15",
                "cabin_class": "business",
                "price": 5500,
                "currency": "USD",
                "available_seats": 2
            },
            {
                "flight_id": "AERO102",
                "origin": "JFK",
                "destination": "LHR",
                "departure_date": "2026-06-15",
                "cabin_class": "economy",
                "price": 800,
                "currency": "USD",
                "available_seats": 5
            }
        ]
    }
    flightpro = {
        "platform_id": "flightpro",
        "name": "FlightPro",
        "region": "North America",
        "is_active": False,
        "transaction_fee": 8.0,
        "service_fee": 20.0,
        "payment_methods": ["credit_card", "apple_pay"],
        "cancellation_policy": "free within 48h",
        "discounts": [],
        "promotions": [],
        "loyalty_program": {"tier": "bronze", "points": 100},
        "flights": [
            {
                "flight_id": "FP301",
                "origin": "JFK",
                "destination": "LHR",
                "departure_date": "2026-06-15",
                "cabin_class": "business",
                "price": 3800,
                "currency": "USD",
                "available_seats": 4
            }
        ]
    }
    with open("data/platforms/skybook.json", "w") as f:
        json.dump(skybook, f, indent=2)
    with open("data/platforms/aerocheap.json", "w") as f:
        json.dump(aerocheap, f, indent=2)
    with open("data/platforms/flightpro.json", "w") as f:
        json.dump(flightpro, f, indent=2)

    # data/accounts
    os.makedirs("data", exist_ok=True)  # already exists
    accounts = {
        "account_id": "acc_alice",
        "company_name": "Acme Corp",
        "travel_budget": 8000,
        "currency": "USD",
        "approvers": ["bob@acme.com", "carol@acme.com"]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # optional: add a historical policy to increase difficulty
    os.makedirs("data/historical", exist_ok=True)
    old_business_policy = {
        "policy_id": "bp_001",
        "name": "Acme Corp Business Travel Policy",
        "version": "1.0",
        "max_cost_per_booking": 3000,
        "max_single_booking_cost": 2000,
        "allowed_cabin_classes": ["economy", "premium_economy"],
        "min_advance_booking_days": 14,
        "requires_approval_above": 1000,
        "preferred_vendors": ["FlightPro"],
        "restricted_routes": [],
        "required_documents": ["passport"],
        "no_refund_cabin_classes": ["economy"]
    }
    with open("data/historical/business_policy_v1.json", "w") as f:
        json.dump(old_business_policy, f, indent=2)

if __name__ == "__main__":
    build_env()
