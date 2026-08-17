import os
import json

def build_env():
    # 创建 papers 目录
    os.makedirs("papers", exist_ok=True)

    # 合法论文 001
    paper_001 = {
        "paper_id": "001",
        "title": "Deep Learning",
        "direction": "AI",
        "year": 2020,
        "keywords": ["neural networks", "representation"],
        "abstract": "Deep learning enables...",
        "citation_ids": ["002", "003"]
    }
    with open("papers/paper_001.json", "w") as f:
        json.dump(paper_001, f)

    # 合法论文 002
    paper_002 = {
        "paper_id": "002",
        "title": "Transformer",
        "direction": "NLP",
        "year": 2019,
        "keywords": ["attention", "sequence"],
        "abstract": "Transformer models...",
        "citation_ids": ["001"]
    }
    with open("papers/paper_002.json", "w") as f:
        json.dump(paper_002, f)

    # 合法论文 003 (无引用)
    paper_003 = {
        "paper_id": "003",
        "title": "Attention Is All You Need",
        "direction": "NLP",
        "year": 2017,
        "keywords": ["attention", "transformer"],
        "abstract": "We propose a new...",
        "citation_ids": []
    }
    with open("papers/paper_003.json", "w") as f:
        json.dump(paper_003, f)

    # 合法论文 004
    paper_004 = {
        "paper_id": "004",
        "title": "Graph Neural Networks",
        "direction": "Graph",
        "year": 2021,
        "keywords": ["graph", "deep learning"],
        "abstract": "GNNs generalize...",
        "citation_ids": ["001", "003"]
    }
    with open("papers/paper_004.json", "w") as f:
        json.dump(paper_004, f)

    # 干扰论文 005 —— 缺少 citation_ids 字段
    paper_005 = {
        "paper_id": "005",
        "title": "Draft: Incomplete",
        "direction": "AI",
        "year": 2020,
        "keywords": ["draft"],
        "abstract": "This is a draft..."
        # 缺少 citation_ids
    }
    with open("papers/paper_005.json", "w") as f:
        json.dump(paper_005, f)

    # 干扰论文 006 —— 缺少 abstract 字段
    paper_006 = {
        "paper_id": "006",
        "title": "Old Paper",
        "direction": "Misc",
        "year": 1990,
        "keywords": ["old"],
        "citation_ids": ["999"]
        # 缺少 abstract
    }
    with open("papers/paper_006.json", "w") as f:
        json.dump(paper_006, f)

    # 旧版本干扰目录
    os.makedirs("old_versions", exist_ok=True)
    old_paper = {
        "paper_id": "001",
        "title": "Deep Learning (old version)",
        "direction": "AI",
        "year": 2019,
        "keywords": ["neural"],
        "abstract": "Old abstract...",
        "citation_ids": ["002"]
    }
    with open("old_versions/paper_001_old.json", "w") as f:
        json.dump(old_paper, f)

    # 其他干扰文件
    with open("notes.txt", "w") as f:
        f.write("These are the papers we collected.\n")

    # 空 cache 目录
    os.makedirs("cache", exist_ok=True)

if __name__ == "__main__":
    build_env()
