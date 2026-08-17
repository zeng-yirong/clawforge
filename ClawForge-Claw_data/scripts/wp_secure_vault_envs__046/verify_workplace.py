import sys
import json
import csv
import os
from datetime import datetime

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

def load_json(rel_path):
    full_path = os.path.join(workspace, rel_path)
    if not os.path.exists(full_path):
        return None
    with open(full_path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_csv(rel_path):
    full_path = os.path.join(workspace, rel_path)
    if not os.path.exists(full_path):
        return None
    with open(full_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)

def check_password_strength(password, policy):
    """Return True if password meets the policy, False otherwise."""
    if not password or len(password) < policy.get("min_length", 0):
        return False
    checks = []
    if policy.get("require_uppercase", False):
        checks.append(any(c.isupper() for c in password))
    if policy.get("require_lowercase", False):
        checks.append(any(c.islower() for c in password))
    if policy.get("require_digit", False):
        checks.append(any(c.isdigit() for c in password))
    if policy.get("require_special", False):
        special = policy.get("special_chars", "")
        checks.append(any(c in special for c in password))
    return all(checks)

def get_expected_result(schema, credentials, audit_log):
    # 构建类别映射
    cat_map = {c["category_id"]: c for c in schema["credential_categories"]}

    # 构建活跃凭证ID集合
    active_ids = set(row["credential_id"] for row in audit_log)

    # 按 username+platform 分组，保留最新的一个
    grouped = {}
    for cred in credentials:
        key = (cred["username"], cred["platform"])
        if key in grouped:
            existing = grouped[key]
            if cred["created_at"] > existing["created_at"]:
                grouped[key] = cred
        else:
            grouped[key] = cred

    valid_creds = []
    weak_ids = []
    ignored_count = 0
    total_active = len(active_ids)

    for (uname, plat), cred in grouped.items():
        cid = cred["id"]
        # 忽略不在审计日志中的
        if cid not in active_ids:
            ignored_count += 1
            continue
        # 忽略空密码
        if not cred.get("password"):
            ignored_count += 1
            continue
        cat_id = cred.get("category_id")
        if cat_id not in cat_map:
            ignored_count += 1
            continue
        policy = cat_map[cat_id]["password_policy"]
        strong = check_password_strength(cred["password"], policy)
        if strong:
            valid_creds.append({
                "id": cid,
                "username": cred["username"],
                "platform": cred["platform"],
                "category_name": cat_map[cat_id]["name"],
                "strength": "strong"
            })
        else:
            weak_ids.append(cid)

    valid_creds.sort(key=lambda x: x["id"])
    weak_ids.sort()

    expected = {
        "valid_credentials": valid_creds,
        "weak_credential_ids": weak_ids,
        "summary": {
            "total_active": total_active,
            "valid_count": len(valid_creds),
            "weak_count": len(weak_ids),
            "ignored_count": ignored_count
        }
    }
    return expected

def run_verification():
    details = []
    total_score = 0

    # 1. 检查输出目录和文件存在性 (15分)
    output_dir = os.path.join(workspace, "output")
    report_path = os.path.join(output_dir, "safety_report.json")
    if os.path.isdir(output_dir):
        details.append({"item": "output目录存在", "score": 5, "max_score": 5, "passed": True, "reason": "output目录已创建"})
        total_score += 5
    else:
        details.append({"item": "output目录存在", "score": 0, "max_score": 5, "passed": False, "reason": "output目录缺失"})

    if os.path.isfile(report_path):
        details.append({"item": "safety_report.json存在", "score": 10, "max_score": 10, "passed": True, "reason": "报告文件已生成"})
        total_score += 10
    else:
        details.append({"item": "safety_report.json存在", "score": 0, "max_score": 10, "passed": False, "reason": "报告文件缺失"})
        # 如果文件不存在，直接结束
        score_info = {"total_score": total_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(score_info, f, indent=2)
        return

    # 2. 读取并验证报告JSON合法性 (15分)
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            report = json.load(f)
        details.append({"item": "报告JSON格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "可解析为JSON"})
        total_score += 10
    except (json.JSONDecodeError, Exception) as e:
        details.append({"item": "报告JSON格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON解析失败: {e}"})
        score_info = {"total_score": total_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(score_info, f, indent=2)
        return

    # 检查报告顶层字段
    required_fields = ["valid_credentials", "weak_credential_ids", "summary"]
    missing = [f for f in required_fields if f not in report]
    if missing:
        details.append({"item": "报告包含所有必需字段", "score": 0, "max_score": 5, "passed": False, "reason": f"缺少字段: {', '.join(missing)}"})
        total_score += 0
    else:
        details.append({"item": "报告包含所有必需字段", "score": 5, "max_score": 5, "passed": True, "reason": "字段齐全"})
        total_score += 5

    # 3. 读取源数据并计算预期结果 (70分)
    schema = load_json("data/vault_schema.json")
    credentials = load_json("data/credentials.json")
    audit_log = load_csv("data/audit_log.csv")
    if None in (schema, credentials, audit_log):
        details.append({"item": "源数据读取", "score": 0, "max_score": 70, "passed": False, "reason": "无法读取工作区源数据"})
        score_info = {"total_score": total_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(score_info, f, indent=2)
        return

    expected = get_expected_result(schema, credentials, audit_log)

    # 比较 valid_credentials
    agent_valid = report.get("valid_credentials", [])
    expected_valid = expected["valid_credentials"]
    valid_match = agent_valid == expected_valid
    if valid_match:
        details.append({"item": "valid_credentials内容正确", "score": 30, "max_score": 30, "passed": True, "reason": "所有有效凭证条目与预期一致"})
        total_score += 30
    else:
        # 部分得分：计算匹配条目的比例
        if len(expected_valid) == 0 and len(agent_valid) == 0:
            details.append({"item": "valid_credentials内容正确", "score": 30, "max_score": 30, "passed": True, "reason": "两者均为空"})
            total_score += 30
        else:
            match_count = 0
            for ev in expected_valid:
                if ev in agent_valid:
                    match_count += 1
            score_ratio = match_count / max(len(expected_valid), len(agent_valid))
            score = int(30 * score_ratio)
            details.append({"item": "valid_credentials内容正确", "score": score, "max_score": 30, "passed": False, "reason": f"匹配 {match_count}/{len(expected_valid)} 个，多余或缺失"})
            total_score += score

    # 比较 weak_credential_ids
    agent_weak = report.get("weak_credential_ids", [])
    expected_weak = expected["weak_credential_ids"]
    weak_match = sorted(agent_weak) == sorted(expected_weak)
    if weak_match:
        details.append({"item": "weak_credential_ids正确", "score": 20, "max_score": 20, "passed": True, "reason": "弱密码ID列表完全一致"})
        total_score += 20
    else:
        match_count = len(set(agent_weak) & set(expected_weak))
        score = 20 if match_count == len(expected_weak) and len(agent_weak) == len(expected_weak) else int(20 * (match_count / max(len(expected_weak),1)))
        details.append({"item": "weak_credential_ids正确", "score": score, "max_score": 20, "passed": False, "reason": f"交集 {match_count}, 预期 {len(expected_weak)}, 实际 {len(agent_weak)}"})
        total_score += score

    # 比较 summary
    agent_summary = report.get("summary", {})
    expected_summary = expected["summary"]
    summary_ok = all(agent_summary.get(k) == v for k,v in expected_summary.items())
    if summary_ok:
        details.append({"item": "summary统计正确", "score": 20, "max_score": 20, "passed": True, "reason": "所有统计字段与预期一致"})
        total_score += 20
    else:
        match_count = sum(1 for k,v in expected_summary.items() if agent_summary.get(k) == v)
        score = int(20 * (match_count / len(expected_summary)))
        details.append({"item": "summary统计正确", "score": score, "max_score": 20, "passed": False, "reason": f"匹配 {match_count}/{len(expected_summary)} 个字段"})
        total_score += score

    # 输出分数
    final_score = min(total_score, 100)
    result = {
        "total_score": final_score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    run_verification()
