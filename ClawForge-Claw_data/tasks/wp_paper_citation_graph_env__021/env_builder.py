import json
import os

def build_env():
    # papers directory
    os.makedirs("papers", exist_ok=True)

    papers = [
        {
            "paper_id": "p001",
            "title": "Deep Learning for NLP",
            "direction": "NLP",
            "year": 2022,
            "keywords": ["deep learning", "NLP", "transformer"],
            "abstract": "This paper explores deep learning techniques for natural language processing.",
            "citation_ids": ["p002", "p003"]
        },
        {
            "paper_id": "p002",
            "title": "Graph Neural Networks",
            "direction": "Graph ML",
            "year": 2021,
            "keywords": ["graph", "neural network", "embedding"],
            "abstract": "A comprehensive survey of graph neural networks.",
            "citation_ids": ["p003"]
        },
        {
            "paper_id": "p003",
            "title": "Attention Is All You Need",
            "direction": "Architecture",
            "year": 2023,
            "keywords": ["attention", "transformer", "sequence"],
            "abstract": "Introduces the transformer architecture based solely on attention mechanisms.",
            "citation_ids": ["p001"]
        },
        # 干扰项1：缺少 citation_ids 字段
        {
            "paper_id": "p004",
            "title": "Obsolete Methods in AI",
            "direction": "History",
            "year": 2005,
            "keywords": ["obsolete"],
            "abstract": "Older methods that are no longer used."
            # 故意不写 citation_ids
        },
        # 干扰项2：引用不存在的论文
        {
            "paper_id": "p005",
            "title": "Fake References Paper",
            "direction": "Misc",
            "year": 2020,
            "keywords": ["fake"],
            "abstract": "This paper contains non-existent references.",
            "citation_ids": ["p999", "p000"]
        },
        # 干扰项3：老论文，引用自身（无效边，因为 p006 本身干净但年代老且引用不存在的论文？改为引用 p001 但自身老，但为了保持唯一答案，我们让它也引用不存在，这样所有干扰都不会产生有效边）
        {
            "paper_id": "p006",
            "title": "Early Work on Attention",
            "direction": "History",
            "year": 1999,
            "keywords": ["attention", "early"],
            "abstract": "An early attempt to use attention.",
            "citation_ids": ["p100"]  # 不存在的论文
        }
    ]

    with open("papers/papers.json", "w") as f:
        json.dump({"papers": papers}, f, indent=2)

if __name__ == "__main__":
    build_env()
