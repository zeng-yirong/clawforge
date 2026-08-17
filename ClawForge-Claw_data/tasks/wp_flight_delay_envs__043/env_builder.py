import os
import json
import random

def build_env():
    # Ensure ops directory exists
    os.makedirs("ops", exist_ok=True)
    os.makedirs("data/flights", exist_ok=True)
    os.makedirs("data/hotels", exist_ok=True)
    os.makedirs("data/transports", exist_ok=True)
    os.makedirs("data/bookings", exist_ok=True)

    # 1. Flights
    flights = [
        {
            "flight_id": "FL001",
            "flight_number": "UA123",
            "airline": "United Airlines",
            "origin": "SFO",
            "destination": "JFK",
            "departure_time": "2025-04-10T14:00:00Z",
            "arrival_time": "2025-04-10T22:00:00Z",
            "status": "delayed",
            "delay_minutes": 120,
            "gate": "C15"
        },
        {
            "flight_id": "FL002",
            "flight_number": "DL789",
            "airline": "Delta Airlines",
            "origin": "ATL",
            "destination": "ORD",
            "departure_time": "2025-04-10T16:00:00Z",
            "arrival_time": "2025-04-10T18:30:00Z",
            "status": "delayed",
            "delay_minutes": 30,
            "gate": "A10"
        },
        {
            "flight_id": "FL003",
            "flight_number": "AA456",
            "airline": "American Airlines",
            "origin": "LAX",
            "destination": "BOS",
            "departure_time": "2025-04-10T08:00:00Z",
            "arrival_time": "2025-04-10T16:00:00Z",
            "status": "on_time",
            "delay_minutes": 0,
            "gate": "B22"
        }
    ]
    with open("data/flights/flights.json", "w") as f:
        json.dump({"flights": flights}, f, indent=2)

    # 2. Hotels
    hotels = [
        {"hotel_id": "HTL001", "hotel_name": "Hilton Manhattan", "city": "New York", "address": "456 Fashion Ave, New York, NY 10018", "star_rating": 4, "price_per_night": 250.0, "available_rooms": 20, "amenities": ["WiFi", "Pool"]},
        {"hotel_id": "HTL002", "hotel_name": "Marriott JFK Airport", "city": "New York", "address": "123 Airport Rd, Jamaica, NY 11430", "star_rating": 3, "price_per_night": 180.0, "available_rooms": 45, "amenities": ["Shuttle"]},
        {"hotel_id": "HTL003", "hotel_name": "Westin O'Hare", "city": "Chicago", "address": "789 Transit Rd, Rosemont, IL 60018", "star_rating": 4, "price_per_night": 220.0, "available_rooms": 30, "amenities": ["Gym", "Business Center"]}
    ]
    with open("data/hotels/hotels.json", "w") as f:
        json.dump({"hotels": hotels}, f, indent=2)

    # 3. Transports
    transports = [
        {"transport_id": "TRP001", "transport_type": "limousine", "service_provider": "Blacklane", "service_area": "JFK", "vehicle_type": "luxury", "base_price": 150.0, "next_available": "2025-04-10T23:00:00Z"},
        {"transport_id": "TRP002", "transport_type": "shuttle", "service_provider": "SuperShuttle", "service_area": "JFK", "vehicle_type": "van", "base_price": 40.0, "next_available": "2025-04-10T22:30:00Z"},
        {"transport_id": "TRP003", "transport_type": "suv", "service_provider": "Uber", "service_area": "ORD", "vehicle_type": "premium", "base_price": 90.0, "next_available": "2025-04-10T19:00:00Z"}
    ]
    with open("data/transports/transports.json", "w") as f:
        json.dump({"transports": transports}, f, indent=2)

    # 4. Hotel bookings (linked to flights via flight_id)
    hotel_bookings = [
        {"booking_id": "HB001", "flight_id": "FL001", "hotel_id": "HTL001", "guest_name": "Jane Doe", "check_in": "2025-04-10T22:30:00Z", "check_out": "2025-04-12T12:00:00Z"},
        {"booking_id": "HB002", "flight_id": "FL001", "hotel_id": "HTL002", "guest_name": "John Smith", "check_in": "2025-04-10T22:00:00Z", "check_out": "2025-04-11T12:00:00Z"},
        {"booking_id": "HB003", "flight_id": "FL001", "hotel_id": "HTL001", "guest_name": "Mike Johnson", "check_in": "2025-04-10T23:00:00Z", "check_out": "2025-04-13T12:00:00Z"},
        # 干扰项：关联到其他航班
        {"booking_id": "HB004", "flight_id": "FL002", "hotel_id": "HTL003", "guest_name": "Alice Wang", "check_in": "2025-04-10T18:30:00Z", "check_out": "2025-04-11T12:00:00Z"},
        {"booking_id": "HB005", "flight_id": "FL001", "hotel_id": "HTL002", "guest_name": "Bob Lee", "check_in": "2025-04-10T22:15:00Z", "check_out": "2025-04-12T12:00:00Z"},
        {"booking_id": "HB006", "flight_id": "FL003", "hotel_id": "HTL001", "guest_name": "Carol Chen", "check_in": "2025-04-10T16:00:00Z", "check_out": "2025-04-11T12:00:00Z"},
        # 重复记录（诱饵）
        {"booking_id": "HB001", "flight_id": "FL001", "hotel_id": "HTL001", "guest_name": "Jane Doe", "check_in": "2025-04-10T22:30:00Z", "check_out": "2025-04-12T12:00:00Z"},
    ]
    with open("data/bookings/hotel_bookings.json", "w") as f:
        json.dump({"hotel_bookings": hotel_bookings}, f, indent=2)

    # 5. Transport bookings
    transport_bookings = [
        {"booking_id": "TB001", "flight_id": "FL001", "transport_id": "TRP001", "passenger": "Jane Doe", "pickup_time": "2025-04-10T22:30:00Z"},
        {"booking_id": "TB002", "flight_id": "FL001", "transport_id": "TRP002", "passenger": "John Smith", "pickup_time": "2025-04-10T22:15:00Z"},
        {"booking_id": "TB003", "flight_id": "FL002", "transport_id": "TRP003", "passenger": "Alice Wang", "pickup_time": "2025-04-10T18:45:00Z"},
        {"booking_id": "TB004", "flight_id": "FL001", "transport_id": "TRP001", "passenger": "Mike Johnson", "pickup_time": "2025-04-10T23:00:00Z"},
        {"booking_id": "TB005", "flight_id": "FL003", "transport_id": "TRP002", "passenger": "Carol Chen", "pickup_time": "2025-04-10T16:30:00Z"}
    ]
    with open("data/bookings/transport_bookings.json", "w") as f:
        json.dump({"transport_bookings": transport_bookings}, f, indent=2)

    # 6. Accounts (optional but adds realism)
    accounts = [
        {"account_id": "ACC001", "account_name": "traveler_jane", "email": "jane.doe@example.com", "role": "passenger", "display_name": "Jane Doe"},
        {"account_id": "ACC002", "account_name": "traveler_john", "email": "john.smith@example.com", "role": "passenger", "display_name": "John Smith"},
        {"account_id": "ACC003", "account_name": "traveler_mike", "email": "mike.johnson@example.com", "role": "passenger", "display_name": "Mike Johnson"},
        {"account_id": "ACC004", "account_name": "traveler_alice", "email": "alice.wang@example.com", "role": "passenger", "display_name": "Alice Wang"},
        {"account_id": "ACC005", "account_name": "traveler_bob", "email": "bob.lee@example.com", "role": "passenger", "display_name": "Bob Lee"},
        {"account_id": "ACC006", "account_name": "traveler_carol", "email": "carol.chen@example.com", "role": "passenger", "display_name": "Carol Chen"}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

if __name__ == "__main__":
    build_env()
