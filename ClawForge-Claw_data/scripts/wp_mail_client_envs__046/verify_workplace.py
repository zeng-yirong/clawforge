import json
import os
import sys

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    os.chdir(workspace)

    score_details = []
    total_score = 0
    max_total = 100

    # 1. 目录结构检查 (10分)
    dirs_ok = True
    if not os.path.isdir("ops"):
        dirs_ok = False
        score_details.append({
            "item": "ops directory exists",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "ops/ directory not found"
        })
    else:
        score_details.append({
            "item": "ops directory exists",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "ops/ exists"
        })

    if not os.path.isdir("archived"):
        dirs_ok = False
        score_details.append({
            "item": "archived directory exists",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "archived/ directory not found"
        })
    else:
        score_details.append({
            "item": "archived directory exists",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "archived/ exists"
        })

    # 2. todo_items.json 格式和内容 (60分)
    todo_score = 0
    max_todo = 60
    try:
        with open("ops/todo_items.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        score_details.append({
            "item": "todo_items.json exists and valid JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not found"
        })
        # 跳过后续todo检查
        for sub in ["Length", "Entry keys", "Entry values", "Order"]:
            score_details.append({
                "item": f"todo_items.json - {sub}",
                "score": 0,
                "max_score": 12.5,
                "passed": False,
                "reason": "File missing"
            })
        total_score += sum(d["score"] for d in score_details)
        # 继续归档检查
    else:
        # 格式合法
        if isinstance(data, list):
            score_details.append({
                "item": "todo_items.json is a valid JSON array",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "Root element is list"
            })
        else:
            score_details.append({
                "item": "todo_items.json is a valid JSON array",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"Root is {type(data).__name__}, expected list"
            })

        # 长度检查
        expected_items = [
            {"subject": "[TODO] Review Q3 budget", "timestamp": "2025-03-10T09:00:00Z"},
            {"subject": "[TODO] Prepare monthly report", "timestamp": "2025-03-11T14:30:00Z"},
            {"subject": "[TODO] Update client list", "timestamp": "2025-03-12T08:15:00Z"}
        ]
        if len(data) == 3:
            score_details.append({
                "item": "todo_items.json contains exactly 3 items",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "Length 3"
            })
        else:
            score_details.append({
                "item": "todo_items.json contains exactly 3 items",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"Found {len(data)} items"
            })

        # 每个entry的键和值
        entry_ok = True
        for i, (actual, expected) in enumerate(zip(data, expected_items)):
            if not isinstance(actual, dict):
                entry_ok = False
                continue
            if actual.get("subject") != expected["subject"]:
                entry_ok = False
            if actual.get("timestamp") != expected["timestamp"]:
                entry_ok = False
        if entry_ok:
            score_details.append({
                "item": "Each entry has correct subject and timestamp",
                "score": 20,
                "max_score": 20,
                "passed": True,
                "reason": "All fields match expected"
            })
        else:
            score_details.append({
                "item": "Each entry has correct subject and timestamp",
                "score": 0,
                "max_score": 20,
                "passed": False,
                "reason": "Mismatch in one or more entries"
            })

        # 顺序检查 (按时间升序)
        sorted_expected = sorted(expected_items, key=lambda x: x["timestamp"])
        if data == sorted_expected:
            score_details.append({
                "item": "Items are sorted by timestamp ascending",
                "score": 20,
                "max_score": 20,
                "passed": True,
                "reason": "Order correct"
            })
        else:
            score_details.append({
                "item": "Items are sorted by timestamp ascending",
                "score": 0,
                "max_score": 20,
                "passed": False,
                "reason": "Order incorrect"
            })

    # 3. 归档操作检查 (30分)
    archive_score = 0
    max_archive = 30
    spam_ids = ["msg_002", "msg_005"]
    archived_files = os.listdir("archived") if os.path.isdir("archived") else []
    email_dir = "data/emails"
    email_files = os.listdir(email_dir) if os.path.isdir(email_dir) else []

    # 检查两个spam文件是否在archived中
    spam_in_archived = all(f"{sid}.json" in archived_files for sid in spam_ids)
    # 检查两个spam文件是否从emails中移除
    spam_in_emails = any(f"{sid}.json" in email_files for sid in spam_ids)

    if spam_in_archived and not spam_in_emails:
        archive_score = 30
        score_details.append({
            "item": "Spam emails archived correctly (moved from data/emails to archived/)",
            "score": 30,
            "max_score": 30,
            "passed": True,
            "reason": "Both spam files found in archived/, none in emails/"
        })
    elif spam_in_archived and spam_in_emails:
        archive_score = 10
        score_details.append({
            "item": "Spam emails archived but still present in emails/ (should be moved, not copied)",
            "score": 10,
            "max_score": 30,
            "passed": False,
            "reason": "Files exist in both locations; expected move (only in archived/)"
        })
    else:
        archive_score = 0
        reason = ""
        if not spam_in_archived:
            reason += f"Missing in archived: {[s for s in spam_ids if f'{s}.json' not in archived_files]}"
        if spam_in_emails:
            reason += " Spam still in emails/"
        score_details.append({
            "item": "Spam emails archived correctly",
            "score": 0,
            "max_score": 30,
            "passed": False,
            "reason": reason or "No spam files found anywhere"
        })

    # 计算总分
    total_score = sum(d["score"] for d in score_details)
    result = {
        "total_score": total_score,
        "details": score_details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

    print(f"Total score: {total_score}/{max_total}")
    sys.exit(0 if total_score >= 60 else 1)  # 可选退出码

if __name__ == "__main__":
    main()
