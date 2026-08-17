import os
import json
import shutil

def build_env():
    # 创建数据目录
    os.makedirs("data/flights", exist_ok=True)
    os.makedirs("data/hotels", exist_ok=True)
    os.makedirs("data/accounts", exist_ok=True)
    os.makedirs("data/bookings", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 航班数据
    flights = {
        "flights": [
            {
                "flight_id": "FL001",
                "flight_number": "UA123",
                "airline": "United Airlines",
                "origin": "SFO",
                "destination": "ORD",
                "departure_time": "2025-04-10T06:00:00",
                "arrival_time": "2025-04-10T12:00:00",
                "status": "delayed",
                "delay_minutes": 180,
                "gate": "C15"
            },
            {
                "flight_id": "FL002",
                "flight_number": "DL789",
                "airline": "Delta Airlines",
                "origin": "ATL",
                "destination": "JFK",
                "departure_time": "2025-04-10T08:00:00",
                "arrival_time": "2025-04-10T10:30:00",
                "status": "delayed",
                "delay_minutes": 10,
                "gate": "A10"
            },
            {
                "flight_id": "FL003",
                "flight_number": "AA456",
                "airline": "American Airlines",
                "origin": "LAX",
                "destination": "BOS",
                "departure_time": "2025-04-10T09:00:00",
                "arrival_time": "2025-04-10T15:00:00",
                "status": "on_time",
                "delay_minutes": 0,
                "gate": "B22"
            }
        ]
    }
    with open("data/flights/flights.json", "w") as f:
        json.dump(flights, f, indent=2)

    # 账户数据
    accounts = {
        "accounts": [
            {
                "account_id": "ACC001",
                "account_name": "John Smith",
                "email": "john.smith@example.com",
                "role": "passenger",
                "display_name": "John Smith"
            },
            {
                "account_id": "ACC002",
                "account_name": "Jane Doe",
                "email": "jane.doe@example.com",
                "role": "passenger",
                "display_name": "Jane Doe"
            },
            {
                "account_id": "ACC003",
                "account_name": "Mike Johnson",
                "email": "mike.johnson@example.com",
                "role": "passenger",
                "display_name": "Mike Johnson"
            }
        ]
    }
    with open("data/accounts/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # 酒店预订数据（带有account_id和flight_id关联）
    hotel_bookings = {
        "hotel_bookings": [
            {
                "booking_id": "HB001",
                "account_id": "ACC001",
                "flight_id": "FL001",
                "hotel_id": "HTL001",
                "hotel_name": "Hilton Manhattan",
                "city": "New York",
                "check_in": "2025-04-10",
                "check_out": "2025-04-12",
                "status": "confirmed"
            },
            {
                "booking_id": "HB002",
                "account_id": "ACC002",
                "flight_id": "FL001",
                "hotel_id": "HTL002",
                "hotel_name": "Marriott JFK Airport",
                "city": "New York",
                "check_in": "2025-04-10",
                "check_out": "2025-04-11",
                "status": "confirmed"
            },
            {
                "booking_id": "HB003",
                "account_id": "ACC001",
                "flight_id": "FL002",
                "hotel_id": "HTL003",
                "hotel_name": "Westin O'Hare",
                "city": "Chicago",
                "check_in": "2025-04-10",
                "check_out": "2025-04-13",
                "status": "confirmed"
            },
            {
                "booking_id": "HB004",
                "account_id": "ACC003",
                "flight_id": None,
                "hotel_id": "HTL001",
                "hotel_name": "Hilton Manhattan",
                "city": "New York",
                "check_in": "2025-04-11",
                "check_out": "2025-04-14",
                "status": "confirmed"
            }
        ]
    }
    with open("data/bookings/hotel_bookings.json", "w") as f:
        json.dump(hotel_bookings, f, indent=2)

    # 交通预订数据
    transport_bookings = {
        "transport_bookings": [
            {
                "booking_id": "TB001",
                "account_id": "ACC001",
                "flight_id": "FL001",
                "transport_type": "limousine",
                "service_provider": "Blacklane",
                "pickup_time": "2025-04-10T11:00:00",
                "status": "confirmed"
            },
            {
                "booking_id": "TB002",
                "account_id": "ACC002",
                "flight_id": "FL001",
                "transport_type": "shuttle",
                "service_provider": "SuperShuttle",
                "pickup_time": "2025-04-10T11:30:00",
                "status": "confirmed"
            },
            {
                "booking_id": "TB003",
                "account_id": "ACC001",
                "flight_id": "FL002",
                "transport_type": "suv",
                "service_provider": "Uber",
                "pickup_time": "2025-04-10T08:15:00",
                "status": "confirmed"
            },
            {
                "booking_id": "TB004",
                "account_id": "ACC003",
                "flight_id": None,
                "transport_type": "limousine",
                "service_provider": "Blacklane",
                "pickup_time": "2025-04-11T09:00:00",
                "status": "confirmed"
            }
        ]
    }
    with open("data/bookings/transport_bookings.json", "w") as f:
        json.dump(transport_bookings, f, indent=2)

    # 干扰项：旧备份目录，包含错误版本
    os.makedirs("data/backup", exist_ok=True)
    backup_hotel_bookings = {
        "hotel_bookings": [
            {
                "booking_id": "HB001",
                "account_id": "ACC001",
                "flight_id": "FL001",
                "hotel_id": "HTL001",
                "check_in": "2025-04-10",
                "check_out": "2025-04-12",
                "status": "confirmed"
            },
            {
                "booking_id": "HB002",
                "account_id": "ACC002",
                "flight_id": "FL001",
                "hotel_id": "HTL002",
                "check_in": "2025-04-10",
                "check_out": "2025-04-11",
                "status": "confirmed"
            },
            {
                "booking_id": "HB003",
                "account_id": "ACC001",
                "flight_id": "FL001",  # 旧版本错误关联了FL001，实际上应该是FL002
                "hotel_id": "HTL003",
                "check_in": "2025-04-10",
                "check_out": "2025-04-13",
                "status": "confirmed"
            }
        ]
    }
    with open("data/backup/hotel_bookings_backup.json", "w") as f:
        json.dump(backup_hotel_bookings, f, indent=2)

    # 额外的干扰文本文件
    with open("data/notes.txt", "w") as f:
        f.write("Some random notes about flight operations.\n")

if __name__ == "__main__":
    build_env()
