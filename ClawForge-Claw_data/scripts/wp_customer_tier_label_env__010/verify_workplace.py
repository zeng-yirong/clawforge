import sys, json, os
from pathlib import Path

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    ws = Path(workspace)
    score = 0
    details = []
    max_total = 100

    # 1. 检查结果文件是否存在 (10分)
    result_path = ws / "ops" / "customer_tier_update.json"
    if result_path.exists():
        score += 10
        details.append({"item": "结果文件存在", "score": 10, "max_score": 10, "passed": True, "reason": "ops/customer_tier_update.json 存在"})
    else:
        details.append({"item": "结果文件存在", "score": 0, "max_score": 10, "passed": False, "reason": "ops/customer_tier_update.json 不存在"})
        # 后续检查无法进行，直接写分数
        _write_score(score, details, ws)
        return

    # 2. 文件内容为合法JSON (10分)
    try:
        with open(result_path, "r") as f:
            data = json.load(f)
        if isinstance(data, list):
            score += 10
            details.append({"item": "JSON格式合法且为列表", "score": 10, "max_score": 10, "passed": True, "reason": "JSON解析成功，类型为列表"})
        else:
            details.append({"item": "JSON格式合法且为列表", "score": 0, "max_score": 10, "passed": False, "reason": "JSON内容不是列表"})
            _write_score(score, details, ws)
            return
    except Exception as e:
        details.append({"item": "JSON格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON解析失败: {str(e)}"})
        _write_score(score, details, ws)
        return

    # 3. 检查每个客户记录是否包含customer_id和labels字段 (10分)
    required_fields = {"customer_id", "labels"}
    all_have_fields = True
    for item in data:
        if not isinstance(item, dict) or not required_fields.issubset(item.keys()):
            all_have_fields = False
            break
    if all_have_fields and len(data) > 0:
        score += 10
        details.append({"item": "每条记录包含customer_id和labels", "score": 10, "max_score": 10, "passed": True, "reason": "所有记录字段正确"})
    else:
        details.append({"item": "每条记录包含customer_id和labels", "score": 0, "max_score": 10, "passed": False, "reason": "存在缺失字段的记录"})
        _write_score(score, details, ws)
        return

    # 4. 检查是否包含了所有5个客户，不多不少 (20分)
    expected_ids = {"C001", "C002", "C003", "C004", "C005"}
    found_ids = {item["customer_id"] for item in data}
    if found_ids == expected_ids:
        score += 20
        details.append({"item": "包含所有5个客户，无多余", "score": 20, "max_score": 20, "passed": True, "reason": f"客户ID集合 = {sorted(found_ids)}"})
    elif found_ids.issuperset(expected_ids):
        score += 10
        details.append({"item": "包含所有5个客户，但有多余", "score": 10, "max_score": 20, "passed": False, "reason": f"多余客户: {sorted(found_ids - expected_ids)}"})
    elif found_ids.issubset(expected_ids):
        score += 10
        details.append({"item": "包含所有5个客户，但缺少部分", "score": 10, "max_score": 20, "passed": False, "reason": f"缺少客户: {sorted(expected_ids - found_ids)}"})
    else:
        details.append({"item": "包含所有5个客户", "score": 0, "max_score": 20, "passed": False, "reason": f"客户ID集合不匹配, 应为{expected_ids}, 实际为{found_ids}"})

    # 5. 检查每个客户的labels是否正确 (50分, 每个客户10分)
    # 预期标签（根据规则）
    expected_labels = {
        "C001": ["gold"],
        "C002": ["silver"],
        "C003": ["bronze"],
        "C004": ["gold"],
        "C005": ["bronze"]
    }
    label_score = 0
    for item in data:
        cid = item["customer_id"]
        labels = item["labels"]
        expected = expected_labels.get(cid)
        if expected is None:
            continue  # 不应该出现，但前面已检查
        if labels == expected:
            label_score += 10
            details.append({"item": f"客户{cid}标签正确", "score": 10, "max_score": 10, "passed": True, "reason": f"标签为{expected}"})
        else:
            details.append({"item": f"客户{cid}标签正确", "score": 0, "max_score": 10, "passed": False, "reason": f"期望{expected}, 实际{labels}"})
    score += label_score

    # 写入分数文件
    _write_score(score, details, ws)

def _write_score(score, details, ws):
    output = {
        "total_score": score,
        "details": details
    }
    with open(ws / "workplace_score.json", "w") as f:
        json.dump(output, f, indent=2)
    print(f"Score: {score}/100")

if __name__ == "__main__":
    verify()
