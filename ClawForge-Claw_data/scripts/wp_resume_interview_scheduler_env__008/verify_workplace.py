import json
import os
import sys

def verify(workspace: str):
    results = []
    total_score = 0

    # 1. 检查 ops 目录和 target 文件存在
    ops_dir = os.path.join(workspace, "ops")
    target_path = os.path.join(ops_dir, "interview_schedule.json")
    if os.path.isdir(ops_dir) and os.path.isfile(target_path):
        results.append({"item": "ops/interview_schedule.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "File found."})
        total_score += 10
    else:
        results.append({"item": "ops/interview_schedule.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "File missing."})

    # 2. 解析 JSON
    if os.path.isfile(target_path):
        try:
            with open(target_path, "r") as f:
                data = json.load(f)
            if isinstance(data, list):
                results.append({"item": "JSON is a list", "score": 10, "max_score": 10, "passed": True, "reason": "Valid JSON array."})
                total_score += 10
            else:
                results.append({"item": "JSON is a list", "score": 0, "max_score": 10, "passed": False, "reason": f"Root is {type(data).__name__}, expected list."})
        except (json.JSONDecodeError, Exception) as e:
            results.append({"item": "JSON is a list", "score": 0, "max_score": 10, "passed": False, "reason": f"Invalid JSON: {str(e)}"})
            data = None
    else:
        data = None
        results.append({"item": "JSON is a list", "score": 0, "max_score": 10, "passed": False, "reason": "File not available for parsing."})

    # 3. 检查字段存在性和记录数
    if data is not None and isinstance(data, list):
        # 检查记录数
        if len(data) == 3:
            results.append({"item": "Number of interview records", "score": 10, "max_score": 10, "passed": True, "reason": "Exactly 3 records found."})
            total_score += 10
        else:
            results.append({"item": "Number of interview records", "score": 0, "max_score": 10, "passed": False, "reason": f"Found {len(data)} records, expected 3."})

        # 检查每个记录的字段完整性和 reminder 默认值
        field_ok = True
        for idx, rec in enumerate(data):
            required_fields = ["candidate_id", "job_id", "scheduled_date", "reminder_minutes_before"]
            for fld in required_fields:
                if fld not in rec:
                    field_ok = False
                    results.append({"item": f"Record {idx+1} field '{fld}'", "score": 0, "max_score": 2.5, "passed": False, "reason": "Missing field."})
                    total_score += 0
                elif fld == "reminder_minutes_before" and rec[fld] != 30:
                    field_ok = False
                    results.append({"item": f"Record {idx+1} field '{fld}'", "score": 0, "max_score": 2.5, "passed": False, "reason": f"Value {rec[fld]}, expected 30."})
                    total_score += 0
                else:
                    # 每个字段满分2.5，如果通过则累计
                    pass  # 稍后统一加
        if field_ok:
            # 如果所有字段都正确且 reminder 为30，给10分
            results.append({"item": "All records have required fields and reminder=30", "score": 10, "max_score": 10, "passed": True, "reason": "Fields valid."})
            total_score += 10
        else:
            # 已经记录了个别缺失，这里不再重复加分
            if not any(r["item"].startswith("Record") for r in results):
                results.append({"item": "All records have required fields and reminder=30", "score": 0, "max_score": 10, "passed": False, "reason": "Field validation failed."})

        # 4. 精确检查三条记录 (每个20分)
        expected_records = [
            {"candidate_id": "cand_4", "job_id": "job_A", "scheduled_date": "2025-04-15", "reminder_minutes_before": 30},
            {"candidate_id": "cand_2", "job_id": "job_B", "scheduled_date": "2025-04-14", "reminder_minutes_before": 30},
            {"candidate_id": "cand_3", "job_id": "job_C", "scheduled_date": "2025-04-15", "reminder_minutes_before": 30}
        ]
        for exp in expected_records:
            found = False
            for rec in data:
                if rec.get("candidate_id") == exp["candidate_id"] and rec.get("job_id") == exp["job_id"]:
                    found = True
                    if (rec.get("scheduled_date") == exp["scheduled_date"] and 
                        rec.get("reminder_minutes_before") == exp["reminder_minutes_before"]):
                        results.append({"item": f"Record for {exp['candidate_id']}/{exp['job_id']} correct", "score": 20, "max_score": 20, "passed": True, "reason": "Exact match."})
                        total_score += 20
                    else:
                        # 部分正确：candidate_id 和 job_id 正确，日期或提醒不对
                        score = 10
                        results.append({"item": f"Record for {exp['candidate_id']}/{exp['job_id']} partially correct", "score": score, "max_score": 20, "passed": False, "reason": f"Expected {exp}, got {rec}"})
                        total_score += score
                    break
            if not found:
                results.append({"item": f"Record for {exp['candidate_id']}/{exp['job_id']} missing", "score": 0, "max_score": 20, "passed": False, "reason": "Not found."})

        # 5. 检查是否包含了 closed 职位的安排（扣分项）
        for rec in data:
            if rec.get("job_id") == "job_D":
                results.append({"item": "No closed job (job_D) included", "score": -10, "max_score": 0, "passed": False, "reason": "job_D is closed but was scheduled."})
                total_score -= 10

        # 6. 检查是否包含了已有面试的候选人（cand_1）的新安排
        for rec in data:
            if rec.get("candidate_id") == "cand_1":
                results.append({"item": "No duplicate interview for cand_1", "score": -10, "max_score": 0, "passed": False, "reason": "cand_1 already has an interview."})
                total_score -= 10
    else:
        # 如果 data 不是列表，直接给剩余项目0分
        results.append({"item": "Number of interview records", "score": 0, "max_score": 10, "passed": False, "reason": "Data not available."})
        results.append({"item": "All records have required fields and reminder=30", "score": 0, "max_score": 10, "passed": False, "reason": "Data not available."})
        for exp in expected_records:
            results.append({"item": f"Record for {exp['candidate_id']}/{exp['job_id']} correct", "score": 0, "max_score": 20, "passed": False, "reason": "Data not available."})

    # 确保总分在0-100之间
    total_score = max(0, min(100, total_score))

    # 写入报告
    report = {
        "total_score": total_score,
        "details": results
    }
    report_path = os.path.join(workspace, "workplace_score.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"Verification complete. Score: {total_score}/100")

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
