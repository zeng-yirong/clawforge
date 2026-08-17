import os
import sys
import json

WORKSPACE = sys.argv[1] if len(sys.argv) > 1 else "."

def load_json(relative_path):
    full_path = os.path.join(WORKSPACE, relative_path)
    if not os.path.exists(full_path):
        return None
    with open(full_path, "r") as f:
        return json.load(f)

def compute_expected_deny_ids():
    """根据 accounts.json, assets.json, requests.json 计算应拒绝的请求ID"""
    accounts = load_json("data/accounts.json")
    assets = load_json("data/assets/assets.json")
    requests = load_json("data/requests/requests.json")
    if not all([accounts, assets, requests]):
        return set()
    # 获取当前账户权限（取第一个账户，实际应取当前操作者，这里固定为 acc_001）
    current_account = None
    for acc in accounts.get("accounts", []):
        if acc["account_id"] == "acc_001":
            current_account = acc
            break
    if not current_account:
        return set()
    allowed_types = set(current_account.get("permissions", []))
    # 构建资产类型映射
    asset_type_map = {}
    for asset in assets.get("assets", []):
        asset_type_map[asset["asset_id"]] = asset.get("asset_type", "")
    # 过滤 pending 请求且目标资产类型不在 allowed_types 中
    deny_ids = set()
    for req in requests.get("requests", []):
        if req.get("status") != "pending":
            continue
        target = req.get("target_asset_id", "")
        asset_type = asset_type_map.get(target, "")
        if asset_type and asset_type not in allowed_types:
            deny_ids.add(req["request_id"])
    return deny_ids

def main():
    details = []
    total_score = 0

    # 1. 检查目录结构 (ops/ 存在)
    ops_path = os.path.join(WORKSPACE, "ops")
    dir_exists = os.path.isdir(ops_path)
    details.append({
        "item": "目录 ops/ 存在",
        "score": 10 if dir_exists else 0,
        "max_score": 10,
        "passed": dir_exists,
        "reason": "ops 目录已创建" if dir_exists else "未在 workspace 根目录下找到 ops/ 文件夹"
    })
    if dir_exists:
        total_score += 10

    # 2. 检查目标文件 ops/deny_requests.json 存在
    deny_path = os.path.join(WORKSPACE, "ops/deny_requests.json")
    file_exists = os.path.isfile(deny_path)
    details.append({
        "item": "文件 ops/deny_requests.json 存在",
        "score": 10 if file_exists else 0,
        "max_score": 10,
        "passed": file_exists,
        "reason": "目标文件已生成" if file_exists else "未找到 ops/deny_requests.json"
    })
    if file_exists:
        total_score += 10

    # 3. JSON 格式合法
    parsed = None
    format_ok = False
    if file_exists:
        try:
            with open(deny_path, "r") as f:
                parsed = json.load(f)
            format_ok = True
        except (json.JSONDecodeError, Exception):
            format_ok = False
    details.append({
        "item": "JSON 格式合法",
        "score": 10 if format_ok else 0,
        "max_score": 10,
        "passed": format_ok,
        "reason": "JSON 解析成功" if format_ok else "文件内容不是合法 JSON"
    })
    if format_ok:
        total_score += 10

    # 4. 包含所需字段 request_ids (必须是列表)
    field_ok = False
    request_ids = []
    if format_ok and isinstance(parsed, dict):
        if "request_ids" in parsed and isinstance(parsed["request_ids"], list):
            field_ok = True
            request_ids = parsed["request_ids"]
    details.append({
        "item": "包含 'request_ids' 列表字段",
        "score": 10 if field_ok else 0,
        "max_score": 10,
        "passed": field_ok,
        "reason": "字段符合要求" if field_ok else "缺少 request_ids 字段或不是列表"
    })
    if field_ok:
        total_score += 10

    # 5. 计算期望的拒绝列表（依赖 env_builder 铺出的数据）
    expected_ids = compute_expected_deny_ids()
    # 如果无法计算期望值（数据缺失），跳过该项（但影响评分）
    if not expected_ids:
        details.append({
            "item": "预期拒绝列表计算",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "无法读取环境数据计算期望值"
        })
        # 不给予分数
    else:
        actual_set = set(request_ids) if field_ok else set()
        matched = actual_set == expected_ids
        details.append({
            "item": "拒绝列表与预期完全一致",
            "score": 30 if matched else 0,
            "max_score": 30,
            "passed": matched,
            "reason": f"匹配预期: {sorted(expected_ids)}" if matched else f"预期 {sorted(expected_ids)}，实际 {sorted(actual_set)}"
        })
        if matched:
            total_score += 30
        else:
            # 部分正确给部分分（例如每正确一个给 15）
            correct = actual_set & expected_ids
            wrong = actual_set - expected_ids
            missing = expected_ids - actual_set
            # 计算分数：每个正确ID得10分，最多30，错误ID每个扣5分（最低0）
            partial = min(len(correct) * 10, 30) - min(len(wrong) * 5, 30)
            partial = max(partial, 0)
            total_score += partial
            details[-1]["score"] = partial
            details[-1]["reason"] = f"部分正确: 正确={sorted(correct)}, 多余={sorted(wrong)}, 缺失={sorted(missing)}"

    # 6. 检查是否包含多余的字段（如存在其他无关字段扣分）
    extra_fields = False
    if format_ok and isinstance(parsed, dict):
        allowed_keys = {"request_ids"}
        actual_keys = set(parsed.keys())
        if actual_keys - allowed_keys:
            extra_fields = True
    details.append({
        "item": "无多余字段",
        "score": 5 if not extra_fields else 0,
        "max_score": 5,
        "passed": not extra_fields,
        "reason": "仅包含预期字段" if not extra_fields else f"包含多余字段: {actual_keys - allowed_keys}"
    })
    if not extra_fields:
        total_score += 5

    # 7. 检查 request_ids 中每个元素都是字符串
    str_ids_ok = all(isinstance(rid, str) for rid in request_ids) if field_ok else False
    details.append({
        "item": "request_ids 内所有元素均为字符串",
        "score": 5 if str_ids_ok else 0,
        "max_score": 5,
        "passed": str_ids_ok,
        "reason": "所有ID为字符串" if str_ids_ok else "存在非字符串ID"
    })
    if str_ids_ok:
        total_score += 5

    # 额外检查：deny_requests.json 中 request_ids 应该去重（重复列表可扣分）
    if field_ok and isinstance(request_ids, list):
        if len(request_ids) != len(set(request_ids)):
            details.append({
                "item": "无重复元素",
                "score": 0,
                "max_score": 5,
                "passed": False,
                "reason": "列表中存在重复ID"
            })
            # 不扣分但提示
        else:
            details.append({
                "item": "无重复元素",
                "score": 5,
                "max_score": 5,
                "passed": True,
                "reason": "所有ID唯一"
            })
            total_score += 5
    else:
        details.append({
            "item": "无重复元素",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "无法检查（字段缺失）"
        })

    # 总分上限100
    total_score = min(total_score, 100)

    result = {
        "total_score": total_score,
        "details": details
    }
    score_path = os.path.join(WORKSPACE, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(result, f, indent=2)

    print(f"Verification complete. Total score: {total_score}/100")

if __name__ == "__main__":
    main()
