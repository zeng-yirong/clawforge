import os
import json

def build_env():
    # 创建目录
    os.makedirs("data/flights", exist_ok=True)
    os.makedirs("data/hotels", exist_ok=True)
    os.makedirs("data/transports", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 航班数据
    flights = [
        {"flight_id": "UA123", "flight_number": "UA123", "airline": "United Airlines", "origin": "SFO", "destination": "JFK", "departure_time": "2025-03-15T18:00", "arrival_time": "2025-03-15T23:00", "status": "delayed", "delay_minutes": 90, "gate": "C15"},
        {"flight_id": "AA456", "flight_number": "AA456", "airline": "American Airlines", "origin": "ATL", "destination": "BOS", "departure_time": "2025-03-15T14:00", "arrival_time": "2025-03-15T16:00", "status": "delayed", "delay_minutes": 30, "gate": "A10"},
        {"flight_id": "DL789", "flight_number": "DL789", "airline": "Delta Airlines", "origin": "LAX", "destination": "ORD", "departure_time": "2025-03-15T20:00", "arrival_time": "2025-03-15T22:00", "status": "on_time", "delay_minutes": 0, "gate": "B22"}
    ]
    with open("data/flights/flights.json", "w") as f:
        json.dump({"flights": flights}, f, indent=2)

    # 酒店信息
    hotels = [
        {"hotel_id": "HIL001", "hotel_name": "Hilton Manhattan", "city": "New York", "address": "456 Fashion Ave, New York, NY 10018", "star_rating": 4, "price_per_night": 250.0, "available_rooms": 10, "amenities": ["WiFi", "Pool"]},
        {"hotel_id": "MAR002", "hotel_name": "Marriott JFK Airport", "city": "New York", "address": "123 Airport Rd, Jamaica, NY 11430", "star_rating": 3, "price_per_night": 180.0, "available_rooms": 5, "amenities": ["Shuttle"]},
        {"hotel_id": "WES003", "hotel_name": "Westin O'Hare", "city": "Chicago", "address": "789 Transit Rd, Rosemont, IL 60018", "star_rating": 4, "price_per_night": 200.0, "available_rooms": 0, "amenities": ["Gym"]}
    ]
    with open("data/hotels/hotels.json", "w") as f:
        json.dump({"hotels": hotels}, f, indent=2)

    # 酒店预订
    hotel_bookings = [
        {"booking_id": "BKG001", "hotel_id": "HIL001", "flight_id": "UA123", "guest_name": "John Smith", "check_in": "2025-03-15", "check_out": "2025-03-17", "status": "confirmed"},
        {"booking_id": "BKG002", "hotel_id": "MAR002", "flight_id": "AA456", "guest_name": "Jane Doe", "check_in": "2025-03-15", "check_out": "2025-03-16", "status": "confirmed"},
        {"booking_id": "BKG003", "hotel_id": "WES003", "flight_id": "DL789", "guest_name": "Mike Johnson", "check_in": "2025-03-15", "check_out": "2025-03-18", "status": "cancelled"}
    ]
    with open("data/hotel_bookings.json", "w") as f:
        json.dump({"bookings": hotel_bookings}, f, indent=2)

    # 交通信息
    transports = [
        {"transport_id": "BLK001", "transport_type": "limousine", "service_provider": "Blacklane", "service_area": "New York", "vehicle_type": "luxury", "base_price": 120.0, "next_available": "2025-03-15T20:00"},
        {"transport_id": "UBR002", "transport_type": "suv", "service_provider": "Uber", "service_area": "Boston", "vehicle_type": "premium", "base_price": 80.0, "next_available": "2025-03-15T14:00"}
    ]
    with open("data/transports/transports.json", "w") as f:
        json.dump({"transports": transports}, f, indent=2)

    # 交通预订
    transport_bookings = [
        {"booking_id": "TRP001", "transport_id": "BLK001", "flight_id": "UA123", "guest_name": "John Smith", "pickup_time": "2025-03-15T23:30", "pickup_location": "JFK Airport", "status": "confirmed"},
        {"booking_id": "TRP002", "transport_id": "UBR002", "flight_id": "AA456", "guest_name": "Jane Doe", "pickup_time": "2025-03-15T16:30", "pickup_location": "BOS Airport", "status": "confirmed"}
    ]
    with open("data/transport_bookings.json", "w") as f:
        json.dump({"bookings": transport_bookings}, f, indent=2)

if __name__ == "__main__":
    build_env()
