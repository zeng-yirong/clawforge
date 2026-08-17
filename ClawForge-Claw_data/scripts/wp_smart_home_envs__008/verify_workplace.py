import sys
import json
import os
from pathlib import Path

def verify(workspace: str):
    details = []
    total_score = 0

    # 期望结果（与 builder 数据严格一致）
    expected_conflicts = [
        {"device_id": "humidifier_bedroom_01", "conflict_type": "humidity_too_high"},
        {"device_id": "humidifier_living_01", "conflict_type": "humidity_too_low"}
    ]

    # 1. 检查 ops/conflicts.json 是否存在
    result_path = Path(workspace) / "ops" / "conflicts.json"
    if result_path.exists():
        details.append({
            "item": "ops/conflicts.json 存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "文件存在"
        })
        total_score += 10
    else:
        details.append({
            "item": "ops/conflicts.json 存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件不存在"
        })
        # 继续检查其他项，但后续依赖文件
        details.append({"item": "JSON 格式合法", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        details.append({"item": "冲突列表长度正确", "score": 0, "max_score": 20, "passed": False, "reason": "文件不存在"})
        details.append({"item": "冲突设备 ID 正确", "score": 0, "max_score": 30, "passed": False, "reason": "文件不存在"})
        details.append({"item": "冲突类型正确", "score": 0, "max_score": 20, "passed": False, "reason": "文件不存在"})
        details.append({"item": "无多余记录", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        total = sum(d["score"] for d in details)
        with open(Path(workspace) / "workplace_score.json", "w") as f:
            json.dump({"total_score": total, "details": details}, f, indent=2)
        return

    # 2. JSON 格式合法
    try:
        with open(result_path, "r") as f:
            data = json.load(f)
        details.append({
            "item": "JSON 格式合法",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "合法 JSON"
        })
        total_score += 10
    except Exception as e:
        details.append({
            "item": "JSON 格式合法",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"解析错误: {e}"
        })
        # 后续无法判断，直接返回
        total = total_score
        with open(Path(workspace) / "workplace_score.json", "w") as f:
            json.dump({"total_score": total, "details": details}, f, indent=2)
        return

    # 3. 必须是列表
    if not isinstance(data, list):
        details.append({
            "item": "冲突列表长度正确",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "根元素不是列表"
        })
        total = total_score
        # 继续检查后面的会出错，直接返回
        details.append({"item": "冲突设备 ID 正确", "score": 0, "max_score": 30, "passed": False, "reason": "格式错误"})
        details.append({"item": "冲突类型正确", "score": 0, "max_score": 20, "passed": False, "reason": "格式错误"})
        details.append({"item": "无多余记录", "score": 0, "max_score": 10, "passed": False, "reason": "格式错误"})
        with open(Path(workspace) / "workplace_score.json", "w") as f:
            json.dump({"total_score": total, "details": details}, f, indent=2)
        return

    # 4. 列表长度正确（2）
    length_ok = len(data) == 2
    details.append({
        "item": "冲突列表长度正确",
        "score": 20 if length_ok else 0,
        "max_score": 20,
        "passed": length_ok,
        "reason": f"长度 {len(data)}, 期望 2"
    })
    if length_ok:
        total_score += 20

    # 5. 检查设备 ID 和冲突类型（无序比较）
    # 转换为可比较集合：每个记录由 (device_id, conflict_type) 元组表示
    actual_tuples = set()
    for entry in data:
        if isinstance(entry, dict):
            actual_tuples.add((entry.get("device_id"), entry.get("conflict_type")))
    expected_tuples = {
        ("humidifier_bedroom_01", "humidity_too_high"),
        ("humidifier_living_01", "humidity_too_low")
    }

    id_match = actual_tuples == expected_tuples
    details.append({
        "item": "冲突设备 ID 与类型整体正确",
        "score": 50 if id_match else 0,
        "max_score": 50,
        "passed": id_match,
        "reason": f"实际 {actual_tuples} vs 预期 {expected_tuples}"
    })
    if id_match:
        total_score += 50

    # 6. 无多余记录（如果长度正确且 ID 匹配则自动满足，但额外检查字段是否有多余）
    # 我们只要求每个 entry 仅包含 device_id 和 conflict_type 两个字段
    extra_fields = False
    for entry in data:
        if set(entry.keys()) != {"device_id", "conflict_type"}:
            extra_fields = True
            break
    details.append({
        "item": "无多余字段",
        "score": 10 if not extra_fields else 0,
        "max_score": 10,
        "passed": not extra_fields,
        "reason": "每个条目只包含 device_id 和 conflict_type" if not extra_fields else "存在额外字段"
    })
    if not extra_fields:
        total_score += 10

    # 写入评分
    with open(Path(workspace) / "workplace_score.json", "w") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
