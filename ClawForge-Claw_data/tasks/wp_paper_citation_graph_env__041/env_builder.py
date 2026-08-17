import os
import json
import random

def build_env():
    # 创建 papers 目录
    os.makedirs("papers", exist_ok=True)

    # 定义有效论文（年份 > 2015，字段完整）
    papers = {
        "P001": {
            "paper_id": "P001",
            "title": "Deep Learning for Citation Networks",
            "direction": "AI",
            "year": 2017,
            "keywords": ["deep learning", "citation"],
            "abstract": "We propose a novel deep learning method for modeling citation networks.",
            "citation_ids": ["P004", "P005"]
        },
        "P004": {
            "paper_id": "P004",
            "title": "Graph Neural Networks in Literature Mining",
            "direction": "NLP",
            "year": 2018,
            "keywords": ["graph neural network", "literature"],
            "abstract": "This paper applies GNNs to extract relationships from academic literature.",
            "citation_ids": ["P005", "P006"]
        },
        "P005": {
            "paper_id": "P005",
            "title": "Attention Mechanisms for Citation Analysis",
            "direction": "AI",
            "year": 2019,
            "keywords": ["attention", "citation analysis"],
            "abstract": "We explore attention-based models for citation graph prediction.",
            "citation_ids": ["P001"]
        },
        "P006": {
            "paper_id": "P006",
            "title": "Temporal Dynamics of Research Impact",
            "direction": "Scientometrics",
            "year": 2020,
            "keywords": ["temporal", "impact"],
            "abstract": "A study on how citation patterns evolve over time.",
            "citation_ids": ["P007"]
        },
        "P007": {
            "paper_id": "P007",
            "title": "Benchmarking Citation Graph Datasets",
            "direction": "ML",
            "year": 2021,
            "keywords": ["benchmark", "dataset"],
            "abstract": "We introduce a new benchmark for citation graph learning tasks.",
            "citation_ids": ["P001", "P004"]
        }
    }

    # 写入有效论文（每个文件以 paper_id 命名）
    for pid, data in papers.items():
        filepath = os.path.join("papers", f"{pid}.json")
        with open(filepath, "w") as f:
            json.dump(data, f)

    # 干扰文件 1：年份太旧 (2014)
    stale_paper = {
        "paper_id": "P002",
        "title": "Old School Citation Methods",
        "direction": "CS",
        "year": 2014,
        "keywords": ["old"],
        "abstract": "This is outdated.",
        "citation_ids": ["P001"]
    }
    with open(os.path.join("papers", "P002_old.json"), "w") as f:
        json.dump(stale_paper, f)

    # 干扰文件 2：缺少 citation_ids 字段
    incomplete_paper = {
        "paper_id": "P003",
        "title": "Incomplete Paper",
        "direction": "Physics",
        "year": 2016,
        "keywords": ["missing"],
        "abstract": "No citation list here."
        # 没有 citation_ids
    }
    with open(os.path.join("papers", "P003_bad.json"), "w") as f:
        json.dump(incomplete_paper, f)

    # 干扰文件 3：非 JSON 文本文件
    with open(os.path.join("papers", "note.txt"), "w") as f:
        f.write("This is a note, not a paper.\n")

    # 干扰文件 4：JSON 但 abstract 为空字符串
    empty_abstract = {
        "paper_id": "P008",
        "title": "Empty Abstract Paper",
        "direction": "Math",
        "year": 2019,
        "keywords": [],
        "abstract": "",
        "citation_ids": ["P001"]
    }
    with open(os.path.join("papers", "P008_empty.json"), "w") as f:
        json.dump(empty_abstract, f)

    # 干扰文件 5：CSV 文件
    with open(os.path.join("papers", "extra.csv"), "w") as f:
        f.write("id,title\nX001,Some title\n")

if __name__ == "__main__":
    build_env()
