import os
import json

def build_env():
    # 创建所需目录
    os.makedirs("data/projects", exist_ok=True)
    os.makedirs("docs", exist_ok=True)
    os.makedirs("raw_logs", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 1. 干扰数据：accounts.json
    accounts = {
        "accounts": [
            {"account_id": "a001", "display_name": "Alice", "department": "Engineering", "email": "alice@example.com", "permissions": ["read", "write"]},
            {"account_id": "a002", "display_name": "Bob", "department": "QA", "email": "bob@example.com", "permissions": ["read"]},
            {"account_id": "a003", "display_name": "Charlie", "department": "DevOps", "email": "charlie@example.com", "permissions": ["admin"]}
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # 2. 干扰数据：contacts.json
    contacts = {
        "contacts": [
            {"contact_id": "c001", "name": "Dave", "role": "Maintainer", "email": "dave@project.org"},
            {"contact_id": "c002", "name": "Eve", "role": "Contributor", "email": "eve@project.org"}
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # 3. 核心数据：project_docs.json（包含目标文档和干扰文档）
    project_docs = {
        "project_docs": [
            {
                "doc_id": "doc_001",
                "project_id": "proj_llm",
                "title": "Getting Started",
                "path": "docs/getting_started.md"
            },
            {
                "doc_id": "doc_002",
                "project_id": "proj_llm",
                "title": "API Reference",
                "path": "docs/api_reference.md"
            },
            {
                "doc_id": "doc_007",
                "project_id": "proj_llm",
                "title": "Memory Leak in Cache Layer",
                "path": "docs/memory_leak.md"
            },
            {
                "doc_id": "doc_003",
                "project_id": "proj_llm",
                "title": "Deployment Guide",
                "path": "docs/deployment.md"
            }
        ]
    }
    with open("data/projects/project_docs.json", "w") as f:
        json.dump(project_docs, f, indent=2)

    # 4. 目标文档：memory_leak.md（复现步骤，每行一条，无编号）
    steps_content = "Start the cache server with default config.\n" \
                   "Send 10000 requests with large payloads.\n" \
                   "Observe memory usage > 1GB.\n" \
                   "Stop the server and restart.\n" \
                   "Memory not released.\n"
    with open("docs/memory_leak.md", "w") as f:
        f.write(steps_content)

    # 5. 干扰文档：其他 .md 文件（内容不同）
    with open("docs/getting_started.md", "w") as f:
        f.write("# Getting Started\nInstall with pip.\n")
    with open("docs/api_reference.md", "w") as f:
        f.write("# API\nendpoint /v1/query.\n")
    with open("docs/deployment.md", "w") as f:
        f.write("# Deployment\nUse Docker.\n")

    # 6. 干扰日志
    with open("raw_logs/system.log", "w") as f:
        f.write("[INFO] 2025-02-10 10:00:00 Server started\n")
        f.write("[ERROR] 2025-02-10 10:05:00 Out of memory\n")

if __name__ == "__main__":
    build_env()
