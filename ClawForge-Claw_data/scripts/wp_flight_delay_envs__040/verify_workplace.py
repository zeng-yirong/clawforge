import sys
import json
import os
from pathlib import Path

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    root = Path(workspace)
    details = []
    total_score = 0

    # === 1. 检查 ops/delay_actions.json 是否存在 (10分) ===
    result_path = root / "ops" / "delay_actions.json"
    if result_path.exists():
        details.append({
            "item": "ops/delay_actions.json 存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "文件已找到"
        })
        total_score += 10
    else:
        details.append({
            "item": "ops/delay_actions.json 存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件不存在"
        })
        # 提前结束，后续检查无意义
        _write_score(total_score, details, root)
        return

    # === 2. JSON 合法性 (10分) ===
    try:
        with open(result_path, "r") as f:
            data = json.load(f)
        details.append({
            "item": "JSON 格式合法",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "解析成功"
        })
        total_score += 10
    except (json.JSONDecodeError, Exception) as e:
        details.append({
            "item": "JSON 格式合法",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"解析失败: {e}"
        })
        _write_score(total_score, details, root)
        return

    # === 3. 核心字段存在性 (20分) ===
    required_keys = ["flight_id", "delay_minutes", "affected_bookings"]
    missing_keys = [k for k in required_keys if k not in data]
    if not missing_keys:
        details.append({
            "item": "顶层必需字段 (flight_id, delay_minutes, affected_bookings)",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "所有必需字段存在"
        })
        total_score += 20
    else:
        details.append({
            "item": "顶层必需字段",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"缺失字段: {missing_keys}"
        })
        _write_score(total_score, details, root)
        return

    # === 4. 核心数值准确性 (30分) ===
    flight_id_ok = data["flight_id"] == "AA456"
    delay_ok = data["delay_minutes"] == 90
    if flight_id_ok and delay_ok:
        details.append({
            "item": "flight_id 和 delay_minutes 正确",
            "score": 30,
            "max_score": 30,
            "passed": True,
            "reason": "AA456, 90分钟"
        })
        total_score += 30
    else:
        score = 0
        if flight_id_ok:
            score += 15
        if delay_ok:
            score += 15
        details.append({
            "item": "flight_id 和 delay_minutes 正确",
            "score": score,
            "max_score": 30,
            "passed": (score == 30),
            "reason": f"flight_id={data.get('flight_id')} (期望AA456), delay_minutes={data.get('delay_minutes')} (期望90)"
        })

    # === 5. affected_bookings 准确性 (30分) ===
    bookings = data.get("affected_bookings", [])
    # 期望只有1个受影响预订：B001
    expected_booking_id = "B001"
    expected_passenger = "Jane Doe"
    expected_hotel = "Hilton Manhattan"
    # 交通重排：原18:00 -> 新19:30
    expected_transport = {
        "type": "limousine",
        "provider": "Blacklane",
        "original_pickup": "2025-04-10T18:00",
        "new_pickup": "2025-04-10T19:30"
    }
    # 通知应包含延误信息和新的接机时间
    # 不检查全文，但关键字必须包含

    if len(bookings) != 1:
        details.append({
            "item": "affected_bookings 数量",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"期望1个，实际{len(bookings)}个"
        })
        # 仍继续检查首个（如果有）
    else:
        details.append({
            "item": "affected_bookings 数量正确",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "刚好1个"
        })
        total_score += 10

    b = bookings[0] if bookings else {}

    # 检查 booking_id
    bid_ok = b.get("booking_id") == expected_booking_id
    if bid_ok:
        details.append({
            "item": "booking_id 正确",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "B001"
        })
        total_score += 5
    else:
        details.append({
            "item": "booking_id 正确",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": f"实际 {b.get('booking_id')}"
        })

    # 检查 passenger
    p_ok = b.get("passenger") == expected_passenger
    if p_ok:
        details.append({
            "item": "passenger 正确",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "Jane Doe"
        })
        total_score += 5
    else:
        details.append({
            "item": "passenger 正确",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": f"实际 {b.get('passenger')}"
        })

    # 检查 hotel 字段
    hotel_ok = b.get("hotel") == expected_hotel or b.get("hotel_name") == expected_hotel  # 允许两种key
    if hotel_ok:
        details.append({
            "item": "酒店名称正确",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "Hilton Manhattan"
        })
        total_score += 5
    else:
        details.append({
            "item": "酒店名称正确",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": f"实际 {b.get('hotel') or b.get('hotel_name')}"
        })

    # 检查 transport 重排
    t = b.get("transport", {})
    if isinstance(t, dict):
        t_type = t.get("type") == expected_transport["type"]
        t_prov = t.get("provider") == expected_transport["provider"]
        t_orig = t.get("original_pickup") == expected_transport["original_pickup"]
        t_new = t.get("new_pickup") == expected_transport["new_pickup"]
        transport_ok = t_type and t_prov and t_orig and t_new
        if transport_ok:
            details.append({
                "item": "transport 重排信息正确",
                "score": 5,
                "max_score": 5,
                "passed": True,
                "reason": "limousine/Blacklane, 18:00->19:30"
            })
            total_score += 5
        else:
            reasons = []
            if not t_type: reasons.append("type")
            if not t_prov: reasons.append("provider")
            if not t_orig: reasons.append("original_pickup")
            if not t_new: reasons.append("new_pickup")
            details.append({
                "item": "transport 重排信息正确",
                "score": 0,
                "max_score": 5,
                "passed": False,
                "reason": f"字段错误: {reasons}"
            })
    else:
        details.append({
            "item": "transport 重排信息正确",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "transport 非字典"
        })

    # 检查 notification 内容
    notif = b.get("notification", "")
    notif_ok = isinstance(notif, str) and "AA456" in notif and "90" in notif and delayed in notif and "19:30" in notif
    if notif_ok:
        details.append({
            "item": "notification 包含关键信息 (AA456, 90分钟, 19:30)",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "内容充分"
        })
        total_score += 5
    else:
        details.append({
            "item": "notification 包含关键信息",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": f"实际内容片段: {notif[:80]}"
        })

    # 最后一轮写分
    _write_score(total_score, details, root)

def _write_score(total, details, root):
    output = {
        "total_score": min(total, 100),
        "details": details
    }
    score_path = root / "workplace_score.json"
    with open(score_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"Score written: {output['total_score']}/100")

if __name__ == "__main__":
    verify()
