import json
import os
import sys
import re

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results = []
    total_score = 0

    # 1. 检查 schedule/interviews.json 是否存在 (10分)
    schedule_path = os.path.join(workspace, "schedule", "interviews.json")
    if os.path.isfile(schedule_path):
        results.append({
            "item": "schedule/interviews.json 文件存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "文件存在"
        })
        total_score += 10
    else:
        results.append({
            "item": "schedule/interviews.json 文件存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件不存在"
        })
        # 后续检查无意义，提前输出
        _write_score(total_score, results)
        return

    # 2. 解析 JSON 合法性 (10分)
    try:
        with open(schedule_path, "r") as f:
            data = json.load(f)
        results.append({
            "item": "JSON 格式正确",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "可正常解析"
        })
        total_score += 10
    except (json.JSONDecodeError, Exception) as e:
        results.append({
            "item": "JSON 格式正确",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"解析失败: {str(e)}"
        })
        _write_score(total_score, results)
        return

    # 3. 检查 interviews 键存在且为列表 (10分)
    if "interviews" not in data or not isinstance(data["interviews"], list):
        results.append({
            "item": "interviews 字段存在且为列表",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "缺少 interviews 字段或不是列表"
        })
        _write_score(total_score, results)
        return
    else:
        results.append({
            "item": "interviews 字段存在且为列表",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"包含 {len(data['interviews'])} 个面试安排"
        })
        total_score += 10

    # 4. 面试安排数量必须为1 (10分)
    if len(data["interviews"]) != 1:
        results.append({
            "item": "仅安排一场面试",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"期望1场，实际{len(data['interviews'])}场"
        })
        _write_score(total_score, results)
        return
    else:
        results.append({
            "item": "仅安排一场面试",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "面试安排数量为1"
        })
        total_score += 10

    interview = data["interviews"][0]

    # 5. 检查 candidate_id 正确性 (20分)
    if interview.get("candidate_id") == "candidate_001":
        results.append({
            "item": "候选人 ID 正确 (candidate_001)",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "选择了最匹配的 Alice Wang"
        })
        total_score += 20
    else:
        results.append({
            "item": "候选人 ID 正确 (candidate_001)",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"实际为 {interview.get('candidate_id', '无')}，期望 candidate_001"
        })

    # 6. 检查 job_id 正确性 (15分)
    if interview.get("job_id") == "job_001":
        results.append({
            "item": "职位 ID 正确 (job_001)",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": "对应 Software Engineer 岗位"
        })
        total_score += 15
    else:
        results.append({
            "item": "职位 ID 正确 (job_001)",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": f"实际为 {interview.get('job_id', '无')}，期望 job_001"
        })

    # 7. 检查 scheduled_time 正确 (15分)
    expected_time = "2025-03-20T09:00:00"
    actual_time = interview.get("scheduled_time", "")
    if actual_time == expected_time:
        results.append({
            "item": "面试时间正确 (2025-03-20T09:00:00)",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": "时间与要求一致"
        })
        total_score += 15
    else:
        results.append({
            "item": "面试时间正确 (2025-03-20T09:00:00)",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": f"实际为 '{actual_time}'，期望 '{expected_time}'"
        })

    # 8. 检查 reminder 为 true (10分)
    if interview.get("reminder") is True:
        results.append({
            "item": "提醒标识为 true",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "已设置提醒"
        })
        total_score += 10
    else:
        results.append({
            "item": "提醒标识为 true",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"实际为 {interview.get('reminder')}，期望 true"
        })

    _write_score(total_score, results)

def _write_score(total, details):
    result = {
        "total_score": total,
        "details": details
    }
    score_path = os.path.join(os.getcwd(), "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written: {total}/100")

if __name__ == "__main__":
    main()
