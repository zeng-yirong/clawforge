import os
import json
import random

def build_env():
    # 创建数据目录
    os.makedirs("data/papers", exist_ok=True)
    os.makedirs("docs", exist_ok=True)  # 用于agent输出

    # 主论文库 (papers.json)
    papers = [
        {
            "paper_id": "paper-001",
            "title": "Vision Transformer: An Image is Worth 16x16 Words",
            "direction": "efficient_vision",
            "year": 2021,
            "keywords": ["transformer", "attention"],
            "abstract": "We present the Vision Transformer...",
            "citation_ids": ["ref01", "ref02"]
        },
        {
            "paper_id": "paper-002",
            "title": "Tool-Augmented Language Models",
            "direction": "tool_augmented_reasoning",
            "year": 2022,
            "keywords": ["tool use", "LLM"],
            "abstract": "We augment language models with external tools...",
            "citation_ids": []
        },
        {
            "paper_id": "paper-003",
            "title": "EfficientNet: Rethinking Model Scaling",
            "direction": "efficient_vision",
            "year": 2019,
            "keywords": ["scaling", "efficiency"],
            "abstract": "We systematically study model scaling...",
            "citation_ids": ["ref03"]
        },
        {
            "paper_id": "paper-004",
            "title": "ReAct: Synergizing Reasoning and Acting",
            "direction": "tool_augmented_reasoning",
            "year": 2023,
            "keywords": ["reasoning", "action"],
            "abstract": "We propose ReAct...",
            "citation_ids": []
        },
        {
            "paper_id": "paper-005",
            "title": "MobileNet: Efficient Convolutional Neural Networks",
            "direction": "efficient_vision",
            "year": 2017,
            "keywords": ["mobile", "depthwise"],
            "abstract": "We present a class of efficient models...",
            "citation_ids": ["ref04"]
        },
        {
            "paper_id": "paper-006",
            "title": "Chain-of-Thought Prompting",
            "direction": "tool_augmented_reasoning",
            "year": 2022,
            "keywords": ["reasoning", "prompt"],
            "abstract": "Chain-of-thought enables complex reasoning...",
            "citation_ids": []
        },
        {
            "paper_id": "paper-007",
            "title": "ConvNeXt: A ConvNet for the 2020s",
            "direction": "efficient_vision",
            "year": 2022,
            "keywords": ["convnet", "modern"],
            "abstract": "We redesign ConvNet architectures...",
            "citation_ids": ["ref05"]
        },
        {
            "paper_id": "paper-008",
            "title": "Gorilla: Large Language Model Connected with Massive APIs",
            "direction": "tool_augmented_reasoning",
            "year": 2023,
            "keywords": ["api", "LLM"],
            "abstract": "Gorilla enables LLMs to use APIs...",
            "citation_ids": []
        },
        {
            "paper_id": "paper-009",
            "title": "EfficientViT: Efficient Vision Transformer",
            "direction": "efficient_vision",
            "year": 2023,
            "keywords": ["transformer", "efficiency"],
            "abstract": "We propose EfficientViT...",
            "citation_ids": ["ref06"]
        },
        {
            "paper_id": "paper-010",
            "title": "BERT: Pre-training of Deep Bidirectional Transformers",
            "direction": "nlp",
            "year": 2019,
            "keywords": ["nlp", "pretraining"],
            "abstract": "BERT achieves state-of-the-art...",
            "citation_ids": []
        },
        {
            "paper_id": "paper-011",
            "title": "A Fast Vision Model",
            "direction": "EFFICIENT_VISION",  # 大小写干扰
            "year": 2020,
            "keywords": ["fast"],
            "abstract": "Some abstract...",
            "citation_ids": []
        },
        {
            "paper_id": "paper-012",
            "title": "Lightweight Vision Backbone",
            "direction": "efficient_vision",
            "year": 2024,
            "keywords": ["lightweight"],
            "abstract": "",  # 空abstract
            "citation_ids": []
        }
    ]
    # 注意：paper-011 方向是 "EFFICIENT_VISION" 全大写，不匹配目标 "efficient_vision"
    # paper-012 是正常efficient_vision，但年份2024，所以总共正确的论文是：paper-005(2017), paper-003(2019), paper-001(2021), paper-007(2022), paper-009(2023), paper-012(2024) 共6篇
    # 这样排序后ID列表为：['paper-005','paper-003','paper-001','paper-007','paper-009','paper-012']

    with open("data/papers/papers.json", "w") as f:
        json.dump({"papers": papers}, f, indent=2)

    # 干扰文件：旧的备份
    os.makedirs("data/backup", exist_ok=True)
    backup_papers = [
        {
            "paper_id": "paper-005",
            "title": "MobileNet (old version)",
            "direction": "efficient_vision",
            "year": 2016,
            "keywords": [],
            "abstract": "old abstract",
            "citation_ids": []
        }
    ]
    with open("data/backup/papers_2019.json", "w") as f:
        json.dump({"papers": backup_papers}, f, indent=2)

    # 干扰文件：其他格式的附件
    attachments = [
        {"path": "data/attachments/fig1.png", "title": "Figure 1", "kind": "image", "description": "Performance curves"},
        {"path": "data/attachments/table1.csv", "title": "Table 1", "kind": "csv", "description": "Comparison results"}
    ]
    os.makedirs("data/attachments", exist_ok=True)
    with open("data/attachments/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

    # 干扰文件：账户数据（完全不相关）
    accounts = [
        {"account_id": "a001", "display_name": "Alice", "department": "CS", "email": "alice@univ.edu", "permissions": ["read"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # 返回成功
    return True

if __name__ == "__main__":
    build_env()
