import json
import os
import sys

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0

    # 1. 检查产物文件是否存在
    record_path = os.path.join(workspace, "ops", "diff_record.json")
    if os.path.exists(record_path):
        score_details.append({
            "item": "产物文件 ops/diff_record.json 存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "文件已找到"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "产物文件 ops/diff_record.json 存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件不存在"
        })
        # 后续检查无法进行，直接输出
        _write_score(workspace, total_score, score_details)
        return

    # 2. 解析 JSON 合法性
    try:
        with open(record_path, "r") as f:
            data = json.load(f)
        score_details.append({
            "item": "JSON 格式合法",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "成功解析为 JSON"
        })
        total_score += 10
    except (json.JSONDecodeError, Exception) as e:
        score_details.append({
            "item": "JSON 格式合法",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON 解析失败: {str(e)}"
        })
        _write_score(workspace, total_score, score_details)
        return

    # 3. 检查顶层结构（必须包含 control 和 treatment）
    expected_groups = {"control", "treatment"}
    if not isinstance(data, dict):
        score_details.append({
            "item": "顶层为字典",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "顶层不是字典"
        })
        total_score += 0
    else:
        actual_keys = set(data.keys())
        if expected_groups.issubset(actual_keys):
            score_details.append({
                "item": "包含 control 和 treatment 两组",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": f"键: {actual_keys}"
            })
            total_score += 10
        else:
            missing = expected_groups - actual_keys
            score_details.append({
                "item": "包含 control 和 treatment 两组",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"缺少: {missing}, 现有: {actual_keys}"
            })

    # 4. 检查每组内字段（accuracy_diff, latency_diff, cost_diff）
    expected_fields = {"accuracy_diff", "latency_diff", "cost_diff"}
    groups = ["control", "treatment"]
    all_fields_ok = True
    for grp in groups:
        grp_data = data.get(grp)
        if not isinstance(grp_data, dict):
            score_details.append({
                "item": f"组 {grp} 为字典",
                "score": 0,
                "max_score": 5,
                "passed": False,
                "reason": f"{grp} 的值不是字典"
            })
            all_fields_ok = False
            continue
        fields_present = set(grp_data.keys())
        if not expected_fields.issubset(fields_present):
            missing_f = expected_fields - fields_present
            score_details.append({
                "item": f"组 {grp} 包含所需差异字段",
                "score": 0,
                "max_score": 5,
                "passed": False,
                "reason": f"缺少字段: {missing_f}"
            })
            all_fields_ok = False
        else:
            # 检查额外字段（视为扣分项）
            extra = fields_present - expected_fields
            if extra:
                reason = f"存在额外字段 {extra}，但暂时不扣分（仅警告）"
            else:
                reason = "字段完整"
            score_details.append({
                "item": f"组 {grp} 包含所需差异字段",
                "score": 5,
                "max_score": 5,
                "passed": True,
                "reason": reason
            })
            total_score += 5

    if not all_fields_ok:
        # 字段不足，后面数值检查跳过
        _write_score(workspace, total_score, score_details)
        return

    # 5. 数值精确性（每个指标 10 分，共 6 个指标 = 60 分）
    # 预期值（batch_002 - batch_001）
    expected = {
        "control": {
            "accuracy_diff": 0.02,
            "latency_diff": -10.0,
            "cost_diff": -0.05
        },
        "treatment": {
            "accuracy_diff": 0.02,
            "latency_diff": -15.0,
            "cost_diff": -0.05
        }
    }
    all_numerical_ok = True
    for grp in groups:
        for field in expected_fields:
            actual_val = data[grp][field]
            exp_val = expected[grp][field]
            if abs(actual_val - exp_val) > 1e-6:
                all_numerical_ok = False
                score_details.append({
                    "item": f"{grp}.{field} 数值正确",
                    "score": 0,
                    "max_score": 10,
                    "passed": False,
                    "reason": f"期望 {exp_val}, 实际 {actual_val}"
                })
            else:
                score_details.append({
                    "item": f"{grp}.{field} 数值正确",
                    "score": 10,
                    "max_score": 10,
                    "passed": True,
                    "reason": f"值 {actual_val} 符合预期"
                })
                total_score += 10

    _write_score(workspace, total_score, score_details)


def _write_score(workspace, total, details):
    output = {
        "total_score": total,
        "details": details
    }
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"Score written to {score_path}, total={total}")


if __name__ == "__main__":
    main()
