import sys
import os
import json
from datetime import datetime, timedelta

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0

    # 1. 文件存在性 (10分)
    target_path = os.path.join(workspace, "ops/interview_schedule.json")
    if os.path.exists(target_path):
        details.append({"item": "产物文件 ops/interview_schedule.json 存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
        total_score += 10
    else:
        details.append({"item": "产物文件 ops/interview_schedule.json 存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        # 后续检查无法进行，直接输出
        _write_score(total_score, details)
        return

    # 2. JSON 合法性 (10分)
    try:
        with open(target_path, "r") as f:
            data = json.load(f)
        details.append({"item": "JSON 格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "解析成功"})
        total_score += 10
    except Exception as e:
        details.append({"item": "JSON 格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {e}"})
        _write_score(total_score, details)
        return

    # 3. 数据类型为列表 (5分)
    if isinstance(data, list):
        details.append({"item": "顶层结构为列表", "score": 5, "max_score": 5, "passed": True, "reason": "列表类型"})
        total_score += 5
    else:
        details.append({"item": "顶层结构为列表", "score": 0, "max_score": 5, "passed": False, "reason": f"类型为 {type(data).__name__}"})
        _write_score(total_score, details)
        return

    # 4. 记录数量 (10分) - 预期2条
    expected_count = 2
    if len(data) == expected_count:
        details.append({"item": f"记录数量为 {expected_count}", "score": 10, "max_score": 10, "passed": True, "reason": f"实际数量 {len(data)}"})
        total_score += 10
    else:
        details.append({"item": f"记录数量为 {expected_count}", "score": 0, "max_score": 10, "passed": False, "reason": f"实际数量 {len(data)}"})

    # 5. 每条记录字段完整 (10分)
    required_fields = ["candidate_id", "job_id", "start_time", "end_time", "reminder_at"]
    all_have_fields = True
    for idx, record in enumerate(data):
        for field in required_fields:
            if field not in record:
                all_have_fields = False
                details.append({"item": f"记录 {idx} 字段完整性", "score": 0, "max_score": 10, "passed": False, "reason": f"缺少字段 {field}"})
                break
        if not all_have_fields:
            break
    if all_have_fields:
        details.append({"item": "每条记录包含所有必需字段", "score": 10, "max_score": 10, "passed": True, "reason": "字段完整"})
        total_score += 10

    # 6. 记录内容正确性 (30分) - 检查匹配对和时间
    correct_pairs = {"candidate_001": "job_A", "candidate_002": "job_B"}
    pair_score = 0
    # 先检查是否包含且只包含这两个对
    found_pairs = {r["candidate_id"]: r["job_id"] for r in data if "candidate_id" in r and "job_id" in r}
    if found_pairs == correct_pairs:
        pair_score = 10
        details.append({"item": "匹配对正确（候选人-职位）", "score": 10, "max_score": 10, "passed": True, "reason": "完全匹配预期"})
        total_score += 10
    else:
        details.append({"item": "匹配对正确（候选人-职位）", "score": 0, "max_score": 10, "passed": False, "reason": f"实际 {found_pairs}，期望 {correct_pairs}"})

    # 时间正确性 (20分)
    # 读取配置确定预期时间
    config_path = os.path.join(workspace, "data/schedule_config.json")
    try:
        with open(config_path) as f:
            config = json.load(f)
        start_date = config["start_date"]
        start_time_str = config["day_start"]
        slot_minutes = config["slot_minutes"]
    except Exception as e:
        details.append({"item": "时间配置读取", "score": 0, "max_score": 20, "passed": False, "reason": f"无法读取配置: {e}"})
        _write_score(total_score, details)
        return

    base_datetime = datetime.strptime(f"{start_date}T{start_time_str}", "%Y-%m-%dT%H:%M")
    expected_interviews = []
    for i, (cid, jid) in enumerate(correct_pairs.items()):
        start = base_datetime + timedelta(minutes=i*slot_minutes)
        end = start + timedelta(minutes=slot_minutes)
        reminder = start - timedelta(minutes=30)
        expected_interviews.append({
            "candidate_id": cid,
            "job_id": jid,
            "start_time": start.strftime("%Y-%m-%dT%H:%M"),
            "end_time": end.strftime("%Y-%m-%dT%H:%M"),
            "reminder_at": reminder.strftime("%Y-%m-%dT%H:%M")
        })

    time_correct = True
    for idx, record in enumerate(data):
        if idx >= len(expected_interviews):
            break
        expected = expected_interviews[idx]
        for field in ["start_time", "end_time", "reminder_at"]:
            if record.get(field) != expected[field]:
                time_correct = False
                details.append({"item": f"记录 {idx} 时间字段 {field}", "score": 0, "max_score": 20, "passed": False, "reason": f"实际 {record.get(field)}，期望 {expected[field]}"})
                break
        if not time_correct:
            break
    if time_correct:
        details.append({"item": "面试时间与提醒时间正确", "score": 20, "max_score": 20, "passed": True, "reason": "所有时间字段匹配预期"})
        total_score += 20

    # 7. 排除了干扰项（无技能候选人+旧数据） (15分)
    excluded_ok = True
    for record in data:
        if record.get("candidate_id") in ["candidate_003", "candidate_004", "candidate_005", "candidate_006"]:
            excluded_ok = False
            details.append({"item": "排除了干扰候选人", "score": 0, "max_score": 15, "passed": False, "reason": f"不应出现 {record['candidate_id']}"})
            break
    if excluded_ok:
        details.append({"item": "排除了干扰候选人（无技能/旧数据）", "score": 15, "max_score": 15, "passed": True, "reason": "所有记录均来自有效候选人"})
        total_score += 15

    # 确保总分为整数
    total_score = min(total_score, 100)
    _write_score(total_score, details)

def _write_score(total_score, details):
    result = {"total_score": total_score, "details": details}
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    verify()
