import os
import json

def build_env():
    # 创建主要论文数据目录
    os.makedirs("papers", exist_ok=True)

    # 论文数据（包含干扰：自引、悬空引用、重复引用）
    papers_data = [
        {
            "paper_id": "p01",
            "title": "Alpha: A Novel Approach to Graph Mining",
            "direction": "ML",
            "year": 2020,
            "keywords": ["graph", "mining", "alpha"],
            "abstract": "We propose Alpha...",
            "citation_ids": ["p02", "p03"]
        },
        {
            "paper_id": "p02",
            "title": "Beta: Scaling Deep Learning",
            "direction": "DL",
            "year": 2021,
            "keywords": ["deep", "scaling"],
            "abstract": "Beta introduces...",
            "citation_ids": ["p01", "p02", "p03"]   # 自引 p02，有效引用 p01, p03
        },
        {
            "paper_id": "p03",
            "title": "Gamma: Efficient Transformers",
            "direction": "NLP",
            "year": 2022,
            "keywords": ["transformer", "efficiency"],
            "abstract": "Gamma shows...",
            "citation_ids": ["p01", "p02", "p04"]   # p04 不存在 → 悬空
        },
        {
            "paper_id": "p04",
            "title": "Delta: Reinforcement Learning in Practice",
            "direction": "RL",
            "year": 2023,
            "keywords": ["rl", "practice"],
            "abstract": "Delta details...",
            "citation_ids": ["p01", "p01"]          # 重复引用 p01
        }
    ]

    with open("papers/papers.json", "w") as f:
        json.dump({"papers": papers_data}, f, indent=2)

    # === 干扰文件 ===
    # 1. 旧格式备份（不同结构）
    os.makedirs("legacy", exist_ok=True)
    legacy_papers = [
        {"id": "x01", "title": "Old Paper", "refs": ["x02"]}
    ]
    with open("legacy/old_papers.json", "w") as f:
        json.dump(legacy_papers, f, indent=2)

    # 2. 无关的 accounts.json
    accounts = [
        {"account_id": "a1", "display_name": "Alice", "department": "CS", "email": "alice@uni.edu", "permissions": ["admin"]}
    ]
    with open("accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # 3. 无关 contacts.json
    contacts = [
        {"contact_id": "c1", "name": "Bob", "role": "reviewer", "email": "bob@journal.org"}
    ]
    with open("contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # 4. 缓存目录（诱饵）
    os.makedirs("cache", exist_ok=True)
    with open("cache/old_citation_graph.json", "w") as f:
        json.dump({"nodes": [], "edges": []}, f)

if __name__ == "__main__":
    build_env()
