import json
import os

def build_env():
    # Create directories
    os.makedirs("flights", exist_ok=True)
    os.makedirs("hotels", exist_ok=True)
    os.makedirs("transports", exist_ok=True)
    os.makedirs("ops", exist_ok=True)   # 用于agent输出，初始为空

    # flights
    flights = {
        "flights": [
            {
                "flight_id": "AA456",
                "flight_number": "AA456",
                "airline": "American Airlines",
                "origin": "ATL",
                "destination": "BOS",
                "departure_time": "2025-03-10T15:30:00Z",
                "arrival_time": "2025-03-10T17:45:00Z",
                "status": "on_time",
                "delay_minutes": 0,
                "gate": "A10"
            },
            {
                "flight_id": "DL789",
                "flight_number": "DL789",
                "airline": "Delta Airlines",
                "origin": "LAX",
                "destination": "JFK",
                "departure_time": "2025-03-10T16:00:00Z",
                "arrival_time": "2025-03-10T20:10:00Z",
                "status": "delayed",
                "delay_minutes": 30,
                "gate": "B22"
            },
            {
                "flight_id": "UA123",
                "flight_number": "UA123",
                "airline": "United Airlines",
                "origin": "SFO",
                "destination": "ORD",
                "departure_time": "2025-03-10T14:00:00Z",
                "arrival_time": "2025-03-10T16:20:00Z",
                "status": "delayed",
                "delay_minutes": 90,
                "gate": "C15"
            }
        ]
    }
    with open("flights/flights.json", "w") as f:
        json.dump(flights, f, indent=2)

    # hotel bookings
    hotel_bookings = {
        "bookings": [
            {"booking_id": "HB-001", "flight_id": "AA456", "passenger_email": "jane.doe@example.com", "status": "confirmed"},
            {"booking_id": "HB-002", "flight_id": "DL789", "passenger_email": "mike.johnson@example.com", "status": "confirmed"},
            {"booking_id": "HB-003", "flight_id": "UA123", "passenger_email": "john.smith@example.com", "status": "confirmed"},
            {"booking_id": "HB-004", "flight_id": "UA123", "passenger_email": "alice.wonder@example.com", "status": "cancelled"},
            # 干扰项：不存在航班的预订
            {"booking_id": "HB-005", "flight_id": "UNKNOWN", "passenger_email": "spam@example.com", "status": "confirmed"}
        ]
    }
    with open("hotels/hotel_bookings.json", "w") as f:
        json.dump(hotel_bookings, f, indent=2)

    # transport bookings
    transport_bookings = {
        "bookings": [
            {"booking_id": "TB-001", "flight_id": "AA456", "passenger_email": "jane.doe@example.com", "status": "confirmed"},
            {"booking_id": "TB-002", "flight_id": "DL789", "passenger_email": "mike.johnson@example.com", "status": "confirmed"},
            {"booking_id": "TB-003", "flight_id": "UA123", "passenger_email": "jane.doe@example.com", "status": "confirmed"},
            {"booking_id": "TB-004", "flight_id": "UA123", "passenger_email": "alice.wonder@example.com", "status": "cancelled"}
        ]
    }
    with open("transports/transport_bookings.json", "w") as f:
        json.dump(transport_bookings, f, indent=2)

if __name__ == "__main__":
    build_env()
