import json
import os
import shutil

def build_env():
    # 清理旧数据（确保每次重建干净）
    for d in ["data", "ops"]:
        if os.path.exists(d):
            shutil.rmtree(d)
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # ---------- 航班数据 ----------
    flights = [
        {
            "flight_id": "FL001",
            "flight_number": "UA123",
            "airline": "United Airlines",
            "origin": "SFO",
            "destination": "ORD",
            "departure_time": "2025-04-01T18:30:00",
            "arrival_time": "2025-04-01T23:15:00",
            "status": "delayed",
            "delay_minutes": 120,
            "gate": "A10"
        },
        {
            "flight_id": "FL002",
            "flight_number": "DL789",
            "airline": "Delta Airlines",
            "origin": "ATL",
            "destination": "JFK",
            "departure_time": "2025-04-01T20:00:00",
            "arrival_time": "2025-04-01T22:30:00",
            "status": "on_time",
            "delay_minutes": 0,
            "gate": "B22"
        },
        {
            "flight_id": "FL003",
            "flight_number": "AA456",
            "airline": "American Airlines",
            "origin": "LAX",
            "destination": "BOS",
            "departure_time": "2025-04-01T19:45:00",
            "arrival_time": "2025-04-02T01:15:00",
            "status": "delayed",
            "delay_minutes": 30,
            "gate": "C15"
        }
    ]
    with open("data/flights.json", "w") as f:
        json.dump({"flights": flights}, f, indent=2)

    # ---------- 酒店 ----------
    hotels = [
        {"hotel_id": "HTL01", "hotel_name": "Hilton Manhattan", "city": "New York", "star_rating": 4, "price_per_night": 280.0, "available_rooms": 15, "amenities": ["wifi", "pool"]},
        {"hotel_id": "HTL02", "hotel_name": "Marriott JFK Airport", "city": "New York", "star_rating": 3, "price_per_night": 190.0, "available_rooms": 32, "amenities": ["shuttle", "gym"]},
        {"hotel_id": "HTL03", "hotel_name": "Westin O'Hare", "city": "Chicago", "star_rating": 4, "price_per_night": 250.0, "available_rooms": 8, "amenities": ["bar", "business_center"]}
    ]
    with open("data/hotels.json", "w") as f:
        json.dump({"hotels": hotels}, f, indent=2)

    # ---------- 交通工具 ----------
    transports = [
        {"transport_id": "TR001", "transport_type": "shuttle", "service_provider": "SuperShuttle", "service_area": "JFK", "vehicle_type": "van", "base_price": 45.00, "next_available": "2025-04-01T22:00:00"},
        {"transport_id": "TR002", "transport_type": "limousine", "service_provider": "Blacklane", "service_area": "LGA", "vehicle_type": "luxury", "base_price": 120.00, "next_available": "2025-04-02T00:30:00"},
        {"transport_id": "TR003", "transport_type": "suv", "service_provider": "Uber", "service_area": "ORD", "vehicle_type": "premium", "base_price": 85.00, "next_available": "2025-04-01T21:15:00"}
    ]
    with open("data/transports.json", "w") as f:
        json.dump({"transports": transports}, f, indent=2)

    # ---------- 联系人 ----------
    contacts = [
        {"contact_id": "C001", "name": "Jane Doe", "email": "jane.doe@example.com", "phone": "+1-555-0101"},
        {"contact_id": "C002", "name": "John Smith", "email": "john.smith@example.com", "phone": "+1-555-0102"},
        {"contact_id": "C003", "name": "Mike Johnson", "email": "mike.johnson@example.com", "phone": "+1-555-0103"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # ---------- 酒店预订 ----------
    hotel_bookings = [
        {
            "booking_id": "BKH01",
            "flight_id": "FL001",
            "hotel_id": "HTL01",
            "contact_id": "C001",
            "check_in": "2025-04-01",
            "check_out": "2025-04-03",
            "status": "confirmed"
        },
        {
            "booking_id": "BKH02",
            "flight_id": "FL003",
            "hotel_id": "HTL02",
            "contact_id": "C002",
            "check_in": "2025-04-01",
            "check_out": "2025-04-02",
            "status": "cancelled"      # 干扰：关联延误航班但已取消
        },
        {
            "booking_id": "BKH03",
            "flight_id": "FL001",
            "hotel_id": "HTL03",
            "contact_id": "C003",
            "check_in": "2025-04-01",
            "check_out": "2025-04-02",
            "status": "cancelled"      # 干扰：同一延误航班但已取消
        }
    ]
    with open("data/hotel_bookings.json", "w") as f:
        json.dump({"hotel_bookings": hotel_bookings}, f, indent=2)

    # ---------- 交通预订 ----------
    transport_bookings = [
        {
            "booking_id": "BKT01",
            "flight_id": "FL001",
            "transport_id": "TR001",
            "contact_id": "C001",
            "pickup_time": "2025-04-01T21:00:00",
            "status": "confirmed"
        },
        {
            "booking_id": "BKT02",
            "flight_id": "FL002",
            "transport_id": "TR002",
            "contact_id": "C002",
            "pickup_time": "2025-04-01T21:30:00",
            "status": "confirmed"      # 干扰：航班正常，无关
        },
        {
            "booking_id": "BKT03",
            "flight_id": "FL003",
            "transport_id": "TR003",
            "contact_id": "C003",
            "pickup_time": "2025-04-01T20:00:00",
            "status": "cancelled"      # 干扰：延误航班但取消
        }
    ]
    with open("data/transport_bookings.json", "w") as f:
        json.dump({"transport_bookings": transport_bookings}, f, indent=2)

    # ---------- 额外干扰项：一个格式错误的文件 ----------
    with open("data/unused_dump.csv", "w") as f:
        f.write("noise,data\n1,irrelevant\n")

if __name__ == "__main__":
    build_env()
