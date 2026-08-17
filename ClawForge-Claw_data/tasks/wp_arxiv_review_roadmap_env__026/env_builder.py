import os
import json

def build_env():
    # papers/papers.json
    papers = [
        {
            "paper_id": "tool_001",
            "title": "Tool-Augmented Reasoning in Language Models",
            "direction": "tool_augmented_reasoning",
            "year": 2023,
            "keywords": ["tool", "reasoning", "LM"],
            "abstract": "We propose a framework that augments LLMs with external tool calls to improve logical deduction.",
            "citation_ids": ["tool_002", "tool_004"]
        },
        {
            "paper_id": "tool_002",
            "title": "Learning to Use Tools: A Survey",
            "direction": "tool_augmented_reasoning",
            "year": 2024,
            "keywords": ["survey", "tool learning"],
            "abstract": "This survey comprehensively reviews methods for training models to invoke external tools.",
            "citation_ids": []
        },
        {
            "paper_id": "tool_003",
            "title": "Chain-of-Thought with Tool Grounding",
            "direction": "tool_augmented_reasoning",
            "year": 2025,
            "keywords": ["CoT", "grounding"],
            "abstract": "We integrate tool grounding into chain-of-thought prompting for multi-step reasoning.",
            "citation_ids": ["tool_001"]
        },
        {
            "paper_id": "tool_004",
            "title": "Tool-Assisted Fact Verification",
            "direction": "tool_augmented_reasoning",
            "year": 2023,
            "keywords": ["fact verification", "tool"],
            "abstract": "Using search and calculator tools to verify factual claims in generated text.",
            "citation_ids": ["tool_001"]
        },
        {
            "paper_id": "vis_001",
            "title": "Efficient Vision Transformers for Mobile",
            "direction": "efficient_vision",
            "year": 2022,
            "keywords": ["vision", "efficient"],
            "abstract": "A lightweight ViT variant optimized for mobile devices.",
            "citation_ids": ["vis_002"]
        },
        {
            "paper_id": "vis_002",
            "title": "Knowledge Distillation for Vision Models",
            "direction": "efficient_vision",
            "year": 2023,
            "keywords": ["distillation", "vision"],
            "abstract": "Distilling large vision models into compact student networks.",
            "citation_ids": []
        }
    ]
    os.makedirs("papers", exist_ok=True)
    with open("papers/papers.json", "w") as f:
        json.dump({"papers": papers}, f, indent=2)

    # attachments/ – 干扰笔记（包含错误引导）
    os.makedirs("attachments", exist_ok=True)
    with open("attachments/note_tool_001.txt", "w") as f:
        f.write("tool_001 is the foundational work, but it actually belongs to efficient_vision (typo in data).")
    with open("attachments/note_vis.txt", "w") as f:
        f.write("vis_001 and vis_002 are great for vision tasks, ignore them for tool reasoning.")
    with open("attachments/random.log", "w") as f:
        f.write("2025-03-01 processing complete. No errors.")

    # data/ – 无关文件增加复杂度
    os.makedirs("data", exist_ok=True)
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": [{"account_id": "u1", "display_name": "Alice", "department": "CS", "email": "a@cs.edu", "permissions": ["read"]}]}, f)

def main():
    build_env()

if __name__ == "__main__":
    main()
