import os
import json

def build_env():
    # 创建目录
    os.makedirs("data/papers", exist_ok=True)
    os.makedirs("data/attachments", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 干扰文件：accounts.json
    accounts = {
        "accounts": [
            {
                "account_id": "a01",
                "display_name": "Alice Chen",
                "department": "CS",
                "email": "alice@univ.edu",
                "permissions": ["read", "write"]
            }
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f)

    # 干扰文件：contacts.json
    contacts = {
        "contacts": {
            "c01": {
                "contact_id": "c01",
                "name": "Bob Lee",
                "role": "reviewer",
                "email": "bob@univ.edu"
            }
        }
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f)

    # 干扰文件：attachments.json（无实质内容）
    attachments = {
        "attachments": [
            {
                "path": "notes/meeting.md",
                "title": "Meeting notes",
                "kind": "markdown",
                "description": "Initial discussion"
            },
            {
                "path": "figures/overview.png",
                "title": "Overview figure",
                "kind": "image",
                "description": "Conceptual diagram"
            }
        ]
    }
    with open("data/attachments.json", "w") as f:
        json.dump(attachments, f)

    # 主论文数据
    papers = [
        {
            "paper_id": "TAR-001",
            "title": "Learning to Reason with Tools: A Survey",
            "direction": "tool_augmented_reasoning",
            "year": 2023,
            "keywords": ["tool use", "reasoning", "survey"],
            "abstract": "This paper surveys recent advances in tool-augmented reasoning...",
            "citation_ids": ["TAR-003", "EFF-001"]
        },
        {
            "paper_id": "TAR-002",
            "title": "ToolFormer: Augmenting LLMs with External APIs",
            "direction": "tool_augmented_reasoning",
            "year": 2024,
            "keywords": ["LLM", "API", "tool learning"],
            "abstract": "We introduce ToolFormer, a model that learns to call APIs...",
            "citation_ids": ["TAR-003", "TAR-001", "EFF-002"]
        },
        {
            "paper_id": "TAR-003",
            "title": "Chain-of-Thought with Tool Augmentation",
            "direction": "tool_augmented_reasoning",
            "year": 2024,
            "keywords": ["chain-of-thought", "tool use", "reasoning"],
            "abstract": "Combining chain-of-thought prompting with tool feedback...",
            "citation_ids": ["EFF-001"]
        },
        {
            "paper_id": "EFF-001",
            "title": "Efficient Vision Transformers for Edge Devices",
            "direction": "efficient_vision",
            "year": 2023,
            "keywords": ["vision transformer", "efficiency", "edge"],
            "abstract": "We propose a lightweight vision transformer architecture...",
            "citation_ids": ["TAR-003", "EFF-002"]
        },
        {
            "paper_id": "EFF-002",
            "title": "Knowledge Distillation for Vision Models",
            "direction": "efficient_vision",
            "year": 2024,
            "keywords": ["knowledge distillation", "vision"],
            "abstract": "A study on distilling large vision models into small ones...",
            "citation_ids": ["EFF-001"]
        }
    ]
    with open("data/papers/papers.json", "w") as f:
        json.dump({"papers": papers}, f)

    # 干扰文件：papers_backup.json（过时数据，方向错乱，引用不同）
    backup_papers = [
        {
            "paper_id": "TAR-001",
            "title": "Learning to Reason with Tools (Old Version)",
            "direction": "tool_augmented_reasoning",
            "year": 2022,
            "keywords": ["tool use", "reasoning"],
            "abstract": "Old survey...",
            "citation_ids": ["EFF-001"]
        },
        {
            "paper_id": "TAR-003",
            "title": "Chain-of-Thought with Tool Augmentation (Draft)",
            "direction": "efficient_vision",  # 错误方向
            "year": 2023,
            "keywords": ["chain-of-thought"],
            "abstract": "Draft version...",
            "citation_ids": []
        },
        {
            "paper_id": "FAKE-001",
            "title": "Spurious Paper",
            "direction": "tool_augmented_reasoning",
            "year": 2025,
            "keywords": [],
            "abstract": "Not real.",
            "citation_ids": ["TAR-001"]
        }
    ]
    with open("data/papers/papers_backup.json", "w") as f:
        json.dump({"papers": backup_papers}, f)

if __name__ == "__main__":
    build_env()
