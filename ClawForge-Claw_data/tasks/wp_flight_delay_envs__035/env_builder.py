import json
import os

def build_env():
    # 创建目录结构
    os.makedirs("data/flights", exist_ok=True)
    os.makedirs("data/hotel_bookings", exist_ok=True)
    os.makedirs("data/transport_bookings", exist_ok=True)
    os.makedirs("data/contacts", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # 空目录，等待 agent 写入

    # ========== 航班数据 ==========
    flights = [
        {
            "flight_id": "F001",
            "flight_number": "UA123",
            "airline": "United Airlines",
            "origin": "SFO",
            "destination": "ORD",
            "departure_time": "2025-03-15 14:00",
            "arrival_time": "2025-03-15 20:00",
            "status": "delayed",
            "delay_minutes": 120,
            "gate": "C15"
        },
        {
            "flight_id": "F002",
            "flight_number": "AA456",
            "airline": "American Airlines",
            "origin": "ATL",
            "destination": "JFK",
            "departure_time": "2025-03-15 15:30",
            "arrival_time": "2025-03-15 17:45",
            "status": "on_time",
            "delay_minutes": 0,
            "gate": "A10"
        },
        {
            "flight_id": "F003",
            "flight_number": "DL789",
            "airline": "Delta Airlines",
            "origin": "LAX",
            "destination": "BOS",
            "departure_time": "2025-03-15 17:00",
            "arrival_time": "2025-03-15 23:30",
            "status": "on_time",
            "delay_minutes": 0,
            "gate": "B22"
        }
    ]
    with open("data/flights/flights.json", "w") as f:
        json.dump({"flights": flights}, f, indent=2)

    # ========== 酒店预订 ==========
    hotel_bookings = [
        {
            "booking_id": "HB001",
            "guest_name": "John Smith",
            "flight_id": "F001",
            "hotel_id": "H01",
            "check_in": "2025-03-15",
            "check_out": "2025-03-17",
            "status": "confirmed"           # UA123 受影响
        },
        {
            "booking_id": "HB002",
            "guest_name": "Jane Doe",
            "flight_id": "F001",
            "hotel_id": "H02",
            "check_in": "2025-03-15",
            "check_out": "2025-03-16",
            "status": "confirmed"           # UA123 受影响
        },
        {
            "booking_id": "HB003",
            "guest_name": "Mike Johnson",
            "flight_id": "F002",
            "hotel_id": "H03",
            "check_in": "2025-03-15",
            "check_out": "2025-03-18",
            "status": "confirmed"           # 关联 AA456，但该航班准点，不需要调整
        },
        {
            "booking_id": "HB004",
            "guest_name": "Alice Brown",
            "flight_id": "F001",
            "hotel_id": "H01",
            "check_in": "2025-03-14",
            "check_out": "2025-03-15",
            "status": "checked_out"         # 已离店，干扰项
        },
        {
            "booking_id": "HB005",
            "guest_name": "Tom Lee",
            "flight_id": "F001",
            "hotel_id": "H02",
            "check_in": "2025-03-16",
            "check_out": "2025-03-18",
            "status": "cancelled"           # 已取消，干扰项
        }
    ]
    with open("data/hotel_bookings/hotel_bookings.json", "w") as f:
        json.dump({"hotel_bookings": hotel_bookings}, f, indent=2)

    # ========== 交通预订 ==========
    transport_bookings = [
        {
            "booking_id": "TB001",
            "passenger": "John Smith",
            "flight_id": "F001",
            "transport_type": "limousine",
            "pickup_time": "2025-03-15 20:00",
            "status": "confirmed"           # UA123 受影响
        },
        {
            "booking_id": "TB002",
            "passenger": "Jane Doe",
            "flight_id": "F002",
            "transport_type": "shuttle",
            "pickup_time": "2025-03-15 17:45",
            "status": "confirmed"           # 关联 AA456，准点，不需要
        },
        {
            "booking_id": "TB003",
            "passenger": "Mike Johnson",
            "flight_id": "F003",
            "transport_type": "suv",
            "pickup_time": "2025-03-15 23:30",
            "status": "confirmed"           # 关联 DL789，准点，不需要
        },
        {
            "booking_id": "TB004",
            "passenger": "Alice Brown",
            "flight_id": "F001",
            "transport_type": "shuttle",
            "pickup_time": "2025-03-15 20:00",
            "status": "completed"           # 已完成，干扰项
        }
    ]
    with open("data/transport_bookings/transport_bookings.json", "w") as f:
        json.dump({"transport_bookings": transport_bookings}, f, indent=2)

    # ========== 联系人 ==========
    contacts = [
        {"contact_id": "C001", "name": "John Smith", "email": "john.smith@example.com", "phone": "+1-555-0101"},
        {"contact_id": "C002", "name": "Jane Doe", "email": "jane.doe@example.com", "phone": "+1-555-0102"},
        {"contact_id": "C003", "name": "Mike Johnson", "email": "mike.johnson@example.com", "phone": "+1-555-0103"},
        {"contact_id": "C004", "name": "Alice Brown", "email": "alice.brown@example.com", "phone": "+1-555-0104"},
        {"contact_id": "C005", "name": "Tom Lee", "email": "tom.lee@example.com", "phone": "+1-555-0105"}
    ]
    with open("data/contacts/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

if __name__ == "__main__":
    build_env()
