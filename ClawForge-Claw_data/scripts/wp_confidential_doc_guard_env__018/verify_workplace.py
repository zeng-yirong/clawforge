import json
import sys
import os
from pathlib import Path

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    ws = Path(workspace)

    details = []
    total_score = 0

    # 1. 检查目录 ops 是否存在 (10分)
    ops_dir = ws / "ops"
    if ops_dir.is_dir():
        details.append({"item": "ops 目录存在", "score": 10, "max_score": 10, "passed": True, "reason": "ops 目录存在"})
        total_score += 10
    else:
        details.append({"item": "ops 目录存在", "score": 0, "max_score": 10, "passed": False, "reason": "ops 目录缺失"})

    # 2. 检查 ops/denied.json 是否存在且为合法 JSON (10分)
    denied_path = ops_dir / "denied.json"
    if denied_path.is_file():
        try:
            with open(denied_path, "r") as f:
                denied_data = json.load(f)
            if isinstance(denied_data, list):
                details.append({"item": "denied.json 格式正确", "score": 10, "max_score": 10, "passed": True, "reason": "合法列表"})
                total_score += 10
            else:
                details.append({"item": "denied.json 格式正确", "score": 0, "max_score": 10, "passed": False, "reason": "不是列表"})
                denied_data = []
        except Exception as e:
            details.append({"item": "denied.json 格式正确", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON解析失败: {e}"})
            denied_data = []
    else:
        details.append({"item": "denied.json 格式正确", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        denied_data = []

    # 3. 读取原始请求数据，确定预期被拒绝的 request_id (80分)
    requests_path = ws / "data/requests/requests.json"
    assets_path = ws / "data/assets/assets.json"
    accounts_path = ws / "data/accounts/accounts.json"

    # 加载资产
    if assets_path.is_file():
        with open(assets_path) as f:
            assets_data = json.load(f).get("assets", [])
    else:
        assets_data = []
    asset_map = {a["asset_id"]: a for a in assets_data}

    # 加载账户
    if accounts_path.is_file():
        with open(accounts_path) as f:
            accounts_data = json.load(f).get("accounts", [])
    else:
        accounts_data = []
    account_map = {a["display_name"]: a for a in accounts_data}

    # 加载请求
    if requests_path.is_file():
        with open(requests_path) as f:
            all_requests = json.load(f).get("requests", [])
    else:
        all_requests = []

    # 定义“应拒绝”逻辑：
    # - 状态是 pending 或 active
    # - 目标资产的 classification 为 confidential 或 restricted（未发布的机密）
    # - asset_type 为 technical_plan 或 finance_archive
    # - 高风险(high/critical) 或 中风险但角色不合规（这里简化：只考虑风险等级≥medium）
    # - 并且角色没有 read_all 权限（即账户的permissions不含read_all）
    #   外部承包商、离职等默认无权限。
    expected_deny = set()
    for req in all_requests:
        status = req.get("status","")
        if status not in ("pending","active"):
            continue
        target = asset_map.get(req.get("target_asset_id"))
        if not target:
            continue
        if target["classification"] not in ("confidential","restricted"):
            continue
        if target["asset_type"] not in ("technical_plan","finance_archive"):
            continue
        risk = req.get("risk_level","low")
        if risk not in ("high","critical","medium"):
            continue
        # 检查 actor 权限
        actor = account_map.get(req.get("actor_name"))
        if actor and "read_all" in actor.get("permissions",[]):
            continue  # 有 full access 的允许
        expected_deny.add(req["request_id"])

    # 预期被拒绝的 ID 列表（按字母序排序以保证匹配）
    expected_list = sorted(expected_deny)

    # 计算匹配分：每个正确 ID 得 20 分，最多 4 个正确则满分 80
    if not expected_list:
        # 如果预期为空（异常情况）
        match_score = 80 if len(denied_data) == 0 else 0
        match_reason = "无预期拒绝项" if len(denied_data)==0 else f"预期无拒绝，但实际有 {len(denied_data)} 项"
        details.append({"item": "拒绝列表精确匹配", "score": match_score, "max_score": 80, "passed": match_score==80, "reason": match_reason})
        total_score += match_score
    else:
        # 实际列表去重排序
        actual_sorted = sorted(set(denied_data))
        # 检查是否完全相等
        if actual_sorted == expected_list:
            details.append({"item": "拒绝列表精确匹配", "score": 80, "max_score": 80, "passed": True, "reason": f"完全匹配预期 {expected_list}"})
            total_score += 80
        else:
            # 部分匹配：计算交集大小
            correct = set(actual_sorted) & expected_deny
            score = int(80 * len(correct) / len(expected_list))
            details.append({"item": "拒绝列表精确匹配", "score": score, "max_score": 80, "passed": False, "reason": f"预期 {expected_list}，实际 {actual_sorted}，正确 {sorted(correct)}"})
            total_score += score

    # 写入结果
    result = {
        "total_score": min(total_score, 100),
        "details": details
    }
    with open(ws / "workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

    print(f"评分完成: {result['total_score']}/100")
    return result["total_score"]

if __name__ == "__main__":
    main()
