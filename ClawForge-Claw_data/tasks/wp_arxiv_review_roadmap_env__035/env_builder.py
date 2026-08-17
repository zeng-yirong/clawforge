import os
import json

def build_env():
    # Core directories
    os.makedirs("data/papers", exist_ok=True)
    os.makedirs("data/events", exist_ok=True)

    # ---- Main papers.json ----
    papers = [
        # efficient_vision papers (5 papers, unique years)
        {"paper_id": "ev01", "title": "EfficientNet: Rethinking Model Scaling",
         "direction": "efficient_vision", "year": 2019,
         "keywords": ["scaling", "efficient"],
         "abstract": "We propose a new scaling method...",
         "citation_ids": ["ev02", "ev03"]},
        {"paper_id": "ev02", "title": "MobileNets: Efficient Convolutional Neural Networks",
         "direction": "efficient_vision", "year": 2017,
         "keywords": ["mobile", "depthwise"],
         "abstract": "MobileNets are based on a streamlined architecture...",
         "citation_ids": ["ev03"]},
        {"paper_id": "ev03", "title": "ShuffleNet: An Extremely Efficient CNN",
         "direction": "efficient_vision", "year": 2018,
         "keywords": ["shuffle", "group conv"],
         "abstract": "ShuffleNet introduces pointwise group convolution...",
         "citation_ids": []},
        {"paper_id": "ev04", "title": "GhostNet: More Features from Cheap Operations",
         "direction": "efficient_vision", "year": 2020,
         "keywords": ["ghost", "cheap"],
         "abstract": "GhostNet generates more features from cheap operations...",
         "citation_ids": ["ev01", "ev02"]},
        {"paper_id": "ev05", "title": "EfficientDet: Scalable and Efficient Object Detection",
         "direction": "efficient_vision", "year": 2021,
         "keywords": ["detection", "scalable"],
         "abstract": "EfficientDet is a family of object detectors...",
         "citation_ids": ["ev01"]},
        # Distractor direction (tool_augmented_reasoning)
        {"paper_id": "ta01", "title": "Tool-Augmented Reasoning with Transformers",
         "direction": "tool_augmented_reasoning", "year": 2022,
         "keywords": ["tool", "reasoning"], "abstract": "...", "citation_ids": []},
        {"paper_id": "ta02", "title": "Reasoning via Tool Use",
         "direction": "tool_augmented_reasoning", "year": 2021,
         "keywords": ["tool", "planning"], "abstract": "...", "citation_ids": ["ta01"]},
        {"paper_id": "ta03", "title": "Augmented Language Models",
         "direction": "tool_augmented_reasoning", "year": 2023,
         "keywords": ["augmented", "language"], "abstract": "...", "citation_ids": ["ta02"]},
        # Dirty records (missing direction, wrong direction)
        {"paper_id": "ev06", "title": "Bad Paper",
         "year": 2020, "keywords": [], "abstract": "Missing direction", "citation_ids": []},
        {"paper_id": "ev07", "title": "Wrong Direction",
         "direction": "tool_augmented_reasoning", "year": 2019,
         "keywords": [], "abstract": "...", "citation_ids": []},
    ]
    with open("data/papers/papers.json", "w") as f:
        json.dump({"papers": papers}, f, indent=2)

    # ---- Distractor files ----
    # attachments.json (irrelevant)
    attachments = [
        {"path": "data/templates/review_template.md", "title": "Review Template",
         "kind": "markdown", "description": "A template for writing review."},
        {"path": "data/templates/roadmap_template.md", "title": "Roadmap Template",
         "kind": "markdown", "description": "A template for roadmap."}
    ]
    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

    # accounts.json (irrelevant)
    accounts = [
        {"account_id": "a1", "display_name": "Alice", "department": "CS",
         "email": "alice@uni.edu", "permissions": ["read"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # contacts.json (irrelevant)
    contacts = [
        {"contact_id": "c1", "name": "Bob", "role": "researcher", "email": "bob@uni.edu"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # old_papers_backup.json (contains an outdated duplicate of ev01)
    old_papers = [
        {"paper_id": "ev01", "title": "EfficientNet (old)",
         "direction": "efficient_vision", "year": 2018,
         "keywords": [], "abstract": "old version", "citation_ids": []}
    ]
    with open("data/old_papers_backup.json", "w") as f:
        json.dump({"papers": old_papers}, f, indent=2)

    # Noise file in events/
    with open("data/events/log.txt", "w") as f:
        f.write("noise\n")

if __name__ == "__main__":
    build_env()
