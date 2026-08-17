#!/usr/bin/env python3
"""
评分脚本：验证 agent 是否根据 prompt 生成了正确的故障事后分析报告。
总分 100，细项：
  - 目录结构 (10分)：ops/postmortems/ 是否存在
  - 文件存在 (10分)：ops/postmortems/F-20250321-001.json 存在
  - JSON 合法性 (10分)：可解析且为 dict
  - 根因匹配 (30分)：root_cause 字段值与预期完全一致
  - 修复计划匹配 (30分)：repair_plan 字段值与预期完全一致
  - 额外扣分：多余关键字段（如 repair_plan_hint）扣 5 分 / 个（最多扣 10 分）
  - 命名严格性 (10分)：文件名必须完全等于 F-20250321-001.json，否则文件存在项归零
"""

import sys
import json
import os

def get_expected_values(workspace):
    """从 builder 铺出的 fault_cases 中读取目标案例的根因和修复计划"""
    faults_path = os.path.join(workspace, "data/faults/fault_cases.json")
    with open(faults_path, 'r') as f:
        data = json.load(f)
    for case in data["fault_cases"]:
        if case["fault_id"] == "F-20250321-001":
            return case["root_cause_hint"], case["repair_plan_hint"]
    raise ValueError("Target fault case not found in fault_cases.json")

def verify(workspace):
    details = []
    total = 0
    max_total = 100

    # ---------- 1. 目录结构 (10) ----------
    dir_path = os.path.join(workspace, "ops", "postmortems")
    dir_exists = os.path.isdir(dir_path)
    details.append({
        "item": "ops/postmortems/ directory exists",
        "score": 10 if dir_exists else 0,
        "max_score": 10,
        "passed": dir_exists,
        "reason": "Directory found" if dir_exists else "Missing directory ops/postmortems/"
    })
    if dir_exists:
        total += 10

    # ---------- 2. 文件存在 (10) ----------
    target_filename = "F-20250321-001.json"
    file_path = os.path.join(dir_path, target_filename) if dir_exists else os.path.join(workspace, "ops", "postmortems", target_filename)
    file_exists = os.path.isfile(file_path)
    details.append({
        "item": f"ops/postmortems/{target_filename} exists",
        "score": 10 if file_exists else 0,
        "max_score": 10,
        "passed": file_exists,
        "reason": "File found" if file_exists else "File not found"
    })
    if file_exists:
        total += 10

    # 如果文件不存在，直接返回（后面项目得0分）
    if not file_exists:
        # 补充其他项目但给0分
        for item_name, max_s in [('JSON validity',10),('root_cause match',30),('repair_plan match',30),('No extra fields',10)]:
            details.append({
                "item": item_name,
                "score": 0,
                "max_score": max_s,
                "passed": False,
                "reason": "Target file missing"
            })
        result = {"total_score": total, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # ---------- 3. JSON 合法性 (10) ----------
    try:
        with open(file_path, 'r') as f:
            content = json.load(f)
        is_valid = isinstance(content, dict)
        reason = "Valid JSON object" if is_valid else "Not a JSON object"
    except Exception as e:
        is_valid = False
        reason = f"JSON parse error: {str(e)}"
    details.append({
        "item": "JSON validity",
        "score": 10 if is_valid else 0,
        "max_score": 10,
        "passed": is_valid,
        "reason": reason
    })
    if is_valid:
        total += 10

    # ---------- 4. 根因匹配 (30) ----------
    expected_root_cause, expected_repair_plan = get_expected_values(workspace)
    actual_root_cause = content.get("root_cause", "") if is_valid else ""
    root_cause_ok = (actual_root_cause == expected_root_cause)
    details.append({
        "item": "root_cause field matches expected",
        "score": 30 if root_cause_ok else 0,
        "max_score": 30,
        "passed": root_cause_ok,
        "reason": f"Expected '{expected_root_cause}', got '{actual_root_cause}'" if not root_cause_ok else "Match"
    })
    if root_cause_ok:
        total += 30

    # ---------- 5. 修复计划匹配 (30) ----------
    actual_repair_plan = content.get("repair_plan", "") if is_valid else ""
    repair_plan_ok = (actual_repair_plan == expected_repair_plan)
    details.append({
        "item": "repair_plan field matches expected",
        "score": 30 if repair_plan_ok else 0,
        "max_score": 30,
        "passed": repair_plan_ok,
        "reason": f"Expected '{expected_repair_plan}', got '{actual_repair_plan}'" if not repair_plan_ok else "Match"
    })
    if repair_plan_ok:
        total += 30

    # ---------- 6. 额外字段扣分（最多扣10分） ----------
    extra_penalty = 0
    if is_valid:
        # 定义允许的字段（不限制，但如果有类似 root_cause_hint 等提示性字段，会泄露业务，扣分）
        forbidden_prefixes = ["hint", "expected", "golden", "solution"]
        extra_fields = []
        for key in content.keys():
            for prefix in forbidden_prefixes:
                if key.lower().startswith(prefix):
                    extra_fields.append(key)
                    break
        # 每出现一个扣5分，最多扣10分
        penalty = min(len(extra_fields) * 5, 10)
        extra_penalty = -penalty
        if penalty > 0:
            reason = f"Found forbidden fields: {extra_fields}, penalty {penalty}"
        else:
            reason = "No forbidden fields"
    else:
        reason = "Skipped (JSON invalid)"
    details.append({
        "item": "No extra forbidden fields (root_cause_hint etc.)",
        "score": max(0, 0 + extra_penalty),  # 此项满分10，扣分后得分≥0
        "max_score": 10,
        "passed": is_valid and extra_penalty == 0,
        "reason": reason
    })
    # 扣分从总分中减去（但不在该项得分中体现负分，而是在总分中手动扣）
    # 为了清晰，我们直接调整 total 并在此项记录实际得分（0-10）
    actual_extra_score = max(0, 10 - abs(extra_penalty))
    details[-1]["score"] = actual_extra_score
    # 如果扣分了，total 需要反映扣分
    total -= abs(extra_penalty) if extra_penalty < 0 else 0
    # 保证总分不低于0
    total = max(total, 0)

    # ---------- 写入结果 ----------
    result = {"total_score": total, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    # 打印摘要
    print(f"Verification complete. Total score: {total}/100")

if __name__ == '__main__':
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
