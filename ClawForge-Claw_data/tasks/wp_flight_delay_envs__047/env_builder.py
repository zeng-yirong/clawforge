import json
import os
import random

def build_env():
    # clean slate
    for root, dirs, files in os.walk(".", topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))

    # --- raw data directory ---
    os.makedirs("raw", exist_ok=True)

    # flights
    flights = [
        {
            "flight_id": "F001",
            "flight_number": "UA123",
            "airline": "United Airlines",
            "origin": "SFO",
            "destination": "JFK",
            "departure_time": "2025-04-10T14:00",
            "arrival_time": "2025-04-10T18:00",
            "status": "delayed",
            "delay_minutes": 120,
            "gate": "C15"
        },
        {
            "flight_id": "F002",
            "flight_number": "DL789",
            "airline": "Delta Airlines",
            "origin": "ATL",
            "destination": "ORD",
            "departure_time": "2025-04-10T15:00",
            "arrival_time": "2025-04-10T16:00",
            "status": "delayed",
            "delay_minutes": 30,
            "gate": "B22"
        },
        {
            "flight_id": "F003",
            "flight_number": "AA456",
            "airline": "American Airlines",
            "origin": "LAX",
            "destination": "BOS",
            "departure_time": "2025-04-10T12:00",
            "arrival_time": "2025-04-10T17:00",
            "status": "on_time",
            "delay_minutes": 0,
            "gate": "A10"
        }
    ]
    with open("raw/flights.json", "w") as f:
        json.dump({"flights": flights}, f, indent=2)

    # hotel_bookings
    hotel_bookings = [
        {
            "booking_id": "HB001",
            "guest_name": "John Smith",
            "flight_id": "F001",
            "hotel_id": "HIL01",
            "check_in_date": "2025-04-10",
            "check_in_time": "15:00",
            "check_out_date": "2025-04-12",
            "status": "confirmed"
        },
        {
            "booking_id": "HB002",
            "guest_name": "Jane Doe",
            "flight_id": "F002",
            "hotel_id": "MAR01",
            "check_in_date": "2025-04-10",
            "check_in_time": "16:00",
            "check_out_date": "2025-04-11",
            "status": "confirmed"
        },
        # unaffected – on-time flight
        {
            "booking_id": "HB003",
            "guest_name": "Mike Johnson",
            "flight_id": "F003",
            "hotel_id": "WES01",
            "check_in_date": "2025-04-10",
            "check_in_time": "17:00",
            "check_out_date": "2025-04-11",
            "status": "confirmed"
        },
        # cancelled booking (no effect)
        {
            "booking_id": "HB004",
            "guest_name": "Alice Brown",
            "flight_id": "F001",
            "hotel_id": "HIL01",
            "check_in_date": "2025-04-10",
            "check_in_time": "14:00",
            "check_out_date": "2025-04-13",
            "status": "cancelled"
        }
    ]
    with open("raw/hotel_bookings.json", "w") as f:
        json.dump({"bookings": hotel_bookings}, f, indent=2)

    # transport_bookings
    transport_bookings = [
        {
            "transport_booking_id": "TB001",
            "passenger_name": "John Smith",
            "flight_id": "F001",
            "service_type": "limousine",
            "pickup_time": "18:30",
            "dropoff_location": "JFK",
            "status": "confirmed"
        },
        {
            "transport_booking_id": "TB002",
            "passenger_name": "Jane Doe",
            "flight_id": "F002",
            "service_type": "shuttle",
            "pickup_time": "16:30",
            "dropoff_location": "ORD",
            "status": "confirmed"
        },
        # unaffected – different flight (F003 no delay)
        {
            "transport_booking_id": "TB003",
            "passenger_name": "Mike Johnson",
            "flight_id": "F003",
            "service_type": "suv",
            "pickup_time": "17:30",
            "dropoff_location": "BOS",
            "status": "confirmed"
        },
        # cancelled
        {
            "transport_booking_id": "TB004",
            "passenger_name": "Charlie Green",
            "flight_id": "F001",
            "service_type": "shuttle",
            "pickup_time": "18:15",
            "dropoff_location": "JFK",
            "status": "cancelled"
        }
    ]
    with open("raw/transport_bookings.json", "w") as f:
        json.dump({"bookings": transport_bookings}, f, indent=2)

    # contacts (for flavour, not required for verification)
    contacts = [
        {"contact_id": "C001", "name": "John Smith", "email": "john.smith@example.com"},
        {"contact_id": "C002", "name": "Jane Doe", "email": "jane.doe@example.com"},
        {"contact_id": "C003", "name": "Mike Johnson", "email": "mike.johnson@example.com"}
    ]
    with open("raw/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # noise file
    with open("raw/irrelevant_old_notes.txt", "w") as f:
        f.write("Don't touch this – old meeting notes.\n")

if __name__ == "__main__":
    build_env()
