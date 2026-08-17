import json
import os
import sys

def verify_workplace(workspace: str):
    score_info = {
        "total_score": 0,
        "details": []
    }

    # 定义权重
    weights = {
        "dir_ops": 10,
        "file_issue_device": 10,
        "json_valid": 10,
        "field_suspect_plug_id": 20,
        "value_correct": 50
    }

    # 1. 检查 ops 目录是否存在
    ops_dir = os.path.join(workspace, "ops")
    dir_exists = os.path.isdir(ops_dir)
    if dir_exists:
        score_info["details"].append({
            "item": "ops directory exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Found ops/ directory."
        })
    else:
        score_info["details"].append({
            "item": "ops directory exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ops/ directory not found."
        })
        # 如果目录都不存在，后续检查不用进行了，但为了完整保持结构

    # 2. 检查 ops/issue_device.json 是否存在
    issue_path = os.path.join(workspace, "ops", "issue_device.json")
    file_exists = os.path.isfile(issue_path)
    if file_exists:
        score_info["details"].append({
            "item": "issue_device.json exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "File ops/issue_device.json found."
        })
    else:
        score_info["details"].append({
            "item": "issue_device.json exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File ops/issue_device.json not found."
        })
        # 如果文件不存在，后续检查都标记为失败，但继续解析以避免 index 错误
        file_exists = False

    # 3. 解析 JSON 并检查合法性
    json_valid = False
    parsed = None
    if file_exists:
        try:
            with open(issue_path, "r") as f:
                parsed = json.load(f)
            json_valid = True
            reason = "Valid JSON."
        except (json.JSONDecodeError, Exception) as e:
            reason = f"Invalid JSON: {e}"
    else:
        reason = "File missing, cannot validate JSON."

    if json_valid:
        score_info["details"].append({
            "item": "JSON is valid",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": reason
        })
    else:
        score_info["details"].append({
            "item": "JSON is valid",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": reason
        })

    # 4. 检查字段 suspect_plug_id 是否存在
    field_exists = False
    if json_valid and isinstance(parsed, dict):
        if "suspect_plug_id" in parsed:
            field_exists = True
            reason = "Field 'suspect_plug_id' exists."
        else:
            reason = "Field 'suspect_plug_id' missing."
    else:
        reason = "Cannot check field because JSON is invalid or not an object."

    if field_exists:
        score_info["details"].append({
            "item": "Field suspect_plug_id exists",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": reason
        })
    else:
        score_info["details"].append({
            "item": "Field suspect_plug_id exists",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": reason
        })

    # 5. 检查值是否正确（必须为 "plug_ac_living"）
    value_correct = False
    if field_exists:
        val = parsed["suspect_plug_id"]
        if val == "plug_ac_living":
            value_correct = True
            reason = f"Value is 'plug_ac_living' as expected."
        else:
            reason = f"Value is '{val}', expected 'plug_ac_living'."
    else:
        reason = "Cannot check value because field missing."

    if value_correct:
        score_info["details"].append({
            "item": "suspect_plug_id value is correct",
            "score": 50,
            "max_score": 50,
            "passed": True,
            "reason": reason
        })
    else:
        score_info["details"].append({
            "item": "suspect_plug_id value is correct",
            "score": 0,
            "max_score": 50,
            "passed": False,
            "reason": reason
        })

    # 计算总分
    total = sum(item["score"] for item in score_info["details"])
    score_info["total_score"] = total

    # 写入 score 文件
    output_path = os.path.join(workspace, "workplace_score.json")
    with open(output_path, "w") as f:
        json.dump(score_info, f, indent=2)

    return score_info

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify_workplace(workspace)
