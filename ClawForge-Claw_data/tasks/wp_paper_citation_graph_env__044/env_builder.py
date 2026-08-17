import os
import json

def build_env():
    # 创建目录结构
    os.makedirs("papers/published", exist_ok=True)
    os.makedirs("papers/drafts", exist_ok=True)
    os.makedirs("output", exist_ok=True)  # 占位，agent会写入

    # ---------- published 论文 ----------
    published_papers = [
        {
            "paper_id": "001",
            "title": "Graph Attention Networks",
            "year": 2020,
            "abstract": "We propose a novel graph attention layer that aggregates neighbor features with learnable attention weights.",
            "keywords": ["graph neural networks", "attention"],
            "citation_ids": ["002", "003", "001"]   # 自引用 + 正常
        },
        {
            "paper_id": "002",
            "title": "Graph Convolutional Networks",
            "year": 2018,
            "abstract": "We present a scalable approach for semi-supervised learning on graph-structured data using convolutional architectures.",
            "keywords": ["graph convolution", "semi-supervised"],
            "citation_ids": ["003", "004"]           # 引用了不存在的004
        },
        {
            "paper_id": "003",
            "title": "GraphSAGE",
            "year": 2019,
            "abstract": "We introduce a framework for inductive node embedding on large graphs using sampling and aggregation.",
            "keywords": ["inductive learning", "graph sampling"],
            "citation_ids": ["001", "002", "003"]   # 自引用 + 重复正常
        },
        {
            "paper_id": "005",
            "title": "node2vec",
            "year": 2020,
            "abstract": "We propose a scalable representation learning method for networks that maps nodes to low-dimensional vectors.",
            "keywords": ["network embedding", "random walk"],
            "citation_ids": ["001", "006"]           # 006不存在
        }
    ]

    for paper in published_papers:
        with open(f"papers/published/paper_{paper['paper_id']}.json", "w") as f:
            json.dump(paper, f)

    # ---------- drafts 干扰论文 ----------
    drafts = [
        {
            "paper_id": "001",
            "title": "GAT (old draft)",
            "year": 2019,
            "abstract": "旧版摘要",
            "keywords": [],
            "citation_ids": ["002"]                  # 仅引用002，与published不同
        },
        {
            "paper_id": "007",
            "title": "Ancient Survey",
            "year": 2005,
            "abstract": "",
            "keywords": ["survey"],
            "citation_ids": ["001"]
        },
        {
            "paper_id": "008",
            "title": "New Draft",
            "year": 2021,
            "abstract": "Some preliminary ideas.",
            "keywords": ["draft"],
            "citation_ids": []
        }
    ]
    for paper in drafts:
        with open(f"papers/drafts/paper_{paper['paper_id']}.json", "w") as f:
            json.dump(paper, f)

    # 在output目录创建占位文件（防止agent没创建时verifier报错）
    # 可以让它不存在，更严格
    # 不创建，agent必须自己写

if __name__ == "__main__":
    build_env()
