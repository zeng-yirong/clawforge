import os
import sys
import json

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

def load_json(rel_path):
    full = os.path.join(workspace, rel_path)
    if not os.path.isfile(full):
        return None
    with open(full, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return None

details = []
total_score = 0

# 1. ops/ 目录存在
ops_dir = os.path.join(workspace, "ops")
if os.path.isdir(ops_dir):
    details.append({"item": "ops/ directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "ops/ found"})
    total_score += 10
else:
    details.append({"item": "ops/ directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "ops/ not found"})

# 2. ops/signal_trace.json 存在
trace_path = os.path.join(workspace, "ops", "signal_trace.json")
if os.path.isfile(trace_path):
    details.append({"item": "ops/signal_trace.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "file found"})
    total_score += 10
else:
    details.append({"item": "ops/signal_trace.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "file not found"})
    # 无法继续，直接写结果
    result = {"total_score": total_score, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    sys.exit(0)

# 3. JSON 合法
data = load_json("ops/signal_trace.json")
if data is not None:
    details.append({"item": "valid JSON", "score": 10, "max_score": 10, "passed": True, "reason": "JSON parsed successfully"})
    total_score += 10
else:
    details.append({"item": "valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": "invalid JSON or unreadable"})
    result = {"total_score": total_score, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    sys.exit(0)

# 4. 根元素是列表
if isinstance(data, list):
    details.append({"item": "root element is list", "score": 5, "max_score": 5, "passed": True, "reason": "root is list"})
    total_score += 5
else:
    details.append({"item": "root element is list", "score": 0, "max_score": 5, "passed": False, "reason": f"root is {type(data).__name__}"})

# 5. 所有条目包含 type, id, clue
all_have_fields = True
for i, entry in enumerate(data):
    if not isinstance(entry, dict):
        all_have_fields = False
        break
    if not all(k in entry for k in ("type", "id", "clue")):
        all_have_fields = False
        break
if all_have_fields:
    details.append({"item": "all entries have type, id, clue", "score": 5, "max_score": 5, "passed": True, "reason": "fields present"})
    total_score += 5
else:
    details.append({"item": "all entries have type, id, clue", "score": 0, "max_score": 5, "passed": False, "reason": "missing fields"})

# 6. type 值有效
valid_types = {"report", "presentation", "media_sample"}
types_ok = all(entry.get("type") in valid_types for entry in data if isinstance(entry, dict))
if types_ok:
    details.append({"item": "type values are valid", "score": 5, "max_score": 5, "passed": True, "reason": "all types valid"})
    total_score += 5
else:
    details.append({"item": "type values are valid", "score": 0, "max_score": 5, "passed": False, "reason": "invalid type found"})

# 7. 无重复 ID
ids_seen = set()
no_dupes = True
for entry in data:
    if isinstance(entry, dict):
        key = (entry.get("type"), entry.get("id"))
        if key in ids_seen:
            no_dupes = False
            break
        ids_seen.add(key)
if no_dupes:
    details.append({"item": "no duplicate (type, id) combinations", "score": 5, "max_score": 5, "passed": True, "reason": "no duplicates"})
    total_score += 5
else:
    details.append({"item": "no duplicate (type, id) combinations", "score": 0, "max_score": 5, "passed": False, "reason": "duplicate found"})

# 8. 长度正确（预期 4）
expected_count = 4
if len(data) == expected_count:
    details.append({"item": f"entry count = {expected_count}", "score": 20, "max_score": 20, "passed": True, "reason": f"found {expected_count} entries"})
    total_score += 20
else:
    details.append({"item": f"entry count = {expected_count}", "score": 0, "max_score": 20, "passed": False, "reason": f"found {len(data)} entries"})

# 9. 逐个验证预期文档（共 4 个，各 5 分）
expected = {
    ("report", "RPT-001"): "This report covers deployment of HelioSync Edge Inference Fabric across manufacturing sites.",
    ("report", "RPT-003"): "Analysis of HelioSync Edge Inference Fabric in robotics.",
    ("presentation", "PRES-001"): "Live demo deck for HelioSync Edge Inference Fabric.",
    ("media_sample", "MED-001"): "Discussion on HelioSync Edge Inference Fabric with industry experts."
}
for (typ, eid), expected_clue in expected.items():
    matched = None
    for entry in data:
        if isinstance(entry, dict) and entry.get("type") == typ and entry.get("id") == eid:
            matched = entry
            break
    if matched is None:
        details.append({"item": f"document {typ} {eid} present", "score": 0, "max_score": 5, "passed": False, "reason": "missing"})
    elif matched.get("clue") == expected_clue:
        details.append({"item": f"document {typ} {eid} present", "score": 5, "max_score": 5, "passed": True, "reason": "correct id and clue"})
        total_score += 5
    else:
        details.append({"item": f"document {typ} {eid} present", "score": 2, "max_score": 5, "passed": False, "reason": f"clue mismatch, got: {matched.get('clue')[:50]!r}"})

# 写入结果
result = {"total_score": total_score, "details": details}
with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
    json.dump(result, f, indent=2)
print(json.dumps(result, indent=2))
