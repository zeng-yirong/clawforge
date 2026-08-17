import json
import os

def build_env():
    # 确保目录结构
    os.makedirs("data/flights", exist_ok=True)
    os.makedirs("data/hotels", exist_ok=True)
    os.makedirs("data/transports", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # agent 将在此输出

    # 1. 航班数据 – 干扰项：另一个航班也延误但无关联预订
    flights = [
        {
            "flight_id": "FL001",
            "flight_number": "UA123",
            "airline": "United Airlines",
            "origin": "SFO",
            "destination": "NYC",
            "departure_time": "2025-06-10 16:30",
            "arrival_time": "2025-06-10 23:45",
            "status": "delayed",
            "delay_minutes": 115,
            "gate": "C15"
        },
        {
            "flight_id": "FL002",
            "flight_number": "AA456",
            "airline": "American Airlines",
            "origin": "LAX",
            "destination": "BOS",
            "departure_time": "2025-06-10 18:00",
            "arrival_time": "2025-06-11 02:10",
            "status": "on_time",
            "delay_minutes": 0,
            "gate": "A10"
        },
        {
            "flight_id": "FL003",
            "flight_number": "DL789",
            "airline": "Delta Airlines",
            "origin": "ATL",
            "destination": "ORD",
            "departure_time": "2025-06-10 20:00",
            "arrival_time": "2025-06-10 21:30",
            "status": "delayed",
            "delay_minutes": 45,
            "gate": "B22"
        }
    ]
    with open("data/flights/flights.json", "w") as f:
        json.dump({"flights": flights}, f, indent=2)

    # 2. 酒店预订 – 一个与UA123相关，两个无关（包括一个干扰项：另一延误航班DL789但预订未关联）
    hotel_bookings = [
        {
            "booking_id": "HB001",
            "guest_name": "John Smith",
            "email": "john.smith@example.com",
            "hotel_name": "Hilton Manhattan",
            "check_in": "2025-06-10",
            "check_out": "2025-06-12",
            "flight_number": "UA123"
        },
        {
            "booking_id": "HB002",
            "guest_name": "Jane Doe",
            "email": "jane.doe@example.com",
            "hotel_name": "Marriott JFK Airport",
            "check_in": "2025-06-11",
            "check_out": "2025-06-13",
            "flight_number": "AA456"
        },
        {
            "booking_id": "HB003",
            "guest_name": "Mike Johnson",
            "email": "mike.johnson@example.com",
            "hotel_name": "Westin O'Hare",
            "check_in": "2025-06-10",
            "check_out": "2025-06-11",
            "flight_number": "DL789"
        }
    ]
    with open("data/hotels/hotel_bookings.json", "w") as f:
        json.dump({"bookings": hotel_bookings}, f, indent=2)

    # 3. 交通预订 – 只有John Smith的接机服务关联UA123
    transport_bookings = [
        {
            "booking_id": "TB001",
            "passenger_name": "John Smith",
            "email": "john.smith@example.com",
            "service_type": "limousine",
            "pickup_time": "2025-06-10 23:45",
            "pickup_location": "JFK Airport",
            "flight_number": "UA123",
            "status": "confirmed"
        },
        {
            "booking_id": "TB002",
            "passenger_name": "Jane Doe",
            "email": "jane.doe@example.com",
            "service_type": "shuttle",
            "pickup_time": "2025-06-11 08:00",
            "pickup_location": "LGA Airport",
            "flight_number": "AA456",
            "status": "confirmed"
        }
    ]
    with open("data/transports/transport_bookings.json", "w") as f:
        json.dump({"bookings": transport_bookings}, f, indent=2)

    # 4. 无关文件干扰项：一个过期的航班快照
    os.makedirs("backup", exist_ok=True)
    with open("backup/old_flights.json", "w") as f:
        json.dump({"flights": [{"flight_number": "UA123", "status": "on_time"}]}, f)

if __name__ == "__main__":
    build_env()
