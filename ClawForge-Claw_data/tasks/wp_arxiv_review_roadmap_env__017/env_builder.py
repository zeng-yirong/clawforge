import os
import json
import shutil

def build_env():
    # Clean slate (ensure we start fresh)
    if os.path.exists("data"):
        shutil.rmtree("data")

    # --- Create main paper database with noise ---
    os.makedirs("data/papers", exist_ok=True)

    correct_papers = [
        {
            "paper_id": "p001",
            "title": "Tool-Augmented LLMs",
            "direction": "tool_augmented_reasoning",
            "year": 2019,
            "keywords": ["language models", "tools"],
            "abstract": "We explore augmenting LLMs with external tool calls to improve reasoning.",
            "citation_ids": ["p002"]
        },
        {
            "paper_id": "p002",
            "title": "Reasoning with External Tools",
            "direction": "tool_augmented_reasoning",
            "year": 2020,
            "keywords": ["reasoning", "tool use"],
            "abstract": "A framework for combining neural models with symbolic tools.",
            "citation_ids": ["p001", "p003"]
        },
        {
            "paper_id": "p003",
            "title": "Augmented Language Models",
            "direction": "tool_augmented_reasoning",
            "year": 2021,
            "keywords": ["augmentation", "retrieval"],
            "abstract": "Large language models augmented with retrieval and tool invocation.",
            "citation_ids": ["p002"]
        },
        {
            "paper_id": "p004",
            "title": "Tool Learning for Agents",
            "direction": "tool_augmented_reasoning",
            "year": 2022,
            "keywords": ["agents", "tool learning"],
            "abstract": "Training agents to autonomously discover and use tools.",
            "citation_ids": ["p003"]
        },
        {
            "paper_id": "p005",
            "title": "Interactive Tool Use",
            "direction": "tool_augmented_reasoning",
            "year": 2023,
            "keywords": ["interaction", "human-ai"],
            "abstract": "A study of interactive tool use in mixed-initiative settings.",
            "citation_ids": ["p004"]
        }
    ]

    noise_papers = [
        {
            "paper_id": "p101",
            "title": "Efficient Vision Transformers",
            "direction": "efficient_vision",
            "year": 2022,
            "keywords": ["vision", "efficiency"],
            "abstract": "Reducing computational cost of vision transformers.",
            "citation_ids": []
        },
        {
            "paper_id": "p102",
            "title": "Wrong Format Paper",
            "direction": "tool-augmented-reasoning",   # hyphenated
            "year": 2021,
            "keywords": ["tools", "reasoning"],
            "abstract": "A paper with a misformatted direction field.",
            "citation_ids": []
        },
        {
            "paper_id": "p103",
            "title": "Capitalized Paper",
            "direction": "Tool Augmented Reasoning",   # spaces and capital
            "year": 2020,
            "keywords": ["tools"],
            "abstract": "Another misformatted direction.",
            "citation_ids": []
        },
        {
            "paper_id": "p104",
            "title": "Missing Direction Paper",
            # direction key intentionally absent
            "year": 2023,
            "keywords": ["unknown"],
            "abstract": "A paper with no direction field at all.",
            "citation_ids": []
        },
        {
            "paper_id": "p105",
            "title": "Another Vision Paper",
            "direction": "efficient_vision",
            "year": 2019,
            "keywords": ["vision", "attention"],
            "abstract": "A second efficient vision paper.",
            "citation_ids": []
        },
        {
            "paper_id": "p106",
            "title": "Yet Another Vision Paper",
            "direction": "efficient_vision",
            "year": 2021,
            "keywords": ["vision"],
            "abstract": "Third efficient vision paper.",
            "citation_ids": []
        }
    ]

    all_papers = correct_papers + noise_papers

    with open("data/papers/papers.json", "w") as f:
        json.dump({"papers": all_papers}, f, indent=2)

    # --- Create additional distracting files ---
    # A CSV pretending to be old paper data
    with open("data/papers/old_papers.csv", "w") as f:
        f.write("paper_id,title,year\np201,Old Paper,2017\np202,Ancient Paper,2016\n")

    # An irrelevant accounts file
    os.makedirs("data", exist_ok=True)
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": [{"account_id": "lin", "display_name": "Lin", "department": "AI", "email": "lin@lab.com", "permissions": ["read"]}]}, f)

    # An attachments file (noise)
    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": [{"path": "fig1.png", "title": "Figure 1", "kind": "image", "description": "A plot"}]}, f)

    print("Environment built successfully.")

if __name__ == "__main__":
    build_env()
