import sys
import os
import json
import re

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results = []
    total_score = 0
    max_total = 100

    # 1. 检查 ops 目录是否存在 (10分)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        results.append({
            "item": "ops directory exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "ops/ directory created."
        })
        total_score += 10
    else:
        results.append({
            "item": "ops directory exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ops/ directory not found."
        })

    # 2. 检查 ops/resolution.json 是否存在并合法 (15分)
    resolution_path = os.path.join(ops_dir, "resolution.json")
    if not os.path.isfile(resolution_path):
        results.append({
            "item": "resolution.json exists and valid JSON",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": "ops/resolution.json not found."
        })
    else:
        try:
            with open(resolution_path, "r") as f:
                resolution = json.load(f)
            # 必须是一个字典，包含 incidents 键
            if isinstance(resolution, dict) and "incidents" in resolution:
                results.append({
                    "item": "resolution.json exists and valid JSON",
                    "score": 15,
                    "max_score": 15,
                    "passed": True,
                    "reason": "Valid JSON object with 'incidents' key."
                })
                total_score += 15
                # 后续检查 incidents 数组内容
                incidents = resolution["incidents"]
                if not isinstance(incidents, list):
                    results.append({"item": "incidents is a list", "score": 0, "max_score": 5, "passed": False, "reason": "'incidents' is not a list."})
                else:
                    # 3. 检查是否包含正确数量的目标工单 (30分)
                    # 目标工单ID: INC-UPS-001, INC-UPS-002, INC-UPS-003
                    expected_ids = {"INC-UPS-001", "INC-UPS-002", "INC-UPS-003"}
                    actual_ids = set()
                    for inc in incidents:
                        if isinstance(inc, dict) and "incident_id" in inc:
                            actual_ids.add(inc["incident_id"])
                    if actual_ids == expected_ids:
                        results.append({
                            "item": "Correct incident IDs (INC-UPS-001/002/003) present",
                            "score": 30,
                            "max_score": 30,
                            "passed": True,
                            "reason": "Exactly the three target incidents included, no extras."
                        })
                        total_score += 30
                    elif expected_ids.issubset(actual_ids) and len(actual_ids) > len(expected_ids):
                        results.append({
                            "item": "Correct incident IDs (no extra)",
                            "score": 15,
                            "max_score": 30,
                            "passed": False,
                            "reason": f"Extra incidents found: {actual_ids - expected_ids}."
                        })
                    else:
                        results.append({
                            "item": "Correct incident IDs",
                            "score": 0,
                            "max_score": 30,
                            "passed": False,
                            "reason": f"Found IDs {actual_ids}, expected {expected_ids}."
                        })

                    # 4. 检查每个工单字段是否正确 (20分)
                    field_ok = True
                    for inc in incidents:
                        if not isinstance(inc, dict):
                            field_ok = False
                            break
                        if not (inc.get("incident_id") in expected_ids and inc.get("status") == "resolved" and inc.get("action") == "batch_remediate"):
                            field_ok = False
                            break
                    if field_ok and len(incidents) == len(expected_ids):
                        results.append({
                            "item": "Each incident has status='resolved' and action='batch_remediate'",
                            "score": 20,
                            "max_score": 20,
                            "passed": True,
                            "reason": "All target incidents correctly formatted."
                        })
                        total_score += 20
                    else:
                        results.append({
                            "item": "Each incident has status='resolved' and action='batch_remediate'",
                            "score": 0,
                            "max_score": 20,
                            "passed": False,
                            "reason": "Some incidents missing required fields or wrong values."
                        })

            else:
                results.append({
                    "item": "resolution.json exists and valid JSON",
                    "score": 0,
                    "max_score": 15,
                    "passed": False,
                    "reason": "JSON root is not an object with 'incidents' key."
                })
        except (json.JSONDecodeError, Exception) as e:
            results.append({
                "item": "resolution.json exists and valid JSON",
                "score": 0,
                "max_score": 15,
                "passed": False,
                "reason": f"JSON parse error: {e}"
            })

    # 5. 检查 ops/audit.log 是否存在并格式合理 (25分)
    audit_path = os.path.join(ops_dir, "audit.log")
    if not os.path.isfile(audit_path):
        results.append({
            "item": "audit.log exists with action steps",
            "score": 0,
            "max_score": 25,
            "passed": False,
            "reason": "ops/audit.log not found."
        })
    else:
        try:
            with open(audit_path, "r") as f:
                lines = f.readlines()
            # 检查至少包含几个关键动作
            required_actions = ["START", "READ_INCIDENTS", "SCREEN_RISK", "BATCH_REMEDIATE", "WRITE_RESOLUTION", "END"]
            found_actions = set()
            for line in lines:
                # 期望格式: timestamp ACTION [detail]
                line = line.strip()
                if line:
                    # 尝试提取动作名称（第二个字段）
                    parts = line.split()
                    if len(parts) >= 2:
                        action = parts[1]  # 假设第二个字段是动作
                        if action in required_actions:
                            found_actions.add(action)
            missing = set(required_actions) - found_actions
            if not missing:
                results.append({
                    "item": "audit.log contains all required steps",
                    "score": 25,
                    "max_score": 25,
                    "passed": True,
                    "reason": "All six key actions found in audit log."
                })
                total_score += 25
            else:
                results.append({
                    "item": "audit.log contains all required steps",
                    "score": int(25 * (len(found_actions) / len(required_actions))),
                    "max_score": 25,
                    "passed": False,
                    "reason": f"Missing actions: {missing}. Found: {found_actions}"
                })
        except Exception as e:
            results.append({
                "item": "audit.log exists with action steps",
                "score": 0,
                "max_score": 25,
                "passed": False,
                "reason": f"Error reading audit.log: {e}"
            })

    # 确保总分不超过100
    total_score = min(total_score, 100)
    final = {
        "total_score": total_score,
        "details": results
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(final, f, indent=2)
    print(f"Score written: {total_score}/100")

if __name__ == "__main__":
    main()
