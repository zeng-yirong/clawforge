import json
import os

def build_env():
    # 确保工作区根目录为当前目录（cwd 已切到 assets/...）
    # 创建 data/ 子目录
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/projects", exist_ok=True)
    os.makedirs("data/reproduction_logs", exist_ok=True)

    # --- accounts.json ---
    accounts = [
        {"account_id": "a001", "display_name": "Alice Wang", "department": "QA", "email": "alice@example.com", "permissions": ["reproduce"]},
        {"account_id": "a002", "display_name": "Bob Li", "department": "Dev", "email": "bob@example.com", "permissions": ["reproduce", "commit"]},
        {"account_id": "a003", "display_name": "Carol Chen", "department": "QA", "email": "carol@example.com", "permissions": ["review"]},
        {"account_id": "a004", "display_name": "David Zhang", "department": "Dev", "email": "david@example.com", "permissions": ["reproduce"]},
    ]
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # --- contacts.json ---
    contacts = [
        {"contact_id": "c101", "name": "John Doe", "role": "maintainer", "email": "john@project-alpha.org"},
        {"contact_id": "c102", "name": "Jane Smith", "role": "contributor", "email": "jane@project-alpha.org"},
        {"contact_id": "c103", "name": "Mike Brown", "role": "user", "email": "mike@someproject.org"},
        {"contact_id": "c104", "name": "Lisa White", "role": "maintainer", "email": "lisa@another.org"},
    ]
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # --- project_docs.json ---
    project_docs = [
        {"doc_id": "doc_001", "project_id": "project-alpha", "title": "Installation Guide", "path": "docs/install.md"},
        {"doc_id": "doc_002", "project_id": "project-alpha", "title": "Bug Report: Login Crash", "path": "docs/bug_login_crash.md"},
        {"doc_id": "doc_003", "project_id": "project-alpha", "title": "API Reference", "path": "docs/api.md"},
        {"doc_id": "doc_004", "project_id": "project-beta", "title": "Overview", "path": "beta/overview.md"},
    ]
    # 注意：这里 doc_002 是 bug 文档，会被复现日志引用
    with open("data/projects/project_docs.json", "w") as f:
        json.dump(project_docs, f, indent=2)

    # --- reproduction_logs/ --- 多份日志，只有一份是 verified
    logs = [
        # Alice 成功复现（对应 doc_002）
        {
            "author": "Alice Wang",
            "date": "2025-02-10",
            "doc_id": "doc_002",
            "status": "verified",
            "notes": "Successfully reproduced the login crash with steps in the bug report."
        },
        # Bob 失败
        {
            "author": "Bob Li",
            "date": "2025-02-10",
            "doc_id": "doc_002",
            "status": "failed",
            "notes": "Could not trigger the crash; environment differs."
        },
        # Carol 未完成
        {
            "author": "Carol Chen",
            "date": "2025-02-10",
            "doc_id": "doc_002",
            "status": "pending",
            "notes": "Still setting up the test environment."
        },
        # David 复现了另一个不相关的文档（干扰）
        {
            "author": "David Zhang",
            "date": "2025-02-10",
            "doc_id": "doc_001",
            "status": "verified",
            "notes": "Installation works fine."
        },
    ]
    # 写入日志文件，文件名用 "author_date.log" 格式（用下划线代替空格）
    for log in logs:
        author_clean = log["author"].replace(" ", "_")
        filename = f"{author_clean}_{log['date']}.log"
        filepath = os.path.join("data/reproduction_logs", filename)
        # 用简单文本格式记录，每行 key: value
        lines = [
            f"author: {log['author']}",
            f"date: {log['date']}",
            f"doc_id: {log['doc_id']}",
            f"status: {log['status']}",
            f"notes: {log['notes']}",
        ]
        with open(filepath, "w") as f:
            f.write("\n".join(lines) + "\n")

if __name__ == "__main__":
    build_env()
