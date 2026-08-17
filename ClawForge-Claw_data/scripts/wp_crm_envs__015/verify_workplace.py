import json
import os
import sys
from datetime import datetime, timedelta
from collections import OrderedDict

def load_json(workspace, rel_path):
    full_path = os.path.join(workspace, rel_path)
    if not os.path.exists(full_path):
        return None
    with open(full_path, "r", encoding="utf-8") as f:
        return json.load(f)

def verify(workspace):
    details = []
    total_score = 0

    # 1. 检查ops目录
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        details.append({"item": "ops目录存在", "score": 5, "max_score": 5, "passed": True, "reason": "ops/ 目录存在"})
        total_score += 5
    else:
        details.append({"item": "ops目录存在", "score": 0, "max_score": 5, "passed": False, "reason": "缺少 ops/ 目录"})
        # 直接返回，没有目录后续无法验证
        finish(details, total_score)
        return

    # 2. 读取输出文件
    output_path = os.path.join(workspace, "ops", "birthday_reminders_plan.json")
    if not os.path.exists(output_path):
        details.append({"item": "输出文件存在", "score": 0, "max_score": 5, "passed": False, "reason": "ops/birthday_reminders_plan.json 不存在"})
        finish(details, total_score)
        return

    try:
        with open(output_path, "r") as f:
            plan = json.load(f)
        if not isinstance(plan, list):
            raise ValueError("不是数组")
        details.append({"item": "输出文件格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 数组格式正确"})
        total_score += 10
    except Exception as e:
        details.append({"item": "输出文件格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {e}"})
        finish(details, total_score)
        return

    # 3. 读取输入数据
    companies = load_json(workspace, "data/companies.json")
    contacts = load_json(workspace, "data/contacts.json")
    birthdays_dict = load_json(workspace, "data/birthdays.json")
    reminders = load_json(workspace, "data/reminders/reminders.json")

    if None in (companies, contacts, birthdays_dict, reminders):
        missing = []
        if companies is None: missing.append("data/companies.json")
        if contacts is None: missing.append("data/contacts.json")
        if birthdays_dict is None: missing.append("data/birthdays.json")
        if reminders is None: missing.append("data/reminders/reminders.json")
        details.append({"item": "输入数据完整性", "score": 0, "max_score": 10, "passed": False, "reason": f"缺少文件: {', '.join(missing)}"})
        finish(details, total_score)
        return
    details.append({"item": "输入数据完整性", "score": 10, "max_score": 10, "passed": True, "reason": "所有必需输入文件存在"})
    total_score += 10

    # 4. 计算正确答案
    # 找到 ClientCo Operations 的 company_id
    target_company_id = None
    for c in companies:
        if c["name"] == "ClientCo Operations":
            target_company_id = c["company_id"]
            break
    if not target_company_id:
        details.append({"item": "计算正确答案", "score": 0, "max_score": 5, "passed": False, "reason": "未找到 ClientCo Operations 公司"})
        finish(details, total_score)
        return

    # 筛选目标联系人: 属于该公司, 不在 inactive 文件夹
    target_contacts = {}
    for c in contacts:
        if c["company_id"] == target_company_id and c["folder"] != "inactive":
            target_contacts[c["contact_id"]] = c

    # 已有生日提醒的 contact_id 集合 (只考虑 type=birthday)
    existing_birthday_contact_ids = set()
    for r in reminders:
        if r.get("reminder_type") == "birthday":
            existing_birthday_contact_ids.add(r["contact_id"])

    # 需要创建提醒的联系人
    expected_entries = []
    for cid in sorted(target_contacts.keys()):
        if cid in existing_birthday_contact_ids:
            continue
        if cid not in birthdays_dict:
            continue
        bir_str = birthdays_dict[cid]
        try:
            bir_date = datetime.strptime(bir_str, "%Y-%m-%d")
        except:
            continue
        reminder_date = bir_date - timedelta(days=7)
        reminder_date_str = reminder_date.strftime("%Y-%m-%d")
        contact = target_contacts[cid]
        expected_entries.append({
            "contact_id": cid,
            "full_name": contact["full_name"],
            "reminder_date": reminder_date_str,
            "reminder_type": "birthday",
            "is_recurring": True,
            "enabled": True
        })

    # 比较
    # 检查字段完整性 (每条记录)
    required_fields = ["contact_id", "full_name", "reminder_date", "reminder_type", "is_recurring", "enabled"]
    field_errors = []
    for i, entry in enumerate(plan):
        for field in required_fields:
            if field not in entry:
                field_errors.append(f"记录 {i} 缺少字段 {field}")
    if field_errors:
        details.append({"item": "字段完整性", "score": 0, "max_score": 15, "passed": False, "reason": "; ".join(field_errors)})
    else:
        details.append({"item": "字段完整性", "score": 15, "max_score": 15, "passed": True, "reason": "所有必需字段存在"})
        total_score += 15

    # 比较联系人的集合 (按contact_id排序)
    plan_ids = sorted([e["contact_id"] for e in plan])
    expected_ids = sorted([e["contact_id"] for e in expected_entries])
    if plan_ids == expected_ids:
        details.append({"item": "联系人ID集合正确", "score": 20, "max_score": 20, "passed": True, "reason": f"包含正确的联系人: {expected_ids}"})
        total_score += 20
    else:
        missing_ids = set(expected_ids) - set(plan_ids)
        extra_ids = set(plan_ids) - set(expected_ids)
        reason = ""
        if missing_ids:
            reason += f"缺少: {sorted(missing_ids)}. "
        if extra_ids:
            reason += f"多余: {sorted(extra_ids)}."
        details.append({"item": "联系人ID集合正确", "score": 0, "max_score": 20, "passed": False, "reason": reason})

    # 比较每个条目的剩余字段 (全匹配)
    def entry_key(e):
        return e["contact_id"]
    plan_sorted = sorted(plan, key=entry_key)
    expected_sorted = sorted(expected_entries, key=entry_key)
    detail_mismatches = []
    for i, (p, e) in enumerate(zip(plan_sorted, expected_sorted)):
        for field in ["full_name", "reminder_date", "reminder_type", "is_recurring", "enabled"]:
            if p.get(field) != e[field]:
                detail_mismatches.append(f"{p['contact_id']} 字段 {field} 应为 {e[field]} 实际 {p.get(field)}")
    if detail_mismatches:
        details.append({"item": "字段值精确匹配", "score": 0, "max_score": 25, "passed": False, "reason": "; ".join(detail_mismatches)})
    else:
        details.append({"item": "字段值精确匹配", "score": 25, "max_score": 25, "passed": True, "reason": "所有记录字段值正确"})
        total_score += 25

    # 检查是否有多余记录 (长度比对已经在集合处做过，但这里再防止数量不对)
    if len(plan) != len(expected_entries):
        # 已经在集合扣过分，这里额外扣分
        pass

    # 没有多余字段扣分 (已涵盖)
    finish(details, total_score)

def finish(details, total_score):
    # 确保总分不超过100
    total_score = min(total_score, 100)
    result = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"Final score: {total_score}/100")
    sys.exit(0)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
