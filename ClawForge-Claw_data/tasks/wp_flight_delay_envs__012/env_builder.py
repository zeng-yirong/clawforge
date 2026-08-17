import os
import json
import csv
from datetime import datetime, timedelta

def build_env():
    # 创建目录
    os.makedirs("logs", exist_ok=True)
    os.makedirs("bookings", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("flights", exist_ok=True)

    # 航班数据
    flights = [
        {
            "flight_id": "F001",
            "flight_number": "UA123",
            "airline": "United Airlines",
            "origin": "SFO",
            "destination": "ORD",
            "departure_time": "2025-07-15 14:00",
            "arrival_time": "2025-07-15 20:20",
            "status": "delayed",
            "delay_minutes": 180,
            "gate": "C15"
        },
        {
            "flight_id": "F002",
            "flight_number": "DL789",
            "airline": "Delta Airlines",
            "origin": "ATL",
            "destination": "JFK",
            "departure_time": "2025-07-15 16:00",
            "arrival_time": "2025-07-15 18:30",
            "status": "delayed",
            "delay_minutes": 90,
            "gate": "A10"
        },
        {
            "flight_id": "F003",
            "flight_number": "AA456",
            "airline": "American Airlines",
            "origin": "LAX",
            "destination": "BOS",
            "departure_time": "2025-07-15 10:00",
            "arrival_time": "2025-07-15 18:45",
            "status": "on_time",
            "delay_minutes": 0,
            "gate": "B22"
        }
    ]
    with open("flights/flights.json", "w") as f:
        json.dump(flights, f, indent=2)

    # 延误报告CSV (干扰项)
    with open("logs/delay_report.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["flight_number", "delay_minutes", "reason"])
        writer.writerow(["UA123", "180", "mechanical_issue"])
        writer.writerow(["DL789", "90", "crew_rest"])
        writer.writerow(["AA456", "0", ""])

    # 酒店预订
    hotel_bookings = [
        {
            "booking_id": "HB-001",
            "flight_id": "F001",
            "hotel_id": "H003",
            "check_in": "2025-07-15",
            "check_out": "2025-07-17",
            "status": "active"
        },
        {
            "booking_id": "HB-002",
            "flight_id": "F002",
            "hotel_id": "H001",
            "check_in": "2025-07-15",
            "check_out": "2025-07-16",
            "status": "active"
        },
        {
            "booking_id": "HB-003",
            "flight_id": "F001",
            "hotel_id": "H002",
            "check_in": "2025-07-15",
            "check_out": "2025-07-16",
            "status": "cancelled"  # 已取消，不应计入
        },
        {
            "booking_id": "HB-004",
            "flight_id": "F003",
            "hotel_id": "H001",
            "check_in": "2025-07-15",
            "check_out": "2025-07-16",
            "status": "active"  # 关联航班准点，不触发
        }
    ]
    with open("bookings/hotel_bookings.json", "w") as f:
        json.dump(hotel_bookings, f, indent=2)

    # 交通预订
    transport_bookings = [
        {
            "booking_id": "TB-001",
            "flight_id": "F001",
            "transport_type": "shuttle",
            "pickup_datetime": "2025-07-15 20:30",
            "service_area": "ORD",
            "status": "active"
        },
        {
            "booking_id": "TB-002",
            "flight_id": "F002",
            "transport_type": "limousine",
            "pickup_datetime": "2025-07-15 18:45",
            "service_area": "JFK",
            "status": "active"
        },
        {
            "booking_id": "TB-003",
            "flight_id": "F001",
            "transport_type": "suv",
            "pickup_datetime": "2025-07-15 20:30",
            "service_area": "ORD",
            "status": "completed"  # 已完成，不处理
        }
    ]
    with open("bookings/transport_bookings.json", "w") as f:
        json.dump(transport_bookings, f, indent=2)

    # 额外干扰：一个旧日志目录
    os.makedirs("logs/archive", exist_ok=True)
    with open("logs/archive/old_weekly_report.csv", "w") as f:
        f.write("flight,delay\nAA101,0\n")

if __name__ == "__main__":
    build_env()
