import os
import json
from datetime import datetime, timedelta

def build_env():
    """Build initial file tree for the flight delay cascade task."""
    # ---- flights ----
    flights = [
        {
            "flight_id": "F001",
            "flight_number": "UA123",
            "airline": "United Airlines",
            "origin": "SFO",
            "destination": "ORD",
            "departure_time": "2025-03-15T14:00",
            "arrival_time": "2025-03-15T18:00",
            "status": "delayed",
            "delay_minutes": 240,
            "gate": "C15",
            "passengers": ["C001"]
        },
        {
            "flight_id": "F002",
            "flight_number": "AA456",
            "airline": "American Airlines",
            "origin": "ATL",
            "destination": "JFK",
            "departure_time": "2025-03-15T16:00",
            "arrival_time": "2025-03-15T20:00",
            "status": "on_time",
            "delay_minutes": 0,
            "gate": "A10",
            "passengers": ["C002"]
        },
        {
            "flight_id": "F003",
            "flight_number": "DL789",
            "airline": "Delta Airlines",
            "origin": "LAX",
            "destination": "BOS",
            "departure_time": "2025-03-15T12:00",
            "arrival_time": "2025-03-15T16:00",
            "status": "delayed",
            "delay_minutes": 60,
            "gate": "B22",
            "passengers": ["C003"]
        }
    ]

    # ---- hotels ----
    hotels = [
        {
            "hotel_id": "H001",
            "hotel_name": "Hilton Manhattan",
            "city": "New York",
            "address": "456 Fashion Ave, New York, NY 10018",
            "star_rating": 4,
            "price_per_night": 250.0,
            "available_rooms": 10,
            "amenities": ["wifi", "gym"],
            "guest_contact": "C001",
            "check_in_date": "2025-03-15",
            "check_out_date": "2025-03-18",
            "related_flight_id": "F001"
        },
        {
            "hotel_id": "H002",
            "hotel_name": "Marriott JFK Airport",
            "city": "New York",
            "address": "123 Airport Rd, Jamaica, NY 11430",
            "star_rating": 3,
            "price_per_night": 180.0,
            "available_rooms": 20,
            "amenities": ["wifi", "pool"],
            "guest_contact": "C002",
            "check_in_date": "2025-03-15",
            "check_out_date": "2025-03-17",
            "related_flight_id": "F002"
        },
        {
            "hotel_id": "H003",
            "hotel_name": "Westin O'Hare",
            "city": "Chicago",
            "address": "789 Transit Rd, Rosemont, IL 60018",
            "star_rating": 4,
            "price_per_night": 220.0,
            "available_rooms": 5,
            "amenities": ["wifi", "restaurant"],
            "guest_contact": "C003",
            "check_in_date": "2025-03-16",
            "check_out_date": "2025-03-19",
            "related_flight_id": "F003"
        }
    ]

    # ---- transports ----
    transports = [
        {
            "transport_id": "T001",
            "transport_type": "shuttle",
            "service_provider": "SuperShuttle",
            "service_area": "Chicago",
            "vehicle_type": "van",
            "base_price": 50.0,
            "next_available": "2025-03-15T18:30",
            "related_contact": "C001",
            "related_flight_id": "F001",
            "pickup_time": "2025-03-15T18:30"
        },
        {
            "transport_id": "T002",
            "transport_type": "limousine",
            "service_provider": "Blacklane",
            "service_area": "New York",
            "vehicle_type": "luxury",
            "base_price": 200.0,
            "next_available": "2025-03-15T20:00",
            "related_contact": "C002",
            "related_flight_id": "F002",
            "pickup_time": "2025-03-15T20:00"
        },
        {
            "transport_id": "T003",
            "transport_type": "suv",
            "service_provider": "Uber",
            "service_area": "Boston",
            "vehicle_type": "premium",
            "base_price": 150.0,
            "next_available": "2025-03-15T16:30",
            "related_contact": "C003",
            "related_flight_id": "F003",
            "pickup_time": "2025-03-15T16:30"
        }
    ]

    # ---- contacts ----
    contacts = [
        {"contact_id": "C001", "name": "John Smith", "email": "john.smith@example.com", "phone": "+1-555-0102"},
        {"contact_id": "C002", "name": "Jane Doe", "email": "jane.doe@example.com", "phone": "+1-555-0101"},
        {"contact_id": "C003", "name": "Mike Johnson", "email": "mike.johnson@example.com", "phone": "+1-555-0103"}
    ]

    # ---- write files ----
    os.makedirs("data", exist_ok=True)
    with open("data/flights.json", "w") as f:
        json.dump(flights, f, indent=2)
    with open("data/hotels.json", "w") as f:
        json.dump(hotels, f, indent=2)
    with open("data/transports.json", "w") as f:
        json.dump(transports, f, indent=2)
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

if __name__ == "__main__":
    build_env()
