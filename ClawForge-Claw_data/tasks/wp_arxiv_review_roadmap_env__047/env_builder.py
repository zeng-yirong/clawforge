import os
import json

def build_env():
    # 目录结构
    os.makedirs("data/papers", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("notes", exist_ok=True)

    # 干扰目录和文件
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": []}, f)
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": []}, f)
    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": []}, f)
    with open("notes/scratch.txt", "w") as f:
        f.write("some scratch notes\n")

    # 核心论文数据
    papers = [
        {
            "paper_id": "tar_001",
            "title": "Tool Augmented Reasoning with LLMs",
            "direction": "tool_augmented_reasoning",
            "year": 2021,
            "keywords": ["reasoning", "tools"],
            "abstract": "We propose a method that dynamically integrates external tools into the reasoning loop of large language models, achieving significant improvements on complex tasks.",
            "citation_ids": ["ref1", "ref2"]
        },
        {
            "paper_id": "tar_002",
            "title": "Enhancing Reasoning via Tool Use",
            "direction": "tool_augmented_reasoning",
            "year": 2022,
            "keywords": ["enhancement", "tool"],
            "abstract": "Our approach augments chain-of-thought prompting with selective tool invocations, reducing hallucination and improving factual accuracy.",
            "citation_ids": ["ref3"]
        },
        {
            "paper_id": "tar_003",
            "title": "A Survey of Tool-Augmented Reasoning",
            "direction": "tool_augmented_reasoning",
            "year": 2023,
            "keywords": ["survey", "tool-augmented"],
            "abstract": "This comprehensive survey categorizes and compares over 50 recent works in tool-augmented reasoning, outlining future research directions.",
            "citation_ids": ["ref4", "ref5"]
        },
        # 脏数据：草稿（抽象为空）
        {
            "paper_id": "tar_004",
            "title": "Draft: Tool Reasoning Preliminary",
            "direction": "tool_augmented_reasoning",
            "year": 2020,
            "keywords": ["draft"],
            "abstract": "",
            "citation_ids": []
        },
        # 脏数据：未来年份
        {
            "paper_id": "tar_005",
            "title": "Future Tool Reasoning",
            "direction": "tool_augmented_reasoning",
            "year": 2025,
            "keywords": ["future"],
            "abstract": "Speculative ideas about tool use in reasoning.",
            "citation_ids": ["ref6"]
        },
        # 干扰方向论文
        {
            "paper_id": "ev_001",
            "title": "Efficient Vision Transformer",
            "direction": "efficient_vision",
            "year": 2022,
            "keywords": ["vision", "transformer"],
            "abstract": "An efficient vision transformer for real-time applications.",
            "citation_ids": ["ref7"]
        },
        {
            "paper_id": "ev_002",
            "title": "Vision-Language Models",
            "direction": "efficient_vision",
            "year": 2023,
            "keywords": ["vision", "language"],
            "abstract": "A study on vision-language pretraining.",
            "citation_ids": ["ref8"]
        },
        {
            "paper_id": "ev_003",
            "title": "Image Classification",
            "direction": "efficient_vision",
            "year": 2021,
            "keywords": ["image"],
            "abstract": "Classic image classification techniques.",
            "citation_ids": ["ref9"]
        }
    ]

    with open("data/papers/papers.json", "w") as f:
        json.dump({"papers": papers}, f, indent=2)

if __name__ == "__main__":
    build_env()
