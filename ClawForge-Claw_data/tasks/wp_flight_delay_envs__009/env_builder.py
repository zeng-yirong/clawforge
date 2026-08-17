import json
import os

def build_env():
    # 创建目录
    os.makedirs("flights", exist_ok=True)
    os.makedirs("hotels", exist_ok=True)
    os.makedirs("transports", exist_ok=True)

    # 航班数据
    flights = [
        {"flight_id": "FL001", "flight_number": "UA123", "airline": "United Airlines",
         "origin": "SFO", "destination": "ORD", "departure_time": "2025-06-15 15:00",
         "arrival_time": "2025-06-15 18:00", "status": "delayed", "delay_minutes": 120, "gate": "C15"},
        {"flight_id": "FL002", "flight_number": "DL789", "airline": "Delta Airlines",
         "origin": "ATL", "destination": "JFK", "departure_time": "2025-06-15 16:00",
         "arrival_time": "2025-06-15 19:00", "status": "delayed", "delay_minutes": 60, "gate": "A10"},
        {"flight_id": "FL003", "flight_number": "AA456", "airline": "American Airlines",
         "origin": "LAX", "destination": "BOS", "departure_time": "2025-06-15 17:00",
         "arrival_time": "2025-06-15 20:30", "status": "on_time", "delay_minutes": 0, "gate": "B22"}
    ]
    with open("flights/flights.json", "w") as f:
        json.dump(flights, f, indent=2)

    # 酒店数据
    hotels = [
        {"hotel_id": "HTL001", "hotel_name": "Westin O'Hare", "city": "Chicago",
         "address": "789 Transit Rd, Rosemont, IL 60018", "star_rating": 4,
         "price_per_night": 189.0, "available_rooms": 15,
         "amenities": ["pool", "gym", "free wifi"]},
        {"hotel_id": "HTL002", "hotel_name": "Hilton Manhattan", "city": "New York",
         "address": "456 Fashion Ave, New York, NY 10018", "star_rating": 5,
         "price_per_night": 299.0, "available_rooms": 8,
         "amenities": ["spa", "bar", "concierge"]},
        {"hotel_id": "HTL003", "hotel_name": "Marriott JFK Airport", "city": "New York",
         "address": "123 Airport Rd, Jamaica, NY 11430", "star_rating": 3,
         "price_per_night": 129.0, "available_rooms": 22,
         "amenities": ["shuttle", "restaurant"]}
    ]
    with open("hotels/hotels.json", "w") as f:
        json.dump(hotels, f, indent=2)

    # 酒店预订数据（包含干扰项）
    hotel_bookings = [
        {"booking_id": "HB001", "hotel_id": "HTL001", "guest_name": "John Smith",
         "flight_number": "UA123", "check_in": "2025-06-15", "check_out": "2025-06-18"},
        {"booking_id": "HB002", "hotel_id": "HTL002", "guest_name": "Jane Doe",
         "flight_number": "AA456", "check_in": "2025-06-15", "check_out": "2025-06-17"}
    ]
    with open("hotels/bookings.json", "w") as f:
        json.dump(hotel_bookings, f, indent=2)

    # 交通服务数据
    transports = [
        {"transport_id": "TRP001", "transport_type": "limousine", "service_provider": "Blacklane",
         "service_area": "ORD", "vehicle_type": "luxury", "base_price": 120.0,
         "next_available": "2025-06-15 20:00"},
        {"transport_id": "TRP002", "transport_type": "shuttle", "service_provider": "SuperShuttle",
         "service_area": "JFK", "vehicle_type": "van", "base_price": 25.0,
         "next_available": "2025-06-15 19:00"},
        {"transport_id": "TRP003", "transport_type": "suv", "service_provider": "Uber",
         "service_area": "BOS", "vehicle_type": "premium", "base_price": 85.0,
         "next_available": "2025-06-15 21:00"}
    ]
    with open("transports/transports.json", "w") as f:
        json.dump(transports, f, indent=2)

    # 交通预订数据（包含干扰项）
    transport_bookings = [
        {"booking_id": "TB001", "transport_id": "TRP001", "guest_name": "John Smith",
         "flight_number": "UA123", "pickup_time": "2025-06-15 18:00", "dropoff_location": "Westin O'Hare"},
        {"booking_id": "TB002", "transport_id": "TRP002", "guest_name": "Mike Johnson",
         "flight_number": "DL789", "pickup_time": "2025-06-15 19:00", "dropoff_location": "Marriott JFK Airport"}
    ]
    with open("transports/bookings.json", "w") as f:
        json.dump(transport_bookings, f, indent=2)

    # 联系人数据
    contacts = [
        {"contact_id": "C001", "name": "John Smith", "email": "john.smith@example.com", "phone": "+1-555-0102"},
        {"contact_id": "C002", "name": "Jane Doe", "email": "jane.doe@example.com", "phone": "+1-555-0101"},
        {"contact_id": "C003", "name": "Mike Johnson", "email": "mike.johnson@example.com", "phone": "+1-555-0103"}
    ]
    with open("contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

if __name__ == "__main__":
    build_env()
