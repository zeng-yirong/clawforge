import os
import json

def build_env():
    # Ensure required directories
    os.makedirs("data/papers", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    # ---- papers.json ----
    papers = [
        {
            "paper_id": "T001",
            "title": "Augmented Reasoning with Tool Use",
            "direction": "tool_augmented_reasoning",
            "year": 2021,
            "keywords": ["reasoning", "tool use"],
            "abstract": "A framework that integrates external tools into reasoning chains.",
            "citation_ids": []
        },
        {
            "paper_id": "T002",
            "title": "Tool-augmented Language Models",
            "direction": "tool_augmented_reasoning",
            "year": 2022,
            "keywords": ["language model", "tool augmentation"],
            "abstract": "Extends language models with dynamic tool invocation.",
            "citation_ids": ["T001"]
        },
        {
            "paper_id": "T003",
            "title": "Scaling Tool-Augmented Reasoning",
            "direction": "tool_augmented_reasoning",
            "year": 2023,
            "keywords": ["scaling", "reasoning"],
            "abstract": "Explores scaling laws for tool-augmented reasoning systems.",
            "citation_ids": ["T002"]
        },
        # Interference papers – different direction
        {
            "paper_id": "E001",
            "title": "Efficient Vision Transformers",
            "direction": "efficient_vision",
            "year": 2021,
            "keywords": ["vision", "transformer"],
            "abstract": "A lightweight vision transformer for real-time tasks.",
            "citation_ids": []
        },
        {
            "paper_id": "E002",
            "title": "Vision-Language Models for Robotics",
            "direction": "efficient_vision",
            "year": 2022,
            "keywords": ["robotics", "vision-language"],
            "abstract": "Combines vision and language for robotic manipulation.",
            "citation_ids": ["E001"]
        },
        # Interference paper with empty direction
        {
            "paper_id": "X001",
            "title": "Miscellaneous Study",
            "direction": "",
            "year": 2020,
            "keywords": [],
            "abstract": "A paper with missing direction field.",
            "citation_ids": []
        }
    ]
    with open("data/papers/papers.json", "w") as f:
        json.dump({"papers": papers}, f, indent=2)

    # ---- Distraction files ----
    # attachments.json (relevant but not needed for the answer)
    attachments = [
        {"path": "data/papers/papers.json", "title": "Paper dump", "kind": "json", "description": "All papers from ArXiv"}
    ]
    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

    # accounts.json (totally unrelated)
    accounts = [
        {"account_id": "A001", "display_name": "Alice", "department": "AI", "email": "alice@example.com", "permissions": ["read"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # contacts.json (unrelated)
    contacts = [
        {"contact_id": "C001", "name": "Bob", "role": "reviewer", "email": "bob@example.com"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

if __name__ == "__main__":
    build_env()
