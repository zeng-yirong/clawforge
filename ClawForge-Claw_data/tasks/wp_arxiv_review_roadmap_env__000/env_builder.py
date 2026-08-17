import os
import json

def build_env():
    os.makedirs("data/papers", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)

    papers = [
        {
            "paper_id": "paper_001",
            "title": "EfficientNet: Rethinking Model Scaling",
            "direction": "efficient_vision",
            "year": 2019,
            "keywords": ["efficient", "scaling"],
            "abstract": "We systematically study model scaling and identify that carefully balancing network depth, width and resolution can lead to better performance. We propose a new scaling method that uniformly scales all dimensions using a simple yet effective composite coefficient. Our model, EfficientNet, achieves state-of-the-art accuracy on ImageNet while being much smaller and faster.",
            "citation_ids": ["paper_002", "paper_003"]
        },
        {
            "paper_id": "paper_002",
            "title": "MobileNets: Efficient Convolutional Neural Networks for Mobile Vision Applications",
            "direction": "efficient_vision",
            "year": 2017,
            "keywords": ["mobile", "efficient"],
            "abstract": "We present a class of efficient models called MobileNets for mobile and embedded vision applications. These models are based on a streamlined architecture that uses depthwise separable convolutions to build lightweight deep neural networks. We introduce two simple global hyper-parameters that efficiently trade off between latency and accuracy.",
            "citation_ids": []
        },
        {
            "paper_id": "paper_003",
            "title": "EfficientDet: Scalable and Efficient Object Detection",
            "direction": "efficient_vision",
            "year": 2020,
            "keywords": ["detection", "efficient"],
            "abstract": "We propose EfficientDet, a family of object detectors that achieve state-of-the-art accuracy while being more efficient than previous detectors. We introduce a weighted bi-directional feature network (BiFPN) and a compound scaling method.",
            "citation_ids": ["paper_001"]
        },
        # distractors
        {
            "paper_id": "paper_004",
            "title": "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models",
            "direction": "tool_augmented_reasoning",
            "year": 2022,
            "keywords": ["reasoning", "prompting"],
            "abstract": "We explore how generating a chain of thought—a series of intermediate reasoning steps—significantly improves the ability of large language models to perform complex reasoning.",
            "citation_ids": []
        },
        {
            "paper_id": "paper_005",
            "title": "ReAct: Synergizing Reasoning and Acting in Language Models",
            "direction": "tool_augmented_reasoning",
            "year": 2022,
            "keywords": ["reasoning", "acting"],
            "abstract": "We present ReAct, a paradigm that combines reasoning and acting in language models to solve diverse tasks.",
            "citation_ids": ["paper_004"]
        },
        {
            "paper_id": "paper_006",
            "title": "Some Paper with Hyphen Direction",
            "direction": "efficient-vision",
            "year": 2021,
            "keywords": ["hyphen"],
            "abstract": "This paper has a direction with a hyphen instead of underscore."
        },
        {
            "paper_id": "paper_007",
            "title": "Empty Direction Paper",
            "direction": "",
            "year": 2020,
            "keywords": [],
            "abstract": "This paper has an empty direction field."
        },
        {
            "paper_id": "paper_008",
            "title": "Leading Space Direction",
            "direction": " efficient_vision",
            "year": 2018,
            "keywords": [],
            "abstract": "This paper has a leading space in direction."
        }
    ]

    with open("data/papers/papers.json", "w") as f:
        json.dump({"papers": papers}, f, indent=2)

    # minimal empty attachment file (not used)
    os.makedirs("data", exist_ok=True)
    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": []}, f)

if __name__ == "__main__":
    build_env()
