import json
import os
import sys
import re

def verify(workspace):
    # 得分明细
    details = []
    total_score = 0

    # ---------- 目录结构检查 ----------
    required_dirs = ["flights", "hotels", "transports"]
    for d in required_dirs:
        path = os.path.join(workspace, d)
        exists = os.path.isdir(path)
        details.append({
            "item": f"Directory '{d}' exists",
            "score": 10 if exists else 0,
            "max_score": 10,
            "passed": exists,
            "reason": "Found" if exists else "Missing"
        })
        if exists:
            total_score += 10

    # ---------- 检查输出文件存在 ----------
    required_files = [
        "adjusted_hotel_bookings.json",
        "rescheduled_transports.json",
        "notification_log.txt"
    ]
    for fname in required_files:
        fpath = os.path.join(workspace, fname)
        exists = os.path.isfile(fpath)
        details.append({
            "item": f"Output file '{fname}' exists",
            "score": 5 if exists else 0,
            "max_score": 5,
            "passed": exists,
            "reason": "Found" if exists else "Missing"
        })
        if exists:
            total_score += 5

    # ---------- 验证 adjusted_hotel_bookings.json ----------
    adj_hotel_path = os.path.join(workspace, "adjusted_hotel_bookings.json")
    if os.path.isfile(adj_hotel_path):
        try:
            with open(adj_hotel_path) as f:
                adj_hotel = json.load(f)
        except (json.JSONDecodeError, Exception) as e:
            details.append({"item": "adjusted_hotel_bookings.json is valid JSON",
                            "score": 0, "max_score": 5, "passed": False, "reason": f"Parse error: {e}"})
        else:
            details.append({"item": "adjusted_hotel_bookings.json is valid JSON",
                            "score": 5, "max_score": 5, "passed": True, "reason": "Valid JSON"})
            total_score += 5

            # 检查是否只包含受影响的一个预订
            if isinstance(adj_hotel, list):
                if len(adj_hotel) == 1:
                    details.append({"item": "Only one booking in adjusted_hotel_bookings.json",
                                    "score": 5, "max_score": 5, "passed": True, "reason": "Exactly one booking"})
                    total_score += 5
                else:
                    details.append({"item": "Only one booking in adjusted_hotel_bookings.json",
                                    "score": 0, "max_score": 5, "passed": False,
                                    "reason": f"Expected 1, got {len(adj_hotel)}"})
                # 验证内容
                booking = adj_hotel[0]
                expected_fields = {"booking_id", "hotel_id", "guest_name", "flight_number", "check_in", "check_out"}
                actual_fields = set(booking.keys())
                if expected_fields.issubset(actual_fields):
                    details.append({"item": "Hotel booking has all required fields",
                                    "score": 5, "max_score": 5, "passed": True, "reason": "Fields OK"})
                    total_score += 5
                    # 检查 booking_id 应为 HB001
                    if booking["booking_id"] == "HB001":
                        details.append({"item": "Correct booking_id HB001",
                                        "score": 5, "max_score": 5, "passed": True, "reason": "Matches expected"})
                        total_score += 5
                    else:
                        details.append({"item": "Correct booking_id HB001",
                                        "score": 0, "max_score": 5, "passed": False,
                                        "reason": f"Got {booking['booking_id']}"})
                    # 检查酒店为 Westin O'Hare (HTL001)
                    if booking["hotel_id"] == "HTL001":
                        details.append({"item": "Hotel ID is HTL001 (Westin O'Hare)",
                                        "score": 5, "max_score": 5, "passed": True, "reason": "Match"})
                        total_score += 5
                    else:
                        details.append({"item": "Hotel ID is HTL001 (Westin O'Hare)",
                                        "score": 0, "max_score": 5, "passed": False,
                                        "reason": f"Got {booking['hotel_id']}"})
                    # 检查 check_in 应为 2025-06-16 (顺延一天)
                    if booking["check_in"] == "2025-06-16":
                        details.append({"item": "Check-in date adjusted to 2025-06-16",
                                        "score": 10, "max_score": 10, "passed": True, "reason": "Correct day shift"})
                        total_score += 10
                    else:
                        details.append({"item": "Check-in date adjusted to 2025-06-16",
                                        "score": 0, "max_score": 10, "passed": False,
                                        "reason": f"Got {booking['check_in']}"})
                else:
                    missing = expected_fields - actual_fields
                    details.append({"item": "Hotel booking has all required fields",
                                    "score": 0, "max_score": 5, "passed": False,
                                    "reason": f"Missing fields: {missing}"})
            else:
                details.append({"item": "adjusted_hotel_bookings.json is a list",
                                "score": 0, "max_score": 5, "passed": False, "reason": "Not a list"})
    else:
        for item in ["adjusted_hotel_bookings.json is valid JSON", "Only one booking...", "Hotel booking has all required fields",
                     "Correct booking_id HB001", "Hotel ID is HTL001", "Check-in date adjusted to 2025-06-16"]:
            details.append({"item": item, "score": 0, "max_score": 5, "passed": False, "reason": "File missing"})

    # ---------- 验证 rescheduled_transports.json ----------
    resched_trans_path = os.path.join(workspace, "rescheduled_transports.json")
    if os.path.isfile(resched_trans_path):
        try:
            with open(resched_trans_path) as f:
                resched_trans = json.load(f)
        except Exception as e:
            details.append({"item": "rescheduled_transports.json is valid JSON",
                            "score": 0, "max_score": 5, "passed": False, "reason": f"Parse error: {e}"})
        else:
            details.append({"item": "rescheduled_transports.json is valid JSON",
                            "score": 5, "max_score": 5, "passed": True, "reason": "Valid JSON"})
            total_score += 5
            if isinstance(resched_trans, list):
                if len(resched_trans) == 1:
                    details.append({"item": "Only one transport booking in rescheduled_transports.json",
                                    "score": 5, "max_score": 5, "passed": True, "reason": "Exactly one"})
                    total_score += 5
                else:
                    details.append({"item": "Only one transport booking in rescheduled_transports.json",
                                    "score": 0, "max_score": 5, "passed": False,
                                    "reason": f"Expected 1, got {len(resched_trans)}"})
                if len(resched_trans) > 0:
                    tb = resched_trans[0]
                    expected_tb_fields = {"booking_id", "transport_id", "guest_name", "flight_number", "pickup_time", "dropoff_location"}
                    actual_tb_fields = set(tb.keys())
                    if expected_tb_fields.issubset(actual_tb_fields):
                        details.append({"item": "Transport booking has all required fields",
                                        "score": 5, "max_score": 5, "passed": True, "reason": "Fields OK"})
                        total_score += 5
                        if tb["booking_id"] == "TB001":
                            details.append({"item": "Correct transport booking_id TB001",
                                            "score": 5, "max_score": 5, "passed": True, "reason": "Match"})
                            total_score += 5
                        else:
                            details.append({"item": "Correct transport booking_id TB001",
                                            "score": 0, "max_score": 5, "passed": False,
                                            "reason": f"Got {tb['booking_id']}"})
                        # pickup_time 应推迟2小时（原18:00 -> 20:00）
                        expected_pickup = "2025-06-15 20:00"
                        if tb["pickup_time"] == expected_pickup:
                            details.append({"item": "Pickup time adjusted to 20:00",
                                            "score": 10, "max_score": 10, "passed": True, "reason": "Correct delay offset"})
                            total_score += 10
                        else:
                            details.append({"item": "Pickup time adjusted to 20:00",
                                            "score": 0, "max_score": 10, "passed": False,
                                            "reason": f"Got '{tb['pickup_time']}' expected '{expected_pickup}'"})
                    else:
                        missing = expected_tb_fields - actual_tb_fields
                        details.append({"item": "Transport booking has all required fields",
                                        "score": 0, "max_score": 5, "passed": False,
                                        "reason": f"Missing fields: {missing}"})
            else:
                details.append({"item": "rescheduled_transports.json is a list",
                                "score": 0, "max_score": 5, "passed": False, "reason": "Not a list"})
    else:
        for item in ["rescheduled_transports.json is valid JSON", "Only one transport booking...",
                     "Transport booking has all required fields", "Correct transport booking_id TB001",
                     "Pickup time adjusted to 20:00"]:
            details.append({"item": item, "score": 0, "max_score": 5, "passed": False, "reason": "File missing"})

    # ---------- 验证 notification_log.txt ----------
    notif_path = os.path.join(workspace, "notification_log.txt")
    if os.path.isfile(notif_path):
        try:
            with open(notif_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            details.append({"item": "notification_log.txt readable",
                            "score": 0, "max_score": 5, "passed": False, "reason": f"Read error: {e}"})
        else:
            details.append({"item": "notification_log.txt readable",
                            "score": 5, "max_score": 5, "passed": True, "reason": "File present and readable"})
            total_score += 5
            # 检查是否包含航班号 UA123
            if "UA123" in content:
                details.append({"item": "Notification contains flight number UA123",
                                "score": 5, "max_score": 5, "passed": True, "reason": "Flight number found"})
                total_score += 5
            else:
                details.append({"item": "Notification contains flight number UA123",
                                "score": 0, "max_score": 5, "passed": False, "reason": "Not found"})
            # 检查延迟分钟数 120 或 2小时
            if "120" in content or "2 hours" in content or "two hours" in content:
                details.append({"item": "Notification contains delay duration (120 min or 2 hours)",
                                "score": 5, "max_score": 5, "passed": True, "reason": "Delay info found"})
                total_score += 5
            else:
                details.append({"item": "Notification contains delay duration (120 min or 2 hours)",
                                "score": 0, "max_score": 5, "passed": False, "reason": "Not found"})
            # 检查是否提及新入住日期 2025-06-16
            if "2025-06-16" in content:
                details.append({"item": "Notification mentions new check-in date 2025-06-16",
                                "score": 5, "max_score": 5, "passed": True, "reason": "Date found"})
                total_score += 5
            else:
                details.append({"item": "Notification mentions new check-in date 2025-06-16",
                                "score": 0, "max_score": 5, "passed": False, "reason": "Not found"})
            # 检查是否提及新接机时间 20:00
            if "20:00" in content:
                details.append({"item": "Notification mentions new pickup time 20:00",
                                "score": 5, "max_score": 5, "passed": True, "reason": "Time found"})
                total_score += 5
            else:
                details.append({"item": "Notification mentions new pickup time 20:00",
                                "score": 0, "max_score": 5, "passed": False, "reason": "Not found"})
    else:
        for item in ["notification_log.txt readable", "Notification contains flight number UA123",
                     "Notification contains delay duration", "Notification mentions new check-in date 2025-06-16",
                     "Notification mentions new pickup time 20:00"]:
            details.append({"item": item, "score": 0, "max_score": 5, "passed": False, "reason": "File missing"})

    # 计算总分（满分100）
    final_score = min(total_score, 100)
    result = {
        "total_score": final_score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written: {final_score}/100")

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
