#!/usr/bin/env python3
import json, os, sys, csv, re
from datetime import date, timedelta
from pathlib import Path

workspace = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
score_file = workspace / "workplace_score.json"

def get_score(workspace):
    details = []
    total_score = 0

    # 1. 目录结构检查 (10分)
    required_dirs = ["data", "data/tags", "data/reminders", "output"]
    dir_score = 0
    for d in required_dirs:
        if (workspace / d).is_dir():
            dir_score += 2.5
    details.append({"item": "Required directories exist", "score": dir_score, "max_score": 10, 
                     "passed": dir_score == 10, "reason": f"Found {int(dir_score/2.5)}/4 dirs"})
    total_score += dir_score

    # 2. 必要文件存在 & 格式合法 (10分)
    files_to_check = [
        ("data/current_date.txt", "text"),
        ("data/contacts.json", "json"),
        ("data/tags/tag_definitions.json", "json"),
        ("data/reminders/reminders.json", "json"),
        ("output/upcoming_birthdays.json", "json"),
    ]
    file_score = 0
    for fname, ftype in files_to_check:
        fpath = workspace / fname
        if not fpath.exists():
            reason = f"{fname} missing"
            details.append({"item": f"File {fname} exists", "score": 0, "max_score": 2, "passed": False, "reason": reason})
            continue
        try:
            if ftype == "json":
                with open(fpath) as f:
                    data = json.load(f)
                if not isinstance(data, (list, dict)):
                    raise ValueError("not list/dict")
            else:
                with open(fpath) as f:
                    text = f.read().strip()
                if not text:
                    raise ValueError("empty")
            file_score += 2
            details.append({"item": f"File {fname} exists & valid", "score": 2, "max_score": 2, "passed": True, "reason": "OK"})
        except Exception as e:
            file_score += 0.5
            details.append({"item": f"File {fname} exists but invalid", "score": 0.5, "max_score": 2, "passed": False, "reason": str(e)})
    total_score += file_score

    # 3. 读取基准日期
    today_str = ""
    try:
        with open(workspace / "data/current_date.txt") as f:
            today_str = f.read().strip()
        today = date.fromisoformat(today_str)
    except:
        today = date(2024, 6, 15)
        today_str = "2024-06-15"
    delta = timedelta(days=30)
    cutoff = today + delta  # 2024-07-15

    # 4. 读取联系人、标签、提醒 (修改后的)
    try:
        with open(workspace / "data/contacts.json") as f:
            contacts = json.load(f)
        with open(workspace / "data/tags/tag_definitions.json") as f:
            tag_defs_raw = json.load(f)
        with open(workspace / "data/reminders/reminders.json") as f:
            reminders = json.load(f)
        with open(workspace / "output/upcoming_birthdays.json") as f:
            report = json.load(f)
    except Exception as e:
        # 如果文件不可读则扣全部的50分
        details.append({"item": "Core data files readable", "score": 0, "max_score": 50, "passed": False, "reason": str(e)})
        total_score += 0
        # 仍要生成最终score
        final = {"total_score": int(total_score), "details": details}
        with open(score_file, "w") as f:
            json.dump(final, f, indent=2)
        return

    # 辅助：联系人ID到记录的映射
    contact_map = {c["contact_id"]: c for c in contacts}
    report_ids = {r.get("contact_id") for r in report} if isinstance(report, list) else set()

    # 验证核心逻辑 -----------------------------------------
    # 预期: business folder, birthday between [today, cutoff] inclusive
    expected_ids = set()
    for c in contacts:
        if c.get("folder") != "business":
            continue
        bday_str = c.get("birthday")
        if not bday_str:
            continue
        try:
            bday = date.fromisoformat(bday_str)
        except:
            continue
        if today <= bday <= cutoff:
            expected_ids.add(c["contact_id"])

    # 应该只有 ct_001, ct_003, ct_005, ct_008
    expected_ids_sorted = sorted(expected_ids)
    correct_expected = {"ct_001", "ct_003", "ct_005", "ct_008"}
    if expected_ids != correct_expected:
        # 如果env_builder中的数据不一致，仍然按实际算
        correct_expected = expected_ids

    # 4.1 检查报告中的联系人集合 (10分)
    report_set = set()
    if isinstance(report, list):
        report_set = {r.get("contact_id") for r in report if "contact_id" in r}
    report_match = (report_set == correct_expected)
    if report_match:
        report_score = 10
        reason = f"报告包含正确联系人: {sorted(correct_expected)}"
    else:
        report_score = 2
        reason = f"报告联系人集合 {report_set} 不匹配预期 {correct_expected} (可能只缺失/多了某些)"
    details.append({"item": "Report contact_id set matches", "score": report_score, "max_score": 10, "passed": report_match, "reason": reason})
    total_score += report_score

    # 4.2 检查每个联系人的标签处理 (20分)
    known_birthday_tag_id = None
    for t in tag_defs_raw:
        if t.get("name") == "birthday":
            known_birthday_tag_id = t["tag_id"]
            break
    tag_score = 0
    tag_items = []
    for cid in correct_expected:
        c = contact_map.get(cid)
        if not c:
            continue
        tags = c.get("tags", [])
        has_birthday_tag = "birthday" in tags or known_birthday_tag_id in tags
        # 预期状态: ct_001 已有birthday (初始有vip, 无birthday) -> 预期未加
        # ct_003 没有 -> 应加
        # ct_005 已有birthday (初始有birthday) -> 未加
        # ct_008 没有 -> 应加
        if cid == "ct_001":
            expect_tag_present = False  # 初始没有birthday，但不应加? 不对，初始tags=["vip"], 没有birthday，但Alice的生日在范围内，应加。我们需要检查初始数据。根据env_builder，ct_001的tags=["vip"]，没有birthday。所以预期应该加。但是注意，我们要求已有标签就不动，ct_001没有，所以要加。所以expect_tag_present = True (最终应该有)
        elif cid == "ct_003":
            expect_tag_present = True
        elif cid == "ct_005":
            expect_tag_present = True  # 初始已有birthday，所以最终仍有
        elif cid == "ct_008":
            expect_tag_present = True
        else:
            expect_tag_present = False

        if has_birthday_tag == expect_tag_present:
            tag_score += 5
            tag_items.append(f"{cid}: OK")
        else:
            tag_items.append(f"{cid}: expect {expect_tag_present}, got {has_birthday_tag}")
    details.append({"item": "Tag presence for each target", "score": tag_score, "max_score": 20, "passed": tag_score == 20, 
                     "reason": "; ".join(tag_items)})
    total_score += tag_score

    # 4.3 检查提醒处理 (20分)
    # 构建现有提醒contact_id set (只考虑birthday类型)
    existing_reminder_contacts = set()
    for r in reminders:
        if r.get("reminder_type") == "birthday":
            existing_reminder_contacts.add(r["contact_id"])
    # 预期: ct_001 已有提醒 (rm_001), 所以不应新增
    # ct_003 无 -> 应新增
    # ct_005 无 (Emma没有提醒) -> 应新增
    # ct_008 无 -> 应新增
    # 所以最终existing_reminder_contacts应包含 ct_001, ct_003, ct_005, ct_008
    expected_reminder_set = {"ct_001", "ct_003", "ct_005", "ct_008"}
    actual_reminder_set = existing_reminder_contacts.intersection(correct_expected)
    if actual_reminder_set == expected_reminder_set:
        reminder_score = 20
        reason = "所有目标联系人均有生日提醒"
    else:
        missing = expected_reminder_set - actual_reminder_set
        extra = actual_reminder_set - expected_reminder_set
        if not missing and not extra:
            reminder_score = 20
        else:
            reminder_score = 5
            reason = f"缺失提醒: {missing}, 多余: {extra}"
    details.append({"item": "Reminder creation for targets", "score": reminder_score, "max_score": 20, "passed": reminder_score == 20, "reason": reason})
    total_score += reminder_score

    # 4.4 检查报告字段完整性 (10分)
    if isinstance(report, list) and len(report) == len(correct_expected):
        # 检查每个条目是否包含contact_id, full_name, birthday, 以及是否新增标记
        fields_ok = True
        for entry in report:
            if not all(k in entry for k in ("contact_id", "full_name", "birthday", "tag_added", "reminder_added")):
                fields_ok = False
                break
        if fields_ok:
            field_score = 10
        else:
            field_score = 3
        details.append({"item": "Report field completeness", "score": field_score, "max_score": 10, "passed": fields_ok, "reason": "All required fields present" if fields_ok else "Missing fields"})
    else:
        field_score = 0
        details.append({"item": "Report field completeness", "score": 0, "max_score": 10, "passed": False, "reason": f"Report length {len(report) if isinstance(report, list) else 'not list'} != expected {len(correct_expected)}"})
    total_score += field_score

    # 4.5 检查未被操作的联系人是否被误改 (10分)
    # 检查ct_002, ct_004, ct_006, ct_007 不应有birthday标签或新提醒
    untouched_ids = ["ct_002", "ct_004", "ct_006", "ct_007"]
    untouched_errors = []
    for cid in untouched_ids:
        c = contact_map.get(cid)
        if c and "birthday" in c.get("tags", []):
            untouched_errors.append(f"{cid} got birthday tag")
        if cid in existing_reminder_contacts:
            # 注意ct_002已经有提醒，但它是inactive，不应新增，但原有提醒保留是可以的
            pass
    # 额外检查：ct_002原有提醒，不应删除或修改
    # 简单检查ct_002提醒是否存在
    ct002_reminder_exists = any(r["contact_id"] == "ct_002" and r.get("reminder_type") == "birthday" for r in reminders)
    if not ct002_reminder_exists:
        untouched_errors.append("ct_002 reminder removed")
    if not untouched_errors:
        untouched_score = 10
        reason = "未误改无关联系人"
    else:
        untouched_score = 2
        reason = "; ".join(untouched_errors)
    details.append({"item": "No unintended modifications", "score": untouched_score, "max_score": 10, "passed": untouched_score == 10, "reason": reason})
    total_score += untouched_score

    # 汇总
    total_score = min(int(total_score), 100)
    final = {"total_score": total_score, "details": details}
    with open(score_file, "w") as f:
        json.dump(final, f, indent=2)
    return

if __name__ == "__main__":
    get_score(workspace)
