import json
import os

def build_env():
    # ---------- flights ----------
    flights = [
        {
            "flight_id": "fl_001",
            "flight_number": "UA123",
            "airline": "United Airlines",
            "origin": "SFO",
            "destination": "ORD",
            "departure_time": "2025-03-15 14:00",
            "arrival_time": "2025-03-15 20:00",
            "status": "delayed",
            "delay_minutes": 120,
            "gate": "A10"
        },
        {
            "flight_id": "fl_002",
            "flight_number": "AA456",
            "airline": "American Airlines",
            "origin": "ATL",
            "destination": "JFK",
            "departure_time": "2025-03-15 16:00",
            "arrival_time": "2025-03-15 22:00",
            "status": "delayed",
            "delay_minutes": 30,
            "gate": "B22"
        },
        {
            "flight_id": "fl_003",
            "flight_number": "DL789",
            "airline": "Delta Airlines",
            "origin": "LAX",
            "destination": "BOS",
            "departure_time": "2025-03-15 10:00",
            "arrival_time": "2025-03-15 18:00",
            "status": "on_time",
            "delay_minutes": 0,
            "gate": "C15"
        }
    ]
    os.makedirs("data/flights", exist_ok=True)
    with open("data/flights/flights.json", "w") as f:
        json.dump({"flights": flights}, f, indent=2)

    # ---------- hotels (reference) ----------
    hotels = [
        {
            "hotel_id": "ht_001",
            "hotel_name": "Hilton Manhattan",
            "city": "New York",
            "address": "456 Fashion Ave, New York, NY 10018",
            "star_rating": 4,
            "price_per_night": 299.0,
            "available_rooms": 12,
            "amenities": ["WiFi", "Gym", "Restaurant"]
        },
        {
            "hotel_id": "ht_002",
            "hotel_name": "Westin O'Hare",
            "city": "Chicago",
            "address": "789 Transit Rd, Rosemont, IL 60018",
            "star_rating": 3,
            "price_per_night": 189.0,
            "available_rooms": 45,
            "amenities": ["Parking", "WiFi"]
        },
        {
            "hotel_id": "ht_003",
            "hotel_name": "Marriott JFK Airport",
            "city": "New York",
            "address": "123 Airport Rd, Jamaica, NY 11430",
            "star_rating": 4,
            "price_per_night": 259.0,
            "available_rooms": 8,
            "amenities": ["Shuttle", "WiFi", "Bar"]
        }
    ]
    os.makedirs("data/hotels", exist_ok=True)
    with open("data/hotels/hotels.json", "w") as f:
        json.dump({"hotels": hotels}, f, indent=2)

    # ---------- hotel bookings ----------
    hotel_bookings = [
        {
            "booking_id": "hb_001",
            "hotel_id": "ht_001",
            "flight_id": "fl_001",
            "customer_name": "Jane Doe",
            "checkin_date": "2025-03-15",
            "status": "confirmed"
        },
        {
            "booking_id": "hb_002",
            "hotel_id": "ht_002",
            "flight_id": "fl_002",
            "customer_name": "John Smith",
            "checkin_date": "2025-03-15",
            "status": "cancelled"          # already cancelled – should be ignored
        },
        {
            "booking_id": "hb_003",
            "hotel_id": "ht_003",
            "flight_id": "fl_001",
            "customer_name": "Mike Johnson",
            "checkin_date": "2025-03-15",
            "status": "confirmed"
        },
        {
            "booking_id": "hb_004",
            "hotel_id": "ht_001",
            "flight_id": "fl_003",
            "customer_name": "Alice Brown",
            "checkin_date": "2025-03-15",
            "status": "cancelled"          # cancelled, on‑time flight anyway
        },
        {
            "booking_id": "hb_005",
            "hotel_id": "ht_002",
            "flight_id": "fl_999",          # non‑existent flight – bait
            "customer_name": "Bob White",
            "checkin_date": "2025-03-15",
            "status": "confirmed"
        }
    ]
    os.makedirs("data/bookings", exist_ok=True)
    with open("data/bookings/hotel_bookings.json", "w") as f:
        json.dump({"hotel_bookings": hotel_bookings}, f, indent=2)

    # ---------- transport bookings ----------
    transport_bookings = [
        {
            "booking_id": "tb_001",
            "flight_id": "fl_001",
            "transport_type": "limousine",
            "pickup_time": "2025-03-15 20:30",
            "status": "confirmed"
        },
        {
            "booking_id": "tb_002",
            "flight_id": "fl_001",
            "transport_type": "shuttle",
            "pickup_time": "2025-03-15 21:00",
            "status": "confirmed"
        },
        {
            "booking_id": "tb_003",
            "flight_id": "fl_002",
            "transport_type": "suv",
            "pickup_time": "2025-03-15 22:15",
            "status": "cancelled"          # cancelled – ignore
        },
        {
            "booking_id": "tb_004",
            "flight_id": "fl_003",
            "transport_type": "limousine",
            "pickup_time": "2025-03-15 18:15",
            "status": "cancelled"          # cancelled – ignore
        }
    ]
    with open("data/bookings/transport_bookings.json", "w") as f:
        json.dump({"transport_bookings": transport_bookings}, f, indent=2)

    # ---------- distractors: old backup & accounts (unused) ----------
    os.makedirs("data/backup", exist_ok=True)
    with open("data/backup/old_hotel_bookings.json", "w") as f:
        json.dump({"hotel_bookings": []}, f, indent=2)

    accounts = [
        {"account_id": "acc_001", "account_name": "Jane Doe", "email": "jane.doe@example.com", "role": "traveler", "display_name": "Jane Doe"},
        {"account_id": "acc_002", "account_name": "John Smith", "email": "john.smith@example.com", "role": "traveler", "display_name": "John Smith"},
        {"account_id": "acc_003", "account_name": "Ops Manager", "email": "ops@example.com", "role": "operator", "display_name": "Jamie"}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # ensure ops directory exists (empty)
    os.makedirs("ops", exist_ok=True)

if __name__ == "__main__":
    build_env()
