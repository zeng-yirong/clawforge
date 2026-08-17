import os
import json

def build_env():
    # 创建 data 目录
    os.makedirs("data", exist_ok=True)

    # 创建干扰附件索引
    attachments = [
        {"path": "data/attachments/roadmap_example.mmd", "title": "Roadmap Example", "kind": "mermaid", "description": "Sample roadmap"},
        {"path": "data/attachments/notes.txt", "title": "Review Notes", "kind": "text", "description": "Draft notes"}
    ]
    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

    # 创建干扰账户数据
    accounts = [
        {"account_id": "researcher_01", "display_name": "Alice", "department": "CV", "email": "alice@example.com", "permissions": ["read"]},
        {"account_id": "researcher_02", "display_name": "Bob", "department": "NLP", "email": "bob@example.com", "permissions": ["read", "write"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # 核心论文数据（包含干扰项）
    papers = [
        {"paper_id": "paper_001", "title": "Efficient Vision Transformer", "direction": "efficient_vision", "year": 2021, "keywords": ["transformer"], "abstract": "We propose a new vision transformer.", "citation_ids": ["paper_003"]},
        {"paper_id": "paper_002", "title": "Tool-Augmented Reasoning", "direction": "tool_augmented_reasoning", "year": 2022, "keywords": ["tool"], "abstract": "LLMs with tools.", "citation_ids": []},
        {"paper_id": "paper_003", "title": "Sparse Attention for Vision", "direction": "efficient_vision", "year": 2020, "keywords": ["sparse"], "abstract": "Sparse attention mechanism.", "citation_ids": ["paper_004"]},
        {"paper_id": "paper_004", "title": "MobileNet V4", "direction": "efficient_vision", "year": 2023, "keywords": ["mobile"], "abstract": "MobileNet version 4.", "citation_ids": ["paper_001"]},
        {"paper_id": "paper_005", "title": "Knowledge Distillation for Vision", "direction": "efficient_vision", "year": 2019, "keywords": ["distillation"], "abstract": "Distillation methods.", "citation_ids": ["paper_007"]},
        {"paper_id": "paper_006", "title": "Tool Use in LLMs", "direction": "tool_augmented_reasoning", "year": 2023, "keywords": ["tool"], "abstract": "Tool use.", "citation_ids": []},
        # 脏数据：缺失年份
        {"paper_id": "paper_007", "title": "Dirty Paper", "direction": "efficient_vision", "year": None, "keywords": [], "abstract": "Incomplete.", "citation_ids": []},
        # 脏数据：重复ID
        {"paper_id": "paper_001", "title": "Duplicate Entry", "direction": "efficient_vision", "year": 2020, "keywords": [], "abstract": "Duplicate.", "citation_ids": []}
    ]
    with open("data/papers/papers.json", "w") as f:
        json.dump({"papers": papers}, f, indent=2)

    # 创建 output 目录（留给 agent 使用，初始为空）
    os.makedirs("output", exist_ok=True)

if __name__ == "__main__":
    build_env()
