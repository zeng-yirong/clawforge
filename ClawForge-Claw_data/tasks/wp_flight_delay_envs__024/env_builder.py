import json
import os
from datetime import datetime, timedelta

def build_env():
    # Ensure base directories exist
    os.makedirs("data/flights", exist_ok=True)
    os.makedirs("data/hotels", exist_ok=True)  # used as placeholder, not required for task
    os.makedirs("data/transports", exist_ok=True)  # used as placeholder

    # Flights
    flights = [
        {
            "flight_id": "FL001",
            "flight_number": "UA123",
            "airline": "United",
            "origin": "SFO",
            "destination": "JFK",
            "departure_time": "2025-04-15T16:00:00",
            "arrival_time": "2025-04-15T18:00:00",
            "status": "delayed",
            "delay_minutes": 120,
            "gate": "A10"
        },
        {
            "flight_id": "FL002",
            "flight_number": "DL789",
            "airline": "Delta",
            "origin": "ATL",
            "destination": "ORD",
            "departure_time": "2025-04-15T14:00:00",
            "arrival_time": "2025-04-15T16:00:00",
            "status": "delayed",
            "delay_minutes": 10,
            "gate": "B22"
        },
        {
            "flight_id": "FL003",
            "flight_number": "AA456",
            "airline": "American",
            "origin": "LAX",
            "destination": "BOS",
            "departure_time": "2025-04-15T20:00:00",
            "arrival_time": "2025-04-15T23:00:00",
            "status": "on_time",
            "delay_minutes": 0,
            "gate": "C15"
        }
    ]
    with open("data/flights/flights.json", "w") as f:
        json.dump(flights, f, indent=2)

    # Hotel bookings (separate file, since hotels.json in schema is just hotel info)
    hotel_bookings = [
        {
            "booking_id": "HB001",
            "flight_id": "FL001",
            "hotel_id": "HTL01",
            "checkin_datetime": "2025-04-15T18:00:00",
            "checkout_datetime": "2025-04-16T10:00:00",
            "guest_name": "John Doe",
            "status": "confirmed"
        },
        {
            "booking_id": "HB002",
            "flight_id": "FL002",
            "hotel_id": "HTL02",
            "checkin_datetime": "2025-04-15T16:00:00",
            "checkout_datetime": "2025-04-16T10:00:00",
            "guest_name": "Jane Smith",
            "status": "confirmed"
        },
        {
            "booking_id": "HB003",
            "flight_id": "FL001",
            "hotel_id": "HTL03",
            "checkin_datetime": "2025-04-15T18:00:00",
            "checkout_datetime": "2025-04-16T10:00:00",
            "guest_name": "Bob",
            "status": "cancelled"
        }
    ]
    with open("data/hotel_bookings.json", "w") as f:
        json.dump(hotel_bookings, f, indent=2)

    # Transport bookings
    transport_bookings = [
        {
            "booking_id": "TB001",
            "flight_id": "FL001",
            "transport_type": "limousine",
            "pickup_datetime": "2025-04-15T18:30:00",
            "dropoff_location": "Manhattan",
            "guest_name": "John Doe",
            "status": "confirmed"
        },
        {
            "booking_id": "TB002",
            "flight_id": "FL002",
            "transport_type": "shuttle",
            "pickup_datetime": "2025-04-15T16:30:00",
            "dropoff_location": "Chicago",
            "guest_name": "Jane Smith",
            "status": "confirmed"
        },
        {
            "booking_id": "TB003",
            "flight_id": "FL003",
            "transport_type": "suv",
            "pickup_datetime": "2025-04-15T23:30:00",
            "dropoff_location": "Boston",
            "guest_name": "Alice",
            "status": "confirmed"
        }
    ]
    with open("data/transport_bookings.json", "w") as f:
        json.dump(transport_bookings, f, indent=2)

    # Add a few irrelevant files as distractors
    os.makedirs("data/old_records", exist_ok=True)
    with open("data/old_records/backup_flights.json", "w") as f:
        json.dump([], f)
    with open("data/notes.txt", "w") as f:
        f.write("These are raw feeds from yesterday. Use them as is.\n")

if __name__ == "__main__":
    build_env()
