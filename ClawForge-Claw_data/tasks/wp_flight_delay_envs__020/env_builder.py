import os
import json

def build_env():
    # 创建数据目录
    os.makedirs('data/flights', exist_ok=True)
    os.makedirs('data/hotels', exist_ok=True)
    os.makedirs('data/bookings', exist_ok=True)
    os.makedirs('ops', exist_ok=True)  # 预先创建ops空目录，agent可以写入

    # 航班
    flights = {
        "flights": [
            {"flight_id": "F001", "flight_number": "UA123", "airline": "United Airlines", "origin": "SFO", "destination": "JFK", "departure_time": "2025-03-15T18:00:00", "arrival_time": "2025-03-15T22:00:00", "status": "delayed", "delay_minutes": 120, "gate": "C15"},
            {"flight_id": "F002", "flight_number": "AA456", "airline": "American Airlines", "origin": "ATL", "destination": "BOS", "departure_time": "2025-03-15T20:00:00", "arrival_time": "2025-03-15T23:00:00", "status": "on_time", "delay_minutes": 0, "gate": "A10"},
            {"flight_id": "F003", "flight_number": "DL789", "airline": "Delta Airlines", "origin": "LAX", "destination": "ORD", "departure_time": "2025-03-15T21:00:00", "arrival_time": "2025-03-16T00:30:00", "status": "delayed", "delay_minutes": 15, "gate": "B22"},
        ]
    }
    with open('data/flights/flights.json', 'w') as f:
        json.dump(flights, f, indent=2)

    # 酒店
    hotels = {
        "hotels": [
            {"hotel_id": "H001", "hotel_name": "Hilton Manhattan", "city": "New York", "address": "456 Fashion Ave, New York, NY 10018", "star_rating": 4, "price_per_night": 250.0, "available_rooms": 10, "amenities": ["WiFi", "Gym"]},
            {"hotel_id": "H002", "hotel_name": "Marriott JFK Airport", "city": "New York", "address": "123 Airport Rd, Jamaica, NY 11430", "star_rating": 3, "price_per_night": 180.0, "available_rooms": 5, "amenities": ["Shuttle", "Breakfast"]},
            {"hotel_id": "H003", "hotel_name": "Westin O'Hare", "city": "Chicago", "address": "789 Transit Rd, Rosemont, IL 60018", "star_rating": 4, "price_per_night": 200.0, "available_rooms": 20, "amenities": ["Pool", "Business Center"]},
        ]
    }
    with open('data/hotels/hotels.json', 'w') as f:
        json.dump(hotels, f, indent=2)

    # 酒店预订
    hotel_bookings = {
        "hotel_bookings": [
            {"booking_id": "HB-001", "flight_id": "F001", "hotel_id": "H001", "guest_name": "Jane Doe", "check_in": "2025-03-15", "check_out": "2025-03-16", "status": "confirmed"},
            {"booking_id": "HB-002", "flight_id": "F002", "hotel_id": "H002", "guest_name": "John Smith", "check_in": "2025-03-15", "check_out": "2025-03-16", "status": "confirmed"},
            {"booking_id": "HB-003", "flight_id": "F003", "hotel_id": "H003", "guest_name": "Mike Johnson", "check_in": "2025-03-15", "check_out": "2025-03-17", "status": "confirmed"},
        ]
    }
    with open('data/bookings/hotel_bookings.json', 'w') as f:
        json.dump(hotel_bookings, f, indent=2)

    # 交通预订
    transport_bookings = {
        "transport_bookings": [
            {"booking_id": "TB-001", "flight_id": "F001", "transport_type": "limousine", "service_provider": "Blacklane", "pickup_time": "2025-03-15T22:00:00", "dropoff_location": "Hilton Manhattan", "status": "confirmed"},
            {"booking_id": "TB-002", "flight_id": "F002", "transport_type": "shuttle", "service_provider": "SuperShuttle", "pickup_time": "2025-03-15T23:00:00", "dropoff_location": "Marriott JFK Airport", "status": "confirmed"},
            {"booking_id": "TB-003", "flight_id": "F003", "transport_type": "suv", "service_provider": "Uber", "pickup_time": "2025-03-16T00:30:00", "dropoff_location": "Westin O'Hare", "status": "confirmed"},
        ]
    }
    with open('data/bookings/transport_bookings.json', 'w') as f:
        json.dump(transport_bookings, f, indent=2)

    # 噪声文件
    accounts = {
        "accounts": [
            {"account_id": "A001", "account_name": "corp_travel", "email": "travel@corp.com", "role": "admin", "display_name": "Corporate Travel"},
            {"account_id": "A002", "account_name": "individual", "email": "user@example.com", "role": "user", "display_name": "Individual User"},
        ]
    }
    with open('data/accounts.json', 'w') as f:
        json.dump(accounts, f, indent=2)

    contacts = {
        "contacts": [
            {"contact_id": "C001", "name": "Jane Doe", "email": "jane.doe@example.com", "phone": "+1-555-0101"},
            {"contact_id": "C002", "name": "John Smith", "email": "john.smith@example.com", "phone": "+1-555-0102"},
            {"contact_id": "C003", "name": "Mike Johnson", "email": "mike.johnson@example.com", "phone": "+1-555-0103"},
        ]
    }
    with open('data/contacts.json', 'w') as f:
        json.dump(contacts, f, indent=2)

if __name__ == '__main__':
    build_env()
