import json, os

def build_env():
    # 航班数据
    flights = [
        {"flight_id": "FL001", "flight_number": "UA123", "airline": "United Airlines", "origin": "SFO", "destination": "ORD", "departure_time": "2025-03-20T09:00:00", "arrival_time": "2025-03-20T15:00:00", "status": "delayed", "delay_minutes": 60, "gate": "C15"},
        {"flight_id": "FL002", "flight_number": "AA456", "airline": "American Airlines", "origin": "ATL", "destination": "BOS", "departure_time": "2025-03-20T10:00:00", "arrival_time": "2025-03-20T12:30:00", "status": "on_time", "delay_minutes": 0, "gate": "A10"},
        {"flight_id": "FL003", "flight_number": "DL789", "airline": "Delta Airlines", "origin": "LAX", "destination": "JFK", "departure_time": "2025-03-20T14:00:00", "arrival_time": "2025-03-20T22:00:00", "status": "on_time", "delay_minutes": 0, "gate": "B22"},
    ]
    os.makedirs("data/flights", exist_ok=True)
    with open("data/flights/flights.json", "w") as f:
        json.dump({"flights": flights}, f, indent=2)

    # 酒店预订数据 (包含受UA123影响的)
    hotel_bookings = [
        {"booking_id": "HB001", "flight_id": "FL001", "hotel_id": "HT001", "check_in": "2025-03-20", "check_out": "2025-03-22", "guest_name": "Jane Doe"},
        {"booking_id": "HB002", "flight_id": "FL001", "hotel_id": "HT002", "check_in": "2025-03-20", "check_out": "2025-03-21", "guest_name": "John Smith"},
        {"booking_id": "HB003", "flight_id": "FL002", "hotel_id": "HT001", "check_in": "2025-03-21", "check_out": "2025-03-23", "guest_name": "Alice"},  # 干扰项：关联其他航班
        {"booking_id": "HB004", "flight_id": "FL001", "hotel_id": "HT003", "check_in": "2025-03-20", "check_out": "2025-03-24", "guest_name": "Bob", "status": "cancelled"},  # 已取消的干扰
    ]
    os.makedirs("data/hotels", exist_ok=True)
    with open("data/hotels/bookings.json", "w") as f:
        json.dump({"bookings": hotel_bookings}, f, indent=2)

    # 交通预订数据
    transport_bookings = [
        {"booking_id": "TB001", "flight_id": "FL001", "transport_id": "TR001", "pickup_time": "2025-03-20T15:30:00", "guest_name": "Jane Doe"},
        {"booking_id": "TB002", "flight_id": "FL001", "transport_id": "TR002", "pickup_time": "2025-03-20T15:45:00", "guest_name": "John Smith"},
        {"booking_id": "TB003", "flight_id": "FL003", "transport_id": "TR003", "pickup_time": "2025-03-20T22:30:00", "guest_name": "Mike"},  # 干扰
        {"booking_id": "TB004", "flight_id": "FL001", "transport_id": "TR001", "pickup_time": "2025-03-20T16:00:00", "guest_name": "Extra Guest", "status": "completed"},  # 已完成干扰
    ]
    os.makedirs("data/transports", exist_ok=True)
    with open("data/transports/bookings.json", "w") as f:
        json.dump({"bookings": transport_bookings}, f, indent=2)

    # 酒店和交通详情（用于丰富环境但不影响答案）
    hotels = [
        {"hotel_id": "HT001", "hotel_name": "Hilton Manhattan", "city": "New York", "address": "456 Fashion Ave, New York, NY 10018", "star_rating": 4, "price_per_night": 250.0, "available_rooms": 10, "amenities": ["wifi", "pool"]},
        {"hotel_id": "HT002", "hotel_name": "Marriott JFK Airport", "city": "New York", "address": "123 Airport Rd, Jamaica, NY 11430", "star_rating": 3, "price_per_night": 180.0, "available_rooms": 5, "amenities": ["shuttle", "wifi"]},
        {"hotel_id": "HT003", "hotel_name": "Westin O'Hare", "city": "Chicago", "address": "789 Transit Rd, Rosemont, IL 60018", "star_rating": 4, "price_per_night": 220.0, "available_rooms": 3, "amenities": ["gym", "restaurant"]},
    ]
    with open("data/hotels/hotels.json", "w") as f:
        json.dump({"hotels": hotels}, f, indent=2)

    transports = [
        {"transport_id": "TR001", "transport_type": "limousine", "service_provider": "Blacklane", "service_area": "ORD", "vehicle_type": "luxury", "base_price": 120.0, "next_available": "2025-03-20T16:00:00"},
        {"transport_id": "TR002", "transport_type": "shuttle", "service_provider": "SuperShuttle", "service_area": "ORD", "vehicle_type": "van", "base_price": 45.0, "next_available": "2025-03-20T15:00:00"},
        {"transport_id": "TR003", "transport_type": "suv", "service_provider": "Uber", "service_area": "JFK", "vehicle_type": "premium", "base_price": 85.0, "next_available": "2025-03-20T22:00:00"},
    ]
    with open("data/transports/transports.json", "w") as f:
        json.dump({"transports": transports}, f, indent=2)

    # 其他干扰文件
    os.makedirs("data", exist_ok=True)
    contacts = [
        {"contact_id": "C001", "name": "Jane Doe", "email": "jane.doe@example.com", "phone": "+1-555-0101"},
        {"contact_id": "C002", "name": "John Smith", "email": "john.smith@example.com", "phone": "+1-555-0102"},
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    accounts = [
        {"account_id": "A001", "account_name": "TravelCorp", "email": "ops@travelcorp.com", "role": "coordinator", "display_name": "TravelCorp Ops"},
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # 创建目标输出目录（agent需要创建ops/）
    os.makedirs("ops", exist_ok=True)

if __name__ == "__main__":
    build_env()
