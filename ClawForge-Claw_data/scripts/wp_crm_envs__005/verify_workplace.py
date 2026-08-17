import sys
import json
import os

def verify(workspace):
    score = 0
    details = []
    max_total = 100

    # 1. 检查结果文件是否存在且合法JSON (10分)
    result_path = os.path.join(workspace, "ops", "contact_updates.json")
    if not os.path.exists(result_path):
        details.append({
            "item": "结果文件 ops/contact_updates.json 存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件不存在"
        })
        # 无文件无法继续，直接返回
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": 0, "details": details}, f)
        return

    try:
        with open(result_path, "r") as f:
            data = json.load(f)
        details.append({
            "item": "结果文件为合法JSON",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "成功解析"
        })
        score += 10
    except (json.JSONDecodeError, ValueError, TypeError) as e:
        details.append({
            "item": "结果文件为合法JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON解析失败: {e}"
        })
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": score, "details": details}, f)
        return

    # 2. 必须是列表 (5分)
    if not isinstance(data, list):
        details.append({
            "item": "结果是列表",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": f"期望列表, 实际类型 {type(data).__name__}"
        })
        total = score
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": details}, f)
        return
    else:
        details.append({
            "item": "结果是列表",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "类型正确"
        })
        score += 5

    # 3. 列表长度必须为3 (10分)
    expected_count = 3
    actual_count = len(data)
    if actual_count == expected_count:
        details.append({
            "item": "列表长度正确",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"长度 {actual_count}"
        })
        score += 10
    else:
        details.append({
            "item": "列表长度正确（应为3）",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"实际长度 {actual_count}"
        })

    # 4. 每个条目必须包含 contact_id, folder, tags 字段 (10分)
    for i, entry in enumerate(data):
        if not isinstance(entry, dict):
            details.append({
                "item": f"第{i+1}个条目是字典",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"不是字典"
            })
            break
        missing = [f for f in ("contact_id", "folder", "tags") if f not in entry]
        if missing:
            details.append({
                "item": f"第{i+1}个条目包含所有必需字段",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"缺少字段 {missing}"
            })
            break
    else:
        details.append({
            "item": "所有条目包含必需字段 (contact_id, folder, tags)",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "字段齐全"
        })
        score += 10

    # 5. 预期的 contact_id 集合
    expected_ids = {"c001", "c002", "c008"}
    actual_ids = set()
    for entry in data:
        cid = entry.get("contact_id")
        if cid:
            actual_ids.add(cid)

    # 检查是否有不在预期中的ID (20分)
    unexpected = actual_ids - expected_ids
    if unexpected:
        details.append({
            "item": "没有多余的联系人ID",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"包含不应出现的ID: {unexpected}"
        })
    elif actual_ids == expected_ids:
        details.append({
            "item": "联系人ID集合完全匹配",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": f"ID集合 {sorted(actual_ids)}"
        })
        score += 20
    else:
        missing = expected_ids - actual_ids
        details.append({
            "item": "联系人ID集合完全匹配",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"缺少ID: {missing}"
        })

    # 6. 每个条目的 folder 必须是 "business" (10分)
    folder_ok = True
    for entry in data:
        if entry.get("folder") != "business":
            folder_ok = False
            break
    if folder_ok:
        details.append({
            "item": "所有条目folder为 business",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "全部正确"
        })
        score += 10
    else:
        details.append({
            "item": "所有条目folder为 business",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "存在非 business 的folder"
        })

    # 7. 每个条目的 tags 必须包含 "VIP" (10分)
    tags_ok = True
    for entry in data:
        tags = entry.get("tags", [])
        if not isinstance(tags, list) or "VIP" not in tags:
            tags_ok = False
            break
    if tags_ok:
        details.append({
            "item": "所有条目tags包含 VIP",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "全部包含VIP标签"
        })
        score += 10
    else:
        details.append({
            "item": "所有条目tags包含 VIP",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "有条目缺少VIP或tags非列表"
        })

    # 8. 额外检查：每个条目的tags还应包含原始标签 "industry:technology" (5分)
    orig_tag_ok = True
    for entry in data:
        tags = entry.get("tags", [])
        if "industry:technology" not in tags:
            orig_tag_ok = False
            break
    if orig_tag_ok:
        details.append({
            "item": "所有条目tags保留原始 industry:technology 标签",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "原始标签保留"
        })
        score += 5
    else:
        details.append({
            "item": "所有条目tags保留原始 industry:technology 标签",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "缺少 industry:technology 标签"
        })

    # 9. 顺序无关，但确保没有重复ID (10分)
    if len(actual_ids) == len(data):
        details.append({
            "item": "没有重复的联系人ID",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "所有ID唯一"
        })
        score += 10
    else:
        details.append({
            "item": "没有重复的联系人ID",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "存在重复ID"
        })

    # 写入结果
    final_score = min(score, max_total)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": final_score, "details": details}, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
