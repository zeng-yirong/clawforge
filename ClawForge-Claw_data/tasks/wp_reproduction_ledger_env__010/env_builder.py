import csv
import json
import os

def build_env():
    # 创建目录结构
    os.makedirs("data/projects", exist_ok=True)
    os.makedirs("ops", exist_ok=False)  # 故意不创建，agent需要自己创建

    # 1. 项目文档 (project_docs.json)
    project_docs = {
        "project_docs": [
            {"doc_id": "doc1", "project_id": "proj-alpha", "title": "Alpha Project Doc", "path": "docs/alpha.md", "status": "active"},
            {"doc_id": "doc2", "project_id": "proj-beta",  "title": "Beta Project Doc",  "path": "docs/beta.md",  "status": "archived"},
            {"doc_id": "doc3", "project_id": "proj-gamma", "title": "Gamma Project Doc", "path": "docs/gamma.md", "status": "active"},
            {"doc_id": "doc4", "project_id": "proj-delta", "title": "Delta Project Doc", "path": "docs/delta.md", "status": "archived"},
            {"doc_id": "doc5", "project_id": "proj-epsilon", "title": "Epsilon Project Doc", "path": "docs/epsilon.md", "status": "active"}
        ]
    }
    with open("data/projects/project_docs.json", "w") as f:
        json.dump(project_docs, f, indent=2)

    # 2. 复现尝试记录 (project_ledgers.csv)
    rows = [
        ["issue_id", "project_name", "reproducibility", "reproduction_date", "notes"],
        ["I-001", "proj-alpha", "yes", "2025-01-10", "First success"],
        ["I-002", "proj-alpha", "no",  "2025-01-12", "Failed"],
        ["I-003", "proj-alpha", "yes", "2025-01-15", "Second success"],
        ["I-004", "proj-beta",  "yes", "2025-01-08", "Beta success"],
        ["I-005", "proj-gamma", "no",  "2025-01-09", "Gamma failed"],
        ["I-006", "proj-gamma", "yes", "2025-01-11", "Gamma success"],
        ["I-007", "proj-delta", "yes", "2025-01-07", "Delta success"],
        ["I-008", "proj-epsilon", "yes", "2025-01-14", "Epsilon only success"],
        ["I-009", "proj-alpha", "yes", "2025-01-16", "Most recent alpha"],
        ["I-010", "proj-alpha", "no",  "2025-01-17", "Failed again"],
        ["I-011", "proj-gamma", "no",  "2025-01-12", "Gamma another fail"],
        ["I-012", "proj-beta",  "yes", "2025-01-13", "Beta second success"],
        ["I-013", "proj-gamma", "yes", "2025-01-14", "Gamma most recent success"],
        ["I-014", "proj-delta", "no",  "2025-01-06", "Delta fail"],
        ["I-015", "proj-epsilon", "yes", "2025-01-16", "Epsilon second"],
        ["I-016", "proj-epsilon", "yes", "2025-01-17", "Epsilon most recent"],
        ["I-017", "proj-alpha", "yes", "2025-01-18", "Alpha after most recent? but later"]
    ]
    with open("project_ledgers.csv", "w", newline="") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerows(rows)

    # 3. 干扰文件 (accounts / contacts)
    accounts = {
        "accounts": [
            {"account_id": "acc1", "display_name": "Alice", "department": "R&D", "email": "alice@example.com", "permissions": ["read", "write"]},
            {"account_id": "acc2", "display_name": "Bob",   "department": "QA",   "email": "bob@example.com",   "permissions": ["read"]}
        ]
    }
    contacts = {
        "contacts": [
            {"contact_id": "con1", "name": "Charlie", "role": "maintainer", "email": "charlie@example.com"},
            {"contact_id": "con2", "name": "Diana",   "role": "contributor", "email": "diana@example.com"}
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

if __name__ == "__main__":
    build_env()
