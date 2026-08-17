import json
import os
import sys

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def compute_expected_denied(workspace):
    # 读取账户
    accounts_path = os.path.join(workspace, "data/accounts.json")
    assets_path = os.path.join(workspace, "data/assets/assets.json")
    requests_path = os.path.join(workspace, "data/requests/requests.json")
    
    with open(accounts_path, 'r') as f:
        accounts_data = json.load(f)
    with open(assets_path, 'r') as f:
        assets_data = json.load(f)
    with open(requests_path, 'r') as f:
        requests_data = json.load(f)
    
    # 构建账户字典：actor_name -> account_info
    accounts = {acc["display_name"]: acc for acc in accounts_data["accounts"]}
    
    # 构建资产字典：asset_id -> asset_info
    assets = {ast["asset_id"]: ast for ast in assets_data["assets"]}
    
    # 判断是否受限资产（classification restricted 且 read_policy audit_only）
    def is_restricted_asset(asset):
        return asset.get("classification") == "restricted" and asset.get("read_policy") == "audit_only"
    
    # 判断账户是否真正的审计员（Security Engineering 且拥有 audit 权限）
    def is_legitimate_auditor(account):
        return account["department"] == "Security Engineering" and "audit" in account.get("permissions", [])
    
    expected = set()
    for req in requests_data["requests"]:
        if req["claimed_role"] != "Security Auditor":
            continue
        target_asset = assets.get(req["target_asset_id"])
        if target_asset is None or not is_restricted_asset(target_asset):
            continue
        # actor_name 在 accounts 里找
        actor = accounts.get(req["actor_name"])
        if actor is None or not is_legitimate_auditor(actor):
            expected.add(req["request_id"])
    return expected

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results = []

    # 1. 检查 ops 目录是否存在
    ops_path = os.path.join(workspace, "ops")
    dir_exists = os.path.isdir(ops_path)
    results.append({
        "item": "ops 目录存在",
        "score": 5 if dir_exists else 0,
        "max_score": 5,
        "passed": dir_exists,
        "reason": "ops 目录存在" if dir_exists else "ops 目录不存在"
    })

    # 2. 检查 denied_requests.json 是否存在
    denied_path = os.path.join(ops_path, "denied_requests.json") if dir_exists else None
    file_exists = denied_path is not None and os.path.isfile(denied_path)
    results.append({
        "item": "denied_requests.json 存在",
        "score": 5 if file_exists else 0,
        "max_score": 5,
        "passed": file_exists,
        "reason": "文件存在" if file_exists else "文件不存在"
    })

    if not file_exists:
        # 无法继续，总分0
        total = sum(r["score"] for r in results)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": results}, f, indent=2)
        print(f"Score: {total}/100")
        return

    # 3. 解析 JSON 格式并获取拒绝集合
    try:
        with open(denied_path, 'r') as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        results.append({
            "item": "denied_requests.json JSON 解析",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON 解析失败: {e}"
        })
        total = sum(r["score"] for r in results)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": results}, f, indent=2)
        print(f"Score: {total}/100")
        return

    # 支持两种格式：直接列表 或 包含 "denied_request_ids" 键的字典
    if isinstance(data, list):
        denied_set = set(data)
        field_ok = True
    elif isinstance(data, dict) and "denied_request_ids" in data:
        denied_set = set(data["denied_request_ids"])
        field_ok = True
    else:
        denied_set = set()
        field_ok = False

    results.append({
        "item": "denied_requests.json 结构合法",
        "score": 10 if field_ok else 0,
        "max_score": 10,
        "passed": field_ok,
        "reason": "结构正确（列表或包含denied_request_ids的字典）" if field_ok else "结构错误，期望列表或{'denied_request_ids': [...]}"
    })

    if not field_ok:
        total = sum(r["score"] for r in results)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": results}, f, indent=2)
        print(f"Score: {total}/100")
        return

    # 4. 计算预期拒绝集合
    try:
        expected_set = compute_expected_denied(workspace)
    except Exception as e:
        results.append({
            "item": "计算预期拒绝结果",
            "score": 0,
            "max_score": 50,
            "passed": False,
            "reason": f"读取数据文件时出错: {e}"
        })
        total = sum(r["score"] for r in results)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": results}, f, indent=2)
        print(f"Score: {total}/100")
        return

    # 5. 比较集合
    true_positives = denied_set & expected_set
    false_positives = denied_set - expected_set
    false_negatives = expected_set - denied_set

    # 精确率、召回率、F1，但为了简单，使用差异扣分法
    # 满分50，每个多出的（false positive）扣10分，每个遗漏的（false negative）扣10分，最少0分
    deduction = (len(false_positives) + len(false_negatives)) * 10
    match_score = max(0, 50 - deduction)

    if match_score == 50:
        reason = "完全匹配，无多余无遗漏"
    else:
        reason_parts = []
        if false_positives:
            reason_parts.append(f"多出请求: {sorted(false_positives)}")
        if false_negatives:
            reason_parts.append(f"遗漏请求: {sorted(false_negatives)}")
        reason = "; ".join(reason_parts)

    results.append({
        "item": "拒绝请求集合匹配",
        "score": match_score,
        "max_score": 50,
        "passed": (match_score == 50),
        "reason": reason
    })

    # 6. 额外的数据有效性检查：所有 denied 中的 request_id 必须存在于原始 requests.json 中
    # 读取原始请求ID
    try:
        with open(os.path.join(workspace, "data/requests/requests.json"), 'r') as f:
            all_requests = json.load(f)["requests"]
        all_ids = {r["request_id"] for r in all_requests}
        invalid_ids = denied_set - all_ids
        validity_ok = len(invalid_ids) == 0
        validity_score = 10 if validity_ok else 0
        validity_reason = "所有ID有效" if validity_ok else f"无效ID: {invalid_ids}"
    except Exception as e:
        validity_ok = False
        validity_score = 0
        validity_reason = f"检查数据有效性出错: {e}"

    results.append({
        "item": "拒绝ID全部在原始请求中",
        "score": validity_score,
        "max_score": 10,
        "passed": validity_ok,
        "reason": validity_reason
    })

    # 7. 检查 denied_requests.json 是否包含多余字段（如果有不应该出现的键）
    # 只对字典格式检查
    extra_fields_penalty = 0
    if isinstance(data, dict):
        allowed_keys = {"denied_request_ids"}
        actual_keys = set(data.keys())
        extra = actual_keys - allowed_keys
        if extra:
            extra_fields_penalty = 10
            extra_field_reason = f"含有非预期字段: {extra}"
        else:
            extra_field_reason = "无多余字段"
    else:
        extra_field_reason = "列表格式，不检查多余字段（视为可接受）"

    results.append({
        "item": "无多余字段",
        "score": max(0, 10 - extra_fields_penalty),
        "max_score": 10,
        "passed": (extra_fields_penalty == 0),
        "reason": extra_field_reason
    })

    # 计算总分
    total_score = sum(r["score"] for r in results)
    # 确保不超过100
    total_score = min(100, total_score)

    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": results}, f, indent=2)
    print(f"Score: {total_score}/100")

if __name__ == "__main__":
    main()
