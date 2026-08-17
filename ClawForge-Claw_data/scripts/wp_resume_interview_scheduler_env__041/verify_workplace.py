import sys
import json
import os
import re

def validate(workspace):
    details = []
    total_score = 0
    max_total = 100

    # 1. 检查 interview_schedule.json 是否存在 (10分)
    path_ok = os.path.isfile(os.path.join(workspace, "interview_schedule.json"))
    details.append({
        "item": "interview_schedule.json 存在",
        "score": 10 if path_ok else 0,
        "max_score": 10,
        "passed": path_ok,
        "reason": "文件存在" if path_ok else "文件缺失"
    })
    if not path_ok:
        # 直接结束，剩余0分
        for rest in ["JSON 格式合法", "记录条数正确", "每项字段完整且 interview_id 正确", "匹配记录值准确"]:
            details.append({
                "item": rest,
                "score": 0,
                "max_score": 22,
                "passed": False,
                "reason": "主文件缺失，跳过"
            })
        total_score = 0
        write_score(workspace, total_score, details)
        return

    # 2. JSON 格式合法 (10分)
    try:
        with open(os.path.join(workspace, "interview_schedule.json"), "r") as f:
            content = f.read()
            schedule = json.loads(content)
        format_ok = True
    except (json.JSONDecodeError, FileNotFoundError) as e:
        format_ok = False
        schedule = None
    details.append({
        "item": "JSON 格式合法",
        "score": 10 if format_ok else 0,
        "max_score": 10,
        "passed": format_ok,
        "reason": "JSON 解析成功" if format_ok else f"JSON 解析失败: {e}"
    })
    if not format_ok:
        write_score(workspace, sum(d["score"] for d in details), details)
        return

    # 3. 记录条数正确 (22分)
    expected_count = 3  # C001匹配 J001, C005匹配 J001, C002匹配 J002
    actual_count = len(schedule) if isinstance(schedule, list) else 0
    count_ok = (actual_count == expected_count)
    details.append({
        "item": "记录条数正确",
        "score": 22 if count_ok else 0,
        "max_score": 22,
        "passed": count_ok,
        "reason": f"期望 {expected_count} 条，实际 {actual_count} 条" if count_ok else f"期望 {expected_count} 条，实际 {actual_count} 条（错误）"
    })

    # 4. 每项字段完整且 interview_id 格式正确 (22分)
    required_fields = {"candidate_id", "job_id", "status", "interview_date", "interview_id"}
    field_ok = True
    id_format_ok = True
    field_reasons = []
    for rec in schedule if isinstance(schedule, list) else []:
        # 字段存在性
        missing = required_fields - set(rec.keys())
        if missing:
            field_ok = False
            field_reasons.append(f"记录 {rec.get('interview_id','?')} 缺少字段 {missing}")
        # interview_id 格式：<candidate_id>_<job_id>
        if "interview_id" in rec and "candidate_id" in rec and "job_id" in rec:
            expected_id = f"{rec['candidate_id']}_{rec['job_id']}"
            if rec["interview_id"] != expected_id:
                id_format_ok = False
                field_reasons.append(f"记录 {rec.get('interview_id','?')} interview_id 应为 {expected_id}，实际 {rec['interview_id']}")
        else:
            id_format_ok = False
    field_score = 22 if (field_ok and id_format_ok) else 0
    details.append({
        "item": "每项字段完整且 interview_id 正确",
        "score": field_score,
        "max_score": 22,
        "passed": (field_ok and id_format_ok),
        "reason": "所有字段齐全且 interview_id 格式正确" if (field_ok and id_format_ok) else f"错误: {'; '.join(field_reasons)}"
    })

    # 5. 匹配记录值准确 (36分)
    # 期望的三条记录：
    expected_records = [
        {"candidate_id": "C001", "job_id": "J001", "status": "scheduled", "interview_date": "2025-06-02", "interview_id": "C001_J001"},
        {"candidate_id": "C005", "job_id": "J001", "status": "scheduled", "interview_date": "2025-06-02", "interview_id": "C005_J001"},
        {"candidate_id": "C002", "job_id": "J002", "status": "scheduled", "interview_date": "2025-06-02", "interview_id": "C002_J002"},
    ]
    # 构建实际记录的相似性查找器（根据interview_id）
    if isinstance(schedule, list):
        actual_by_id = {rec.get("interview_id"): rec for rec in schedule}
    else:
        actual_by_id = {}
    match_score = 0
    max_match = 36
    per_record = max_match // len(expected_records)
    match_reasons = []
    for exp in expected_records:
        eid = exp["interview_id"]
        if eid not in actual_by_id:
            match_reasons.append(f"缺失记录 {eid}")
            continue
        act = actual_by_id[eid]
        mismatch = {}
        for key in ["candidate_id", "job_id", "status", "interview_date"]:
            if act.get(key) != exp[key]:
                mismatch[key] = f"期望 {exp[key]}, 实际 {act.get(key)}"
        if mismatch:
            match_reasons.append(f"{eid} 字段错误: {mismatch}")
        else:
            match_score += per_record
    if match_score == max_match:
        match_reasons.append("所有记录值完全匹配")
    details.append({
        "item": "匹配记录值准确",
        "score": match_score,
        "max_score": max_match,
        "passed": (match_score == max_match),
        "reason": "所有记录值完全匹配" if match_score == max_match else f"部分错误: {'; '.join(match_reasons)}"
    })

    total_score = sum(d["score"] for d in details)
    write_score(workspace, total_score, details)

def write_score(workspace, total, details):
    result = {
        "total_score": total,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    validate(workspace)
