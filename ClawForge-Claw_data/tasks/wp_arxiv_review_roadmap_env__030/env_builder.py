import os
import json
import random
from datetime import datetime

def build_env():
    # 确保种子固定，让答案唯一
    random.seed(42)

    # 1. 创建 papers 目录，写入主数据
    os.makedirs("papers", exist_ok=True)
    papers = [
        # 有效论文 (efficient_vision)
        {"paper_id": "v1", "title": "EfficientNet: Rethinking Model Scaling", "direction": "efficient_vision", "year": 2019,
         "keywords": ["scaling", "efficiency"], "abstract": "A new scaling method for CNNs.",
         "citation_ids": []},
        {"paper_id": "v2", "title": "MobileNetV3: Searching for Lightweight Networks", "direction": "efficient_vision", "year": 2020,
         "keywords": ["mobile", "NAS"], "abstract": "Automated search for efficient architectures.",
         "citation_ids": ["v1"]},
        {"paper_id": "v3", "title": "Swin Transformer: Hierarchical Vision Transformer", "direction": "efficient_vision", "year": 2021,
         "keywords": ["transformer", "hierarchical"], "abstract": "A transformer backbone for vision.",
         "citation_ids": ["v2"]},
        {"paper_id": "v4", "title": "ConvNeXt: A ConvNet for the 2020s", "direction": "efficient_vision", "year": 2022,
         "keywords": ["convolution", "modern"], "abstract": "Reviving convolutions with modern designs.",
         "citation_ids": ["v3"]},
        {"paper_id": "v5", "title": "FastViT: A Hybrid Vision Transformer", "direction": "efficient_vision", "year": 2023,
         "keywords": ["hybrid", "speed"], "abstract": "Combining convolution and attention for speed.",
         "citation_ids": ["v4", "v1"]},
        # 干扰项 - 不同方向
        {"paper_id": "w1", "title": "ToolFormer: Learning to Use Tools", "direction": "tool_augmented_reasoning", "year": 2022,
         "keywords": ["tool", "language"], "abstract": "Training LLMs to call APIs.",
         "citation_ids": []},
        {"paper_id": "w2", "title": "ReAct: Synergizing Reasoning and Acting", "direction": "tool_augmented_reasoning", "year": 2023,
         "keywords": ["reasoning", "acting"], "abstract": "Interleaving reasoning traces.",
         "citation_ids": ["w1"]},
        # 干扰项 - 年份不合规（2018）
        {"paper_id": "v0", "title": "SqueezeNet: AlexNet-level accuracy with 50x fewer parameters", "direction": "efficient_vision", "year": 2018,
         "keywords": ["compression"], "abstract": "Early efficient network.",
         "citation_ids": []},
        # 脏数据 - 缺 direction 字段
        {"paper_id": "x1", "title": "No direction paper", "year": 2021, "abstract": "Missing direction.",
         "keywords": [], "citation_ids": []},
        # 脏数据 - direction 拼写错误
        {"paper_id": "x2", "title": "Efficient Vision Paper Typo", "direction": "efficient_visio", "year": 2022,
         "abstract": "Typo in direction.",
         "keywords": [], "citation_ids": []},
        # 重复项（完全相同的 paper_id 和内容，模拟冗余记录）
        {"paper_id": "v3", "title": "Swin Transformer: Hierarchical Vision Transformer", "direction": "efficient_vision", "year": 2021,
         "keywords": ["transformer", "hierarchical"], "abstract": "A transformer backbone for vision.",
         "citation_ids": ["v2"]},
    ]
    random.shuffle(papers)
    with open("papers/papers.json", "w") as f:
        json.dump({"papers": papers}, f, indent=2)

    # 2. 创建附件目录，放一些无关的 PDF 摘要（不影响核心逻辑，但增加迷惑）
    os.makedirs("attachments", exist_ok=True)
    attachments = [
        {"path": "attachments/v1_abstract.txt", "content": "Abstract of EfficientNet: rethinking scaling."},
        {"path": "attachments/w1_abstract.txt", "content": "Abstract of ToolFormer."},
        {"path": "attachments/old_note.txt", "content": "Random note for confusion."},
    ]
    for att in attachments:
        with open(att["path"], "w") as f:
            f.write(att["content"])

    # 3. 创建 cache 目录，放一份旧快照（其中可能包含有效论文的额外信息，但不需要使用）
    os.makedirs("cache", exist_ok=True)
    cache_entry = {
        "entry_id": "cache_001",
        "timestamp": "2024-01-01",
        "papers": [
            {"paper_id": "v1", "cached_title": "EfficientNet Rethinking"},
            {"paper_id": "v5", "cached_title": "FastViT"},
            {"paper_id": "old", "cached_title": "Old paper"},
        ]
    }
    with open("cache/old_snapshot.json", "w") as f:
        json.dump({"cache": cache_entry}, f, indent=2)

    # 4. 创建 reviews 和 roadmaps 目录（空目录，等待 agent 填充）
    os.makedirs("reviews", exist_ok=True)
    os.makedirs("roadmaps", exist_ok=True)

    # 5. 额外干扰：一个无关的 log 文件
    with open("system.log", "w") as f:
        f.write("INFO: system started\nWARNING: none\n")

if __name__ == "__main__":
    build_env()
