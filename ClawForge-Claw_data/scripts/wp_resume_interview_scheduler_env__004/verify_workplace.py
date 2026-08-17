import os
import sys
import json
from datetime import datetime, timedelta

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

score_dict = {
    "total_score": 0,
    "details": []
}

total_score = 0

# 1. 检查 ops 目录是否存在 (10分)
ops_path = os.path.join(workspace, "ops")
if os.path.isdir(ops_path):
    score_dict["details"].append({
        "item": "ops directory exists",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "Found ops/ directory."
    })
    total_score += 10
else:
    score_dict["details"].append({
        "item": "ops directory exists",
        "score": 0,
        "max_score": 10,
        "passed": False,
        "reason": "ops/ directory not found or not a directory."
    })

# 2. 检查 interview_schedule.json 存在 (10分)
schedule_path = os.path.join(workspace, "ops", "interview_schedule.json")
if os.path.isfile(schedule_path):
    score_dict["details"].append({
        "item": "interview_schedule.json exists",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "File found."
    })
    total_score += 10
else:
    score_dict["details"].append({
        "item": "interview_schedule.json exists",
        "score": 0,
        "max_score": 10,
        "passed": False,
        "reason": "File not found."
    })

# 3. 检查 reminder.json 存在 (10分)
reminder_path = os.path.join(workspace, "ops", "reminder.json")
if os.path.isfile(reminder_path):
    score_dict["details"].append({
        "item": "reminder.json exists",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "File found."
    })
    total_score += 10
else:
    score_dict["details"].append({
        "item": "reminder.json exists",
        "score": 0,
        "max_score": 10,
        "passed": False,
        "reason": "File not found."
    })

# 辅助函数：检查 JSON 有效性并返回对象
def load_json(path):
    try:
        with open(path, "r") as f:
            data = json.load(f)
        return data, True
    except Exception:
        return None, False

# 4. 检查 interview_schedule.json 格式合法 (10分)
schedule_data, valid = load_json(schedule_path)
if valid:
    score_dict["details"].append({
        "item": "interview_schedule.json is valid JSON",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "JSON parsed successfully."
    })
    total_score += 10
else:
    score_dict["details"].append({
        "item": "interview_schedule.json is valid JSON",
        "score": 0,
        "max_score": 10,
        "passed": False,
        "reason": "File is not valid JSON or unreadable."
    })

# 5. 检查 reminder.json 格式合法 (10分)
reminder_data, valid = load_json(reminder_path)
if valid:
    score_dict["details"].append({
        "item": "reminder.json is valid JSON",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "JSON parsed successfully."
    })
    total_score += 10
else:
    score_dict["details"].append({
        "item": "reminder.json is valid JSON",
        "score": 0,
        "max_score": 10,
        "passed": False,
        "reason": "File is not valid JSON or unreadable."
    })

# 如果文件有效，继续检查字段
if schedule_data and isinstance(schedule_data, dict):
    # 6. candidate_id 正确 (10分)
    if schedule_data.get("candidate_id") == "C003":
        score_dict["details"].append({
            "item": "schedule: candidate_id = C003",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Correct candidate."
        })
        total_score += 10
    else:
        score_dict["details"].append({
            "item": "schedule: candidate_id = C003",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Got {schedule_data.get('candidate_id')}, expected C003."
        })

    # 7. job_id 正确 (10分)
    if schedule_data.get("job_id") == "J001":
        score_dict["details"].append({
            "item": "schedule: job_id = J001",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Correct job."
        })
        total_score += 10
    else:
        score_dict["details"].append({
            "item": "schedule: job_id = J001",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Got {schedule_data.get('job_id')}, expected J001."
        })

    # 8. organizer 正确 (10分)
    if schedule_data.get("organizer") == "bob@example.com":
        score_dict["details"].append({
            "item": "schedule: organizer = bob@example.com",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Correct organizer email."
        })
        total_score += 10
    else:
        score_dict["details"].append({
            "item": "schedule: organizer = bob@example.com",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Got {schedule_data.get('organizer')}, expected bob@example.com."
        })

    # 9. status 正确 (5分)
    if schedule_data.get("status") == "confirmed":
        score_dict["details"].append({
            "item": "schedule: status = confirmed",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "Status confirmed."
        })
        total_score += 5
    else:
        score_dict["details"].append({
            "item": "schedule: status = confirmed",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": f"Got {schedule_data.get('status')}, expected confirmed."
        })

    # 10. 面试时间正确 (来自 current_time.txt 明天10:00) (15分)
    time_str = schedule_data.get("scheduled_time", "")
    try:
        # 计算预期时间
        current_time_path = os.path.join(workspace, "data", "current_time.txt")
        if os.path.isfile(current_time_path):
            with open(current_time_path, "r") as f:
                ref_str = f.read().strip()
            ref_dt = datetime.fromisoformat(ref_str)
            expected_dt = ref_dt.replace(hour=10, minute=0, second=0, microsecond=0) + timedelta(days=1)
            expected_str = expected_dt.isoformat()
        else:
            expected_str = ""

        if time_str == expected_str:
            score_dict["details"].append({
                "item": "schedule: scheduled_time = " + expected_str,
                "score": 15,
                "max_score": 15,
                "passed": True,
                "reason": "Time matches expected."
            })
            total_score += 15
        else:
            score_dict["details"].append({
                "item": "schedule: scheduled_time = " + expected_str,
                "score": 0,
                "max_score": 15,
                "passed": False,
                "reason": f"Got {time_str}, expected {expected_str}."
            })
    except Exception as e:
        score_dict["details"].append({
            "item": "schedule: scheduled_time check",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": f"Error parsing time: {str(e)}."
        })
