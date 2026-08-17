import sys
import os
import json
import csv

def parse_permission(perm):
    """解析权限字符串，如 'customer_data:standard' 或 'customer_data:*'，返回 (asset_type, classification)"""
    parts = perm.split(':')
    if len(parts) != 2:
        return None, None
    return parts[0], parts[1]

def account_allows(account, asset_type, classification):
    """判断账户是否允许访问指定资产类型和分类。classification可以是资产分类或附件中的客户分类"""
    for perm in account.get("permissions", []):
        atype, aclass = parse_permission(perm)
        if atype is None:
            continue
        if atype != asset_type and atype != "*":
            continue
        if aclass == "*" or aclass == classification:
            return True
    return False

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results = []
    total_score = 0

    def check(description, condition, score, max_score):
        nonlocal total_score
        passed = bool(condition)
        if passed:
            total_score += score
        results.append({
            "item": description,
            "score": score if passed else 0,
            "max_score": max_score,
            "passed": passed,
            "reason": "OK" if passed else "Failed"
        })

    # 1. 检查ops/export_deny.json是否存在
    deny_path = os.path.join(workspace, "ops", "export_deny.json")
    check("File ops/export_deny.json exists", os.path.isfile(deny_path), 10, 10)
    if not os.path.isfile(deny_path):
        final_score = total_score
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": final_score, "details": results}, f, indent=2)
        return

    # 2. 读取并验证JSON格式
    try:
        with open(deny_path, "r") as f:
            data = json.load(f)
        check("JSON is valid", True, 10, 10)
    except Exception as e:
        check("JSON is valid", False, 10, 10)
        final_score = total_score
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": final_score, "details": results}, f, indent=2)
        return

    # 3. 检查是否包含键denied_requests且值为列表
    check("Key 'denied_requests' exists and is a list", 
          isinstance(data.get("denied_requests"), list), 10, 10)
    if not isinstance(data.get("denied_requests"), list):
        final_score = total_score
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": final_score, "details": results}, f, indent=2)
        return

    denied = data["denied_requests"]
    denied_set = set(denied)
    # 检查是否有多余的请求（误判）
    check("No duplicate request IDs", len(denied) == len(denied_set), 5, 5)

    # 4. 计算期望的拒绝列表
    accounts_path = os.path.join(workspace, "data", "accounts.json")
    assets_path = os.path.join(workspace, "data", "assets", "assets.json")
    requests_path = os.path.join(workspace, "data", "requests", "requests.json")
    attachments_path = os.path.join(workspace, "data", "attachments.json")

    try:
        with open(accounts_path) as f:
            accounts_list = json.load(f)
        with open(assets_path) as f:
            assets_list = json.load(f)
        with open(requests_path) as f:
            requests_list = json.load(f)
        with open(attachments_path) as f:
            attachments_list = json.load(f)
    except Exception as e:
        check("Reading source data files", False, 0, 0)
        final_score = total_score
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": final_score, "details": results}, f, indent=2)
        return

    accounts = {a["account_id"]: a for a in accounts_list}
    assets = {a["asset_id"]: a for a in assets_list}
    att_by_req = {att.get("request_id"): att for att in attachments_list if att.get("request_id")}

    expected_denied = []
    for req in requests_list:
        if req["status"] != "pending":
            continue
        actor = req["actor_name"]
        target_asset_id = req["target_asset_id"]
        account = accounts.get(actor)
        asset = assets.get(target_asset_id)
        if not account or not asset:
            continue
        asset_type = asset["asset_type"]
        asset_classification = asset["classification"]

        # 检查是否有附件
        att = att_by_req.get(req["request_id"])
        if att:
            att_path = os.path.join(workspace, att["path"])
            if os.path.isfile(att_path):
                with open(att_path, newline='') as csvfile:
                    reader = csv.DictReader(csvfile)
                    classifications_in_attachment = set()
                    for row in reader:
                        classifications_in_attachment.add(row.get("classification", "").strip())
                allowed = True
                for cls in classifications_in_attachment:
                    if not account_allows(account, asset_type, cls):
                        allowed = False
                        break
                if not allowed:
                    expected_denied.append(req["request_id"])
                    continue
            else:
                expected_denied.append(req["request_id"])
                continue

        # 如果没有附件，则只检查资产类型和分类
        if not account_allows(account, asset_type, asset_classification):
            expected_denied.append(req["request_id"])

    expected_set = set(expected_denied)
    for rid in sorted(expected_set):
        check(f"Correctly denied request {rid}", rid in denied_set, 20, 20)

    legitimate = [r["request_id"] for r in requests_list if r["status"] == "pending" and r["request_id"] not in expected_set]
    for rid in sorted(legitimate):
        check(f"Did not wrongly deny legitimate request {rid}", rid not in denied_set, 10, 10)

    check("All denied request IDs are strings", all(isinstance(i, str) for i in denied), 5, 5)

    final_score = min(total_score, 100)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": final_score, "details": results}, f, indent=2)

if __name__ == "__main__":
    main()
