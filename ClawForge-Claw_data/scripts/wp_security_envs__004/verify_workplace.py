import sys
import os
import json
import csv
import re

def verify(workspace):
    details = []
    total_score = 0
    max_total = 100

    # ------------------------------------------------------------------
    # 1. 基础目录结构检查 (10分)
    # ------------------------------------------------------------------
    required_dirs = ["data", "logs", "ops"]
    dir_score = 0
    for d in required_dirs:
        if os.path.isdir(os.path.join(workspace, d)):
            dir_score += 3
        else:
            details.append({
                "item": f"Directory {d} exists",
                "score": 0,
                "max_score": 3,
                "passed": False,
                "reason": f"Missing directory: {d}"
            })
    # 额外奖励: 检测到干扰文件 data/zones_backup.json 存在 (1分)
    if os.path.isfile(os.path.join(workspace, "data", "zones_backup.json")):
        dir_score += 1
    details.append({
        "item": "Required directories & expected interference files",
        "score": dir_score,
        "max_score": 10,
        "passed": dir_score >= 6,
        "reason": f"Directories: {required_dirs} present, backup file found: {os.path.isfile(os.path.join(workspace, 'data', 'zones_backup.json'))}"
    })
    total_score += dir_score

    # ------------------------------------------------------------------
    # 2. 目标文件 ops/lock_target.json 存在性 (10分)
    # ------------------------------------------------------------------
    target_path = os.path.join(workspace, "ops", "lock_target.json")
    if os.path.isfile(target_path):
        target_exists_score = 10
        details.append({
            "item": "ops/lock_target.json exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Target file found."
        })
    else:
        details.append({
            "item": "ops/lock_target.json exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Target file not found."
        })
        total_score += 0
        # 如果文件不存在，后续不执行
        total_score = min(total_score, 100)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return total_score

    total_score += 10

    # ------------------------------------------------------------------
    # 3. JSON 合法性 (10分)
    # ------------------------------------------------------------------
    try:
        with open(target_path, "r") as f:
            data = json.load(f)
        json_valid_score = 10
        details.append({
            "item": "lock_target.json is valid JSON",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Parsed successfully."
        })
    except (json.JSONDecodeError, Exception) as e:
        details.append({
            "item": "lock_target.json is valid JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON parse error: {e}"
        })
        total_score += 0
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return total_score

    total_score += 10

    # ------------------------------------------------------------------
    # 4. 字段结构检查 (10分) 必须包含 door_id 且值为字符串
    # ------------------------------------------------------------------
    if isinstance(data, dict) and "door_id" in data and isinstance(data["door_id"], str):
        field_score = 10
        details.append({
            "item": "lock_target.json has correct field: door_id (string)",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"Found door_id: {data['door_id']}"
        })
    else:
        field_score = 0
        details.append({
            "item": "lock_target.json has correct field: door_id (string)",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Expected dict with 'door_id' string, got: {type(data)}; keys: {data.keys() if isinstance(data, dict) else 'N/A'}"
        })
    total_score += field_score

    # ------------------------------------------------------------------
    # 5. door_id 值正确性 (50分) 唯一正确答案: door_001
    # ------------------------------------------------------------------
    correct_door_id = "door_001"
    if data.get("door_id") == correct_door_id:
        value_score = 50
        details.append({
            "item": "door_id value is correct",
            "score": 50,
            "max_score": 50,
            "passed": True,
            "reason": f"Expected {correct_door_id}, got {data.get('door_id')}"
        })
    else:
        value_score = 0
        details.append({
            "item": "door_id value is correct",
            "score": 0,
            "max_score": 50,
            "passed": False,
            "reason": f"Expected {correct_door_id}, got {data.get('door_id')}"
        })
    total_score += value_score

    # ------------------------------------------------------------------
    # 6. 额外: 确保没有多余的非预期字段 (扣分项, 从总分扣, 最多-10)
    # ------------------------------------------------------------------
    expected_keys = {"door_id"}
    extra_keys = set(data.keys()) - expected_keys
    if extra_keys:
        penalty = min(10, len(extra_keys) * 5)
        total_score -= penalty
        details.append({
            "item": "No extra fields in lock_target.json",
            "score": max(0, 10 - penalty),
            "max_score": 10,
            "passed": False,
            "reason": f"Extra keys found: {extra_keys}. Penalty -{penalty}."
        })
    else:
        details.append({
            "item": "No extra fields in lock_target.json",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Only expected field present."
        })

    # 总分不超过100
    total_score = min(total_score, 100)
    total_score = max(total_score, 0)

    # 写入结果
    result = {
        "total_score": total_score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

    return total_score

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
