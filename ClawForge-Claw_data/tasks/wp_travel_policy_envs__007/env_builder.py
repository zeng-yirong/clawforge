import os
import json
import datetime

def build_env():
    # ---- dirs ----
    os.makedirs("data/platforms", exist_ok=True)
    os.makedirs("data/policies", exist_ok=True)
    os.makedirs("data/flights", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # ---- current date ----
    with open("data/current_date.txt", "w") as f:
        f.write("2026-06-12")

    # ---- platforms ----
    platforms = {
        "skybook": {
            "platform_id": "skybook",
            "name": "SkyBook",
            "region": "North America",
            "is_active": True,
            "transaction_fee": 20,
            "service_fee": 30,
            "payment_methods": ["credit_card", "paypal"],
            "cancellation_policy": "refundable",
            "discounts": [],
            "promotions": [],
            "loyalty_program": {"name": "SkyMiles", "tier": "Silver"}
        },
        "aerocheap": {
            "platform_id": "aerocheap",
            "name": "AeroCheap",
            "region": "Europe",
            "is_active": True,
            "transaction_fee": 10,
            "service_fee": 25,
            "payment_methods": ["credit_card"],
            "cancellation_policy": "non-refundable",
            "discounts": [],
            "promotions": [],
            "loyalty_program": {"name": "AeroPoints", "tier": "Gold"}
        },
        "flightpro": {
            "platform_id": "flightpro",
            "name": "FlightPro",
            "region": "Asia Pacific",
            "is_active": False,
            "transaction_fee": 15,
            "service_fee": 40,
            "payment_methods": ["credit_card", "bank_transfer"],
            "cancellation_policy": "refundable",
            "discounts": [],
            "promotions": [],
            "loyalty_program": {"name": "ProRewards", "tier": "Platinum"}
        }
    }
    for pid, data in platforms.items():
        with open(f"data/platforms/{pid}.json", "w") as f:
            json.dump(data, f, indent=2)

    # ---- policies ----
    policies = {
        "acme_corp_business_travel_policy_v2": {
            "policy_id": "acme_corp_business_travel_policy_v2",
            "name": "Acme Corp Business Travel Policy",
            "version": "2.0",
            "max_cost_per_booking": 1500,
            "max_single_booking_cost": 1200,
            "allowed_cabin_classes": ["business", "economy"],
            "min_advance_booking_days": 3,
            "requires_approval_above": 1000,
            "preferred_vendors": ["SkyBook"],
            "restricted_routes": [],
            "required_documents": ["passport"],
            "no_refund_cabin_classes": ["economy"]
        },
        "acme_corp_executive_travel_policy_v1": {
            "policy_id": "acme_corp_executive_travel_policy_v1",
            "name": "Acme Corp Executive Travel Policy",
            "version": "1.0",
            "max_cost_per_booking": 3000,
            "max_single_booking_cost": 2500,
            "allowed_cabin_classes": ["first", "business"],
            "min_advance_booking_days": 1,
            "requires_approval_above": 2000,
            "preferred_vendors": ["FlightPro"],
            "restricted_routes": [],
            "required_documents": ["passport", "visa"],
            "no_refund_cabin_classes": ["economy"]
        }
    }
    for pid, data in policies.items():
        with open(f"data/policies/{pid}.json", "w") as f:
            json.dump(data, f, indent=2)

    # ---- accounts ----
    accounts = {
        "acme_corp": {
            "account_id": "acme_corp",
            "company_name": "Acme Corp",
            "travel_budget": 5000,
            "currency": "USD",
            "approvers": [
                {"name": "Alice Johnson", "email": "alice@acme.com"},
                {"name": "Bob Smith", "email": "bob@acme.com"}
            ]
        }
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # ---- flights ----
    flights_skybook = [
        {
            "flight_id": "SB101",
            "platform_id": "skybook",
            "origin": "JFK",
            "destination": "LHR",
            "departure_date": "2026-06-15",
            "cabin_class": "business",
            "base_price": 1100,
            "available": True,
            "stops": 0,
            "flight_time_hours": 7
        },
        {
            "flight_id": "SB102",
            "platform_id": "skybook",
            "origin": "JFK",
            "destination": "LHR",
            "departure_date": "2026-06-15",
            "cabin_class": "economy",
            "base_price": 650,
            "available": True,
            "stops": 0,
            "flight_time_hours": 7
        },
        {
            "flight_id": "SB103",
            "platform_id": "skybook",
            "origin": "JFK",
            "destination": "LHR",
            "departure_date": "2026-06-14",
            "cabin_class": "business",
            "base_price": 1200,
            "available": True,
            "stops": 0,
            "flight_time_hours": 7
        }
    ]
    with open("data/flights/skybook_flights.json", "w") as f:
        json.dump(flights_skybook, f, indent=2)

    flights_aerocheap = [
        {
            "flight_id": "AC201",
            "platform_id": "aerocheap",
            "origin": "JFK",
            "destination": "LHR",
            "departure_date": "2026-06-13",
            "cabin_class": "business",
            "base_price": 1200,
            "available": True,
            "stops": 0,
            "flight_time_hours": 7
        },
        {
            "flight_id": "AC202",
            "platform_id": "aerocheap",
            "origin": "JFK",
            "destination": "LHR",
            "departure_date": "2026-06-15",
            "cabin_class": "economy",
            "base_price": 700,
            "available": True,
            "stops": 0,
            "flight_time_hours": 8
        }
    ]
    with open("data/flights/aerocheap_flights.json", "w") as f:
        json.dump(flights_aerocheap, f, indent=2)

    flights_flightpro = [
        {
            "flight_id": "FP301",
            "platform_id": "flightpro",
            "origin": "JFK",
            "destination": "LHR",
            "departure_date": "2026-06-15",
            "cabin_class": "business",
            "base_price": 1000,
            "available": True,
            "stops": 0,
            "flight_time_hours": 6
        }
    ]
    with open("data/flights/flightpro_flights.json", "w") as f:
        json.dump(flights_flightpro, f, indent=2)

if __name__ == "__main__":
    build_env()
