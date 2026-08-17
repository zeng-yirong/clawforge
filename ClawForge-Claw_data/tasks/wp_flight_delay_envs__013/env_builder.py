import os
import json

def build_env():
    # ----- 航班数据 -----
    flights = {
        "flights": [
            {
                "flight_id": "FL-001",
                "flight_number": "UA123",
                "airline": "United Airlines",
                "origin": "LAX",
                "destination": "JFK",
                "departure_time": "2025-07-15T14:00:00",
                "arrival_time": "2025-07-15T22:00:00",
                "status": "delayed",
                "delay_minutes": 120,
                "gate": "B22"
            },
            {
                "flight_id": "FL-002",
                "flight_number": "DL789",
                "airline": "Delta Airlines",
                "origin": "ATL",
                "destination": "ORD",
                "departure_time": "2025-07-15T08:00:00",
                "arrival_time": "2025-07-15T10:00:00",
                "status": "on_time",
                "delay_minutes": 0,
                "gate": "C15"
            },
            {
                "flight_id": "FL-003",
                "flight_number": "AA456",
                "airline": "American Airlines",
                "origin": "SFO",
                "destination": "BOS",
                "departure_time": "2025-07-15T18:00:00",
                "arrival_time": "2025-07-15T23:00:00",
                "status": "cancelled",
                "delay_minutes": 0,
                "gate": "A10"
            }
        ]
    }

    # ----- 旧航班备份（干扰） -----
    old_flights = {
        "flights": [
            {
                "flight_id": "FL-001",
                "flight_number": "UA123",
                "airline": "United Airlines",
                "origin": "LAX",
                "destination": "JFK",
                "departure_time": "2025-07-15T14:00:00",
                "arrival_time": "2025-07-15T22:00:00",
                "status": "on_time",
                "delay_minutes": 0,
                "gate": "B22"
            }
        ]
    }

    # ----- 酒店数据 -----
    hotels = {
        "hotels": [
            {
                "hotel_id": "HTL-001",
                "hotel_name": "Marriott JFK Airport",
                "city": "New York",
                "address": "123 Airport Rd, Jamaica, NY 11430",
                "star_rating": 4,
                "price_per_night": 189.0,
                "available_rooms": 50,
                "amenities": ["WiFi", "Gym", "Restaurant"]
            },
            {
                "hotel_id": "HTL-002",
                "hotel_name": "Hilton Manhattan",
                "city": "New York",
                "address": "456 Fashion Ave, New York, NY 10018",
                "star_rating": 5,
                "price_per_night": 299.0,
                "available_rooms": 20,
                "amenities": ["Spa", "Pool", "Bar"]
            }
        ]
    }

    # ----- 酒店预订 -----
    hotel_bookings = {
        "bookings": [
            {
                "booking_id": "HB-001",
                "flight_id": "FL-001",
                "guest_name": "John Smith",
                "guest_email": "john.smith@example.com",
                "hotel_id": "HTL-001",
                "checkin_date": "2025-07-15",
                "checkout_date": "2025-07-17",
                "status": "confirmed"
            },
            {
                "booking_id": "HB-002",
                "flight_id": "FL-002",
                "guest_name": "Jane Doe",
                "guest_email": "jane.doe@example.com",
                "hotel_id": "HTL-002",
                "checkin_date": "2025-07-15",
                "checkout_date": "2025-07-16",
                "status": "confirmed"
            },
            {
                "booking_id": "HB-003",
                "flight_id": "FL-003",
                "guest_name": "Mike Johnson",
                "guest_email": "mike.johnson@example.com",
                "hotel_id": "HTL-001",
                "checkin_date": "2025-07-16",
                "checkout_date": "2025-07-18",
                "status": "confirmed"
            }
        ]
    }

    # ----- 交通数据 -----
    transports = {
        "transports": [
            {
                "transport_id": "TRP-001",
                "transport_type": "shuttle",
                "service_provider": "SuperShuttle",
                "service_area": "JFK",
                "vehicle_type": "van",
                "base_price": 25.0,
                "next_available": "2025-07-15T22:30:00"
            },
            {
                "transport_id": "TRP-002",
                "transport_type": "limousine",
                "service_provider": "Blacklane",
                "service_area": "Manhattan",
                "vehicle_type": "luxury",
                "base_price": 120.0,
                "next_available": "2025-07-16T00:00:00"
            }
        ]
    }

    # ----- 交通预订 -----
    transport_bookings = {
        "bookings": [
            {
                "booking_id": "TB-001",
                "flight_id": "FL-001",
                "guest_name": "John Smith",
                "guest_email": "john.smith@example.com",
                "transport_id": "TRP-001",
                "pickup_time": "2025-07-15T22:30:00",
                "pickup_location": "JFK Terminal 4",
                "dropoff_location": "Marriott JFK Airport",
                "status": "confirmed"
            },
            {
                "booking_id": "TB-002",
                "flight_id": "FL-002",
                "guest_name": "Jane Doe",
                "guest_email": "jane.doe@example.com",
                "transport_id": "TRP-002",
                "pickup_time": "2025-07-15T10:30:00",
                "pickup_location": "ATL Airport",
                "dropoff_location": "Hilton Manhattan",
                "status": "confirmed"
            }
        ]
    }

    # ----- 联系人（仅用于混淆）-----
    contacts = {
        "contacts": [
            {
                "contact_id": "CT-001",
                "name": "John Smith",
                "email": "john.smith@example.com",
                "phone": "+1-555-0101"
            },
            {
                "contact_id": "CT-002",
                "name": "Jane Doe",
                "email": "jane.doe@example.com",
                "phone": "+1-555-0102"
            },
            {
                "contact_id": "CT-003",
                "name": "Mike Johnson",
                "email": "mike.johnson@example.com",
                "phone": "+1-555-0103"
            }
        ]
    }

    # ----- 写文件 -----
    os.makedirs("data/flights/backup", exist_ok=True)
    os.makedirs("data/hotels", exist_ok=True)
    os.makedirs("data/hotel_bookings", exist_ok=True)
    os.makedirs("data/transports", exist_ok=True)
    os.makedirs("data/transport_bookings", exist_ok=True)
    os.makedirs("data/contacts", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    with open("data/flights/flights.json", "w") as f:
        json.dump(flights, f, indent=2)
    with open("data/flights/backup/flights_old.json", "w") as f:
        json.dump(old_flights, f, indent=2)
    with open("data/hotels/hotels.json", "w") as f:
        json.dump(hotels, f, indent=2)
    with open("data/hotel_bookings/bookings.json", "w") as f:
        json.dump(hotel_bookings, f, indent=2)
    with open("data/transports/transports.json", "w") as f:
        json.dump(transports, f, indent=2)
    with open("data/transport_bookings/bookings.json", "w") as f:
        json.dump(transport_bookings, f, indent=2)
    with open("data/contacts/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # 额外干扰文件（格式错误的JSON、无关txt）
    with open("data/irrelevant_log.txt", "w") as f:
        f.write("This is just a log, ignore me.")
    with open("data/config.ini", "w") as f:
        f.write("[database]\nhost=localhost\nport=5432\n")

if __name__ == "__main__":
    build_env()
