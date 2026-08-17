import json
import os

def build_env():
    # 创建目录结构
    os.makedirs("data/flights", exist_ok=True)
    os.makedirs("data/hotels", exist_ok=True)
    os.makedirs("data/transports", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 1. 航班数据 (flights.json)
    flights = [
        {
            "flight_id": "UA123",
            "flight_number": "UA123",
            "airline": "United Airlines",
            "origin": "SFO",
            "destination": "ORD",
            "departure_time": "2025-03-20 18:00",
            "arrival_time": "2025-03-20 22:00",
            "status": "delayed",
            "delay_minutes": 120,
            "gate": "C15"
        },
        {
            "flight_id": "AA456",
            "flight_number": "AA456",
            "airline": "American Airlines",
            "origin": "LAX",
            "destination": "JFK",
            "departure_time": "2025-03-20 14:00",
            "arrival_time": "2025-03-20 20:00",
            "status": "delayed",
            "delay_minutes": 90,
            "gate": "A10"
        },
        {
            "flight_id": "DL789",
            "flight_number": "DL789",
            "airline": "Delta Airlines",
            "origin": "ATL",
            "destination": "BOS",
            "departure_time": "2025-03-20 16:00",
            "arrival_time": "2025-03-20 18:30",
            "status": "on_time",
            "delay_minutes": 0,
            "gate": "B22"
        }
    ]
    with open("data/flights/flights.json", "w") as f:
        json.dump({"flights": flights}, f, indent=2)

    # 2. 酒店数据 (hotels.json) - 仅作为参考
    hotels = [
        {"hotel_id": "H1", "hotel_name": "Hilton Manhattan", "city": "New York", "address": "456 Fashion Ave, New York, NY 10018", "star_rating": 4, "price_per_night": 250.0, "available_rooms": 10, "amenities": ["gym", "restaurant"]},
        {"hotel_id": "H2", "hotel_name": "Marriott JFK Airport", "city": "New York", "address": "123 Airport Rd, Jamaica, NY 11430", "star_rating": 3, "price_per_night": 180.0, "available_rooms": 5, "amenities": ["shuttle", "wifi"]},
        {"hotel_id": "H3", "hotel_name": "Westin O'Hare", "city": "Chicago", "address": "789 Transit Rd, Rosemont, IL 60018", "star_rating": 4, "price_per_night": 220.0, "available_rooms": 3, "amenities": ["pool", "gym"]}
    ]
    with open("data/hotels/hotels.json", "w") as f:
        json.dump({"hotels": hotels}, f, indent=2)

    # 3. 酒店预订 (hotel_bookings.json)
    hotel_bookings = [
        {
            "booking_id": "B1",
            "hotel_id": "H3",
            "flight_id": "UA123",
            "contact_id": "C2",
            "checkin": "2025-03-20",
            "checkout": "2025-03-21",
            "status": "active"
        },
        {
            "booking_id": "B2",
            "hotel_id": "H1",
            "flight_id": "AA456",
            "contact_id": "C1",
            "checkin": "2025-03-20",
            "checkout": "2025-03-21",
            "status": "cancelled"
        },
        {
            "booking_id": "B3",
            "hotel_id": "H2",
            "flight_id": "DL789",
            "contact_id": "C3",
            "checkin": "2025-03-20",
            "checkout": "2025-03-21",
            "status": "active"
        }
    ]
    os.makedirs("data/hotels", exist_ok=True)
    with open("data/hotels/hotel_bookings.json", "w") as f:
        json.dump({"hotel_bookings": hotel_bookings}, f, indent=2)

    # 4. 交通预订 (transport_bookings.json)
    transport_bookings = [
        {
            "transport_booking_id": "T1",
            "transport_id": "T1",
            "flight_id": "AA456",
            "contact_id": "C1",
            "pickup_datetime": "2025-03-20 20:30",
            "status": "cancelled"
        },
        {
            "transport_booking_id": "T2",
            "transport_id": "T2",
            "flight_id": "UA123",
            "contact_id": "C2",
            "pickup_datetime": "2025-03-20 22:30",
            "status": "active"
        },
        {
            "transport_booking_id": "T3",
            "transport_id": "T3",
            "flight_id": "DL789",
            "contact_id": "C3",
            "pickup_datetime": "2025-03-20 18:00",
            "status": "completed"
        }
    ]
    os.makedirs("data/transports", exist_ok=True)
    with open("data/transports/transport_bookings.json", "w") as f:
        json.dump({"transport_bookings": transport_bookings}, f, indent=2)

    # 5. 联系人数据 (contacts.json)
    contacts = [
        {"contact_id": "C1", "name": "Jane Doe", "email": "jane.doe@example.com", "phone": "+1-555-0101"},
        {"contact_id": "C2", "name": "John Smith", "email": "john.smith@example.com", "phone": "+1-555-0102"},
        {"contact_id": "C3", "name": "Mike Johnson", "email": "mike.johnson@example.com", "phone": "+1-555-0103"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # 6. 报告模板 (ops/README.md)
    readme_content = """# Report Template
When generating the cascade action report, use the following JSON format:

{
    "flight_id": "xxx",
    "affected_hotel_booking": {
        "booking_id": "xxx",
        "new_checkin": "YYYY-MM-DD",
        "new_checkout": "YYYY-MM-DD",
        "action": "change_dates"
    },
    "rescheduled_transport": {
        "booking_id": "xxx",
        "new_pickup_date": "YYYY-MM-DD",
        "new_pickup_time": "HH:MM"
    },
    "notifications_sent": [
        {
            "contact_id": "xxx",
            "type": "delay_and_change",
            "status": "sent"
        }
    ]
}
"""
    with open("ops/README.md", "w") as f:
        f.write(readme_content)

if __name__ == "__main__":
    build_env()
