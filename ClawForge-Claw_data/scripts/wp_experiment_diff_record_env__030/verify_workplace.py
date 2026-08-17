import sys
import os
import json
import math

def verify(workspace):
    details = []
    total_score = 0
    max_total = 100

    # 1. 检查目录 ops 是否存在 (10分)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        details.append({
            "item": "ops directory exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "ops/ directory found"
        })
        total_score += 10
    else:
        details.append({
            "item": "ops directory exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ops/ directory missing"
        })
        # 如果目录都不存在，直接结束，后续没意义
        output = {"total_score": 0, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(output, f, indent=2)
        return

    # 2. 文件 ops/diff_record.json 是否存在 (10分)
    json_path = os.path.join(ops_dir, "diff_record.json")
    if not os.path.isfile(json_path):
        details.append({
            "item": "ops/diff_record.json exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "file not found"
        })
        output = {"total_score": total_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(output, f, indent=2)
        return
    else:
        details.append({
            "item": "ops/diff_record.json exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "file found"
        })
        total_score += 10

    # 3. JSON 格式合法性 (10分)
    try:
        with open(json_path, "r") as f:
            data = json.load(f)
        details.append({
            "item": "JSON format valid",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "valid JSON"
        })
        total_score += 10
    except Exception as e:
        details.append({
            "item": "JSON format valid",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"invalid JSON: {str(e)}"
        })
        # 不终止，仍可尝试解析？但后面都会失败，直接写分结束
        output = {"total_score": total_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(output, f, indent=2)
        return

    # 4. 数据结构：必须是一个列表 (10分)
    if not isinstance(data, list):
        details.append({
            "item": "data is a list",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"expected list, got {type(data).__name__}"
        })
        total_score += 0
    else:
        details.append({
            "item": "data is a list",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "correct type"
        })
        total_score += 10

    # 5. 每个元素必须包含 group_id 和 delta_accuracy (10分)
    field_ok = True
    for i, item in enumerate(data):
        if not isinstance(item, dict) or "group_id" not in item or "delta_accuracy" not in item:
            field_ok = False
            break
    if field_ok:
        details.append({
            "item": "each entry has group_id and delta_accuracy",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"all {len(data)} entries have required fields"
        })
        total_score += 10
    else:
        details.append({
            "item": "each entry has group_id and delta_accuracy",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "some entries missing fields"
        })

    # 6. 预期的组数量应为 3（group-A, group-B, group-C），且不能有其他组 (20分)
    expected_groups = {"group-A", "group-B", "group-C"}
    found_groups = set()
    for item in data:
        found_groups.add(item["group_id"])
    extra_groups = found_groups - expected_groups
    missing_groups = expected_groups - found_groups
    if not extra_groups and not missing_groups:
        details.append({
            "item": "correct set of groups (A, B, C only)",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "exactly group-A, group-B, group-C present"
        })
        total_score += 20
    else:
        reason_parts = []
        if extra_groups:
            reason_parts.append(f"unexpected groups: {extra_groups}")
        if missing_groups:
            reason_parts.append(f"missing groups: {missing_groups}")
        details.append({
            "item": "correct set of groups (A, B, C only)",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "; ".join(reason_parts)
        })

    # 7. 检查每个组的 delta_accuracy 准确值 (共30分，每个10分)
    # 根据 env_builder 生成的数据：
    #   batch-001: group-A=0.85, group-B=0.90, group-C=0.88
    #   batch-002: group-A=0.87, group-B=0.92, group-C=0.84
    # 差值 (batch_002 - batch_001): group-A=0.02, group-B=0.02, group-C=-0.04
    expected_deltas = {
        "group-A": 0.02,
        "group-B": 0.02,
        "group-C": -0.04,
    }
    # 构建查找字典
    delta_map = {item["group_id"]: item["delta_accuracy"] for item in data}
    for gid, expected_val in expected_deltas.items():
        if gid not in delta_map:
            details.append({
                "item": f"delta_accuracy for {gid}",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": "group not found in output"
            })
            continue
        actual = delta_map[gid]
        # 允许浮点误差 1e-6
        if abs(actual - expected_val) < 1e-6:
            details.append({
                "item": f"delta_accuracy for {gid}",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": f"expected {expected_val}, got {actual}"
            })
            total_score += 10
        else:
            details.append({
                "item": f"delta_accuracy for {gid}",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"expected {expected_val}, got {actual}"
            })

    # 确保总分不超过100
    if total_score > max_total:
        total_score = max_total

    # 输出评分结果
    output = {
        "total_score": total_score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(output, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
