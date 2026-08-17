import os
import json
import random

def build_env():
    # 确保目录结构
    dirs = [
        "data/flights",
        "data/hotels",
        "data/transports",
        "data/bookings",
        "ops",
        "logs"
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # ---------- flights.json ----------
    flights = [
        {"flight_id": "FL001", "flight_number": "UA123", "airline": "United Airlines",
         "origin": "SFO", "destination": "JFK",
         "departure_time": "2025-06-15T08:00:00", "arrival_time": "2025-06-15T16:30:00",
         "status": "delayed", "delay_minutes": 45, "gate": "C15"},
        {"flight_id": "FL002", "flight_number": "AA456", "airline": "American Airlines",
         "origin": "LAX", "destination": "BOS",
         "departure_time": "2025-06-15T09:00:00", "arrival_time": "2025-06-15T17:00:00",
         "status": "on_time", "delay_minutes": 0, "gate": "A10"},
        {"flight_id": "FL003", "flight_number": "DL789", "airline": "Delta Airlines",
         "origin": "ATL", "destination": "ORD",
         "departure_time": "2025-06-15T10:00:00", "arrival_time": "2025-06-15T12:00:00",
         "status": "delayed", "delay_minutes": 20, "gate": "B22"}  # 干扰项：另一个延误但无关
    ]
    with open("data/flights/flights.json", "w") as f:
        json.dump({"flights": flights}, f, indent=2)

    # ---------- hotel bookings ----------
    hotel_bookings = [
        {"booking_id": "HB001", "flight_number": "UA123", "hotel_name": "Hilton Manhattan",
         "check_in": "2025-06-15", "nights": 2, "guest": "John Smith"},
        {"booking_id": "HB002", "flight_number": "UA123", "hotel_name": "Marriott JFK Airport",
         "check_in": "2025-06-15", "nights": 1, "guest": "Jane Doe"},
        {"booking_id": "HB003", "flight_number": "AA456", "hotel_name": "Westin O'Hare",
         "check_in": "2025-06-15", "nights": 3, "guest": "Mike Johnson"}  # 干扰：关联正常航班
    ]
    with open("data/bookings/hotel_bookings.json", "w") as f:
        json.dump({"bookings": hotel_bookings}, f, indent=2)

    # ---------- transport bookings ----------
    transport_bookings = [
        {"booking_id": "TB001", "flight_number": "UA123", "type": "limousine",
         "pickup_location": "JFK", "dropoff_location": "Hilton Manhattan", "provider": "Blacklane"},
        {"booking_id": "TB002", "flight_number": "UA123", "type": "shuttle",
         "pickup_location": "JFK", "dropoff_location": "Marriott JFK Airport", "provider": "SuperShuttle"},
        {"booking_id": "TB003", "flight_number": "DL789", "type": "suv",
         "pickup_location": "ORD", "dropoff_location": "Westin O'Hare", "provider": "Uber"}  # 干扰：不同航班
    ]
    with open("data/bookings/transport_bookings.json", "w") as f:
        json.dump({"bookings": transport_bookings}, f, indent=2)

    # ---------- 诱饵：过期备份 ----------
    os.makedirs("backups", exist_ok=True)
    old_flights = [
        {"flight_number": "UA123", "status": "on_time", "delay_minutes": 0}
    ]
    with open("backups/flights_20250610.json", "w") as f:
        json.dump({"flights": old_flights}, f, indent=2)

    # ---------- 干扰日志文件 ----------
    with open("logs/syslog.txt", "w") as f:
        f.write("2025-06-15 07:55:00 INFO Gate assignment updated for UA123\n")
        f.write("2025-06-15 08:10:00 WARN UA123 maintenance delay\n")
        f.write("2025-06-15 08:15:00 INFO DL789 on time\n")

    # ---------- 一个无关的会议数据（增加复杂度） ----------
    conferences = [
        {"conference_id": "C001", "name": "TechSummit", "organizer": "Jane Doe",
         "start_date": "2025-06-16", "end_date": "2025-06-18",
         "location": "New York", "status": "upcoming", "attendees": ["alice@corp.com", "bob@corp.com"]}
    ]
    with open("data/conferences/conferences.json", "w") as f:
        json.dump({"conferences": conferences}, f, indent=2)

if __name__ == "__main__":
    build_env()
