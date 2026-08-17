import os
import json
import random

def build_env():
    # 确保工作目录是 .
    cwd = os.getcwd()
    # 创建目录
    dirs = [
        "data/papers/current",
        "data/papers/backup",
        "data/papers/archive",
        "cache",
        "logs"
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # ---- 真实论文数据（唯一正确答案） ----
    papers_current = [
        {
            "paper_id": "p001",
            "title": "Deep Learning for NLP",
            "direction": "AI",
            "year": 2020,
            "keywords": ["NLP", "deep learning"],
            "abstract": "This paper explores deep learning methods for natural language processing.",
            "citation_ids": ["p002", "p003"]
        },
        {
            "paper_id": "p002",
            "title": "Attention Mechanisms",
            "direction": "AI",
            "year": 2019,
            "keywords": ["attention", "transformer"],
            "abstract": "A comprehensive review of attention mechanisms in neural networks.",
            "citation_ids": ["p003", "p004"]
        },
        {
            "paper_id": "p003",
            "title": "Graph Neural Networks",
            "direction": "AI",
            "year": 2021,
            "keywords": ["GNN", "graph"],
            "abstract": "Introduction to graph neural networks and their applications.",
            "citation_ids": ["p004"]
        },
        {
            "paper_id": "p004",
            "title": "Reinforcement Learning Basics",
            "direction": "ML",
            "year": 2018,
            "keywords": ["RL", "basics"],
            "abstract": "Foundations of reinforcement learning.",
            "citation_ids": []
        },
        {
            "paper_id": "p005",
            "title": "Quantum Computing",
            "direction": "Physics",
            "year": 2022,
            "keywords": ["quantum"],
            "abstract": "Quantum computing for beginners.",
            "citation_ids": ["p001", "p003"]
        }
    ]
    with open("data/papers/current/papers.json", "w") as f:
        json.dump({"papers": papers_current}, f, indent=2)

    # ---- 干扰：过期备份（引用关系不同，但不应被使用） ----
    papers_backup = [
        {
            "paper_id": "p001",
            "title": "Deep Learning for NLP (old)",
            "direction": "AI",
            "year": 2019,
            "keywords": ["NLP"],
            "abstract": "Older version.",
            "citation_ids": ["p002"]
        },
        {
            "paper_id": "p002",
            "title": "Attention Mechanisms (old)",
            "direction": "AI",
            "year": 2018,
            "keywords": ["attention"],
            "abstract": "Old.",
            "citation_ids": []
        }
    ]
    with open("data/papers/backup/papers.json", "w") as f:
        json.dump({"papers": papers_backup}, f, indent=2)

    # ---- 干扰：无关日志文件 ----
    with open("logs/server.log", "w") as f:
        f.write("INFO: 2024-01-01 00:00:00 system started\n")
        f.write("WARN: memory usage high\n")

    # ---- 干扰：一个 CSV 文件（假装是论文列表但格式不对） ----
    with open("data/papers/archive/old_papers.csv", "w") as f:
        f.write("paper_id,title,year\n")
        f.write("p011,Some Old Paper,2017\n")
        f.write("p012,Another Old,2016\n")

    # ---- 干扰：一个包含无效引用的 papers.json 在 archive 下（可能被误读） ----
    papers_archive = [
        {
            "paper_id": "p010",
            "title": "Invalid Paper",
            "direction": "Fake",
            "year": 2000,
            "keywords": [],
            "abstract": "This paper references non-existent IDs.",
            "citation_ids": ["p999", "p888"]
        }
    ]
    with open("data/papers/archive/papers.json", "w") as f:
        json.dump({"papers": papers_archive}, f, indent=2)

    # ---- 干扰：一个文本文件在 current 下，不是 json ----
    with open("data/papers/current/readme.txt", "w") as f:
        f.write("This directory contains the latest paper data.\n")

    # ---- 干扰：在 cache 下预先放一个假文件（防止agent直接修改） ----
    with open("cache/citation_graph.json", "w") as f:
        f.write("{\"fake\": true}\n")

if __name__ == "__main__":
    build_env()
