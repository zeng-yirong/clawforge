import sys
import os
import json

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    # 1. 检查 schedules/ 目录是否存在
    sched_dir = os.path.join(workspace, "schedules")
    dir_exists = os.path.isdir(sched_dir)
    if dir_exists:
        score += 10
        details.append({"item": "schedules/ directory", "score": 10, "max_score": 10, "passed": True, "reason": "Directory exists."})
    else:
        details.append({"item": "schedules/ directory", "score": 0, "max_score": 10, "passed": False, "reason": "Directory not found."})

    # 2. 检查 interview_plan.json 是否存在
    plan_path = os.path.join(sched_dir, "interview_plan.json")
    file_exists = os.path.isfile(plan_path)
    if file_exists:
        score += 10
        details.append({"item": "interview_plan.json file", "score": 10, "max_score": 10, "passed": True, "reason": "File exists."})
    else:
        details.append({"item": "interview_plan.json file", "score": 0, "max_score": 10, "passed": False, "reason": "File not found."})
        # 如果文件不存在，提前返回
        total = score
        result = {"total_score": total, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # 3. JSON 格式合法性
    try:
        data = load_json(plan_path)
        score += 10
        details.append({"item": "JSON format valid", "score": 10, "max_score": 10, "passed": True, "reason": "Valid JSON."})
    except Exception as e:
        details.append({"item": "JSON format valid", "score": 0, "max_score": 10, "passed": False, "reason": f"Invalid JSON: {e}"})
        total = score
        result = {"total_score": total, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # 4. 必须字段检查
    required_fields = ["job_id", "candidate_id", "scheduled_time", "interviewer", "reminder", "reminder_minutes"]
    field_score = 0
    for field in required_fields:
        if field in data:
            field_score += 3  # 每个字段3分，共18分，取整
        else:
            details.append({"item": f"Field '{field}' present", "score": 0, "max_score": 3, "passed": False, "reason": f"Missing field: {field}"})
    if field_score == 18:
        details.append({"item": "All required fields present", "score": 18, "max_score": 18, "passed": True, "reason": "All fields found."})
    else:
        # 已经添加了缺失字段的详细条目，这里再汇总
        details.append({"item": "All required fields present", "score": field_score, "max_score": 18, "passed": field_score==18, "reason": f"Got {field_score}/18 fields"})
    score += field_score

    # 5. job_id 值检查
    if data.get("job_id") == "JOB-003":
        score += 10
        details.append({"item": "job_id correct", "score": 10, "max_score": 10, "passed": True, "reason": "Value is JOB-003."})
    else:
        details.append({"item": "job_id correct", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected JOB-003, got {data.get('job_id')}"})

    # 6. candidate_id 值检查（核心）
    if data.get("candidate_id") == "C001":
        score += 20
        details.append({"item": "candidate_id correct", "score": 20, "max_score": 20, "passed": True, "reason": "Value is C001 (only active candidate with all required skills)."})
    else:
        details.append({"item": "candidate_id correct", "score": 0, "max_score": 20, "passed": False, "reason": f"Expected C001, got {data.get('candidate_id')}"})

    # 7. scheduled_time 检查
    expected_time = "2025-03-21T15:00:00"
    if data.get("scheduled_time") == expected_time:
        score += 10
        details.append({"item": "scheduled_time correct", "score": 10, "max_score": 10, "passed": True, "reason": f"Matches {expected_time}."})
    else:
        details.append({"item": "scheduled_time correct", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected {expected_time}, got {data.get('scheduled_time')}"})

    # 8. interviewer 检查
    if data.get("interviewer") == "CONT-001":
        score += 5
        details.append({"item": "interviewer correct", "score": 5, "max_score": 5, "passed": True, "reason": "Value is CONT-001."})
    else:
        details.append({"item": "interviewer correct", "score": 0, "max_score": 5, "passed": False, "reason": f"Expected CONT-001, got {data.get('interviewer')}"})

    # 9. reminder 布尔检查
    reminder = data.get("reminder")
    if reminder is True:
        score += 5
        details.append({"item": "reminder set to true", "score": 5, "max_score": 5, "passed": True, "reason": "reminder is true."})
    else:
        details.append({"item": "reminder set to true", "score": 0, "max_score": 5, "passed": False, "reason": f"Expected true, got {reminder}"})

    # 10. reminder_minutes 检查
    rmin = data.get("reminder_minutes")
    if rmin == 15:
        score += 2
        details.append({"item": "reminder_minutes correct", "score": 2, "max_score": 2, "passed": True, "reason": "Value is 15."})
    else:
        details.append({"item": "reminder_minutes correct", "score": 0, "max_score": 2, "passed": False, "reason": f"Expected 15, got {rmin}"})

    # 汇总总分
    total_score = min(score, 100)  # 确保不超过100
    result = {"total_score": total_score, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    verify()
