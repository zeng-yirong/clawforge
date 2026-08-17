import os
import json
import random

def build_env():
    # 创建目录结构
    os.makedirs("data", exist_ok=True)
    os.makedirs("project_docs", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("archive", exist_ok=True)

    # --- accounts.json (团队账户) ---
    accounts = [
        {
            "account_id": "acc-001",
            "display_name": "Alice Chen",
            "department": "QA",
            "email": "alice@example.com",
            "permissions": ["reproduce", "view"]
        },
        {
            "account_id": "acc-002",
            "display_name": "Bob Zhang",
            "department": "Engineering",
            "email": "bob@example.com",
            "permissions": ["view"]
        },
        {
            "account_id": "acc-003",
            "display_name": "Carol Li",
            "department": "Docs",
            "email": "carol@example.com",
            "permissions": ["edit", "view"]
        }
    ]
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # --- contacts.json (干扰联系人) ---
    contacts = [
        {"contact_id": "ct-001", "name": "Dave Wang", "role": "PM", "email": "dave@example.com"},
        {"contact_id": "ct-002", "name": "Eva Liu", "role": "Dev", "email": "eva@example.com"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # --- project_docs 目录 ---

    # 正确的复现指南 v2
    v2_content = """# Reproduction Guide v2

## Project ID: proj-034
## Doc ID: doc-007

### Steps
1. Run `python run_test.py`
2. Check output in logs/run.log
3. Result should be "All tests passed"

- 本次复现成功，结果标记为 success.
"""
    with open("project_docs/reproduction_guide_v2.md", "w") as f:
        f.write(v2_content)

    # 干扰 v1 版本（不同的项目ID）
    v1_content = """# Reproduction Guide v1 (deprecated)

## Project ID: proj-012
## Doc ID: doc-003

### Steps
1. ...
- 结果标记为 fail.
"""
    with open("project_docs/reproduction_guide_v1.md", "w") as f:
        f.write(v1_content)

    # 其他干扰文档
    with open("project_docs/notes.md", "w") as f:
        f.write("Team notes - no reproduction info here.")

    with open("project_docs/old_guide.md", "w") as f:
        f.write("# Old guide\nProject ID: proj-034\nDoc ID: doc-005\nResult: fail")

    # --- 时间戳文件 ---
    with open("timestamp.txt", "w") as f:
        f.write("2025-03-22T14:30:00Z")

    # --- 干扰日志 ---
    with open("logs/run.log", "w") as f:
        f.write("[INFO] Starting tests...\n[INFO] All tests passed.\n")
    with open("logs/old_run.log", "w") as f:
        f.write("[ERROR] Test failed.\n")

    # 创建一个空的 archive 目录，等待 agent 写入
