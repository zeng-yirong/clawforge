import sys
import os
import json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."

    details = []
    total_score = 0

    # 1. 检查 ops 目录是否存在 (10分)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        details.append({"item": "ops directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "目录存在"})
        total_score += 10
    else:
        details.append({"item": "ops directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "目录不存在"})

    # 2. 检查 best_flight.json 是否存在 (10分)
    target_file = os.path.join(ops_dir, "best_flight.json")
    if os.path.isfile(target_file):
        details.append({"item": "best_flight.json file exists", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
        total_score += 10
    else:
        details.append({"item": "best_flight.json file exists", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        # 如果文件不存在，后续检查无法进行，直接输出总分
        result = {"total_score": total_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # 3. 检查 JSON 格式合法性 (10分)
    try:
        with open(target_file, "r") as f:
            data = json.load(f)
        details.append({"item": "JSON format valid", "score": 10, "max_score": 10, "passed": True, "reason": "JSON解析成功"})
        total_score += 10
    except Exception as e:
        details.append({"item": "JSON format valid", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON解析失败: {str(e)}"})
        result = {"total_score": total_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # 4. 检查 flight_id 字段 (30分)
    expected_flight_id = "SB-123"
    if isinstance(data, dict) and "flight_id" in data:
        if data["flight_id"] == expected_flight_id:
            details.append({"item": "flight_id is correct", "score": 30, "max_score": 30, "passed": True, "reason": f"flight_id = {expected_flight_id}"})
            total_score += 30
        else:
            details.append({"item": "flight_id is correct", "score": 0, "max_score": 30, "passed": False, "reason": f"期望 {expected_flight_id}，实际 {data['flight_id']}"})
    else:
        details.append({"item": "flight_id is correct", "score": 0, "max_score": 30, "passed": False, "reason": "缺少flight_id字段或格式错误"})

    # 5. 检查 price 字段 (30分)
    expected_price = 8500
    if isinstance(data, dict) and "price" in data:
        if data["price"] == expected_price:
            details.append({"item": "price is correct", "score": 30, "max_score": 30, "passed": True, "reason": f"price = {expected_price}"})
            total_score += 30
        else:
            details.append({"item": "price is correct", "score": 0, "max_score": 30, "passed": False, "reason": f"期望 {expected_price}，实际 {data['price']}"})
    else:
        details.append({"item": "price is correct", "score": 0, "max_score": 30, "passed": False, "reason": "缺少price字段或格式错误"})

    # 6. 检查是否有多余字段 (10分) —— 只允许 flight_id 和 price
    allowed_keys = {"flight_id", "price"}
    if isinstance(data, dict):
        extra_keys = set(data.keys()) - allowed_keys
        if not extra_keys:
            details.append({"item": "no extra fields", "score": 10, "max_score": 10, "passed": True, "reason": "没有多余字段"})
            total_score += 10
        else:
            details.append({"item": "no extra fields", "score": 0, "max_score": 10, "passed": False, "reason": f"发现多余字段: {extra_keys}"})
    else:
        details.append({"item": "no extra fields", "score": 0, "max_score": 10, "passed": False, "reason": "JSON不是字典对象"})

    # 写入评分结果
    result = {"total_score": total_score, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
