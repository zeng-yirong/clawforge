import sys
import os
import json
from pathlib import Path

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def compute_expected_blocked(workspace):
    """根据策略和账户信息计算应阻止的请求ID和期望理由关键词"""
    # 加载策略
    policy_path = os.path.join(workspace, "ops/policy.md")
    with open(policy_path, 'r') as f:
        policy = json.load(f)
    rules = policy.get("rules", [])
    default_deny = policy.get("default", "deny") == "deny"

    # 构建部门->允许资产映射
    dept_allowed = {}
    for rule in rules:
        dept = rule.get("department")
        if dept:
            dept_allowed[dept] = set(rule.get("allowed", []))

    # 加载账户
    accounts_path = os.path.join(workspace, "data/accounts.json")
    accounts = load_json(accounts_path)["accounts"]
    account_dept = {a["account_id"]: a["department"] for a in accounts}

    # 加载请求
    requests_path = os.path.join(workspace, "data/requests/requests.json")
    requests = load_json(requests_path)["requests"]

    expected = []
    for req in requests:
        rid = req["request_id"]
        actor = req["actor_name"]
        target = req["target_asset_id"]
        if actor in account_dept:
            dept = account_dept[actor]
            allowed_set = dept_allowed.get(dept, set())
            if target not in allowed_set:
                # 阻止，理由应包含部门或 "not allowed"
                expected.append((rid, [dept, "not allowed", "deny"]))
        else:
            if default_deny:
                expected.append((rid, [actor, "Unknown", "default", "deny"]))
    return expected

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    workspace = Path(workspace).resolve()

    details = []
    total_score = 0

    # 1. 检查ops/blocked.json是否存在 (10分)
    blocked_path = workspace / "ops" / "blocked.json"
    if blocked_path.exists() and blocked_path.is_file():
        details.append({"item": "ops/blocked.json 存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
        total_score += 10
    else:
        details.append({"item": "ops/blocked.json 存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        # 后续无法检查，直接返回
        final_score = total_score
        result = {"total_score": final_score, "details": details}
        with open(workspace / "workplace_score.json", "w") as f:
            json.dump(result, f, indent=2)
        print(json.dumps(result, indent=2))
        return

    # 2. JSON合法且结构正确 (10分)
    try:
        with open(blocked_path, 'r') as f:
            blocked_list = json.load(f)
        if not isinstance(blocked_list, list):
            raise ValueError("不是数组")
        for item in blocked_list:
            if not isinstance(item, dict) or "request_id" not in item or "reason" not in item:
                raise ValueError("缺少必要字段")
        details.append({"item": "JSON格式正确", "score": 10, "max_score": 10, "passed": True, "reason": "合法列表结构"})
        total_score += 10
    except Exception as e:
        details.append({"item": "JSON格式正确", "score": 0, "max_score": 10, "passed": False, "reason": str(e)})
        final_score = total_score
        result = {"total_score": final_score, "details": details}
        with open(workspace / "workplace_score.json", "w") as f:
            json.dump(result, f, indent=2)
        print(json.dumps(result, indent=2))
        return

    # 3. 计算期望结果
    expected = compute_expected_blocked(workspace)
    expected_ids = set(e[0] for e in expected)
    actual_ids = set(item["request_id"] for item in blocked_list)

    # 结果正确性 (50分)
    if actual_ids == expected_ids:
        details.append({"item": "阻止的请求ID匹配", "score": 50, "max_score": 50, "passed": True, "reason": "完全正确"})
        total_score += 50
    else:
        missing = expected_ids - actual_ids
        extra = actual_ids - expected_ids
        reason = f"缺失：{missing}，多余：{extra}"
        # 每个ID错误扣25分，最多扣50
        penalty = len(missing) * 25 + len(extra) * 25
        score = max(0, 50 - penalty)
        details.append({"item": "阻止的请求ID匹配", "score": score, "max_score": 50, "passed": score == 50, "reason": reason})
        total_score += score

    # 4. 理由质量 (每个条目10分，共20分)
    # 建立实际理由字典
    actual_reasons = {item["request_id"]: item.get("reason", "") for item in blocked_list}
    reason_score = 0
    max_reason = 20
    for rid, keywords_list in expected:
        if rid in actual_reasons:
            reason = actual_reasons[rid]
            # 检查是否包含任一关键词
            if any(kw.lower() in reason.lower() for kw in keywords_list):
                reason_score += 10
                sub_pass = True
            else:
                sub_pass = False
        else:
            sub_pass = False
        if not sub_pass:
            # 扣分记录在details里，但我们要汇总
            pass
    # 实际加起来
    details.append({"item": "理由包含必要关键词", "score": reason_score, "max_score": max_reason, "passed": reason_score == max_reason,
                    "reason": f"得{reason_score}/20"})
    total_score += reason_score

    # 5. 无多余字段 (10分)
    extra_fields = False
    for item in blocked_list:
        if set(item.keys()) != {"request_id", "reason"}:
            extra_fields = True
            break
    if not extra_fields:
        details.append({"item": "无多余字段", "score": 10, "max_score": 10, "passed": True, "reason": "仅含request_id和reason"})
        total_score += 10
    else:
        details.append({"item": "无多余字段", "score": 0, "max_score": 10, "passed": False, "reason": "发现额外字段"})
        total_score += 0

    # 最终结果
    final_score = min(100, total_score)
    result = {"total_score": final_score, "details": details}
    with open(workspace / "workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    verify()
