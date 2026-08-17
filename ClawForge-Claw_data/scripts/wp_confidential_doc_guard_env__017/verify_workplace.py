import json
import os
import sys

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0

    # 1. 检查 ops 目录是否存在 (10分)
    ops_path = os.path.join(workspace, "ops")
    if os.path.isdir(ops_path):
        score_details.append({
            "item": "ops directory exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "ops directory found"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "ops directory exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ops directory missing"
        })
        # 如果目录不存在，后续检查无法进行，直接输出结果
        result = {"total_score": total_score, "details": score_details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        print(json.dumps(result, indent=2))
        return

    # 2. 检查 blocked_requests.json 是否存在且格式合法 (10分)
    result_path = os.path.join(workspace, "ops", "blocked_requests.json")
    if not os.path.isfile(result_path):
        score_details.append({
            "item": "blocked_requests.json exists and valid JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not found"
        })
        result = {"total_score": total_score, "details": score_details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        print(json.dumps(result, indent=2))
        return

    try:
        blocked = load_json(result_path)
        if not isinstance(blocked, list):
            raise ValueError("Not a list")
        # 每个元素必须有 request_id 和 reason
        for entry in blocked:
            if not isinstance(entry, dict) or "request_id" not in entry or "reason" not in entry:
                raise ValueError("Missing fields")
        score_details.append({
            "item": "blocked_requests.json exists and valid JSON",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Valid JSON array with required fields"
        })
        total_score += 10
    except Exception as e:
        score_details.append({
            "item": "blocked_requests.json exists and valid JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Invalid format: {e}"
        })
        result = {"total_score": total_score, "details": score_details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        print(json.dumps(result, indent=2))
        return

    # 3. 从环境数据获取期望的拒绝列表 (50分)
    try:
        assets = load_json(os.path.join(workspace, "data/assets/assets.json"))["assets"]
        requests_data = load_json(os.path.join(workspace, "data/requests/requests.json"))["requests"]
    except Exception as e:
        score_details.append({
            "item": "Correct request IDs (matching expected)",
            "score": 0,
            "max_score": 50,
            "passed": False,
            "reason": f"Cannot load env data: {e}"
        })
        result = {"total_score": total_score, "details": score_details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        print(json.dumps(result, indent=2))
        return

    # 找出所有未发布的技术计划或财务资产 (名称包含 "Unpublished")
    target_asset_ids = set()
    for a in assets:
        if "Unpublished" in a["asset_name"] and a["asset_type"] in ("technical_plan", "finance_archive"):
            target_asset_ids.add(a["asset_id"])

    # 找出所有应拒绝的请求: target_asset_id 在 target 中, channel=external, status=pending
    expected_requests = []
    for req in requests_data:
        if (req["target_asset_id"] in target_asset_ids and
            req["channel"] == "external" and
            req["status"] == "pending"):
            expected_requests.append(req)

    expected_ids = sorted([r["request_id"] for r in expected_requests])

    # 获取 agent 提交的 request_id 列表
    agent_ids = sorted([entry["request_id"] for entry in blocked])

    if agent_ids == expected_ids:
        score_details.append({
            "item": "Correct request IDs (matching expected)",
            "score": 50,
            "max_score": 50,
            "passed": True,
            "reason": f"All {len(expected_ids)} expected requests present, no extra/missing"
        })
        total_score += 50
    else:
        missing = set(expected_ids) - set(agent_ids)
        extra = set(agent_ids) - set(expected_ids)
        reason_parts = []
        if missing:
            reason_parts.append(f"Missing ids: {sorted(missing)}")
        if extra:
            reason_parts.append(f"Extra ids: {sorted(extra)}")
        score_details.append({
            "item": "Correct request IDs (matching expected)",
            "score": 0,
            "max_score": 50,
            "passed": False,
            "reason": "; ".join(reason_parts)
        })

    # 4. 检查每个 reason 是否包含对应的资产名称 (30分)
    # 为每个请求构造 asset_name 映射
    asset_name_map = {a["asset_id"]: a["asset_name"] for a in assets}
    req_target_map = {r["request_id"]: r["target_asset_id"] for r in requests_data}

    reason_score = 0
    reason_details = []
    for entry in blocked:
        rid = entry["request_id"]
        if rid not in expected_ids:
            continue  # 多余的不计分
        expected_asset_name = asset_name_map.get(req_target_map[rid], "")
        if expected_asset_name in entry["reason"]:
            reason_score += 30 // len(expected_ids) if expected_ids else 0
            reason_details.append(f"{rid}: reason contains '{expected_asset_name}'")
        else:
            reason_details.append(f"{rid}: reason missing '{expected_asset_name}', got '{entry['reason']}'")

    # 如果 expected_ids 为空，则 reason_score 直接给30（无理由要求）
    if not expected_ids:
        reason_score = 30
        reason_details = ["No expected requests, reason check skipped"]

    score_details.append({
        "item": "Reason contains correct asset name",
        "score": reason_score,
        "max_score": 30,
        "passed": reason_score == 30,
        "reason": "; ".join(reason_details) if reason_details else "All ok"
    })
    total_score += reason_score

    # 写入结果
    result = {"total_score": total_score, "details": score_details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
