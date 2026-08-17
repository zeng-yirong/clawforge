import sys
import json
import os

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0
    max_possible = 100

    # 1. 目录与文件存在检查 (10分)
    ops_dir = os.path.join(workspace, "ops")
    pm_file = os.path.join(ops_dir, "postmortem.json")
    dir_exists = os.path.isdir(ops_dir)
    file_exists = os.path.isfile(pm_file)

    if dir_exists:
        score_details.append({"item": "ops directory exists", "score": 5, "max_score": 5, "passed": True, "reason": "ops/ found"})
        total_score += 5
    else:
        score_details.append({"item": "ops directory exists", "score": 0, "max_score": 5, "passed": False, "reason": "ops/ not found"})

    if file_exists:
        score_details.append({"item": "postmortem.json exists", "score": 5, "max_score": 5, "passed": True, "reason": "postmortem.json found"})
        total_score += 5
    else:
        score_details.append({"item": "postmortem.json exists", "score": 0, "max_score": 5, "passed": False, "reason": "postmortem.json not found"})
        # 后续无法继续检查，直接返回
        write_score(total_score, score_details)
        return

    # 2. JSON合法与必要字段 (30分)
    try:
        with open(pm_file, "r") as f:
            data = json.load(f)
        score_details.append({"item": "JSON parseable", "score": 10, "max_score": 10, "passed": True, "reason": "valid JSON"})
        total_score += 10
    except Exception as e:
        score_details.append({"item": "JSON parseable", "score": 0, "max_score": 10, "passed": False, "reason": f"parse error: {e}"})
        write_score(total_score, score_details)
        return

    # 检查必要字段
    required_fields = ["fault_id", "root_cause", "repair_plan", "affected_services"]
    missing = [f for f in required_fields if f not in data]
    if missing:
        score_details.append({"item": "Required fields present", "score": 0, "max_score": 20, "passed": False, "reason": f"missing fields: {missing}"})
        total_score += 0
    else:
        score_details.append({"item": "Required fields present", "score": 20, "max_score": 20, "passed": True, "reason": "all four fields present"})
        total_score += 20

    # 3. 字段值正确性 (60分)
    # fault_id
    fid = data.get("fault_id")
    if fid == "fault_003":
        score_details.append({"item": "fault_id correct", "score": 15, "max_score": 15, "passed": True, "reason": "fault_003"})
        total_score += 15
    else:
        score_details.append({"item": "fault_id correct", "score": 0, "max_score": 15, "passed": False, "reason": f"got {fid}, expected fault_003"})

    # root_cause
    rc = data.get("root_cause", "")
    expected_rc = "Database connection pool exhausted"
    if rc == expected_rc:
        score_details.append({"item": "root_cause correct", "score": 15, "max_score": 15, "passed": True, "reason": "exact match"})
        total_score += 15
    else:
        score_details.append({"item": "root_cause correct", "score": 0, "max_score": 15, "passed": False, "reason": f"got '{rc}', expected '{expected_rc}'"})

    # repair_plan
    rp = data.get("repair_plan", "")
    expected_rp = "Increase max connections from 10 to 50, and add connection timeout"
    if rp == expected_rp:
        score_details.append({"item": "repair_plan correct", "score": 15, "max_score": 15, "passed": True, "reason": "exact match"})
        total_score += 15
    else:
        score_details.append({"item": "repair_plan correct", "score": 0, "max_score": 15, "passed": False, "reason": f"got '{rp}', expected '{expected_rp}'"})

    # affected_services (支持字符串或列表，但必须包含 payment-svc 和 db-pool)
    af = data.get("affected_services")
    af_string = ""
    if isinstance(af, list):
        af_string = ", ".join(af)
    elif isinstance(af, str):
        af_string = af
    else:
        af_string = str(af) if af else ""
    # 标准化后比较
    expected_af = "payment-svc, db-pool"
    # 允许空格和顺序不同，但这里我们精确要求相同顺序（附件中顺序如此）
    if af_string == expected_af:
        score_details.append({"item": "affected_services correct", "score": 15, "max_score": 15, "passed": True, "reason": "exact match"})
        total_score += 15
    else:
        # 宽松检查：两个服务名都存在
        services = [s.strip() for s in af_string.replace(",", " ").split() if s.strip()]
        if "payment-svc" in services and "db-pool" in services:
            score_details.append({"item": "affected_services correct", "score": 10, "max_score": 15, "passed": True, "reason": "contains both services but format differs"})
            total_score += 10
        else:
            score_details.append({"item": "affected_services correct", "score": 0, "max_score": 15, "passed": False, "reason": f"got '{af_string}', expected '{expected_af}'"})

    write_score(total_score, score_details)

def write_score(total, details):
    output = {
        "total_score": min(total, 100),
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(output, f, indent=2)
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
