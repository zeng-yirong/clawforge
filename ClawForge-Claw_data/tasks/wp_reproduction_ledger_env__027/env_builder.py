import os, json

# 确保必要的目录存在
os.makedirs("data/projects", exist_ok=True)
os.makedirs("data", exist_ok=True)
os.makedirs("archive", exist_ok=True)  # 空目录，让 Agent 写入输出
os.makedirs("raw_logs", exist_ok=True)  # 干扰目录

# 联系人数据
contacts = [
    {"contact_id": "c001", "name": "Alice", "role": "lead", "email": "alice@example.com"},
    {"contact_id": "c002", "name": "Bob", "role": "reviewer", "email": "bob@example.com"},
    {"contact_id": "c003", "name": "Charlie", "role": "lead", "email": "charlie@example.com"},
    {"contact_id": "c004", "name": "Diana", "role": "lead", "email": "diana@example.com"}
]
with open("data/contacts.json", "w") as f:
    json.dump(contacts, f, indent=2)

# 项目文档数据（包含干扰项）
project_docs = [
    {"doc_id": "doc001", "project_id": "proj1", "title": "Reproduction of Bug A", "status": "active", "contact_id": "c001"},
    {"doc_id": "doc002", "project_id": "proj1", "title": "Reproduction of Bug B", "status": "archived", "contact_id": "c002"},
    {"doc_id": "doc003", "project_id": "proj2", "title": "Reproduction of Feature C", "status": "active", "contact_id": "c003"},
    {"doc_id": "doc004", "project_id": "proj2", "title": "Reproduction of Feature D", "status": "active", "contact_id": "c005"},  # 联系人不存在
    {"doc_id": "doc005", "project_id": "proj3", "title": "Reproduction of Security E", "status": "active", "contact_id": "c001"},
    {"doc_id": "doc006", "project_id": "proj3", "title": "Reproduction of Security E (old)", "status": "archived", "contact_id": "c004"},
    {"doc_id": "doc007", "project_id": "proj4", "title": None, "status": "active", "contact_id": "c001"},
    {"doc_id": "doc008", "project_id": "proj4", "status": "active", "contact_id": "c001"},  # 缺少 title
    {"doc_id": "doc009", "project_id": "proj5", "title": "Test", "status": "active", "contact_id": ""}  # 空 contact_id
]
with open("data/projects/project_docs.json", "w") as f:
    json.dump(project_docs, f, indent=2)

# 干扰文件：无关的日志
with open("raw_logs/system.log", "w") as f:
    f.write("2025-03-01 03:00:00 INFO Process started\n")
with open("raw_logs/error.log", "w") as f:
    f.write("2025-03-01 03:05:00 ERROR Database timeout\n")

# 干扰文件：accounts.json (不相关)
accounts = [
    {"account_id": "a1", "display_name": "Alice", "department": "R&D", "email": "alice@company.com", "permissions": ["read", "write"]},
    {"account_id": "a2", "display_name": "Bob", "department": "QA", "email": "bob@company.com", "permissions": ["read"]}
]
with open("data/accounts.json", "w") as f:
    json.dump(accounts, f, indent=2)
