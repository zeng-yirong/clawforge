import os
import json
import random
random.seed(42)

def build_env():
    # Ensure base directories exist
    os.makedirs("data/papers", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("report", exist_ok=True)  # placeholder, will be populated by agent

    # ========== papers.json ==========
    papers = []
    # Valid papers (tool_augmented_reasoning, year 2022-2024, no obsolete keyword)
    papers.append({
        "paper_id": "arxiv_2023_11023",
        "title": "Tool Learning with Large Language Models",
        "direction": "tool_augmented_reasoning",
        "year": 2023,
        "keywords": ["LLM", "tool use", "reasoning"],
        "abstract": "We explore how LLMs can leverage external tools to solve complex reasoning tasks.",
        "citation_ids": []
    })
    papers.append({
        "paper_id": "arxiv_2022_08901",
        "title": "Chain of Thought with Tool Augmentation",
        "direction": "tool_augmented_reasoning",
        "year": 2022,
        "keywords": ["chain-of-thought", "tool", "reasoning"],
        "abstract": "A method that interleaves reasoning steps with tool calls.",
        "citation_ids": []
    })
    papers.append({
        "paper_id": "arxiv_2024_04567",
        "title": "Autonomous Agents that Use APIs",
        "direction": "tool_augmented_reasoning",
        "year": 2024,
        "keywords": ["agent", "API", "planning"],
        "abstract": "Agents that plan and execute API calls to achieve goals.",
        "citation_ids": []
    })
    papers.append({
        "paper_id": "arxiv_2023_13245",
        "title": "Interactive Reasoning with Database Tools",
        "direction": "tool_augmented_reasoning",
        "year": 2023,
        "keywords": ["database", "interactive", "reasoning"],
        "abstract": "Combining SQL queries with reasoning steps.",
        "citation_ids": []
    })
    # Invalid: year outside range
    papers.append({
        "paper_id": "arxiv_2021_99887",
        "title": "Early Tool Reasoning",
        "direction": "tool_augmented_reasoning",
        "year": 2021,
        "keywords": ["early", "tool"],
        "abstract": "Old paper before the surge.",
        "citation_ids": []
    })
    papers.append({
        "paper_id": "arxiv_2025_00123",
        "title": "Future Tool Reasoning",
        "direction": "tool_augmented_reasoning",
        "year": 2025,
        "keywords": ["future", "tool"],
        "abstract": "Not published yet.",
        "citation_ids": []
    })
    # Invalid: wrong direction
    papers.append({
        "paper_id": "arxiv_2023_55443",
        "title": "Efficient Vision Backbones",
        "direction": "efficient_vision",
        "year": 2023,
        "keywords": ["vision", "efficient"],
        "abstract": "Not relevant.",
        "citation_ids": []
    })
    # Invalid: has 'obsolete' keyword
    papers.append({
        "paper_id": "arxiv_2022_77777",
        "title": "Obsolete Tool Method",
        "direction": "tool_augmented_reasoning",
        "year": 2022,
        "keywords": ["obsolete", "tool"],
        "abstract": "This method is outdated.",
        "citation_ids": []
    })
    papers.append({
        "paper_id": "arxiv_2023_88888",
        "title": "Another Obsolete Approach",
        "direction": "tool_augmented_reasoning",
        "year": 2023,
        "keywords": ["LLM", "obsolete"],
        "abstract": "Also outdated.",
        "citation_ids": []
    })
    # Duplicate paper_id? Not allowed, but we add one as duplicate (will be ignored by verifier if we pick first)
    # Actually we ensure no duplicate IDs here. All IDs are unique.

    with open("data/papers/papers.json", "w") as f:
        json.dump({"papers": papers}, f, indent=2)

    # ========== attachments.json (distractors) ==========
    attachments = [
        {
            "path": "attachments/vision_paper.pdf",
            "title": "Efficient Vision Paper",
            "kind": "pdf",
            "description": "Full text of a vision paper (irrelevant)"
        },
        {
            "path": "attachments/tool_reasoning_2023.pdf",
            "title": "Tool Learning 2023",
            "kind": "pdf",
            "description": "Full text of arxiv_2023_11023"
        },
        {
            "path": "attachments/old_method.pdf",
            "title": "Obsolete Method",
            "kind": "pdf",
            "description": "Full text of arxiv_2022_77777"
        }
    ]
    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

    # ========== extra irrelevant files ==========
    os.makedirs("data/accounts", exist_ok=True)
    accounts = [
        {"account_id": "alice", "display_name": "Alice", "department": "AI", "email": "alice@lab.institute", "permissions": ["read"]},
        {"account_id": "bob", "display_name": "Bob", "department": "Systems", "email": "bob@lab.institute", "permissions": ["write"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # Also create an empty contacts.json to add noise
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": []}, f, indent=2)

    # ========== summary ==========
    print("Environment built. Valid paper IDs:", [p["paper_id"] for p in papers if
        p["direction"] == "tool_augmented_reasoning" and 2022 <= p["year"] <= 2024 and
        not any("obsolete" in kw.lower() for kw in p["keywords"])])

if __name__ == "__main__":
    build_env()
