import sys
import json
import os

workspace = sys.argv[1] if len(sys.argv) > 1 else "."
score = 0
details = []

# ---------- 检查 ops 目录 ----------
ops_path = os.path.join(workspace, "ops")
if os.path.isdir(ops_path):
    details.append({"item": "ops directory exists", "score": 5, "max_score": 5, "passed": True, "reason": "ops/ directory found"})
    score += 5
else:
    details.append({"item": "ops directory exists", "score": 0, "max_score": 5, "passed": False, "reason": "ops/ directory not found"})

# ---------- 检查 action.json ----------
action_path = os.path.join(ops_path, "action.json") if os.path.isdir(ops_path) else None
file_exists = (action_path is not None and os.path.isfile(action_path))

if file_exists:
    details.append({"item": "action.json exists", "score": 5, "max_score": 5, "passed": True, "reason": "action.json found"})
    score += 5
else:
    details.append({"item": "action.json exists", "score": 0, "max_score": 5, "passed": False, "reason": "action.json not found"})

# ---------- 解析并验证内容 ----------
data = None
if file_exists:
    try:
        with open(action_path, "r") as f:
            data = json.load(f)
        details.append({"item": "JSON is valid", "score": 10, "max_score": 10, "passed": True, "reason": "Valid JSON"})
        score += 10
    except Exception as e:
        details.append({"item": "JSON is valid", "score": 0, "max_score": 10, "passed": False, "reason": f"Invalid JSON: {e}"})
else:
    details.append({"item": "JSON is valid", "score": 0, "max_score": 10, "passed": False, "reason": "action.json missing"})

# 字段检查（无论文件是否存在，都会添加分数项）
if not file_exists:
    # 文件不存在时添加所有剩余项为失败
    for field in [("Contains 'device_id' field", 10), ("device_id correct", 30),
                  ("Contains 'action' field", 10), ("action correct", 30)]:
        details.append({"item": field[0], "score": 0, "max_score": field[1], "passed": False, "reason": "action.json missing"})
else:
    # 文件存在且解析成功
    if data is None:
        # 解析失败，添加字段检查失败
        for field in [("Contains 'device_id' field", 10), ("device_id correct", 30),
                      ("Contains 'action' field", 10), ("action correct", 30)]:
            details.append({"item": field[0], "score": 0, "max_score": field[1], "passed": False, "reason": "Invalid JSON, cannot evaluate"})
    else:
        # 检查 device_id
        if isinstance(data, dict) and "device_id" in data:
            details.append({"item": "Contains 'device_id' field", "score": 10, "max_score": 10, "passed": True, "reason": "field present"})
            score += 10
            if data["device_id"] == "ac-001":
                details.append({"item": "device_id correct", "score": 30, "max_score": 30, "passed": True, "reason": "device_id is ac-001"})
                score += 30
            else:
                details.append({"item": "device_id correct", "score": 0, "max_score": 30, "passed": False, "reason": f"got '{data['device_id']}', expected 'ac-001'"})
        else:
            details.append({"item": "Contains 'device_id' field", "score": 0, "max_score": 10, "passed": False, "reason": "missing or not a dict"})
            details.append({"item": "device_id correct", "score": 0, "max_score": 30, "passed": False, "reason": "cannot check due to missing field"})

        # 检查 action
        if isinstance(data, dict) and "action" in data:
            details.append({"item": "Contains 'action' field", "score": 10, "max_score": 10, "passed": True, "reason": "field present"})
            score += 10
            if data["action"] == "turn_on":
                details.append({"item": "action correct", "score": 30, "max_score": 30, "passed": True, "reason": "action is turn_on"})
                score += 30
            else:
                details.append({"item": "action correct", "score": 0, "max_score": 30, "passed": False, "reason": f"got '{data['action']}', expected 'turn_on'"})
        else:
            details.append({"item": "Contains 'action' field", "score": 0, "max_score": 10, "passed": False, "reason": "missing or not a dict"})
            details.append({"item": "action correct", "score": 0, "max_score": 30, "passed": False, "reason": "cannot check due to missing field"})

# 写入最终评分
final_score = min(score, 100)
result = {"total_score": final_score, "details": details}
with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
    json.dump(result, f, indent=2)
print(f"Total score: {final_score}/100")
