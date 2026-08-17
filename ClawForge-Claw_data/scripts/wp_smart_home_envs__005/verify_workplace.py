import json
import os
import sys

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    os.chdir(workspace)

    details = []
    total_score = 0
    max_total = 100

    # 1. 检查 ops 目录是否存在 (10分)
    ops_dir = "ops"
    if os.path.isdir(ops_dir):
        details.append({"item": "ops directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "ops directory found"})
        total_score += 10
    else:
        details.append({"item": "ops directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "ops directory missing"})

    # 2. 检查目标文件是否存在 (10分)
    target_file = os.path.join(ops_dir, "health_conflicts.json")
    if os.path.isfile(target_file):
        details.append({"item": "ops/health_conflicts.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "file found"})
        total_score += 10
    else:
        details.append({"item": "ops/health_conflicts.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "file missing"})
        # 后续检查无法进行，直接返回
        # 仍然生成 score 文件
        write_score(total_score, max_total, details)
        return

    # 3. 检查 JSON 合法性 (10分)
    try:
        with open(target_file, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        details.append({"item": "valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON parse error: {e}"})
        write_score(total_score, max_total, details)
        return

    if not isinstance(data, list):
        details.append({"item": "valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": "root must be a list"})
        write_score(total_score, max_total, details)
        return
    details.append({"item": "valid JSON", "score": 10, "max_score": 10, "passed": True, "reason": "valid list"})
    total_score += 10

    # 4. 内容正确性 (70分)
    # 期望的两个冲突项
    expected_conflicts = [
        {
            "user_id": "jane_smith",
            "device_id": "humidifier_bedroom",
            "conflict_type": "humidity_out_of_range",
            "current_humidity": 30,
            "recommended_humidity": 50
        },
        {
            "user_id": "john_smith",
            "device_id": "ac_bedroom",
            "conflict_type": "temperature_out_of_range",
            "current_temperature": 26,
            "recommended_temperature": 21
        }
    ]

    # 简单起见，每匹配一个完整项35分，共70分；额外项或缺少项扣分
    matched_entries = 0
    for exp in expected_conflicts:
        found = False
        for entry in data:
            if all(entry.get(k) == v for k, v in exp.items()):
                found = True
                break
        if found:
            matched_entries += 1
        else:
            details.append({"item": f"Conflict for {exp['user_id']} / {exp['device_id']}", "score": 0, "max_score": 35, "passed": False, "reason": f"Missing or incorrect entry: expected {json.dumps(exp)}"})

    # 检查多余项（有额外项扣分）
    extra_entries = len(data) - len(expected_conflicts)
    if extra_entries > 0:
        # 每个多余项扣5分，最多扣20分
        penalty = min(extra_entries * 5, 20)
        details.append({"item": "No extra conflicts", "score": 0, "max_score": 0, "passed": False, "reason": f"Found {extra_entries} extra entries, penalty -{penalty}"})
        # 从总得分中扣分，但不在 details 中体现分数？我们直接在 total_score 中减
        # 更规范：在 detail 中记录扣分
        details.append({"item": "Extra entries penalty", "score": -penalty, "max_score": 0, "passed": False, "reason": f"Penalty for {extra_entries} extra entries"})
        # 修改总得分
        total_score -= penalty

    if matched_entries == 2:
        details.append({"item": "Both core conflicts matched", "score": 70, "max_score": 70, "passed": True, "reason": "All expected conflict entries found"})
        total_score += 70
    else:
        # 已在上面的循环中记录了缺失项的分数，这里只补充总分
        score_this = matched_entries * 35
        details.append({"item": "Core conflicts matching", "score": score_this, "max_score": 70, "passed": score_this == 70, "reason": f"Matched {matched_entries} out of 2 expected"})
        total_score += score_this

    # 确保总分不超过100
    final_score = max(0, min(total_score, 100))

    # 写入分数文件
    write_score(final_score, max_total, details)

def write_score(total, max_total, details):
    result = {
        "total_score": total,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    verify()
