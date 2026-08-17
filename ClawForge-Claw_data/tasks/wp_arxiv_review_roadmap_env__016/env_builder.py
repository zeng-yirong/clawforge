import os
import json

def build_env():
    # 确保目录结构
    os.makedirs("data/papers", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    # 核心论文数据
    papers = [
        {
            "paper_id": "tar001",
            "title": "Learning to Reason with Tools",
            "direction": "tool_augmented_reasoning",
            "year": 2021,
            "keywords": ["tool", "reasoning"],
            "abstract": "We show how language models can learn to invoke external tools to improve reasoning.",
            "citation_ids": []
        },
        {
            "paper_id": "tar002",
            "title": "Tool-Augmented Language Models",
            "direction": "tool_augmented_reasoning",
            "year": 2022,
            "keywords": ["tool", "language model"],
            "abstract": "A comprehensive survey of language models that augment themselves with tool use.",
            "citation_ids": []
        },
        {
            "paper_id": "tar003",
            "title": "Beyond Text: Multi-tool Reasoning",
            "direction": "tool_augmented_reasoning",
            "year": 2023,
            "keywords": ["multi-tool", "reasoning"],
            "abstract": "Extending tool use to encompass diverse modalities and APIs.",
            "citation_ids": []
        },
        # 干扰项：不同方向
        {
            "paper_id": "ev001",
            "title": "Efficient Vision Transformers",
            "direction": "efficient_vision",
            "year": 2021,
            "keywords": ["vision", "efficient"],
            "abstract": "Reducing computational cost of vision transformers.",
            "citation_ids": []
        },
        {
            "paper_id": "ev002",
            "title": "Lightweight Vision Models",
            "direction": "efficient_vision",
            "year": 2022,
            "keywords": ["vision", "lightweight"],
            "abstract": "Designing tiny yet accurate vision architectures.",
            "citation_ids": []
        },
        # 额外干扰：年份重复但方向不同
        {
            "paper_id": "ev003",
            "title": "Vision Tool Integration",
            "direction": "efficient_vision",
            "year": 2023,
            "keywords": ["vision", "tool"],
            "abstract": "Attempt to integrate tools into vision models.",
            "citation_ids": []
        }
    ]

    # 写入 papers.json（带 wrapper）
    with open("data/papers/papers.json", "w") as f:
        json.dump({"papers": papers}, f, indent=2)

    # 其他干扰文件 —— accounts.json, attachments.json, contacts.json
    accounts = [
        {"account_id": "alice", "display_name": "Alice Chen", "department": "AI", "email": "alice@lab.org", "permissions": ["read"]},
        {"account_id": "bob", "display_name": "Bob Liu", "department": "NLP", "email": "bob@lab.org", "permissions": ["read", "write"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    attachments = [
        {"path": "data/papers/tar001_supp.pdf", "title": "Supplementary for Learning to Reason with Tools", "kind": "pdf", "description": "Appendix and experiments"},
        {"path": "data/papers/ev001_code.zip", "title": "Efficient Vision Transformers Code", "kind": "zip", "description": "Implementation in PyTorch"}
    ]
    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

    contacts = [
        {"contact_id": "c01", "name": "Yan Zhang", "role": "reviewer", "email": "yan@example.org"},
        {"contact_id": "c02", "name": "Maria Schmidt", "role": "lead", "email": "maria@example.org"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # 额外脏数据：一个旧格式的 CSV 文件（干扰）
    with open("data/old_papers.csv", "w") as f:
        f.write("id,title,year\nxxx,broken,2020\n")

if __name__ == "__main__":
    build_env()
