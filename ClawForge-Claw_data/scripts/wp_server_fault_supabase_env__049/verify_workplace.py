import sys
import os
import json

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    # 1. 目录结构检查 (10分)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        score += 10
        details.append({"item": "目录 ops/ 存在", "score": 10, "max_score": 10, "passed": True, "reason": "ops目录已创建"})
    else:
        details.append({"item": "目录 ops/ 存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到ops目录"})

    # 2. 文件格式合法性 (10分)
    target_file = os.path.join(ops_dir, "screened_incidents.json")
    if not os.path.isfile(target_file):
        details.append({"item": "ops/screened_incidents.json 存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        # 无法继续，直接返回
        total_score = score  # 只有目录分
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f)
        return

    try:
        with open(target_file, "r") as f:
            data = json.load(f)
        if isinstance(data, list):
            details.append({"item": "JSON文件格式合法且为数组", "score": 10, "max_score": 10, "passed": True, "reason": "正确解析JSON数组"})
            score += 10
        else:
            details.append({"item": "JSON文件格式合法且为数组", "score": 0, "max_score": 10, "passed": False, "reason": "顶层不是数组"})
            # 仍然继续检查内容，但格式分扣掉
    except json.JSONDecodeError:
        details.append({"item": "JSON文件格式合法", "score": 0, "max_score": 10, "passed": False, "reason": "JSON解析失败"})
        # 需写结果并退出
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": score, "details": details}, f)
        return

    # 3. 筛选准确性 (30分) —— 排除干扰项，只保留目标5条
    # 预期结果：只有5条，分别是INC-0101到INC-0105，每条包含incident_id和severity
    expected_ids = ["INC-0101", "INC-0102", "INC-0103", "INC-0104", "INC-0105"]
    expected_severity = {"INC-0101": "critical", "INC-0102": "high", "INC-0103": "medium", "INC-0104": "critical", "INC-0105": "high"}

    actual_ids = [item.get("incident_id") for item in data if "incident_id" in item]
    actual_set = set(actual_ids)
    expected_set = set(expected_ids)

    if actual_set == expected_set:
        score += 30
        details.append({"item": "筛选结果集合与预期一致", "score": 30, "max_score": 30, "passed": True, "reason": f"包含且仅包含目标工单: {expected_ids}"})
    else:
        # 部分正确或多了/少了
        extra = actual_set - expected_set
        missing = expected_set - actual_set
        if len(extra) == 0 and len(missing) == 0:
            # 虽然集合相等但顺序可能不同，上面已处理，这里备选
            pass
        else:
            # 按缺失和多余比例给分
            missing_count = len(missing)
            extra_count = len(extra)
            # 最多扣30分，每个错误扣6分
            penalty = (missing_count + extra_count) * 6
            partial = max(0, 30 - penalty)
            score += partial
            reason = f"缺少 {missing_count} 条: {missing}, 多余 {extra_count} 条: {extra}"
            details.append({"item": "筛选结果集合与预期一致", "score": partial, "max_score": 30, "passed": partial == 30, "reason": reason})

    # 4. 关键字段正确性 (50分) —— 每条记录必须有incident_id和severity，且severity值正确
    field_score = 0
    field_max = 50
    # 每一条正确记录10分，共5条50分
    for item in data:
        if not isinstance(item, dict):
            continue
        iid = item.get("incident_id")
        sev = item.get("severity")
        if iid in expected_severity:
            if sev == expected_severity[iid]:
                field_score += 10
            else:
                # severity错误扣一半分（5分）
                field_score += 5
        else:
            # 如果出现了多余的工单，但字段正确，不加分也不扣分（已在集合检查中扣过）
            pass
    score += field_score
    details.append({"item": "每个工单的severity字段正确", "score": field_score, "max_score": field_max, "passed": field_score == field_max, "reason": f"字段正确性得分 {field_score}/{field_max}"})

    # 写入结果
    total_score = min(100, score)  # 防止溢出
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2)

if __name__ == "__main__":
    verify()
