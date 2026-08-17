import sys
import os
import json

def verify(workspace):
    details = []
    total_score = 0

    # 1. 检查 ops 目录是否存在
    ops_path = os.path.join(workspace, "ops")
    if os.path.isdir(ops_path):
        details.append({
            "item": "ops 目录存在",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "ops 目录已创建"
        })
        total_score += 5
    else:
        details.append({
            "item": "ops 目录存在",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "ops 目录不存在"
        })

    # 2. 检查 interview_invite.json 是否存在
    invite_path = os.path.join(workspace, "ops", "interview_invite.json")
    if os.path.isfile(invite_path):
        details.append({
            "item": "interview_invite.json 文件存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "文件已创建"
        })
        total_score += 10
    else:
        details.append({
            "item": "interview_invite.json 文件存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件不存在"
        })
        # 后续检查无法进行，返回当前得分
        write_score(details, total_score)
        return

    # 3. 检查 JSON 合法性
    try:
        with open(invite_path, "r") as f:
            data = json.load(f)
        details.append({
            "item": "JSON 格式合法",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "可正常解析"
        })
        total_score += 10
    except (json.JSONDecodeError, IOError) as e:
        details.append({
            "item": "JSON 格式合法",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"解析失败: {str(e)}"
        })
        write_score(details, total_score)
        return

    # 4. 检查必需字段
    required_fields = ["candidate_id", "job_id", "scheduled_time", "location", "notes"]
    missing = [f for f in required_fields if f not in data]
    if not missing:
        details.append({
            "item": "包含所有必需字段 (candidate_id, job_id, scheduled_time, location, notes)",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": "所有字段存在"
        })
        total_score += 15
    else:
        details.append({
            "item": "包含所有必需字段",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": f"缺少字段: {missing}"
        })
        write_score(details, total_score)
        return

    # 5. 检查 candidate_id 正确值
    if data["candidate_id"] == "alice_001":
        details.append({
            "item": "candidate_id 正确 (alice_001)",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "值匹配"
        })
        total_score += 20
    else:
        details.append({
            "item": "candidate_id 正确",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"期望 alice_001，实际 {data['candidate_id']}"
        })

    # 6. 检查 job_id 正确值
    if data["job_id"] == "job_001":
        details.append({
            "item": "job_id 正确 (job_001)",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "值匹配"
        })
        total_score += 20
    else:
        details.append({
            "item": "job_id 正确",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"期望 job_001，实际 {data['job_id']}"
        })

    # 7. 检查 scheduled_time 正确值
    expected_time = "2025-03-11T14:00:00"
    if data["scheduled_time"] == expected_time:
        details.append({
            "item": "scheduled_time 正确 (2025-03-11T14:00:00)",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "值匹配"
        })
        total_score += 10
    else:
        details.append({
            "item": "scheduled_time 正确",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"期望 {expected_time}，实际 {data['scheduled_time']}"
        })

    # 8. 检查 location 正确值
    if data["location"] == "Room 301":
        details.append({
            "item": "location 正确 (Room 301)",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "值匹配"
        })
        total_score += 5
    else:
        details.append({
            "item": "location 正确",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": f"期望 Room 301，实际 {data['location']}"
        })

    # 9. 检查 notes 正确值
    if data["notes"] == "Please confirm with candidate.":
        details.append({
            "item": "notes 正确 (Please confirm with candidate.)",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "值匹配"
        })
        total_score += 5
    else:
        details.append({
            "item": "notes 正确",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": f"期望 'Please confirm with candidate.'，实际 {data['notes']}"
        })

    write_score(details, total_score)

def write_score(details, total_score):
    result = {
        "total_score": total_score,
        "details": details
    }
    score_path = os.path.join(sys.argv[1] if len(sys.argv) > 1 else ".", "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"验证完成，总分: {total_score}/100")

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)

if __name__ == "__main__":
    main()
