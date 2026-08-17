import os
import json
import random

def build_env():
    random.seed(42)  # deterministic for reproducibility

    # --- flights ---
    flights_path = "data/flights/flights.json"
    os.makedirs(os.path.dirname(flights_path), exist_ok=True)
    flights = {
        "flights": [
            {"flight_id": "f001", "flight_number": "UA123", "airline": "United Airlines",
             "origin": "SFO", "destination": "JFK", "departure_time": "2024-03-15 18:00",
             "arrival_time": "2024-03-15 22:00", "status": "delayed", "delay_minutes": 120, "gate": "C15"},
            {"flight_id": "f002", "flight_number": "AA456", "airline": "American Airlines",
             "origin": "ATL", "destination": "BOS", "departure_time": "2024-03-15 14:00",
             "arrival_time": "2024-03-15 16:00", "status": "on_time", "delay_minutes": 0, "gate": "A10"},
            {"flight_id": "f003", "flight_number": "DL789", "airline": "Delta Airlines",
             "origin": "LAX", "destination": "ORD", "departure_time": "2024-03-15 10:00",
             "arrival_time": "2024-03-15 12:30", "status": "delayed", "delay_minutes": 30, "gate": "B22"},
            {"flight_id": "f004", "flight_number": "UA456", "airline": "United Airlines",
             "origin": "SFO", "destination": "JFK", "departure_time": "2024-03-15 20:00",
             "arrival_time": "2024-03-16 00:00", "status": "on_time", "delay_minutes": 0, "gate": "D5"},
        ]
    }
    with open(flights_path, "w") as f:
        json.dump(flights, f, indent=2)

    # --- customers (simple) ---
    customers_path = "data/customers/customers.json"
    os.makedirs(os.path.dirname(customers_path), exist_ok=True)
    customers = {
        "customers": [
            {"account_id": "c001", "account_name": "John Smith", "email": "john.smith@example.com",
             "role": "traveler", "display_name": "John Smith"},
            {"account_id": "c002", "account_name": "Jane Doe", "email": "jane.doe@example.com",
             "role": "traveler", "display_name": "Jane Doe"},
        ]
    }
    with open(customers_path, "w") as f:
        json.dump(customers, f, indent=2)

    # --- contacts ---
    contacts_path = "data/contacts.json"
    os.makedirs(os.path.dirname(contacts_path), exist_ok=True)
    contacts = {
        "contacts": [
            {"contact_id": "ct001", "name": "John Smith", "email": "john.smith@example.com",
             "phone": "+1-555-0102"},
            {"contact_id": "ct002", "name": "Jane Doe", "email": "jane.doe@example.com",
             "phone": "+1-555-0101"},
            {"contact_id": "ct003", "name": "Mike Johnson", "email": "mike.johnson@example.com",
             "phone": "+1-555-0103"},
        ]
    }
    with open(contacts_path, "w") as f:
        json.dump(contacts, f, indent=2)

    # --- transport bookings ---
    transport_bookings_path = "data/bookings/transport_bookings.json"
    os.makedirs(os.path.dirname(transport_bookings_path), exist_ok=True)
    transport_bookings = {
        "transport_bookings": [
            {
                "booking_id": "tb001",
                "transport_id": "t001",
                "customer_id": "c001",
                "flight_id": "f001",
                "pickup_time": "2024-03-15 18:30",
                "dropoff_location": "Hilton Manhattan",
                "service_provider": "Blacklane",
                "vehicle_type": "limousine",
                "status": "confirmed"
            },
            {
                "booking_id": "tb002",
                "transport_id": "t002",
                "customer_id": "c002",
                "flight_id": "f002",
                "pickup_time": "2024-03-15 16:00",
                "dropoff_location": "Marriott JFK Airport",
                "service_provider": "SuperShuttle",
                "vehicle_type": "shuttle",
                "status": "confirmed"
            },
            {
                "booking_id": "tb003",
                "transport_id": "t003",
                "customer_id": "c001",
                "flight_id": "f003",
                "pickup_time": "2024-03-15 12:45",
                "dropoff_location": "Westin O'Hare",
                "service_provider": "Uber",
                "vehicle_type": "premium",
                "status": "cancelled"   # old cancelled booking – should be ignored
            },
            # unrelated booking for a different customer with a different flight
            {
                "booking_id": "tb004",
                "transport_id": "t004",
                "customer_id": "c002",
                "flight_id": "f004",
                "pickup_time": "2024-03-16 00:30",
                "dropoff_location": "Hilton Manhattan",
                "service_provider": "Blacklane",
                "vehicle_type": "limousine",
                "status": "confirmed"
            },
        ]
    }
    with open(transport_bookings_path, "w") as f:
        json.dump(transport_bookings, f, indent=2)

    # --- hotel bookings (not directly needed for task but provide context)
    hotel_bookings_path = "data/bookings/hotel_bookings.json"
    os.makedirs(os.path.dirname(hotel_bookings_path), exist_ok=True)
    hotel_bookings = {
        "hotel_bookings": [
            {"booking_id": "hb001", "customer_id": "c001", "hotel_id": "h001",
             "check_in": "2024-03-15", "check_out": "2024-03-17", "status": "confirmed"},
            {"booking_id": "hb002", "customer_id": "c002", "hotel_id": "h002",
             "check_in": "2024-03-15", "check_out": "2024-03-16", "status": "confirmed"},
        ]
    }
    with open(hotel_bookings_path, "w") as f:
        json.dump(hotel_bookings, f, indent=2)

    # --- hotels master (for reference)
    hotels_path = "data/hotels/hotels.json"
    os.makedirs(os.path.dirname(hotels_path), exist_ok=True)
    hotels = {
        "hotels": [
            {"hotel_id": "h001", "hotel_name": "Hilton Manhattan", "city": "New York",
             "address": "456 Fashion Ave, New York, NY 10018", "star_rating": 4,
             "price_per_night": 250.0, "available_rooms": 12, "amenities": ["WiFi", "Gym", "Restaurant"]},
            {"hotel_id": "h002", "hotel_name": "Marriott JFK Airport", "city": "New York",
             "address": "123 Airport Rd, Jamaica, NY 11430", "star_rating": 3,
             "price_per_night": 180.0, "available_rooms": 5, "amenities": ["WiFi", "Shuttle"]},
        ]
    }
    with open(hotels_path, "w") as f:
        json.dump(hotels, f, indent=2)

    # --- legacy / noise files ---
    # a stale dump
    stale_path = "data/backups/old_bookings.json"
    os.makedirs(os.path.dirname(stale_path), exist_ok=True)
    with open(stale_path, "w") as f:
        json.dump({"old": True}, f)

    # a text memo
    memo_path = "data/notes/tom_reminder.txt"
    os.makedirs(os.path.dirname(memo_path), exist_ok=True)
    with open(memo_path, "w") as f:
        f.write("Remember to check UA123 delay impact on John Smith's limo.\n")

if __name__ == "__main__":
    build_env()
    print("Environment built successfully.")
