import os
import json
import random

def build_env():
    # 确保根目录存在（当前cwd已是资产目录）
    os.makedirs("project_docs", exist_ok=True)
    os.makedirs("scenarios", exist_ok=True)
    os.makedirs("knowledge_entries", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("backups", exist_ok=True)
    os.makedirs("output", exist_ok=True)  # agent应输出的目录

    # --- 项目文档 ---
    doc_038 = {
        "doc_id": "doc_001",
        "project_id": "proj_038",
        "title": "Bug Fix v2.1",
        "path": "docs/readme.md"
    }
    # 干扰文档（其他项目）
    doc_other = {
        "doc_id": "doc_002",
        "project_id": "proj_999",
        "title": "Feature Update",
        "path": "docs/feature.md"
    }
    with open("project_docs/project_038_doc.json", "w") as f:
        json.dump(doc_038, f, indent=2)
    with open("project_docs/other_project_doc.json", "w") as f:
        json.dump(doc_other, f, indent=2)

    # --- 场景记录 ---
    # 属于 proj_038 的场景
    scenario_01 = {
        "scenario_id": "sc_01",
        "project_id": "proj_038",
        "title": "Login crash",
        "steps": ["open app", "enter credentials", "click login"],
        "expected_result": "login success",
        "actual_result": "app crash",
        "status": "failed"
    }
    scenario_02 = {
        "scenario_id": "sc_02",
        "project_id": "proj_038",
        "title": "Data not saved",
        "steps": ["fill form", "submit", "reopen"],
        "expected_result": "data persisted",
        "actual_result": "data lost",
        "status": "failed"
    }
    # 干扰场景（其他项目）
    scenario_other = {
        "scenario_id": "sc_03",
        "project_id": "proj_999",
        "title": "Another bug",
        "steps": ["do X", "do Y"],
        "expected_result": "success",
        "actual_result": "error",
        "status": "failed"
    }
    # 干扰场景（重复 ID 但属于其他项目，应不被纳入）
    scenario_duplicate = {
        "scenario_id": "sc_01",
        "project_id": "proj_999",
        "title": "Duplicate ID different project",
        "steps": ["test"],
        "expected_result": "ok",
        "actual_result": "ok",
        "status": "passed"
    }
    with open("scenarios/scenario_a.json", "w") as f:
        json.dump(scenario_01, f, indent=2)
    with open("scenarios/scenario_b.json", "w") as f:
        json.dump(scenario_02, f, indent=2)
    with open("scenarios/scenario_other.json", "w") as f:
        json.dump(scenario_other, f, indent=2)
    with open("scenarios/scenario_dup.json", "w") as f:
        json.dump(scenario_duplicate, f, indent=2)

    # --- 旧的知识库条目（干扰） ---
    old_ledger = {
        "ledger_id": "ledger_037",
        "project_id": "proj_038",
        "title": "Old Bug Fix v2.0",
        "scenarios": [
            {"scenario_id": "sc_01", "title": "Login crash", "status": "failed"},
            {"scenario_id": "sc_04", "title": "Missing cache", "status": "failed"}
        ],
        "status": "archived"
    }
    with open("knowledge_entries/old_ledger.json", "w") as f:
        json.dump(old_ledger, f, indent=2)

    # --- 干扰日志与备份 ---
    for i in range(5):
        with open(f"logs/log_{i}.txt", "w") as f:
            f.write(f"dummy log entry {i}\n")
    with open("backups/old_scenarios_backup.json", "w") as f:
        json.dump({"ignored": True}, f)

if __name__ == "__main__":
    build_env()
