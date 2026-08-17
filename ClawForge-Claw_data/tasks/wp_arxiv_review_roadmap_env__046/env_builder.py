import json, os, random

def build_env():
    # Create necessary subdirectories
    os.makedirs("data/papers", exist_ok=True)
    os.makedirs("review", exist_ok=True)

    # Papers (both directions + one duplicate with wrong direction)
    papers = [
        # Tool-Augmented Reasoning papers (5)
        {
            "paper_id": "TAR-2020",
            "title": "ToolFormer: Learning to Use APIs",
            "direction": "tool_augmented_reasoning",
            "year": 2020,
            "keywords": ["tool use", "API", "language model"],
            "abstract": "We show how a language model can learn to call external APIs to answer questions, improving factual accuracy.",
            "citation_ids": ["TAR-2021"]
        },
        {
            "paper_id": "TAR-2021",
            "title": "ReAct: Synergizing Reasoning and Acting",
            "direction": "tool_augmented_reasoning",
            "year": 2021,
            "keywords": ["reasoning", "action", "tool calling"],
            "abstract": "ReAct interleaves reasoning traces with tool calls, achieving better performance on complex tasks.",
            "citation_ids": ["TAR-2022"]
        },
        {
            "paper_id": "TAR-2022",
            "title": "ToolAlpaca: Open Tool-Augmented LLMs",
            "direction": "tool_augmented_reasoning",
            "year": 2022,
            "keywords": ["open source", "tool learning", "instruction tuning"],
            "abstract": "We release a fully open-source tool-augmented LLM trained on diverse tool-use data.",
            "citation_ids": ["TAR-2023"]
        },
        {
            "paper_id": "TAR-2023",
            "title": "Gorilla: Large Language Model Connected with Massive APIs",
            "direction": "tool_augmented_reasoning",
            "year": 2023,
            "keywords": ["API selection", "large language model", "tool retrieval"],
            "abstract": "Gorilla finetunes a LLM to select and call over 1,600 APIs with high accuracy.",
            "citation_ids": ["TAR-2024"]
        },
        {
            "paper_id": "TAR-2024",
            "title": "ToolLLM: Facilitating Large Language Models to Master 16000+ Real-world APIs",
            "direction": "tool_augmented_reasoning",
            "year": 2024,
            "keywords": ["real-world APIs", "tool learning", "planning"],
            "abstract": "ToolLLM demonstrates how to equip LLMs with over 16,000 real-world APIs through instruction tuning and self-improvement.",
            "citation_ids": []
        },
        # Distractor papers (different direction)
        {
            "paper_id": "EV-2019",
            "title": "Efficient Vision Transformers",
            "direction": "efficient_vision",
            "year": 2019,
            "keywords": ["vision transformer", "efficiency", "attention"],
            "abstract": "A novel architecture for efficient image classification with reduced computational cost.",
            "citation_ids": ["EV-2020"]
        },
        {
            "paper_id": "EV-2020",
            "title": "MobileViT: Light-weight Vision Transformer",
            "direction": "efficient_vision",
            "year": 2020,
            "keywords": ["mobile", "vision transformer", "lightweight"],
            "abstract": "MobileViT combines CNN and ViT for efficient on-device vision tasks.",
            "citation_ids": ["EV-2021"]
        },
        {
            "paper_id": "EV-2021",
            "title": "Compact Convolutional Transformers",
            "direction": "efficient_vision",
            "year": 2021,
            "keywords": ["compact", "transformer", "convolution"],
            "abstract": "A hybrid architecture achieving state-of-the-art accuracy on small datasets.",
            "citation_ids": ["EV-2022"]
        },
        # Fake duplicate (same id but wrong direction – should be ignored)
        {
            "paper_id": "TAR-2022",
            "title": "Fake Duplicate (Ignore this)",
            "direction": "efficient_vision",
            "year": 2022,
            "keywords": ["fake"],
            "abstract": "This is a deliberately inserted duplicate with wrong direction to test filtering.",
            "citation_ids": []
        }
    ]

    with open("data/papers/papers.json", "w") as f:
        json.dump({"papers": papers}, f, indent=2)

    # Attachments (distractor)
    attachments = [
        {
            "path": "notes/meeting_notes.txt",
            "title": "Group Meeting Notes",
            "kind": "text",
            "description": "Random notes about vision projects."
        },
        {
            "path": "notes/reading_list.md",
            "title": "Reading List",
            "kind": "markdown",
            "description": "A list of papers on efficient vision."
        }
    ]
    os.makedirs("notes", exist_ok=True)
    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

    # Accounts / Contacts (distractors)
    accounts = [
        {"account_id": "karen", "display_name": "Karen Liu", "department": "AI Strategy", "email": "karen@example.com", "permissions": ["read"]},
        {"account_id": "alex", "display_name": "Alex Chen", "department": "Research", "email": "alex@example.com", "permissions": ["read","write"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    contacts = [
        {"contact_id": "c001", "name": "Bob Zhang", "role": "Lead Researcher", "email": "bob@example.com"},
        {"contact_id": "c002", "name": "Carol Wang", "role": "Postdoc", "email": "carol@example.com"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # Also create a few empty/irrelevant files to increase noise
    with open("README.txt", "w") as f:
        f.write("ArXiv snapshot taken on 2024-10-01\n")
    os.makedirs("logs", exist_ok=True)
    with open("logs/empty.log", "w") as f:
        f.write("")

if __name__ == "__main__":
    build_env()
