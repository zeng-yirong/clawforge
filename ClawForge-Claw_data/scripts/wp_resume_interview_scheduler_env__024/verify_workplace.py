import os
import sys
import json
from datetime import datetime

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results = []
    total_score = 0
    max_total = 100

    # 1. 检查必备目录是否存在 (5分)
    req_dirs = ["ops"]
    for d in req_dirs:
        p = os.path.join(workspace, d)
        exists = os.path.isdir(p)
        results.append({
            "item": f"目录 {d} 存在",
            "score": 5 if exists else 0,
            "max_score": 5,
            "passed": exists,
            "reason": "目录存在" if exists else "目录缺失"
        })
        if exists:
            total_score += 5

    # 2. 检查 ops/interviews.json 存在且合法 (10分)
    interviews_path = os.path.join(workspace, "ops", "interviews.json")
    interviews_valid = False
    interviews_data = None
    if os.path.isfile(interviews_path):
        try:
            with open(interviews_path, "r") as f:
                interviews_data = json.load(f)
            interviews_valid = True
            results.append({
                "item": "ops/interviews.json 存在且合法JSON",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "文件合法"
            })
            total_score += 10
        except (json.JSONDecodeError, Exception) as e:
            results.append({
                "item": "ops/interviews.json 存在且合法JSON",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"JSON解析失败: {str(e)[:100]}"
            })
    else:
        results.append({
            "item": "ops/interviews.json 存在且合法JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件不存在"
        })

    # 3. 检查 ops/reminders.json 存在且合法 (10分)
    reminders_path = os.path.join(workspace, "ops", "reminders.json")
    reminders_valid = False
    reminders_data = None
    if os.path.isfile(reminders_path):
        try:
            with open(reminders_path, "r") as f:
                reminders_data = json.load(f)
            reminders_valid = True
            results.append({
                "item": "ops/reminders.json 存在且合法JSON",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "文件合法"
            })
            total_score += 10
        except (json.JSONDecodeError, Exception) as e:
            results.append({
                "item": "ops/reminders.json 存在且合法JSON",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"JSON解析失败: {str(e)[:100]}"
            })
    else:
        results.append({
            "item": "ops/reminders.json 存在且合法JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件不存在"
        })

    # 4. interviews 内容校验 (30分)
    interview_score = 0
    interview_max = 30
    interview_fail_reason = ""
    if interviews_valid and isinstance(interviews_data, dict):
        # 期望是一个单一面试对象或包含在某个字段中？我们设计成直接包含面试对象或列表？
        # 根据常见做法，可能是一个对象，但也可以是一个列表。我们允许两种形式。
        # 为了简化，我们要求是一个对象，包含以下字段。
        if "interviews" in interviews_data:
            interview_list = interviews_data["interviews"]
            if isinstance(interview_list, list) and len(interview_list) == 1:
                interview = interview_list[0]
            else:
                interview_fail_reason = "interviews字段不是只含一个元素的列表"
        else:
            interview = interviews_data  # 直接对象

        # 检查必要字段
        required_fields = {
            "candidate_id": str,
            "job_id": str,
            "interviewer_id": str,
            "datetime": str,
            "room": str,
            "duration_minutes": (int, float)
        }
        field_ok = True
        for field, ftype in required_fields.items():
            if field not in interview:
                field_ok = False
                interview_fail_reason = f"缺少字段 {field}"
                break
            if not isinstance(interview[field], ftype if isinstance(ftype, type) else (int,float)):
                # 对duration_minutes可以接受int或float
                if field == "duration_minutes":
                    if not isinstance(interview[field], (int, float)):
                        field_ok = False
                        interview_fail_reason = f"字段 {field} 类型不正确 (期望int/float)"
                else:
                    field_ok = False
                    interview_fail_reason = f"字段 {field} 类型不正确 (期望 {ftype})"
                break
        if field_ok:
            # 检查字段值正确性
            value_ok = True
            # candidate_id 应该是 c_001 (Alice Wang)
            if interview["candidate_id"] != "c_001":
                value_ok = False
                interview_fail_reason = f"candidate_id 应为 c_001, 实际是 {interview['candidate_id']}"
            elif interview["job_id"] != "job_001":
                value_ok = False
                interview_fail_reason = f"job_id 应为 job_001"
            elif interview["interviewer_id"] != "b_001":
                value_ok = False
                interview_fail_reason = f"interviewer_id 应为 b_001"
            elif interview["room"] != "A201":
                value_ok = False
                interview_fail_reason = f"room 应为 A201"
            elif interview.get("duration_minutes", 0) != 60:
                value_ok = False
                interview_fail_reason = f"duration_minutes 应为 60"
            elif interview["datetime"] != "2025-04-16T10:00:00":
                value_ok = False
                interview_fail_reason = f"datetime 应为 2025-04-16T10:00:00"
            if value_ok:
                interview_score = 30
            else:
                interview_score = 15  # 部分字段对给一半
        else:
            interview_score = 0
    else:
        interview_fail_reason = "interviews 数据不存在或不是对象"

    results.append({
        "item": "interviews.json 内容正确性",
        "score": interview_score,
        "max_score": interview_max,
        "passed": interview_score == interview_max,
        "reason": (interview_fail_reason if interview_fail_reason else "全部正确")
    })
    total_score += interview_score

    # 5. reminders 内容校验 (30分)
    reminder_score = 0
    reminder_max = 30
    reminder_fail_reason = ""
    if reminders_valid and isinstance(reminders_data, dict):
        if "reminders" in reminders_data:
            reminder_list = reminders_data["reminders"]
            if isinstance(reminder_list, list) and len(reminder_list) == 1:
                reminder = reminder_list[0]
            else:
                reminder_fail_reason = "reminders字段不是只含一个元素的列表"
        else:
            reminder = reminders_data
        required_fields = {
            "associated_interview_id": str,  # 可以用面试id或candidate_id，我们要求关联candidate_id
            "remind_at": str,
            "type": str
        }
        field_ok = True
        for field, ftype in required_fields.items():
            if field not in reminder:
                field_ok = False
                reminder_fail_reason = f"缺少字段 {field}"
                break
            if not isinstance(reminder[field], str):
                field_ok = False
                reminder_fail_reason = f"字段 {field} 类型不正确 (期望字符串)"
                break
        if field_ok:
            value_ok = True
            # 关联candidate_id 应为 c_001
            if reminder.get("associated_interview_id") != "c_001":
                value_ok = False
                reminder_fail_reason = f"associated_interview_id 应为 c_001"
            elif reminder.get("type") != "interview_reminder":
                value_ok = False
                reminder_fail_reason = f"type 应为 interview_reminder"
            # remind_at 应该是面试时间前30分钟: 2025-04-16T09:30:00
            elif reminder.get("remind_at") != "2025-04-16T09:30:00":
                value_ok = False
                reminder_fail_reason = f"remind_at 应为 2025-04-16T09:30:00 (提前30分钟)"
            if value_ok:
                reminder_score = 30
            else:
                reminder_score = 15
        else:
            reminder_score = 0
    else:
        reminder_fail_reason = "reminders数据不存在或不是对象"

    results.append({
        "item": "reminders.json 内容正确性",
        "score": reminder_score,
        "max_score": reminder_max,
        "passed": reminder_score == reminder_max,
        "reason": (reminder_fail_reason if reminder_fail_reason else "全部正确")
    })
    total_score += reminder_score

    # 6. 禁止有多余答案文件 (5分) —— 检查是否还有别的面试文件
    extra_files_score = 0
    extra_max = 5
    extra_issues = []
    # 检查 ops 下是否只有 interviews.json 和 reminders.json
    if os.path.isdir(os.path.join(workspace, "ops")):
        ops_files = [f for f in os.listdir(os.path.join(workspace, "ops")) if f.endswith('.json')]
        allowed = {"interviews.json", "reminders.json"}
        extra_files = [f for f in ops_files if f not in allowed]
        if extra_files:
            extra_issues.append(f"多余的文件: {', '.join(extra_files)}")
            extra_files_score = 2  # 给部分分
        else:
            extra_files_score = 5
    else:
        extra_issues.append("ops目录不存在")
    results.append({
        "item": "ops目录下无多余JSON文件",
        "score": extra_files_score,
        "max_score": extra_max,
        "passed": extra_files_score == extra_max,
        "reason": extra_issues[0] if extra_issues else "正确"
    })
    total_score += extra_files_score

    # 7. 其他干扰文件检测 (5分) —— 如果生成了错误的候选人或错误匹配，扣分（通过检查内容已经体现）
    # 这一项给满分，因为内容检查已经覆盖
    results.append({
        "item": "没有生成非预期答案（通过内容检查覆盖）",
        "score": 5,
        "max_score": 5,
        "passed": True,
        "reason": "内容检查足够"
    })
    total_score += 5

    # 8. 格式一致性 (5分) —— interviews 和 reminders 中的 datetime 格式是否为 ISO 8601
    format_score = 0
    format_max = 5
    if interviews_valid and reminders_valid:
        # 简单检查是否包含T以及是标准格式
        ok = True
        if interviews_data and isinstance(interviews_data, dict):
            iv = interviews_data.get("interviews", [interviews_data])
            if isinstance(iv, list) and len(iv)>0:
                dt = iv[0].get("datetime", "")
                if "T" not in dt or len(dt) != 19:
                    ok = False
            if reminders_data and isinstance(reminders_data, dict):
                rm = reminders_data.get("reminders", [reminders_data])
                if isinstance(rm, list) and len(rm)>0:
                    dt2 = rm[0].get("remind_at", "")
                    if "T" not in dt2 or len(dt2) != 19:
                        ok = False
        if ok:
            format_score = 5
        else:
            format_score = 2
    results.append({
        "item": "时间格式符合ISO 8601",
        "score": format_score,
        "max_score": format_max,
        "passed": format_score == format_max,
        "reason": "格式正确" if format_score == format_max else "格式有误"
    })
    total_score += format_score

    # 写入结果
    total_score = min(total_score, 100)  # 上限100
    output = {
        "total_score": total_score,
        "details": results
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(output, f, indent=2)

    print(f"Score: {total_score}/100")
    return total_score

if __name__ == "__main__":
    verify()
