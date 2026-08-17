import os
import json
import shutil
from datetime import datetime, timedelta

def build_env():
    # 确保工作区干净
    for d in ['data', 'ops', 'tmp']:
        if os.path.exists(d):
            shutil.rmtree(d)
        os.makedirs(d, exist_ok=True)

    # 航班数据
    flights = [
        {
            "flight_id": "FL001",
            "flight_number": "AA456",
            "airline": "American Airlines",
            "origin": "ATL",
            "destination": "BOS",
            "departure_time": "2025-03-15 08:00",
            "arrival_time": "2025-03-15 10:15",
            "status": "delayed",
            "delay_minutes": 120,
            "gate": "A10"
        },
        {
            "flight_id": "FL002",
            "flight_number": "DL789",
            "airline": "Delta Airlines",
            "origin": "LAX",
            "destination": "JFK",
            "departure_time": "2025-03-15 09:30",
            "arrival_time": "2025-03-15 13:45",
            "status": "on_time",
            "delay_minutes": 0,
            "gate": "B22"
        },
        {
            "flight_id": "FL003",
            "flight_number": "UA123",
            "airline": "United Airlines",
            "origin": "SFO",
            "destination": "ORD",
            "departure_time": "2025-03-15 07:00",
            "arrival_time": "2025-03-15 11:00",
            "status": "delayed",
            "delay_minutes": 45,
            "gate": "C15"
        }
    ]
    os.makedirs("data/flights", exist_ok=True)
    with open("data/flights/flights.json", "w") as f:
        json.dump({"flights": flights}, f, indent=2)

    # 旅客联系人
    contacts = [
        {"contact_id": "C001", "name": "Jane Doe", "email": "jane.doe@example.com", "phone": "+1-555-0101"},
        {"contact_id": "C002", "name": "John Smith", "email": "john.smith@example.com", "phone": "+1-555-0102"},
        {"contact_id": "C003", "name": "Mike Johnson", "email": "mike.johnson@example.com", "phone": "+1-555-0103"},
        {"contact_id": "C004", "name": "Alice Brown", "email": "alice.brown@example.com", "phone": "+1-555-0104"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # 酒店预订 (部分与AA456关联)
    hotels_data = [
        {
            "hotel_id": "H001",
            "hotel_name": "Hilton Boston",
            "city": "Boston",
            "address": "100 Main St, Boston, MA 02101",
            "star_rating": 4,
            "price_per_night": 250.0,
            "available_rooms": 20,
            "amenities": ["gym", "restaurant"]
        },
        {
            "hotel_id": "H002",
            "hotel_name": "Marriott JFK Airport",
            "city": "New York",
            "address": "123 Airport Rd, Jamaica, NY 11430",
            "star_rating": 5,
            "price_per_night": 350.0,
            "available_rooms": 5,
            "amenities": ["spa", "shuttle"]
        },
        {
            "hotel_id": "H003",
            "hotel_name": "Westin O'Hare",
            "city": "Chicago",
            "address": "789 Transit Rd, Rosemont, IL 60018",
            "star_rating": 4,
            "price_per_night": 200.0,
            "available_rooms": 30,
            "amenities": ["pool", "bar"]
        }
    ]
    with open("data/hotels/hotels.json", "w") as f:
        json.dump({"hotels": hotels_data}, f, indent=2)

    # 酒店预订记录（bookings）
    hotel_bookings = [
        {"booking_id": "HB001", "flight_id": "FL001", "contact_id": "C001", "hotel_id": "H001", "check_in": "2025-03-15", "check_out": "2025-03-17", "status": "confirmed"},
        {"booking_id": "HB002", "flight_id": "FL001", "contact_id": "C002", "hotel_id": "H001", "check_in": "2025-03-15", "check_out": "2025-03-16", "status": "confirmed"},
        {"booking_id": "HB003", "flight_id": "FL002", "contact_id": "C003", "hotel_id": "H002", "check_in": "2025-03-15", "check_out": "2025-03-18", "status": "confirmed"},
        {"booking_id": "HB004", "flight_id": "FL001", "contact_id": "C004", "hotel_id": "H001", "check_in": "2025-03-15", "check_out": "2025-03-16", "status": "cancelled"},  # 已取消，干扰项
        {"booking_id": "HB005", "flight_id": "FL003", "contact_id": "C001", "hotel_id": "H003", "check_in": "2025-03-15", "check_out": "2025-03-16", "status": "confirmed"}
    ]
    with open("data/hotel_bookings.json", "w") as f:
        json.dump({"hotel_bookings": hotel_bookings}, f, indent=2)

    # 交通预订
    transport_bookings = [
        {"booking_id": "TB001", "flight_id": "FL001", "contact_id": "C001", "transport_type": "limousine", "pickup_time": "2025-03-15 10:00", "status": "confirmed"},
        {"booking_id": "TB002", "flight_id": "FL001", "contact_id": "C002", "transport_type": "shuttle", "pickup_time": "2025-03-15 10:15", "status": "confirmed"},
        {"booking_id": "TB003", "flight_id": "FL002", "contact_id": "C003", "transport_type": "suv", "pickup_time": "2025-03-15 14:00", "status": "confirmed"},
        {"booking_id": "TB004", "flight_id": "FL001", "contact_id": "C004", "transport_type": "limousine", "pickup_time": "2025-03-15 10:00", "status": "cancelled"}  # 已取消
    ]
    with open("data/transport_bookings.json", "w") as f:
        json.dump({"transport_bookings": transport_bookings}, f, indent=2)

    # 额外干扰文件：tmp 目录
    with open("tmp/scratch_notes.txt", "w") as f:
        f.write("AA456可能晚点，需确认影响。\n")

    # 额外脏数据：一个 CSV 文件，部分字段缺失（无关，但增加复杂度）
    import csv
    with open("data/extra_mapping.csv", "w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["flight_id", "contact_id", "note"])
        writer.writerow(["FL001", "C001", "VIP"])
        writer.writerow(["FL001", "C002", "member"])
        writer.writerow(["", "C003", ""])  # 脏行

if __name__ == "__main__":
    build_env()
