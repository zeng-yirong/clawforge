import os
import json
import shutil

def build_env():
    """构建包含论文快照和干扰数据的初始工作区"""
    # 如果已有旧数据则清理
    for d in ['db_dumps']:
        if os.path.exists(d):
            shutil.rmtree(d)
    os.makedirs('db_dumps', exist_ok=True)

    # 论文数据 (按照 schema)
    papers = []
    # 有效论文 (Tool-Augmented Reasoning, 无重复, 合理年份)
    valid_tool = [
        {
            "paper_id": "paper_001",
            "title": "Learning to Reason with Tools",
            "direction": "tool_augmented_reasoning",
            "year": 2020,
            "keywords": ["tool use", "reasoning", "LLM"],
            "abstract": "We propose a framework that augments language models with external tools for multi-step reasoning.",
            "citation_ids": ["paper_003", "paper_005"]
        },
        {
            "paper_id": "paper_003",
            "title": "Toolformer: Language Models Can Teach Themselves to Use Tools",
            "direction": "tool_augmented_reasoning",
            "year": 2022,
            "keywords": ["tool learning", "self-supervised"],
            "abstract": "Toolformer shows that language models can learn to call APIs and tools through self-supervised fine-tuning.",
            "citation_ids": ["paper_001"]
        },
        {
            "paper_id": "paper_005",
            "title": "Augmented Language Models: A Survey",
            "direction": "tool_augmented_reasoning",
            "year": 2023,
            "keywords": ["survey", "tool augmentation"],
            "abstract": "We survey the emerging field of augmenting language models with external knowledge and tools.",
            "citation_ids": ["paper_001", "paper_003"]
        },
        {
            "paper_id": "paper_007",
            "title": "Reasoning with Retrieval and Tools",
            "direction": "tool_augmented_reasoning",
            "year": 2024,
            "keywords": ["retrieval-augmented", "tool calling"],
            "abstract": "Combining retrieval-augmented generation with tool-use enables more robust reasoning in complex domains.",
            "citation_ids": ["paper_005"]
        },
        {
            "paper_id": "paper_009",
            "title": "Multi-step Tool Reasoning via Program Synthesis",
            "direction": "tool_augmented_reasoning",
            "year": 2024,
            "keywords": ["program synthesis", "multi-step"],
            "abstract": "We use program synthesis to compose multiple tool calls for complex question answering.",
            "citation_ids": ["paper_007"]
        }
    ]
    papers.extend(valid_tool)

    # 脏数据：重复的 paper_id (重复记录)
    duplicate = {
        "paper_id": "paper_001",
        "title": "Learning to Reason with Tools (v2)",
        "direction": "tool_augmented_reasoning",
        "year": 2020,
        "keywords": ["tool use"],
        "abstract": "A duplicate version with different title.",
        "citation_ids": []
    }
    papers.append(duplicate)

    # 脏数据：未来年份 (2026)
    future_paper = {
        "paper_id": "paper_011",
        "title": "Future of Tool Augmentation",
        "direction": "tool_augmented_reasoning",
        "year": 2026,
        "keywords": ["future", "speculative"],
        "abstract": "This paper discusses hypothetical tool augmentation beyond 2025.",
        "citation_ids": []
    }
    papers.append(future_paper)

    # 脏数据：缺失 abstract 字段
    missing_abstract = {
        "paper_id": "paper_013",
        "title": "Broken Record",
        "direction": "tool_augmented_reasoning",
        "year": 2021,
        "keywords": ["incomplete"],
        # abstract omitted on purpose
    }
    papers.append(missing_abstract)

    # 干扰方向：Efficient Vision 的论文 (不需要)
    vision_papers = [
        {
            "paper_id": "paper_002",
            "title": "Efficient Vision Transformers",
            "direction": "efficient_vision",
            "year": 2021,
            "keywords": ["vision", "transformer", "efficiency"],
            "abstract": "We propose a lightweight vision transformer for mobile devices.",
            "citation_ids": []
        },
        {
            "paper_id": "paper_004",
            "title": "Fast Convolutional Networks",
            "direction": "efficient_vision",
            "year": 2022,
            "keywords": ["cnn", "speed"],
            "abstract": "Optimizing convolutional networks for real-time inference.",
            "citation_ids": []
        },
        {
            "paper_id": "paper_006",
            "title": "Knowledge Distillation for Vision",
            "direction": "efficient_vision",
            "year": 2023,
            "keywords": ["distillation", "compression"],
            "abstract": "Distilling large vision models into small ones for edge deployment.",
            "citation_ids": []
        }
    ]
    papers.extend(vision_papers)

    # 写入 papers.json
    with open('db_dumps/papers.json', 'w') as f:
        json.dump({"papers": papers}, f, indent=2)

    # 创建空的附件文件作为干扰 (agent 不需要读取)
    os.makedirs('db_dumps/attachments', exist_ok=True)
    attachments_data = {
        "attachments": [
            {"path": "attachments/paper_001.pdf", "title": "Tool Reasoning Paper", "kind": "pdf", "description": "Full text of paper_001"},
            {"path": "attachments/paper_003.pdf", "title": "Toolformer", "kind": "pdf", "description": "Full text of paper_003"},
        ]
    }
    with open('db_dumps/attachments.json', 'w') as f:
        json.dump(attachments_data, f, indent=2)

    # 干扰日志文件
    os.makedirs('logs', exist_ok=True)
    with open('logs/system.log', 'w') as f:
        f.write("2025-02-10 03:00:12 INFO Starting database dump...\n")
        f.write("2025-02-10 03:00:15 ERROR timeout.\n")

    print("Environment built successfully.")

if __name__ == '__main__':
    build_env()
