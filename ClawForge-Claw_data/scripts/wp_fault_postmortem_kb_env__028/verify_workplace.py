import os
import sys
import json

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

score_details = []
total_score = 0

def add_score(item, score, max_score, passed, reason):
    score_details.append({
        "item": item,
        "score": score,
        "max_score": max_score,
        "passed": passed,
        "reason": reason
    })
    return score

# 1. 检查 postmortem 目录是否存在 (10分)
path = os.path.join(workspace, "postmortem")
if os.path.isdir(path):
    total_score += add_score("postmortem 目录存在", 10, 10, True, "目录已创建")
else:
    total_score += add_score("postmortem 目录存在", 0, 10, False, "目录不存在")

# 2. 检查 postmortem/analysis.json 文件是否存在 (20分)
file_path = os.path.join(workspace, "postmortem", "analysis.json")
if not os.path.isfile(file_path):
    total_score += add_score("postmortem/analysis.json 文件存在", 0, 20, False, "文件不存在")
    # 后续检查跳过
    result = {"total_score": total_score, "details": score_details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    sys.exit(0)
else:
    total_score += add_score("postmortem/analysis.json 文件存在", 20, 20, True, "文件存在")

# 3. 解析 JSON 合法性 (10分)
try:
    with open(file_path, "r") as f:
        data = json.load(f)
    total_score += add_score("JSON 格式合法", 10, 10, True, "解析成功")
except Exception as e:
    total_score += add_score("JSON 格式合法", 0, 10, False, f"解析失败: {e}")
    result = {"total_score": total_score, "details": score_details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    sys.exit(0)

# 4. 检查必需字段 (25分, 每个字段5分)
required_fields = ["fault_id", "root_cause", "repair_plan", "reference_kb_title"]
field_score = 0
for field in required_fields:
    if field in data and data[field] is not None:
        field_score += 5
        add_score(f"字段 {field} 存在且非空", 5, 5, True, "字段存在")
    else:
        add_score(f"字段 {field} 存在且非空", 0, 5, False, f"字段缺失或为空")
total_score += field_score

# 5. 字段值精确匹配 (35分)
# 预期答案
expected = {
    "fault_id": "fault-001",
    "root_cause": "NullPointerException in AccountService.getAccountBalance",
    "repair_plan": "Root cause: NullPointerException in getAccountBalance due to missing null check. Repair: add null check before invoking method.",
    "reference_kb_title": "Known Issue: NullPointer fix"
}

value_score = 0
all_match = True
for field, expected_val in expected.items():
    actual = data.get(field)
    if actual == expected_val:
        value_score += 8.75  # 35/4
        add_score(f"字段 {field} 值正确", 8.75, 8.75, True, f"值匹配: {expected_val}")
    else:
        value_score += 0
        all_match = False
        add_score(f"字段 {field} 值正确", 0, 8.75, False, f"期望 '{expected_val}', 得到 '{actual}'")
total_score += int(round(value_score))  # 确保整数

# 写入结果
result = {"total_score": min(total_score, 100), "details": score_details}
with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
    json.dump(result, f, indent=2)

print(f"得分: {result['total_score']}/100")
