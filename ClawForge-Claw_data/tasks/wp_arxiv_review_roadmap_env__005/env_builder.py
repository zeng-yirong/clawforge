import os
import json
import shutil

def build_env():
    # 清理并重建工作区
    base = "."
    if os.path.exists(base):
        # 只清理我们创建的目录，避免误删其他文件
        for d in ["data", "ops"]:
            p = os.path.join(base, d)
            if os.path.exists(p):
                shutil.rmtree(p)
    os.makedirs("data/papers", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # ----- 构造 papers.json（含干扰项） -----
    papers = [
        # --- tool_augmented_reasoning 方向（目标）---
        {
            "paper_id": "TAR-2020-001",
            "title": "Toolformer: Teaching Language Models to Use Tools",
            "direction": "tool_augmented_reasoning",
            "year": 2020,
            "keywords": ["tool use", "language model", "augmentation"],
            "abstract": "We present Toolformer, a model that learns to use external tools via demonstrations.",
            "citation_ids": ["TAR-2021-002"]
        },
        {
            "paper_id": "TAR-2021-002",
            "title": "ART: Automatic Reasoning with Tool-Augmented Language Models",
            "direction": "tool_augmented_reasoning",
            "year": 2021,
            "keywords": ["reasoning", "tool", "chain-of-thought"],
            "abstract": "ART combines reasoning chains with external tool calls.",
            "citation_ids": ["TAR-2022-004"]
        },
        {
            "paper_id": "TAR-2022-004",
            "title": "WebGPT: Browser-assisted question answering",
            "direction": "tool_augmented_reasoning",
            "year": 2022,
            "keywords": ["web search", "qa", "tool"],
            "abstract": "WebGPT uses a browser to answer questions.",
            "citation_ids": ["TAR-2023-005"]
        },
        {
            "paper_id": "TAR-2023-005",
            "title": "ToolLLM: Facilitating Large Language Models to Master 16000+ Real-world APIs",
            "direction": "tool_augmented_reasoning",
            "year": 2023,
            "keywords": ["API", "tool learning", "llm"],
            "abstract": "A framework enabling LLMs to use thousands of APIs.",
            "citation_ids": []
        },
        # --- 2019年的旧论文（应被排除）---
        {
            "paper_id": "TAR-2019-000",
            "title": "Early Tool-Augmented Models",
            "direction": "tool_augmented_reasoning",
            "year": 2019,
            "keywords": ["tool", "early"],
            "abstract": "Early work on tool integration.",
            "citation_ids": []
        },
        # --- 另一个方向（干扰）---
        {
            "paper_id": "EV-2020-001",
            "title": "EfficientNet: Rethinking Model Scaling",
            "direction": "efficient_vision",
            "year": 2020,
            "keywords": ["efficient", "vision", "scaling"],
            "abstract": "A systematic study of model scaling.",
            "citation_ids": []
        },
        {
            "paper_id": "EV-2022-002",
            "title": "Vision Transformer",
            "direction": "efficient_vision",
            "year": 2022,
            "keywords": ["transformer", "vision"],
            "abstract": "ViT applies transformers directly to image patches.",
            "citation_ids": []
        },
        # --- 方向字段拼写错误（脏数据）---
        {
            "paper_id": "MAL-2021-003",
            "title": "Mislabeled Paper on Tool Use",
            "direction": "tool_augmented_reasonning",  # 故意拼错
            "year": 2021,
            "keywords": ["tool", "spelling"],
            "abstract": "This paper has a typo in direction.",
            "citation_ids": []
        },
        # --- 缺少 year 字段（应被忽略）---
        {
            "paper_id": "NOYEAR-001",
            "title": "Paper Without Year",
            "direction": "tool_augmented_reasoning",
            "keywords": ["missing"],
            "abstract": "No year field.",
            "citation_ids": []
        }
    ]
    with open("data/papers/papers.json", "w") as f:
        json.dump({"papers": papers}, f, indent=2)

    # ----- 构造 attachments.json（仅为增加真实性，不用于验证）-----
    attachments = [
        {
            "path": "attachments/toolformer_supp.pdf",
            "title": "Toolformer Supplementary",
            "kind": "pdf",
            "description": "Additional experiments and ablation studies."
        },
        {
            "path": "attachments/art_code.zip",
            "title": "ART Codebase",
            "kind": "zip",
            "description": "Source code for ART."
        }
    ]
    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

    # ----- 其他干扰文件（账户、联系人）-----
    accounts = [
        {"account_id": "a001", "display_name": "Alice", "department": "AI", "email": "alice@lab.com", "permissions": ["read"]},
        {"account_id": "a002", "display_name": "Bob", "department": "CS", "email": "bob@lab.com", "permissions": ["read", "write"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    contacts = [
        {"contact_id": "c001", "name": "Charlie", "role": "reviewer", "email": "charlie@conf.com"},
        {"contact_id": "c002", "name": "Dave", "role": "author", "email": "dave@univ.edu"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # 创建 ops 目录（空，等待 agent 填充）
    os.makedirs("ops", exist_ok=True)
