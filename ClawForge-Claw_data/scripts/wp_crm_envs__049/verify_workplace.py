#!/usr/bin/env python3
import json
import sys
import os
from datetime import date, timedelta
from pathlib import Path

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def verify(workspace):
    ws = Path(workspace)
    score_details = []
    total_score = 0

    # 1. 检查产物文件是否存在 (10分)
    result_path = ws / "ops" / "birthday_task_result.json"
    if result_path.exists():
        score_details.append({
            "item": "产物文件 ops/birthday_task_result.json 存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "文件存在"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "产物文件 ops/birthday_task_result.json 存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件不存在"
        })
        # 后续检查无法进行，直接写结果
        _write_score(score_details, total_score)
        return

    # 2. 解析JSON合法性 (5分)
    try:
        data = load_json(str(result_path))
        score_details.append({
            "item": "JSON格式合法",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "解析成功"
        })
        total_score += 5
    except Exception as e:
        score_details.append({
            "item": "JSON格式合法",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": f"解析失败: {str(e)}"
        })
        _write_score(score_details, total_score)
        return

    # 3. 检查数据结构：必须包含 updated_contacts 列表（至少一个） (10分)
    if not isinstance(data, dict) or "updated_contacts" not in data:
        score_details.append({
            "item": "JSON包含 updated_contacts 数组",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "缺少 updated_contacts 字段或不是对象"
        })
        _write_score(score_details, total_score)
        return
    contacts_list = data["updated_contacts"]
    if not isinstance(contacts_list, list) or len(contacts_list) == 0:
        score_details.append({
            "item": "updated_contacts 为非空列表",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "列表为空或不是列表"
        })
        _write_score(score_details, total_score)
        return
    score_details.append({
        "item": "updated_contacts 为非空列表",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": f"包含 {len(contacts_list)} 个联系人"
    })
    total_score += 10

    # 4. 检查是否存在 tag_created 字段 (5分)
    tag_created = data.get("tag_created", None)
    if tag_created is not None and isinstance(tag_created, bool):
        score_details.append({
            "item": "tag_created 字段存在且布尔类型",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": f"tag_created = {tag_created}"
        })
        total_score += 5
    else:
        score_details.append({
            "item": "tag_created 字段存在且布尔类型",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "字段缺失或类型错误"
        })

    # 5. 核心：校验符合条件的联系人 (40分)
    # 预期：未来7天内（2025-07-15 ~ 2025-07-22）过生日的联系人：
    # ct_001 Alice (7/18), ct_002 Bob (7/20), ct_003 Carol (7/22), ct_008 Henry (7/16)
    # 注意：ct_002 Bob的提醒虽然禁用，但生日在范围内；ct_003 Carol没有提醒但生日在范围内；
    # ct_008 Henry提醒禁用但生日在范围内。
    expected_contacts = {
        "ct_001": {"full_name": "Alice Johnson", "birthday": "2025-07-18"},
        "ct_002": {"full_name": "Bob Smith", "birthday": "2025-07-20"},
        "ct_003": {"full_name": "Carol Williams", "birthday": "2025-07-22"},
        "ct_008": {"full_name": "Henry Taylor", "birthday": "2025-07-16"}
    }
    # 加载原始联系人数据以获取完整标签
    contacts_path = ws / "data" / "contacts.json"
    if not contacts_path.exists():
        score_details.append({
            "item": "原始联系人文件存在",
            "score": 0,
            "max_score": 40,
            "passed": False,
            "reason": "data/contacts.json 不存在，无法校验"
        })
        _write_score(score_details, total_score)
        return
    original_contacts = load_json(str(contacts_path)).get("contacts", [])
    original_map = {c["contact_id"]: c for c in original_contacts}

    # 加载标签定义，确认是否有 birthday-reminder
    tags_path = ws / "data" / "tags" / "tag_definitions.json"
    tag_name_map = {}
    if tags_path.exists():
        all_tags = load_json(str(tags_path)).get("tag_definitions", [])
        tag_name_map = {t["name"]: t for t in all_tags}

    # 检查每个预期联系人是否在结果中
    found_ids = set()
    correct_count = 0
    for entry in contacts_list:
        cid = entry.get("contact_id")
        if cid in expected_contacts:
            found_ids.add(cid)
            expected = expected_contacts[cid]
            # 检查 full_name
            if entry.get("full_name") != expected["full_name"]:
                continue
            # 检查 birthday (字段可能是 birthday 或 reminder_date)
            bday = entry.get("birthday") or entry.get("reminder_date")
            if bday != expected["birthday"]:
                continue
            # 检查 tags 是否包含 "birthday-reminder"
            tags = entry.get("tags", [])
            if "birthday-reminder" not in tags:
                continue
            correct_count += 1

    if correct_count == 4 and len(found_ids) == 4:
        score_details.append({
            "item": "所有4个符合条件的联系人均被正确列出，含正确full_name、birthday和birthday-reminder标签",
            "score": 40,
            "max_score": 40,
            "passed": True,
            "reason": f"找到 {correct_count} 个"
        })
        total_score += 40
    else:
        # 部分正确给部分分
        partial = correct_count * 10  # 每个10分
        score_details.append({
            "item": "所有4个符合条件的联系人均被正确列出",
            "score": min(partial, 40),
            "max_score": 40,
            "passed": False,
            "reason": f"正确 {correct_count}/4，发现ID集合: {found_ids}"
        })
        total_score += min(partial, 40)

    # 6. 检查是否包含了不在预期内的联系人（多余）扣分，但不为负 (10分)
    extra_ids = [e.get("contact_id") for e in contacts_list if e.get("contact_id") not in expected_contacts]
    if extra_ids:
        score_details.append({
            "item": "结果中无多余的非预期联系人",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"包含多余联系人: {extra_ids}"
        })
    else:
        score_details.append({
            "item": "结果中无多余的非预期联系人",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "无多余"
        })
        total_score += 10

    # 7. 检查 tag_created 是否合理：因为初始没有 "birthday-reminder"，agent应该创建，所以应为true (5分)
    if tag_created is True:
        score_details.append({
            "item": "tag_created 值为 true（标签为新创建）",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "正确"
        })
        total_score += 5
    else:
        # 如果初始有标签则情况不同，但初始没有，所以给0分
        score_details.append({
            "item": "tag_created 值为 true（标签为新创建）",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": f"期望 true，得到 {tag_created}"
        })

    # 8. 检查每个联系人的 tags 中 birthday-reminder 是否在原始定义中存在 (5分)
    if "birthday-reminder" in tag_name_map:
        score_details.append({
            "item": "birthday-reminder 标签定义存在于 tags/tag_definitions.json",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "定义存在"
        })
        total_score += 5
    else:
        score_details.append({
            "item": "birthday-reminder 标签定义存在于 tags/tag_definitions.json",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "未找到定义，可能agent未创建标签定义文件"
        })

    # 总分上限100，若超出剪裁
    final_score = min(total_score, 100)
    _write_score(score_details, final_score)

def _write_score(details, total):
    result = {
        "total_score": total,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
