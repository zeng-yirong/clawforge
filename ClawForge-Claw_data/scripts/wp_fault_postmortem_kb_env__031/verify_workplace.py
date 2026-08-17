import sys
import os
import json
import math

def verify(workspace: str) -> dict:
    details = []
    total_score = 0.0

    # ---------- 1. 目录结构检查 (10分) ----------
    expected_dirs = ["data/faults", "data/logs", "ops"]
    dir_score = 0
    max_dir = 10
    for d in expected_dirs:
        full_path = os.path.join(workspace, d)
        if os.path.isdir(full_path):
            dir_score += 3.33  # 约3.33分每个，总分10
    dir_score = min(dir_score, max_dir)
    total_score += dir_score
    details.append({
        "item": "Required directories exist",
        "score": round(dir_score, 2),
        "max_score": max_dir,
        "passed": dir_score == max_dir,
        "reason": f"Found {int(dir_score/3.33)} of 3 expected directories"
    })

    # ---------- 2. 报告文件存在 (15分) ----------
    report_path = os.path.join(workspace, "ops", "report.json")
    file_exists = os.path.isfile(report_path)
    file_score = 15 if file_exists else 0
    total_score += file_score
    details.append({
        "item": "ops/report.json exists",
        "score": file_score,
        "max_score": 15,
        "passed": file_exists,
        "reason": "File exists" if file_exists else "File not found"
    })

    if not file_exists:
        # 后续检查无法进行，直接返回
        return {"total_score": round(total_score), "details": details}

    # ---------- 3. JSON 合法性 (10分) ----------
    try:
        with open(report_path, "r") as f:
            report = json.load(f)
        json_score = 10
    except (json.JSONDecodeError, Exception) as e:
        json_score = 0
        report = {}
        details.append({
            "item": "report.json is valid JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Invalid JSON: {str(e)}"
        })
        total_score += 0
        # 继续可能报错，但为了鲁棒性，返回
        return {"total_score": round(total_score), "details": details}

    details.append({
        "item": "report.json is valid JSON",
        "score": json_score,
        "max_score": 10,
        "passed": True,
        "reason": "Valid JSON"
    })
    total_score += json_score

    # ---------- 4. 必填字段检查 (15分) ----------
    required_fields = ["fault_id", "root_cause", "repair_plan", "severity", "service_name"]
    field_score = 0
    max_field = 15
    missing = []
    for f in required_fields:
        if f in report and report[f] is not None and (isinstance(report[f], str) and report[f].strip() != ""):
            field_score += 3
        else:
            missing.append(f)
    details.append({
        "item": "Required fields present and non-empty",
        "score": field_score,
        "max_score": max_field,
        "passed": field_score == max_field,
        "reason": f"Missing or empty fields: {missing}" if missing else "All required fields present"
    })
    total_score += field_score

    # ---------- 5. 核心内容正确性 (50分) ----------
    # 正确答案由环境唯一确定：
    # fault_id = "fault_002"
    # root_cause = "Missing composite index on orders (status, created_at) causing full table scans and lock escalation."
    # repair_plan = "Create index idx_orders_status_created_at on orders(status, created_at); also add retry logic for deadlock."
    # severity = "critical"
    # service_name = "order-service"
    core_score = 0
    max_core = 50

    # 逐项比对，允许轻微前后空格差异
    def normalize(s):
        return " ".join(s.strip().split())

    # fault_id
    expected_fault_id = "fault_002"
    if normalize(report.get("fault_id", "")) == normalize(expected_fault_id):
        core_score += 10
    else:
        pass  # no partial credit for wrong id

    # root_cause
    expected_root_cause = "Missing composite index on orders (status, created_at) causing full table scans and lock escalation."
    if normalize(report.get("root_cause", "")) == normalize(expected_root_cause):
        core_score += 20
    else:
        # 部分匹配？不设部分分，直接0
        pass

    # repair_plan
    expected_repair = "Create index idx_orders_status_created_at on orders(status, created_at); also add retry logic for deadlock."
    if normalize(report.get("repair_plan", "")) == normalize(expected_repair):
        core_score += 10
    else:
        pass

    # severity
    expected_severity = "critical"
    if normalize(report.get("severity", "")) == normalize(expected_severity):
        core_score += 5
    else:
        pass

    # service_name
    expected_service = "order-service"
    if normalize(report.get("service_name", "")) == normalize(expected_service):
        core_score += 5
    else:
        pass

    details.append({
        "item": "Core content matches ground truth",
        "score": core_score,
        "max_score": max_core,
        "passed": core_score == max_core,
        "reason": f"Got {core_score}/{max_core} points on exact field matching"
    })
    total_score += core_score

    # ---------- 6. 禁止额外字段乱入 (可选扣分，这里不加分) ----------
    allowed_extra = set()  # 不鼓励添加额外字段，但如果有也不扣分（保持简单）

    # 最终总分取整
    final_score = math.floor(total_score)
    return {
        "total_score": final_score,
        "details": details
    }

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    # 写入评分文件
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Verification completed, score: {result['total_score']}")

if __name__ == "__main__":
    main()
