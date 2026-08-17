import os
import json
import random

def build_env():
    # 创建论文数据目录
    os.makedirs("papers", exist_ok=True)
    # 创建缓存目录（干扰项）
    os.makedirs("cache", exist_ok=True)
    # 创建输出目标目录（初始为空，agent需要写入）
    os.makedirs("ops", exist_ok=True)

    # 定义三篇实际存在的论文
    papers = [
        {
            "paper_id": "paper_001",
            "title": "Deep Learning for NLP",
            "direction": "AI",
            "year": 2020,
            "keywords": ["deep learning", "NLP"],
            "abstract": "A paper about deep learning in NLP.",
            "citation_ids": ["paper_002", "paper_003", "paper_002"]  # 重复引用
        },
        {
            "paper_id": "paper_002",
            "title": "Attention Mechanisms",
            "direction": "AI",
            "year": 2019,
            "keywords": ["attention"],
            "abstract": "A paper about attention.",
            "citation_ids": ["paper_001"]
        },
        {
            "paper_id": "paper_003",
            "title": "Transformers",
            "direction": "AI",
            "year": 2021,
            "keywords": ["transformers"],
            "abstract": "A paper about transformers.",
            "citation_ids": ["paper_004"]  # 引用不存在的论文ID
        }
    ]
    # 额外干扰项：一篇论文但citation_ids字段缺失（格式错误）
    bad_paper = {
        "paper_id": "paper_005",
        "title": "Fake Paper",
        "direction": "CS",
        "year": 2022,
        "keywords": ["fake"],
        "abstract": "This should be ignored."
        # 没有citation_ids字段
    }
    # 额外干扰项：一篇论文的citation_ids是字符串而非列表
    weird_paper = {
        "paper_id": "paper_006",
        "title": "Weird Paper",
        "direction": "CS",
        "year": 2023,
        "keywords": ["weird"],
        "abstract": "Has a string citation.",
        "citation_ids": "paper_001"  # 不是列表，应视为无效
    }
    # 干扰文件：旧缓存图
    old_graph = {"edges": [{"source": "paper_001", "target": "paper_002"}, {"source": "paper_002", "target": "paper_003"}]}
    with open("cache/old_citation_graph.json", "w") as f:
        json.dump(old_graph, f)

    # 写papers.json (包含合法论文、干扰论文)
    all_papers = papers + [bad_paper, weird_paper]
    # 为了增加难度，随机打乱顺序
    random.shuffle(all_papers)
    paper_data = {"papers": all_papers}
    with open("papers/papers.json", "w") as f:
        json.dump(paper_data, f, indent=2)

    # 其他干扰文件
    with open("papers/note.txt", "w") as f:
        f.write("This is a note, not a data file.\n")

if __name__ == "__main__":
    build_env()
