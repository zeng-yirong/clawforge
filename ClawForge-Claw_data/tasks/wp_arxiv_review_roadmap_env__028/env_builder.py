import os
import json

def build_env():
    # 目录结构
    os.makedirs("data/papers", exist_ok=True)
    os.makedirs("data/attachments", exist_ok=True)
    os.makedirs("data", exist_ok=True)  # 用于干扰文件

    # 1. 论文数据（含干扰论文）
    papers = {
        "papers": [
            {
                "paper_id": "EV-001",
                "title": "Efficient Vision Transformer",
                "direction": "efficient_vision",
                "year": 2022,
                "keywords": ["vision", "transformer", "efficient"],
                "abstract": "We propose an efficient vision transformer that reduces computation by 40%.",
                "citation_ids": ["EV-002"]
            },
            {
                "paper_id": "EV-002",
                "title": "MobileViT: Lightweight Vision Transformer",
                "direction": "efficient_vision",
                "year": 2023,
                "keywords": ["mobile", "vision", "transformer"],
                "abstract": "MobileViT combines CNNs and transformers for mobile-friendly vision.",
                "citation_ids": ["EV-001"]
            },
            {
                "paper_id": "EV-003",
                "title": "FastViT: Speed-Optimized Vision Transformer",
                "direction": "efficient_vision",
                "year": 2024,
                "keywords": ["speed", "vision", "transformer"],
                "abstract": "FastViT achieves real-time inference on edge devices.",
                "citation_ids": []
            },
            # 干扰论文
            {
                "paper_id": "TA-001",
                "title": "Tool-Augmented Reasoning with LLMs",
                "direction": "tool_augmented_reasoning",
                "year": 2023,
                "keywords": ["tool", "LLM", "reasoning"],
                "abstract": "Using tools to enhance LLM reasoning capabilities.",
                "citation_ids": []
            },
            {
                "paper_id": "TA-002",
                "title": "ReAct: Synergizing Reasoning and Acting",
                "direction": "tool_augmented_reasoning",
                "year": 2022,
                "keywords": ["reasoning", "acting"],
                "abstract": "ReAct combines reasoning traces and task-specific actions.",
                "citation_ids": []
            }
        ]
    }
    with open("data/papers/papers.json", "w", encoding="utf-8") as f:
        json.dump(papers, f, indent=2)

    # 2. 附件元数据
    attachments = {
        "attachments": [
            {
                "path": "attachments/vision_notes.txt",
                "title": "Vision Research Notes",
                "kind": "text",
                "description": "Notes on efficient vision including key insights from recent papers."
            },
            {
                "path": "attachments/tool_notes.txt",
                "title": "Tool Usage Notes",
                "kind": "text",
                "description": "Notes on tool-augmented reasoning, irrelevant to vision."
            }
        ]
    }
    with open("data/attachments.json", "w", encoding="utf-8") as f:
        json.dump(attachments, f, indent=2)

    # 3. 实际附件内容（只有 vision_notes.txt 有营养）
    os.makedirs("attachments", exist_ok=True)
    with open("attachments/vision_notes.txt", "w", encoding="utf-8") as f:
        f.write("Key insight: Vision Transformers achieve state-of-the-art on ImageNet. "
                "Also, combination with CNNs can reduce parameters.\n")
    with open("attachments/tool_notes.txt", "w", encoding="utf-8") as f:
        f.write("Tools like calculators and search engines help LLMs.\n")

    # 4. 干扰文件（账户、联系人等，模拟完整环境）
    accounts = {"accounts": [
        {"account_id": "acc01", "display_name": "Chen", "department": "Vision", "email": "chen@lab.example.com", "permissions": ["admin"]}
    ]}
    with open("data/accounts.json", "w", encoding="utf-8") as f:
        json.dump(accounts, f, indent=2)

    contacts = {"contacts": [
        {"contact_id": "c01", "name": "Liu", "role": "assistant", "email": "liu@lab.example.com"}
    ]}
    with open("data/contacts.json", "w", encoding="utf-8") as f:
        json.dump(contacts, f, indent=2)

if __name__ == "__main__":
    build_env()
