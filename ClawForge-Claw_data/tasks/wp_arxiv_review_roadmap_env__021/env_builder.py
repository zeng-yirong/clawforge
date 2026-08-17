import os
import json
import random

def build_env():
    # 确保 output 目录存在
    os.makedirs("output", exist_ok=True)

    # 构建论文数据（含干扰项）
    papers = [
        # 工具增强推理方向（5篇）
        {"paper_id": "123", "title": "Tool-Augmented Reasoning", "direction": "tool_augmented_reasoning", "year": 2022, "citations": 50, "keywords": ["reasoning", "tools"], "abstract": "..."},
        {"paper_id": "456", "title": "Reasoning with External Tools", "direction": "tool_augmented_reasoning", "year": 2021, "citations": 30, "keywords": ["tools", "external"], "abstract": "..."},
        {"paper_id": "789", "title": "Augmented Reasoning in NLP", "direction": "tool_augmented_reasoning", "year": 2023, "citations": 20, "keywords": ["nlp", "augmented"], "abstract": "..."},
        {"paper_id": "101", "title": "Tool Use for Reasoning", "direction": "tool_augmented_reasoning", "year": 2020, "citations": 40, "keywords": ["tool use"], "abstract": "..."},  # 年份不符
        {"paper_id": "112", "title": "Reasoning via Tool Integration", "direction": "tool_augmented_reasoning", "year": 2023, "citations": 10, "keywords": ["integration"], "abstract": "..."},
        # 高效视觉方向（干扰）
        {"paper_id": "201", "title": "Efficient Vision Transformers", "direction": "efficient_vision", "year": 2022, "citations": 100, "keywords": ["vision", "efficient"], "abstract": "..."},
        {"paper_id": "202", "title": "Vision Efficiency", "direction": "efficient_vision", "year": 2021, "citations": 80, "keywords": ["efficiency"], "abstract": "..."},
        {"paper_id": "203", "title": "Sparse Attention for Vision", "direction": "efficient_vision", "year": 2023, "citations": 60, "keywords": ["sparse", "attention"], "abstract": "..."},
        {"paper_id": "204", "title": "CNN Acceleration", "direction": "efficient_vision", "year": 2020, "citations": 90, "keywords": ["cnn"], "abstract": "..."},
        {"paper_id": "205", "title": "Vision Mamba", "direction": "efficient_vision", "year": 2022, "citations": 70, "keywords": ["mamba"], "abstract": "..."},
    ]

    # 写入 papers.json
    os.makedirs("data/papers", exist_ok=True)
    with open("data/papers/papers.json", "w") as f:
        json.dump({"papers": papers}, f, indent=2)

    # 创建一些干扰文件（可选，增加真实感）
    os.makedirs("data", exist_ok=True)
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": [{"account_id": "a1", "display_name": "Jack", "department": "CS", "email": "jack@lab.org", "permissions": ["read"]}]}, f, indent=2)
    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": [{"path": "logs/run1.log", "title": "run1", "kind": "log", "description": "first run"}]}, f, indent=2)

if __name__ == "__main__":
    build_env()
