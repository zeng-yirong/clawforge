import sys
import os
import json
import re
from pathlib import Path

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    workspace_path = Path(workspace)

    details = []
    total_score = 0

    # ---------- 1. 目录结构检查 (10分) ----------
    # 要求 ops 目录存在
    ops_dir = workspace_path / "ops"
    if ops_dir.is_dir():
        details.append({
            "item": "ops directory exists",
            "score": 10, "max_score": 10, "passed": True,
            "reason": "ops/ directory found"
        })
        total_score += 10
    else:
        details.append({
            "item": "ops directory exists",
            "score": 0, "max_score": 10, "passed": False,
            "reason": "ops/ directory missing"
        })

    # ---------- 2. 目标文件存在且为合法 JSON (10分) ----------
    target_file = ops_dir / "birthday_reminders_to_create.json"
    if not target_file.is_file():
        details.append({
            "item": "output file exists",
            "score": 0, "max_score": 10, "passed": False,
            "reason": "ops/birthday_reminders_to_create.json not found"
        })
        # 后续无法继续，直接输出结果
        _write_score(total_score, details)
        return
    try:
        with open(target_file, "r") as f:
            reminders = json.load(f)
        details.append({
            "item": "valid JSON",
            "score": 10, "max_score": 10, "passed": True,
            "reason": "File is valid JSON"
        })
        total_score += 10
    except (json.JSONDecodeError, ValueError) as e:
        details.append({
            "item": "valid JSON",
            "score": 0, "max_score": 10, "passed": False,
            "reason": f"Invalid JSON: {e}"
        })
        _write_score(total_score, details)
        return

    # ---------- 3. 数据源读取 ----------
    contacts_path = workspace_path / "data" / "contacts.json"
    try:
        with open(contacts_path) as f:
            contacts = json.load(f)
    except Exception as e:
        details.append({
            "item": "data source loading",
            "score": 0, "max_score": 30, "passed": False,
            "reason": f"Cannot load contacts.json: {e}"
        })
        _write_score(total_score, details)
        return

    reminders_path = workspace_path / "data" / "reminders" / "reminders.json"
    try:
        with open(reminders_path) as f:
            existing_reminders = json.load(f)
    except Exception as e:
        details.append({
            "item": "data source loading",
            "score": 0, "max_score": 30, "passed": False,
            "reason": f"Cannot load reminders.json: {e}"
        })
        _write_score(total_score, details)
        return

    # 构建已有提醒联系人集合
    existing_contacts_with_birthday_reminder = {
        r["contact_id"] for r in existing_reminders
        if r.get("reminder_type") == "birthday" and r.get("enabled") is True
    }

    # 正确的记录生成逻辑
    correct_reminders = []
    birthday_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    for c in contacts:
        # 必须是 business folder
        if c.get("folder") != "business":
            continue
        birthday = c.get("birthday", "")
        if not isinstance(birthday, str) or not birthday_pattern.match(birthday):
            continue
        # 不能已有生日提醒
        if c.get("contact_id") in existing_contacts_with_birthday_reminder:
            continue
        # 计算 suggested_reminder_date (生日前3天)
        from datetime import datetime, timedelta
        try:
            dt = datetime.strptime(birthday, "%Y-%m-%d")
            suggested = (dt - timedelta(days=3)).strftime("%Y-%m-%d")
        except:
            continue
        correct_reminders.append({
            "contact_id": c["contact_id"],
            "full_name": c["full_name"],
            "birthday": birthday,
            "suggested_reminder_date": suggested
        })

    # 期望结果：仅 ct_002 (Bob Smith) 符合
    expected = [
        {
            "contact_id": "ct_002",
            "full_name": "Bob Smith",
            "birthday": "2025-11-15",
            "suggested_reminder_date": "2025-11-12"
        }
    ]

    # ---------- 4. 检查记录数量与内容 (30分 剔除脏数据 + 50分 关键计算) ----------
    # 4a. 数量正确性 (10分)
    if len(reminders) == len(expected):
        details.append({
            "item": "correct number of records",
            "score": 10, "max_score": 10, "passed": True,
            "reason": f"Exactly {len(expected)} record(s) produced"
        })
        total_score += 10
    else:
        details.append({
            "item": "correct number of records",
            "score": 0, "max_score": 10, "passed": False,
            "reason": f"Expected {len(expected)} record(s), got {len(reminders)}"
        })

    # 4b. 每个字段值匹配 (40分，每条记录10分)
    # 由于只有一条预期，我们逐字段比较
    field_score_per_record = 10  # 每个字段2.5分，我们简化：记录完全正确得10分，否则0
    field_checks = ["contact_id", "full_name", "birthday", "suggested_reminder_date"]
    # 将 agent 输出转换为键值字典按 contact_id 索引（可能存在多条）
    agent_map = {r.get("contact_id"): r for r in reminders}

    for exp in expected:
        cid = exp["contact_id"]
        if cid not in agent_map:
            details.append({
                "item": f"record for {cid} exists",
                "score": 0, "max_score": 10, "passed": False,
                "reason": f"Missing record for contact_id={cid}"
            })
            continue
        agent_rec = agent_map[cid]
        ok = True
        for field in field_checks:
            if agent_rec.get(field) != exp[field]:
                ok = False
                break
        if ok:
            details.append({
                "item": f"record for {cid} fields match",
                "score": 10, "max_score": 10, "passed": True,
                "reason": "All fields correct"
            })
            total_score += 10
        else:
            details.append({
                "item": f"record for {cid} fields match",
                "score": 0, "max_score": 10, "passed": False,
                "reason": f"Expected {exp}, got {agent_rec}"
            })

    # 4c. 没有额外记录 (惩罚 - 从总分扣减，但这里我们单独记分)
    # 如果 agent 输出了多余记录，但数量上已经扣过分了；这里额外检查每一条多余记录扣分
    extra_ids = set(agent_map.keys()) - {e["contact_id"] for e in expected}
    if extra_ids:
        details.append({
            "item": "no extra records",
            "score": 0, "max_score": 10, "passed": False,
            "reason": f"Extra records found: {extra_ids}"
        })
        # 但不从总分加，而是设为0分（已算在数量里）
    else:
        details.append({
            "item": "no extra records",
            "score": 10, "max_score": 10, "passed": True,
            "reason": "No extra records"
        })
        total_score += 10

    # ---------- 最终分数 (0-100) ----------
    total_score = min(total_score, 100)
    _write_score(total_score, details)

def _write_score(total, details):
    result = {
        "total_score": total,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
