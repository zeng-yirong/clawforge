import os
import json

def build_env():
    # Create directories
    os.makedirs("data/papers", exist_ok=True)
    os.makedirs("data/attachments", exist_ok=True)
    os.makedirs("data/cache", exist_ok=True)

    # Define papers
    papers = [
        {
            "paper_id": "ev01",
            "title": "EfficientNet: Rethinking Model Scaling for Convolutional Neural Networks",
            "direction": "efficient_vision",
            "year": 2020,
            "keywords": ["scaling", "CNN", "efficient"],
            "abstract": "We systematically study model scaling...",
            "citation_ids": ["cit001", "cit002"]
        },
        {
            "paper_id": "ev02",
            "title": "EfficientDet: Scalable and Efficient Object Detection",
            "direction": "efficient_vision",
            "year": 2020,
            "keywords": ["object detection", "scaling", "efficient"],
            "abstract": "We propose EfficientDet...",
            "citation_ids": ["cit003"]
        },
        {
            "paper_id": "ev03",
            "title": "MobileNetV3: Searching for MobileNetV3",
            "direction": "efficient_vision",
            "year": 2021,
            "keywords": ["mobile", "NAS", "efficient"],
            "abstract": "MobileNetV3 is tuned via NAS...",
            "citation_ids": ["cit004"]
        },
        {
            "paper_id": "ev04",
            "title": "ShuffleNet V2: Practical Guidelines for Efficient CNN Architecture Design",
            "direction": "efficient_vision",
            "year": 2022,
            "keywords": ["shuffle", "guidelines", "efficient"],
            "abstract": "We propose ShuffleNet V2...",
            "citation_ids": ["cit005"]
        },
        {
            "paper_id": "ev05",
            "title": "EfficientFormer: Vision Transformers at MobileNet Speed",
            "direction": "efficient_vision",
            "year": 2023,
            "keywords": ["transformer", "efficient", "mobile"],
            "abstract": "EfficientFormer achieves...",
            "citation_ids": ["cit006"]
        },
        # Interference: tool-augmented reasoning papers
        {
            "paper_id": "ta01",
            "title": "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models",
            "direction": "tool_augmented_reasoning",
            "year": 2022,
            "keywords": ["reasoning", "prompting", "LLM"],
            "abstract": "Chain-of-thought prompting...",
            "citation_ids": ["cit007"]
        },
        {
            "paper_id": "ta02",
            "title": "Toolformer: Language Models Can Teach Themselves to Use Tools",
            "direction": "tool_augmented_reasoning",
            "year": 2023,
            "keywords": ["tool", "LLM", "self-supervised"],
            "abstract": "Toolformer enables...",
            "citation_ids": ["cit008"]
        },
        {
            "paper_id": "ta03",
            "title": "ReAct: Synergizing Reasoning and Acting in Language Models",
            "direction": "tool_augmented_reasoning",
            "year": 2022,
            "keywords": ["reasoning", "acting", "LLM"],
            "abstract": "ReAct combines reasoning and acting...",
            "citation_ids": ["cit009"]
        },
        # Dirty data: typo in direction
        {
            "paper_id": "ev06",
            "title": "EfficientNetV2: Smaller Models and Faster Training",
            "direction": "efficient_visio",
            "year": 2021,
            "keywords": ["efficient", "scaling"],
            "abstract": "EfficientNetV2 improves...",
            "citation_ids": ["cit010"]
        }
    ]

    # Write papers.json
    with open("data/papers/papers.json", "w") as f:
        json.dump(papers, f, indent=2)

    # Create dummy attachments (interference)
    attachments = [
        {"path": "attachments/fig1.png", "title": "Figure 1", "kind": "image", "description": "Architecture diagram"},
        {"path": "attachments/paper_ev01.pdf", "title": "EfficientNet paper", "kind": "pdf", "description": "Full text"}
    ]
    with open("data/attachments/attachments.json", "w") as f:
        json.dump(attachments, f, indent=2)

    # Create dummy cache entries
    cache = {"last_query": "efficient_vision", "results": ["ev01", "ev02", "ev03"]}
    with open("data/cache/search_cache.json", "w") as f:
        json.dump(cache, f, indent=2)

if __name__ == "__main__":
    build_env()
