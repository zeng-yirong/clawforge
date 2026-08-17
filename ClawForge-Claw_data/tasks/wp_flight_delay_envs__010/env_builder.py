import os
import json
import csv
from datetime import datetime, timedelta

def build_env():
    # 确保目录存在
    for d in ["data/flights", "data/hotels", "data/transports", "ops"]:
        os.makedirs(d, exist_ok=True)

    # ========== 干扰项：旧的/无关文件 ==========
    # ops 里放一个旧报告
    with open("ops/old_report.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["flight", "delay", "action"])
        w.writerow(["AA456", "0", "no change"])
    # 一个无用的 note
    with open("ops/note.txt", "w") as f:
        f.write("旧的调整方案已废弃，不要用。\n")

    # ========== 1. 航班数据 ==========
    flights = [
        {"flight_id": "FL001", "flight_number": "DL789", "airline": "Delta Airlines",
         "origin": "ATL", "destination": "JFK", "departure_time": "2025-04-10 16:00",
         "arrival_time": "2025-04-10 20:00", "status": "delayed", "delay_minutes": 240, "gate": "B22"},
        {"flight_id": "FL002", "flight_number": "UA123", "airline": "United Airlines",
         "origin": "SFO", "destination": "ORD", "departure_time": "2025-04-10 14:00",
         "arrival_time": "2025-04-10 20:30", "status": "on_time", "delay_minutes": 0, "gate": "C15"},
        {"flight_id": "FL003", "flight_number": "AA456", "airline": "American Airlines",
         "origin": "LAX", "destination": "BOS", "departure_time": "2025-04-11 08:00",
         "arrival_time": "2025-04-11 14:00", "status": "delayed", "delay_minutes": 30, "gate": "A10"},  # 干扰：小延误但关联预订已取消
        {"flight_id": "FL004", "flight_number": "DL789", "airline": "Delta Airlines",
         "origin": "ATL", "destination": "JFK", "departure_time": "2025-04-12 16:00",
         "arrival_time": "2025-04-12 20:00", "status": "on_time", "delay_minutes": 0, "gate": "B22"}  # 同一航班号另一天的正常航班
    ]
    with open("data/flights/flights.json", "w") as f:
        json.dump({"flights": flights}, f, indent=2)

    # ========== 2. 酒店预订 ==========
    hotel_bookings = [
        # 真正受影响的：关联 FL001 (DL789 4月10日)
        {"booking_id": "HB001", "flight_id": "FL001", "hotel_id": "HIL001",
         "hotel_name": "Hilton Manhattan", "check_in": "2025-04-10", "check_out": "2025-04-13",
         "status": "active", "guest": "Jane Doe"},
        # 干扰：关联 FL003 (小延误) 但状态已取消
        {"booking_id": "HB002", "flight_id": "FL003", "hotel_id": "MAR001",
         "hotel_name": "Marriott JFK Airport", "check_in": "2025-04-11", "check_out": "2025-04-12",
         "status": "cancelled", "guest": "John Smith"},
        # 干扰：关联 FL002 (正常航班)
        {"booking_id": "HB003", "flight_id": "FL002", "hotel_id": "WES001",
         "hotel_name": "Westin O'Hare", "check_in": "2025-04-10", "check_out": "2025-04-11",
         "status": "active", "guest": "Mike Johnson"},
        # 干扰：过期预订（check_out 已过今天）即使关联延误航班也不处理
        {"booking_id": "HB004", "flight_id": "FL001", "hotel_id": "HIL001",
         "hotel_name": "Hilton Manhattan", "check_in": "2025-04-08", "check_out": "2025-04-10",
         "status": "active", "guest": "Extra Guest"}  # 已经结束，不需要调整
    ]
    with open("data/hotel_bookings.json", "w") as f:
        json.dump(hotel_bookings, f, indent=2)

    # ========== 3. 交通预订 ==========
    transport_bookings = [
        # 真正受影响的：关联 FL001
        {"booking_id": "TB001", "flight_id": "FL001", "transport_id": "TR001",
         "transport_type": "limousine", "service_provider": "Blacklane",
         "pickup_datetime": "2025-04-10 20:30", "status": "active", "passenger": "Jane Doe"},
        # 干扰：关联 FL003 但预订已取消
        {"booking_id": "TB002", "flight_id": "FL003", "transport_id": "TR002",
         "transport_type": "shuttle", "service_provider": "SuperShuttle",
         "pickup_datetime": "2025-04-11 14:30", "status": "cancelled", "passenger": "John Smith"},
        # 干扰：关联正常航班
        {"booking_id": "TB003", "flight_id": "FL002", "transport_id": "TR003",
         "transport_type": "suv", "service_provider": "Uber",
         "pickup_datetime": "2025-04-10 20:45", "status": "active", "passenger": "Mike Johnson"},
        # 干扰：过期已完成的交通
        {"booking_id": "TB004", "flight_id": "FL001", "transport_id": "TR001",
         "transport_type": "limousine", "service_provider": "Blacklane",
         "pickup_datetime": "2025-04-08 20:30", "status": "completed", "passenger": "Jane Doe"}
    ]
    with open("data/transport_bookings.json", "w") as f:
        json.dump(transport_bookings, f, indent=2)

    # ========== 4. 酒店和交通的参考资料（干扰） ==========
    hotels = [
        {"hotel_id": "HIL001", "hotel_name": "Hilton Manhattan", "city": "New York"},
        {"hotel_id": "MAR001", "hotel_name": "Marriott JFK Airport", "city": "New York"},
        {"hotel_id": "WES001", "hotel_name": "Westin O'Hare", "city": "Chicago"}
    ]
    with open("data/hotels/hotels.json", "w") as f:
        json.dump({"hotels": hotels}, f, indent=2)

    transports = [
        {"transport_id": "TR001", "transport_type": "limousine", "service_provider": "Blacklane"},
        {"transport_id": "TR002", "transport_type": "shuttle", "service_provider": "SuperShuttle"},
        {"transport_id": "TR003", "transport_type": "suv", "service_provider": "Uber"}
    ]
    with open("data/transports/transports.json", "w") as f:
        json.dump({"transports": transports}, f, indent=2)

if __name__ == "__main__":
    build_env()
