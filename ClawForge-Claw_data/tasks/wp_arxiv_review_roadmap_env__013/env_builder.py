import os
import json
import random

def build_env():
    # Ensure directories exist
    os.makedirs("data/papers", exist_ok=True)
    os.makedirs("data/attachments", exist_ok=True)
    os.makedirs("data/cache", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    # ---- papers.json (main data with intentional dirty entries) ----
    papers = [
        {
            "paper_id": "p001",
            "title": "Efficient Vision Transformer",
            "direction": "efficient_vision",
            "year": 2020,
            "keywords": ["transformer", "efficiency"],
            "abstract": "Proposes a lightweight transformer for vision tasks.",
            "citation_ids": ["p003"]
        },
        {
            "paper_id": "p002",
            "title": "Tool-Augmented Reasoning",
            "direction": "tool_augmented_reasoning",
            "year": 2021,
            "keywords": ["tool", "reasoning"],
            "abstract": "Enhances LLMs with external tool use.",
            "citation_ids": []
        },
        {
            "paper_id": "p003",
            "title": "Lightweight CNN for Mobile",
            "direction": "efficient_vision",
            "year": 2022,
            "keywords": ["cnn", "mobile"],
            "abstract": "A compact CNN optimized for mobile devices.",
            "citation_ids": ["p001", "p005"]
        },
        {
            "paper_id": "p004",
            "title": "Large Language Model Agents",
            "direction": "tool_augmented_reasoning",
            "year": 2023,
            "keywords": ["llm", "agent"],
            "abstract": "Survey of LLM-based autonomous agents.",
            "citation_ids": []
        },
        {
            "paper_id": "p005",
            "title": "Pruning for Edge Deployment",
            "direction": "efficient_vision",
            "year": 2023,
            "keywords": ["pruning", "edge"],
            "abstract": "Structured pruning techniques for edge devices.",
            "citation_ids": []
        },
        {
            "paper_id": "p006",
            "title": "Mistyped Direction",
            "direction": "efficient-vision",          # wrong hyphen
            "year": 2022,
            "keywords": [],
            "abstract": "Dummy paper with malformed direction.",
            "citation_ids": []
        },
        {
            "paper_id": "p007",
            "title": "Missing Direction",
            "year": 2021,                              # no direction field
            "keywords": [],
            "abstract": "Missing direction field.",
            "citation_ids": []
        },
        {
            "paper_id": "p008",
            "title": "Year as String",
            "direction": "efficient_vision",
            "year": "2024",                             # string instead of int
            "keywords": [],
            "abstract": "Paper with year stored as string.",
            "citation_ids": []
        }
    ]
    with open("data/papers/papers.json", "w") as f:
        json.dump(papers, f, indent=2)

    # ---- attachments/notes.txt (distraction) ----
    with open("data/attachments/notes.txt", "w") as f:
        f.write("Remember to check p003 citation list for recent works.\n")

    # ---- cache/summaries.json (distraction) ----
    cache_summaries = {
        "p005": "This paper is highly cited for its practical pruning approach."
    }
    with open("data/cache/summaries.json", "w") as f:
        json.dump(cache_summaries, f, indent=2)

    # ---- logs/error.log (distraction) ----
    with open("logs/error.log", "w") as f:
        f.write("WARNING: Some papers have incomplete fields\n")

if __name__ == "__main__":
    build_env()
