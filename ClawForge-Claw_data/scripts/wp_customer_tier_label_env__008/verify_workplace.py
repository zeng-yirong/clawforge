import json
import sys
import os

workspace = sys.argv[1] if len(sys.argv) > 1 else "."
score = 0
details = []

# 1. 检查目标文件是否存在 (10 points)
target_path = os.path.join(workspace, "data/updated_labels.json")
if not os.path.exists(target_path):
    details.append({"item": "file existence", "score": 0, "max_score": 10, "passed": False, "reason": "File data/updated_labels.json not found"})
else:
    details.append({"item": "file existence", "score": 10, "max_score": 10, "passed": True, "reason": "File exists"})

# 2. 检查 JSON 合法且为列表 (10 points)
file_ok = False
data = None
if os.path.exists(target_path):
    try:
        with open(target_path) as f:
            data = json.load(f)
        if not isinstance(data, list):
            details.append({"item": "json format", "score": 0, "max_score": 10, "passed": False, "reason": "JSON is not a list"})
        else:
            details.append({"item": "json format", "score": 10, "max_score": 10, "passed": True, "reason": "Valid JSON list"})
            file_ok = True
    except Exception as e:
        details.append({"item": "json format", "score": 0, "max_score": 10, "passed": False, "reason": f"Invalid JSON: {e}"})

# 3. 检查每条记录包含 customer_id 和 label (10 points)
if file_ok:
    required_keys = {'customer_id', 'label'}
    all_have_keys = True
    for i, rec in enumerate(data):
        if not isinstance(rec, dict):
            all_have_keys = False
            break
        if not required_keys.issubset(rec.keys()):
            all_have_keys = False
            break
    if all_have_keys:
        details.append({"item": "field structure", "score": 10, "max_score": 10, "passed": True, "reason": "All records have customer_id and label"})
    else:
        details.append({"item": "field structure", "score": 0, "max_score": 10, "passed": False, "reason": "Some records missing required fields"})

# 4. 检查标签正确性 (50 points, 每个客户10分)
expected = {
    "C001": "VIP",
    "C002": "High",
    "C003": "Standard",
    "C004": "High",
    "C005": "Churned"
}
if file_ok and all_have_keys:
    correct = 0
    actual_ids = set()
    for rec in data:
        cid = rec.get('customer_id')
        label = rec.get('label')
        if cid in expected and expected[cid] == label:
            correct += 1
        actual_ids.add(cid)
    expected_ids = set(expected.keys())
    missing = expected_ids - actual_ids
    extra = actual_ids - expected_ids
    reason_parts = []
    if correct > 0:
        reason_parts.append(f"correct: {correct}/{len(expected)}")
    if missing:
        reason_parts.append(f"missing: {sorted(missing)}")
    if extra:
        reason_parts.append(f"extra: {sorted(extra)}")
    reason = "; ".join(reason_parts) if reason_parts else "all correct"
    passed = (correct == len(expected) and len(extra) == 0)
    item_score = 50 if passed else correct * 10
    details.append({"item": "correct labels", "score": item_score, "max_score": 50, "passed": passed, "reason": reason})
else:
    details.append({"item": "correct labels", "score": 0, "max_score": 50, "passed": False, "reason": "Could not evaluate due to prior failures"})

# 计算总分
total_score = sum(d['score'] for d in details)
result = {
    "total_score": total_score,
    "details": details
}

output_path = os.path.join(workspace, "workplace_score.json")
with open(output_path, "w") as f:
    json.dump(result, f, indent=2)

print(f"Total score: {total_score}")
