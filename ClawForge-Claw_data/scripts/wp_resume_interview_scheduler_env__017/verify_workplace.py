#!/usr/bin/env python3
"""纯代码客观验证：检查 ops/interview_schedule.json 是否匹配唯一正确答案"""
import sys
import json
import os
from pathlib import Path

def verify(workspace: str) -> dict:
    ws = Path(workspace)
    details = []
    total_score = 0
    max_total = 100

    # 预期唯一答案
    expected_candidate_id = "cand_001"
    expected_job_id = "job_002"
    expected_interview_time = "2025-06-15T10:00:00"

    # 1. 文件存在性 (10分)
    file_path = ws / "ops" / "interview_schedule.json"
    if file_path.exists():
        details.append({"item": "文件存在", "score": 10, "max_score": 10, "passed": True, "reason": "ops/interview_schedule.json 存在"})
        total_score += 10
    else:
        details.append({"item": "文件存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        # 文件不存在则后续无法验证，直接返回
        return {"total_score": total_score, "details": details}

    # 2. 格式合法性 (10分)
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        details.append({"item": "JSON格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "可正常解析"})
        total_score += 10
    except Exception as e:
        details.append({"item": "JSON格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {str(e)}"})
        return {"total_score": total_score, "details": details}

    # 3. 必需字段完整性 (20分，每个字段5分)
    required_fields = ["candidate_id", "job_id", "interview_time"]
    fields_ok = True
    for field in required_fields:
        if field in data:
            details.append({"item": f"字段 '{field}' 存在", "score": 5, "max_score": 5, "passed": True, "reason": f"包含字段 {field}"})
            total_score += 5
        else:
            details.append({"item": f"字段 '{field}' 存在", "score": 0, "max_score": 5, "passed": False, "reason": f"缺少字段 {field}"})
            fields_ok = False
    # 如果缺少关键字段则终止，避免后续错误
    if not fields_ok:
        return {"total_score": total_score, "details": details}

    # 4. candidate_id 正确性 (30分)
    if data["candidate_id"] == expected_candidate_id:
        details.append({"item": "候选人匹配", "score": 30, "max_score": 30, "passed": True, "reason": f"选择的候选人是 {expected_candidate_id}"})
        total_score += 30
    else:
        details.append({"item": "候选人匹配", "score": 0, "max_score": 30, "passed": False, "reason": f"实际为 {data['candidate_id']}，应为 {expected_candidate_id}"})

    # 5. job_id 正确性 (20分)
    if data["job_id"] == expected_job_id:
        details.append({"item": "职位匹配", "score": 20, "max_score": 20, "passed": True, "reason": f"选择的职位是 {expected_job_id}"})
        total_score += 20
    else:
        details.append({"item": "职位匹配", "score": 0, "max_score": 20, "passed": False, "reason": f"实际为 {data['job_id']}，应为 {expected_job_id}"})

    # 6. interview_time 正确性 (10分)
    if data["interview_time"] == expected_interview_time:
        details.append({"item": "面试时间正确", "score": 10, "max_score": 10, "passed": True, "reason": f"时间 {expected_interview_time}"})
        total_score += 10
    else:
        details.append({"item": "面试时间正确", "score": 0, "max_score": 10, "passed": False, "reason": f"实际为 {data.get('interview_time', 'N/A')}，应为 {expected_interview_time}"})

    return {"total_score": total_score, "details": details}


if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score: {result['total_score']}/100")
