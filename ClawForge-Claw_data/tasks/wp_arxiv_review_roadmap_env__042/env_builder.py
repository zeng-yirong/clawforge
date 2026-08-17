import os
import json

def build_env():
    # 确保 data/papers 目录存在
    os.makedirs("data/papers", exist_ok=True)

    # 定义论文列表（包含干扰项）
    papers = [
        {
            "paper_id": "p1",
            "title": "Tool Learning with Large Language Models",
            "direction": "tool_augmented_reasoning",
            "year": 2022,
            "keywords": ["tool", "LLM"],
            "abstract": "This paper investigates how large language models can learn to use external tools to augment their reasoning capabilities. We propose a framework that combines tool retrieval with in-context learning.",
            "citation_ids": []
        },
        {
            "paper_id": "p2",
            "title": "Augmented Reasoning via Tool-Use",
            "direction": "tool_augmented_reasoning",
            "year": 2023,
            "keywords": ["reasoning", "tools"],
            "abstract": "We present a method for augmenting chain-of-thought reasoning with tool invocations. Experiments show significant improvements on math and coding benchmarks.",
            "citation_ids": ["p1"]
        },
        {
            "paper_id": "p3",
            "title": "Reasoning with Tools: A Survey",
            "direction": "tool_augmented_reasoning",
            "year": 2024,
            "keywords": ["survey", "tools", "reasoning"],
            "abstract": "This survey categorizes and compares various approaches that integrate tool use into reasoning processes. It covers tool retrieval, tool-augmented LLMs, and hybrid systems.",
            "citation_ids": ["p1", "p2"]
        },
        {
            "paper_id": "p4",
            "title": "Tool-Augmented Agent Architectures",
            "direction": "tool_augmented_reasoning",
            "year": 2023,
            "keywords": ["agents", "tools"],
            "abstract": "We design a modular architecture for building agents that can autonomously discover and invoke tools to complete complex tasks. The system is evaluated on web navigation.",
            "citation_ids": ["p2"]
        },
        # 干扰项：方向不同
        {
            "paper_id": "p5",
            "title": "Efficient Vision Transformers",
            "direction": "efficient_vision",
            "year": 2021,
            "keywords": ["vision", "transformer"],
            "abstract": "This work proposes a lightweight vision transformer for image classification.",
            "citation_ids": []
        },
        # 干扰项：年份过早
        {
            "paper_id": "p6",
            "title": "Early Tool Use in AI",
            "direction": "tool_augmented_reasoning",
            "year": 2019,
            "keywords": ["tool", "early"],
            "abstract": "An early exploration of tool use in AI systems.",
            "citation_ids": []
        },
        # 干扰项：年份过晚
        {
            "paper_id": "p7",
            "title": "Future Tools",
            "direction": "tool_augmented_reasoning",
            "year": 2025,
            "keywords": ["future"],
            "abstract": "Speculative paper about future tool use.",
            "citation_ids": ["p1"]
        },
        # 干扰项：缺少 abstract 字段
        {
            "paper_id": "p8",
            "title": "Incomplete Paper",
            "direction": "tool_augmented_reasoning",
            "year": 2023,
            "keywords": [],
            "citation_ids": []
        },
        # 干扰项：方向拼写错误
        {
            "paper_id": "p9",
            "title": "Wrong Direction",
            "direction": "tool_argumented_reasoning",
            "year": 2022,
            "keywords": ["tool"],
            "abstract": "Slightly misspelled direction.",
            "citation_ids": []
        }
    ]

    with open("data/papers/papers.json", "w", encoding="utf-8") as f:
        json.dump({"papers": papers}, f, indent=2)

    # 生成另一个干扰文件（无用附件）
    os.makedirs("data", exist_ok=True)
    attachments = [
        {"path": "data/papers/papers.json", "title": "Paper Dump", "kind": "json", "description": "Contains all paper records."},
        {"path": "data/attachments.json", "title": "Attachment Index", "kind": "json", "description": "Index of all attachments."}
    ]
    with open("data/attachments.json", "w", encoding="utf-8") as f:
        json.dump({"attachments": attachments}, f, indent=2)

if __name__ == "__main__":
    build_env()
