import json
import os
import shutil

def build_env():
    # Clean previous state if exists
    for d in ['raw_data', 'ops', 'archive']:
        if os.path.exists(d):
            shutil.rmtree(d)

    # Create directories
    os.makedirs('raw_data', exist_ok=True)
    os.makedirs('ops', exist_ok=True)          # agent will write into it
    os.makedirs('archive', exist_ok=True)      #干扰

    # ===== Flights =====
    flights = [
        {
            "flight_id": "FL001",
            "flight_number": "AA456",
            "airline": "American Airlines",
            "origin": "LAX",
            "destination": "JFK",
            "departure_time": "2025-03-01T17:30:00",
            "arrival_time": "2025-03-02T01:15:00",
            "status": "delayed",
            "delay_minutes": 180,
            "gate": "B22"
        },
        {
            "flight_id": "FL002",
            "flight_number": "DL789",
            "airline": "Delta Airlines",
            "origin": "ATL",
            "destination": "ORD",
            "departure_time": "2025-03-01T14:00:00",
            "arrival_time": "2025-03-01T16:30:00",
            "status": "on_time",
            "delay_minutes": 0,
            "gate": "C15"
        },
        {
            "flight_id": "FL003",
            "flight_number": "UA123",
            "airline": "United Airlines",
            "origin": "SFO",
            "destination": "BOS",
            "departure_time": "2025-03-01T19:00:00",
            "arrival_time": "2025-03-02T03:00:00",
            "status": "delayed",
            "delay_minutes": 45,
            "gate": "A10"
        }
    ]
    with open('raw_data/flights.json', 'w') as f:
        json.dump(flights, f, indent=2)

    # ===== Hotel Bookings =====
    hotel_bookings = [
        {
            "booking_id": "HB001",
            "guest_name": "Jane Doe",
            "flight_id": "FL001",
            "check_in": "2025-03-01",
            "check_out": "2025-03-03",
            "hotel": "Hilton Manhattan",
            "status": "confirmed"
        },
        {
            "booking_id": "HB002",
            "guest_name": "John Smith",
            "flight_id": "FL001",
            "check_in": "2025-03-02",
            "check_out": "2025-03-04",
            "hotel": "Marriott JFK Airport",
            "status": "confirmed"
        },
        {
            "booking_id": "HB003",
            "guest_name": "Mike Johnson",
            "flight_id": "FL002",
            "check_in": "2025-03-01",
            "check_out": "2025-03-03",
            "hotel": "Westin O'Hare",
            "status": "confirmed"
        },
        {
            "booking_id": "HB004",
            "guest_name": "Alice Wang",
            "flight_id": "FL003",
            "check_in": "2025-03-02",
            "check_out": "2025-03-05",
            "hotel": "Hilton Manhattan",
            "status": "confirmed"
        }
    ]
    with open('raw_data/hotel_bookings.json', 'w') as f:
        json.dump(hotel_bookings, f, indent=2)

    # ===== Transport Bookings =====
    transport_bookings = [
        {
            "booking_id": "TB001",
            "guest_name": "Jane Doe",
            "flight_id": "FL001",
            "service_type": "limousine",
            "pickup_time": "2025-03-01T17:00:00",
            "status": "confirmed"
        },
        {
            "booking_id": "TB002",
            "guest_name": "John Smith",
            "flight_id": "FL002",
            "service_type": "shuttle",
            "pickup_time": "2025-03-01T13:30:00",
            "status": "confirmed"
        },
        {
            "booking_id": "TB003",
            "guest_name": "Mike Johnson",
            "flight_id": "FL003",
            "service_type": "suv",
            "pickup_time": "2025-03-01T18:30:00",
            "status": "confirmed"
        }
    ]
    with open('raw_data/transport_bookings.json', 'w') as f:
        json.dump(transport_bookings, f, indent=2)

    # ===== Contacts =====
    contacts = [
        {"contact_id": "C001", "name": "Jane Doe", "email": "jane.doe@example.com"},
        {"contact_id": "C002", "name": "John Smith", "email": "john.smith@example.com"},
        {"contact_id": "C003", "name": "Mike Johnson", "email": "mike.johnson@example.com"},
        {"contact_id": "C004", "name": "Alice Wang", "email": "alice.wang@example.com"}
    ]
    with open('raw_data/contacts.json', 'w') as f:
        json.dump(contacts, f, indent=2)

    # ===== 干扰文件：过期备份 =====
    # 一个旧版本的 booking 备份，包含已取消的记录
    old_bookings = [
        {
            "booking_id": "HB001",
            "guest_name": "Jane Doe",
            "flight_id": "FL001",
            "status": "cancelled"
        }
    ]
    with open('archive/old_hotel_bookings.json', 'w') as f:
        json.dump(old_bookings, f, indent=2)

    # 一个无关的 notes 文件
    with open('archive/notes.txt', 'w') as f:
        f.write("This is an old note. Ignore it.\n")

if __name__ == '__main__':
    build_env()
