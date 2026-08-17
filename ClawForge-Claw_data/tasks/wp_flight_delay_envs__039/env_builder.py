import json
import os

def build_env():
    # 创建目录
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # contacts.json
    contacts = {
        "contacts": [
            {"contact_id": "C001", "name": "Jane Doe", "email": "jane.doe@example.com", "phone": "+1-555-0101"},
            {"contact_id": "C002", "name": "John Smith", "email": "john.smith@example.com", "phone": "+1-555-0102"},
            {"contact_id": "C003", "name": "Mike Johnson", "email": "mike.johnson@example.com", "phone": "+1-555-0103"}
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # flights.json
    flights = {
        "flights": [
            {"flight_id": "FL001", "flight_number": "AA456", "airline": "American Airlines", "origin": "ATL", "destination": "BOS", "departure_time": "2025-03-15T18:00:00Z", "arrival_time": "2025-03-15T21:30:00Z", "status": "delayed", "delay_minutes": 90, "gate": "A10"},
            {"flight_id": "FL002", "flight_number": "DL789", "airline": "Delta Airlines", "origin": "LAX", "destination": "JFK", "departure_time": "2025-03-15T20:00:00Z", "arrival_time": "2025-03-16T04:00:00Z", "status": "on_time", "delay_minutes": 0, "gate": "B22"},
            {"flight_id": "FL003", "flight_number": "UA123", "airline": "United Airlines", "origin": "SFO", "destination": "ORD", "departure_time": "2025-03-15T22:00:00Z", "arrival_time": "2025-03-16T04:30:00Z", "status": "delayed", "delay_minutes": 45, "gate": "C15"}
        ]
    }
    with open("data/flights.json", "w") as f:
        json.dump(flights, f, indent=2)

    # hotels.json (包含一个已取消的干扰项)
    hotels = {
        "hotels": [
            {"hotel_id": "H001", "hotel_name": "Hilton Manhattan", "city": "New York", "address": "456 Fashion Ave, New York, NY 10018", "star_rating": 4, "price_per_night": 299.0, "available_rooms": 10, "amenities": ["Wifi", "Gym"], "contact_id": "C001", "flight_id": "FL001", "status": "confirmed"},
            {"hotel_id": "H002", "hotel_name": "Marriott JFK Airport", "city": "New York", "address": "123 Airport Rd, Jamaica, NY 11430", "star_rating": 3, "price_per_night": 189.0, "available_rooms": 25, "amenities": ["Wifi", "Shuttle"], "contact_id": "C002", "flight_id": "FL002", "status": "confirmed"},
            {"hotel_id": "H003", "hotel_name": "Westin O'Hare", "city": "Chicago", "address": "789 Transit Rd, Rosemont, IL 60018", "star_rating": 4, "price_per_night": 259.0, "available_rooms": 15, "amenities": ["Pool", "Wifi"], "contact_id": "C003", "flight_id": "FL003", "status": "confirmed"},
            {"hotel_id": "H004", "hotel_name": "Hilton Manhattan", "city": "New York", "address": "456 Fashion Ave, New York, NY 10018", "star_rating": 4, "price_per_night": 299.0, "available_rooms": 10, "amenities": ["Wifi", "Gym"], "contact_id": "C001", "flight_id": "FL001", "status": "canceled"}
        ]
    }
    with open("data/hotels.json", "w") as f:
        json.dump(hotels, f, indent=2)

    # transports.json (正常航班关联一个干扰，但该航班未延误)
    transports = {
        "transports": [
            {"transport_id": "T001", "transport_type": "limousine", "service_provider": "Blacklane", "service_area": "NYC", "vehicle_type": "luxury", "base_price": 150.0, "next_available": "2025-03-15T20:00:00Z", "contact_id": "C001", "flight_id": "FL001"},
            {"transport_id": "T002", "transport_type": "shuttle", "service_provider": "SuperShuttle", "service_area": "NYC", "vehicle_type": "van", "base_price": 30.0, "next_available": "2025-03-15T22:00:00Z", "contact_id": "C002", "flight_id": "FL002"},
            {"transport_id": "T003", "transport_type": "suv", "service_provider": "Uber", "service_area": "ORD", "vehicle_type": "premium", "base_price": 80.0, "next_available": "2025-03-16T05:00:00Z", "contact_id": "C003", "flight_id": "FL003"}
        ]
    }
    with open("data/transports.json", "w") as f:
        json.dump(transports, f, indent=2)

if __name__ == "__main__":
    build_env()
