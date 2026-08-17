import json, os, datetime

def build():
    # ---- flights ----
    flights = [
        {"flight_id": "FL001", "flight_number": "UA123", "airline": "United Airlines",
         "origin": "SFO", "destination": "ORD", "departure_time": "2025-06-15T18:00:00",
         "arrival_time": "2025-06-15T21:30:00", "status": "delayed", "delay_minutes": 120, "gate": "C15"},
        {"flight_id": "FL002", "flight_number": "AA456", "airline": "American Airlines",
         "origin": "ATL", "destination": "JFK", "departure_time": "2025-06-15T20:00:00",
         "arrival_time": "2025-06-15T22:15:00", "status": "delayed", "delay_minutes": 30, "gate": "A10"},
        {"flight_id": "FL003", "flight_number": "DL789", "airline": "Delta Airlines",
         "origin": "LAX", "destination": "BOS", "departure_time": "2025-06-15T16:00:00",
         "arrival_time": "2025-06-15T20:30:00", "status": "on_time", "delay_minutes": 0, "gate": "B22"},
    ]
    os.makedirs("data/flights", exist_ok=True)
    with open("data/flights/flights.json", "w") as f:
        json.dump({"flights": flights}, f)

    # ---- hotels ----
    hotels = [
        {"hotel_id": "HTL10", "hotel_name": "Hilton Manhattan", "city": "New York",
         "address": "456 Fashion Ave, New York, NY 10018", "star_rating": 4,
         "price_per_night": 250.0, "available_rooms": 10, "amenities": ["wifi", "gym"]},
        {"hotel_id": "HTL11", "hotel_name": "Marriott JFK Airport", "city": "New York",
         "address": "123 Airport Rd, Jamaica, NY 11430", "star_rating": 3,
         "price_per_night": 180.0, "available_rooms": 5, "amenities": ["shuttle", "wifi"]},
        {"hotel_id": "HTL12", "hotel_name": "Westin O'Hare", "city": "Chicago",
         "address": "789 Transit Rd, Rosemont, IL 60018", "star_rating": 4,
         "price_per_night": 220.0, "available_rooms": 8, "amenities": ["pool", "wifi"]},
    ]
    os.makedirs("data/hotels", exist_ok=True)
    with open("data/hotels/hotels.json", "w") as f:
        json.dump({"hotels": hotels}, f)

    # ---- transports ----
    transports = [
        {"transport_id": "TRN01", "transport_type": "limousine", "service_provider": "Blacklane",
         "service_area": "Chicago", "vehicle_type": "luxury", "base_price": 150.0,
         "next_available": "2025-06-15T22:00:00"},
        {"transport_id": "TRN02", "transport_type": "shuttle", "service_provider": "SuperShuttle",
         "service_area": "New York", "vehicle_type": "van", "base_price": 60.0,
         "next_available": "2025-06-15T23:00:00"},
        {"transport_id": "TRN03", "transport_type": "suv", "service_provider": "Uber",
         "service_area": "Chicago", "vehicle_type": "premium", "base_price": 120.0,
         "next_available": "2025-06-15T21:30:00"},
    ]
    os.makedirs("data/transports", exist_ok=True)
    with open("data/transports/transports.json", "w") as f:
        json.dump({"transports": transports}, f)

    # ---- hotel bookings ----
    hotel_bookings = [
        {"booking_id": "HB01", "flight_id": "FL001", "hotel_id": "HTL12",
         "check_in": "2025-06-15", "check_out": "2025-06-17", "status": "active"},
        {"booking_id": "HB02", "flight_id": "FL001", "hotel_id": "HTL11",
         "check_in": "2025-06-16", "check_out": "2025-06-17", "status": "cancelled"},  # 已取消，不计入
        {"booking_id": "HB03", "flight_id": "FL002", "hotel_id": "HTL10",
         "check_in": "2025-06-15", "check_out": "2025-06-16", "status": "active"},     # 另一个航班，延误仅30分钟
        {"booking_id": "HB04", "flight_id": "FL001", "hotel_id": "HTL10",
         "check_in": "2025-06-15", "check_out": "2025-06-18", "status": "active"},
    ]
    # 注意：HB01和HB04是UA123的有效预订，HB02已取消，HB03关联AA456（延误小于60分钟）
    os.makedirs("data/bookings", exist_ok=True)
    with open("data/bookings/hotel_bookings.json", "w") as f:
        json.dump({"hotel_bookings": hotel_bookings}, f)

    # ---- transport bookings ----
    transport_bookings = [
        {"booking_id": "TB01", "flight_id": "FL001", "transport_id": "TRN01",
         "scheduled_time": "2025-06-15T21:45:00", "status": "active"},
        {"booking_id": "TB02", "flight_id": "FL001", "transport_id": "TRN03",
         "scheduled_time": "2025-06-15T22:00:00", "status": "active"},
        {"booking_id": "TB03", "flight_id": "FL003", "transport_id": "TRN02",
         "scheduled_time": "2025-06-15T20:45:00", "status": "active"},   # 准点航班
    ]
    with open("data/bookings/transport_bookings.json", "w") as f:
        json.dump({"transport_bookings": transport_bookings}, f)

    # ---- 干扰文件：过期版本备份 ----
    os.makedirs("data/backup", exist_ok=True)
    with open("data/backup/flights_old.json", "w") as f:
        json.dump({"flights": [{"flight_id": "FL001", "delay_minutes": 0}]}, f)

    # ---- 额外：accounts / contacts (仅作背景) ----
    accounts = [
        {"account_id": "ACC01", "account_name": "Delta Travel", "email": "ops@delta.travel", "role": "coordinator", "display_name": "Delta Ops"},
        {"account_id": "ACC02", "account_name": "United Travel", "email": "ops@united.travel", "role": "coordinator", "display_name": "United Ops"},
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f)

    contacts = [
        {"contact_id": "C01", "name": "Jane Doe", "email": "jane.doe@example.com", "phone": "+1-555-0101"},
        {"contact_id": "C02", "name": "John Smith", "email": "john.smith@example.com", "phone": "+1-555-0102"},
        {"contact_id": "C03", "name": "Mike Johnson", "email": "mike.johnson@example.com", "phone": "+1-555-0103"},
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f)

if __name__ == "__main__":
    build()
