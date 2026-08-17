import sys
import json
import os
from pathlib import Path

def verify(workspace: str):
    details = []
    total_score = 0
    max_total = 100

    # 1. 检查文件存在 (10 分)
    output_path = Path(workspace) / "ops" / "updated_contacts.json"
    if output_path.exists() and output_path.is_file():
        details.append({
            "item": "输出文件 ops/updated_contacts.json 存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "文件存在"
        })
        total_score += 10
    else:
        details.append({
            "item": "输出文件 ops/updated_contacts.json 存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件不存在"
        })
        # 如果文件不存在，后续检查无法进行，直接输出结果
        _write_score(total_score, details)
        return

    # 2. 文件格式合法 (10 分)
    try:
        with open(output_path, "r") as f:
            data = json.load(f)
        details.append({
            "item": "JSON 格式合法",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "解析成功"
        })
        total_score += 10
    except (json.JSONDecodeError, Exception) as e:
        details.append({
            "item": "JSON 格式合法",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"解析失败: {str(e)}"
        })
        _write_score(total_score, details)
        return

    # 3. 类型为 list (10 分)
    if isinstance(data, list):
        details.append({
            "item": "根对象是列表",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "类型正确"
        })
        total_score += 10
    else:
        details.append({
            "item": "根对象是列表",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"期望 list，实际 {type(data).__name__}"
        })
        _write_score(total_score, details)
        return

    # 4. 列表长度正确 (10 分) -- 期望 2
    expected_length = 2
    if len(data) == expected_length:
        details.append({
            "item": "列表长度正确",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"长度为 {expected_length}"
        })
        total_score += 10
    else:
        details.append({
            "item": "列表长度正确",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"期望 {expected_length}，实际 {len(data)}"
        })

    # 根据 contact_id 建立字典以便验证
    contact_map = {item.get("contact_id"): item for item in data if isinstance(item, dict)}

    # 允许的顺序无关，我们检查集合
    expected_ids = {"c002", "c005"}
    actual_ids = set(contact_map.keys())
    if actual_ids == expected_ids:
        details.append({
            "item": "联系人 ID 集合正确",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": f"ID 为 {expected_ids}"
        })
        total_score += 20
    else:
        missing = expected_ids - actual_ids
        extra = actual_ids - expected_ids
        reason_parts = []
        if missing:
            reason_parts.append(f"缺少: {missing}")
        if extra:
            reason_parts.append(f"多余: {extra}")
        details.append({
            "item": "联系人 ID 集合正确",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "; ".join(reason_parts) if reason_parts else "集合不匹配"
        })

    # 5. 检查每个联系人的 folder 和 tags
    # 预定义期望的最终状态
    expected_state = {
        "c002": {"folder": "business", "tags": ["tech_partner"]},
        "c005": {"folder": "business", "tags": ["new", "tech_partner"]}  # 保留原标签 new
    }

    folder_score = 0
    folder_max = 20  # 每个联系人10分，共2个
    tags_score = 0
    tags_max = 20   # 每个联系人10分，共2个
    retain_score = 0
    retain_max = 10  # c005 保留 new

    for cid in ["c002", "c005"]:
        item = contact_map.get(cid)
        if item is None:
            continue

        # folder 检查
        if item.get("folder") == "business":
            folder_score += 10
        # tags 检查：必须包含 tech_partner
        tags = item.get("tags", [])
        if "tech_partner" in tags:
            tags_score += 10

        # 保留原标签检查 (c005 必须有 new)
        if cid == "c005" and "new" in tags:
            retain_score += 10

    details.append({
        "item": "所有联系人的 folder 为 business",
        "score": folder_score,
        "max_score": folder_max,
        "passed": folder_score == folder_max,
        "reason": f"获得 {folder_score}/{folder_max}"
    })
    total_score += folder_score

    details.append({
        "item": "所有联系人包含 tech_partner 标签",
        "score": tags_score,
        "max_score": tags_max,
        "passed": tags_score == tags_max,
        "reason": f"获得 {tags_score}/{tags_max}"
    })
    total_score += tags_score

    details.append({
        "item": "c005 保留原有 'new' 标签",
        "score": retain_score,
        "max_score": retain_max,
        "passed": retain_score == retain_max,
        "reason": f"获得 {retain_score}/{retain_max}"
    })
    total_score += retain_score

    # 6. 没有多余的联系人 (10 分) - 额外 ID 检查已在集合中扣分，这里额外确认没有未知 ID
    extra_ids = actual_ids - expected_ids
    if not extra_ids:
        details.append({
            "item": "无多余联系人",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "没有额外 contact_id"
        })
        total_score += 10
    else:
        details.append({
            "item": "无多余联系人",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"存在额外 ID: {extra_ids}"
        })

    # 最终总分
    _write_score(total_score, details)

def _write_score(total_score, details):
    result = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    # 同时打印到 stdout 便于调试
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
