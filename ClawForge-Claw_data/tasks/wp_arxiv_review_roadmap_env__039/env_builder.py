import os
import json

def build_env():
    # 创建目录结构
    os.makedirs("data/papers", exist_ok=True)
    os.makedirs("data/backup", exist_ok=True)
    os.makedirs("research", exist_ok=True)  # 目标目录，agent 需要写入文件

    # 主论文数据
    papers = [
        {
            "paper_id": "p01",
            "title": "Tool-Augmented Language Models",
            "direction": "tool_augmented_reasoning",
            "year": 2020,
            "keywords": ["tool", "language model"],
            "abstract": "We propose a framework that augments language models with external tools for improved reasoning.",
            "citation_ids": []
        },
        {
            "paper_id": "p02",
            "title": "Reasoning with External Tools",
            "direction": "tool_augmented_reasoning",
            "year": 2021,
            "keywords": ["reasoning", "tool"],
            "abstract": "We introduce a method that enables models to call tools dynamically during reasoning steps.",
            "citation_ids": []
        },
        {
            "paper_id": "p03",
            "title": "Augmented Retrieval for QA",
            "direction": "tool_augmented_reasoning",
            "year": 2022,
            "keywords": ["retrieval", "qa"],
            "abstract": "Our method combines retrieval with tool-augmented reasoning to improve question answering.",
            "citation_ids": []
        },
        {
            "paper_id": "p04",
            "title": "Interactive Tool Use",
            "direction": "tool_augmented_reasoning",
            "year": 2023,
            "keywords": ["interactive", "tool"],
            "abstract": "We present an interactive framework where models learn to use tools through iterative feedback.",
            "citation_ids": []
        },
        {
            "paper_id": "p05",
            "title": "Efficient Vision Backbone",
            "direction": "efficient_vision",
            "year": 2020,
            "keywords": ["vision", "efficient"],
            "abstract": "A new efficient backbone for vision tasks with reduced parameters.",
            "citation_ids": []
        },
        {
            "paper_id": "p06",
            "title": "Vision Transformer Lite",
            "direction": "efficient_vision",
            "year": 2021,
            "keywords": ["vision", "transformer"],
            "abstract": "A lightweight vision transformer that maintains accuracy with fewer computations.",
            "citation_ids": []
        },
        {
            "paper_id": "p07",
            "title": "Tool Reasoning in 2019",
            "direction": "tool_augmented_reasoning",
            "year": 2019,
            "keywords": ["old"],
            "abstract": "Early work on tool reasoning before the recent surge.",
            "citation_ids": []
        },
        {
            "paper_id": "p08",
            "title": "Another Vision Model",
            "direction": "efficient_vision",
            "year": 2022,
            "keywords": ["vision"],
            "abstract": "Another vision model for efficient inference.",
            "citation_ids": []
        }
    ]
    with open("data/papers/papers.json", "w") as f:
        json.dump({"papers": papers}, f, indent=2)

    # 干扰备份文件（旧版数据，包含错误年份和方向）
    backup_papers = [
        {
            "paper_id": "p01",
            "title": "Tool-Augmented Language Models",
            "direction": "tool_augmented_reasoning",
            "year": 2025,  # 错误年份
            "keywords": ["tool", "language model"],
            "abstract": "Old version with wrong year.",
            "citation_ids": []
        },
        {
            "paper_id": "p02",
            "title": "Reasoning with External Tools",
            "direction": "efficient_vision",  # 错误方向
            "year": 2021,
            "keywords": ["reasoning", "tool"],
            "abstract": "Old version with wrong direction.",
            "citation_ids": []
        }
    ]
    with open("data/backup/papers_backup.json", "w") as f:
        json.dump({"papers": backup_papers}, f, indent=2)

    # 空 attachments 文件（用于丰富环境，但不是必需的）
    os.makedirs("data/attachments", exist_ok=True)
    attachments = []
    with open("data/attachments/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

if __name__ == "__main__":
    build_env()
