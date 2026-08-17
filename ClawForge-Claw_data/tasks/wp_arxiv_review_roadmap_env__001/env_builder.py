import os, json, random

random.seed(42)

def build_env():
    # ------------------------------------------------------------
    # 1. 创建目录结构
    # ------------------------------------------------------------
    os.makedirs("data/papers", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops/attachments", exist_ok=True)
    os.makedirs("raw_logs", exist_ok=True)        # 干扰目录
    os.makedirs("db_dumps", exist_ok=True)        # 干扰目录

    # ------------------------------------------------------------
    # 2. 目标论文 (tool_augmented_reasoning, 2019-2024)
    # ------------------------------------------------------------
    target_papers = [
        {
            "paper_id": "tr001",
            "title": "ToolChain: A Framework for Tool-Augmented Reasoning",
            "direction": "tool_augmented_reasoning",
            "year": 2019,
            "keywords": ["tool", "reasoning", "framework"],
            "abstract": "Introduces ToolChain, a modular pipeline that combines LLMs with external tool APIs for multi-step reasoning.",
            "citation_ids": []
        },
        {
            "paper_id": "tr002",
            "title": "Reasoning with Tools: Advances in Symbolic Integration",
            "direction": "tool_augmented_reasoning",
            "year": 2020,
            "keywords": ["tool use", "symbolic reasoning", "LLM"],
            "abstract": "Explores how large language models can leverage symbolic mathematics tools to improve reasoning accuracy.",
            "citation_ids": ["tr001"]
        },
        {
            "paper_id": "tr003",
            "title": "Interactive Tool-Augmented Agents for Task Planning",
            "direction": "tool_augmented_reasoning",
            "year": 2021,
            "keywords": ["agents", "task planning", "tool interaction"],
            "abstract": "Proposes an agent architecture that dynamically selects and invokes tools during hierarchical task decomposition.",
            "citation_ids": ["tr001", "tr002"]
        },
        {
            "paper_id": "tr004",
            "title": "Benchmarking Tool-Augmented Reasoning: A Comprehensive Study",
            "direction": "tool_augmented_reasoning",
            "year": 2022,
            "keywords": ["benchmark", "evaluation", "tool reasoning"],
            "abstract": "Presents a standardized suite of tasks and metrics for evaluating tool-augmented reasoning systems.",
            "citation_ids": ["tr001", "tr002", "tr003"]
        },
        {
            "paper_id": "tr005",
            "title": "Tool-Augmented LLMs for Code Generation and Debugging",
            "direction": "tool_augmented_reasoning",
            "year": 2023,
            "keywords": ["code generation", "debugging", "LLM"],
            "abstract": "Demonstrates how integrating a debugger tool and a code interpreter enhances LLM-based code generation and repair.",
            "citation_ids": ["tr003", "tr004"]
        },
        {
            "paper_id": "tr006",
            "title": "Adaptive Tool Selection for Open-Domain Question Answering",
            "direction": "tool_augmented_reasoning",
            "year": 2024,
            "keywords": ["question answering", "tool selection", "adaptation"],
            "abstract": "Develops a meta-learning approach that selects the best tool combination for each query in open-domain QA.",
            "citation_ids": ["tr004", "tr005"]
        }
    ]

    # ------------------------------------------------------------
    # 3. 干扰论文
    # ------------------------------------------------------------
    distractor_papers = [
        # (a) 其他方向
        {"paper_id": "ev101", "title": "Efficient Vision Transformers via Sparse Attention",
         "direction": "efficient_vision", "year": 2021,
         "keywords": ["vision", "transformer", "sparse"], "abstract": "...", "citation_ids": []},
        {"paper_id": "ev102", "title": "Lightweight CNN for Real-Time Object Detection",
         "direction": "efficient_vision", "year": 2022,
         "keywords": ["cnn", "object detection"], "abstract": "...", "citation_ids": []},
        {"paper_id": "ev103", "title": "Knowledge Distillation for Vision Models",
         "direction": "efficient_vision", "year": 2023,
         "keywords": ["distillation", "vision"], "abstract": "...", "citation_ids": []},
        {"paper_id": "ev104", "title": "Neural Architecture Search for Edge Devices",
         "direction": "efficient_vision", "year": 2024,
         "keywords": ["nas", "edge"], "abstract": "...", "citation_ids": []},
        # (b) 方向正确但年份越界
        {"paper_id": "tr007", "title": "Future Tool Reasoning (preprint)",
         "direction": "tool_augmented_reasoning", "year": 2025,
         "keywords": ["future"], "abstract": "A speculative piece on next-generation tool reasoning.", "citation_ids": []},
        # (c) 方向正确但年份太早
        {"paper_id": "tr008", "title": "Early Ideas on Tool Use",
         "direction": "tool_augmented_reasoning", "year": 2015,
         "keywords": ["historical"], "abstract": "Early exploration of tool use in AI.", "citation_ids": []},
        # (d) 方向字段缺失 (空字符串)
        {"paper_id": "tr009", "title": "Mysterious Paper",
         "direction": "", "year": 2022,
         "keywords": [], "abstract": "No direction assigned.", "citation_ids": []},
        # (e) 方向字段为 null (用 Python None 表示)
        {"paper_id": "tr010", "title": "Another Orphan",
         "direction": None, "year": 2023,
         "keywords": [], "abstract": "Direction missing.", "citation_ids": []}
    ]

    all_papers = target_papers + distractor_papers
    random.shuffle(all_papers)

    # 写入 papers.json
    with open("data/papers/papers.json", "w", encoding="utf-8") as f:
        json.dump({"papers": all_papers}, f, indent=2, ensure_ascii=False)

    # ------------------------------------------------------------
    # 4. 附件数据 (attachments.json) 以及对应的附件文件
    # ------------------------------------------------------------
    # 为前3篇目标论文创建附件 (tr001, tr002, tr003)
    attachments = [
        {
            "path": "ops/attachments/tr001_notes.md",
            "title": "ToolChain Notes",
            "kind": "markdown",
            "description": "TR001 introduces the ToolChain pipeline. Key insight: modular tool orchestration."
        },
        {
            "path": "ops/attachments/tr002_notes.md",
            "title": "Symbolic Integration Remarks",
            "kind": "markdown",
            "description": "TR002 shows that symbolic solvers boost LLM accuracy by 15% on algebra tasks."
        },
        {
            "path": "ops/attachments/tr003_notes.md",
            "title": "Agent Planning Appendix",
            "kind": "markdown",
            "description": "TR003's agent selects tools via a learned utility function."
        }
    ]

    with open("ops/attachments.json", "w", encoding="utf-8") as f:
        json.dump({"attachments": attachments}, f, indent=2, ensure_ascii=False)

    # 创建附件文件 (内容与 description 相同，方便 Agent 读取)
    for att in attachments:
        filepath = att["path"]
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(att["description"] + "\n")

    # ------------------------------------------------------------
    # 5. 其他干扰文件 (accounts, contacts) 增加真实性
    # ------------------------------------------------------------
    accounts = [
        {"account_id": "res-001", "display_name": "Alice Chen", "department": "AI", "email": "alice@lab.org", "permissions": ["read", "write"]},
        {"account_id": "res-002", "display_name": "Bob Liu", "department": "Vision", "email": "bob@lab.org", "permissions": ["read"]}
    ]
    with open("data/accounts.json", "w", encoding="utf-8") as f:
        json.dump({"accounts": accounts}, f, indent=2, ensure_ascii=False)

    contacts = [
        {"contact_id": "c001", "name": "Dr. Smith", "role": "advisor", "email": "smith@uni.edu"},
        {"contact_id": "c002", "name": "Dr. Jones", "role": "reviewer", "email": "jones@uni.edu"}
    ]
    with open("data/contacts.json", "w", encoding="utf-8") as f:
        json.dump({"contacts": contacts}, f, indent=2, ensure_ascii=False)

    # 填一些空文件到 raw_logs 和 db_dumps
    for i in range(3):
        with open(f"raw_logs/system_{i}.log", "w") as f:
            f.write("# dummy log\n")
    for i in range(2):
        with open(f"db_dumps/snapshot_{i}.sql", "w") as f:
            f.write("-- dummy sql\n")

if __name__ == "__main__":
    build_env()
