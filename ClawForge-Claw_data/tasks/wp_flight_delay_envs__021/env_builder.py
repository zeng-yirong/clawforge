import os
import json
import random

def build_env():
    # 创建 data/ 和 ops/ 目录
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # ========== flights.json ==========
    flights = [
        {
            "flight_id": "AA456",
            "flight_number": "AA456",
            "airline": "American Airlines",
            "origin": "ATL",
            "destination": "JFK",
            "departure_time": "2025-04-15T06:00:00",
            "arrival_time": "2025-04-15T08:30:00",
            "status": "delayed",
            "delay_minutes": 120,
            "gate": "A10"
        },
        {
            "flight_id": "DL789",
            "flight_number": "DL789",
            "airline": "Delta Airlines",
            "origin": "LAX",
            "destination": "ORD",
            "departure_time": "2025-04-15T10:00:00",
            "arrival_time": "2025-04-15T14:00:00",
            "status": "on_time",
            "delay_minutes": 0,
            "gate": "B22"
        },
        {
            "flight_id": "UA123",
            "flight_number": "UA123",
            "airline": "United Airlines",
            "origin": "SFO",
            "destination": "BOS",
            "departure_time": "2025-04-15T12:00:00",
            "arrival_time": "2025-04-15T18:30:00",
            "status": "cancelled",
            "delay_minutes": 0,
            "gate": "C15"
        }
    ]
    with open("data/flights.json", "w") as f:
        json.dump({"flights": flights}, f, indent=2)

    # ========== hotel_bookings.json ==========
    hotel_bookings = [
        {
            "booking_id": "HB001",
            "flight_id": "AA456",
            "hotel_id": "HIL01",
            "guest_name": "Jane Doe",
            "checkin": "2025-04-15",
            "checkout": "2025-04-17",
            "status": "active"
        },
        {
            "booking_id": "HB002",
            "flight_id": "AA456",
            "hotel_id": "MAR01",
            "guest_name": "John Smith",
            "checkin": "2025-04-16",
            "checkout": "2025-04-18",
            "status": "active"
        },
        {
            "booking_id": "HB003",
            "flight_id": "DL789",
            "hotel_id": "WST01",
            "guest_name": "Mike Johnson",
            "checkin": "2025-04-15",
            "checkout": "2025-04-16",
            "status": "active"
        },
        {
            "booking_id": "HB004",
            "flight_id": "UA123",
            "hotel_id": "HIL01",
            "guest_name": "Alice Brown",
            "checkin": "2025-04-17",
            "checkout": "2025-04-19",
            "status": "active"
        },
        {
            "booking_id": "HB005",
            "flight_id": "NONEXIST",
            "hotel_id": "MAR01",
            "guest_name": "Tom White",
            "checkin": "2025-04-18",
            "checkout": "2025-04-20",
            "status": "active"
        },
        {
            "booking_id": "HB006",
            "flight_id": "AA456",
            "hotel_id": "WST01",
            "guest_name": "Diana Green",
            "checkin": "2025-04-15",
            "checkout": "2025-04-16",
            "status": "cancelled"
        }
    ]
    # 打乱顺序，增加干扰
    random.shuffle(hotel_bookings)
    with open("data/hotel_bookings.json", "w") as f:
        json.dump({"hotel_bookings": hotel_bookings}, f, indent=2)

    # ========== transport_bookings.json ==========
    transport_bookings = [
        {
            "booking_id": "TB001",
            "flight_id": "AA456",
            "transport_type": "limousine",
            "provider": "Blacklane",
            "pickup_datetime": "2025-04-15T08:00:00",
            "status": "confirmed"
        },
        {
            "booking_id": "TB002",
            "flight_id": "DL789",
            "transport_type": "shuttle",
            "provider": "SuperShuttle",
            "pickup_datetime": "2025-04-15T13:30:00",
            "status": "confirmed"
        },
        {
            "booking_id": "TB003",
            "flight_id": "AA456",
            "transport_type": "suv",
            "provider": "Uber",
            "pickup_datetime": "2025-04-15T08:15:00",
            "status": "cancelled"
        }
    ]
    random.shuffle(transport_bookings)
    with open("data/transport_bookings.json", "w") as f:
        json.dump({"transport_bookings": transport_bookings}, f, indent=2)

    # ========== 额外的干扰文件（无关但存在） ==========
    # 添加一个 contact.json 但关联不大，可以干扰 agent 读取所有文件
    contacts = [
        {"contact_id": "C001", "name": "Jane Doe", "email": "jane.doe@example.com"},
        {"contact_id": "C002", "name": "John Smith", "email": "john.smith@example.com"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

if __name__ == "__main__":
    build_env()
