import sys
import json
import os

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    # 1. 检查 ops/resolution.json 是否存在 (20分)
    resolution_path = os.path.join(workspace, "ops", "resolution.json")
    if os.path.exists(resolution_path):
        details.append({
            "item": "ops/resolution.json 文件存在",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "文件存在"
        })
        score += 20
    else:
        details.append({
            "item": "ops/resolution.json 文件存在",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "文件不存在"
        })
        # 文件不存在则后续检查无意义，直接输出结果
        result = {"total_score": score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # 2. JSON 合法性检查 (10分)
    try:
        with open(resolution_path, "r") as f:
            data = json.load(f)
        details.append({
            "item": "JSON 格式合法",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "成功解析"
        })
        score += 10
    except Exception as e:
        details.append({
            "item": "JSON 格式合法",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"解析失败: {str(e)}"
        })
        result = {"total_score": score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # 3. 数据类型检查 (必须是列表) (10分)
    if isinstance(data, list):
        details.append({
            "item": "根元素类型为列表",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"类型正确，长度为 {len(data)}"
        })
        score += 10
    else:
        details.append({
            "item": "根元素类型为列表",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"类型为 {type(data).__name__}"
        })

    # 4. 检查列表长度是否为 2 (25分)
    expected_len = 2
    if len(data) == expected_len:
        details.append({
            "item": "条目数量正确",
            "score": 25,
            "max_score": 25,
            "passed": True,
            "reason": f"包含 {expected_len} 个条目"
        })
        score += 25
    else:
        details.append({
            "item": "条目数量正确",
            "score": 0,
            "max_score": 25,
            "passed": False,
            "reason": f"实际 {len(data)} 个，期望 {expected_len} 个"
        })

    # 5. 检查是否包含预期 incident_id 列表 (25分)
    expected_ids = {"INC-001", "INC-002"}
    actual_ids = {entry.get("incident_id") for entry in data if isinstance(entry, dict)}
    if expected_ids == actual_ids:
        details.append({
            "item": "包含正确的 incident_id",
            "score": 25,
            "max_score": 25,
            "passed": True,
            "reason": f"包含 {sorted(expected_ids)}"
        })
        score += 25
    else:
        missing = expected_ids - actual_ids
        extra = actual_ids - expected_ids
        reason_parts = []
        if missing:
            reason_parts.append(f"缺失: {sorted(missing)}")
        if extra:
            reason_parts.append(f"多余: {sorted(extra)}")
        details.append({
            "item": "包含正确的 incident_id",
            "score": 0,
            "max_score": 25,
            "passed": False,
            "reason": "; ".join(reason_parts) if reason_parts else "id 字段缺失"
        })

    # 6. 检查每个条目的 action 是否为 "remediate" (10分)
    action_ok = all(
        isinstance(entry, dict) and entry.get("action") == "remediate"
        for entry in data
    )
    if action_ok:
        details.append({
            "item": "所有 action 字段值为 'remediate'",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"全部 {len(data)} 条记录 action 正确"
        })
        score += 10
    else:
        # 统计哪些条目 action 不对
        bad = [str(entry) for entry in data if not (isinstance(entry, dict) and entry.get("action") == "remediate")]
        details.append({
            "item": "所有 action 字段值为 'remediate'",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"错误的条目: {bad}"
        })

    # 总分写入
    result = {
        "total_score": score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
