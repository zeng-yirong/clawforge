import sys
import os
import json
import math

def verify(workspace: str) -> dict:
    details = []
    total_score = 0
    max_total = 100

    # 1. 目录结构（10分）
    ops_dir = os.path.join(workspace, "ops")
    data_dir = os.path.join(workspace, "data")
    dirs_exist = os.path.isdir(ops_dir) and os.path.isdir(data_dir)
    details.append({
        "item": "目录结构（ops/ 和 data/ 存在）",
        "score": 10 if dirs_exist else 0,
        "max_score": 10,
        "passed": dirs_exist,
        "reason": "ops/ and data/ directories exist" if dirs_exist else "ops/ or data/ missing"
    })
    if dirs_exist:
        total_score += 10

    # 2. 产物文件存在（10分）
    target_path = os.path.join(workspace, "ops", "defog_recommendation.json")
    file_exists = os.path.isfile(target_path)
    details.append({
        "item": "产物文件 ops/defog_recommendation.json 存在",
        "score": 10 if file_exists else 0,
        "max_score": 10,
        "passed": file_exists,
        "reason": "File exists" if file_exists else "File not found"
    })
    if file_exists:
        total_score += 10

    # 3. JSON 合法（10分）
    if file_exists:
        try:
            with open(target_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            json_valid = True
        except (json.JSONDecodeError, UnicodeDecodeError):
            data = None
            json_valid = False
    else:
        json_valid = False
        data = None
    details.append({
        "item": "JSON 格式合法",
        "score": 10 if json_valid else 0,
        "max_score": 10,
        "passed": json_valid,
        "reason": "Valid JSON" if json_valid else "Invalid or unreadable JSON"
    })
    if json_valid:
        total_score += 10

    # 4. 字段完整性（20分，每个必要字段5分，共4个字段）
    required_fields = ["average_temperature", "recommended_fan_speed", "preset_ids"]
    field_scores = {}
    if json_valid and isinstance(data, dict):
        for field in required_fields:
            if field in data:
                field_scores[field] = 5
            else:
                field_scores[field] = 0
        # 额外检查不可有多余字段？（可选扣分，但这里不加分也不扣分，保持简单）
    else:
        for field in required_fields:
            field_scores[field] = 0

    field_total = sum(field_scores.values())
    details.append({
        "item": "字段完整性（average_temperature, recommended_fan_speed, preset_ids）",
        "score": field_total,
        "max_score": 15,  # 15分（三个字段各5分）
        "passed": field_total == 15,
        "reason": f"Fields present: {[f for f in required_fields if field_scores[f]==5]}" if field_total == 15 else f"Missing fields: {[f for f in required_fields if field_scores[f]==0]}"
    })
    total_score += field_total

    # 5. 数值正确性（50分）
    correct_avg = 26
    correct_fan = "high"
    correct_ids = sorted(["preset_1", "preset_2", "preset_4"])

    avg_score = 0
    fan_score = 0
    ids_score = 0

    if json_valid and isinstance(data, dict):
        # 平均温度
        avg = data.get("average_temperature")
        if isinstance(avg, (int, float)) and round(float(avg)) == correct_avg:
            avg_score = 20
        # 风扇速度
        fan = data.get("recommended_fan_speed")
        if isinstance(fan, str) and fan == correct_fan:
            fan_score = 20
        # 预设ID列表（比较排序后是否一致）
        ids = data.get("preset_ids")
        if isinstance(ids, list) and sorted(ids) == correct_ids:
            ids_score = 10

    total_accuracy = avg_score + fan_score + ids_score
    details.append({
        "item": "average_temperature 正确（26）",
        "score": avg_score,
        "max_score": 20,
        "passed": avg_score == 20,
        "reason": f"average_temperature = {data.get('average_temperature')}" if avg_score == 20 else f"Expected 26, got {data.get('average_temperature')}"
    })
    details.append({
        "item": "recommended_fan_speed 正确（high）",
        "score": fan_score,
        "max_score": 20,
        "passed": fan_score == 20,
        "reason": f"recommended_fan_speed = {data.get('recommended_fan_speed')}" if fan_score == 20 else f"Expected 'high', got {data.get('recommended_fan_speed')}"
    })
    details.append({
        "item": "preset_ids 列表正确（preset_1, preset_2, preset_4）",
        "score": ids_score,
        "max_score": 10,
        "passed": ids_score == 10,
        "reason": f"preset_ids = {data.get('preset_ids')}" if ids_score == 10 else f"Expected {correct_ids}, got {data.get('preset_ids')}"
    })

    total_score += total_accuracy

    # 最终总分（0-100）
    total_score = min(total_score, 100)  # 防止超出

    result = {
        "total_score": total_score,
        "details": details
    }
    return result

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    # 写入结果
    output_path = os.path.join(workspace, "workplace_score.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
