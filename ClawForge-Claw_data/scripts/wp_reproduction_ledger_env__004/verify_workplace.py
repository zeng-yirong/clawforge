import sys
import os
import json

workspace = sys.argv[1] if len(sys.argv) > 1 else "."
details = []

def check(condition, item, max_score, reason=""):
    score = max_score if condition else 0
    details.append({
        "item": item,
        "score": score,
        "max_score": max_score,
        "passed": condition,
        "reason": reason if not condition else ""
    })
    return condition

# 1. 检查 knowledge_base 目录是否存在
kb_dir = os.path.join(workspace, "knowledge_base")
check(os.path.isdir(kb_dir), "knowledge_base directory exists", 10,
      "Directory knowledge_base/ not found")

# 2. 检查 reproduction_ledger.json 是否存在
ledger_path = os.path.join(kb_dir, "reproduction_ledger.json")
file_exists = check(os.path.isfile(ledger_path),
                    "reproduction_ledger.json file exists", 10,
                    "File knowledge_base/reproduction_ledger.json not found")

if not file_exists:
    # 如果文件不存在，后续检查直接跳过，总分为当前已得分
    total_score = sum(d["score"] for d in details)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2)
    print(f"Total: {total_score}/100")
    sys.exit(0)

# 3. 检查 JSON 合法性
try:
    with open(ledger_path, "r") as f:
        data = json.load(f)
    check(True, "JSON parseable", 10, "")
except json.JSONDecodeError as e:
    check(False, "JSON parseable", 10, f"Invalid JSON: {e}")
    total_score = sum(d["score"] for d in details)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2)
    print(f"Total: {total_score}/100")
    sys.exit(0)

# 4. 检查字段完整性
expected_fields = {"project_id", "author", "steps"}
actual_fields = set(data.keys())
check(actual_fields == expected_fields,
      "Fields are exactly project_id, author, steps", 10,
      f"Unexpected fields: {actual_fields - expected_fields}")

# 5. 检查 project_id
check(data.get("project_id") == "proj-042",
      "project_id is 'proj-042'", 10,
      f"Got project_id = {data.get('project_id')}")

# 6. 检查 author
check(data.get("author") == "Alice Zhang",
      "author is 'Alice Zhang'", 10,
      f"Got author = {data.get('author')}")

# 7. 检查 steps 是列表
steps = data.get("steps", [])
check(isinstance(steps, list),
      "steps is a list", 10,
      "steps is not a list")

if not isinstance(steps, list):
    total_score = sum(d["score"] for d in details)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2)
    print(f"Total: {total_score}/100")
    sys.exit(0)

# 8. 检查 steps 数量
check(len(steps) == 3,
      "steps has exactly 3 items", 10,
      f"steps length = {len(steps)}")

# 9. 检查 steps 内容（精确匹配，去除首尾空白）
expected_steps = [
    "Install package version 2.1.0",
    "Run command `example --flag`",
    'Observe output contains "error code 0xDEAD"'
]
actual_stripped = [s.strip() for s in steps]
expected_stripped = [s.strip() for s in expected_steps]
steps_match = actual_stripped == expected_stripped
check(steps_match,
      "steps content match exactly", 20,
      f"Expected {expected_stripped}, got {actual_stripped}")

# 总分计算
total_score = sum(d["score"] for d in details)

# 写入结果
result = {
    "total_score": total_score,
    "details": details
}
with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
    json.dump(result, f, indent=2)

print(f"Total: {total_score}/100")
