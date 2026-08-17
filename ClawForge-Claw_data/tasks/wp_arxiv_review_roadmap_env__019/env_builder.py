import os
import json

def build_env():
    # 创建目录
    os.makedirs("papers", exist_ok=True)
    os.makedirs("attachments", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)

    # 目标论文 (tool_augmented_reasoning)
    target_papers = [
        {
            "paper_id": "paper_001",
            "title": "Reasoning via Tool Use",
            "direction": "tool_augmented_reasoning",
            "year": 2020,
            "keywords": ["reasoning", "tools"],
            "abstract": "This paper explores using external tools to augment reasoning.",
            "citation_ids": []
        },
        {
            "paper_id": "paper_002",
            "title": "Chain-of-Thought with Tools",
            "direction": "tool_augmented_reasoning",
            "year": 2021,
            "keywords": ["chain-of-thought", "tool"],
            "abstract": "Extending CoT with tool invocations.",
            "citation_ids": ["paper_001"]
        },
        {
            "paper_id": "paper_003",
            "title": "Tool-Former: Learning to Use Tools",
            "direction": "tool_augmented_reasoning",
            "year": 2022,
            "keywords": ["tool learning", "transformer"],
            "abstract": "A transformer model that learns to use tools via reinforcement learning.",
            "citation_ids": ["paper_001", "paper_002"]
        },
        {
            "paper_id": "paper_004",
            "title": "Interactive Tool Reasoning with Human Feedback",
            "direction": "tool_augmented_reasoning",
            "year": 2023,
            "keywords": ["interactive", "human feedback"],
            "abstract": "Incorporating human feedback for tool selection.",
            "citation_ids": ["paper_003"]
        },
        {
            "paper_id": "paper_005",
            "title": "Scaling Tool-Augmented Reasoning",
            "direction": "tool_augmented_reasoning",
            "year": 2024,
            "keywords": ["scaling", "language models"],
            "abstract": "How to scale tool use for large language models.",
            "citation_ids": ["paper_004"]
        }
    ]

    # 干扰论文 (efficient_vision 方向)
    distractor_papers = [
        {
            "paper_id": "paper_006",
            "title": "Efficient Vision Transformers",
            "direction": "efficient_vision",
            "year": 2021,
            "keywords": ["vision", "efficiency"],
            "abstract": "Making ViTs faster.",
            "citation_ids": []
        },
        {
            "paper_id": "paper_007",
            "title": "Lightweight Object Detection",
            "direction": "efficient_vision",
            "year": 2022,
            "keywords": ["detection", "lightweight"],
            "abstract": "Small model for object detection.",
            "citation_ids": []
        },
        {
            "paper_id": "paper_008",
            "title": "Image Segmentation with Limited Data",
            "direction": "efficient_vision",
            "year": 2023,
            "keywords": ["segmentation", "few-shot"],
            "abstract": "Segmentation with few labels.",
            "citation_ids": []
        }
    ]

    # 拼写错误的目标论文 (诱饵)
    misspelled_paper = {
        "paper_id": "paper_009",
        "title": "Tool Reasoning for Beginners",
        "direction": "tool_augmented_reasonning",  # 故意拼错
        "year": 2020,
        "keywords": ["beginner", "tools"],
        "abstract": "A tutorial on tool reasoning.",
        "citation_ids": []
    }

    all_papers = target_papers + distractor_papers + [misspelled_paper]

    # 写入 papers.json
    with open("papers/papers.json", "w") as f:
        json.dump({"papers": all_papers}, f, indent=2)

    # 创建附件列表
    attachments = []
    for p in target_papers:
        attach_path = f"attachments/paper_{p['paper_id'].split('_')[1]}_summary.txt"
        attachments.append({
            "paper_id": p["paper_id"],
            "path": attach_path,
            "title": f"Summary of {p['title']}",
            "kind": "text",
            "description": "Additional notes."
        })
        # 写入附件内容
        with open(attach_path, "w") as f:
            f.write(f"Key Insight: {p['title']} introduces important ideas about tool use.\n"
                    f"Authors: Some authors.\n")
    # 添加一个干扰附件 (对应 vision 论文)
    attachments.append({
        "paper_id": "paper_006",
        "path": "attachments/paper_006_vision_summary.txt",
        "title": "Vision summary",
        "kind": "text",
        "description": "Vision related."
    })
    # 写入 attachments.json
    with open("attachments/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

    # 创建干扰附件文件 (实际存在)
    with open("attachments/paper_006_vision_summary.txt", "w") as f:
        f.write("Vision paper note.")

    # 额外干扰文件
    with open("cache.db", "w") as f:
        f.write("some cache")

if __name__ == "__main__":
    build_env()
