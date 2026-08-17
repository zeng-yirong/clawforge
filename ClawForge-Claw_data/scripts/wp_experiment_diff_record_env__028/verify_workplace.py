import sys
import os
import json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0

    # 1. 检查 ops 目录是否存在 (10分)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        score_details.append({
            "item": "ops 目录存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "ops 目录已创建"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "ops 目录存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ops 目录不存在"
        })

    # 2. 检查 diff_record.json 是否存在且为合法 JSON 列表 (10分)
    json_path = os.path.join(ops_dir, "diff_record.json")
    if os.path.isfile(json_path):
        try:
            with open(json_path, "r") as f:
                data = json.load(f)
            if isinstance(data, list):
                score_details.append({
                    "item": "diff_record.json 存在且为列表",
                    "score": 10,
                    "max_score": 10,
                    "passed": True,
                    "reason": "文件存在，JSON 解析成功，根对象为列表"
                })
                total_score += 10
            else:
                score_details.append({
                    "item": "diff_record.json 存在且为列表",
                    "score": 0,
                    "max_score": 10,
                    "passed": False,
                    "reason": "JSON 根对象不是列表"
                })
        except json.JSONDecodeError:
            score_details.append({
                "item": "diff_record.json 存在且为列表",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": "JSON 解析失败"
            })
    else:
        score_details.append({
            "item": "diff_record.json 存在且为列表",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件不存在"
        })

    # 如果文件不存在，则后续检查跳过
    if not os.path.isfile(json_path):
        _write_score(workspace, total_score, score_details)
        return

    # 3. 检查每条记录是否包含所有必需字段 (10分)
    required_fields = [
        "group_id",
        "batch_001_accuracy", "batch_002_accuracy", "accuracy_diff",
        "batch_001_latency_ms", "batch_002_latency_ms", "latency_diff",
        "batch_001_cost_usd", "batch_002_cost_usd", "cost_diff"
    ]
    field_ok = True
    for idx, rec in enumerate(data):
        for field in required_fields:
            if field not in rec:
                field_ok = False
                break
        if not field_ok:
            break

    if field_ok and len(data) > 0:
        score_details.append({
            "item": "每条记录包含所有必需字段",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"共 {len(data)} 条记录，字段完整"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "每条记录包含所有必需字段",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "缺少必需字段或列表为空"
        })

    # 4. 排除脏数据，只保留符合条件的 group (20分)
    expected_groups = {"A"}
    actual_groups = set(rec.get("group_id") for rec in data)
    if actual_groups == expected_groups:
        score_details.append({
            "item": "只包含符合条件的 group（排除脏数据）",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "没有包含脏数据行对应的 group (D/E/F) 或未达标的 group (B/C)"
        })
        total_score += 20
    elif "D" in actual_groups or "E" in actual_groups or "F" in actual_groups:
        score_details.append({
            "item": "只包含符合条件的 group（排除脏数据）",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"包含了脏数据对应的 group: {actual_groups & {'D','E','F'}}"
        })
    elif actual_groups != expected_groups:
        extra = actual_groups - expected_groups
        missing = expected_groups - actual_groups
        reason = ""
        if extra:
            reason += f"包含多余 group: {extra}; "
        if missing:
            reason += f"缺少预期 group: {missing}"
        score_details.append({
            "item": "只包含符合条件的 group（排除脏数据）",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": reason.strip("; ")
        })

    # 5. 关键计算验证 (50分)
    rec_a = None
    for rec in data:
        if rec.get("group_id") == "A":
            rec_a = rec
            break

    if rec_a is not None:
        expected = {
            "batch_001_accuracy": 0.80,
            "batch_002_accuracy": 0.87,
            "accuracy_diff": 0.07,
            "batch_001_latency_ms": 100.0,
            "batch_002_latency_ms": 95.0,
            "latency_diff": -5.0,
            "batch_001_cost_usd": 0.10,
            "batch_002_cost_usd": 0.12,
            "cost_diff": 0.02
        }
        all_correct = True
        for key, val in expected.items():
            got = rec_a.get(key)
            if got is None or abs(got - val) > 1e-6:
                all_correct = False
                break
        if all_correct:
            score_details.append({
                "item": "group A 的指标计算准确",
                "score": 50,
                "max_score": 50,
                "passed": True,
                "reason": "所有数值与预期一致（容差 1e-6）"
            })
            total_score += 50
        else:
            score_details.append({
                "item": "group A 的指标计算准确",
                "score": 0,
                "max_score": 50,
                "passed": False,
                "reason": "存在数值错误，请检查计算逻辑"
            })
    else:
        score_details.append({
            "item": "group A 的指标计算准确",
            "score": 0,
            "max_score": 50,
            "passed": False,
            "reason": "未找到 group A 的记录"
        })

    # 写入最终评分
    _write_score(workspace, total_score, score_details)

def _write_score(workspace, total_score, details):
    output = {
        "total_score": total_score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(output, f)

if __name__ == "__main__":
    main()
