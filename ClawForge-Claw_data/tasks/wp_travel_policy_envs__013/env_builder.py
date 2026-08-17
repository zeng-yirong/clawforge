import os
import json
from datetime import datetime, timedelta

def build_env():
    # create directories
    os.makedirs("data/policies", exist_ok=True)
    os.makedirs("data/platforms", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("raw_flights", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # current date
    with open("current_date.txt", "w") as f:
        f.write("2026-06-06")

    # accounts (only one for simplicity, plus a decoy)
    accounts = {
        "acme-001": {"company_name": "Acme Corp", "travel_budget": 500000, "currency": "USD", "approvers": ["emily@acme.com"]},
        "acme-002": {"company_name": "Acme Corp Subsidiary", "travel_budget": 200000, "currency": "USD", "approvers": []}
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # policies – version 1.0 (old, decoy) and version 2.0 (current)
    policy_v1 = {
        "policy_id": "policy_001",
        "name": "Acme Corp Business Travel Policy",
        "version": "1.0",
        "max_cost_per_booking": 3000,
        "max_single_booking_cost": 3000,
        "allowed_cabin_classes": ["economy", "business"],
        "min_advance_booking_days": 3,
        "requires_approval_above": 2500,
        "preferred_vendors": ["AeroCheap"],
        "restricted_routes": [],
        "required_documents": ["passport"],
        "no_refund_cabin_classes": ["economy"]
    }
    policy_v2 = {
        "policy_id": "policy_002",
        "name": "Acme Corp Executive Travel Policy",
        "version": "2.0",
        "max_cost_per_booking": 2500,
        "max_single_booking_cost": 2500,
        "allowed_cabin_classes": ["business", "first"],
        "min_advance_booking_days": 7,
        "requires_approval_above": 2000,
        "preferred_vendors": ["SkyBook"],
        "restricted_routes": [],
        "required_documents": ["passport", "visa"],
        "no_refund_cabin_classes": ["business"]
    }
    with open("data/policies/policy_001.json", "w") as f:
        json.dump(policy_v1, f, indent=2)
    with open("data/policies/policy_002.json", "w") as f:
        json.dump(policy_v2, f, indent=2)

    # platforms – one active (skybook), one inactive (aerocheap), one active but no suitable flight (flightpro)
    skybook = {
        "platform_id": "skybook",
        "name": "SkyBook",
        "region": "North America",
        "is_active": True,
        "transaction_fee": 50.0,
        "service_fee": 100.0,
        "payment_methods": ["credit_card", "paypal"],
        "cancellation_policy": "flexible",
        "discounts": [],
        "promotions": [],
        "loyalty_program": {"tier": "silver", "points": 1000}
    }
    aerocheap = {
        "platform_id": "aerocheap",
        "name": "AeroCheap",
        "region": "Europe",
        "is_active": False,
        "transaction_fee": 20.0,
        "service_fee": 50.0,
        "payment_methods": ["credit_card"],
        "cancellation_policy": "non_refundable",
        "discounts": [],
        "promotions": [],
        "loyalty_program": {"tier": "none", "points": 0}
    }
    flightpro = {
        "platform_id": "flightpro",
        "name": "FlightPro",
        "region": "Asia Pacific",
        "is_active": True,
        "transaction_fee": 30.0,
        "service_fee": 80.0,
        "payment_methods": ["credit_card", "bank_transfer"],
        "cancellation_policy": "moderate",
        "discounts": [],
        "promotions": [],
        "loyalty_program": {"tier": "gold", "points": 5000}
    }
    with open("data/platforms/skybook.json", "w") as f:
        json.dump(skybook, f, indent=2)
    with open("data/platforms/aerocheap.json", "w") as f:
        json.dump(aerocheap, f, indent=2)
    with open("data/platforms/flightpro.json", "w") as f:
        json.dump(flightpro, f, indent=2)

    # raw flights – each platform gets a JSON file with a list of flights
    # SkyBook: one qualifying flight (flight-001) and one decoy (economy class, too low price but wrong cabin)
    skybook_flights = [
        {"flight_id": "flight-001", "platform_id": "skybook", "origin": "JFK", "destination": "LHR", "departure_date": "2026-06-15", "cabin_class": "business", "base_price": 2000.00},
        {"flight_id": "flight-002", "platform_id": "skybook", "origin": "JFK", "destination": "LHR", "departure_date": "2026-06-15", "cabin_class": "economy", "base_price": 1800.00}
    ]
    # AeroCheap: one flight that would be cheaper but platform is inactive
    aerocheap_flights = [
        {"flight_id": "flight-003", "platform_id": "aerocheap", "origin": "JFK", "destination": "LHR", "departure_date": "2026-06-15", "cabin_class": "business", "base_price": 1850.00}
    ]
    # FlightPro: one flight that meets cabin class but departure is too close (5 days advance, policy min is 7)
    flightpro_flights = [
        {"flight_id": "flight-004", "platform_id": "flightpro", "origin": "JFK", "destination": "LHR", "departure_date": "2026-06-10", "cabin_class": "business", "base_price": 1900.00}  # departure before June 15, advance days = 4 -> fails
    ]
    with open("raw_flights/skybook_flights.json", "w") as f:
        json.dump(skybook_flights, f, indent=2)
    with open("raw_flights/aerocheap_flights.json", "w") as f:
        json.dump(aerocheap_flights, f, indent=2)
    with open("raw_flights/flightpro_flights.json", "w") as f:
        json.dump(flightpro_flights, f, indent=2)

    # also create a decoy file in raw_flights with non-JSON content to confuse
    with open("raw_flights/note.txt", "w") as f:
        f.write("This file is not a flight data file.\n")

if __name__ == "__main__":
    build_env()
