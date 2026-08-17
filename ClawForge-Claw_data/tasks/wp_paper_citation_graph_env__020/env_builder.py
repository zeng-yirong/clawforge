import os
import json
import re

def build_env():
    # 创建目录
    os.makedirs("papers", exist_ok=True)
    os.makedirs("cache", exist_ok=True)

    # 有效论文
    valid_papers = {
        "P-001": {
            "title": "Deep Learning for NLP",
            "direction": "NLP",
            "year": 2018,
            "keywords": ["deep learning", "NLP"],
            "abstract": "A survey of deep learning methods for natural language processing.",
            "citation_ids": ["P-002", "P-003"]
        },
        "P-002": {
            "title": "Attention Is All You Need",
            "direction": "Seq2Seq",
            "year": 2017,
            "keywords": ["attention", "transformer"],
            "abstract": "Proposes the Transformer architecture.",
            "citation_ids": ["P-004"]
        },
        "P-003": {
            "title": "BERT: Pre-training of Deep Bidirectional Transformers",
            "direction": "NLP",
            "year": 2019,
            "keywords": ["BERT", "pre-training"],
            "abstract": "Introduces BERT model.",
            "citation_ids": ["P-002"]
        },
        "P-004": {
            "title": "Transformer: A Novel Neural Network Architecture",
            "direction": "Architecture",
            "year": 2017,
            "keywords": ["transformer"],
            "abstract": "Detailed description of Transformer.",
            "citation_ids": ["P-005"]
        },
        "P-005": {
            "title": "Generative Pre-trained Transformer (GPT)",
            "direction": "Language Model",
            "year": 2020,
            "keywords": ["GPT", "language model"],
            "abstract": "Introduces GPT architecture.",
            "citation_ids": ["P-002", "P-003"]
        }
    }

    # 干扰项
    distractor_papers = {
        "X-999": {
            "title": "Fake Paper",
            "direction": "Fake",
            "year": 2025,
            "keywords": [],
            "abstract": "This paper has invalid ID format.",
            "citation_ids": []
        },
        "P-006": {
            "title": "Future Tech",
            "direction": "AI",
            "year": 2025,
            "keywords": ["future"],
            "abstract": "Paper from the future.",
            "citation_ids": ["P-001"]
        },
        "P-007": {
            "title": "Missing Year",
            "direction": "AI",
            # year missing
            "keywords": [],
            "abstract": "No year field.",
            "citation_ids": []
        },
        "P-008": {
            "title": "Bad Citation",
            "direction": "AI",
            "year": 2021,
            "keywords": [],
            "abstract": "Points to non-existent paper.",
            "citation_ids": ["P-NONEXIST", "P-001"]
        },
        "P-009": {
            "title": "Duplicate ID",
            "direction": "AI",
            "year": 2021,
            "keywords": [],
            "abstract": "This paper has same ID as another? Actually not duplicate, just extra.",
            "citation_ids": ["P-001"]
        }
    }

    # 去除干扰项中缺失 year 的（P-007 故意没有 year 字段）
    distractor_papers["P-007"].pop("year", None)

    # 合并成整体 papers 字典
    all_papers = {}
    all_papers.update(valid_papers)
    all_papers.update(distractor_papers)

    # 写入 papers.json
    papers_data = {"papers": all_papers}
    with open("papers/papers.json", "w") as f:
        json.dump(papers_data, f, indent=2)

if __name__ == "__main__":
    build_env()
