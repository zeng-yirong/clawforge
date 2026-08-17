import os
import json

def build_env():
    os.makedirs("data", exist_ok=True)

    papers = [
        {
            "paper_id": "p001",
            "title": "Augmenting Language Models with Tools",
            "direction": "tool_augmented_reasoning",
            "year": 2020,
            "keywords": ["tool use", "LLM"],
            "abstract": "We present a method to augment language models with external tools.",
            "citation_ids": []
        },
        {
            "paper_id": "p002",
            "title": "Toolformer: Teaching Language Models to Use Tools",
            "direction": "tool_augmented_reasoning",
            "year": 2022,
            "keywords": ["toolformer", "API"],
            "abstract": "Toolformer learns to use APIs from demonstrations.",
            "citation_ids": ["p001"]
        },
        {
            "paper_id": "p003",
            "title": "ReAct: Synergizing Reasoning and Acting in Language Models",
            "direction": "tool_augmented_reasoning",
            "year": 2022,
            "keywords": ["react", "reasoning"],
            "abstract": "ReAct combines reasoning traces with action plans.",
            "citation_ids": ["p001", "p002"]
        },
        {
            "paper_id": "p004",
            "title": "Efficient Vision Transformers",
            "direction": "efficient_vision",
            "year": 2021,
            "keywords": ["vision", "efficient"],
            "abstract": "Efficient vision transformers for image classification.",
            "citation_ids": []
        },
        {
            "paper_id": "p005",
            "title": "Scaling Vision Transformers",
            "direction": "efficient_vision",
            "year": 2022,
            "keywords": ["scaling", "vit"],
            "abstract": "Scaling vision transformers beyond 1B parameters.",
            "citation_ids": ["p004"]
        },
        {
            "paper_id": "p006",
            "title": "No Direction Paper",
            "direction": "",
            "year": 2023,
            "keywords": [],
            "abstract": "Some abstract without direction.",
            "citation_ids": []
        }
    ]

    with open("data/papers.json", "w") as f:
        json.dump({"papers": papers}, f, indent=2)

    attachments = [
        {
            "path": "data/attachments/note.txt",
            "title": "Reading Notes",
            "kind": "text",
            "description": "Some personal notes, not helpful."
        }
    ]
    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

    contacts = [
        {"contact_id": "c001", "name": "Alice", "role": "Reviewer", "email": "alice@example.com"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

if __name__ == "__main__":
    build_env()
