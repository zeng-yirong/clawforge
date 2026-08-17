import json
import os
from datetime import datetime, timedelta

def build_env():
    # ========== 1. 航班数据 ==========
    flights = [
        {
            "flight_id": "FL001",
            "flight_number": "AA456",
            "airline": "American Airlines",
            "origin": "ATL",
            "destination": "BOS",
            "departure_time": "2025-03-20T12:00",
            "arrival_time": "2025-03-20T14:00",
            "status": "delayed",
            "delay_minutes": 120,
            "gate": "A10"
        },
        {
            "flight_id": "FL002",
            "flight_number": "UA123",
            "airline": "United Airlines",
            "origin": "SFO",
            "destination": "ORD",
            "departure_time": "2025-03-20T10:00",
            "arrival_time": "2025-03-20T16:00",
            "status": "delayed",
            "delay_minutes": 90,
            "gate": "C15"
        },
        {
            "flight_id": "FL003",
            "flight_number": "DL789",
            "airline": "Delta Airlines",
            "origin": "LAX",
            "destination": "JFK",
            "departure_time": "2025-03-20T08:00",
            "arrival_time": "2025-03-20T14:30",
            "status": "on_time",
            "delay_minutes": 0,
            "gate": "B22"
        }
    ]
    os.makedirs("data/flights", exist_ok=True)
    with open("data/flights/flights.json", "w") as f:
        json.dump({"flights": flights}, f, indent=2)

    # ========== 2. 酒店数据 ==========
    hotels = [
        {
            "hotel_id": "H001",
            "hotel_name": "Hilton Manhattan",
            "city": "New York",
            "address": "456 Fashion Ave, New York, NY 10018",
            "star_rating": 4,
            "price_per_night": 250.0,
            "available_rooms": 10,
            "amenities": ["WiFi", "Gym", "Pool"]
        },
        {
            "hotel_id": "H002",
            "hotel_name": "Marriott JFK Airport",
            "city": "New York",
            "address": "123 Airport Rd, Jamaica, NY 11430",
            "star_rating": 3,
            "price_per_night": 180.0,
            "available_rooms": 20,
            "amenities": ["WiFi", "Shuttle"]
        },
        {
            "hotel_id": "H003",
            "hotel_name": "Westin O'Hare",
            "city": "Chicago",
            "address": "789 Transit Rd, Rosemont, IL 60018",
            "star_rating": 4,
            "price_per_night": 200.0,
            "available_rooms": 5,
            "amenities": ["WiFi", "Restaurant"]
        }
    ]
    os.makedirs("data/hotels", exist_ok=True)
    with open("data/hotels/hotels.json", "w") as f:
        json.dump({"hotels": hotels}, f, indent=2)

    # ========== 3. 联系人数据 ==========
    contacts = [
        {
            "contact_id": "C001",
            "name": "Jane Doe",
            "email": "jane.doe@example.com",
            "phone": "+1-555-0101"
        },
        {
            "contact_id": "C002",
            "name": "John Smith",
            "email": "john.smith@example.com",
            "phone": "+1-555-0102"
        },
        {
            "contact_id": "C003",
            "name": "Mike Johnson",
            "email": "mike.johnson@example.com",
            "phone": "+1-555-0103"
        }
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # ========== 4. 酒店预订 ==========
    hotel_bookings = [
        {
            "booking_id": "HB-001",
            "guest_id": "C002",
            "hotel_id": "H001",
            "check_in": "2025-03-20T18:00",
            "flight_id": "FL001",
            "status": "confirmed"
        },
        {
            "booking_id": "HB-002",
            "guest_id": "C001",
            "hotel_id": "H002",
            "check_in": "2025-03-20T19:00",
            "flight_id": "FL003",
            "status": "confirmed"
        },
        {
            "booking_id": "HB-003",
            "guest_id": "C003",
            "hotel_id": "H003",
            "check_in": "2025-03-20T20:00",
            "flight_id": "FL002",
            "status": "cancelled"
        }
    ]
    os.makedirs("data/bookings", exist_ok=True)
    with open("data/bookings/hotel_bookings.json", "w") as f:
        json.dump({"hotel_bookings": hotel_bookings}, f, indent=2)

    # ========== 5. 交通预订 ==========
    transport_bookings = [
        {
            "booking_id": "TB-001",
            "guest_id": "C002",
            "transport_type": "shuttle",
            "pickup_time": "2025-03-20T18:30",
            "flight_id": "FL001",
            "status": "confirmed"
        },
        {
            "booking_id": "TB-002",
            "guest_id": "C001",
            "transport_type": "limousine",
            "pickup_time": "2025-03-20T19:30",
            "flight_id": "FL003",
            "status": "confirmed"
        },
        {
            "booking_id": "TB-003",
            "guest_id": "C003",
            "transport_type": "suv",
            "pickup_time": "2025-03-20T20:30",
            "flight_id": "FL002",
            "status": "cancelled"
        }
    ]
    with open("data/bookings/transport_bookings.json", "w") as f:
        json.dump({"transport_bookings": transport_bookings}, f, indent=2)

if __name__ == "__main__":
    build_env()
