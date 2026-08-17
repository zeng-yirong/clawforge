import os
import json
import yaml

def build_env():
    # 创建目录结构
    os.makedirs("docs", exist_ok=True)
    os.makedirs("scenarios", exist_ok=True)
    os.makedirs("knowledge_base", exist_ok=True)

    # 项目文档 (docs/)
    projects = [
        {"project_id": "react-hooks", "title": "React Hooks Performance", "path": "docs/react-hooks.md"},
        {"project_id": "rust-cli", "title": "Rust CLI Argument Parsing", "path": "docs/rust-cli.md"},
        {"project_id": "pytorch-inference", "title": "PyTorch ONNX Inference", "path": "docs/pytorch-inference.md"},
        {"project_id": "pandas-groupby", "title": "Pandas GroupBy Aggregation", "path": "docs/pandas-groupby.md"},
        {"project_id": "flask-caching", "title": "Flask Cache Performance", "path": "docs/flask-caching.md"},
    ]
    os.makedirs("docs", exist_ok=True)
    for p in projects:
        with open(p["path"], "w") as f:
            f.write(f"# {p['title']}\n\nReproduction steps...\n")

    # 场景记录 (scenarios/) - 包含失败、成功、干扰项
    scenarios = [
        # 失败场景（目标）
        {"scenario_id": "sc-001", "project_id": "react-hooks", "status": "FAILED", "error": "Memory leak in useEffect cleanup", "doc_path": "docs/react-hooks.md"},
        {"scenario_id": "sc-004", "project_id": "pytorch-inference", "status": "ERROR", "error": "Tensor shape mismatch at layer 3", "doc_path": "docs/pytorch-inference.md"},
        {"scenario_id": "sc-007", "project_id": "flask-caching", "status": "FAILED", "error": "Cache invalidation timeout after 30s", "doc_path": "docs/flask-caching.md"},
        # 成功场景（干扰）
        {"scenario_id": "sc-002", "project_id": "rust-cli", "status": "SUCCESS", "error": None, "doc_path": "docs/rust-cli.md"},
        {"scenario_id": "sc-005", "project_id": "pandas-groupby", "status": "SUCCESS", "error": None, "doc_path": "docs/pandas-groupby.md"},
        # 过期的旧副本（干扰）
        {"scenario_id": "sc-001_old", "project_id": "react-hooks", "status": "FAILED", "error": "deprecated approach", "doc_path": "docs/react-hooks.md"},
        {"scenario_id": "sc-004_old", "project_id": "pytorch-inference", "status": "ERROR", "error": "old error", "doc_path": "docs/pytorch-inference.md"},
        # 缺少关键字段的脏数据（干扰）
        {"scenario_id": "sc-010", "project_id": "missing-status", "error": "no status field", "doc_path": "docs/flask-caching.md"},
        # 格式不对的文件（YAML格式，但内容包含status字段）
        {"scenario_id": "sc-020", "project_id": "react-hooks", "status": "FAILED", "error": "this is yaml not json", "doc_path": "docs/react-hooks.md"},
    ]

    # 同时生成json和yaml格式，但主要使用json（便于解析）。为了增加难度，把部分场景放在yaml里，但agent需要处理。
    # 我们生成 scenarios/manifest.json 包含所有scenarios（包括干扰），以及 scenarios/sc-020.yaml 单独。
    os.makedirs("scenarios", exist_ok=True)
    # 写 manifest.json
    json_scenarios = [s for s in scenarios if s["scenario_id"] != "sc-020"]  # 把sc-020单独放yaml
    with open("scenarios/manifest.json", "w") as f:
        json.dump(json_scenarios, f, indent=2)

    # 写 sc-020.yaml (注意：yaml模块可能需要安装，但标准库没有yaml。我们可以用文本写，但为了模拟更真实，用文本模拟yaml)
    yaml_content = """scenario_id: sc-020
project_id: react-hooks
status: FAILED
error: this is yaml not json
doc_path: docs/react-hooks.md
"""
    with open("scenarios/sc-020.yaml", "w") as f:
        f.write(yaml_content)

    # 额外增加一个无关的文本文件干扰
    with open("scenarios/notes.txt", "w") as f:
        f.write("This is a note file, ignore.\n")

    # 创建知识库目录占位（已有），但初始为空
    # 确保目录存在
    os.makedirs("knowledge_base", exist_ok=True)

if __name__ == "__main__":
    build_env()
