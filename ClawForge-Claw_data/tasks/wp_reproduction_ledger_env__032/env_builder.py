import os
import json
import shutil

def build_env():
    # 清理并重建目录（防止重复运行）
    dirs_to_clean = ["data", "raw_logs", "ops"]
    for d in dirs_to_clean:
        if os.path.exists(d):
            shutil.rmtree(d)
    # 创建必要目录
    os.makedirs("data/projects", exist_ok=True)
    os.makedirs("raw_logs", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # ------ 1. 创建项目文档索引（含干扰项） ------
    project_docs = [
        {
            "doc_id": "doc-001",
            "project_id": "proj-alpha",
            "title": "Setup Guide",
            "path": "docs/doc001_setup.md"
        },
        {
            "doc_id": "doc-002",
            "project_id": "proj-beta",
            "title": "API Reference",
            "path": "docs/doc002_api.md"
        },
        {
            "doc_id": "doc-003",
            "project_id": "proj-gamma",
            "title": "Troubleshooting FAQ",
            "path": "docs/doc003_troubleshoot.md"
        },
        # 干扰项：这两个文档没有在日志中出现
        {
            "doc_id": "doc-004",
            "project_id": "proj-alpha",
            "title": "Migration Notes",
            "path": "docs/doc004_migration.md"
        },
        {
            "doc_id": "doc-005",
            "project_id": "proj-delta",
            "title": "Deprecated Features",
            "path": "docs/doc005_deprecated.md"
        }
    ]
    with open("data/projects/project_docs.json", "w") as f:
        json.dump({"project_docs": project_docs}, f, indent=2)

    # ------ 2. 创建干扰的数据文件（accounts, contacts） ------
    accounts = [
        {"account_id": "a001", "display_name": "Alice", "department": "R&D", "email": "alice@example.com", "permissions": ["read", "write"]},
        {"account_id": "a002", "display_name": "Bob", "department": "QA", "email": "bob@example.com", "permissions": ["read"]}
    ]
    os.makedirs("data", exist_ok=True)
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    contacts = [
        {"contact_id": "c001", "name": "Charlie", "role": "Maintainer", "email": "charlie@project.org"},
        {"contact_id": "c002", "name": "Diana", "role": "Contributor", "email": "diana@project.org"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # ------ 3. 创建部分文档文件（诱饵，但实际验证只关心日志内容） ------
    os.makedirs("docs", exist_ok=True)
    # doc-001 的文件存在
    with open("docs/doc001_setup.md", "w") as f:
        f.write("# Setup Guide\n\nSteps to install...\n")
    # doc-002 的文件存在
    with open("docs/doc002_api.md", "w") as f:
        f.write("# API Reference\n\nEndpoints...\n")
    # doc-003 的文件故意缺失（模拟复现失败原因）
    # doc-004、doc-005 的文件也存在作为干扰
    with open("docs/doc004_migration.md", "w") as f:
        f.write("# Migration Notes\n\nUpgrade path...\n")
    with open("docs/doc005_deprecated.md", "w") as f:
        f.write("# Deprecated Features\n\nOld APIs...\n")

    # ------ 4. 创建复现日志（唯一答案来源） ------
    log_entries = [
        {"doc_id": "doc-001", "status": "success", "timestamp": "2025-03-01T10:00:00Z"},
        {"doc_id": "doc-002", "status": "success", "timestamp": "2025-03-01T10:05:00Z"},
        {"doc_id": "doc-003", "status": "failed", "error": "missing dependency", "timestamp": "2025-03-01T10:10:00Z"}
    ]
    with open("raw_logs/reproduction.log", "w") as f:
        for entry in log_entries:
            f.write(json.dumps(entry) + "\n")

if __name__ == "__main__":
    build_env()
