import json
import os
import sys

def verify(workspace: str):
    score = 0
    details = []

    # ------------------------------------------------------------------------
    # 1. 检查输出文件是否存在 (10分)
    # ------------------------------------------------------------------------
    out_path = os.path.join(workspace, "ops/interview_plan.json")
    if not os.path.isfile(out_path):
        details.append({
            "item": "Output file ops/interview_plan.json exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not found."
        })
        # 如果文件不存在，后面没有检查的必要，直接返回
        result = {"total_score": 0, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    details.append({
        "item": "Output file ops/interview_plan.json exists",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "File found."
    })
    score += 10

    # ------------------------------------------------------------------------
    # 2. 文件内容是否合法 JSON (10分)
    # ------------------------------------------------------------------------
    try:
        with open(out_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        details.append({
            "item": "Content is valid JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON decode error: {e}"
        })
        result = {"total_score": score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    details.append({
        "item": "Content is valid JSON",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "Valid JSON."
    })
    score += 10

    # ------------------------------------------------------------------------
    # 3. 检查数据结构：必须是一个列表，且长度正确 (10分)
    # ------------------------------------------------------------------------
    if not isinstance(data, list):
        details.append({
            "item": "Data is a list",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Top-level structure is not a list."
        })
        result = {"total_score": score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    expected_count = 3  # 三个活跃职位分别匹配一个候选人
    actual_count = len(data)
    if actual_count != expected_count:
        details.append({
            "item": f"List length is {expected_count}",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Expected {expected_count} entries, got {actual_count}."
        })
        result = {"total_score": score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    details.append({
        "item": f"List length is {expected_count}",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": f"Exactly {expected_count} entries."
    })
    score += 10

    # ------------------------------------------------------------------------
    # 4. 必备字段是否存在且准确 (50分, 细分为字段完整性20 + 值正确30)
    # ------------------------------------------------------------------------
    required_fields = ["job_id", "candidate_id", "interviewer_id",
                       "interview_time", "reminder_time", "status"]

    # 4a. 每一条记录都有所有字段 (20分)
    fields_ok = True
    for idx, rec in enumerate(data):
        for field in required_fields:
            if field not in rec:
                fields_ok = False
                break
        if not fields_ok:
            break

    if not fields_ok:
        details.append({
            "item": "Each entry has all required fields",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"Missing required field in entry {idx}."
        })
        result = {"total_score": score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    details.append({
        "item": "Each entry has all required fields",
        "score": 20,
        "max_score": 20,
        "passed": True,
        "reason": "All entries contain job_id, candidate_id, interviewer_id, interview_time, reminder_time, status."
    })
    score += 20

    # 4b. 具体值正确性 (30分)
    # 按 job_id 排序后比较唯一答案
    sorted_data = sorted(data, key=lambda x: x["job_id"])
    expected = [
        {
            "job_id": "J001",
            "candidate_id": "C001",
            "interviewer_id": "int1",
            "interview_time": "2025-04-15T10:00:00",
            "reminder_time": "2025-04-15T09:30:00",
            "status": "scheduled"
        },
        {
            "job_id": "J002",
            "candidate_id": "C002",
            "interviewer_id": "int1",
            "interview_time": "2025-04-15T10:00:00",
            "reminder_time": "2025-04-15T09:30:00",
            "status": "scheduled"
        },
        {
            "job_id": "J003",
            "candidate_id": "C004",
            "interviewer_id": "int1",
            "interview_time": "2025-04-15T10:00:00",
            "reminder_time": "2025-04-15T09:30:00",
            "status": "scheduled"
        }
    ]

    value_match = True
    mismatch_reason = []
    for i, (exp, act) in enumerate(zip(expected, sorted_data)):
        for key in exp:
            if act.get(key) != exp[key]:
                value_match = False
                mismatch_reason.append(
                    f"Entry for job_id {exp['job_id']}: field '{key}' expected '{exp[key]}', got '{act.get(key)}'."
                )
    if not value_match:
        reason_str = "; ".join(mismatch_reason)
        details.append({
            "item": "All field values match expected answer",
            "score": 0,
            "max_score": 30,
            "passed": False,
            "reason": reason_str
        })
        result = {"total_score": score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    details.append({
        "item": "All field values match expected answer",
        "score": 30,
        "max_score": 30,
        "passed": True,
        "reason": "All values exactly match the unique correct answer."
    })
    score += 30

    # ------------------------------------------------------------------------
    # 5. 排序检查：job_id 升序 (10分)
    # ------------------------------------------------------------------------
    job_ids = [rec["job_id"] for rec in data]
    if job_ids == sorted(job_ids):
        details.append({
            "item": "Entries sorted by job_id in ascending order",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"Order: {job_ids}"
        })
        score += 10
    else:
        details.append({
            "item": "Entries sorted by job_id in ascending order",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Order is {job_ids}, expected sorted ascending."
        })

    # ------------------------------------------------------------------------
    # 总分
    # ------------------------------------------------------------------------
    final_score = min(score, 100)  # 理论上最大100
    result = {"total_score": final_score, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

    print(f"Verification done: total_score = {final_score}")


if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
