import os
import json

def build_env():
    # 创建 scenarios 目录
    os.makedirs("scenarios", exist_ok=True)
    os.makedirs("archive", exist_ok=True)

    # 正确的 scenario（唯一可复现的）
    correct_scenario = {
        "scenario_id": "S-002",
        "project": "alpha",
        "steps": [
            "Step 1: Start the server with `npm start`",
            "Step 2: Send POST request to /api/trigger with payload {\"type\": \"bug\"}",
            "Step 3: Check logs for stack trace and observe database write failure"
        ],
        "status": "verified"
    }
    with open("scenarios/scenario_002.json", "w", encoding="utf-8") as f:
        json.dump(correct_scenario, f, indent=2)

    # 干扰项：草稿，status 不是 verified
    draft_scenario = {
        "scenario_id": "S-001",
        "project": "alpha",
        "steps": [
            "Step 1: Install dependencies",
            "Step 2: Run tests (not stable yet)"
        ],
        "status": "draft"
    }
    with open("scenarios/scenario_001.json", "w", encoding="utf-8") as f:
        json.dump(draft_scenario, f, indent=2)

    # 干扰项：status 是 verified 但 steps 为空（不完整）
    empty_steps_scenario = {
        "scenario_id": "S-003",
        "project": "beta",
        "steps": [],
        "status": "verified"
    }
    with open("scenarios/scenario_003.json", "w", encoding="utf-8") as f:
        json.dump(empty_steps_scenario, f, indent=2)

    # 干扰项：字段缺失（没有 steps）
    missing_field_scenario = {
        "scenario_id": "S-004",
        "project": "gamma",
        "status": "verified"
    }
    with open("scenarios/scenario_004.json", "w", encoding="utf-8") as f:
        json.dump(missing_field_scenario, f, indent=2)

    # 干扰项：重复文件名但内容无关（诱饵）
    with open("scenarios/duplicate.json", "w", encoding="utf-8") as f:
        f.write("This is not a valid JSON file -- just a decoy.\n")

    # 额外脏数据：在 archive 目录预先放一个旧版本（应与最终结果不同）
    old_archive = {
        "scenario_id": "S-OLD",
        "project": "obsolete",
        "steps": ["Old step that doesn't matter"],
        "status": "archived"
    }
    with open("archive/reproduction_ledger.json", "w", encoding="utf-8") as f:
        json.dump(old_archive, f, indent=2)

if __name__ == "__main__":
    build_env()
