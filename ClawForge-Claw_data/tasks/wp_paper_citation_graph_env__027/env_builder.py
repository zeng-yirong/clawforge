import json
import os

def build_env():
    # 创建 papers 目录
    os.makedirs("papers", exist_ok=True)
    
    # 有效论文数据 (6篇，其中一篇的文件会被故意损坏)
    papers = {
        "P001": {
            "paper_id": "P001",
            "title": "Deep Learning for NLP",
            "direction": "cs.CL",
            "year": 2020,
            "keywords": ["deep learning", "NLP"],
            "abstract": "We propose a novel architecture for natural language understanding.",
            "citation_ids": ["P002", "P003"]
        },
        "P002": {
            "paper_id": "P002",
            "title": "Attention Is All You Need",
            "direction": "cs.AI",
            "year": 2017,
            "keywords": ["attention", "transformer"],
            "abstract": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks.",
            "citation_ids": ["P001", "P004"]
        },
        "P003": {
            "paper_id": "P003",
            "title": "BERT: Pre-training of Deep Bidirectional Transformers",
            "direction": "cs.CL",
            "year": 2018,
            "keywords": ["BERT", "pre-training"],
            "abstract": "We introduce a new language representation model called BERT.",
            "citation_ids": ["P002", "P005"]
        },
        "P004": {
            "paper_id": "P004",
            "title": "Generative Adversarial Nets",
            "direction": "cs.LG",
            "year": 2014,
            "keywords": ["GAN", "generative"],
            "abstract": "We propose a new framework for estimating generative models via an adversarial process.",
            "citation_ids": ["P005"]
        },
        "P005": {
            "paper_id": "P005",
            "title": "ImageNet Classification with Deep Convolutional Neural Networks",
            "direction": "cs.CV",
            "year": 2012,
            "keywords": ["CNN", "ImageNet"],
            "abstract": "We trained a large, deep convolutional neural network to classify the 1.2 million high-resolution images.",
            "citation_ids": ["P001", "P006"]  # P006 不存在（该论文文件损坏）
        },
        "P006": {
            "paper_id": "P006",
            "title": "A Broken Paper",
            "direction": "cs.IR",
            "year": 2021,
            "keywords": ["broken"],
            "abstract": "This file will be deliberately malformed.",
            "citation_ids": ["P001"]
        }
    }
    
    # 写入有效论文文件 (P001-P005 正常)
    for pid in ["P001", "P002", "P003", "P004", "P005"]:
        with open(f"papers/{pid}.json", "w", encoding="utf-8") as f:
            json.dump(papers[pid], f, indent=2)
    
    # 故意使 P006 文件损坏（缺少逗号，或者截断）
    with open("papers/P006.json", "w", encoding="utf-8") as f:
        f.write('{"paper_id": "P006", "title": "A Broken Paper", "citation_ids": ["P001"]')   # 缺少 closing }
    
    # 添加干扰文件：一个非 JSON 文本文件
    with open("papers/notes.txt", "w", encoding="utf-8") as f:
        f.write("These are just some scratch notes, ignore me.\n")
    
    # 添加一个格式完全错误的 JSON 文件（非论文结构）
    with open("papers/random.json", "w", encoding="utf-8") as f:
        json.dump({"foo": "bar"}, f, indent=2)
    
    # 创建 graph 目录（但留空，让 agent 写入）
    os.makedirs("graph", exist_ok=True)

if __name__ == "__main__":
    build_env()
