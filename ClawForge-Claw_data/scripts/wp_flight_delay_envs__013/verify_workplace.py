import json
import os
import sys

def check_file_exists(path, workspace):
    full = os.path.join(workspace, path)
    return os.path.isfile(full)

def load_json(path, workspace):
    full = os.path.join(workspace, path)
    with open(full, "r") as f:
        return json.load(f)

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    # 1. 检查目录 ops 是否存在 (10分)
    ops_dir = os.path.join(workspace, "ops")
    passed = os.path.isdir(ops_dir)
    details.append({
        "item": "ops directory exists",
        "score": 10 if passed else 0,
        "max_score": 10,
        "passed": passed,
        "reason": "Directory ops/ found" if passed else "Directory ops/ missing"
    })
    if passed:
        score += 10

    # 2. 检查推荐报告文件是否存在 (10分)
    report_path = "ops/delay_cascade_report.json"
    passed = check_file_exists(report_path, workspace)
    details.append({
        "item": "Report file ops/delay_cascade_report.json exists",
        "score": 10 if passed else 0,
        "max_score": 10,
        "passed": passed,
        "reason": "File found" if passed else "File missing"
    })
    if passed:
        score += 10

    # 3. 报告JSON合法性 (10分)
    if passed:
        try:
            data = load_json(report_path, workspace)
            json_valid = True
        except Exception as e:
            json_valid = False
            reason = f"Invalid JSON: {e}"
        else:
            reason = "Valid JSON"
        details.append({
            "item": "Report is valid JSON",
            "score": 10 if json_valid else 0,
            "max_score": 10,
            "passed": json_valid,
            "reason": reason
        })
        if json_valid:
            score += 10
        else:
            # 后续检查跳过
            pass
    else:
        details.append({
            "item": "Report is valid JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File missing, cannot parse"
        })

    # 只有文件存在且合法才继续详细检查
    if passed and json_valid:
        # 4. 检查 flight_id (10分)
        expected_flight_id = "FL-001"
        actual = data.get("flight_id")
        passed = actual == expected_flight_id
        details.append({
            "item": "flight_id equals FL-001",
            "score": 10 if passed else 0,
            "max_score": 10,
            "passed": passed,
            "reason": f"Got {actual}" if not passed else "Correct"
        })
        if passed:
            score += 10

        # 5. 检查 delay_minutes (10分)
        expected_delay = 120
        actual = data.get("delay_minutes")
        passed = actual == expected_delay
        details.append({
            "item": "delay_minutes equals 120",
            "score": 10 if passed else 0,
            "max_score": 10,
            "passed": passed,
            "reason": f"Got {actual}" if not passed else "Correct"
        })
        if passed:
            score += 10

        # 6. 检查 impacted_hotel_booking (20分)
        hotel = data.get("impacted_hotel_booking")
        if hotel and isinstance(hotel, dict):
            expected_hotel = {
                "booking_id": "HB-001",
                "guest_name": "John Smith",
                "original_checkin": "2025-07-15",
                "adjusted_checkin": "2025-07-16",
                "status": "adjusted"
            }
            hotel_ok = all(hotel.get(k) == v for k, v in expected_hotel.items())
            hotel_score = 20 if hotel_ok else 0
            reason = "All fields match" if hotel_ok else f"Mismatch: {hotel}"
        else:
            hotel_ok = False
            hotel_score = 0
            reason = "Missing or not dict"
        details.append({
            "item": "impacted_hotel_booking fields correct",
            "score": hotel_score,
            "max_score": 20,
            "passed": hotel_ok,
            "reason": reason
        })
        if hotel_ok:
            score += 20

        # 7. 检查 impacted_transport_booking (20分)
        transport = data.get("impacted_transport_booking")
        if transport and isinstance(transport, dict):
            expected_transport = {
                "booking_id": "TB-001",
                "transport_type": "shuttle",
                "original_time": "2025-07-15T22:30:00",
                "rescheduled_time": "2025-07-16T00:30:00",
                "status": "rescheduled"
            }
            transport_ok = all(transport.get(k) == v for k, v in expected_transport.items())
            transport_score = 20 if transport_ok else 0
            reason = "All fields match" if transport_ok else f"Mismatch: {transport}"
        else:
            transport_ok = False
            transport_score = 0
            reason = "Missing or not dict"
        details.append({
            "item": "impacted_transport_booking fields correct",
            "score": transport_score,
            "max_score": 20,
            "passed": transport_ok,
            "reason": reason
        })
        if transport_ok:
            score += 20

        # 8. 检查 notification_sent (20分)
        notif = data.get("notification_sent")
        if notif and isinstance(notif, dict):
            expected_notif = {
                "to": "john.smith@example.com",
                "status": "sent"
            }
            notif_ok = all(notif.get(k) == v for k, v in expected_notif.items())
            notif_score = 20 if notif_ok else 0
            reason = "All fields match" if notif_ok else f"Mismatch: {notif}"
        else:
            notif_ok = False
            notif_score = 0
            reason = "Missing or not dict"
        details.append({
            "item": "notification_sent fields correct",
            "score": notif_score,
            "max_score": 20,
            "passed": notif_ok,
            "reason": reason
        })
        if notif_ok:
            score += 20

    # 写入结果
    result = {
        "total_score": score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
