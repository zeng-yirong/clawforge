import os
import json
from datetime import datetime, timedelta

def build_env():
    # 创建目录结构
    dirs = [
        "data/flights",
        "data/hotels",
        "data/transports",
        "data/bookings",
        "backup",
        "ops",
        "logs",
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # ========== 航班数据 ==========
    # 核心航班 AA456 延误 90 分钟
    flights = [
        {
            "flight_id": "F001",
            "flight_number": "AA456",
            "airline": "American Airlines",
            "origin": "LAX",
            "destination": "JFK",
            "departure_time": "2025-04-10T15:30",
            "arrival_time": "2025-04-10T18:00",
            "status": "delayed",
            "delay_minutes": 90,
            "gate": "A10"
        },
        {
            "flight_id": "F002",
            "flight_number": "DL789",
            "airline": "Delta Airlines",
            "origin": "ATL",
            "destination": "BOS",
            "departure_time": "2025-04-10T14:00",
            "arrival_time": "2025-04-10T16:30",
            "status": "on_time",
            "delay_minutes": 0,
            "gate": "B22"
        },
        {
            "flight_id": "F003",
            "flight_number": "UA123",
            "airline": "United Airlines",
            "origin": "SFO",
            "destination": "ORD",
            "departure_time": "2025-04-10T17:00",
            "arrival_time": "2025-04-10T19:00",
            "status": "delayed",
            "delay_minutes": 30,
            "gate": "C15"
        }
    ]
    with open("data/flights/flights.json", "w") as f:
        json.dump({"flights": flights}, f, indent=2)

    # ========== 干扰：旧版本航班数据（诱饵，flight_id混乱） ==========
    backup_flights = [
        {
            "flight_id": "OLD_F001",
            "flight_number": "AA456",
            "airline": "American Airlines",
            "origin": "LAX",
            "destination": "JFK",
            "departure_time": "2025-04-10T15:30",
            "arrival_time": "2025-04-10T18:00",
            "status": "on_time",
            "delay_minutes": 0,
            "gate": "A10"
        }
    ]
    with open("backup/flights_backup.json", "w") as f:
        json.dump({"flights": backup_flights}, f, indent=2)

    # ========== 酒店数据 ==========
    hotels = [
        {
            "hotel_id": "H001",
            "hotel_name": "Hilton Manhattan",
            "city": "New York",
            "address": "456 Fashion Ave, New York, NY 10018",
            "star_rating": 4,
            "price_per_night": 250.0,
            "available_rooms": 10,
            "amenities": ["WiFi", "Gym", "Restaurant"]
        },
        {
            "hotel_id": "H002",
            "hotel_name": "Marriott JFK Airport",
            "city": "New York",
            "address": "123 Airport Rd, Jamaica, NY 11430",
            "star_rating": 3,
            "price_per_night": 180.0,
            "available_rooms": 5,
            "amenities": ["Shuttle", "WiFi"]
        },
        {
            "hotel_id": "H003",
            "hotel_name": "Westin O'Hare",
            "city": "Chicago",
            "address": "789 Transit Rd, Rosemont, IL 60018",
            "star_rating": 4,
            "price_per_night": 220.0,
            "available_rooms": 8,
            "amenities": ["Pool", "WiFi", "Business Center"]
        }
    ]
    with open("data/hotels/hotels.json", "w") as f:
        json.dump({"hotels": hotels}, f, indent=2)

    # ========== 交通数据 ==========
    transports = [
        {
            "transport_id": "T001",
            "transport_type": "limousine",
            "service_provider": "Blacklane",
            "service_area": "JFK",
            "vehicle_type": "luxury",
            "base_price": 120.0,
            "next_available": "2025-04-10T19:30"
        },
        {
            "transport_id": "T002",
            "transport_type": "shuttle",
            "service_provider": "SuperShuttle",
            "service_area": "BOS",
            "vehicle_type": "van",
            "base_price": 45.0,
            "next_available": "2025-04-10T17:00"
        },
        {
            "transport_id": "T003",
            "transport_type": "suv",
            "service_provider": "Uber",
            "service_area": "ORD",
            "vehicle_type": "premium",
            "base_price": 80.0,
            "next_available": "2025-04-10T19:30"
        }
    ]
    with open("data/transports/transports.json", "w") as f:
        json.dump({"transports": transports}, f, indent=2)

    # ========== 预订数据（核心 + 干扰） ==========
    bookings = [
        # --- 真正受影响的预订：Jane Doe，AA456，Hilton Manhattan，Blacklane limousine
        {
            "booking_id": "B001",
            "passenger": "Jane Doe",
            "email": "jane.doe@example.com",
            "phone": "+1-555-0101",
            "flight_id": "F001",
            "hotel_id": "H001",
            "transport_id": "T001",
            "hotel_checkin": "2025-04-10T15:00",
            "hotel_checkout": "2025-04-13T11:00",
            "transport_pickup_time": "2025-04-10T18:00",
            "transport_pickup_location": "JFK Airport Terminal 4"
        },
        # --- 未受影响的预订：航班准点，酒店、交通没问题
        {
            "booking_id": "B002",
            "passenger": "John Smith",
            "email": "john.smith@example.com",
            "phone": "+1-555-0102",
            "flight_id": "F002",
            "hotel_id": "H002",
            "transport_id": "T002",
            "hotel_checkin": "2025-04-10T16:30",
            "hotel_checkout": "2025-04-12T10:00",
            "transport_pickup_time": "2025-04-10T16:30",
            "transport_pickup_location": "BOS Arrivals"
        },
        # --- 诱饵：航班延误30分钟但时间仍足够，交通不调整（或忽略）
        {
            "booking_id": "B003",
            "passenger": "Mike Johnson",
            "email": "mike.johnson@example.com",
            "phone": "+1-555-0103",
            "flight_id": "F003",
            "hotel_id": "H003",
            "transport_id": "T003",
            "hotel_checkin": "2025-04-10T20:00",   # 19:00到，延误30分钟到19:30，完全来得及
            "hotel_checkout": "2025-04-12T10:00",
            "transport_pickup_time": "2025-04-10T19:00",
            "transport_pickup_location": "ORD Terminal 3"
        },
        # --- 干扰：预订记录不完整（缺少 flight_id）
        {
            "booking_id": "B004",
            "passenger": "Invalid Guest",
            "email": "invalid@example.com",
            "phone": "+1-555-0000",
            "flight_id": None,
            "hotel_id": "H001",
            "transport_id": "T001",
            "hotel_checkin": "2025-04-10T12:00",
            "hotel_checkout": "2025-04-11T10:00",
            "transport_pickup_time": "2025-04-10T12:30",
            "transport_pickup_location": "JFK"
        }
    ]
    with open("data/bookings/bookings.json", "w") as f:
        json.dump({"bookings": bookings}, f, indent=2)

    # ========== 额外干扰：日志文件，无关内容 ==========
    with open("logs/system_health.log", "w") as f:
        f.write("2025-04-10 14:00:00 INFO All systems nominal\n")
        f.write("2025-04-10 15:00:00 WARN Flight AA456 delay detected\n")
        f.write("2025-04-10 16:00:00 INFO Hotel booking confirmed\n")

    # 空的 ops 目录（agent 应在此生成结果）
    # 已经创建

    print("Environment built successfully.")

if __name__ == "__main__":
    build_env()
