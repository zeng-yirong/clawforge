import os
import json
import random
from datetime import datetime

def build_env():
    # Create output directory (agent will fill)
    os.makedirs("output", exist_ok=True)

    # --- data/platforms/ ---
    platforms_dir = "data/platforms"
    os.makedirs(platforms_dir, exist_ok=True)

    # Valid active platform: SkyBook
    skybook = {
        "platform_id": "skybook_001",
        "name": "SkyBook",
        "region": "North America",
        "is_active": True,
        "transaction_fee": 15.0,
        "service_fee": 25.0,
        "payment_methods": ["credit_card", "paypal"],
        "cancellation_policy": "free 24h",
        "discounts": [{"code": "FLY20", "percent": 20, "expires": "2026-07-01"}],
        "promotions": ["business_seasonal"],
        "loyalty_program": {"name": "Sky Miles", "tier": "silver"}
    }
    with open(os.path.join(platforms_dir, "skybook_001.json"), "w") as f:
        json.dump(skybook, f, indent=2)

    # Inactive platform: FlightPro
    flightpro = {
        "platform_id": "flightpro_002",
        "name": "FlightPro",
        "region": "Europe",
        "is_active": False,
        "transaction_fee": 20.0,
        "service_fee": 30.0,
        "payment_methods": ["credit_card", "wire"],
        "cancellation_policy": "no refund",
        "discounts": [],
        "promotions": [],
        "loyalty_program": {"name": "Pro Points", "tier": "gold"}
    }
    with open(os.path.join(platforms_dir, "flightpro_002.json"), "w") as f:
        json.dump(flightpro, f, indent=2)

    # Active but wrong cabin class (economy only): AeroCheap
    aerocheap = {
        "platform_id": "aerocheap_003",
        "name": "AeroCheap",
        "region": "Asia Pacific",
        "is_active": True,
        "transaction_fee": 5.0,
        "service_fee": 10.0,
        "payment_methods": ["debit_card"],
        "cancellation_policy": "strict",
        "discounts": [{"code": "BUDGET50", "percent": 50, "expires": "2025-12-31"}],
        "promotions": ["economy_weekend"],
        "loyalty_program": {"name": "Cheap Miles", "tier": "bronze"}
    }
    with open(os.path.join(platforms_dir, "aerocheap_003.json"), "w") as f:
        json.dump(aerocheap, f, indent=2)

    # Expired platform (old data)
    old_skybook = {
        "platform_id": "skybook_legacy",
        "name": "SkyBook (Legacy)",
        "region": "North America",
        "is_active": False,
        "transaction_fee": 10.0,
        "service_fee": 20.0,
        "payment_methods": ["credit_card"],
        "cancellation_policy": "no refund",
        "discounts": [{"code": "OLD20", "percent": 20, "expires": "2025-01-01"}],
        "promotions": [],
        "loyalty_program": {"name": "Sky Miles", "tier": "bronze"}
    }
    with open(os.path.join(platforms_dir, "skybook_legacy.json"), "w") as f:
        json.dump(old_skybook, f, indent=2)

    # --- data/policies/ ---
    policies_dir = "data/policies"
    os.makedirs(policies_dir, exist_ok=True)

    # Standard business travel policy (applicable)
    standard_policy = {
        "policy_id": "standard_travel_policy",
        "name": "Acme Corp Business Travel Policy",
        "version": "2.1",
        "max_cost_per_booking": 5000,
        "max_single_booking_cost": 5000,
        "allowed_cabin_classes": ["business", "premium_economy"],
        "min_advance_booking_days": 14,
        "requires_approval_above": 3000,
        "preferred_vendors": ["SkyBook"],
        "restricted_routes": ["JFK-LHR"],  # not restricted actually, just a data example
        "required_documents": ["passport", "visa"],
        "no_refund_cabin_classes": ["economy"]
    }
    with open(os.path.join(policies_dir, "standard_travel_policy.json"), "w") as f:
        json.dump(standard_policy, f, indent=2)

    # Executive policy (distractor)
    executive_policy = {
        "policy_id": "executive_travel_policy",
        "name": "Acme Corp Executive Travel Policy",
        "version": "1.0",
        "max_cost_per_booking": 10000,
        "max_single_booking_cost": 10000,
        "allowed_cabin_classes": ["first", "business"],
        "min_advance_booking_days": 7,
        "requires_approval_above": 5000,
        "preferred_vendors": ["FlightPro", "SkyBook"],
        "restricted_routes": [],
        "required_documents": ["passport"],
        "no_refund_cabin_classes": ["economy"]
    }
    with open(os.path.join(policies_dir, "executive_travel_policy.json"), "w") as f:
        json.dump(executive_policy, f, indent=2)

    # --- data/accounts.json ---
    accounts = {
        "acct_001": {
            "account_id": "acct_001",
            "company_name": "Acme Corp",
            "travel_budget": 10000,
            "currency": "USD",
            "approvers": ["alice@acme.com", "bob@acme.com"]
        }
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # --- data/flights/ (simulated trip data for each active platform) ---
    flights_dir = "data/flights"
    os.makedirs(flights_dir, exist_ok=True)

    # SkyBook has a business flight for 3200 USD
    skybook_flight = {
        "flight_id": "SKY20260615JFK-LHR",
        "platform_id": "skybook_001",
        "origin": "JFK",
        "destination": "LHR",
        "departure_date": "2026-06-15",
        "cabin_class": "business",
        "price": 3200,
        "currency": "USD",
        "available": True
    }
    with open(os.path.join(flights_dir, "skybook_flight.json"), "w") as f:
        json.dump(skybook_flight, f, indent=2)

    # FlightPro flight but platform is inactive -> should be ignored
    flightpro_flight = {
        "flight_id": "FP20260615JFK-LHR",
        "platform_id": "flightpro_002",
        "origin": "JFK",
        "destination": "LHR",
        "departure_date": "2026-06-15",
        "cabin_class": "business",
        "price": 4500,
        "currency": "USD",
        "available": False
    }
    with open(os.path.join(flights_dir, "flightpro_flight.json"), "w") as f:
        json.dump(flightpro_flight, f, indent=2)

    # AeroCheap flight (economy only)
    aerocheap_flight = {
        "flight_id": "AC20260615JFK-LHR",
        "platform_id": "aerocheap_003",
        "origin": "JFK",
        "destination": "LHR",
        "departure_date": "2026-06-15",
        "cabin_class": "economy",
        "price": 2800,
        "currency": "USD",
        "available": True
    }
    with open(os.path.join(flights_dir, "aerocheap_flight.json"), "w") as f:
        json.dump(aerocheap_flight, f, indent=2)

    # Additional distractor: a different route from SkyBook
    skybook_other = {
        "flight_id": "SKY20260615JFK-CDG",
        "platform_id": "skybook_001",
        "origin": "JFK",
        "destination": "CDG",
        "departure_date": "2026-06-15",
        "cabin_class": "business",
        "price": 2800,
        "currency": "USD",
        "available": True
    }
    with open(os.path.join(flights_dir, "skybook_other_flight.json"), "w") as f:
        json.dump(skybook_other, f, indent=2)

    # --- data/current_date.txt (to indicate today is 2026-06-01) ---
    with open("data/current_date.txt", "w") as f:
        f.write("2026-06-01\n")

if __name__ == "__main__":
    build_env()
