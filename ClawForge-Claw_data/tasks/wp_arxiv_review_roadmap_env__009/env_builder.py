import os
import json
import shutil

def build_env():
    # 创建数据目录
    os.makedirs("data/papers", exist_ok=True)
    os.makedirs("results", exist_ok=True)  # 让 agent 有目标目录

    # --- 核心论文数据 (8篇，包含干扰) ---
    papers = [
        {
            "paper_id": "paper_001",
            "title": "Tool-Augmented Reasoning with Transformers (paper_001)",
            "direction": "tool_augmented_reasoning",
            "year": 2021,
            "abstract": "We present a transformer architecture that leverages external tools for multi-step reasoning... ABSTRACT_CONTENT_001",
            "keywords": ["tool use", "reasoning", "transformer"],
            "citation_ids": ["paper_005"]
        },
        {
            "paper_id": "paper_002",
            "title": "Augmented Language Models and Tool Use (paper_002)",
            "direction": "tool_augmented_reasoning",
            "year": 2022,
            "abstract": "",  # 空摘要 —— 脏数据
            "keywords": ["language model", "tool"],
            "citation_ids": []
        },
        {
            "paper_id": "paper_003",
            "title": "Chain-of-Thought Meets Tool Calling (paper_003)",
            "direction": "tool_augmented_reasoning",
            "year": 2023,
            "abstract": "This work integrates chain-of-thought prompting with external tool invocation... ABSTRACT_CONTENT_003",
            "keywords": ["chain-of-thought", "tool calling", "reasoning"],
            "citation_ids": ["paper_001", "paper_005"]
        },
        {
            "paper_id": "paper_004",
            "title": "Early Work on Tool-Augmented Agents (paper_004)",
            "direction": "tool_augmented_reasoning",
            "year": 1998,   # 年份太早，不在近五年
            "abstract": "Pioneering approach to tool-augmented reasoning in symbolic AI... ABSTRACT_CONTENT_004",
            "keywords": ["symbolic", "tool"],
            "citation_ids": []
        },
        {
            "paper_id": "paper_005",
            "title": "Toolformer: Teaching Language Models to Use Tools (paper_005)",
            "direction": "tool_augmented_reasoning",
            "year": 2020,
            "abstract": "Toolformer is a language model trained to decide which tool to call and how... ABSTRACT_CONTENT_005",
            "keywords": ["toolformer", "tool learning", "language model"],
            "citation_ids": []
        },
        {
            "paper_id": "paper_006",
            "title": "Efficient Vision Backbones for Mobile Devices (paper_006)",
            "direction": "efficient_vision",   # 方向不同，诱饵
            "year": 2022,
            "abstract": "This paper proposes a lightweight vision transformer for mobile deployment... ABSTRACT_CONTENT_006",
            "keywords": ["efficient vision", "mobile", "transformer"],
            "citation_ids": []
        },
        {
            "paper_id": "paper_007",
            "title": "ReAct: Synergizing Reasoning and Acting with Tool Use (paper_007)",
            "direction": "tool_augmented_reasoning",
            "year": 2024,
            "abstract": "ReAct combines reasoning traces and tool-use actions for enhanced performance... ABSTRACT_CONTENT_007",
            "keywords": ["react", "reasoning", "acting", "tool"],
            "citation_ids": ["paper_005", "paper_001"]
        }
    ]

    with open("data/papers/papers.json", "w") as f:
        json.dump({"papers": papers}, f, indent=2)

    # --- 干扰附件 ---
    attachments = [
        {"path": "figures/tool_usage_overview.png", "title": "Tool Usage Overview",
         "kind": "figure", "description": "Diagram showing how agents call tools."},
        {"path": "tables/benchmarks.csv", "title": "Benchmark Comparison",
         "kind": "table", "description": "Performance numbers across different methods."}
    ]
    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

    # --- 其他无关杂物 ---
    with open("data/notes.txt", "w") as f:
        f.write("Meeting notes from 2024-01-15:\nDiscuss direction of tool-augmented reasoning...")
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": [{"contact_id": "c001", "name": "Alice", "role": "advisor", "email": "alice@lab.org"}]}, f, indent=2)

if __name__ == "__main__":
    build_env()
