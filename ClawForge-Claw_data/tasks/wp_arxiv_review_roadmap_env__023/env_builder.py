import os
import json

def build_env():
    # 创建 data 子目录
    os.makedirs("data/papers", exist_ok=True)
    os.makedirs("data/attachments", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    # 正确的主数据 papers.json
    papers = [
        {
            "paper_id": "paper_001",
            "title": "EfficientNet: Rethinking Model Scaling",
            "direction": "efficient_vision",
            "year": 2019,
            "keywords": ["scaling", "efficiency", "cnn"],
            "abstract": "We systematically study model scaling...",
            "citation_ids": ["paper_002"]
        },
        {
            "paper_id": "paper_002",
            "title": "MobileNets: Efficient Convolutional Neural Networks",
            "direction": "efficient_vision",
            "year": 2020,
            "keywords": ["mobile", "depthwise", "efficiency"],
            "abstract": "MobileNets are based on depthwise separable convolutions...",
            "citation_ids": ["paper_001"]
        },
        {
            "paper_id": "paper_003",
            "title": "GhostNet: More Features from Cheap Operations",
            "direction": "efficient_vision",
            "year": 2021,
            "keywords": ["ghost", "cheap", "feature"],
            "abstract": "GhostNet uses cheap operations to generate more feature maps...",
            "citation_ids": []
        },
        {
            "paper_id": "paper_004",
            "title": "ShuffleNet: An Extremely Efficient CNN",
            "direction": "efficient_vision",
            "year": 2022,
            "keywords": ["shuffle", "group conv", "efficiency"],
            "abstract": "ShuffleNet uses pointwise group convolution and channel shuffle...",
            "citation_ids": ["paper_003"]
        },
        {
            "paper_id": "paper_005",
            "title": "EfficientFormer: Mobile Vision Transformer",
            "direction": "efficient_vision",
            "year": 2023,
            "keywords": ["transformer", "mobile", "efficiency"],
            "abstract": "EfficientFormer designs a pure transformer that can run on mobile devices...",
            "citation_ids": ["paper_001", "paper_002"]
        },
        # 干扰方向：tool_augmented_reasoning
        {
            "paper_id": "paper_006",
            "title": "Toolformer: Teaching Language Models to Use Tools",
            "direction": "tool_augmented_reasoning",
            "year": 2022,
            "keywords": ["tool", "lm", "augmented"],
            "abstract": "We introduce Toolformer...",
            "citation_ids": []
        },
        {
            "paper_id": "paper_007",
            "title": "Gorilla: Large Language Model Connected with APIs",
            "direction": "tool_augmented_reasoning",
            "year": 2023,
            "keywords": ["api", "llm", "tool"],
            "abstract": "Gorilla enables LLMs to invoke APIs...",
            "citation_ids": ["paper_006"]
        },
        {
            "paper_id": "paper_008",
            "title": "ReAct: Synergizing Reasoning and Acting",
            "direction": "tool_augmented_reasoning",
            "year": 2021,
            "keywords": ["reasoning", "acting", "synergy"],
            "abstract": "ReAct interleaves reasoning traces and action steps...",
            "citation_ids": []
        },
        {
            "paper_id": "paper_009",
            "title": "WebGPT: Browser-Assisted Question-Answering",
            "direction": "tool_augmented_reasoning",
            "year": 2022,
            "keywords": ["web", "browser", "qa"],
            "abstract": "WebGPT fine-tunes GPT to browse the web...",
            "citation_ids": ["paper_007"]
        },
        {
            "paper_id": "paper_010",
            "title": "ART: Automatic multi-step reasoning and tool use",
            "direction": "tool_augmented_reasoning",
            "year": 2023,
            "keywords": ["automatic", "multi-step", "tool"],
            "abstract": "ART allows LLMs to decompose tasks...",
            "citation_ids": ["paper_006", "paper_008"]
        }
    ]

    with open("data/papers/papers.json", "w") as f:
        json.dump({"papers": papers}, f, indent=2)

    # 干扰：旧备份 papers_old.json，包含错误方向或过时论文
    old_papers = [
        {
            "paper_id": "paper_001",
            "title": "EfficientNet (old)",
            "direction": "tool_augmented_reasoning",  # 错误方向
            "year": 2018,
            "keywords": ["old"],
            "abstract": "Old version",
            "citation_ids": []
        },
        {
            "paper_id": "paper_011",
            "title": "RepVGG: Making VGG-style ConvNets Great Again",
            "direction": "efficient_vision",
            "year": 2021,
            "keywords": ["vgg", "reparameterization"],
            "abstract": "RepVGG uses structural reparameterization...",
            "citation_ids": []
        }
    ]
    with open("data/papers/papers_old.json", "w") as f:
        json.dump({"papers": old_papers}, f, indent=2)

    # 干扰：无关 accounts.json
    accounts = [
        {"account_id": "acc_1", "display_name": "Alice", "department": "CS", "email": "alice@uni.edu", "permissions": ["read"]},
        {"account_id": "acc_2", "display_name": "Bob", "department": "Math", "email": "bob@uni.edu", "permissions": ["write"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # 干扰：attachments.json（描述论文的附件，但agent不需要）
    attachments = [
        {"path": "attachments/efficientnet_supp.pdf", "title": "EfficientNet Supplementary", "kind": "pdf", "description": "Additional experiments"},
        {"path": "attachments/ghostnet_code.zip", "title": "GhostNet Code", "kind": "zip", "description": "Source code"}
    ]
    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

if __name__ == "__main__":
    build_env()
