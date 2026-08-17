import os
import json
import random

def build_env():
    # Create directories
    os.makedirs("flights", exist_ok=True)
    os.makedirs("hotels", exist_ok=True)
    os.makedirs("transports", exist_ok=True)
    os.makedirs("contacts", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # --- Flights ---
    # Main delayed flight
    flights = [
        {
            "flight_id": "F001",
            "flight_number": "UA123",
            "airline": "United Airlines",
            "origin": "SFO",
            "destination": "ORD",
            "departure_time": "2025-03-15 10:00",
            "arrival_time": "2025-03-15 16:00",
            "status": "delayed",
            "delay_minutes": 120,
            "gate": "C15"
        },
        # Distractor flight (also delayed but no downstream bookings)
        {
            "flight_id": "F002",
            "flight_number": "DL789",
            "airline": "Delta Airlines",
            "origin": "ATL",
            "destination": "JFK",
            "departure_time": "2025-03-15 14:00",
            "arrival_time": "2025-03-15 17:00",
            "status": "delayed",
            "delay_minutes": 45,
            "gate": "A10"
        },
        # On-time flight (no issues)
        {
            "flight_id": "F003",
            "flight_number": "AA456",
            "airline": "American Airlines",
            "origin": "LAX",
            "destination": "BOS",
            "departure_time": "2025-03-15 18:00",
            "arrival_time": "2025-03-16 02:00",
            "status": "on_time",
            "delay_minutes": 0,
            "gate": "B22"
        }
    ]
    with open("flights/flights.json", "w") as f:
        json.dump({"flights": flights}, f, indent=2)

    # --- Contacts ---
    contacts = [
        {
            "contact_id": "C001",
            "name": "John Smith",
            "email": "john.smith@example.com",
            "phone": "+1-555-0102"
        },
        {
            "contact_id": "C002",
            "name": "Jane Doe",
            "email": "jane.doe@example.com",
            "phone": "+1-555-0101"
        },
        {
            "contact_id": "C003",
            "name": "Mike Johnson",
            "email": "mike.johnson@example.com",
            "phone": "+1-555-0103"
        }
    ]
    with open("contacts/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # --- Hotels ---
    hotels = [
        {
            "hotel_id": "H001",
            "hotel_name": "Hilton Manhattan",
            "city": "New York",
            "address": "456 Fashion Ave, New York, NY 10018",
            "star_rating": 4,
            "price_per_night": 250.0,
            "available_rooms": 15,
            "amenities": ["WiFi", "Gym", "Restaurant"]
        },
        {
            "hotel_id": "H002",
            "hotel_name": "Marriott JFK Airport",
            "city": "New York",
            "address": "123 Airport Rd, Jamaica, NY 11430",
            "star_rating": 3,
            "price_per_night": 180.0,
            "available_rooms": 30,
            "amenities": ["Shuttle", "Free Breakfast"]
        }
    ]
    with open("hotels/hotels.json", "w") as f:
        json.dump({"hotels": hotels}, f, indent=2)

    # --- Hotel Bookings ---
    hotel_bookings = [
        {
            "booking_id": "HB001",
            "guest_name": "John Smith",
            "hotel_id": "H001",
            "flight_id": "F001",
            "check_in_date": "2025-03-15",
            "check_out_date": "2025-03-18",
            "status": "confirmed"
        },
        # Distractor: cancelled booking linked to the delayed flight
        {
            "booking_id": "HB002",
            "guest_name": "John Smith",
            "hotel_id": "H002",
            "flight_id": "F001",
            "check_in_date": "2025-03-15",
            "check_out_date": "2025-03-18",
            "status": "cancelled"
        }
    ]
    with open("hotel_bookings.json", "w") as f:
        json.dump({"hotel_bookings": hotel_bookings}, f, indent=2)

    # --- Transports ---
    transports = [
        {
            "transport_id": "T001",
            "transport_type": "suv",
            "service_provider": "Uber",
            "service_area": "ORD",
            "vehicle_type": "premium",
            "base_price": 75.0,
            "next_available": "2025-03-15 08:00"
        },
        {
            "transport_id": "T002",
            "transport_type": "limousine",
            "service_provider": "Blacklane",
            "service_area": "JFK",
            "vehicle_type": "luxury",
            "base_price": 120.0,
            "next_available": "2025-03-15 12:00"
        }
    ]
    with open("transports/transports.json", "w") as f:
        json.dump({"transports": transports}, f, indent=2)

    # --- Transport Bookings ---
    # Original pickup time: 2025-03-15 16:30 (30 min after scheduled arrival 16:00)
    # After 120 min delay, new arrival at 18:00, so pickup should be 18:30.
    transport_bookings = [
        {
            "booking_id": "TB001",
            "guest_name": "John Smith",
            "transport_id": "T001",
            "flight_id": "F001",
            "pickup_time": "2025-03-15 16:30",
            "status": "confirmed"
        },
        # Distractor: old booking already past (time earlier than current)
        {
            "booking_id": "TB002",
            "guest_name": "Jane Doe",
            "transport_id": "T002",
            "flight_id": "F002",
            "pickup_time": "2025-03-14 10:00",
            "status": "completed"
        }
    ]
    with open("transport_bookings.json", "w") as f:
        json.dump({"transport_bookings": transport_bookings}, f, indent=2)

    # --- Additional noise file (unrelated CSV) ---
    with open("ops/event_log.csv", "w") as f:
        f.write("timestamp,event,detail\n2025-03-15 10:15,delay_alert,UA123\n2025-03-15 10:16,ticket_update,DL789\n")

if __name__ == "__main__":
    build_env()
