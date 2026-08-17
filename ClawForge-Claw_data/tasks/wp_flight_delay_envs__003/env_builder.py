import json
import os
from datetime import datetime, timedelta

def build_env():
    # 创建目录结构
    dirs = [
        "data/flights",
        "data/hotels",
        "data/contacts",
        "data/hotel_bookings",
        "data/transport_bookings",
        "ops"
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # 航班数据
    flights = [
        {"flight_id": "F001", "flight_number": "AA456", "airline": "American Airlines",
         "origin": "ATL", "destination": "BOS", "departure_time": "2025-03-20T14:00",
         "arrival_time": "2025-03-20T16:00", "status": "delayed", "delay_minutes": 120, "gate": "A10"},
        {"flight_id": "F002", "flight_number": "DL789", "airline": "Delta Airlines",
         "origin": "LAX", "destination": "JFK", "departure_time": "2025-03-20T10:00",
         "arrival_time": "2025-03-20T13:00", "status": "delayed", "delay_minutes": 60, "gate": "B22"},
        {"flight_id": "F003", "flight_number": "UA123", "airline": "United Airlines",
         "origin": "SFO", "destination": "ORD", "departure_time": "2025-03-20T18:00",
         "arrival_time": "2025-03-20T20:00", "status": "on_time", "delay_minutes": 0, "gate": "C15"}
    ]
    with open("data/flights/flights.json", "w") as f:
        json.dump({"flights": flights}, f, indent=2)

    # 酒店数据
    hotels = [
        {"hotel_id": "H001", "hotel_name": "Hilton Manhattan", "city": "New York",
         "address": "456 Fashion Ave, New York, NY 10018", "star_rating": 4,
         "price_per_night": 250.0, "available_rooms": 0, "amenities": ["WiFi", "Gym", "Restaurant"]},
        {"hotel_id": "H002", "hotel_name": "Marriott JFK Airport", "city": "New York",
         "address": "123 Airport Rd, Jamaica, NY 11430", "star_rating": 3,
         "price_per_night": 180.0, "available_rooms": 10, "amenities": ["WiFi", "Shuttle"]},
        {"hotel_id": "H003", "hotel_name": "Westin O'Hare", "city": "Chicago",
         "address": "789 Transit Rd, Rosemont, IL 60018", "star_rating": 4,
         "price_per_night": 200.0, "available_rooms": 5, "amenities": ["WiFi", "Pool", "Business Center"]}
    ]
    with open("data/hotels/hotels.json", "w") as f:
        json.dump({"hotels": hotels}, f, indent=2)

    # 联系人数据
    contacts = [
        {"contact_id": "C001", "name": "Jane Doe", "email": "jane.doe@example.com", "phone": "+1-555-0101"},
        {"contact_id": "C002", "name": "John Smith", "email": "john.smith@example.com", "phone": "+1-555-0102"},
        {"contact_id": "C003", "name": "Mike Johnson", "email": "mike.johnson@example.com", "phone": "+1-555-0103"}
    ]
    with open("data/contacts/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # 酒店预订数据 (包含受影响的HB003和干扰项)
    hotel_bookings = [
        {"booking_id": "HB001", "contact_id": "C001", "hotel_id": "H002",
         "check_in": "2025-03-20", "check_out": "2025-03-22", "status": "confirmed"},
        {"booking_id": "HB002", "contact_id": "C002", "hotel_id": "H001",
         "check_in": "2025-03-22", "check_out": "2025-03-24", "status": "confirmed"},
        {"booking_id": "HB003", "contact_id": "C002", "hotel_id": "H001",
         "check_in": "2025-03-20", "check_out": "2025-03-22", "status": "confirmed"},
        {"booking_id": "HB004", "contact_id": "C003", "hotel_id": "H003",
         "check_in": "2025-03-21", "check_out": "2025-03-23", "status": "confirmed"}
    ]
    with open("data/hotel_bookings/hotel_bookings.json", "w") as f:
        json.dump({"hotel_bookings": hotel_bookings}, f, indent=2)

    # 交通预订数据
    transport_bookings = [
        {"booking_id": "TB001", "contact_id": "C002", "transport_type": "suv",
         "service_provider": "Uber", "service_area": "JFK",
         "pickup_time": "2025-03-20T16:30", "status": "confirmed"},
        {"booking_id": "TB002", "contact_id": "C001", "transport_type": "limousine",
         "service_provider": "Blacklane", "service_area": "JFK",
         "pickup_time": "2025-03-20T13:00", "status": "confirmed"},
        {"booking_id": "TB003", "contact_id": "C003", "transport_type": "shuttle",
         "service_provider": "SuperShuttle", "service_area": "ORD",
         "pickup_time": "2025-03-21T08:00", "status": "confirmed"}
    ]
    with open("data/transport_bookings/transport_bookings.json", "w") as f:
        json.dump({"transport_bookings": transport_bookings}, f, indent=2)

if __name__ == "__main__":
    build_env()
