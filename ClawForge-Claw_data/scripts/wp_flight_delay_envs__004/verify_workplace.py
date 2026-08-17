import sys
import os
import json
import re

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results = []
    total_score = 0

    # 1. 目录结构检查 (10分)
    score_item = {"item": "ops 目录存在", "score": 0, "max_score": 5, "passed": False, "reason": ""}
    if os.path.isdir(os.path.join(workspace, "ops")):
        score_item["score"] = 5
        score_item["passed"] = True
        score_item["reason"] = "ops/ 目录存在"
    else:
        score_item["reason"] = "ops/ 目录缺失"
    results.append(score_item)
    total_score += score_item["score"]

    target_path = os.path.join(workspace, "ops", "delay_action_plan.json")
    score_item = {"item": "结果文件存在", "score": 0, "max_score": 5, "passed": False, "reason": ""}
    if os.path.isfile(target_path):
        score_item["score"] = 5
        score_item["passed"] = True
        score_item["reason"] = "ops/delay_action_plan.json 存在"
    else:
        score_item["reason"] = "结果文件缺失"
    results.append(score_item)
    total_score += score_item["score"]

    # 2. JSON合法性 (10分)
    score_item = {"item": "JSON 格式合法", "score": 0, "max_score": 10, "passed": False, "reason": ""}
    try:
        with open(target_path, "r") as f:
            data = json.load(f)
        score_item["score"] = 10
        score_item["passed"] = True
        score_item["reason"] = "JSON 解析成功"
    except (json.JSONDecodeError, FileNotFoundError) as e:
        score_item["reason"] = f"JSON 解析失败: {str(e)}"
        results.append(score_item)
        total_score += score_item["score"]
        # 如果文件不存在或格式错误，后续检查跳过
        write_score(results, total_score, target_path)
        return
    results.append(score_item)
    total_score += score_item["score"]

    # 3. 必填字段检查 (20分)
    required_keys = ["affected_hotel_bookings", "affected_transport_bookings", "notifications"]
    key_score = 20 / len(required_keys)
    for key in required_keys:
        item = {"item": f"结果包含字段 '{key}'", "score": 0, "max_score": key_score, "passed": False, "reason": ""}
        if key in data:
            item["score"] = key_score
            item["passed"] = True
            item["reason"] = f"字段 '{key}' 存在"
        else:
            item["reason"] = f"缺失字段 '{key}'"
        results.append(item)
        total_score += item["score"]

    # 4. 数据准确性检查 (60分)
    # 4a. 受影响酒店预订 (只与 FL001 且 status=confirmed 关联)
    correct_hotel_bookings = [
        {"booking_id": "HB001", "flight_id": "FL001", "contact_id": "C001", "hotel_id": "H001", "check_in": "2025-03-15", "check_out": "2025-03-17", "status": "confirmed"},
        {"booking_id": "HB002", "flight_id": "FL001", "contact_id": "C002", "hotel_id": "H001", "check_in": "2025-03-15", "check_out": "2025-03-16", "status": "confirmed"}
    ]
    hotel_bookings = data.get("affected_hotel_bookings", [])
    # 简化校验：只检查 booking_id 集合和个数
    correct_ids = {hb["booking_id"] for hb in correct_hotel_bookings}
    actual_ids = {hb.get("booking_id") for hb in hotel_bookings}
    if actual_ids == correct_ids:
        results.append({"item": "影响酒店预订 ID 正确", "score": 20, "max_score": 20, "passed": True, "reason": f"包含 {correct_ids}"})
        total_score += 20
    else:
        results.append({"item": "影响酒店预订 ID 错误", "score": 0, "max_score": 20, "passed": False,
                        "reason": f"期望 {correct_ids}, 实际 {actual_ids}"})

    # 4b. 受影响交通预订 (只与 FL001 且 status=confirmed)
    correct_transport_bookings = [
        {"booking_id": "TB001", "flight_id": "FL001", "contact_id": "C001", "transport_type": "limousine", "pickup_time": "2025-03-15 10:00", "status": "confirmed"},
        {"booking_id": "TB002", "flight_id": "FL001", "contact_id": "C002", "transport_type": "shuttle", "pickup_time": "2025-03-15 10:15", "status": "confirmed"}
    ]
    transport_bookings = data.get("affected_transport_bookings", [])
    correct_t_ids = {tb["booking_id"] for tb in correct_transport_bookings}
    actual_t_ids = {tb.get("booking_id") for tb in transport_bookings}
    if actual_t_ids == correct_t_ids:
        results.append({"item": "影响交通预订 ID 正确", "score": 20, "max_score": 20, "passed": True, "reason": f"包含 {correct_t_ids}"})
        total_score += 20
    else:
        results.append({"item": "影响交通预订 ID 错误", "score": 0, "max_score": 20, "passed": False,
                        "reason": f"期望 {correct_t_ids}, 实际 {actual_t_ids}"})

    # 4c. 通知 (每条应包含 contact_name, email, 延误说明)
    notifications = data.get("notifications", [])
    correct_notifications = [
        {"contact_name": "Jane Doe", "email": "jane.doe@example.com"},
        {"contact_name": "John Smith", "email": "john.smith@example.com"}
    ]
    if len(notifications) == len(correct_notifications):
        # 检查内容是否包含名字和邮箱（不严格要求顺序）
        notif_set = {(n.get("contact_name",""), n.get("email","")) for n in notifications}
        expected_set = {(n["contact_name"], n["email"]) for n in correct_notifications}
        if notif_set == expected_set:
            results.append({"item": "通知内容正确", "score": 20, "max_score": 20, "passed": True,
                            "reason": f"通知列表包含正确的联系人"})
            total_score += 20
        else:
            results.append({"item": "通知内容错误", "score": 0, "max_score": 20, "passed": False,
                            "reason": f"期望 {expected_set}, 实际 {notif_set}"})
    else:
        results.append({"item": "通知数量错误", "score": 0, "max_score": 20, "passed": False,
                        "reason": f"期望 {len(correct_notifications)} 条, 实际 {len(notifications)} 条"})

    # 5. 写入结果
    final_score = min(int(total_score), 100)
    output = {
        "total_score": final_score,
        "details": results
    }
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(output, f, indent=2)

def write_score(results, current_total, target_path):
    # 用于文件缺失时的快速写入
    output = {
        "total_score": current_total,
        "details": results
    }
    score_path = os.path.join(os.path.dirname(target_path), "..", "workplace_score.json")
    score_path = os.path.abspath(score_path)
    with open(score_path, "w") as f:
        json.dump(output, f, indent=2)

if __name__ == "__main__":
    verify()
