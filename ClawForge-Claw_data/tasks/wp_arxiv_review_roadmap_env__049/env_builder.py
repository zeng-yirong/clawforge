import os
import json
import random
import time

def build_env():
    # 确保数据目录存在
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/attachments", exist_ok=True)

    # 构建论文列表
    papers = [
        # 目标方向：tool_augmented_reasoning
        {
            "paper_id": "TAR-001",
            "title": "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models",
            "direction": "tool_augmented_reasoning",
            "year": 2021,
            "keywords": ["chain-of-thought", "reasoning", "LLM"],
            "abstract": "We explore how chain-of-thought prompting can elicit step-by-step reasoning...",
            "citation_ids": ["LM-001", "LM-002"]
        },
        {
            "paper_id": "TAR-002",
            "title": "Toolformer: Language Models Can Teach Themselves to Use Tools",
            "direction": "tool_augmented_reasoning",
            "year": 2022,
            "keywords": ["tool use", "self-supervised", "API"],
            "abstract": "Toolformer enables LLMs to autonomously decide which tools to call...",
            "citation_ids": ["TAR-001", "API-01"]
        },
        {
            "paper_id": "TAR-003",
            "title": "ART: Automatic multi-step reasoning and tool use",
            "direction": "tool_augmented_reasoning",
            "year": 2023,
            "keywords": ["multi-step", "reasoning", "tool orchestration"],
            "abstract": "ART proposes a framework for automatic multi-step reasoning with tool integration...",
            "citation_ids": ["TAR-002", "RE-003"]
        },
        # 干扰：efficient_vision 方向
        {
            "paper_id": "VIS-001",
            "title": "An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale",
            "direction": "efficient_vision",
            "year": 2020,
            "keywords": ["ViT", "transformer", "image classification"],
            "abstract": "We apply a pure transformer directly to sequences of image patches...",
            "citation_ids": []
        },
        {
            "paper_id": "VIS-002",
            "title": "EfficientNet: Rethinking Model Scaling for Convolutional Neural Networks",
            "direction": "efficient_vision",
            "year": 2019,
            "keywords": ["compound scaling", "depth", "width", "resolution"],
            "abstract": "We systematically study model scaling and propose a compound scaling method...",
            "citation_ids": ["VIS-001"]
        },
        {
            "paper_id": "VIS-003",
            "title": "ResNeSt: Split-Attention Networks",
            "direction": "efficient_vision",
            "year": 2022,
            "keywords": ["split-attention", "backbone"],
            "abstract": "ResNeSt introduces a modular split-attention block that enables cross-channel interactions...",
            "citation_ids": ["VIS-002", "VIS-001"]
        },
        # 干扰：direction 缺失
        {
            "paper_id": "ERR-001",
            "title": "A Study on Random Noise in Neural Networks",
            "direction": "",
            "year": 2021,
            "keywords": ["noise", "regularization"],
            "abstract": "This paper investigates the effect of random noise injection...",
            "citation_ids": []
        },
        # 干扰：年份异常（未来）
        {
            "paper_id": "TAR-099",
            "title": "Hypothetical Future Tool-Augmented System",
            "direction": "tool_augmented_reasoning",
            "year": 2030,
            "keywords": ["future", "speculative"],
            "abstract": "A purely speculative paper about future tool usage...",
            "citation_ids": []
        },
        # 干扰：重复 paper_id 但内容不同（脏数据）- 实际上不应该重复，但作为干扰
        # 我们故意写一个 id 与 TAR-001 相同的记录，但方向不同，这会造成歧义，agent 需要处理重复
        # 注意：实际中应该唯一，但这里模拟脏数据，让 agent 决定如何处理
        {
            "paper_id": "TAR-001",
            "title": "Duplicate entry: Chain-of-Thought (wrong)",
            "direction": "efficient_vision",
            "year": 2020,
            "keywords": ["fake"],
            "abstract": "This is a duplicate record with conflicting direction.",
            "citation_ids": []
        }
    ]

    # 写入 papers.json
    with open("data/papers.json", "w") as f:
        json.dump({"papers": papers}, f, indent=2)

    # 构建附件列表（干扰/辅助）
    attachments = [
        {
            "path": "attachments/TAR-002_supplement.pdf",
            "title": "Toolformer Supplementary Material",
            "kind": "pdf",
            "description": "Additional experiments and prompts"
        },
        {
            "path": "attachments/VIS-003_code.zip",
            "title": "ResNeSt Source Code",
            "kind": "zip",
            "description": "PyTorch implementation"
        },
        {
            "path": "attachments/old_review_draft.md",
            "title": "Old Review Draft (outdated)",
            "kind": "markdown",
            "description": "An earlier attempt at this review, may contain errors"
        }
    ]
    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

if __name__ == "__main__":
    build_env()
