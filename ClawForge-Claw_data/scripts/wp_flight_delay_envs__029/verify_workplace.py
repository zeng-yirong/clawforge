import sys
import json
import os

def verify(workspace):
    details = []
    total_score = 0

    # 1. ops 目录存在 (10分)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        details.append({"item": "ops目录存在", "score": 10, "max_score": 10, "passed": True, "reason": "ops目录存在"})
        total_score += 10
    else:
        details.append({"item": "ops目录存在", "score": 0, "max_score": 10, "passed": False, "reason": "ops目录不存在"})

    # 2. adjustments.json 文件存在 (10分)
    adj_path = os.path.join(ops_dir, "adjustments.json")
    if not os.path.isfile(adj_path):
        details.append({"item": "adjustments.json文件存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        details.append({"item": "JSON合法性", "score": 0, "max_score": 10, "passed": False, "reason": "文件缺失"})
        details.append({"item": "字段完整性", "score": 0, "max_score": 20, "passed": False, "reason": "文件缺失"})
        details.append({"item": "酒店调整值", "score": 0, "max_score": 25, "passed": False, "reason": "文件缺失"})
        details.append({"item": "交通调整值", "score": 0, "max_score": 25, "passed": False, "reason": "文件缺失"})
        return details, total_score

    details.append({"item": "adjustments.json文件存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
    total_score += 10

    # 3. JSON 合法性 (10分)
    try:
        with open(adj_path, "r") as f:
            data = json.load(f)
        details.append({"item": "JSON合法性", "score": 10, "max_score": 10, "passed": True, "reason": "JSON格式正确"})
        total_score += 10
    except Exception as e:
        details.append({"item": "JSON合法性", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON解析失败: {e}"})
        details.append({"item": "字段完整性", "score": 0, "max_score": 20, "passed": False, "reason": "JSON解析失败"})
        details.append({"item": "酒店调整值", "score": 0, "max_score": 25, "passed": False, "reason": "JSON解析失败"})
        details.append({"item": "交通调整值", "score": 0, "max_score": 25, "passed": False, "reason": "JSON解析失败"})
        return details, total_score

    # 4. 字段完整性 (20分)
    required_keys = ["flight_id", "passenger_name", "hotel_adjustment", "transport_adjustment"]
    missing = [k for k in required_keys if k not in data]
    if not missing:
        hotel_adj = data.get("hotel_adjustment", {})
        transport_adj = data.get("transport_adjustment", {})
        sub_missing = []
        if "new_check_in" not in hotel_adj:
            sub_missing.append("hotel_adjustment.new_check_in")
        if "new_pickup_time" not in transport_adj:
            sub_missing.append("transport_adjustment.new_pickup_time")
        if sub_missing:
            details.append({"item": "字段完整性", "score": 5, "max_score": 20, "passed": False, "reason": f"缺少子字段: {sub_missing}"})
            total_score += 5
        else:
            details.append({"item": "字段完整性", "score": 20, "max_score": 20, "passed": True, "reason": "所有必需字段存在"})
            total_score += 20
    else:
        details.append({"item": "字段完整性", "score": 5, "max_score": 20, "passed": False, "reason": f"缺少顶层字段: {missing}"})
        total_score += 5

    # 5. 酒店调整值 (25分)
    expected_hotel_checkin = "2025-03-16"
    hotel_adj = data.get("hotel_adjustment", {})
    actual_checkin = hotel_adj.get("new_check_in")
    if actual_checkin == expected_hotel_checkin:
        details.append({"item": "酒店调整值", "score": 25, "max_score": 25, "passed": True, "reason": f"新入住日期正确: {actual_checkin}"})
        total_score += 25
    else:
        details.append({"item": "酒店调整值", "score": 0, "max_score": 25, "passed": False, "reason": f"期望 {expected_hotel_checkin}, 实际 {actual_checkin}"})

    # 6. 交通调整值 (25分)
    # 原23:30 + 90分钟 = 次日01:00
    expected_pickup = "2025-03-16T01:00"
    transport_adj = data.get("transport_adjustment", {})
    actual_pickup = transport_adj.get("new_pickup_time")
    if actual_pickup == expected_pickup:
        details.append({"item": "交通调整值", "score": 25, "max_score": 25, "passed": True, "reason": f"新接机时间正确: {actual_pickup}"})
        total_score += 25
    else:
        details.append({"item": "交通调整值", "score": 0, "max_score": 25, "passed": False, "reason": f"期望 {expected_pickup}, 实际 {actual_pickup}"})

    return details, total_score

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details, total = verify(workspace)
    result = {
        "total_score": total,
        "details": details
    }
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Total score: {total}/100")

if __name__ == "__main__":
    main()
