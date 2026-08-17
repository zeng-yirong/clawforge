import os
import json
import random

def build_env():
    # Create required directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    # Define papers list with interference, duplicates, incomplete records
    papers = [
        # Valid tool_augmented_reasoning papers
        {
            "paper_id": "TAR01",
            "title": "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models",
            "direction": "tool_augmented_reasoning",
            "year": 2022,
            "keywords": ["reasoning", "chain-of-thought"],
            "abstract": "We explore how generating a chain of thought improves reasoning.",
            "citation_ids": ["TAR03"]
        },
        {
            "paper_id": "TAR02",
            "title": "ReAct: Synergizing Reasoning and Acting in Language Models",
            "direction": "tool_augmented_reasoning",
            "year": 2022,
            "keywords": ["reasoning", "acting"],
            "abstract": "Combines reasoning traces and action plans.",
            "citation_ids": ["TAR01"]
        },
        {
            "paper_id": "TAR03",
            "title": "Toolformer: Language Models Can Teach Themselves to Use Tools",
            "direction": "tool_augmented_reasoning",
            "year": 2023,
            "keywords": ["tool", "augmented"],
            "abstract": "Self-supervised learning for tool use.",
            "citation_ids": []
        },
        {
            "paper_id": "TAR04",
            "title": "ART: Automatic multi-step reasoning and tool use",
            "direction": "tool_augmented_reasoning",
            "year": 2022,
            "keywords": ["reasoning", "automatic"],
            "abstract": "Learns to decompose tasks automatically.",
            "citation_ids": ["TAR01"]
        },
        {
            "paper_id": "TAR05",
            "title": "Thought Generation and Tool Augmentation",
            "direction": "tool_augmented_reasoning",
            "year": 2021,
            "keywords": ["reasoning", "generation"],
            "abstract": "Early work on generating reasoning traces.",
            "citation_ids": []
        },
        # Efficient vision papers (distractors)
        {
            "paper_id": "EFF01",
            "title": "EfficientNet: Rethinking Model Scaling",
            "direction": "efficient_vision",
            "year": 2019,
            "keywords": ["efficient", "vision"],
            "abstract": "Systematic scaling of CNNs.",
            "citation_ids": []
        },
        {
            "paper_id": "EFF02",
            "title": "MobileNets: Efficient Convolutional Neural Networks",
            "direction": "efficient_vision",
            "year": 2017,
            "keywords": ["mobile", "vision"],
            "abstract": "Depthwise separable convolutions.",
            "citation_ids": []
        },
        # Incomplete record (missing year)
        {
            "paper_id": "DIR01",
            "title": "Incomplete Paper",
            "direction": "tool_augmented_reasoning",
            "keywords": ["incomplete"],
            "abstract": "Missing year.",
            "citation_ids": []
        },
        # Duplicate ID but different direction (should be ignored)
        {
            "paper_id": "TAR01",
            "title": "Older Version (wrong direction)",
            "direction": "efficient_vision",
            "year": 2021,
            "keywords": ["old"],
            "abstract": "Duplicate.",
            "citation_ids": []
        },
        # Wrong direction (not in enum)
        {
            "paper_id": "NLP01",
            "title": "BERT: Pre-training of Deep Bidirectional Transformers",
            "direction": "nlp",
            "year": 2018,
            "keywords": ["nlp"],
            "abstract": "Language model.",
            "citation_ids": []
        },
        # Missing paper_id
        {
            "title": "No ID Paper",
            "direction": "tool_augmented_reasoning",
            "year": 2020,
            "keywords": ["missing"],
            "abstract": "No identifier.",
            "citation_ids": []
        }
    ]

    # Write papers.json
    with open("data/papers.json", "w") as f:
        json.dump({"papers": papers}, f, indent=2)

    # Additional noise files
    with open("data/notes.txt", "w") as f:
        f.write("Ignore this file.\n")

    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": []}, f)

if __name__ == "__main__":
    build_env()
