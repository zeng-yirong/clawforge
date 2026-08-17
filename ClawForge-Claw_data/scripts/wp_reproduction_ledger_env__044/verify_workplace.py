import os
import sys
import json

workspace = sys.argv[1] if len(sys.argv) > 1 else "."
details = []
total_score = 0

# 1. 检查 archive 目录存在 (10分)
archive_dir = os.path.join(workspace, "archive")
dir_exists = os.path.isdir(archive_dir)
if dir_exists:
    total_score += 10
    details.append({
        "item": "archive directory exists",
        "score": 10, "max_score": 10, "passed": True,
        "reason": "archive/ directory found"
    })
else:
    details.append({
        "item": "archive directory exists",
        "score": 0, "max_score": 10, "passed": False,
        "reason": "archive/ directory not found"
    })

# 2. 检查目标文件存在 (最多10分，但先判存在，后面再判内容)
target_file = os.path.join(archive_dir, "reproduction_ledger_summary.json")
file_exists = os.path.isfile(target_file)
if file_exists:
    total_score += 10
    details.append({
        "item": "reproduction_ledger_summary.json file exists",
        "score": 10, "max_score": 10, "passed": True,
        "reason": "File found at archive/reproduction_ledger_summary.json"
    })
else:
    details.append({
        "item": "reproduction_ledger_summary.json file exists",
        "score": 0, "max_score": 10, "passed": False,
        "reason": "File not found"
    })
    # 如果文件不存在，后续无法继续，直接输出结果
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": details}, f)
    sys.exit(0)

# 3. 文件内容解析 (10分)
try:
    with open(target_file, "r") as f:
        data = json.load(f)
    total_score += 10
    details.append({
        "item": "file is valid JSON",
        "score": 10, "max_score": 10, "passed": True,
        "reason": "Successfully parsed JSON"
    })
except (json.JSONDecodeError, Exception) as e:
    total_score += 0
    details.append({
        "item": "file is valid JSON",
        "score": 0, "max_score": 10, "passed": False,
        "reason": f"Invalid JSON: {str(e)}"
    })
    # 后续无法检查字段
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": details}, f)
    sys.exit(0)

# 4. 必含字段完整性 (30分, 每个字段10分, 共4个)
required_fields = ["doc_id", "title", "reproduction_steps", "result"]
field_score = 0
field_reasons = []
for field in required_fields:
    if field in data:
        field_score += 10
        field_reasons.append(f"{field} present")
    else:
        field_reasons.append(f"{field} missing")
total_score += field_score
details.append({
    "item": "required fields present",
    "score": field_score, "max_score": 40,
    "passed": field_score == 40,
    "reason": "; ".join(field_reasons)
})

# 5. 字段值精确匹配 (50分, 每个关键字段值10-15分不等)
value_score = 0
value_reasons = []

# doc_id 必须为 "LGR-2024-003"
if data.get("doc_id") == "LGR-2024-003":
    value_score += 10
    value_reasons.append("doc_id correct")
else:
    value_reasons.append(f"doc_id incorrect: got '{data.get('doc_id')}'")

# title 必须包含 "Failed Reproduction" 且 "V2.1"
title = data.get("title", "")
if "Failed Reproduction" in title and "V2.1" in title:
    value_score += 10
    value_reasons.append("title matches expected")
else:
    value_reasons.append(f"title mismatch: got '{title}'")

# reproduction_steps 必须是列表且长度 >= 3，且包含 "stress test" 和 "2GB"
steps = data.get("reproduction_steps", [])
if isinstance(steps, list) and len(steps) >= 3:
    step_text = " ".join(steps).lower()
    if "stress test" in step_text and "2gb" in step_text:
        value_score += 15
        value_reasons.append("reproduction_steps contain stress test and 2GB threshold")
    else:
        value_score += 5
        value_reasons.append("steps list present but missing key phrases")
else:
    value_reasons.append("reproduction_steps not a list or too short")

# result 必须包含 "2GB" 和 "OOM" (不区分大小写)
result = data.get("result", "")
if "2gb" in result.lower() and "oom" in result.lower():
    value_score += 15
    value_reasons.append("result contains 2GB and OOM")
else:
    value_reasons.append(f"result mismatch: got '{result}'")

total_score += value_score
details.append({
    "item": "field values match ground truth",
    "score": value_score, "max_score": 50,
    "passed": value_score == 50,
    "reason": "; ".join(value_reasons)
})

# 总分
total_score = min(total_score, 100)  # 防止溢出
final_result = {
    "total_score": total_score,
    "details": details
}
with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
    json.dump(final_result, f, indent=2)
