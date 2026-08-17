import json
import os
import sys

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

def read_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def check_path_exists(*parts):
    full = os.path.join(workspace, *parts)
    return os.path.exists(full)

score_details = []
total_score = 0

# 1. 必读目录存在 (10 points)
dirs_ok = all(
    check_path_exists(d) for d in ["reports", "presentations", "media_samples"]
)
score_details.append({
    "item": "Required subdirectories exist",
    "score": 10 if dirs_ok else 0,
    "max_score": 10,
    "passed": dirs_ok,
    "reason": "reports/, presentations/, media_samples/ all present" if dirs_ok else "Missing one or more required directories"
})
if dirs_ok:
    total_score += 10

# 2. 结果文件 clue_list.json 存在 (5 points)
clue_path = os.path.join(workspace, "clue_list.json")
clue_exists = os.path.exists(clue_path)
score_details.append({
    "item": "clue_list.json exists",
    "score": 5 if clue_exists else 0,
    "max_score": 5,
    "passed": clue_exists,
    "reason": "Found clue_list.json" if clue_exists else "clue_list.json not found"
})
if clue_exists:
    total_score += 5
else:
    # 无法继续检查，输出当前分数
    final_score = min(total_score, 100)
    output = {"total_score": final_score, "details": score_details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(output, f, indent=2)
    sys.exit(0)

# 3. JSON 格式合法 (5 points)
try:
    clues = read_json(clue_path)
    score_details.append({
        "item": "clue_list.json is valid JSON",
        "score": 5,
        "max_score": 5,
        "passed": True,
        "reason": "Parsed successfully"
    })
    total_score += 5
except Exception as e:
    score_details.append({
        "item": "clue_list.json is valid JSON",
        "score": 0,
        "max_score": 5,
        "passed": False,
        "reason": f"JSON parse error: {e}"
    })
    total_score += 0
    # 无法进一步检查
    final_score = min(total_score, 100)
    output = {"total_score": final_score, "details": score_details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(output, f, indent=2)
    sys.exit(0)

# 4. 线索列表应为数组 (5 points)
if isinstance(clues, list):
    score_details.append({
        "item": "clue_list.json root is a list",
        "score": 5,
        "max_score": 5,
        "passed": True,
        "reason": "Root element is list"
    })
    total_score += 5
else:
    score_details.append({
        "item": "clue_list.json root is a list",
        "score": 0,
        "max_score": 5,
        "passed": False,
        "reason": f"Root is {type(clues).__name__}, expected list"
    })

# 5. 每个条目包含 id 和 summary 字段 (10 points)
field_ok = all(isinstance(item, dict) and "id" in item and "summary" in item for item in clues)
field_bad = [i for i, item in enumerate(clues) if not (isinstance(item, dict) and "id" in item and "summary" in item)]
score_details.append({
    "item": "Each entry has 'id' and 'summary' fields",
    "score": 10 if field_ok else 0,
    "max_score": 10,
    "passed": field_ok,
    "reason": "All entries correct" if field_ok else f"Entries missing fields: indices {field_bad}"
})
if field_ok:
    total_score += 10

# 6. 正确的文档数量 (20 points)
# 预期的正确文档：来自 reports: RPT-2026-001, RPT-2026-004; presentations: PRES-2026-101; media_samples: MEDIA-2026-201, MEDIA-2026-203
expected_ids = {"RPT-2026-001", "RPT-2026-004", "PRES-2026-101", "MEDIA-2026-201", "MEDIA-2026-203"}
actual_ids = {item["id"] for item in clues if isinstance(item, dict) and "id" in item}

correct_ids = expected_ids.intersection(actual_ids)
extra_ids = actual_ids - expected_ids
missing_ids = expected_ids - actual_ids

count_correct = len(correct_ids)
count_expected = len(expected_ids)
if count_correct == count_expected and len(extra_ids) == 0:
    score_details.append({
        "item": "Correct documents identified (no misses, no extras)",
        "score": 20,
        "max_score": 20,
        "passed": True,
        "reason": "All 5 expected IDs present, no extra IDs"
    })
    total_score += 20
else:
    deduction = 0
    if missing_ids:
        deduction += len(missing_ids) * 4
    if extra_ids:
        deduction += len(extra_ids) * 4
    score = max(0, 20 - deduction)
    score_details.append({
        "item": "Correct documents identified (no misses, no extras)",
        "score": score,
        "max_score": 20,
        "passed": False,
        "reason": f"Missing: {missing_ids}, Extra: {extra_ids}"
    })
    total_score += score

# 7. 摘要内容正确性 (30 points)
# 加载原始数据以验证 summary 字段
loaded_docs = {}
# reports
try:
    rpt_data = read_json(os.path.join(workspace, "reports", "reports.json"))
    for r in rpt_data.get("reports", []):
        loaded_docs[r["report_id"]] = r["summary"]
except:
    pass
# presentations
try:
    pres_data = read_json(os.path.join(workspace, "presentations", "presentations.json"))
    for p in pres_data.get("presentations", []):
        loaded_docs[p["presentation_id"]] = p["summary"]
except:
    pass
# media_samples
try:
    med_data = read_json(os.path.join(workspace, "media_samples", "media_samples.json"))
    for m in med_data.get("media_samples", []):
        loaded_docs[m["sample_id"]] = m["summary"]
except:
    pass

summary_errors = 0
for item in clues:
    if not isinstance(item, dict):
        summary_errors += 1
        continue
    doc_id = item.get("id")
    expected_summary = loaded_docs.get(doc_id)
    if expected_summary is None:
        # 文档未在原数据中（可能是多余的）
        summary_errors += 1
    else:
        if item.get("summary") != expected_summary:
            summary_errors += 1

max_summary_score = 30
summary_score = max(0, max_summary_score - summary_errors * 6)
score_details.append({
    "item": "Summary field matches original source",
    "score": summary_score,
    "max_score": max_summary_score,
    "passed": summary_errors == 0,
    "reason": f"{summary_errors} entry/entries have incorrect summary" if summary_errors else "All summaries correct"
})
total_score += summary_score

# 8. 没有多余节点或字段 (10 points)
# 检查每个条目是否只有 id 和 summary
extra_field_count = 0
for item in clues:
    if isinstance(item, dict):
        keys = set(item.keys())
        if keys != {"id", "summary"}:
            extra_field_count += 1
score_details.append({
    "item": "No extra fields beyond id and summary",
    "score": 10 if extra_field_count == 0 else 0,
    "max_score": 10,
    "passed": extra_field_count == 0,
    "reason": "All entries have exactly id and summary" if extra_field_count == 0 else f"{extra_field_count} entries have extra fields"
})
if extra_field_count == 0:
    total_score += 10

# 9. 结果文件没有其他意外数据 (5 points)
# 检查 clue_list.json 根目录无额外属性（已经是 list）
score_details.append({
    "item": "clue_list.json contains only the expected list (no extraneous metadata)",
    "score": 5,
    "max_score": 5,
    "passed": True,
    "reason": "Root is a list, no extra properties"
})
total_score += 5

final_score = min(total_score, 100)
output = {"total_score": final_score, "details": score_details}
with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
    json.dump(output, f, indent=2)

print(f"Verification complete. Total score: {final_score}/100")
