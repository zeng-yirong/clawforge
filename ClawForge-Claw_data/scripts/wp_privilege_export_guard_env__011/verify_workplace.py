import json
import os
import sys

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    # 10分: 检查 ops/deny_list.json 是否存在
    deny_path = os.path.join(workspace, "ops/deny_list.json")
    if os.path.isfile(deny_path):
        details.append({"item": "ops/deny_list.json 存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
        score += 10
    else:
        details.append({"item": "ops/deny_list.json 存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        # 后续检查依赖此文件，若不存在直接结束
        write_score(score, details)
        return

    # 10分: JSON 格式合法
    try:
        with open(deny_path, "r") as f:
            data = json.load(f)
        details.append({"item": "JSON 格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "解析成功"})
        score += 10
    except (json.JSONDecodeError, Exception) as e:
        details.append({"item": "JSON 格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {e}"})
        write_score(score, details)
        return

    # 10分: 必须是 list
    if isinstance(data, list):
        details.append({"item": "顶层结构是列表", "score": 10, "max_score": 10, "passed": True, "reason": "类型正确"})
        score += 10
    else:
        details.append({"item": "顶层结构是列表", "score": 0, "max_score": 10, "passed": False, "reason": f"类型为 {type(data).__name__}, 期望 list"})
        write_score(score, details)
        return

    # 10分: 每个元素包含 request_id 和 reason
    all_have_fields = True
    for item in data:
        if not isinstance(item, dict) or "request_id" not in item or "reason" not in item:
            all_have_fields = False
            break
    if all_have_fields:
        details.append({"item": "每个条目包含 request_id 和 reason", "score": 10, "max_score": 10, "passed": True, "reason": "字段完整"})
        score += 10
    else:
        details.append({"item": "每个条目包含 request_id 和 reason", "score": 0, "max_score": 10, "passed": False, "reason": "存在缺失字段的条目"})

    # 30分: 必须包含所有违规请求 (req01, req03, req04) 且不包含合法请求
    # 先加载原始数据重建预期
    try:
        with open(os.path.join(workspace, "data/accounts.json")) as f:
            accounts_data = json.load(f)
        with open(os.path.join(workspace, "data/assets/assets.json")) as f:
            assets_data = json.load(f)
        with open(os.path.join(workspace, "data/requests/requests.json")) as f:
            requests_data = json.load(f)
    except Exception as e:
        details.append({"item": "检查数据基础文件", "score": 0, "max_score": 30, "passed": False, "reason": f"无法读取原始数据: {e}"})
        write_score(score, details)
        return

    # 构建权限映射
    perm_map = {acc["account_id"]: set(acc["permissions"]) for acc in accounts_data["accounts"]}
    # 构建资产映射
    asset_map = {ast["asset_id"]: ast["read_policy"] for ast in assets_data["assets"]}

    # 预期违规请求
    expected_violations = set()
    for req in requests_data["requests"]:
        actor_id = req["actor_name"]  # 注意 actor_name 是 display_name? 但我们accounts里 display_name 与 actor_name 一致
        # 需要找到 account_id 对应 display_name
        target_asset = req["target_asset_id"]
        read_policy = asset_map.get(target_asset)
        if read_policy is None:
            continue
        # 找到 account 的 permissions
        actor_perms = None
        for acc in accounts_data["accounts"]:
            if acc["display_name"] == actor_id:
                actor_perms = set(acc["permissions"])
                break
        if actor_perms is None:
            continue
        if read_policy not in actor_perms:
            expected_violations.add(req["request_id"])

    # 从 agent 输出中提取 request_id 集合
    agent_ids = {item["request_id"] for item in data}

    # 计算误判和遗漏
    false_positives = agent_ids - expected_violations
    false_negatives = expected_violations - agent_ids

    violation_score = 30
    if false_positives or false_negatives:
        # 每个错误扣 10 分，最多扣完
        penalty = 10 * (len(false_positives) + len(false_negatives))
        if penalty > 30:
            penalty = 30
        violation_score = 30 - penalty
        reason_parts = []
        if false_positives:
            reason_parts.append(f"误判: {sorted(false_positives)}")
        if false_negatives:
            reason_parts.append(f"遗漏: {sorted(false_negatives)}")
        details.append({"item": "违规请求识别准确", "score": violation_score, "max_score": 30, "passed": violation_score == 30, "reason": "; ".join(reason_parts)})
    else:
        details.append({"item": "违规请求识别准确", "score": 30, "max_score": 30, "passed": True, "reason": "完全正确"})
    score += violation_score

    # 20分: 不得有多余的 request_id 重复（即每个请求只出现一次）
    ids_list = [item["request_id"] for item in data]
    if len(ids_list) == len(set(ids_list)):
        details.append({"item": "无重复 request_id", "score": 20, "max_score": 20, "passed": True, "reason": "所有ID唯一"})
        score += 20
    else:
        duplicates = [x for x in ids_list if ids_list.count(x) > 1]
        details.append({"item": "无重复 request_id", "score": 0, "max_score": 20, "passed": False, "reason": f"发现重复: {set(duplicates)}"})

    write_score(score, details)

def write_score(score, details):
    result = {
        "total_score": score,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"Total score: {score}")

if __name__ == "__main__":
    main()
