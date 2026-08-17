import os
import json

def build_env():
    # 创建目录
    os.makedirs("papers", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/attachments", exist_ok=True)

    # --- 论文数据 ---
    papers = [
        {
            "paper_id": "ev001",
            "title": "EfficientNet: Rethinking Model Scaling for Convolutional Neural Networks",
            "direction": "efficient_vision",
            "year": 2019,
            "keywords": ["scaling", "efficiency", "CNN"],
            "abstract": "",
            "citation_ids": []
        },
        {
            "paper_id": "ev002",
            "title": "MobileNetV3: Searching for Efficient Architectures",
            "direction": "efficient_vision",
            "year": 2020,
            "keywords": ["mobile", "NAS", "efficiency"],
            "abstract": "",
            "citation_ids": ["ev001"]
        },
        {
            "paper_id": "ev003",
            "title": "EfficientDet: Scalable and Efficient Object Detection",
            "direction": "efficient_vision",
            "year": 2020,
            "keywords": ["detection", "scaling"],
            "abstract": "",
            "citation_ids": ["ev001"]
        },
        {
            "paper_id": "ev004",
            "title": "RepVGG: Making VGG-style ConvNets Great Again",
            "direction": "efficient_vision",
            "year": 2021,
            "keywords": ["VGG", "reparameterization"],
            "abstract": "",
            "citation_ids": []
        },
        {
            "paper_id": "ev005",
            "title": "ConvNeXt: A Modern ConvNet for the 2020s",
            "direction": "efficient_vision",
            "year": 2022,
            "keywords": ["modern", "CNN", "transformer"],
            "abstract": "",
            "citation_ids": ["ev001","ev004"]
        },
        # 干扰方向论文
        {
            "paper_id": "ta001",
            "title": "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models",
            "direction": "tool_augmented_reasoning",
            "year": 2022,
            "keywords": ["reasoning", "prompting"],
            "abstract": "",
            "citation_ids": []
        },
        {
            "paper_id": "ta002",
            "title": "ReAct: Synergizing Reasoning and Acting in Language Models",
            "direction": "tool_augmented_reasoning",
            "year": 2023,
            "keywords": ["reasoning", "acting"],
            "abstract": "",
            "citation_ids": ["ta001"]
        },
        {
            "paper_id": "ta003",
            "title": "Toolformer: Language Models Can Teach Themselves to Use Tools",
            "direction": "tool_augmented_reasoning",
            "year": 2023,
            "keywords": ["tools", "self-supervised"],
            "abstract": "",
            "citation_ids": ["ta001","ta002"]
        }
    ]

    with open("papers/papers.json", "w") as f:
        json.dump({"papers": papers}, f, indent=2)

    # --- 附件数据（映射 + 具体内容） ---
    attachments_list = [
        {
            "paper_id": "ev001",
            "path": "data/attachments/ev001_abstract.txt",
            "title": "EfficientNet Abstract Extended",
            "kind": "abstract",
            "description": "Extended abstract for EfficientNet."
        },
        {
            "paper_id": "ev002",
            "path": "data/attachments/ev002_abstract.txt",
            "title": "MobileNetV3 Abstract Extended",
            "kind": "abstract",
            "description": "Extended abstract for MobileNetV3."
        },
        {
            "paper_id": "ev003",
            "path": "data/attachments/ev003_abstract.txt",
            "title": "EfficientDet Abstract Extended",
            "kind": "abstract",
            "description": "Extended abstract for EfficientDet."
        },
        {
            "paper_id": "ev004",
            "path": "data/attachments/ev004_abstract.txt",
            "title": "RepVGG Abstract Extended",
            "kind": "abstract",
            "description": "Extended abstract for RepVGG."
        },
        {
            "paper_id": "ev005",
            "path": "data/attachments/ev005_abstract.txt",
            "title": "ConvNeXt Abstract Extended",
            "kind": "abstract",
            "description": "Extended abstract for ConvNeXt."
        },
        # 干扰附件（对应tool_augmented_reasoning方向）
        {
            "paper_id": "ta001",
            "path": "data/attachments/ta001_abstract.txt",
            "title": "CoT Abstract",
            "kind": "abstract",
            "description": "Chain-of-Thought abstract."
        },
        {
            "paper_id": "ta002",
            "path": "data/attachments/ta002_abstract.txt",
            "title": "ReAct Abstract",
            "kind": "abstract",
            "description": "ReAct abstract."
        },
        {
            "paper_id": "ta003",
            "path": "data/attachments/ta003_abstract.txt",
            "title": "Toolformer Abstract",
            "kind": "abstract",
            "description": "Toolformer abstract."
        }
    ]

    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": attachments_list}, f, indent=2)

    # --- 创建附件文件内容（真实摘要片断） ---
    abstracts = {
        "ev001": (
            "EfficientNet systematically studies model scaling and identifies that carefully balancing "
            "network depth, width, and resolution can lead to better performance. The resulting EfficientNet "
            "family achieves state-of-the-art accuracy on ImageNet with an order of magnitude fewer parameters."
        ),
        "ev002": (
            "MobileNetV3 uses a combination of hardware-aware network architecture search and novel building "
            "blocks such as squeeze-and-excitation and hard-swish activation to achieve high accuracy on mobile "
            "devices while being computationally efficient."
        ),
        "ev003": (
            "EfficientDet proposes a weighted bi-directional feature pyramid network (BiFPN) and a compound "
            "scaling method that jointly scales resolution, depth, and width for object detectors. It achieves "
            "better accuracy and efficiency than previous detectors across a wide range of resource constraints."
        ),
        "ev004": (
            "RepVGG makes VGG-style convolutional networks great again by using a simple reparameterization "
            "technique that decouples the training-time multi-branch topology from the inference-time plain "
            "architecture. The resulting networks match or exceed the performance of state-of-the-art models."
        ),
        "ev005": (
            "ConvNeXt modernizes the standard ConvNet by incorporating design ideas from vision transformers, "
            "such as larger kernel sizes, layer normalization, and GELU activations. The resulting architecture "
            "achieves competitive performance with vision transformers on ImageNet and downstream tasks."
        ),
        # 干扰方向摘要（agent不应使用）
        "ta001": "Chain-of-Thought prompting enables language models to perform multi-step reasoning by generating intermediate steps.",
        "ta002": "ReAct interleaves reasoning traces and task-specific actions to enhance both reasoning and acting capabilities.",
        "ta003": "Toolformer learns to use external tools via self-supervised learning, calling APIs when beneficial."
    }

    for pid, text in abstracts.items():
        file_path = f"data/attachments/{pid}_abstract.txt"
        with open(file_path, "w") as f:
            f.write(text)

    # --- 额外的干扰文件（contacts.json, README等） ---
    contacts = [
        {"contact_id": "c001", "name": "Alice", "role": "researcher", "email": "alice@example.com"},
        {"contact_id": "c002", "name": "Bob", "role": "reviewer", "email": "bob@example.com"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # 创建一些无关txt文件增加干扰
    with open("data/README.txt", "w") as f:
        f.write("This directory contains supplementary data.\n")
    with open("data/temp_note.txt", "w") as f:
        f.write("Ignore this file.\n")

if __name__ == "__main__":
    build_env()
