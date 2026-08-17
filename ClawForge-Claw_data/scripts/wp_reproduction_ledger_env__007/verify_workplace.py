import sys
import json
import os

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

score = 0
details = []
max_total = 100

# 1. File existence
target_path = os.path.join(workspace, "ops", "reproduction_ledger.json")
if os.path.isfile(target_path):
    details.append({"item": "File existence", "score": 10, "max_score": 10, "passed": True, "reason": "ops/reproduction_ledger.json exists"})
    score += 10
else:
    details.append({"item": "File existence", "score": 0, "max_score": 10, "passed": False, "reason": "File not found"})
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": score, "details": details}, f, indent=2)
    sys.exit(0)

# 2. Parse JSON
try:
    with open(target_path, "r") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        details.append({"item": "Valid JSON object", "score": 0, "max_score": 10, "passed": False, "reason": "Root is not a dict"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": score, "details": details}, f, indent=2)
        sys.exit(0)
    details.append({"item": "Valid JSON object", "score": 10, "max_score": 10, "passed": True, "reason": "Root is a dict"})
    score += 10
except Exception as e:
    details.append({"item": "Valid JSON object", "score": 0, "max_score": 10, "passed": False, "reason": f"Failed to parse: {e}"})
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": score, "details": details}, f, indent=2)
    sys.exit(0)

# 3. Required fields
required_fields = ["doc_id", "project_id", "replication_time", "status", "replication_successful", "applied_version", "steps", "result"]
missing = [f for f in required_fields if f not in data]
if missing:
    details.append({"item": "Required fields", "score": 0, "max_score": 20, "passed": False, "reason": f"Missing fields: {missing}"})
else:
    details.append({"item": "Required fields", "score": 20, "max_score": 20, "passed": True, "reason": "All required fields present"})
    score += 20

# 4. Core value matching (only if fields present)
expected = {
    "doc_id": "doc_repro_alpha",
    "project_id": "proj_alpha",
    "replication_time": "2025-03-03T10:00:00",
    "status": "completed",
    "replication_successful": True,
    "applied_version": "1.1.0",
    "steps": ["environment setup", "dependency install", "patch apply", "run test"],
    "result": "Bug reproduced on v1.1.0"
}
core_score = 0
core_max = 60
field_weights = {"doc_id": 5, "project_id": 10, "replication_time": 10, "status": 5, "replication_successful": 10, "applied_version": 10, "steps": 5, "result": 5}
for field, expected_val in expected.items():
    if field not in data:
        continue
    actual = data[field]
    passed = (actual == expected_val)
    if passed:
        core_score += field_weights[field]
        details.append({"item": f"Field '{field}' match", "score": field_weights[field], "max_score": field_weights[field], "passed": True, "reason": f"Value = {actual}"})
    else:
        details.append({"item": f"Field '{field}' match", "score": 0, "max_score": field_weights[field], "passed": False, "reason": f"Expected {expected_val}, got {actual}"})
score += core_score
details.append({"item": "Core value matching total", "score": core_score, "max_score": core_max, "passed": core_score == core_max, "reason": f"Scored {core_score}/{core_max}"})

total_score = score
details.append({"item": "Total score", "score": total_score, "max_score": max_total, "passed": total_score >= 80, "reason": f"Overall score {total_score}/{max_total}"})

with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
    json.dump({"total_score": total_score, "details": details}, f, indent=2)

print(f"Score: {total_score}/{max_total}")
