"""
验证脚本：检查 agent 是否在 ops/ 下生成了 affected_bookings.json，
内容是否正确反映了 UA123 延误影响的预订和通知收件人。
满分 100，细粒度扣分。
"""
import json
import os
import sys

def verify(workspace):
    details = []
    total = 0

    # 1. ops 目录存在 (10分)
    ops_path = os.path.join(workspace, "ops")
    if os.path.isdir(ops_path):
        details.append({"item": "ops/ 目录存在", "score": 10, "max_score": 10, "passed": True, "reason": "ops/ 目录已创建"})
        total += 10
    else:
        details.append({"item": "ops/ 目录存在", "score": 0, "max_score": 10, "passed": False, "reason": "缺少 ops/ 目录"})
        # 后续检查不再有意义，直接返回
        _write_score(details, total, workspace)
        return

    # 2. affected_bookings.json 文件存在 (10分)
    target_file = os.path.join(ops_path, "affected_bookings.json")
    if not os.path.isfile(target_file):
        details.append({"item": "affected_bookings.json 文件存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件未找到"})
        _write_score(details, total, workspace)
        return
    details.append({"item": "affected_bookings.json 文件存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
    total += 10

    # 3. JSON 合法 (10分)
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        details.append({"item": "JSON 格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "解析成功"})
        total += 10
    except Exception as e:
        details.append({"item": "JSON 格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {str(e)}"})
        _write_score(details, total, workspace)
        return

    # 4. 必要字段存在 (20分)
    required_fields = ["flight_id", "delay_minutes", "affected_hotel_bookings", "affected_transport_bookings", "notification_recipients"]
    missing = [f for f in required_fields if f not in data]
    if missing:
        details.append({"item": "必要字段完整性", "score": 0, "max_score": 20, "passed": False, "reason": f"缺少字段: {', '.join(missing)}"})
        _write_score(details, total, workspace)
        return
    details.append({"item": "必要字段完整性", "score": 20, "max_score": 20, "passed": True, "reason": "所有必需字段都存在"})
    total += 20

    # 5. 核心值正确性 (50分)
    # 子项：flight_id, delay_minutes, affected_hotel_bookings 列表, affected_transport_bookings 列表, notification_recipients 列表
    correct = True
    reasons = []

    # 5.1 flight_id
    if data["flight_id"] != "UA123":
        correct = False
        reasons.append("flight_id 应为 UA123，实际为 " + data["flight_id"])
    # 5.2 delay_minutes
    if data["delay_minutes"] != 120:
        correct = False
        reasons.append("delay_minutes 应为 120，实际为 " + str(data["delay_minutes"]))
    # 5.3 affected_hotel_bookings (应为 HB001, HB002 两个，顺序可任意)
    expected_hotels = {"HB001", "HB002"}
    actual_hotels = set(data.get("affected_hotel_bookings", []))
    if actual_hotels != expected_hotels:
        correct = False
        reasons.append(f"affected_hotel_bookings 应为 {sorted(expected_hotels)}，实际为 {sorted(actual_hotels)}")
    # 5.4 affected_transport_bookings (应为 TB001)
    expected_transports = {"TB001"}
    actual_transports = set(data.get("affected_transport_bookings", []))
    if actual_transports != expected_transports:
        correct = False
        reasons.append(f"affected_transport_bookings 应为 {sorted(expected_transports)}，实际为 {sorted(actual_transports)}")
    # 5.5 notification_recipients (应为 john.smith@example.com 和 jane.doe@example.com)
    expected_emails = {"john.smith@example.com", "jane.doe@example.com"}
    actual_emails = set(data.get("notification_recipients", []))
    if actual_emails != expected_emails:
        correct = False
        reasons.append(f"notification_recipients 应为 {sorted(expected_emails)}，实际为 {sorted(actual_emails)}")

    if correct:
        details.append({"item": "核心数值与列表完全正确", "score": 50, "max_score": 50, "passed": True, "reason": "所有值均符合预期"})
        total += 50
    else:
        details.append({"item": "核心数值与列表完全正确", "score": 0, "max_score": 50, "passed": False, "reason": "; ".join(reasons)})

    # 写入结果
    _write_score(details, total, workspace)


def _write_score(details, total, workspace):
    result = {
        "total_score": total,
        "details": details
    }
    out_path = os.path.join(workspace, "workplace_score.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"Score written: total={total}/100")


if __name__ == "__main__":
    ws = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(ws)
