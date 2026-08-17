import sys
import json
import os
from pathlib import Path

def verify_workplace(workspace):
    ws = Path(workspace).resolve()
    details = []
    total_score = 0

    # 1. 检查目录结构是否存在 (10分)
    dirs_ok = True
    needed_dirs = ["data/assets", "data/requests", "ops"]
    for d in needed_dirs:
        if not (ws / d).is_dir():
            dirs_ok = False
            break
    if dirs_ok:
        details.append({"item": "required directories exist", "score": 10, "max_score": 10, "passed": True, "reason": "All required directories present"})
        total_score += 10
    else:
        details.append({"item": "required directories exist", "score": 0, "max_score": 10, "passed": False, "reason": "Missing one or more directories: data/assets, data/requests, ops"})
        # 若目录都不全则直接返回，不再继续
        _write_result(ws, total_score, details)
        return

    # 2. 读取资产和请求文件 (格式合法性 10分)
    try:
        with open(ws / "data/assets/assets.json") as f:
            assets_data = json.load(f)
        with open(ws / "data/requests/requests.json") as f:
            requests_data = json.load(f)
        # 检查包装器
        if "assets" not in assets_data or "requests" not in requests_data:
            raise ValueError("Missing wrapper keys")
        assets = assets_data["assets"]
        requests = requests_data["requests"]
        details.append({"item": "asset and request JSON files valid", "score": 10, "max_score": 10, "passed": True, "reason": "Files parse correctly and contain expected wrappers"})
        total_score += 10
    except Exception as e:
        details.append({"item": "asset and request JSON files valid", "score": 0, "max_score": 10, "passed": False, "reason": f"Failed to parse: {e}"})
        _write_result(ws, total_score, details)
        return

    # 3. 计算正确答案：所有 read_policy == "unpublished" 的资产ID
    unpublished_asset_ids = set()
    for asset in assets:
        if asset.get("read_policy") == "unpublished":
            unpublished_asset_ids.add(asset["asset_id"])

    # 从请求中找出所有 target_asset_id 在 unpublished_asset_ids 中的请求ID
    expected_deny_ids = set()
    for req in requests:
        if req.get("target_asset_id") in unpublished_asset_ids:
            expected_deny_ids.add(req["request_id"])

    # 4. 检查 agent 产出的 ops/deny_requests.json (80分)
    agent_file = ws / "ops/deny_requests.json"
    if not agent_file.is_file():
        details.append({"item": "output file ops/deny_requests.json exists", "score": 0, "max_score": 80, "passed": False, "reason": "File not found"})
        _write_result(ws, total_score + 0, details)
        return

    try:
        with open(agent_file) as f:
            agent_ids = json.load(f)
        if not isinstance(agent_ids, list):
            details.append({"item": "output file content type", "score": 0, "max_score": 80, "passed": False, "reason": "JSON root is not a list"})
            _write_result(ws, total_score + 0, details)
            return
        # 去重？我们允许重复，但算错
        agent_set = set(agent_ids)
    except Exception as e:
        details.append({"item": "output file valid JSON", "score": 0, "max_score": 80, "passed": False, "reason": f"Invalid JSON: {e}"})
        _write_result(ws, total_score + 0, details)
        return

    # 5. 比对 (80分)
    # 完全匹配得80，每个漏/多扣20分（上限80）
    false_negatives = expected_deny_ids - agent_set
    false_positives = agent_set - expected_deny_ids
    total_errors = len(false_negatives) + len(false_positives)
    penalty = total_errors * 20
    score_80 = max(0, 80 - penalty)

    if total_errors == 0:
        reason = "All expected request IDs present, no extra IDs"
    else:
        fn_list = sorted(false_negatives)
        fp_list = sorted(false_positives)
        reason = f"Errors: missed {fn_list}, extra {fp_list}"
    details.append({
        "item": "deny list matches expected requests targeting unpublished assets",
        "score": score_80,
        "max_score": 80,
        "passed": total_errors == 0,
        "reason": reason
    })
    total_score += score_80

    _write_result(ws, total_score, details)

def _write_result(ws, total_score, details):
    result = {
        "total_score": min(total_score, 100),
        "details": details
    }
    with open(ws / "workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify_workplace(workspace)
