import sys
import json
import os
from pathlib import Path

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    ws = Path(workspace)
    score = 0
    max_score = 100
    details = []

    # 1. 目录结构检查 (5分)
    expected_dirs = ["ops"]
    dir_score = 0
    for d in expected_dirs:
        if (ws / d).is_dir():
            dir_score += 5
            details.append({
                "item": f"目录 {d} 存在",
                "score": 5,
                "max_score": 5,
                "passed": True,
                "reason": f"目录 {d} 已创建"
            })
        else:
            details.append({
                "item": f"目录 {d} 存在",
                "score": 0,
                "max_score": 5,
                "passed": False,
                "reason": f"目录 {d} 未创建"
            })
    if dir_score == 5:
        score += 5

    # 2. 目标文件存在 & JSON 合法 (15分)
    target_file = ws / "ops" / "urgent_ups_outages.json"
    json_valid = False
    if target_file.is_file():
        try:
            data = json.loads(target_file.read_text())
            json_valid = True
            score += 15
            details.append({
                "item": "ops/urgent_ups_outages.json 存在且合法JSON",
                "score": 15,
                "max_score": 15,
                "passed": True,
                "reason": "文件存在，JSON解析成功"
            })
        except (json.JSONDecodeError, ValueError):
            details.append({
                "item": "ops/urgent_ups_outages.json 存在且合法JSON",
                "score": 0,
                "max_score": 15,
                "passed": False,
                "reason": "文件存在但不是合法JSON"
            })
    else:
        details.append({
            "item": "ops/urgent_ups_outages.json 存在且合法JSON",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": "文件不存在"
        })

    if not json_valid:
        # 后续检查无法进行，直接返回
        details.append({
            "item": "整体结果",
            "score": score,
            "max_score": max_score,
            "passed": score >= 60,
            "reason": f"JSON无效，总分{score}"
        })
        result = {"total_score": score, "details": details}
        (ws / "workplace_score.json").write_text(json.dumps(result, indent=2))
        return

    # 3. 数据格式：每个元素必须包含 incident_id 和 title，且没有多余字段 (20分)
    item_score = 0
    all_items_valid = True
    reasons = []
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            all_items_valid = False
            reasons.append(f"第{i}个元素不是对象")
            continue
        has_id = "incident_id" in item
        has_title = "title" in item
        # 检查是否有多余字段（只允许这两个）
        allowed = {"incident_id", "title"}
        extra = set(item.keys()) - allowed
        if not (has_id and has_title) or extra:
            all_items_valid = False
            if not has_id:
                reasons.append(f"第{i}个元素缺少 incident_id")
            if not has_title:
                reasons.append(f"第{i}个元素缺少 title")
            if extra:
                reasons.append(f"第{i}个元素有多余字段: {extra}")
    if all_items_valid and len(data) > 0:
        item_score = 20
        score += 20
        details.append({
            "item": "每个对象包含 incident_id 和 title，无多余字段",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "所有元素格式正确"
        })
    else:
        details.append({
            "item": "每个对象包含 incident_id 和 title，无多余字段",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "; ".join(reasons)
        })

    # 4. 数量正确 (20分)
    expected_count = 2
    if len(data) == expected_count:
        score += 20
        details.append({
            "item": "数组长度应为2",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": f"数量为 {len(data)}"
        })
    else:
        details.append({
            "item": "数组长度应为2",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"实际数量为 {len(data)}，期望 2"
        })

    # 5. 内容正确且按 opened_at 升序 (40分)
    # 从 env_builder 可知正确顺序：INC-2025-06-15-002 (03分) 然后 INC-2025-06-15-001 (05分)
    expected_ids = ["INC-2025-06-15-002", "INC-2025-06-15-001"]
    expected_titles = [
        "Inference Worker power loss – UPS overload",
        "west4 UPS primary failure – Billing API down"
    ]
    content_failures = []
    if len(data) == 2:
        for idx, (expected_id, expected_title) in enumerate(zip(expected_ids, expected_titles)):
            actual = data[idx]
            if actual.get("incident_id") != expected_id:
                content_failures.append(f"第{idx+1}个 incident_id 应为 {expected_id}，实际为 {actual.get('incident_id')}")
            if actual.get("title") != expected_title:
                content_failures.append(f"第{idx+1}个 title 应为 {expected_title}，实际为 {actual.get('title')}")
    else:
        content_failures.append("数量不对，无法逐项检查")

    if not content_failures:
        score += 40
        details.append({
            "item": "内容与顺序正确（按 opened_at 升序）",
            "score": 40,
            "max_score": 40,
            "passed": True,
            "reason": "两个工单 ID 和 title 完全匹配，且顺序正确"
        })
    else:
        details.append({
            "item": "内容与顺序正确（按 opened_at 升序）",
            "score": 0,
            "max_score": 40,
            "passed": False,
            "reason": "; ".join(content_failures)
        })

    # 最终总分
    details.append({
        "item": "总得分",
        "score": score,
        "max_score": max_score,
        "passed": score >= 60,
        "reason": f"总分 {score}/{max_score}"
    })

    result = {"total_score": score, "details": details}
    (ws / "workplace_score.json").write_text(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
