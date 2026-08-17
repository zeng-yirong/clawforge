import json
import os

def build_env():
    # --- flights ---
    flights = [
        {
            "flight_id": "f001",
            "flight_number": "UA123",
            "airline": "United Airlines",
            "origin": "SFO",
            "destination": "JFK",
            "departure_time": "2025-04-10T16:00:00",
            "arrival_time": "2025-04-10T18:30:00",
            "status": "delayed",
            "delay_minutes": 120,
            "gate": "C15"
        },
        {
            "flight_id": "f002",
            "flight_number": "AA456",
            "airline": "American Airlines",
            "origin": "ATL",
            "destination": "ORD",
            "departure_time": "2025-04-10T15:00:00",
            "arrival_time": "2025-04-10T17:00:00",
            "status": "on_time",
            "delay_minutes": 0,
            "gate": "A10"
        }
    ]
    os.makedirs("data/flights", exist_ok=True)
    with open("data/flights/flights.json", "w") as f:
        json.dump({"flights": flights}, f, indent=2)
    # 干扰：旧的备份航班文件
    with open("data/flights/backup_flights.json", "w") as f:
        json.dump({"flights": [{"flight_id":"f_old","flight_number":"UA999","status":"cancelled"}]}, f, indent=2)

    # --- hotels ---
    hotels = [
        {
            "hotel_id": "h001",
            "hotel_name": "Hilton Manhattan",
            "city": "New York",
            "address": "456 Fashion Ave, New York, NY 10018",
            "star_rating": 4,
            "price_per_night": 250.0,
            "available_rooms": 20,
            "amenities": ["WiFi", "Gym"]
        },
        {
            "hotel_id": "h002",
            "hotel_name": "Marriott JFK Airport",
            "city": "New York",
            "address": "123 Airport Rd, Jamaica, NY 11430",
            "star_rating": 3,
            "price_per_night": 180.0,
            "available_rooms": 5,
            "amenities": ["Shuttle", "WiFi"]
        }
    ]
    os.makedirs("data/hotels", exist_ok=True)
    with open("data/hotels/hotels.json", "w") as f:
        json.dump({"hotels": hotels}, f, indent=2)
    # 干扰：无关的费率文件
    with open("data/hotels/rates.csv", "w") as f:
        f.write("hotel_id,rate_code,amount\nh001,WEEKEND,220.0\n")

    # --- transports ---
    transports = [
        {
            "transport_id": "t001",
            "transport_type": "limousine",
            "service_provider": "Blacklane",
            "service_area": "JFK",
            "vehicle_type": "luxury",
            "base_price": 120.0,
            "next_available": "2025-04-10T22:00:00"
        }
    ]
    os.makedirs("data/transports", exist_ok=True)
    with open("data/transports/transports.json", "w") as f:
        json.dump({"transports": transports}, f, indent=2)

    # --- contacts ---
    contacts = [
        {
            "contact_id": "c001",
            "name": "John Smith",
            "email": "john.smith@example.com",
            "phone": "+1-555-0102"
        },
        {
            "contact_id": "c002",
            "name": "Jane Doe",
            "email": "jane.doe@example.com",
            "phone": "+1-555-0101"
        }
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # --- hotel bookings ---
    hotel_bookings = [
        {
            "booking_id": "hb001",
            "flight_id": "f001",
            "hotel_id": "h001",
            "contact_id": "c001",
            "check_in": "2025-04-10T18:00:00",
            "check_out": "2025-04-12T11:00:00",
            "status": "active"
        },
        {
            "booking_id": "hb002",
            "flight_id": "f002",
            "hotel_id": "h002",
            "contact_id": "c002",
            "check_in": "2025-04-10T17:30:00",
            "check_out": "2025-04-11T10:00:00",
            "status": "active"
        },
        {
            "booking_id": "hb003",
            "flight_id": "f001",
            "hotel_id": "h002",
            "contact_id": "c001",
            "check_in": "2025-04-10T18:00:00",
            "check_out": "2025-04-11T10:00:00",
            "status": "cancelled"   # 干扰：已取消
        }
    ]
    os.makedirs("data/bookings", exist_ok=True)
    with open("data/bookings/hotel_bookings.json", "w") as f:
        json.dump({"hotel_bookings": hotel_bookings}, f, indent=2)
    # 干扰：旧的预订文件
    with open("data/bookings/old_hotel_bookings.json", "w") as f:
        json.dump([{"booking_id":"hb_old","status":"archived"}], f, indent=2)

    # --- transport bookings ---
    transport_bookings = [
        {
            "booking_id": "tb001",
            "flight_id": "f001",
            "transport_id": "t001",
            "contact_id": "c001",
            "pickup_time": "2025-04-10T18:15:00",
            "status": "active"
        },
        {
            "booking_id": "tb002",
            "flight_id": "f002",
            "transport_id": "t001",
            "contact_id": "c002",
            "pickup_time": "2025-04-10T17:30:00",
            "status": "cancelled"   # 干扰：已取消
        }
    ]
    with open("data/bookings/transport_bookings.json", "w") as f:
        json.dump({"transport_bookings": transport_bookings}, f, indent=2)

    # --- ops directory (empty, agent will write here) ---
    os.makedirs("ops", exist_ok=True)

    # 干扰：无关的日志目录
    os.makedirs("logs", exist_ok=True)
    with open("logs/system.log", "w") as f:
        f.write("2025-04-10 18:00:00 INFO Flight UA123 status updated\n")

if __name__ == "__main__":
    build_env()
