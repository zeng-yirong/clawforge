import os
import json

def build_env():
    # 创建必要目录
    os.makedirs("data/projects", exist_ok=True)
    os.makedirs("raw_docs", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 干扰文件 —— 无关账户和联系人数据
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": [{"account_id": "a1", "display_name": "Dev", "department": "R&D", "email": "dev@x.com", "permissions": ["read"]}]}, f)
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": [{"contact_id": "c1", "name": "Alice", "role": "reviewer", "email": "alice@x.com"}]}, f)
    with open("ops/README.md", "w") as f:
        f.write("# Ops directory\n")

    # 项目文档清单（只有三个条目，第四个文档是诱饵不在清单中）
    project_docs = {
        "project_docs": [
            {"doc_id": "doc_001", "project_id": "proj-failed-1", "title": "Bug #101", "path": "raw_docs/doc_001.md"},
            {"doc_id": "doc_002", "project_id": "proj-success",   "title": "Bug #456", "path": "raw_docs/doc_002.md"},
            {"doc_id": "doc_003", "project_id": "proj-failed-2",  "title": "Bug #789", "path": "raw_docs/doc_003.md"}
        ]
    }
    with open("data/projects/project_docs.json", "w") as f:
        json.dump(project_docs, f)

    # 各文档内容（使用 YAML front matter 格式）
    doc_contents = {
        "doc_001.md": "---\nproject: proj-failed-1\nstatus: failed\ndate: 2025-03-15\n---\nSome steps failed due to timeout.",
        "doc_002.md": "---\nproject: proj-success\nstatus: success\ndate: 2025-04-01\n---\nReproduction successful! Steps: 1...",
        "doc_003.md": "---\nproject: proj-failed-2\nstatus: undefined\n---\nNo status information.",
    }
    for fname, content in doc_contents.items():
        with open(f"raw_docs/{fname}", "w") as f:
            f.write(content)

    # 诱饵文档：不在清单中，但 status 也是 success，会误导直接遍历 raw_docs 的 Agent
    with open("raw_docs/doc_004.md", "w") as f:
        f.write("---\nproject: proj-ghost\nstatus: success\ndate: 2025-04-03\n---\nThis doc is not referenced in the ledger list.")

    # 额外诱饵文件
    with open("raw_docs/temp.txt", "w") as f:
        f.write("This is a temp file.\n")

if __name__ == "__main__":
    build_env()
