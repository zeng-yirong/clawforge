import sys
import os
import json

def check(result_path):
    errors = []
    details = []
    total = 0

    # 1. 目录结构检查 (10分)
    ops_dir = os.path.join(result_path, "ops")
    target_file = os.path.join(result_path, "ops", "acknowledge_list.json")
    if not os.path.isdir(ops_dir):
        details.append({"item": "ops 目录存在", "score": 0, "max_score": 10, "passed": False, "reason": "ops 目录不存在"})
        # 若目录不存在，后续无法检查文件，直接返回
        return {"total_score": 0, "details": details}
    else:
        details.append({"item": "ops 目录存在", "score": 10, "max_score": 10, "passed": True, "reason": "ops 目录已创建"})
        total += 10

    # 2. 文件存在性 (10分)
    if not os.path.isfile(target_file):
        details.append({"item": "acknowledge_list.json 存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件未找到"})
        return {"total_score": total, "details": details}
    else:
        details.append({"item": "acknowledge_list.json 存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件已创建"})
        total += 10

    # 3. JSON 合法性 (10分)
    try:
        with open(target_file, "r") as f:
            data = json.load(f)
        details.append({"item": "JSON 格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 解析成功"})
        total += 10
    except (json.JSONDecodeError, ValueError) as e:
        details.append({"item": "JSON 格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析失败: {e}"})
        return {"total_score": total, "details": details}

    # 4. 数据类型：必须是列表 (10分)
    if not isinstance(data, list):
        details.append({"item": "根元素是数组", "score": 0, "max_score": 10, "passed": False, "reason": "根元素不是数组"})
        return {"total_score": total, "details": details}
    else:
        details.append({"item": "根元素是数组", "score": 10, "max_score": 10, "passed": True, "reason": "数据类型正确"})
        total += 10

    # 5. 长度检查 (20分) — 正确答案应包含2个 alert_id
    expected_ids = {"ALERT-003", "ALERT-007"}  # 注意：干扰项 ALERT-005 也是 new，但 ALERT-005 的 door_id 是 door-office，且没有重复；实际应包含 ALERT-003, ALERT-005, ALERT-007？等一下，需要确认答案唯一性。
    # 重新检查 builder：ALERT-003 (new), ALERT-005 (new), ALERT-007 (new) 共三个？ ALERT-005 也是 new! 之前列表有 ALERT-005 status new。所以答案应该是三个：003,005,007。但为了区分干扰，考虑 ALERT-005 也可能是合理的。需要调整 builder 让答案唯一。
    # 为了避免设计失误，我们调整期望：确保只有两个 new：去掉 ALERT-005 或改为 acknowledged。在 builder 中已包含 ALERT-005 为 new，需要修改。
    # 这里假设 builder 已经修正：将 ALERT-005 改为 acknowledged。我们按修正后的期望写。
    # 实际上在输出前需要同步修正 builder，但根据推理，我们在这里设定期望为两个：003,007。
    # 但为了严谨，我们动态计算：从原始 alerts.json 中读取 status==new 的唯一 alert_id。
    # 这样更灵活，也符合验证逻辑：verifier 不应硬编码 ID，而应该从初始数据推导。但 verifier 可以读取初始文件。
    # 更好的做法：verifier 先读取 builder 铺出的 alerts.json，过滤出 status=='new' 的 alert_id（去重后），然后与 agent 输出的列表比对。
    # 这样即使 builder 变化，verifier 依然正确。下面我们实现动态推导。

    # 读取初始警报文件
    initial_alerts_path = os.path.join(result_path, "data", "alerts", "alerts.json")
    if not os.path.isfile(initial_alerts_path):
        details.append({"item": "数据源存在", "score": 0, "max_score": 0, "passed": False, "reason": "无法找到初始警报文件"})
        return {"total_score": total, "details": details}
    with open(initial_alerts_path, "r") as f:
        initial_alerts = json.load(f)

    # 收集所有 status=='new' 的 alert_id（按最后一次出现去重，保留顺序）
    seen = set()
    expected_new_ids = []
    for alert in initial_alerts:
        if alert.get("status") == "new" and alert["alert_id"] not in seen:
            seen.add(alert["alert_id"])
            expected_new_ids.append(alert["alert_id"])
    # 注意：有重复 ALERT-003 一个 new 一个 acknowledged，我们只取 status=new 的。
    expected_new_ids.sort()  # 排序以保证比较顺序

    actual_ids = []
    for item in data:
        if isinstance(item, dict) and "alert_id" in item:
            actual_ids.append(item["alert_id"])
    actual_ids.sort()

    if actual_ids == expected_new_ids:
        details.append({"item": "列表内容正确", "score": 20, "max_score": 20, "passed": True, "reason": f"包含正确的 alert_id: {expected_new_ids}"})
        total += 20
    else:
        details.append({"item": "列表内容正确", "score": 0, "max_score": 20, "passed": False, "reason": f"预期 {expected_new_ids}，实际 {actual_ids}"})
        # 不提前返回，继续检查部分得分

    # 6. 每个元素必须包含 alert_id 字段 (10分)
    all_have_id = all(isinstance(item, dict) and "alert_id" in item for item in data)
    if all_have_id:
        details.append({"item": "每个元素含 alert_id", "score": 10, "max_score": 10, "passed": True, "reason": "所有元素均有 alert_id"})
        total += 10
    else:
        details.append({"item": "每个元素含 alert_id", "score": 0, "max_score": 10, "passed": False, "reason": "存在缺少 alert_id 的元素"})

    # 7. 没有多余字段验证 (10分) — 仅允许 alert_id 字段，其他字段可选但不扣分（不强制）
    # 实际上 agent 可能加其他字段，不扣分。所以这里给满分。
    details.append({"item": "无多余约束", "score": 10, "max_score": 10, "passed": True, "reason": "允许额外字段"})
    total += 10

    # 总分 sum
    return {"total_score": total, "details": details}

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = check(workspace)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(score, f, indent=2)
    print(f"Score: {score['total_score']}/100")
