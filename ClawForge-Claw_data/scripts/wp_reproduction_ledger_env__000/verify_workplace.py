#!/usr/bin/env python3
import sys
import json
import os
import pathlib

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0

    # 1. 检查 archive 目录存在 (10分)
    archive_dir = os.path.join(workspace, "archive")
    if os.path.isdir(archive_dir):
        score_details.append({
            "item": "archive directory exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "archive directory is present"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "archive directory exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "archive directory not found"
        })

    # 2. 检查 reproduction_ledger.json 存在且合法 (10分)
    ledger_path = os.path.join(archive_dir, "reproduction_ledger.json")
    if os.path.isfile(ledger_path):
        try:
            with open(ledger_path, "r") as f:
                data = json.load(f)
            is_valid = isinstance(data, dict) and "project" in data and "commit_hash" in data and "version" in data
            if is_valid:
                score_details.append({
                    "item": "ledger JSON valid and has required fields",
                    "score": 10,
                    "max_score": 10,
                    "passed": True,
                    "reason": "JSON is valid with all required fields"
                })
                total_score += 10
            else:
                score_details.append({
                    "item": "ledger JSON valid and has required fields",
                    "score": 0,
                    "max_score": 10,
                    "passed": False,
                    "reason": "JSON is missing one or more required fields (project, commit_hash, version)"
                })
        except (json.JSONDecodeError, IOError) as e:
            score_details.append({
                "item": "ledger JSON valid and has required fields",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"Failed to parse JSON: {e}"
            })
    else:
        score_details.append({
            "item": "ledger JSON valid and has required fields",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "archive/reproduction_ledger.json not found"
        })

    # 3. 检查核心值正确性 (70分)
    if os.path.isfile(ledger_path):
        try:
            with open(ledger_path, "r") as f:
                data = json.load(f)
        except:
            data = {}
        # 3a. project 应为 project-alpha (10分)
        project_ok = data.get("project") == "project-alpha"
        if project_ok:
            score_details.append({
                "item": "project field is 'project-alpha'",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "project set correctly"
            })
            total_score += 10
        else:
            score_details.append({
                "item": "project field is 'project-alpha'",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"expected 'project-alpha', got {data.get('project')}"
            })

        # 3b. commit_hash 应为 def456 (30分)
        commit_ok = data.get("commit_hash") == "def456"
        if commit_ok:
            score_details.append({
                "item": "commit_hash is 'def456'",
                "score": 30,
                "max_score": 30,
                "passed": True,
                "reason": "correct commit hash from latest valid document"
            })
            total_score += 30
        else:
            score_details.append({
                "item": "commit_hash is 'def456'",
                "score": 0,
                "max_score": 30,
                "passed": False,
                "reason": f"expected 'def456', got {data.get('commit_hash')}"
            })

        # 3c. version 应为 2.0 (30分)
        version_ok = data.get("version") == "2.0"
        if version_ok:
            score_details.append({
                "item": "version is '2.0'",
                "score": 30,
                "max_score": 30,
                "passed": True,
                "reason": "correct version from latest valid document"
            })
            total_score += 30
        else:
            score_details.append({
                "item": "version is '2.0'",
                "score": 0,
                "max_score": 30,
                "passed": False,
                "reason": f"expected '2.0', got {data.get('version')}"
            })
    else:
        # 如果文件不存在，这些子项全部0分
        for item_name in ["project field", "commit_hash", "version"]:
            score_details.append({
                "item": f"core value: {item_name}",
                "score": 0,
                "max_score": 10 if "project" in item_name else 30,
                "passed": False,
                "reason": "ledger file missing"
            })

    # 4. 检查未使用干扰项/废弃文档 (10分)
    # 理论上如果 agent 用错了，commit_hash 或 version 就会错，但额外加分项：
    # 确保文件中没有包含废弃文档或错误项目的痕迹。
    # 这里简单检查: 如果 commit_hash 是 def456 且 version 是 2.0，则加分。
    if os.path.isfile(ledger_path):
        try:
            with open(ledger_path, "r") as f:
                data = json.load(f)
        except:
            data = {}
        if data.get("commit_hash") == "def456" and data.get("version") == "2.0":
            score_details.append({
                "item": "no deprecated/other project data used",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "correct data indicates no interference"
            })
            total_score += 10
        else:
            score_details.append({
                "item": "no deprecated/other project data used",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": "incorrect data suggests wrong source"
            })
    else:
        score_details.append({
            "item": "no deprecated/other project data used",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ledger file missing"
        })

    # 汇总总分 (上限100)
    total_score = min(total_score, 100)
    result = {
        "total_score": total_score,
        "details": score_details
    }
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score: {total_score}/100")

if __name__ == "__main__":
    main()
