import os
import json
import shutil

def build_env():
    # 清理旧数据
    for d in ["data", "cache"]:
        if os.path.exists(d):
            shutil.rmtree(d)
    os.makedirs("data/papers")
    os.makedirs("cache")

    # 有效论文（5篇，有引用关系）
    papers = [
        {
            "paper_id": "p001",
            "title": "Deep Learning for NLP",
            "year": 2020,
            "keywords": ["deep learning", "NLP"],
            "abstract": "This paper introduces a deep learning approach to NLP.",
            "citation_ids": ["p002", "p003"]   # 有效
        },
        {
            "paper_id": "p002",
            "title": "Attention Is All You Need",
            "year": 2017,
            "keywords": ["attention", "transformer"],
            "abstract": "We propose a new network architecture, the Transformer.",
            "citation_ids": ["p004"]           # 有效
        },
        {
            "paper_id": "p003",
            "title": "BERT: Pre-training of Deep Bidirectional Transformers",
            "year": 2018,
            "keywords": ["BERT", "pre-training"],
            "abstract": "We introduce BERT, a language representation model.",
            "citation_ids": ["p002", "p005"]   # p005 不存在 -> 无效
        },
        {
            "paper_id": "p004",
            "title": "ImageNet Classification with Deep Convolutional Neural Networks",
            "year": 2012,
            "keywords": ["CNN", "ImageNet"],
            "abstract": "We trained a large deep convolutional neural network.",
            "citation_ids": []                  # 无引用
        },
        {
            "paper_id": "p005_alias",           # 注意：实际 paper_id 是 p005_alias 而非 p005
            "title": "A fake paper",
            "year": 2019,
            "keywords": ["fake"],
            "abstract": "This paper is a decoy.",
            "citation_ids": ["p001"]
        }
    ]

    # 写入官方 papers.json
    with open("data/papers/papers.json", "w") as f:
        json.dump({"papers": papers}, f, indent=2)

    # 干扰：旧版 papers_old.json（格式不同，且包含已删除的论文）
    old_papers = [
        {"pid": "p999", "title": "Old paper", "refs": ["p001"]}
    ]
    with open("data/papers/papers_old.json", "w") as f:
        json.dump({"papers": old_papers}, f, indent=2)

    # 干扰：非论文目录
    os.makedirs("data/errata", exist_ok=True)
    with open("data/errata/notes.txt", "w") as f:
        f.write("This is not a paper file.\n")

    # 答案唯一确定：有效论文ID = {"p001","p002","p003","p004","p005_alias"}
    # 有效引用边（只保留 target 存在于有效集合中）：
    # p001 -> p002, p003
    # p002 -> p004
    # p003 -> p002 (p005 不存在，忽略)
    # p004 -> (无)
    # p005_alias -> p001
    # 最终正确结果应包含5个节点和4条边。

if __name__ == "__main__":
    build_env()
