import sys
import os
import json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    os.chdir(workspace)

    details = []
    total_score = 0

    # 1. 检查 ops/deny_list.json 是否存在 (10分)
    deny_path = "ops/deny_list.json"
    if os.path.exists(deny_path):
        details.append({
            "item": "Output file exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"Found {deny_path}"
        })
        total_score += 10
    else:
        details.append({
            "item": "Output file exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Missing {deny_path}"
        })
        # 无法继续，直接写入结果并退出
        write_result(details, total_score)
        return

    # 2. 解析 deny_list.json 合法性 (10分)
    try:
        with open(deny_path, 'r') as f:
            deny_list = json.load(f)
        if not isinstance(deny_list, list):
            raise ValueError("deny_list must be a list")
        details.append({
            "item": "File is valid JSON and contains a list",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"Parsed list with {len(deny_list)} items"
        })
        total_score += 10
    except Exception as e:
        details.append({
            "item": "File is valid JSON and contains a list",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Invalid: {str(e)}"
        })
        write_result(details, total_score)
        return

    # 3. 计算正确答案 (30分)
    # 重新读取原始数据
    try:
        with open('data/assets/assets.json', 'r') as f:
            assets_data = json.load(f)["assets"]
        with open('data/requests/requests.json', 'r') as f:
            requests_data = json.load(f)["requests"]
    except Exception as e:
        details.append({
            "item": "Read original data",
            "score": 0,
            "max_score": 30,
            "passed": False,
            "reason": f"Cannot read data files: {str(e)}"
        })
        total_score += 0
        write_result(details, total_score)
        return

    # 构建 asset_id -> asset 映射
    asset_map = {a["asset_id"]: a for a in assets_data}
    # 构建正确答案：pending 且目标资产存在 且 read_policy==unpublished 且 asset_type in (finance_archive, technical_plan)
    correct_ids = set()
    for req in requests_data:
        if req["status"] != "pending":
            continue
        target = asset_map.get(req["target_asset_id"])
        if target is None:
            continue
        if target["read_policy"] == "unpublished" and target["asset_type"] in ("finance_archive", "technical_plan"):
            correct_ids.add(req["request_id"])

    # 4. 比对答案 (40分)
    agent_set = set(deny_list)
    expected_set = correct_ids

    # 准确度：完全匹配得30分，每多一个或少一个扣5分（最多扣30）
    false_positives = agent_set - expected_set
    false_negatives = expected_set - agent_set
    penalty = (len(false_positives) + len(false_negatives)) * 5
    match_score = max(0, 30 - penalty)

    details.append({
        "item": "Correct deny list content",
        "score": match_score,
        "max_score": 30,
        "passed": match_score == 30,
        "reason": f"Expected {sorted(expected_set)}, got {sorted(agent_set)}. "
                  f"False positives: {sorted(false_positives)}, false negatives: {sorted(false_negatives)}"
    })
    total_score += match_score

    # 5. 额外细节：列表无重复，格式整洁 (10分)
    if len(agent_set) == len(deny_list):
        details.append({
            "item": "No duplicate entries",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "List has no duplicates"
        })
        total_score += 10
    else:
        details.append({
            "item": "No duplicate entries",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"List contains {len(deny_list) - len(agent_set)} duplicate(s)"
        })

    # 总分
    write_result(details, total_score)

def write_result(details, total_score):
    result = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
