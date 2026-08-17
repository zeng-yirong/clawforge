import sys
import os
import json

workspace = sys.argv[1] if len(sys.argv) > 1 else "."
target_file = os.path.join(workspace, "contact_info.json")

score = 0
max_score = 100
details = []

# 1. 文件存在
if os.path.isfile(target_file):
    details.append({"item": "contact_info.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "File found"})
    score += 10
else:
    details.append({"item": "contact_info.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "File not found"})
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": 0, "details": details}, f)
    sys.exit(0)

# 2. JSON合法性
try:
    with open(target_file, "r") as f:
        data = json.load(f)
    details.append({"item": "JSON format valid", "score": 10, "max_score": 10, "passed": True, "reason": "Valid JSON"})
    score += 10
except Exception as e:
    details.append({"item": "JSON format valid", "score": 0, "max_score": 10, "passed": False, "reason": str(e)})
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": score, "details": details}, f)
    sys.exit(0)

# 3. 顶层是字典
if isinstance(data, dict):
    details.append({"item": "Top-level is a dict", "score": 10, "max_score": 10, "passed": True, "reason": "Is dict"})
    score += 10
else:
    details.append({"item": "Top-level is a dict", "score": 0, "max_score": 10, "passed": False, "reason": f"Type is {type(data).__name__}"})
    data = {}

# 4. 包含所有必需字段
expected_fields = {"contact_id", "name", "email", "role", "team", "priority"}
actual_fields = set(data.keys())
missing = expected_fields - actual_fields
extra = actual_fields - expected_fields

if not missing:
    details.append({"item": "All required fields present", "score": 20, "max_score": 20, "passed": True, "reason": "All fields found"})
    score += 20
else:
    details.append({"item": "All required fields present", "score": 0, "max_score": 20, "passed": False, "reason": f"Missing fields: {missing}"})

# 5. 无多余字段
if not extra:
    details.append({"item": "No extra fields", "score": 10, "max_score": 10, "passed": True, "reason": "No extra fields"})
    score += 10
else:
    details.append({"item": "No extra fields", "score": 0, "max_score": 10, "passed": False, "reason": f"Extra fields: {extra}"})

# 6. 字段值精确匹配
expected_values = {
    "contact_id": "alice_001",
    "name": "Alice Client",
    "email": "alice@clientcorp.com",
    "role": "Client",
    "team": "External",
    "priority": "high"
}
field_correct = 0
field_issues = []
for f in expected_fields:
    if f in data and data[f] == expected_values[f]:
        field_correct += 1
    else:
        field_issues.append(f"{f}: got {data.get(f)!r}, expected {expected_values[f]!r}")

if field_correct == len(expected_fields):
    details.append({"item": "Field values correct", "score": 40, "max_score": 40, "passed": True, "reason": "All values match exactly"})
    score += 40
else:
    details.append({"item": "Field values correct", "score": 0, "max_score": 40, "passed": False, "reason": "; ".join(field_issues)})

# 写出最终评分
with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
    json.dump({"total_score": score, "details": details}, f)
