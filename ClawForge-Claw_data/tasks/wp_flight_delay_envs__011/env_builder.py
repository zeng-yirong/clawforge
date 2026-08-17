import os
import json

def build_env():
    # Create directory structure
    os.makedirs("data/templates", exist_ok=True)
    os.makedirs("data/backup", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # empty output folder for agent

    # --- flights.json ---
    flights = [
        {"flight_id": "fl_001", "flight_number": "UA123", "airline": "United Airlines",
         "origin": "SFO", "destination": "ORD", "departure_time": "2025-06-15T08:00",
         "arrival_time": "2025-06-15T10:00", "status": "delayed", "delay_minutes": 120, "gate": "C15"},
        {"flight_id": "fl_002", "flight_number": "DL789", "airline": "Delta Airlines",
         "origin": "ATL", "destination": "JFK", "departure_time": "2025-06-15T09:00",
         "arrival_time": "2025-06-15T12:00", "status": "on_time", "delay_minutes": 0, "gate": "A10"},
        {"flight_id": "fl_003", "flight_number": "AA456", "airline": "American Airlines",
         "origin": "LAX", "destination": "BOS", "departure_time": "2025-06-15T07:00",
         "arrival_time": "2025-06-15T11:00", "status": "cancelled", "delay_minutes": 0, "gate": "B22"}
    ]
    with open("data/flights.json", "w") as f:
        json.dump({"flights": flights}, f, indent=2)

    # --- hotels.json ---
    hotels = [
        {"hotel_id": "hot_westin", "hotel_name": "Westin O'Hare", "city": "Chicago",
         "address": "789 Transit Rd, Rosemont, IL 60018", "star_rating": 4,
         "price_per_night": 200, "available_rooms": 10, "amenities": ["WiFi", "Pool"]},
        {"hotel_id": "hot_hilton", "hotel_name": "Hilton Manhattan", "city": "New York",
         "address": "456 Fashion Ave, New York, NY 10018", "star_rating": 5,
         "price_per_night": 350, "available_rooms": 5, "amenities": ["Spa", "Gym"]}
    ]
    with open("data/hotels.json", "w") as f:
        json.dump({"hotels": hotels}, f, indent=2)

    # --- hotel_bookings.json ---
    hotel_bookings = [
        {"booking_id": "hb_001", "hotel_id": "hot_westin", "flight_id": "fl_001",
         "guest_name": "Jane Doe", "contact_id": "ct_001",
         "check_in": "2025-06-15", "check_out": "2025-06-16"},
        {"booking_id": "hb_002", "hotel_id": "hot_hilton", "flight_id": "fl_002",
         "guest_name": "John Smith", "contact_id": "ct_002",
         "check_in": "2025-06-15", "check_out": "2025-06-16"},
        {"booking_id": "hb_003", "hotel_id": "hot_westin", "flight_id": "fl_003",
         "guest_name": "Mike Johnson", "contact_id": "ct_003",
         "check_in": "2025-06-15", "check_out": "2025-06-16"}
    ]
    with open("data/hotel_bookings.json", "w") as f:
        json.dump({"hotel_bookings": hotel_bookings}, f, indent=2)

    # --- transport_bookings.json ---
    transport_bookings = [
        {"booking_id": "tb_001", "transport_id": "trans_limo", "flight_id": "fl_001",
         "guest_name": "Jane Doe", "pickup_time": "2025-06-15T10:00",
         "dropoff_location": "Westin O'Hare"},
        {"booking_id": "tb_002", "transport_id": "trans_shuttle", "flight_id": "fl_002",
         "guest_name": "John Smith", "pickup_time": "2025-06-15T09:00",
         "dropoff_location": "JFK Airport"},
        {"booking_id": "tb_003", "transport_id": "trans_suv", "flight_id": "fl_003",
         "guest_name": "Mike Johnson", "pickup_time": "2025-06-15T07:00",
         "dropoff_location": "BOS Airport"}
    ]
    with open("data/transport_bookings.json", "w") as f:
        json.dump({"transport_bookings": transport_bookings}, f, indent=2)

    # --- transports.json ---
    transports = [
        {"transport_id": "trans_limo", "transport_type": "limousine",
         "service_provider": "Blacklane", "service_area": "Chicago",
         "vehicle_type": "luxury", "base_price": 100, "next_available": "2025-06-15T12:00"},
        {"transport_id": "trans_shuttle", "transport_type": "shuttle",
         "service_provider": "SuperShuttle", "service_area": "New York",
         "vehicle_type": "van", "base_price": 50, "next_available": "2025-06-15T10:00"},
        {"transport_id": "trans_suv", "transport_type": "suv",
         "service_provider": "Uber", "service_area": "Boston",
         "vehicle_type": "premium", "base_price": 80, "next_available": "2025-06-15T11:00"}
    ]
    with open("data/transports.json", "w") as f:
        json.dump({"transports": transports}, f, indent=2)

    # --- contacts.json ---
    contacts = [
        {"contact_id": "ct_001", "name": "Jane Doe", "email": "jane.doe@example.com",
         "phone": "+1-555-0101"},
        {"contact_id": "ct_002", "name": "John Smith", "email": "john.smith@example.com",
         "phone": "+1-555-0102"},
        {"contact_id": "ct_003", "name": "Mike Johnson", "email": "mike.johnson@example.com",
         "phone": "+1-555-0103"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # --- notification template ---
    template = """Dear {{guest_name}},

Your flight {{flight_number}} ({{origin}} → {{destination}}) is delayed by {{delay_minutes}} minutes.
Your hotel check-in at {{hotel_name}} has been moved to {{new_check_in}} and your {{transport_type}} pickup has been rescheduled to {{new_time}}.

We apologize for any inconvenience.
Best regards,
Travel Ops"""
    with open("data/templates/notification_template.txt", "w") as f:
        f.write(template)

    # --- interference files ---
    # Old backup (outdated flight data)
    old_flights = [
        {"flight_id": "fl_001", "flight_number": "UA123", "status": "on_time", "delay_minutes": 0}
    ]
    with open("data/backup/flights_backup.json", "w") as f:
        json.dump({"flights": old_flights}, f, indent=2)

    # Unrelated notes
    with open("data/notes.txt", "w") as f:
        f.write("Reminder: Verify all bookings before sending notifications.\n")

    # A dummy CSV with irrelevant data
    with open("data/audit_trail.csv", "w") as f:
        f.write("timestamp,user,action\n2025-06-14T23:00,admin,manual_adjust\n")

if __name__ == "__main__":
    build_env()
