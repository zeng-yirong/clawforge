import json
import os

def build_env():
    # Create directory structure
    os.makedirs("data/flights", exist_ok=True)
    os.makedirs("data/hotels", exist_ok=True)
    os.makedirs("data/transports", exist_ok=True)
    os.makedirs("data/bookings", exist_ok=True)
    os.makedirs("backup", exist_ok=True)

    # ---- Flights ----
    flights = [
        {
            "flight_id": "AA456",
            "flight_number": "AA456",
            "airline": "American Airlines",
            "origin": "ATL",
            "destination": "JFK",
            "departure_time": "2025-07-20 15:00",
            "arrival_time": "2025-07-20 17:30",
            "status": "delayed",
            "delay_minutes": 145,
            "gate": "A10"
        },
        {
            "flight_id": "DL789",
            "flight_number": "DL789",
            "airline": "Delta Airlines",
            "origin": "LAX",
            "destination": "ORD",
            "departure_time": "2025-07-20 18:00",
            "arrival_time": "2025-07-20 23:00",
            "status": "delayed",
            "delay_minutes": 60,
            "gate": "B22"
        },
        {
            "flight_id": "UA123",
            "flight_number": "UA123",
            "airline": "United Airlines",
            "origin": "SFO",
            "destination": "BOS",
            "departure_time": "2025-07-20 10:00",
            "arrival_time": "2025-07-20 14:30",
            "status": "on_time",
            "delay_minutes": 0,
            "gate": "C15"
        }
    ]
    with open("data/flights/flights.json", "w") as f:
        json.dump({"flights": flights}, f, indent=2)

    # ---- Hotels ----
    hotels = [
        {
            "hotel_id": "hotel_001",
            "hotel_name": "Hilton Manhattan",
            "city": "New York",
            "address": "456 Fashion Ave, New York, NY 10018",
            "star_rating": 4,
            "price_per_night": 250.0,
            "available_rooms": 20,
            "amenities": ["WiFi", "Gym", "Pool"]
        },
        {
            "hotel_id": "hotel_002",
            "hotel_name": "Marriott JFK Airport",
            "city": "New York",
            "address": "123 Airport Rd, Jamaica, NY 11430",
            "star_rating": 3,
            "price_per_night": 180.0,
            "available_rooms": 50,
            "amenities": ["WiFi", "Shuttle"]
        },
        {
            "hotel_id": "hotel_003",
            "hotel_name": "Westin O'Hare",
            "city": "Chicago",
            "address": "789 Transit Rd, Rosemont, IL 60018",
            "star_rating": 4,
            "price_per_night": 220.0,
            "available_rooms": 30,
            "amenities": ["WiFi", "Business Center"]
        }
    ]
    with open("data/hotels/hotels.json", "w") as f:
        json.dump({"hotels": hotels}, f, indent=2)

    # ---- Transports ----
    transports = [
        {
            "transport_id": "trans_001",
            "transport_type": "limousine",
            "service_provider": "Blacklane",
            "service_area": "JFK",
            "vehicle_type": "luxury",
            "base_price": 120.0,
            "next_available": "2025-07-20 21:00"
        },
        {
            "transport_id": "trans_002",
            "transport_type": "shuttle",
            "service_provider": "SuperShuttle",
            "service_area": "ORD",
            "vehicle_type": "van",
            "base_price": 45.0,
            "next_available": "2025-07-20 19:00"
        },
        {
            "transport_id": "trans_003",
            "transport_type": "suv",
            "service_provider": "Uber",
            "service_area": "BOS",
            "vehicle_type": "premium",
            "base_price": 80.0,
            "next_available": "2025-07-20 15:00"
        }
    ]
    with open("data/transports/transports.json", "w") as f:
        json.dump({"transports": transports}, f, indent=2)

    # ---- Contacts ----
    contacts = [
        {
            "contact_id": "contact_001",
            "name": "Jane Doe",
            "email": "jane.doe@example.com",
            "phone": "+1-555-0101"
        },
        {
            "contact_id": "contact_002",
            "name": "John Smith",
            "email": "john.smith@example.com",
            "phone": "+1-555-0102"
        },
        {
            "contact_id": "contact_003",
            "name": "Mike Johnson",
            "email": "mike.johnson@example.com",
            "phone": "+1-555-0103"
        }
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # ---- Hotel Bookings ----
    hotel_bookings = [
        {
            "booking_id": "booking_h1",
            "hotel_id": "hotel_001",
            "flight_id": "AA456",
            "check_in": "2025-07-20",
            "check_out": "2025-07-22",
            "guest_ids": ["contact_001", "contact_002"],
            "status": "confirmed"
        },
        {
            "booking_id": "booking_h2",
            "hotel_id": "hotel_002",
            "flight_id": "DL789",
            "check_in": "2025-07-20",
            "check_out": "2025-07-22",
            "guest_ids": ["contact_003"],
            "status": "cancelled"
        }
    ]
    with open("data/bookings/hotel_bookings.json", "w") as f:
        json.dump({"hotel_bookings": hotel_bookings}, f, indent=2)

    # ---- Transport Bookings ----
    transport_bookings = [
        {
            "booking_id": "booking_t1",
            "transport_id": "trans_001",
            "flight_id": "AA456",
            "pickup_time": "2025-07-20 17:30",
            "dropoff": "Hilton Manhattan",
            "guest_ids": ["contact_001", "contact_002"],
            "status": "confirmed"
        },
        {
            "booking_id": "booking_t2",
            "transport_id": "trans_002",
            "flight_id": "DL789",
            "pickup_time": "2025-07-20 22:30",
            "dropoff": "Marriott",
            "guest_ids": ["contact_003"],
            "status": "cancelled"
        },
        {
            "booking_id": "booking_t3",
            "transport_id": "trans_003",
            "flight_id": "AA456",
            "pickup_time": "2025-07-20 17:00",
            "dropoff": "Central Park",
            "guest_ids": ["contact_001"],
            "status": "cancelled"
        }
    ]
    with open("data/bookings/transport_bookings.json", "w") as f:
        json.dump({"transport_bookings": transport_bookings}, f, indent=2)

    # ---- Decoy files ----
    with open("backup/old_flights_backup.json", "w") as f:
        json.dump({"flights": []}, f, indent=2)

    with open("server.log", "w") as f:
        f.write("2025-07-20 12:00:00 INFO Starting system...\n")
        f.write("2025-07-20 17:35:00 WARN Flight AA456 delayed\n")

if __name__ == "__main__":
    build_env()
