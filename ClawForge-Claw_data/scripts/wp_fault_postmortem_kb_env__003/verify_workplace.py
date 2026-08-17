import json
import os
import sys

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

def load_json(path):
    with open(os.path.join(workspace, path), "r") as f:
        return json.load(f)

score_details = []
total_score = 0

# 1. 目录结构 (10分)
def check_dir_structure():
    required_dirs = ["ops"]
    max_score = 10
    for d in required_dirs:
        if not os.path.isdir(os.path.join(workspace, d)):
            return score_details.append({
                "item": "Directory structure",
                "score": 0,
                "max_score": max_score,
                "passed": False,
                "reason": f"Missing directory: {d}"
            })
    score_details.append({
        "item": "Directory structure",
        "score": max_score,
        "max_score": max_score,
        "passed": True,
        "reason": "ops directory exists"
    })
    return max_score

total_score += check_dir_structure()

# 2. 报告文件存在且合法JSON (10分)
def check_report_exists():
    path = os.path.join(workspace, "ops", "postmortem_report.json")
    max_score = 10
    if not os.path.isfile(path):
        score_details.append({
            "item": "Report file exists",
            "score": 0,
            "max_score": max_score,
            "passed": False,
            "reason": "ops/postmortem_report.json not found"
        })
        return 0
    try:
        with open(path, "r") as f:
            data = json.load(f)
        score_details.append({
            "item": "Report file exists and valid JSON",
            "score": max_score,
            "max_score": max_score,
            "passed": True,
            "reason": "File exists and parses as JSON"
        })
        return max_score, data
    except Exception as e:
        score_details.append({
            "item": "Report file exists and valid JSON",
            "score": 0,
            "max_score": max_score,
            "passed": False,
            "reason": f"JSON parse error: {e}"
        })
        return 0, None

res = check_report_exists()
if isinstance(res, tuple):
    score_part, report = res
    total_score += score_part
else:
    total_score += res
    report = None

# 3. 字段完整性 (10分) - 要求只包含这5个字段，无多余
if report is not None:
    required_fields = ["fault_id", "root_cause", "repair_plan", "affected_services", "related_knowledge_entry_ids"]
    report_keys = set(report.keys())
    required_set = set(required_fields)
    max_score = 10
    if report_keys == required_set:
        score_details.append({
            "item": "Field completeness",
            "score": max_score,
            "max_score": max_score,
            "passed": True,
            "reason": "All required fields present, no extra fields"
        })
        total_score += max_score
    elif required_set.issubset(report_keys):
        extras = report_keys - required_set
        if extras:
            score_details.append({
                "item": "Field completeness",
                "score": 5,
                "max_score": max_score,
                "passed": False,
                "reason": f"Extra fields found: {extras}"
            })
            total_score += 5
        else:
            # 缺少字段
            missing = required_set - report_keys
            score_details.append({
                "item": "Field completeness",
                "score": 0,
                "max_score": max_score,
                "passed": False,
                "reason": f"Missing fields: {missing}"
            })
    else:
        score_details.append({
            "item": "Field completeness",
            "score": 0,
            "max_score": max_score,
            "passed": False,
            "reason": "Required fields not fully present"
        })

    # 4. 精确值检查 (70分)
    # fault_id 精确匹配 (10分)
    expected_fault_id = "fc_001"
    if report.get("fault_id") == expected_fault_id:
        score_details.append({
            "item": "fault_id",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"fault_id is '{expected_fault_id}'"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "fault_id",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Expected '{expected_fault_id}', got '{report.get('fault_id')}'"
        })

    # root_cause 精确匹配 (20分)
    expected_root_cause = "Database connection pool exhaustion"
    if report.get("root_cause") == expected_root_cause:
        score_details.append({
            "item": "root_cause",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "root_cause matches expected"
        })
        total_score += 20
    else:
        score_details.append({
            "item": "root_cause",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"Expected '{expected_root_cause}', got '{report.get('root_cause')}'"
        })

    # repair_plan 精确匹配 (20分)
    expected_repair_plan = "Increase max_connections and reduce timeout"
    if report.get("repair_plan") == expected_repair_plan:
        score_details.append({
            "item": "repair_plan",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "repair_plan matches expected"
        })
        total_score += 20
    else:
        score_details.append({
            "item": "repair_plan",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"Expected '{expected_repair_plan}', got '{report.get('repair_plan')}'"
        })

    # affected_services 必须包含两个服务，顺序无关 (10分)
    expected_services = {"api-gateway", "user-service"}
    actual_services = set(report.get("affected_services", []))
    if actual_services == expected_services:
        score_details.append({
            "item": "affected_services",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "affected_services contains exactly api-gateway and user-service"
        })
        total_score += 10
    elif expected_services.issubset(actual_services):
        extra = actual_services - expected_services
        score_details.append({
            "item": "affected_services",
            "score": 5,
            "max_score": 10,
            "passed": False,
            "reason": f"Extra services: {extra}"
        })
        total_score += 5
    else:
        missing = expected_services - actual_services
        score_details.append({
            "item": "affected_services",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Missing services: {missing}"
        })

    # related_knowledge_entry_ids 必须包含 ke_001 (10分)
    expected_entry_ids = ["ke_001"]
    actual_ids = report.get("related_knowledge_entry_ids", [])
    if isinstance(actual_ids, list) and expected_entry_ids == actual_ids:
        score_details.append({
            "item": "related_knowledge_entry_ids",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Contains exactly ['ke_001']"
        })
        total_score += 10
    elif isinstance(actual_ids, list) and "ke_001" in actual_ids:
        score_details.append({
            "item": "related_knowledge_entry_ids",
            "score": 5,
            "max_score": 10,
            "passed": False,
            "reason": f"Contains ke_001 but extra entries: {actual_ids}"
        })
        total_score += 5
    else:
        score_details.append({
            "item": "related_knowledge_entry_ids",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Expected ['ke_001'], got {actual_ids}"
        })
else:
    # 如果报告不存在，其他项自动0分
    pass

# 输出结果
result = {
    "total_score": min(total_score, 100),
    "details": score_details
}
with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
    json.dump(result, f, indent=2)
print(json.dumps(result, indent=2))
