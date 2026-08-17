import sys
import os
import json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0

    # 1. 检查 ops/deny_targets.json 是否存在
    target_path = os.path.join(workspace, "ops", "deny_targets.json")
    if os.path.isfile(target_path):
        score_details.append({"item": "ops/deny_targets.json 存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
        total_score += 10
    else:
        score_details.append({"item": "ops/deny_targets.json 存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        # 后续评分项直接判零
        for item_name in ["JSON格式合法", "包含request_ids字段", "包含req-101", "包含req-102", "包含req-106", "无多余ID"]:
            score_details.append({"item": item_name, "score": 0, "max_score": 10 if "多余" not in item_name else 10, "passed": False, "reason": "前置检查失败"})
        finalize(score_details, total_score)
        return

    # 2. JSON 解析
    try:
        with open(target_path, "r") as f:
            data = json.load(f)
        score_details.append({"item": "JSON格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "可解析为合法JSON"})
        total_score += 10
    except (json.JSONDecodeError, ValueError) as e:
        score_details.append({"item": "JSON格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON解析失败: {e}"})
        for item_name in ["包含request_ids字段", "包含req-101", "包含req-102", "包含req-106", "无多余ID"]:
            score_details.append({"item": item_name, "score": 0, "max_score": 10 if "多余" not in item_name else 10, "passed": False, "reason": "前置检查失败"})
        finalize(score_details, total_score)
        return

    # 3. 检查 request_ids 字段
    if isinstance(data, dict) and "request_ids" in data and isinstance(data["request_ids"], list):
        score_details.append({"item": "包含request_ids字段且为数组", "score": 10, "max_score": 10, "passed": True, "reason": "存在正确字段"})
        total_score += 10
    else:
        score_details.append({"item": "包含request_ids字段且为数组", "score": 0, "max_score": 10, "passed": False, "reason": "字段缺失或类型错误"})
        for item_name in ["包含req-101", "包含req-102", "包含req-106", "无多余ID"]:
            score_details.append({"item": item_name, "score": 0, "max_score": 10 if "多余" not in item_name else 10, "passed": False, "reason": "前置检查失败"})
        finalize(score_details, total_score)
        return

    agent_ids = set(data["request_ids"])

    # 读取环境原始数据，计算期望ID
    assets_path = os.path.join(workspace, "data", "assets", "assets.json")
    requests_path = os.path.join(workspace, "data", "requests", "requests.json")

    try:
        with open(assets_path) as f:
            assets_list = json.load(f)
        with open(requests_path) as f:
            requests_list = json.load(f)
    except Exception as e:
        score_details.append({"item": "环境数据读取", "score": 0, "max_score": 10, "passed": False, "reason": f"无法读取资产或请求文件: {e}"})
        finalize(score_details, total_score)
        return

    # 构建资产查找字典
    asset_map = {a["asset_id"]: a for a in assets_list}

    # 计算期望ID：pending 状态，目标资产 classification = highly_confidential 且 asset_type 为 technical_plan 或 finance_archive
    expected_ids = set()
    for r in requests_list:
        if r["status"] != "pending":
            continue
        asset = asset_map.get(r["target_asset_id"])
        if asset is None:
            continue
        if asset["classification"] == "highly_confidential" and asset["asset_type"] in ("technical_plan", "finance_archive"):
            expected_ids.add(r["request_id"])

    # 4-6 检查每个期望ID是否存在
    expected_list = sorted(expected_ids)
    for idx, eid in enumerate(expected_list):
        if eid in agent_ids:
            score_details.append({"item": f"包含{eid}", "score": 20, "max_score": 20, "passed": True, "reason": f"期望ID {eid} 存在"})
            total_score += 20
        else:
            score_details.append({"item": f"包含{eid}", "score": 0, "max_score": 20, "passed": False, "reason": f"缺少期望ID {eid}"})

    # 7. 无多余ID
    extra = agent_ids - expected_ids
    if len(extra) == 0:
        score_details.append({"item": "无多余ID", "score": 10, "max_score": 10, "passed": True, "reason": "没有额外ID"})
        total_score += 10
    else:
        score_details.append({"item": "无多余ID", "score": 0, "max_score": 10, "passed": False, "reason": f"存在额外ID: {sorted(extra)}"})

    finalize(score_details, total_score)

def finalize(details, total_score):
    total_score = min(total_score, 100)  # 确保不超100
    result = {
        "total_score": total_score,
        "details": details
    }
    output_path = "workplace_score.json"
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written: {total_score}/100")

if __name__ == "__main__":
    main()
