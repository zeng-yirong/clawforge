import os
import json
import random
import string
from datetime import datetime

def build_env():
    # 确保目录存在
    os.makedirs("project_docs", exist_ok=True)
    os.makedirs("ledger", exist_ok=True)

    # ---- 干扰文件：accounts.json ----
    accounts = {
        "accounts": [
            {"account_id": "acc-001", "display_name": "Alice", "department": "AI Research", "email": "alice@lab.com", "permissions": ["read", "write"]},
            {"account_id": "acc-002", "display_name": "Bob", "department": "Infra", "email": "bob@lab.com", "permissions": ["read"]},
        ]
    }
    with open("project_docs/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # ---- 干扰文件：contacts.json ----
    contacts = {
        "contacts": [
            {"contact_id": "con-001", "name": "Charlie", "role": "reviewer", "email": "charlie@lab.com"},
            {"contact_id": "con-002", "name": "Diana", "role": "lead", "email": "diana@lab.com"},
        ]
    }
    with open("project_docs/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # ---- 目标文档：proj-018，标题匹配 ----
    target_doc = {
        "doc_id": "doc-001",
        "project_id": "proj-018",
        "title": "Reproduction Steps for Model v2",
        "path": "project_docs/doc_proj018.json",
        "status": "active",
        "steps": [
            "1. 配置 Python 3.10 环境并安装 requirements.txt",
            "2. 下载模型权重 v2.1 至 ./weights/",
            "3. 运行 preprocessing_script.sh --input data/raw --output data/clean",
            "4. 执行训练脚本: python train.py --config configs/proj018.yaml",
            "5. 验证损失曲线收敛至 0.023 以下",
            "6. 输出来自测试集的 F1-score: 0.912"
        ],
        "result": "成功复现模型 v2，最终 F1 分数 0.912，符合论文预期。"
    }
    with open("project_docs/doc_proj018.json", "w") as f:
        json.dump(target_doc, f, indent=2)

    # ---- 干扰文档1：同一项目但已废弃 ----
    deprecated_doc = {
        "doc_id": "doc-002",
        "project_id": "proj-018",
        "title": "Reproduction Steps for Model v1 (deprecated)",
        "path": "project_docs/doc_proj018_v1.json",
        "status": "deprecated",
        "steps": [
            "步骤已过时",
            "使用老版本权重"
        ],
        "result": "不再适用"
    }
    with open("project_docs/doc_proj018_v1.json", "w") as f:
        json.dump(deprecated_doc, f, indent=2)

    # ---- 干扰文档2：不同项目，但标题相似 ----
    other_project_doc = {
        "doc_id": "doc-003",
        "project_id": "proj-019",
        "title": "Reproduction Steps for Model v2 (alpha)",
        "path": "project_docs/doc_proj019.json",
        "status": "active",
        "steps": [
            "1. 安装特定依赖",
            "2. 运行不同脚本"
        ],
        "result": "部分成功"
    }
    with open("project_docs/doc_proj019.json", "w") as f:
        json.dump(other_project_doc, f, indent=2)

    # ---- 干扰文件：一个无关的文本文件 ----
    with open("project_docs/notes.txt", "w") as f:
        f.write("这是无关的笔记，不要管我。\n")

    # ---- 在 ledger 目录下留一个空文件作为诱饵 ----
    with open("ledger/temp_log.txt", "w") as f:
        f.write("临时日志，可忽略\n")

if __name__ == "__main__":
    build_env()
