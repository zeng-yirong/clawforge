import json
import os
from datetime import datetime, timedelta

# Ensure we are in the correct cwd (already asset root)
# Create directories
os.makedirs("data", exist_ok=True)
os.makedirs("ops", exist_ok=True)

# --- Flights ---
base_time = datetime(2025, 8, 15, 8, 0)  # arbitrary base
flights = [
    {
        "flight_id": "F001",
        "flight_number": "AA456",
        "airline": "American Airlines",
        "origin": "ATL",
        "destination": "BOS",
        "departure_time": base_time.strftime("%Y-%m-%d %H:%M"),
        "arrival_time": (base_time + timedelta(hours=3)).strftime("%Y-%m-%d %H:%M"),
        "status": "delayed",
        "delay_minutes": 120,
        "gate": "A10"
    },
    {
        "flight_id": "F002",
        "flight_number": "DL789",
        "airline": "Delta Airlines",
        "origin": "LAX",
        "destination": "JFK",
        "departure_time": base_time.strftime("%Y-%m-%d %H:%M"),
        "arrival_time": (base_time + timedelta(hours=5)).strftime("%Y-%m-%d %H:%M"),
        "status": "on_time",
        "delay_minutes": 0,
        "gate": "B22"
    },
    {
        "flight_id": "F003",
        "flight_number": "UA123",
        "airline": "United Airlines",
        "origin": "SFO",
        "destination": "ORD",
        "departure_time": base_time.strftime("%Y-%m-%d %H:%M"),
        "arrival_time": (base_time + timedelta(hours=4)).strftime("%Y-%m-%d %H:%M"),
        "status": "on_time",
        "delay_minutes": 0,
        "gate": "C15"
    }
]
with open("data/flights.json", "w") as f:
    json.dump(flights, f, indent=2)

# --- Transports ---
# For AA456, original arrival = base+3h = 11:00. Pickup at 11:30 (30 min after).
original_arrival = base_time + timedelta(hours=3)
new_arrival = original_arrival + timedelta(minutes=120)  # 13:00
# Affected transport: pickup at 11:30 → should move to 13:30 (new arrival + 30 min)
# Another transport for same flight but well after original arrival (e.g., 14:00) is unaffected because it's after new arrival.
# Also two other flights' transports.
transports = [
    {
        "transport_id": "TR001",
        "transport_type": "limousine",
        "service_provider": "Blacklane",
        "service_area": "ATL Airport",
        "vehicle_type": "luxury",
        "base_price": 120.0,
        "next_available": "2025-08-15 11:30",
        "flight_id": "F001",
        "pickup_time": "2025-08-15 11:30"
    },
    {
        "transport_id": "TR002",
        "transport_type": "shuttle",
        "service_provider": "SuperShuttle",
        "service_area": "ATL Airport",
        "vehicle_type": "van",
        "base_price": 45.0,
        "next_available": "2025-08-15 14:00",
        "flight_id": "F001",
        "pickup_time": "2025-08-15 14:00"  # unaffected (after new arrival)
    },
    {
        "transport_id": "TR003",
        "transport_type": "suv",
        "service_provider": "Uber",
        "service_area": "JFK Airport",
        "vehicle_type": "premium",
        "base_price": 85.0,
        "next_available": "2025-08-15 12:00",
        "flight_id": "F002",  # DL789 (on time)
        "pickup_time": "2025-08-15 12:00"
    },
    {
        "transport_id": "TR004",
        "transport_type": "limousine",
        "service_provider": "Blacklane",
        "service_area": "ORD Airport",
        "vehicle_type": "luxury",
        "base_price": 135.0,
        "next_available": "2025-08-15 13:30",
        "flight_id": "F003",  # UA123 (on time)
        "pickup_time": "2025-08-15 13:30"
    }
]
with open("data/transports.json", "w") as f:
    json.dump(transports, f, indent=2)

# --- Hotels (decoration / distractor) ---
hotels = [
    {
        "hotel_id": "H001",
        "hotel_name": "Hilton Manhattan",
        "city": "New York",
        "address": "456 Fashion Ave, New York, NY 10018",
        "star_rating": 4,
        "price_per_night": 250.0,
        "available_rooms": 12,
        "amenities": ["wifi", "gym", "restaurant"],
        "flight_id": "F002"  # not affected
    },
    {
        "hotel_id": "H002",
        "hotel_name": "Marriott JFK Airport",
        "city": "New York",
        "address": "123 Airport Rd, Jamaica, NY 11430",
        "star_rating": 3,
        "price_per_night": 180.0,
        "available_rooms": 8,
        "amenities": ["wifi", "shuttle"],
        "flight_id": "F001"  # affected but we ignore hotel in this task
    },
    {
        "hotel_id": "H003",
        "hotel_name": "Westin O'Hare",
        "city": "Chicago",
        "address": "789 Transit Rd, Rosemont, IL 60018",
        "star_rating": 4,
        "price_per_night": 200.0,
        "available_rooms": 20,
        "amenities": ["wifi", "pool", "gym"],
        "flight_id": "F003"
    }
]
with open("data/hotels.json", "w") as f:
    json.dump(hotels, f, indent=2)

# --- Accounts (distractor) ---
accounts = [
    {"account_id": "ACC001", "account_name": "John Smith", "email": "john.smith@example.com", "role": "traveler", "display_name": "John"},
    {"account_id": "ACC002", "account_name": "Jane Doe", "email": "jane.doe@example.com", "role": "traveler", "display_name": "Jane"}
]
with open("data/accounts.json", "w") as f:
    json.dump(accounts, f, indent=2)

# --- Contacts (distractor) ---
contacts = [
    {"contact_id": "C001", "name": "John Smith", "email": "john.smith@example.com", "phone": "+1-555-0101"},
    {"contact_id": "C002", "name": "Jane Doe", "email": "jane.doe@example.com", "phone": "+1-555-0102"}
]
with open("data/contacts.json", "w") as f:
    json.dump(contacts, f, indent=2)

# --- Some dummy files to add noise ---
with open("ops/log.txt", "w") as f:
    f.write("This is a log file, not relevant.\n")
with open("data/notes.txt", "w") as f:
    f.write("Reminder: check all bookings.\n")
