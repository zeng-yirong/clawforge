import sys
import os
import json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    max_score = 100
    details = []

    # 1. 检查必要目录 (10分)
    required_dirs = ["data", "data/devices", "data/health", "data/electricity", "data/weather", "ops"]
    dir_score = 0
    for d in required_dirs:
        if os.path.isdir(os.path.join(workspace, d)):
            dir_score += 1
    dir_score = dir_score  # 满分6分但只给10分按比例? 简化：全部存在得10分
    if dir_score == len(required_dirs):
        score += 10
        details.append({"item": "Required directories exist", "score": 10, "max_score": 10, "passed": True, "reason": "All required directories present"})
    else:
        score += 0
        details.append({"item": "Required directories exist", "score": 0, "max_score": 10, "passed": False, "reason": f"Missing directories, got {dir_score}/{len(required_dirs)}"})

    # 2. 检查产物文件 ops/violations.json 是否存在 (10分)
    violations_path = os.path.join(workspace, "ops", "violations.json")
    if os.path.isfile(violations_path):
        score += 10
        details.append({"item": "ops/violations.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "File found"})
    else:
        score += 0
        details.append({"item": "ops/violations.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "File not found"})
        # 后续检查无法进行，直接输出当前分数
        write_score(workspace, score, details, max_score)
        return

    # 3. 解析JSON合法性 (10分)
    try:
        with open(violations_path, 'r') as f:
            data = json.load(f)
        score += 10
        details.append({"item": "JSON is valid", "score": 10, "max_score": 10, "passed": True, "reason": "Parsed successfully"})
    except Exception as e:
        score += 0
        details.append({"item": "JSON is valid", "score": 0, "max_score": 10, "passed": False, "reason": f"Parse error: {e}"})
        write_score(workspace, score, details, max_score)
        return

    # 4. 检查是否为list (10分)
    if isinstance(data, list):
        score += 10
        details.append({"item": "Root element is a list", "score": 10, "max_score": 10, "passed": True, "reason": "Type is list"})
    else:
        score += 0
        details.append({"item": "Root element is a list", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected list, got {type(data).__name__}"})
        write_score(workspace, score, details, max_score)
        return

    # 5. 列表长度应为1 (10分)
    if len(data) == 1:
        score += 10
        details.append({"item": "Violation count == 1", "score": 10, "max_score": 10, "passed": True, "reason": "Exactly one violation"})
    else:
        score += 0
        details.append({"item": "Violation count == 1", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected 1, got {len(data)}"})
        # 继续检查第一个元素可能仍有部分正确

    violation = data[0] if data else {}

    # 6. device_id = "bedroom_ac" (15分)
    expected_device = "bedroom_ac"
    if violation.get("device_id") == expected_device:
        score += 15
        details.append({"item": "device_id is correct", "score": 15, "max_score": 15, "passed": True, "reason": f"Got {expected_device}"})
    else:
        score += 0
        details.append({"item": "device_id is correct", "score": 0, "max_score": 15, "passed": False, "reason": f"Expected {expected_device}, got {violation.get('device_id')}"})

    # 7. violation_type = "temperature" (15分)
    expected_type = "temperature"
    if violation.get("violation_type") == expected_type:
        score += 15
        details.append({"item": "violation_type is correct", "score": 15, "max_score": 15, "passed": True, "reason": f"Got {expected_type}"})
    else:
        score += 0
        details.append({"item": "violation_type is correct", "score": 0, "max_score": 15, "passed": False, "reason": f"Expected {expected_type}, got {violation.get('violation_type')}"})

    # 8. current_value = 18 (15分)
    expected_current = 18
    if violation.get("current_value") == expected_current:
        score += 15
        details.append({"item": "current_value is correct", "score": 15, "max_score": 15, "passed": True, "reason": f"Got {expected_current}"})
    else:
        score += 0
        details.append({"item": "current_value is correct", "score": 0, "max_score": 15, "passed": False, "reason": f"Expected {expected_current}, got {violation.get('current_value')}"})

    # 9. recommended_value = 22 (15分)
    expected_recommended = 22
    if violation.get("recommended_value") == expected_recommended:
        score += 15
        details.append({"item": "recommended_value is correct", "score": 15, "max_score": 15, "passed": True, "reason": f"Got {expected_recommended}"})
    else:
        score += 0
        details.append({"item": "recommended_value is correct", "score": 0, "max_score": 15, "passed": False, "reason": f"Expected {expected_recommended}, got {violation.get('recommended_value')}"})

    # 写入结果
    write_score(workspace, score, details, max_score)

def write_score(workspace, score, details, max_score):
    result = {
        "total_score": min(score, max_score),
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