else:
    # 若文件无效，后续项不得分
    for item in ["candidate_id", "job_id", "organizer", "status", "scheduled_time"]:
        score_dict["details"].append({
            "item": f"schedule: {item}",
            "score": 0,
            "max_score": 10 if item != "status" else 5,
            "passed": False,
            "reason": "Schedule file was invalid, cannot check field."
        })
    if not isinstance(schedule_data, dict):
        score_dict["details"].append({
            "item": "schedule: scheduled_time",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": "Schedule data is not a dict."
        })

if reminder_data and isinstance(reminder_data, dict):
    # 11. reminder 候选人和职位一致 (5分)
    if reminder_data.get("candidate_id") == "C003" and reminder_data.get("job_id") == "J001":
        score_dict["details"].append({
            "item": "reminder: candidate_id & job_id match schedule",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "Correct references."
        })
        total_score += 5
    else:
        score_dict["details"].append({
            "item": "reminder: candidate_id & job_id match schedule",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": f"Got candidate_id={reminder_data.get('candidate_id')}, job_id={reminder_data.get('job_id')}, expected C003 and J001."
        })

    # 12. reminder_time 正确 (提前30分钟) (5分)
    time_str = reminder_data.get("reminder_time", "")
    try:
        current_time_path = os.path.join(workspace, "data", "current_time.txt")
        if os.path.isfile(current_time_path):
            with open(current_time_path, "r") as f:
                ref_str = f.read().strip()
            ref_dt = datetime.fromisoformat(ref_str)
            expected_interview = ref_dt.replace(hour=10, minute=0, second=0, microsecond=0) + timedelta(days=1)
            expected_reminder = expected_interview - timedelta(minutes=30)
            expected_reminder_str = expected_reminder.isoformat()
        else:
            expected_reminder_str = ""

        if time_str == expected_reminder_str:
            score_dict["details"].append({
                "item": "reminder: reminder_time = " + expected_reminder_str,
                "score": 5,
                "max_score": 5,
                "passed": True,
                "reason": "Reminder time correct."
            })
            total_score += 5
        else:
            score_dict["details"].append({
                "item": "reminder: reminder_time = " + expected_reminder_str,
                "score": 0,
                "max_score": 5,
                "passed": False,
                "reason": f"Got {time_str}, expected {expected_reminder_str}."
            })
    except Exception as e:
        score_dict["details"].append({
            "item": "reminder: reminder_time",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": f"Error parsing time: {str(e)}."
        })

    # 13. reminder type (5分)
    if reminder_data.get("type") == "interview_reminder":
        score_dict["details"].append({
            "item": "reminder: type = interview_reminder",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "Correct type."
        })
        total_score += 5
    else:
        score_dict["details"].append({
            "item": "reminder: type = interview_reminder",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": f"Got {reminder_data.get('type')}, expected interview_reminder."
        })

    # 14. recipient (5分)
    if reminder_data.get("recipient") == "bob@example.com":
        score_dict["details"].append({
            "item": "reminder: recipient = bob@example.com",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "Correct recipient."
        })
        total_score += 5
    else:
        score_dict["details"].append({
            "item": "reminder: recipient = bob@example.com",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": f"Got {reminder_data.get('recipient')}, expected bob@example.com."
        })
else:
    for item in ["candidate_id & job_id", "reminder_time", "type", "recipient"]:
        score_dict["details"].append({
            "item": f"reminder: {item}",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "Reminder file was invalid, cannot check field."
        })

# 计算总分并写入
total_score = min(total_score, 100)  # 确保不超分
score_dict["total_score"] = total_score

with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
    json.dump(score_dict, f, indent=2)

print(f"Total score: {total_score}/100")
