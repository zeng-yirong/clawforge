import json
import os
import sys
import re

def parse_level(level_str: str) -> int:
    """Parse 'levelN' to integer N."""
    match = re.match(r"level(\d+)", level_str)
    if match:
        return int(match.group(1))
    return 0

def compute_expected_deny_list(workspace: str) -> list:
    """从工作区原始数据计算期望的拒绝列表"""
    # 读取 config
    with open(os.path.join(workspace, "ops", "config.json")) as f:
        config = json.load(f)
    current_id = config["current_account_id"]

    # 读取 accounts
    with open(os.path.join(workspace, "data", "accounts.json")) as f:
        acc_data = json.load(f)
    accounts = {a["account_id"]: a for a in acc_data["accounts"]}
    current_account = accounts.get(current_id)
    if not current_account:
        return []  # 无当前账户，无法判断
    # 解析权限字典: {type: level_int}
    perms = {}
    for perm_str in current_account.get("permissions", []):
        parts = perm_str.split(":", 1)
        if len(parts) == 2:
            dtype, lvl = parts
            perms[dtype] = parse_level(lvl)

    # 读取 assets
    with open(os.path.join(workspace, "data", "assets", "assets.json")) as f:
        ast_data = json.load(f)
    assets = {a["asset_id"]: a for a in ast_data["assets"]}

    # 读取 requests
    with open(os.path.join(workspace, "data", "requests", "requests.json")) as f:
        req_data = json.load(f)
    requests = req_data["requests"]

    deny_ids = []
    for req in requests:
        if req.get("status") != "pending":
            continue
        if req.get("actor_name") != current_id:
            continue
        asset_id = req.get("target_asset_id")
        asset = assets.get(asset_id)
        if not asset:
            continue  # 资产不存在，跳过
        required_level_str = asset.get("read_policy", "level0")
        required_level = parse_level(required_level_str)
        asset_type = asset.get("asset_type", "")
        user_level = perms.get(asset_type, 0)  # 默认 0 表示无权限
        if user_level < required_level:
            deny_ids.append(req["request_id"])
    return sorted(deny_ids)

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total = 0

    # --- 检查目录和文件存在 ---
    ops_dir = os.path.join(workspace, "ops")
    deny_path = os.path.join(ops_dir, "deny_list.json")
    # item 1: ops 目录
    dir_exists = os.path.isdir(ops_dir)
    details.append({
        "item": "ops directory exists",
        "score": 10 if dir_exists else 0,
        "max_score": 10,
        "passed": dir_exists,
        "reason": "ops/ found" if dir_exists else "ops/ missing"
    })
    total += details[-1]["score"]

    # item 2: deny_list.json 存在
    file_exists = os.path.isfile(deny_path)
    details.append({
        "item": "deny_list.json exists",
        "score": 10 if file_exists else 0,
        "max_score": 10,
        "passed": file_exists,
        "reason": "ops/deny_list.json found" if file_exists else "ops/deny_list.json not found"
    })
    total += details[-1]["score"]

    if not file_exists:
        # 如果文件不存在，后续检查无法进行，直接返回
        score = {"total_score": total, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(score, f, indent=2)
        print(json.dumps(score, indent=2))
        return

    # --- 解析 agent 结果 ---
    try:
        with open(deny_path) as f:
            agent_data = json.load(f)
        json_valid = True
    except (json.JSONDecodeError, Exception) as e:
        json_valid = False
        agent_data = None
    details.append({
        "item": "deny_list.json is valid JSON",
        "score": 10 if json_valid else 0,
        "max_score": 10,
        "passed": json_valid,
        "reason": "Valid JSON" if json_valid else f"Invalid JSON: {e}"
    })
    total += details[-1]["score"]

    if not json_valid:
        # 后续无法处理
        score = {"total_score": total, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(score, f, indent=2)
        print(json.dumps(score, indent=2))
        return

    # item 4: 结果应为列表
    is_list = isinstance(agent_data, list)
    details.append({
        "item": "Result is a list",
        "score": 10 if is_list else 0,
        "max_score": 10,
        "passed": is_list,
        "reason": "Is list" if is_list else f"Type is {type(agent_data).__name__}"
    })
    total += details[-1]["score"]

    if not is_list:
        score = {"total_score": total, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(score, f, indent=2)
        print(json.dumps(score, indent=2))
        return

    # item 5: 列表元素都是字符串
    all_str = all(isinstance(x, str) for x in agent_data)
    details.append({
        "item": "All elements are strings",
        "score": 10 if all_str else 0,
        "max_score": 10,
        "passed": all_str,
        "reason": "All strings" if all_str else "Non-string elements found"
    })
    total += details[-1]["score"]

    if not all_str:
        score = {"total_score": total, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(score, f, indent=2)
        print(json.dumps(score, indent=2))
        return

    # --- 计算期望结果 ---
    expected = compute_expected_deny_list(workspace)
    agent_sorted = sorted(agent_data)

    # item 6: 长度一致
    len_ok = len(agent_sorted) == len(expected)
    details.append({
        "item": "Correct number of request IDs",
        "score": 20 if len_ok else 0,
        "max_score": 20,
        "passed": len_ok,
        "reason": f"Expected {len(expected)} IDs, got {len(agent_sorted)}" if not len_ok else f"Count matches ({len(expected)})"
    })
    total += details[-1]["score"]

    # item 7: 内容一致 (集合相等)
    content_ok = agent_sorted == expected
    details.append({
        "item": "All expected request IDs present and no extras",
        "score": 30 if content_ok else 0,
        "max_score": 30,
        "passed": content_ok,
        "reason": "Content matches exactly" if content_ok else f"agent={agent_sorted}, expected={expected}"
    })
    total += details[-1]["score"]

    # 写入最终评分
    score = {"total_score": total, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(score, f, indent=2)
    print(json.dumps(score, indent=2))

if __name__ == "__main__":
    main()
