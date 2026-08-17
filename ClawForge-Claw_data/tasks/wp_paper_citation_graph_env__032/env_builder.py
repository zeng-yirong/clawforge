import os
import json

def build_env():
    # 创建必要目录
    os.makedirs("papers", exist_ok=True)
    os.makedirs("cache", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    # 生成论文数据（含干扰引用的脏数据）
    papers = [
        {
            "paper_id": "paper_001",
            "title": "Deep Learning",
            "direction": "AI",
            "year": 2020,
            "keywords": ["neural", "network"],
            "abstract": "A deep learning survey.",
            "citation_ids": ["paper_002", "paper_003"]
        },
        {
            "paper_id": "paper_002",
            "title": "GANs",
            "direction": "CV",
            "year": 2021,
            "keywords": ["generative"],
            "abstract": "Generative Adversarial Networks.",
            "citation_ids": ["paper_003"]
        },
        {
            "paper_id": "paper_003",
            "title": "Transformers",
            "direction": "NLP",
            "year": 2019,
            "keywords": ["attention"],
            "abstract": "Transformer architecture.",
            "citation_ids": ["paper_004", "paper_005"]
        },
        {
            "paper_id": "paper_004",
            "title": "Attention",
            "direction": "NLP",
            "year": 2018,
            "keywords": ["seq2seq"],
            "abstract": "Attention mechanism.",
            "citation_ids": ["paper_002", "paper_999"]  # paper_999 不存在
        },
        {
            "paper_id": "paper_005",
            "title": "CNN",
            "direction": "CV",
            "year": 2017,
            "keywords": ["convolution"],
            "abstract": "Convolutional neural networks.",
            "citation_ids": ["paper_001", "paper_002", "paper_005"]  # 含自引用
        }
    ]

    # 写入官方论文列表
    with open("papers/papers.json", "w") as f:
        json.dump({"papers": papers}, f, indent=2)

    # 创建干扰文件（过期版本、日志等）
    # 老旧论文列表（部分过时）
    old_papers = [
        {
            "paper_id": "paper_000",
            "title": "Old ML",
            "citation_ids": ["paper_001"]
        }
    ]
    with open("papers/old_papers.json", "w") as f:
        json.dump(old_papers, f, indent=2)

    # 一些无用的日志文件
    with open("logs/error_2023.log", "w") as f:
        f.write("ERROR: failed to parse paper_001 abstract\n")
    with open("logs/debug.log", "w") as f:
        f.write("DEBUG: loaded 6 papers\n")

    # 一个错误格式的cache占位（诱饵）
    with open("cache/broken_graph.json", "w") as f:
        f.write("not json at all")

    # 一个已有的不完整图（旧版本）
    with open("cache/old_citation_graph.json", "w") as f:
        json.dump({"nodes": [], "edges": []}, f, indent=2)

if __name__ == "__main__":
    build_env()
