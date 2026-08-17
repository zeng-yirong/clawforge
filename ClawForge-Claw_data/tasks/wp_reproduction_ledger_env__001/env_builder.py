import os
import json

def build_env():
    # 创建 accounts.json
    accounts = {
        "accounts": [
            {
                "account_id": "a001",
                "display_name": "Alice",
                "department": "QA",
                "email": "alice@co.io",
                "permissions": ["archive"]
            },
            {
                "account_id": "a002",
                "display_name": "Bob",
                "department": "Dev",
                "email": "bob@co.io",
                "permissions": ["read"]
            }
        ]
    }
    os.makedirs("data", exist_ok=True)
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f)

    # 创建 contacts.json
    contacts = {
        "contacts": [
            {
                "contact_id": "c001",
                "name": "Charlie Support",
                "role": "Technical Support",
                "email": "charlie@support.io"
            }
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f)

    # 创建 project_docs.json
    project_docs = {
        "project_docs": [
            {
                "doc_id": "doc_alpha_001",
                "project_id": "proj-alpha",
                "title": "Reproduction Steps v1",
                "path": "docs/repro_alpha_v1.md"
            },
            {
                "doc_id": "doc_alpha_002",
                "project_id": "proj-alpha",
                "title": "Reproduction Steps v2 (Correct)",
                "path": "docs/repro_alpha_v2.md"
            },
            {
                "doc_id": "doc_beta_001",
                "project_id": "proj-beta",
                "title": "Beta Bug Report",
                "path": "docs/beta_report.md"
            }
        ]
    }
    os.makedirs("data/projects", exist_ok=True)
    with open("data/projects/project_docs.json", "w") as f:
        json.dump(project_docs, f)

    # 创建文档文件
    os.makedirs("docs", exist_ok=True)

    # 旧版（干扰）
    with open("docs/repro_alpha_v1.md", "w") as f:
        f.write("Steps: 1. Do A; 2. Do B. Result: Not fully reproduced.\n")

    # 正确版（答案）
    with open("docs/repro_alpha_v2.md", "w") as f:
        f.write("Steps: 1. Install version 2.3; 2. Run `./start.sh --debug`; 3. Observe log line 'ERROR DB'.\nResult: Database connection fails consistently.\n")

    # 无关项目
    with open("docs/beta_report.md", "w") as f:
        f.write("Steps: 1. Enable beta flag; 2. Restart service. Result: No crash.\n")

if __name__ == "__main__":
    build_env()
