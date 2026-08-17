import json
import os

def build_env():
    # 创建数据目录
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/archive", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    # 1. 航班数据
    flights = [
        {
            "flight_id": "UA123",
            "flight_number": "UA123",
            "airline": "United Airlines",
            "origin": "SFO",
            "destination": "ORD",
            "departure_time": "2025-04-10T06:00",
            "arrival_time": "2025-04-10T09:00",
            "status": "delayed",
            "delay_minutes": 180,
            "gate": "C15"
        },
        {
            "flight_id": "AA456",
            "flight_number": "AA456",
            "airline": "American Airlines",
            "origin": "ATL",
            "destination": "JFK",
            "departure_time": "2025-04-10T08:00",
            "arrival_time": "2025-04-10T11:00",
            "status": "on_time",
            "delay_minutes": 0,
            "gate": "A10"
        },
        {
            "flight_id": "DL789",
            "flight_number": "DL789",
            "airline": "Delta Airlines",
            "origin": "LAX",
            "destination": "BOS",
            "departure_time": "2025-04-10T07:30",
            "arrival_time": "2025-04-10T15:00",
            "status": "on_time",
            "delay_minutes": 0,
            "gate": "B22"
        }
    ]
    with open("data/flights.json", "w") as f:
        json.dump(flights, f, indent=2)

    # 2. 账户数据
    accounts = [
        {"account_id": "acc_john_smith", "name": "John Smith", "email": "john.smith@example.com", "role": "traveler"},
        {"account_id": "acc_jane_doe", "name": "Jane Doe", "email": "jane.doe@example.com", "role": "traveler"}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # 3. 酒店数据
    hotels = [
        {"hotel_id": "westin_ohare", "hotel_name": "Westin O'Hare", "city": "Chicago", "address": "789 Transit Rd, Rosemont, IL 60018", "star_rating": 4, "price_per_night": 189.0, "available_rooms": 15, "amenities": ["WiFi", "Gym", "Business Center"]},
        {"hotel_id": "marriott_jfk", "hotel_name": "Marriott JFK Airport", "city": "New York", "address": "123 Airport Rd, Jamaica, NY 11430", "star_rating": 3, "price_per_night": 149.0, "available_rooms": 8, "amenities": ["WiFi", "Shuttle"]}
    ]
    with open("data/hotels.json", "w") as f:
        json.dump(hotels, f, indent=2)

    # 4. 交通数据
    transports = [
        {"transport_id": "shuttle_001", "transport_type": "shuttle", "service_provider": "SuperShuttle", "service_area": "ORD", "vehicle_type": "van", "base_price": 45.0, "next_available": "2025-04-10T08:00"},
        {"transport_id": "limo_001", "transport_type": "limousine", "service_provider": "Blacklane", "service_area": "JFK", "vehicle_type": "luxury", "base_price": 120.0, "next_available": "2025-04-10T07:00"}
    ]
    with open("data/transports.json", "w") as f:
        json.dump(transports, f, indent=2)

    # 5. 酒店预订（含干扰项：已取消的预订）
    hotel_bookings = [
        {"booking_id": "hb_001", "account_id": "acc_john_smith", "flight_id": "UA123", "hotel_id": "westin_ohare", "check_in": "2025-04-10", "check_out": "2025-04-13", "status": "active"},
        {"booking_id": "hb_002", "account_id": "acc_jane_doe", "flight_id": "AA456", "hotel_id": "marriott_jfk", "check_in": "2025-04-10", "check_out": "2025-04-12", "status": "active"},
        {"booking_id": "hb_003", "account_id": "acc_john_smith", "flight_id": "UA123", "hotel_id": "westin_ohare", "check_in": "2025-04-11", "check_out": "2025-04-14", "status": "cancelled"}
    ]
    with open("data/hotel_bookings.json", "w") as f:
        json.dump(hotel_bookings, f, indent=2)

    # 6. 交通预订
    transport_bookings = [
        {"booking_id": "tb_001", "account_id": "acc_john_smith", "flight_id": "UA123", "transport_id": "shuttle_001", "pickup_datetime": "2025-04-10T09:00", "dropoff": "Westin O'Hare", "status": "confirmed"},
        {"booking_id": "tb_002", "account_id": "acc_jane_doe", "flight_id": "AA456", "transport_id": "limo_001", "pickup_datetime": "2025-04-10T08:00", "dropoff": "Marriott JFK", "status": "confirmed"}
    ]
    with open("data/transport_bookings.json", "w") as f:
        json.dump(transport_bookings, f, indent=2)

    # 7. 干扰文件：旧备份、日志
    with open("data/archive/old_flights_2024.json", "w") as f:
        json.dump([], f)
    with open("logs/system.log", "w") as f:
        f.write("[2025-04-09 23:00] System ready\n")

if __name__ == "__main__":
    build_env()
