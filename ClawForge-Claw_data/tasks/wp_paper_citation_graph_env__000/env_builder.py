import os
import json

def build_env():
    # 创建目录结构
    os.makedirs("papers", exist_ok=True)
    os.makedirs("cache", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    # 构建一组论文（包含干扰项）
    papers = [
        # 有效论文
        {
            "paper_id": "P001",
            "title": "Attention Is All You Need",
            "direction": "NLP",
            "year": 2017,
            "keywords": ["transformer"],
            "abstract": "abstract1",
            "citation_ids": ["P002", "P003"]
        },
        {
            "paper_id": "P002",
            "title": "BERT",
            "direction": "NLP",
            "year": 2018,
            "keywords": ["pretraining"],
            "abstract": "abstract2",
            "citation_ids": ["P004", "P005"]
        },
        {
            "paper_id": "P003",
            "title": "GPT",
            "direction": "NLP",
            "year": 2018,
            "keywords": ["generative"],
            "abstract": "abstract3",
            "citation_ids": ["P006"]
        },
        {
            "paper_id": "P004",
            "title": "ResNet",
            "direction": "CV",
            "year": 2015,
            "keywords": ["deep learning"],
            "abstract": "abstract4",
            "citation_ids": ["P001"]
        },
        {
            "paper_id": "P005",
            "title": "CNN",
            "direction": "CV",
            "year": 2012,
            "keywords": ["convolution"],
            "abstract": "abstract5",
            "citation_ids": []
        },
        {
            "paper_id": "P006",
            "title": "LSTM",
            "direction": "NLP",
            "year": 1997,
            "keywords": ["RNN"],
            "abstract": "abstract6",
            "citation_ids": ["P007"]   # 引用不存在的论文
        },
        # 干扰：重复P001（缺少abstract和citation_ids）
        {
            "paper_id": "P001",
            "title": "Duplicate P001",
            "direction": "NLP",
            "year": 2017,
            "keywords": ["dup"]
            # 故意没有 abstract 和 citation_ids
        },
        # 干扰：自引用论文P008（缺少abstract）
        {
            "paper_id": "P008",
            "title": "Self citation",
            "direction": "ML",
            "year": 2020,
            "keywords": ["self"],
            "citation_ids": ["P008"]
            # 缺少 abstract
        },
        # 干扰：缺少citation_ids的论文P009
        {
            "paper_id": "P009",
            "title": "No citations",
            "direction": "ML",
            "year": 2021,
            "keywords": ["none"],
            "abstract": "abstract9"
            # 缺少 citation_ids
        }
    ]

    # 写入主要的papers.json
    with open("papers/papers.json", "w") as f:
        json.dump({"papers": papers}, f, indent=2)

    # 额外干扰文件：旧版论文数据
    old_papers = [
        {"paper_id": "P999", "title": "Old paper", "direction": "OLD", "year": 2000, "keywords": [], "abstract": "old", "citation_ids": []}
    ]
    with open("papers/old_papers.json", "w") as f:
        json.dump({"papers": old_papers}, f, indent=2)

    # 无关的data文件
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": []}, f)
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": []}, f)

if __name__ == "__main__":
    build_env()
