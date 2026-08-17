import os
import json
import random

def build_env():
    # 创建数据目录
    os.makedirs("data/papers", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    # 干扰文件：附件和联系人（内容无关）
    attachments = {
        "attachments": [
            {"path": "notes/old_draft.md", "title": "Old draft", "kind": "note", "description": "Obsolete notes"},
            {"path": "figures/overview.png", "title": "Overview image", "kind": "image", "description": "placeholder"},
        ]
    }
    with open("data/attachments.json", "w") as f:
        json.dump(attachments, f, indent=2)

    contacts = {
        "contacts": [
            {"contact_id": "c001", "name": "Alice", "role": "author", "email": "alice@lab.org"},
            {"contact_id": "c002", "name": "Bob", "role": "reviewer", "email": "bob@lab.org"},
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    accounts = {
        "accounts": [
            {"account_id": "a01", "display_name": "Admin", "department": "IT", "email": "admin@lab.org", "permissions": ["read", "write"]},
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # 核心论文数据
    papers = []
    tar_papers = [
        {
            "paper_id": "paper_001",
            "title": "Tool-Augmented Reasoning via Symbolic Execution",
            "direction": "tool_augmented_reasoning",
            "year": 2021,
            "keywords": ["tool use", "symbolic reasoning"],
            "abstract": "We propose a method that combines neural reasoning with symbolic tool calls.",
            "citation_ids": ["paper_002"]
        },
        {
            "paper_id": "paper_002",
            "title": "Learning to Call External APIs for Complex QA",
            "direction": "tool_augmented_reasoning",
            "year": 2022,
            "keywords": ["API calling", "question answering"],
            "abstract": "This work extends tool-augmented reasoning to multi-step API orchestration.",
            "citation_ids": ["paper_003"]
        },
        {
            "paper_id": "paper_003",
            "title": "Neural-Symbolic Programming with Tool Memories",
            "direction": "tool_augmented_reasoning",
            "year": 2023,
            "keywords": ["memory", "neural-symbolic"],
            "abstract": "We introduce persistent tool memories for improved generalization.",
            "citation_ids": ["paper_004"]
        },
        {
            "paper_id": "paper_004",
            "title": "Scaling Tool-Augmented Reasoning with Retrieval",
            "direction": "tool_augmented_reasoning",
            "year": 2024,
            "keywords": ["scale", "retrieval", "tool"],
            "abstract": "We show that retrieval-augmented tool use scales to thousands of APIs.",
            "citation_ids": []
        }
    ]

    # 干扰方向论文（efficient_vision）
    vision_papers = [
        {
            "paper_id": "paper_101",
            "title": "Efficient Vision Transformers via Pruning",
            "direction": "efficient_vision",
            "year": 2022,
            "keywords": ["vision", "efficiency", "pruning"],
            "abstract": "We prune redundant heads in vision transformers.",
            "citation_ids": ["paper_102"]
        },
        {
            "paper_id": "paper_102",
            "title": "Lightweight Convolutional Networks for Mobile",
            "direction": "efficient_vision",
            "year": 2023,
            "keywords": ["lightweight", "mobile", "convnet"],
            "abstract": "Design of a highly efficient convnet for mobile devices.",
            "citation_ids": []
        },
        {
            "paper_id": "paper_103",
            "title": "Knowledge Distillation for Vision Models",
            "direction": "efficient_vision",
            "year": 2023,
            "keywords": ["distillation", "vision"],
            "abstract": "We apply knowledge distillation to reduce vision model size.",
            "citation_ids": ["paper_101"]
        }
    ]

    papers = tar_papers + vision_papers
    random.shuffle(papers)  # 打乱顺序增加迷惑性

    with open("data/papers/papers.json", "w") as f:
        json.dump({"papers": papers}, f, indent=2)

    print("Environment built: data/papers/papers.json with 7 papers (4 target + 3 distractor).")

if __name__ == "__main__":
    build_env()
