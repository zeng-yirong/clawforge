import sys
import os
import json

def verify_workspace(workspace: str):
    result = {
        "total_score": 0,
        "details": []
    }

    def add_item(name, score, max_score, passed, reason):
        result["details"].append({
            "item": name,
            "score": score,
            "max_score": max_score,
            "passed": passed,
            "reason": reason
        })
        result["total_score"] += score

    # 1. 检查 ops 目录是否存在 (10分)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        add_item("ops/ directory exists", 10, 10, True, "ops/ directory found")
    else:
        add_item("ops/ directory exists", 0, 10, False, "ops/ directory missing")
        # 如果目录都不存在，直接结束
        result["total_score"] = 0
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f)
        return

    # 2. 检查 ops/launch_post.json 是否存在 (10分)
    target_path = os.path.join(ops_dir, "launch_post.json")
    if os.path.isfile(target_path):
        add_item("ops/launch_post.json exists", 10, 10, True, "Target file found")
    else:
        add_item("ops/launch_post.json exists", 0, 10, False, "Target file missing")
        # 直接结束
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f)
        return

    # 3. 检查 JSON 合法性 (10分)
    try:
        with open(target_path, "r") as f:
            data = json.load(f)
        add_item("JSON parseable", 10, 10, True, "Valid JSON")
    except (json.JSONDecodeError, Exception) as e:
        add_item("JSON parseable", 0, 10, False, f"Invalid JSON: {str(e)}")
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f)
        return

    # 期望的值（来自正确的附件和 accounts.json）
    expected = {
        "mission_name": "Orbital Dawn",
        "launch_window": "2025-06-15T04:30:00Z to 2025-06-15T06:30:00Z",
        "payload": "AuroraCom-2 communications satellite",
        "orbit": "LEO 550km",
        "brand_name": "Aurora Labs Inc.",
        "x_handle": "@auroralabs"
    }

    # 4. 检查必需的字段是否存在 (20分) —— 每个字段 3.33，取整
    required_fields = ["mission_name", "launch_window", "payload", "orbit", "brand_name", "x_handle"]
    missing_fields = [f for f in required_fields if f not in data]
    if missing_fields:
        add_item("Required fields present", 0, 20, False, f"Missing fields: {', '.join(missing_fields)}")
        # 后续字段值检查跳过
        field_score = 0
    else:
        add_item("Required fields present", 20, 20, True, "All six required fields found")
        # 字段值检查 (40分，每个字段 6.66，总计40)
        field_score = 40
        for field in required_fields:
            if data[field] == expected[field]:
                add_item(f"Field '{field}' value correct", 6.66, 6.66, True, f"Value matches expected")
            else:
                add_item(f"Field '{field}' value correct", 0, 6.66, False,
                         f"Expected '{expected[field]}', got '{data[field]}'")
                field_score -= 6.66
        # 调整 field_score 为实际得分（由于浮点，最后取整）
        # 但 add_item 已经累加，我们直接继续

    # 5. 检查是否有多余的字段 (10分)
    allowed_fields = set(required_fields)
    extra_fields = [k for k in data if k not in allowed_fields]
    if extra_fields:
        add_item("No extra fields", 0, 10, False, f"Extra fields: {', '.join(extra_fields)}")
    else:
        add_item("No extra fields", 10, 10, True, "No extra fields present")

    # 6. 检查是否使用了错误的附件版本（通过 mission_name 和 launch_window 的组合确保是 v3 approved）
    # 如果 mission_name 正确但 launch_window 是 draft 或 v2，则会扣分，但字段值检查已经处理
    # 这里额外检测是否用了 v2 或 draft 的 launch_window，但字段值已经扣分。所以不需要再重复。

    # 浮点数处理，确保总分整数
    total_int = round(result["total_score"])
    result["total_score"] = total_int

    # 写入结果
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

    print(f"Verification complete. Score: {total_int}/100")

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify_workspace(workspace)
