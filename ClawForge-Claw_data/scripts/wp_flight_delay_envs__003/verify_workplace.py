import json
import sys
import os
from pathlib import Path

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    ws = Path(workspace)
    scores = []
    max_total = 100

    # 1. 文件存在 (10分)
    target = ws / "ops" / "action_plan.json"
    if target.exists():
        scores.append({"item": "action_plan.json 存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件已创建"})
    else:
        scores.append({"item": "action_plan.json 存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        # 直接结束，无需后续检查
        total = sum(s["score"] for s in scores)
        with open(ws / "workplace_score.json", "w") as f:
            json.dump({"total_score": total, "details": scores}, f, indent=2)
        return

    # 2. JSON 合法 (10分)
    try:
        data = load_json(target)
        scores.append({"item": "JSON 解析合法", "score": 10, "max_score": 10, "passed": True, "reason": "语法正确"})
    except Exception as e:
        with open(ws / "workplace_score.json", "w") as f:
            json.dump({"total_score": 10, "details": [{"item": "JSON 解析合法", "score": 0, "max_score": 10, "passed": False, "reason": str(e)}]}, f, indent=2)
        return

    # 3. 字段完整性 (10分)
    required_keys = {"flight_id", "flight_number", "delay_minutes", "affected_hotel_bookings",
                     "affected_transport_bookings", "recommended_actions", "notification_recipient"}
    actual_keys = set(data.keys())
    missing = required_keys - actual_keys
    extra = actual_keys - required_keys
    if missing:
        scores.append({"item": "必需字段完整", "score": 0, "max_score": 10, "passed": False,
                       "reason": f"缺少字段: {missing}"})
    else:
        penalty = 0
        if extra:
            penalty = min(5, len(extra) * 2)  # 每多一个字段扣2分，最多扣5
        base = 10 - penalty
        scores.append({"item": "必需字段完整", "score": base, "max_score": 10, "passed": base >= 5,
                       "reason": f"额外字段: {extra if extra else '无'}"})

    # 4. 航班信息正确 (10分)
    flight_ok = (
        data.get("flight_id") == "F001" and
        data.get("flight_number") == "AA456" and
        data.get("delay_minutes") == 120
    )
    scores.append({"item": "航班信息 (flight_id, flight_number, delay_minutes)", "score": 10 if flight_ok else 0,
                   "max_score": 10, "passed": flight_ok,
                   "reason": "正确" if flight_ok else f"预期 F001/AA456/120，实际 {data.get('flight_id')}/{data.get('flight_number')}/{data.get('delay_minutes')}"})

    # 5. 受影响酒店预订 (15分)
    affected_hotels = data.get("affected_hotel_bookings", [])
    if isinstance(affected_hotels, list) and len(affected_hotels) == 1 and affected_hotels[0] == "HB003":
        scores.append({"item": "affected_hotel_bookings 正确", "score": 15, "max_score": 15, "passed": True, "reason": "包含 HB003"})
    else:
        scores.append({"item": "affected_hotel_bookings 正确", "score": 0, "max_score": 15, "passed": False,
                       "reason": f"预期 ['HB003']，实际 {affected_hotels}"})

    # 6. 受影响交通预订 (15分)
    affected_transports = data.get("affected_transport_bookings", [])
    if isinstance(affected_transports, list) and len(affected_transports) == 1 and affected_transports[0] == "TB001":
        scores.append({"item": "affected_transport_bookings 正确", "score": 15, "max_score": 15, "passed": True, "reason": "包含 TB001"})
    else:
        scores.append({"item": "affected_transport_bookings 正确", "score": 0, "max_score": 15, "passed": False,
                       "reason": f"预期 ['TB001']，实际 {affected_transports}"})

    # 7. 推荐操作 (20分)
    actions = data.get("recommended_actions", [])
    expected_actions = [
        {"type": "adjust_hotel", "booking_id": "HB003", "new_check_in": "2025-03-21", "new_check_out": "2025-03-23", "reason": "hotel full on original date"},
        {"type": "reschedule_transport", "booking_id": "TB001", "new_pickup_time": "2025-03-20T18:00", "reason": "flight delay"}
    ]
    action_ok = True
    reason_extra = ""
    if not isinstance(actions, list) or len(actions) != 2:
        action_ok = False
        reason_extra = f"长度应为2，实际 {len(actions)}"
    else:
        for i, (exp, act) in enumerate(zip(expected_actions, actions)):
            if exp != act:
                action_ok = False
                reason_extra = f"第{i+1}项不匹配：预期 {exp}，实际 {act}"
                break
    scores.append({"item": "recommended_actions 正确", "score": 20 if action_ok else 0,
                   "max_score": 20, "passed": action_ok,
                   "reason": "正确" if action_ok else reason_extra})

    # 8. 通知收件人 (10分)
    recipient = data.get("notification_recipient")
    if recipient == "john.smith@example.com":
        scores.append({"item": "notification_recipient 正确", "score": 10, "max_score": 10, "passed": True, "reason": "邮箱正确"})
    else:
        scores.append({"item": "notification_recipient 正确", "score": 0, "max_score": 10, "passed": False,
                       "reason": f"预期 john.smith@example.com，实际 {recipient}"})

    total = sum(s["score"] for s in scores)
    with open(ws / "workplace_score.json", "w") as f:
        json.dump({"total_score": total, "details": scores}, f, indent=2)

if __name__ == "__main__":
    main()
