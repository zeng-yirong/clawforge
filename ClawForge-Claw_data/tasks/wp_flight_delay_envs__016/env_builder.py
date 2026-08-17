import json, os, shutil, random
from datetime import datetime, timedelta

def build_env():
    # 清理旧数据
    for d in ["data", "ops", "output"]:
        shutil.rmtree(d, ignore_errors=True)

    # ==================== 1. 航班数据 ====================
    flights = [
        {
            "flight_id": "F001",
            "flight_number": "UA123",
            "airline": "United Airlines",
            "origin": "SFO",
            "destination": "JFK",
            "departure_time": "2025-06-15T16:00:00-05:00",
            "arrival_time": "2025-06-15T18:30:00-05:00",
            "status": "delayed",
            "delay_minutes": 120,
            "gate": "C15"
        },
        {
            "flight_id": "F002",
            "flight_number": "AA456",
            "airline": "American Airlines",
            "origin": "ATL",
            "destination": "BOS",
            "departure_time": "2025-06-15T10:00:00-05:00",
            "arrival_time": "2025-06-15T12:30:00-05:00",
            "status": "on_time",
            "delay_minutes": 0,
            "gate": "A10"
        },
        {
            "flight_id": "F003",
            "flight_number": "DL789",
            "airline": "Delta Airlines",
            "origin": "LAX",
            "destination": "ORD",
            "departure_time": "2025-06-15T20:00:00-06:00",
            "arrival_time": "2025-06-16T02:00:00-06:00",
            "status": "delayed",
            "delay_minutes": 30,
            "gate": "B22"
        }
    ]
    os.makedirs("data/flights", exist_ok=True)
    with open("data/flights/flights.json", "w") as f:
        json.dump({"flights": flights}, f, indent=2)

    # ==================== 2. 账户 ====================
    accounts = [
        {"account_id": "ACC01", "account_name": "alice_travel", "email": "alice@travelco.com", "role": "coordinator", "display_name": "Alice Chen"}
    ]
    os.makedirs("data", exist_ok=True)
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # ==================== 3. 联系人 ====================
    contacts = [
        {"contact_id": "C001", "name": "John Smith", "email": "john.smith@example.com", "phone": "+1-555-0101"},
        {"contact_id": "C002", "name": "Jane Doe", "email": "jane.doe@example.com", "phone": "+1-555-0102"},
        {"contact_id": "C003", "name": "Mike Johnson", "email": "mike.johnson@example.com", "phone": "+1-555-0103"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # ==================== 4. 酒店 ====================
    hotels = [
        {"hotel_id": "H01", "hotel_name": "Hilton Manhattan", "city": "New York", "address": "456 Fashion Ave, New York, NY 10018", "star_rating": 4, "price_per_night": 280.0, "available_rooms": 10, "amenities": ["wifi", "gym", "restaurant"]},
        {"hotel_id": "H02", "hotel_name": "Marriott JFK Airport", "city": "New York", "address": "123 Airport Rd, Jamaica, NY 11430", "star_rating": 3, "price_per_night": 150.0, "available_rooms": 25, "amenities": ["wifi", "shuttle"]},
        {"hotel_id": "H03", "hotel_name": "Westin O'Hare", "city": "Chicago", "address": "789 Transit Rd, Rosemont, IL 60018", "star_rating": 4, "price_per_night": 220.0, "available_rooms": 5, "amenities": ["wifi", "pool", "bar"]}
    ]
    os.makedirs("data/hotels", exist_ok=True)
    with open("data/hotels/hotels.json", "w") as f:
        json.dump({"hotels": hotels}, f, indent=2)

    # ==================== 5. 交通服务 ====================
    transports = [
        {"transport_id": "T01", "transport_type": "limousine", "service_provider": "Blacklane", "service_area": "JFK", "vehicle_type": "luxury", "base_price": 120.0, "next_available": "2025-06-15T22:00:00-05:00"},
        {"transport_id": "T02", "transport_type": "shuttle", "service_provider": "SuperShuttle", "service_area": "JFK", "vehicle_type": "van", "base_price": 35.0, "next_available": "2025-06-15T19:00:00-05:00"},
        {"transport_id": "T03", "transport_type": "suv", "service_provider": "Uber", "service_area": "ORD", "vehicle_type": "premium", "base_price": 85.0, "next_available": "2025-06-16T00:00:00-06:00"}
    ]
    os.makedirs("data/transports", exist_ok=True)
    with open("data/transports/transports.json", "w") as f:
        json.dump({"transports": transports}, f, indent=2)

    # ==================== 6. 酒店预订（核心） ====================
    hotel_bookings = [
        {
            "booking_id": "HB001",
            "contact_id": "C001",  # John Smith
            "hotel_id": "H01",
            "check_in": "2025-06-15",
            "check_out": "2025-06-18",
            "status": "confirmed",
            "price": 840.0
        },
        {
            "booking_id": "HB002",
            "contact_id": "C002",  # Jane Doe – unaffected flight (AA456)
            "hotel_id": "H02",
            "check_in": "2025-06-15",
            "check_out": "2025-06-16",
            "status": "confirmed",
            "price": 150.0
        },
        {
            "booking_id": "HB003",
            "contact_id": "C003",  # Mike Johnson – flight DL789 delayed 30min, minor
            "hotel_id": "H03",
            "check_in": "2025-06-16",
            "check_out": "2025-06-18",
            "status": "confirmed",
            "price": 440.0
        }
    ]
    os.makedirs("data/hotel_bookings", exist_ok=True)
    with open("data/hotel_bookings/hotel_bookings.json", "w") as f:
        json.dump({"hotel_bookings": hotel_bookings}, f, indent=2)

    # ==================== 7. 交通预订 ====================
    transport_bookings = [
        {
            "booking_id": "TB001",
            "contact_id": "C001",  # John Smith
            "transport_id": "T01",
            "pickup_time": "2025-06-15T19:00:00-05:00",
            "dropoff_location": "Hilton Manhattan",
            "status": "confirmed",
            "price": 120.0
        },
        {
            "booking_id": "TB002",
            "contact_id": "C002",  # Jane Doe
            "transport_id": "T02",
            "pickup_time": "2025-06-15T13:00:00-05:00",
            "dropoff_location": "Marriott JFK",
            "status": "confirmed",
            "price": 35.0
        },
        {
            "booking_id": "TB003",
            "contact_id": "C003",  # Mike Johnson – will be adjusted later but not main focus
            "transport_id": "T03",
            "pickup_time": "2025-06-16T02:30:00-06:00",
            "dropoff_location": "Westin O'Hare",
            "status": "confirmed",
            "price": 85.0
        }
    ]
    os.makedirs("data/transport_bookings", exist_ok=True)
    with open("data/transport_bookings/transport_bookings.json", "w") as f:
        json.dump({"transport_bookings": transport_bookings}, f, indent=2)

    # ==================== 8. 扰项：过期预订目录 ====================
    # 放一个旧格式的预订文件，里面包含已取消的记录
    old_bookings = [
        {"book_id": "EXPIRED", "name": "Old Booking", "date": "2025-05-01"}
    ]
    os.makedirs("data/archive", exist_ok=True)
    with open("data/archive/old_bookings.json", "w") as f:
        json.dump(old_bookings, f, indent=2)

    # 再放一个非 JSON 文件干扰
    with open("data/readme.txt", "w") as f:
        f.write("This is a readme. Ignore.\n")

    print("Environment built successfully.")

if __name__ == "__main__":
    build_env()
