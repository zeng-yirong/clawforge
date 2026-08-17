import os
import sys
import json

workspace = sys.argv[1] if len(sys.argv) > 1 else "."
result = {
    "total_score": 0,
    "details": []
}
score = 0
max_total = 100

# 1. 目录结构检查 (10分)
target_dir = os.path.join(workspace, "ops")
detail = {"item": "目录 ops 存在", "score": 0, "max_score": 10, "passed": False, "reason": ""}
if os.path.isdir(target_dir):
    detail["score"] = 10
    detail["passed"] = True
    detail["reason"] = "ops 目录已创建"
else:
    detail["reason"] = "未找到 ops 目录"
score += detail["score"]
result["details"].append(detail)

# 2. 文件存在性检查 (10分)
target_file = os.path.join(target_dir, "kill_target.json")
detail = {"item": "文件 ops/kill_target.json 存在", "score": 0, "max_score": 10, "passed": False, "reason": ""}
if os.path.isfile(target_file):
    detail["score"] = 10
    detail["passed"] = True
    detail["reason"] = "文件存在"
else:
    detail["reason"] = f"未找到文件 {target_file}"
score += detail["score"]
result["details"].append(detail)

# 3. JSON 合法性 (10分)
detail = {"item": "kill_target.json 是合法JSON", "score": 0, "max_score": 10, "passed": False, "reason": ""}
if os.path.isfile(target_file):
    try:
        with open(target_file, "r") as f:
            data = json.load(f)
        detail["score"] = 10
        detail["passed"] = True
        detail["reason"] = "JSON 解析成功"
    except json.JSONDecodeError as e:
        detail["reason"] = f"JSON 解析失败: {e}"
else:
    detail["reason"] = "文件不存在，跳过解析"
score += detail["score"]
result["details"].append(detail)

# 4. 字段 "transaction_id" 存在且值为正确事务ID (60分)
detail = {"item": "字段 transaction_id 值正确 (TXN-20250315-001)", "score": 0, "max_score": 60, "passed": False, "reason": ""}
if os.path.isfile(target_file) and 'data' in locals():
    if isinstance(data, dict) and "transaction_id" in data:
        val = data["transaction_id"]
        if val == "TXN-20250315-001":
            detail["score"] = 60
            detail["passed"] = True
            detail["reason"] = f"值为 {val}"
        else:
            detail["reason"] = f"字段 transaction_id 值为 '{val}'，期望 'TXN-20250315-001'"
    else:
        detail["reason"] = "JSON 不是字典或缺少 transaction_id 字段"
else:
    detail["reason"] = "文件不存在或未解析"
score += detail["score"]
result["details"].append(detail)

# 5. 无多余字段 (10分)
detail = {"item": "kill_target.json 无多余字段", "score": 0, "max_score": 10, "passed": False, "reason": ""}
if os.path.isfile(target_file) and 'data' in locals() and isinstance(data, dict):
    allowed = {"transaction_id"}
    extra = set(data.keys()) - allowed
    if not extra:
        detail["score"] = 10
        detail["passed"] = True
        detail["reason"] = "只有 transaction_id 字段"
    else:
        detail["reason"] = f"多余字段: {extra}"
else:
    detail["reason"] = "条件不足，跳过"
score += detail["score"]
result["details"].append(detail)

result["total_score"] = score
# 写入评分文件
score_file = os.path.join(workspace, "workplace_score.json")
with open(score_file, "w") as f:
    json.dump(result, f, indent=2)
print(json.dumps(result, indent=2))
