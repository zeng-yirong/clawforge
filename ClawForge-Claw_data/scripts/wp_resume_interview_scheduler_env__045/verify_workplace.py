import json
import os
import sys
from datetime import datetime, timedelta

def verify(workspace: str):
    score_details = []
    total_score = 0

    # 1. 检查 data/schedules 目录是否存在 (10分)
    schedules_dir = os.path.join(workspace, "data", "schedules")
    if os.path.isdir(schedules_dir):
        score_details.append({
            "item": "data/schedules 目录存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "目录已创建"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "data/schedules 目录存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "目录不存在"
        })

    # 2. 检查 new_interview.json 是否存在 (10分)
    target_file = os.path.join(schedules_dir, "new_interview.json")
    if os.path.isfile(target_file):
        score_details.append({
            "item": "new_interview.json 文件存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "文件已创建"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "new_interview.json 文件存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件不存在"
        })
        # 如果文件不存在，后续检查无法进行，直接返回
        write_score(score_details, total_score)
        return

    # 3. 读取 JSON 并检查合法性 (10分)
    try:
        with open(target_file, "r") as f:
            data = json.load(f)
        score_details.append({
            "item": "JSON 格式合法",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "JSON 解析成功"
        })
        total_score += 10
    except (json.JSONDecodeError, Exception) as e:
        score_details.append({
            "item": "JSON 格式合法",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON 解析失败: {str(e)}"
        })
        write_score(score_details, total_score)
        return

    # 4. 检查必需的字段 (20分)
    required_fields = ["candidate_id", "job_id", "interview_date", "status"]
    missing_fields = [f for f in required_fields if f not in data]
    if not missing_fields:
        score_details.append({
            "item": "字段完整性 (candidate_id, job_id, interview_date, status)",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "所有必需字段均存在"
        })
        total_score += 20
    else:
        score_details.append({
            "item": "字段完整性",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"缺少字段: {', '.join(missing_fields)}"
        })

    # 5. 检查 candidate_id 是否为 C003 (20分)
    if data.get("candidate_id") == "C003":
        score_details.append({
            "item": "candidate_id 正确",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "候选人为 Carol Zhang"
        })
        total_score += 20
    else:
        score_details.append({
            "item": "candidate_id 正确",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"实际为 {data.get('candidate_id')}，期望 C003"
        })

    # 6. 检查 job_id 是否为 J001 (10分)
    if data.get("job_id") == "J001":
        score_details.append({
            "item": "job_id 正确",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "职位为 Senior DevOps Engineer"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "job_id 正确",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"实际为 {data.get('job_id')}，期望 J001"
        })

    # 7. 检查 interview_date 是否为 2025-04-10 (10分)
    expected_date = "2025-04-10"  # 与 today.txt 中的 2025-04-09 对应
    actual_date = data.get("interview_date")
    if actual_date == expected_date:
        score_details.append({
            "item": "interview_date 正确 (明天日期)",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"日期为 {expected_date}"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "interview_date 正确",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"实际为 {actual_date}，期望 {expected_date}"
        })

    # 8. 检查 status 是否为 "scheduled" (10分)
    if data.get("status") == "scheduled":
        score_details.append({
            "item": "status 正确",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "状态为 scheduled"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "status 正确",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"实际为 {data.get('status')}，期望 scheduled"
        })

    # 写入评分结果
    write_score(score_details, total_score)

def write_score(details, total):
    result = {
        "total_score": total,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
