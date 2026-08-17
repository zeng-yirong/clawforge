import os
import json

def build_env():
    # 创建主数据目录
    os.makedirs("data/papers", exist_ok=True)
    os.makedirs("data/backup", exist_ok=True)
    os.makedirs("cache", exist_ok=True)  # 实际 Agent 需要创建，这里预创建空目录不影响判断

    # 最新论文库（唯一权威数据源）
    papers = [
        {
            "paper_id": "paper_a",
            "title": "A Novel Method for Graph Analysis",
            "year": 2022,
            "abstract": "We propose a new method...",
            "keywords": ["graph", "analysis"],
            "citation_ids": ["paper_b", "paper_c", "paper_z"]  # paper_z不存在
        },
        {
            "paper_id": "paper_b",
            "title": "Deep Learning on Graphs",
            "year": 2021,
            "abstract": "Deep learning techniques...",
            "keywords": ["deep learning", "graph"],
            "citation_ids": ["paper_a", "paper_d", "paper_b"]  # 自引用paper_b
        },
        {
            "paper_id": "paper_c",
            "title": "Network Embedding Survey",
            "year": 2020,
            "abstract": "A comprehensive survey...",
            "keywords": ["network", "embedding"],
            "citation_ids": ["paper_a", "paper_b", "paper_e"]
        },
        {
            "paper_id": "paper_d",
            "title": "Community Detection Algorithms",
            "year": 2023,
            "abstract": "We compare various algorithms...",
            "keywords": ["community", "detection"],
            "citation_ids": ["paper_a", "paper_z", "paper_c"]  # paper_z不存在
        },
        {
            "paper_id": "paper_e",
            "title": "Scalable Graph Processing",
            "year": 2022,
            "abstract": "A scalable framework...",
            "keywords": ["scalable", "graph"],
            "citation_ids": ["paper_a", "paper_b", "paper_c", "paper_d", "paper_e"]  # 自引用
        }
    ]
    with open("data/papers/papers.json", "w") as f:
        json.dump({"papers": papers}, f, indent=2)

    # 干扰：旧的论文库（包含不存在的论文，引用关系不同）
    old_papers = [
        {
            "paper_id": "paper_x",
            "title": "Old Method",
            "year": 2019,
            "abstract": "Outdated...",
            "keywords": ["old"],
            "citation_ids": ["paper_y"]
        },
        {
            "paper_id": "paper_y",
            "title": "Ancient Work",
            "year": 2018,
            "abstract": "Very old...",
            "keywords": ["ancient"],
            "citation_ids": ["paper_z"]
        }
    ]
    with open("data/papers/old_papers.json", "w") as f:
        json.dump({"papers": old_papers}, f, indent=2)

    # 完全无关的文件
    with open("data/backup/notes.txt", "w") as f:
        f.write("Backup of experiment logs - ignore this.\n")
    with open("readme.txt", "w") as f:
        f.write("This directory contains citation data.\n")

if __name__ == "__main__":
    build_env()
