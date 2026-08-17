import os
import json

def build_env():
    # 创建所需的目录
    os.makedirs("data/papers", exist_ok=True)
    os.makedirs("output", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    # 干扰文件：无关的 accounts
    accounts = {
        "accounts": [
            {
                "account_id": "a1",
                "display_name": "Alice",
                "department": "CS",
                "email": "alice@uni.edu",
                "permissions": ["read"]
            }
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # 干扰文件：无关的 contacts
    contacts = {
        "contacts": [
            {
                "contact_id": "c1",
                "name": "Bob",
                "role": "reviewer",
                "email": "bob@uni.edu"
            }
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # 五篇有效论文（唯一答案来源）
    papers_data = {
        "p001": {
            "paper_id": "p001",
            "title": "Alpha",
            "direction": "forward",
            "year": 2020,
            "keywords": ["AI"],
            "abstract": "Abstract alpha",
            "citation_ids": ["p002", "p003", "p999"]   # p999 不存在的论文
        },
        "p002": {
            "paper_id": "p002",
            "title": "Beta",
            "direction": "forward",
            "year": 2021,
            "keywords": ["ML"],
            "abstract": "Abstract beta",
            "citation_ids": ["p001", "p003"]
        },
        "p003": {
            "paper_id": "p003",
            "title": "Gamma",
            "direction": "forward",
            "year": 2022,
            "keywords": ["DL"],
            "abstract": "Abstract gamma",
            "citation_ids": ["p001", "p002", "p003"]   # 自引用 p003
        },
        "p004": {
            "paper_id": "p004",
            "title": "Delta",
            "direction": "forward",
            "year": 2019,
            "keywords": ["NLP"],
            "abstract": "Abstract delta",
            "citation_ids": ["p001"]
        },
        "p005": {
            "paper_id": "p005",
            "title": "Epsilon",
            "direction": "forward",
            "year": 2023,
            "keywords": ["CV"],
            "abstract": "Abstract epsilon",
            "citation_ids": []   # 无引用
        }
    }

    # 写入有效论文文件 (仅 .json 后缀)
    for pid, pdata in papers_data.items():
        with open(f"data/papers/{pid}.json", "w") as f:
            json.dump(pdata, f, indent=2)

    # 干扰文件：旧版本备份（.bak 后缀，应被忽略）
    old_p001 = {
        "paper_id": "p001",
        "title": "Alpha_old",
        "citation_ids": ["p005"]   # 若被错误读取会引入非法边
    }
    with open("data/papers/p001_old.bak", "w") as f:
        json.dump(old_p001, f, indent=2)

    # 干扰文件：内容相同的备份（.bak 后缀，也应被忽略）
    with open("data/papers/p001_backup.bak", "w") as f:
        json.dump(papers_data["p001"], f, indent=2)

    # 干扰文件：完全无关的临时 JSON
    with open("data/papers/temp.json", "w") as f:
        json.dump({"unrelated": 1}, f, indent=2)

    # 干扰文件：日志
    with open("logs/system.log", "w") as f:
        f.write("INFO: system started\n")

if __name__ == "__main__":
    build_env()
