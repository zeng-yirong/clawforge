import json
import os
import sys
import re

def verify(workspace):
    details = []
    total_score = 0

    # 1. 目录结构检查 (10分)
    dirs = ["data", "data/requests", "data/assets", "ops"]
    all_dirs_exist = all(os.path.isdir(os.path.join(workspace, d)) for d in dirs)
    details.append({
        "item": "Directory structure - required folders exist",
        "score": 10 if all_dirs_exist else 0,
        "max_score": 10,
        "passed": all_dirs_exist,
        "reason": "All required directories present" if all_dirs_exist else "Missing one or more: data/, data/requests/, data/assets/, ops/"
    })
    total_score += details[-1]["score"]

    # 2. 输出文件 ops/violations.json 存在且合法 (10分)
    output_path = os.path.join(workspace, "ops", "violations.json")
    file_exists = os.path.isfile(output_path)
    if file_exists:
        try:
            with open(output_path, "r") as f:
                violations = json.load(f)
            valid_json = isinstance(violations, list)
            if not valid_json:
                reason = "Output is not a JSON list"
        except (json.JSONDecodeError, ValueError) as e:
            valid_json = False
            reason = f"JSON parse error: {e}"
    else:
        valid_json = False
        reason = "File ops/violations.json not found"
    details.append({
        "item": "ops/violations.json exists and is valid JSON array",
        "score": 10 if (file_exists and valid_json) else 0,
        "max_score": 10,
        "passed": file_exists and valid_json,
        "reason": reason if not (file_exists and valid_json) else "File is valid"
    })
    total_score += details[-1]["score"]

    if not (file_exists and valid_json):
        # 如果文件不存在或不是数组，后续无法检查，直接结束
        score = total_score
        result = {"total_score": score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # 3. 违规条目数量检查 (20分) - 预期2个违规请求：req_040 和 req_042
    expected_ids = {"req_040", "req_042"}
    actual_ids = set()
    for item in violations:
        if isinstance(item, dict) and "request_id" in item:
            actual_ids.add(item["request_id"])
    # 额外检查：不得包含非违规请求（例如拒绝的、已完成的、正常的）
    forbidden = {"req_041", "req_043", "req_044"}
    has_extra = bool(actual_ids & forbidden)
    correct_count = (len(actual_ids) == 2 and actual_ids == expected_ids)
    count_score = 20 if correct_count else (10 if len(actual_ids) == 2 else 5 if len(actual_ids) > 0 else 0)
    if has_extra:
        count_score = max(0, count_score - 10)
    details.append({
        "item": "Exactly the two violating request IDs (req_040, req_042) are present, no extra or missing",
        "score": count_score,
        "max_score": 20,
        "passed": correct_count and not has_extra,
        "reason": f"Found IDs: {actual_ids}" if not (correct_count and not has_extra) else "Correct set"
    })
    total_score += details[-1]["score"]

    # 4. 每个违规条目包含reason字段且合理 (20分)
    reason_score = 0
    reason_max = 20
    # 预期每个reason包含表示权限不足的关键词
    required_keywords = ["insufficient", "permission", "access"]
    all_reason_ok = True
    for item in violations:
        if not isinstance(item, dict) or "reason" not in item or not isinstance(item["reason"], str):
            all_reason_ok = False
            break
        # 检查至少包含一个关键词
        if not any(kw in item["reason"].lower() for kw in required_keywords):
            all_reason_ok = False
            break
    if all_reason_ok:
        reason_score = reason_max
    elif not all_reason_ok and actual_ids == expected_ids:
        # 如果ID正确但reason不理想，给部分分
        reason_score = 10
    details.append({
        "item": "Each violation entry has a 'reason' field with evidence of privilege/access insufficiency",
        "score": reason_score,
        "max_score": reason_max,
        "passed": all_reason_ok,
        "reason": "All reasons plausible" if all_reason_ok else "Missing or insufficient keywords in reason(s)"
    })
    total_score += details[-1]["score"]

    # 5. 验证是否正确根据权限判断 (额外精确性 40分)
    # 我们需要从环境文件中读取账户和资产信息，检查agent是否推断了正确原因
    # 但我们不能直接计算，因为验证脚本不应依赖重新计算（但为了严格，可以读取并对比）
    # 更好：检查每个违规项对应的request_id是否确实符合规则。
    # 我们在此重新计算期望结果，并与agent输出对比
    # 读取工作区原始数据
    requests_path = os.path.join(workspace, "data/requests/requests.json")
    accounts_path = os.path.join(workspace, "data/accounts.json")
    assets_path = os.path.join(workspace, "data/assets/assets.json")
    try:
        with open(requests_path) as f:
            reqs_dict = json.load(f)
        with open(accounts_path) as f:
            accs_dict = json.load(f)
        with open(assets_path) as f:
            assets_dict = json.load(f)
    except Exception as e:
        details.append({"item": "Ability to read source data for cross-verification", "score": 0, "max_score": 40, "passed": False, "reason": "Cannot load source data"})
        total_score += 0
        # 存储并退出
        result = {"total_score": total_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # 构建映射
    account_perms = {acc["account_id"]: set(acc["permissions"]) for acc in accs_dict.get("accounts", [])}
    asset_class = {ast["asset_id"]: ast["classification"] for ast in assets_dict.get("assets", [])}
    # 找出所有pending请求中，actor对应的账户权限不足的
    expected_violations = set()
    for req in reqs_dict.get("requests", []):
        if req.get("status") != "pending":
            continue
        actor = req.get("actor_name", "")
        # 根据actor_name查找account_id: 从accounts中找到display_name匹配的（或直接从request中拿？请求中没有直接account_id，只有actor_name）
        # 我们设计时actor_name与accounts.display_name对应
        matched_acct = None
        for acct in accs_dict.get("accounts", []):
            if acct["display_name"] == actor:
                matched_acct = acct
                break
        if matched_acct is None:
            continue
        target_asset_id = req.get("target_asset_id", "")
        if target_asset_id not in asset_class:
            continue
        required_class = asset_class[target_asset_id]
        user_perms = set(matched_acct.get("permissions", []))
        if required_class not in user_perms:
            expected_violations.add(req["request_id"])
    # 期望结果：{'req_040', 'req_042'}
    agent_ids = actual_ids
    correct_judgment = (agent_ids == expected_violations)
    judgment_score = 40 if correct_judgment else (20 if agent_ids.issubset(expected_violations) or expected_violations.issubset(agent_ids) else 0)
    details.append({
        "item": "Cross-verified: agent's violation list matches actual privilege rule evaluation",
        "score": judgment_score,
        "max_score": 40,
        "passed": correct_judgment,
        "reason": f"Expected {expected_violations}, got {agent_ids}" if not correct_judgment else "Perfect match"
    })
    total_score += details[-1]["score"]

    # 最终总分
    total_score = min(total_score, 100)  # 防止超过
    result = {"total_score": total_score, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)

if __name__ == "__main__":
    main()
