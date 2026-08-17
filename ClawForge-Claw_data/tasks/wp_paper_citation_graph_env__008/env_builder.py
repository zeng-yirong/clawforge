import os
import json

def build_env():
    # 创建论文数据目录
    os.makedirs("data/papers", exist_ok=True)
    # 创建 cache 目录（让 agent 写入用）
    os.makedirs("cache", exist_ok=True)

    # 论文列表：包含有效引用和无效引用（干扰项）
    papers = [
        {
            "paper_id": "p1",
            "title": "Deep Learning for NLP",
            "direction": "CS",
            "year": 2020,
            "keywords": ["deep learning", "NLP"],
            "abstract": "This paper explores...",
            "citation_ids": ["p2", "p3"]
        },
        {
            "paper_id": "p2",
            "title": "Attention Mechanisms",
            "direction": "CS",
            "year": 2019,
            "keywords": ["attention"],
            "abstract": "We propose...",
            "citation_ids": ["p4"]
        },
        {
            "paper_id": "p3",
            "title": "Transformers in Vision",
            "direction": "CV",
            "year": 2021,
            "keywords": ["transformer"],
            "abstract": "Applying transformers...",
            "citation_ids": ["p5"]   # p5 不存在 → 无效
        },
        {
            "paper_id": "p4",
            "title": "Graph Neural Networks",
            "direction": "CS",
            "year": 2018,
            "keywords": ["graph"],
            "abstract": "GNN overview...",
            "citation_ids": []
        },
        {
            "paper_id": "p6",
            "title": "Reinforcement Learning Basics",
            "direction": "ML",
            "year": 2017,
            "keywords": ["RL"],
            "abstract": "Intro to RL...",
            "citation_ids": ["p99"]  # p99 不存在 → 无效
        }
    ]

    with open("data/papers/papers.json", "w") as f:
        json.dump({"papers": papers}, f, indent=2)

    # 干扰文件：其他业务数据，不参与引用图
    accounts = [
        {"account_id": "a1", "display_name": "Alice", "department": "cs", "email": "alice@uni.edu", "permissions": ["read", "write"]},
        {"account_id": "a2", "display_name": "Bob", "department": "math", "email": "bob@uni.edu", "permissions": ["read"]}
    ]
    os.makedirs("data", exist_ok=True)
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    contacts = [
        {"contact_id": "c1", "name": "Charlie", "role": "reviewer", "email": "charlie@conf.org"},
        {"contact_id": "c2", "name": "Diana", "role": "author", "email": "diana@paper.org"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

if __name__ == "__main__":
    build_env()
