import sys
import json
import os
from pathlib import Path

def verify(workspace: str) -> dict:
    ws = Path(workspace)
    details = []
    total_score = 0
    max_total = 100

    # 1. 目录结构存在性 (10分)
    score_dir = 0
    max_dir = 10
    dirs_required = ["ops", "data/candidates", "data/jobs"]
    all_dirs_ok = all((ws / d).is_dir() for d in dirs_required)
    if all_dirs_ok:
        score_dir = max_dir
        details.append({"item": "目录结构", "score": max_dir, "max_score": max_dir,
                        "passed": True, "reason": "所有必要目录存在"})
    else:
        missing = [d for d in dirs_required if not (ws / d).is_dir()]
        details.append({"item": "目录结构", "score": 0, "max_score": max_dir,
                        "passed": False, "reason": f"缺少目录: {missing}"})
    total_score += score_dir

    # 2. 产物文件存在且合法JSON (10分)
    result_file = ws / "ops" / "scheduled_interviews.json"
    score_json = 0
    max_json = 10
    if result_file.is_file():
        try:
            with open(result_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            score_json = max_json
            details.append({"item": "产物JSON合法性", "score": max_json, "max_score": max_json,
                            "passed": True, "reason": "文件存在且JSON解析成功"})
        except (json.JSONDecodeError, Exception) as e:
            details.append({"item": "产物JSON合法性", "score": 0, "max_score": max_json,
                            "passed": False, "reason": f"JSON解析失败: {e}"})
    else:
        details.append({"item": "产物JSON合法性", "score": 0, "max_score": max_json,
                        "passed": False, "reason": "ops/scheduled_interviews.json 不存在"})
    total_score += score_json

    # 3. 内容格式检查：必须是一个数组，且长度=1 (10分)
    score_array = 0
    max_array = 10
    if score_json > 0:
        if isinstance(data, list) and len(data) == 1:
            score_array = max_array
            details.append({"item": "产物格式", "score": max_array, "max_score": max_array,
                            "passed": True, "reason": "数组长度正确"})
        elif isinstance(data, list) and len(data) != 1:
            details.append({"item": "产物格式", "score": 0, "max_score": max_array,
                            "passed": False, "reason": f"数组长度为{len(data)}，期望1"})
        else:
            details.append({"item": "产物格式", "score": 0, "max_score": max_array,
                            "passed": False, "reason": "不是数组格式"})
    else:
        details.append({"item": "产物格式", "score": 0, "max_score": max_array,
                        "passed": False, "reason": "前一检查未通过"})
    total_score += score_array

    # 4. 字段完整性 (20分) - 必须有candidate_id, job_id, interviewer, time
    score_fields = 0
    max_fields = 20
    required_fields = {"candidate_id", "job_id", "interviewer", "time"}
    if score_array > 0:
        record = data[0]
        present = set(record.keys())
        if required_fields.issubset(present):
            score_fields = max_fields
            details.append({"item": "字段完整性", "score": max_fields, "max_score": max_fields,
                            "passed": True, "reason": "包含所有必需字段"})
        else:
            missing_f = required_fields - present
            details.append({"item": "字段完整性", "score": 0, "max_score": max_fields,
                            "passed": False, "reason": f"缺少字段: {missing_f}"})
    else:
        details.append({"item": "字段完整性", "score": 0, "max_score": max_fields,
                        "passed": False, "reason": "前序检查未通过"})
    total_score += score_fields

    # 5. candidate_id 正确 (20分)
    score_candidate = 0
    max_candidate = 20
    if score_fields > 0 and "candidate_id" in data[0]:
        if data[0]["candidate_id"] == "C002":
            score_candidate = max_candidate
            details.append({"item": "候选人ID", "score": max_candidate, "max_score": max_candidate,
                            "passed": True, "reason": "正确选择C002"})
        else:
            details.append({"item": "候选人ID", "score": 0, "max_score": max_candidate,
                            "passed": False, "reason": f"值为 {data[0]['candidate_id']}，期望 C002"})
    else:
        details.append({"item": "候选人ID", "score": 0, "max_score": max_candidate,
                        "passed": False, "reason": "字段缺失"})
    total_score += score_candidate

    # 6. job_id 正确 (15分)
    score_job = 0
    max_job = 15
    if score_fields > 0 and "job_id" in data[0]:
        if data[0]["job_id"] == "J001":
            score_job = max_job
            details.append({"item": "职位ID", "score": max_job, "max_score": max_job,
                            "passed": True, "reason": "正确选择J001"})
        else:
            details.append({"item": "职位ID", "score": 0, "max_score": max_job,
                            "passed": False, "reason": f"值为 {data[0]['job_id']}，期望 J001"})
    else:
        details.append({"item": "职位ID", "score": 0, "max_score": max_job,
                        "passed": False, "reason": "字段缺失"})
    total_score += score_job

    # 7. interviewer 正确 (10分)
    score_interviewer = 0
    max_interviewer = 10
    if score_fields > 0 and "interviewer" in data[0]:
        if data[0]["interviewer"] == "contact_001":
            score_interviewer = max_interviewer
            details.append({"item": "面试官ID", "score": max_interviewer, "max_score": max_interviewer,
                            "passed": True, "reason": "正确选择contact_001"})
        else:
            details.append({"item": "面试官ID", "score": 0, "max_score": max_interviewer,
                            "passed": False, "reason": f"值为 {data[0]['interviewer']}，期望 contact_001"})
    else:
        details.append({"item": "面试官ID", "score": 0, "max_score": max_interviewer,
                        "passed": False, "reason": "字段缺失"})
    total_score += score_interviewer

    # 8. time 正确 (15分)
    score_time = 0
    max_time = 15
    if score_fields > 0 and "time" in data[0]:
        if data[0]["time"] == "2025-04-15T10:00" or data[0]["time"] == "2025-04-15T10:00:00":
            score_time = max_time
            details.append({"item": "面试时间", "score": max_time, "max_score": max_time,
                            "passed": True, "reason": "时间正确"})
        else:
            details.append({"item": "面试时间", "score": 0, "max_score": max_time,
                            "passed": False, "reason": f"值为 {data[0]['time']}，期望 2025-04-15T10:00"})
    else:
        details.append({"item": "面试时间", "score": 0, "max_score": max_time,
                        "passed": False, "reason": "字段缺失"})
    total_score += score_time

    # 额外扣分：如果结果中有多余字段（超出4个必需字段），扣5分
    extra_deduct = 5
    if score_fields > 0:
        extra_fields = set(data[0].keys()) - required_fields
        if extra_fields:
            total_score -= extra_deduct
            details.append({"item": "多余字段扣分", "score": -extra_deduct, "max_score": 0,
                            "passed": False, "reason": f"发现多余字段: {extra_fields}"})
            if total_score < 0:
                total_score = 0

    return {
        "total_score": total_score,
        "details": details
    }

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    # 写入结果
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Verify completed. Score: {result['total_score']}")
