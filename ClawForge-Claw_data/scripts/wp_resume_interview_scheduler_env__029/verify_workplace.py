import os
import json
import sys
from datetime import datetime, timedelta

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0

    # 1. 检查 output 目录是否存在
    output_dir = os.path.join(workspace, "output")
    dir_exists = os.path.isdir(output_dir)
    score_details.append({
        "item": "output 目录存在",
        "score": 5 if dir_exists else 0,
        "max_score": 5,
        "passed": dir_exists,
        "reason": "output 目录未找到" if not dir_exists else "output 目录存在"
    })
    total_score += score_details[-1]["score"]

    # 2. 检查 schedule.json 文件是否存在
    schedule_path = os.path.join(output_dir, "schedule.json")
    file_exists = os.path.isfile(schedule_path)
    score_details.append({
        "item": "schedule.json 文件存在",
        "score": 10 if file_exists else 0,
        "max_score": 10,
        "passed": file_exists,
        "reason": "output/schedule.json 未找到" if not file_exists else "文件存在"
    })
    total_score += score_details[-1]["score"]

    if not file_exists:
        # 无法继续，直接输出
        result = {"total_score": total_score, "details": score_details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # 3. 解析 JSON 合法性
    try:
        with open(schedule_path, "r") as f:
            schedule = json.load(f)
        json_valid = isinstance(schedule, list)
        score_details.append({
            "item": "JSON 格式合法且为列表",
            "score": 10 if json_valid else 0,
            "max_score": 10,
            "passed": json_valid,
            "reason": "JSON 不是列表格式" if not json_valid else "格式正确"
        })
        total_score += score_details[-1]["score"]
        if not json_valid:
            # 无法继续
            result = {"total_score": total_score, "details": score_details}
            with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
                json.dump(result, f, indent=2)
            return
    except (json.JSONDecodeError, Exception) as e:
        score_details.append({
            "item": "JSON 格式合法",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON 解析失败: {str(e)}"
        })
        total_score += 0
        result = {"total_score": total_score, "details": score_details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # 4. 检查条目数量（应为2）
    expected_count = 2
    count_ok = len(schedule) == expected_count
    score_details.append({
        "item": "面试安排数量正确（2个）",
        "score": 15 if count_ok else 0,
        "max_score": 15,
        "passed": count_ok,
        "reason": f"预期 {expected_count} 条，实际 {len(schedule)} 条" if not count_ok else "数量正确"
    })
    total_score += score_details[-1]["score"]

    # 5. 检查每个条目的必备字段
    required_fields = ["candidate_id", "job_id", "interviewer_id", "scheduled_at", "reminder_at"]
    fields_ok = True
    field_missing_msg = ""
    for i, item in enumerate(schedule):
        for field in required_fields:
            if field not in item:
                fields_ok = False
                field_missing_msg = f"第 {i+1} 条缺少字段 {field}"
                break
        if not fields_ok:
            break
    score_details.append({
        "item": "每条记录包含全部必需字段",
        "score": 15 if fields_ok else 0,
        "max_score": 15,
        "passed": fields_ok,
        "reason": field_missing_msg if not fields_ok else "字段完整"
    })
    total_score += score_details[-1]["score"]

    if not fields_ok or not count_ok:
        # 无法继续更细粒度检查
        result = {"total_score": total_score, "details": score_details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # 6. 检查具体数据正确性（候选人与职位匹配，时间，提醒，面试官）
    # 预期匹配：C001->J001，C002->J002
    # 时间：09:00 和 10:00，提醒提前1小时
    expected_pairs = {
        "C001": {"job": "J001", "scheduled": "2025-06-15T09:00:00", "reminder": "2025-06-15T08:00:00"},
        "C002": {"job": "J002", "scheduled": "2025-06-15T10:00:00", "reminder": "2025-06-15T09:00:00"}
    }
    # 对 schedule 按 candidate_id 排序（确保顺序不影响）
    schedule_sorted = sorted(schedule, key=lambda x: x.get("candidate_id", ""))
    data_correct = True
    data_error_msg = ""
    for idx, item in enumerate(schedule_sorted):
        cid = item.get("candidate_id", "")
        jid = item.get("job_id", "")
        interviewer = item.get("interviewer_id", "")
        scheduled = item.get("scheduled_at", "")
        reminder = item.get("reminder_at", "")
        if cid not in expected_pairs:
            data_correct = False
            data_error_msg = f"意外出现的候选人 {cid}"
            break
        expected = expected_pairs[cid]
        if jid != expected["job"]:
            data_correct = False
            data_error_msg = f"{cid} 的 job 应为 {expected['job']}，实际 {jid}"
            break
        if scheduled != expected["scheduled"]:
            data_correct = False
            data_error_msg = f"{cid} 的面试时间应为 {expected['scheduled']}，实际 {scheduled}"
            break
        if reminder != expected["reminder"]:
            data_correct = False
            data_error_msg = f"{cid} 的提醒时间应为 {expected['reminder']}，实际 {reminder}"
            break
        if interviewer != "A001":
            data_correct = False
            data_error_msg = f"{cid} 的面试官应为 A001，实际 {interviewer}"
            break
    # 同时检查是否所有期望的候选人都出现了
    actual_cids = {item.get("candidate_id") for item in schedule_sorted}
    expected_cids = set(expected_pairs.keys())
    if actual_cids != expected_cids:
        data_correct = False
        data_error_msg = f"候选人集合不匹配：期望 {expected_cids}，实际 {actual_cids}"
    score_details.append({
        "item": "数据内容完全正确（匹配、时间、提醒、面试官）",
        "score": 45 if data_correct else 0,
        "max_score": 45,
        "passed": data_correct,
        "reason": data_error_msg if not data_correct else "所有字段正确"
    })
    total_score += score_details[-1]["score"]

    # 最终写入评分文件
    result = {
        "total_score": total_score,
        "details": score_details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
