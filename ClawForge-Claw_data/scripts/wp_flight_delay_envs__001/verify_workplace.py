import json
import sys
import os
from pathlib import Path

def verify(workspace: str):
    details = []
    total_score = 0

    # 1. 检查ops目录是否存在 (5分)
    ops_dir = Path(workspace) / "ops"
    item = {"item": "ops directory exists", "score": 0, "max_score": 5, "passed": False, "reason": ""}
    if ops_dir.is_dir():
        item["score"] = 5
        item["passed"] = True
        item["reason"] = "ops directory found"
    else:
        item["reason"] = "ops directory missing"
    details.append(item)
    total_score += item["score"]

    # 2. 检查cascade_action_report.json是否存在 (5分)
    report_path = ops_dir / "cascade_action_report.json"
    item = {"item": "cascade_action_report.json exists", "score": 0, "max_score": 5, "passed": False, "reason": ""}
    if report_path.is_file():
        item["score"] = 5
        item["passed"] = True
        item["reason"] = "file found"
    else:
        item["reason"] = f"file not found at {report_path}"
    details.append(item)
    total_score += item["score"]

    # 3. JSON解析合法性 (10分)
    item = {"item": "JSON is valid", "score": 0, "max_score": 10, "passed": False, "reason": ""}
    if report_path.is_file():
        try:
            with open(report_path, "r") as f:
                data = json.load(f)
            item["score"] = 10
            item["passed"] = True
            item["reason"] = "valid JSON"
        except (json.JSONDecodeError, Exception) as e:
            item["reason"] = f"JSON parse error: {e}"
    else:
        item["reason"] = "file missing"
    details.append(item)
    total_score += item["score"]

    # 接下来需要成功解析才能继续检查
    if report_path.is_file() and "data" in locals():
        with open(report_path, "r") as f:
            data = json.load(f)
    else:
        data = None

    # 4. 包含flight_id字段且值为UA123 (10分)
    item = {"item": "flight_id field correctness", "score": 0, "max_score": 10, "passed": False, "reason": ""}
    if data and isinstance(data, dict) and "flight_id" in data:
        if data["flight_id"] == "UA123":
            item["score"] = 10
            item["passed"] = True
            item["reason"] = "flight_id is UA123"
        else:
            item["reason"] = f"expected UA123, got {data['flight_id']}"
    else:
        item["reason"] = "missing flight_id field"
    details.append(item)
    total_score += item["score"]

    # 5. affected_hotel_booking 正确性 (20分)
    item = {"item": "affected_hotel_booking details", "score": 0, "max_score": 20, "passed": False, "reason": ""}
    if data and isinstance(data, dict) and "affected_hotel_booking" in data:
        hb = data["affected_hotel_booking"]
        if isinstance(hb, dict) and all(k in hb for k in ("booking_id", "new_checkin", "new_checkout", "action")):
            bid = hb["booking_id"]
            new_checkin = hb["new_checkin"]
            new_checkout = hb["new_checkout"]
            action = hb["action"]
            if bid == "B1" and new_checkin == "2025-03-21" and new_checkout == "2025-03-22" and action == "change_dates":
                item["score"] = 20
                item["passed"] = True
                item["reason"] = f"booking_id=B1, checkin=2025-03-21, checkout=2025-03-22, action=change_dates"
            else:
                item["reason"] = f"expected B1/2025-03-21/2025-03-22/change_dates, got {bid}/{new_checkin}/{new_checkout}/{action}"
        else:
            item["reason"] = "affected_hotel_booking missing required fields"
    else:
        item["reason"] = "missing affected_hotel_booking"
    details.append(item)
    total_score += item["score"]

    # 6. rescheduled_transport 正确性 (20分)
    item = {"item": "rescheduled_transport details", "score": 0, "max_score": 20, "passed": False, "reason": ""}
    if data and isinstance(data, dict) and "rescheduled_transport" in data:
        rt = data["rescheduled_transport"]
        if isinstance(rt, dict) and all(k in rt for k in ("booking_id", "new_pickup_date", "new_pickup_time")):
            bid = rt["booking_id"]
            new_date = rt["new_pickup_date"]
            new_time = rt["new_pickup_time"]
            if bid == "T2" and new_date == "2025-03-21" and new_time == "00:30":
                item["score"] = 20
                item["passed"] = True
                item["reason"] = f"booking_id=T2, date=2025-03-21, time=00:30"
            else:
                item["reason"] = f"expected T2/2025-03-21/00:30, got {bid}/{new_date}/{new_time}"
        else:
            item["reason"] = "rescheduled_transport missing required fields"
    else:
        item["reason"] = "missing rescheduled_transport"
    details.append(item)
    total_score += item["score"]

    # 7. notifications_sent 正确性 (20分)
    item = {"item": "notifications_sent details", "score": 0, "max_score": 20, "passed": False, "reason": ""}
    if data and isinstance(data, dict) and "notifications_sent" in data:
        ns = data["notifications_sent"]
        if isinstance(ns, list) and len(ns) > 0:
            entry = ns[0]
            if isinstance(entry, dict) and all(k in entry for k in ("contact_id", "type", "status")):
                if entry["contact_id"] == "C2" and entry["type"] == "delay_and_change" and entry["status"] == "sent":
                    item["score"] = 20
                    item["passed"] = True
                    item["reason"] = "notification for C2, type delay_and_change, status sent"
                else:
                    item["reason"] = f"expected C2/delay_and_change/sent, got {entry['contact_id']}/{entry['type']}/{entry['status']}"
            else:
                item["reason"] = "first notification entry missing required fields"
        else:
            item["reason"] = "notifications_sent is empty or not a list"
    else:
        item["reason"] = "missing notifications_sent"
    details.append(item)
    total_score += item["score"]

    # 8. 检查没有额外多余航班 (10分) - 只接受一个flight_id, 并且是UA123
    item = {"item": "no extra flights in report", "score": 0, "max_score": 10, "passed": False, "reason": ""}
    if data and isinstance(data, dict):
        # 检查是否包含其他意外字段如另一个flight_id
        if "affected_flights" in data:
            item["reason"] = "unexpected affected_flights field"
        elif any(k for k in data if "flight" in k.lower() and k != "flight_id"):
            item["reason"] = "unexpected flight-related field"
        else:
            # 如果只有flight_id且值为UA123, 无多余, 通过
            if data.get("flight_id") == "UA123":
                item["score"] = 10
                item["passed"] = True
                item["reason"] = "only expected flight_id present"
            else:
                item["reason"] = "flight_id incorrect, cannot award extra"
    else:
        item["reason"] = "data not available"
    details.append(item)
    total_score += item["score"]

    # 写入结果
    result = {
        "total_score": total_score,
        "details": details
    }
    with open(Path(workspace) / "workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

    print(f"Total score: {total_score}/100")
    return total_score

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
