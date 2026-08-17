import os
import json

def build():
    # 确保目录存在
    os.makedirs("data/projects", exist_ok=True)
    os.makedirs("docs", exist_ok=True)
    os.makedirs("reproduction_ledger", exist_ok=True)

    # 定义文档内容：每个文档包含 steps 列表
    doc_contents = {
        "doc_alpha": {
            "steps": ["load dataset", "tune hyperparameter", "train model", "evaluate metric"]
        },
        "doc_beta": {
            "steps": ["preprocess data", "train model", "evaluate metric", "visualize result"]
        },
        "doc_gamma": {
            "steps": ["install environment", "load dataset", "train model", "evaluate metric"]
        },
        "doc_delta": {
            "steps": ["preprocess data", "feature engineering", "tune hyperparameter"]
        },
        "doc_epsilon": {
            "steps": ["install environment", "load dataset", "train model", "evaluate metric"]  # 与 doc_gamma 有重复
        },
    }

    # 写入各个文档文件
    for doc_id, content in doc_contents.items():
        filepath = f"docs/{doc_id}.json"
        with open(filepath, "w") as f:
            json.dump(content, f)

    # 创建一个不属于 proj-007 的干扰文档
    doc_intruder = {
        "steps": ["setup", "run simulation", "collect data"]
    }
    with open("docs/doc_zeta.json", "w") as f:
        json.dump(doc_intruder, f)    # 属于 proj-003

    # 创建一个非 JSON 文件干扰项
    with open("docs/readme.txt", "w") as f:
        f.write("This is a plain text file, not a steps document.")

    # 创建 project_docs.json 索引
    project_docs = [
        {"doc_id": "doc_alpha",  "project_id": "proj-007", "title": "Alpha experiment",  "path": "docs/doc_alpha.json"},
        {"doc_id": "doc_beta",   "project_id": "proj-007", "title": "Beta experiment",   "path": "docs/doc_beta.json"},
        {"doc_id": "doc_gamma",  "project_id": "proj-007", "title": "Gamma experiment",  "path": "docs/doc_gamma.json"},
        {"doc_id": "doc_delta",  "project_id": "proj-007", "title": "Delta experiment",  "path": "docs/doc_delta.json"},
        {"doc_id": "doc_epsilon","project_id": "proj-007", "title": "Epsilon experiment","path": "docs/doc_epsilon.json"},
        {"doc_id": "doc_zeta",   "project_id": "proj-003", "title": "Zeta experiment",   "path": "docs/doc_zeta.json"},
    ]
    with open("data/projects/project_docs.json", "w") as f:
        json.dump({"project_docs": project_docs}, f)

    # 创建 accounts.json 和 contacts.json 作为干扰/上下文
    accounts = {
        "accounts": [
            {"account_id": "acc-001", "display_name": "Jen", "department": "lab", "email": "jen@lab.org", "permissions": ["admin"]},
            {"account_id": "acc-002", "display_name": "Bob", "department": "ops", "email": "bob@ops.org", "permissions": ["read"]}
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f)

    contacts = {
        "contacts": [
            {"contact_id": "c-001", "name": "Alice", "role": "researcher", "email": "alice@lab.org"},
            {"contact_id": "c-002", "name": "Charlie", "role": "maintainer", "email": "charlie@lab.org"}
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f)

if __name__ == "__main__":
    build()
