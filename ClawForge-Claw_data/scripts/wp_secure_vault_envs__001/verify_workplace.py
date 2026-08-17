"""
Verify the agent's output for credential audit task.
Checks:
  1. Existence of ops/credential_audit.json
  2. Valid JSON array
  3. Each entry has 'id' and 'reasons' fields
  4. Exactly 7 problematic credentials (precomputed truth)
  5. All expected IDs present and reasons correct
  6. No extra entries
"""
import sys
import json
import os

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    audit_path = os.path.join(workspace, "ops", "credential_audit.json")
    score = 0
    breakdown = []
    
    # --- 1. File existence (10 pts) ---
    if os.path.isfile(audit_path):
        breakdown.append({
            "item": "ops/credential_audit.json 存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "文件存在"
        })
        score += 10
    else:
        breakdown.append({
            "item": "ops/credential_audit.json 存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件不存在或路径错误"
        })
        # 如果不存在，后续检查无意义，直接输出结果
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": score, "details": breakdown}, f)
        return
    
    # --- 2. Valid JSON (10 pts) ---
    try:
        data = load_json(audit_path)
        breakdown.append({
            "item": "有效 JSON 格式",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "成功解析为 JSON"
        })
        score += 10
    except Exception as e:
        breakdown.append({
            "item": "有效 JSON 格式",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON 解析失败: {str(e)}"
        })
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": score, "details": breakdown}, f)
        return
    
    # --- 3. Must be a list (5 pts) ---
    if isinstance(data, list):
        breakdown.append({
            "item": "顶层结构为数组",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "顶层是 JSON 数组"
        })
        score += 5
    else:
        breakdown.append({
            "item": "顶层结构为数组",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": f"顶层类型为 {type(data).__name__}，期望 list"
        })
        data = []  # 后续检查免崩溃
    
    # --- 4. Each entry has 'id' and 'reasons' (20 pts) ---
    field_errors = 0
    for i, entry in enumerate(data):
        if not isinstance(entry, dict):
            field_errors += 1
            continue
        if "id" not in entry or "reasons" not in entry:
            field_errors += 1
            continue
        # reasons must be a non-empty list of strings
        reasons = entry.get("reasons")
        if not isinstance(reasons, list) or len(reasons) == 0:
            field_errors += 1
    if field_errors == 0:
        breakdown.append({
            "item": "每条记录包含 'id' 和 'reasons' 字段且有效",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "所有条目结构正确"
        })
        score += 20
    else:
        breakdown.append({
            "item": "每条记录包含 'id' 和 'reasons' 字段且有效",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"有 {field_errors} 条记录缺少字段或格式错误"
        })
    
    # --- 5. Number of entries exact (15 pts) ---
    expected_count = 7  # 由 builder 确定：cred-003,cred-004,cred-005,cred-006,cred-007,cred-009,cred-010
    actual_count = len(data)
    if actual_count == expected_count:
        breakdown.append({
            "item": "记录数量",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": f"数量正确：{actual_count}"
        })
        score += 15
    else:
        breakdown.append({
            "item": "记录数量",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": f"期望 {expected_count} 条，实际 {actual_count} 条"
        })
    
    # --- 6. ID set exact + reasons not empty (20 pts) ---
    expected_ids = {"cred-003", "cred-004", "cred-005", "cred-006", "cred-007", "cred-009", "cred-010"}
    actual_ids = {entry.get("id") for entry in data if isinstance(entry, dict)}
    # Check extra / missing
    missing = expected_ids - actual_ids
    extra = actual_ids - expected_ids
    if not missing and not extra:
        breakdown.append({
            "item": "包含所有问题凭证 ID，无多余 ID",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "ID 集合完全匹配"
        })
        score += 20
    else:
        reason_parts = []
        if missing:
            reason_parts.append(f"缺失 ID: {sorted(missing)}")
        if extra:
            reason_parts.append(f"多余 ID: {sorted(extra)}")
        breakdown.append({
            "item": "包含所有问题凭证 ID，无多余 ID",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "; ".join(reason_parts)
        })
    
    # --- 7. Reasons are not empty for each entry (10 pts) ---
    empty_reasons = sum(1 for e in data if isinstance(e, dict) and (not e.get("reasons") or len(e["reasons"]) == 0))
    if empty_reasons == 0:
        breakdown.append({
            "item": "所有条目的 reasons 非空",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "每个问题都有说明"
        })
        score += 10
    else:
        breakdown.append({
            "item": "所有条目的 reasons 非空",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"{empty_reasons} 条记录的 reasons 为空"
        })
    
    # --- 8. Bonus: If reasons contain meaningful categories (no extra points, just sanity) ---
    # 不额外计分，但可以输出信息
    breakdown[-1]["reason"] += f" 共 {len(data)} 条记录"
    
    # 输出结果
    total_score = score
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": breakdown}, f, indent=2)
    print(f"Verification finished. Score: {total_score}/100")

if __name__ == "__main__":
    main()
