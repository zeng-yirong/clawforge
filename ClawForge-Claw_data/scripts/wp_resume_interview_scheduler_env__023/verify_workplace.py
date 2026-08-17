import sys
import json
import os

def verify(workspace):
    score = 0
    max_score = 100
    details = []

    # 1. ops 目录存在 (5分)
    ops_dir = os.path.join(workspace, "ops")
    dir_exists = os.path.isdir(ops_dir)
    score += 5 if dir_exists else 0
    details.append({
        "item": "ops 目录存在",
        "score": 5 if dir_exists else 0,
        "max_score": 5,
        "passed": dir_exists,
        "reason": "ops 目录存在" if dir_exists else "ops 目录不存在"
    })

    # 2. ops/interviews.json 文件存在 (10分)
    output_path = os.path.join(ops_dir, "interviews.json")
    file_exists = os.path.isfile(output_path)
    score += 10 if file_exists else 0
    details.append({
        "item": "ops/interviews.json 文件存在",
        "score": 10 if file_exists else 0,
        "max_score": 10,
        "passed": file_exists,
        "reason": "文件存在" if file_exists else "文件不存在"
    })

    if not file_exists:
        # 后续无法检查，直接返回
        return {"total_score": score, "details": details}

    # 3. 可解析为合法 JSON (10分)
    try:
        with open(output_path, "r") as f:
            data = json.load(f)
        json_ok = True
    except:
        json_ok = False
    score += 10 if json_ok else 0
    details.append({
        "item": "JSON 格式合法",
        "score": 10 if json_ok else 0,
        "max_score": 10,
        "passed": json_ok,
        "reason": "JSON 解析成功" if json_ok else "JSON 解析失败"
    })

    if not json_ok:
        return {"total_score": score, "details": details}

    # 4. 是列表 (10分)
    is_list = isinstance(data, list)
    score += 10 if is_list else 0
    details.append({
        "item": "顶层数据结构为列表",
        "score": 10 if is_list else 0,
        "max_score": 10,
        "passed": is_list,
        "reason": "是列表" if is_list else f"类型为 {type(data).__name__}"
    })

    if not is_list:
        return {"total_score": score, "details": details}

    # 5. 列表长度等于 1 (10分)
    length_ok = len(data) == 1
    score += 10 if length_ok else 0
    details.append({
        "item": "列表长度为 1",
        "score": 10 if length_ok else 0,
        "max_score": 10,
        "passed": length_ok,
        "reason": f"长度为 {len(data)}" if length_ok else f"长度为 {len(data)}，预期 1"
    })

    if not length_ok:
        return {"total_score": score, "details": details}

    entry = data[0]

    # 6. 包含 candidate_id 字段 (5分)
    has_cid = "candidate_id" in entry
    score += 5 if has_cid else 0
    details.append({
        "item": "包含 candidate_id 字段",
        "score": 5 if has_cid else 0,
        "max_score": 5,
        "passed": has_cid,
        "reason": "字段存在" if has_cid else "字段缺失"
    })

    # 7. candidate_id 正确 (5分)
    cid_ok = has_cid and entry["candidate_id"] == "C001"
    score += 5 if cid_ok else 0
    details.append({
        "item": "candidate_id 值为 'C001'",
        "score": 5 if cid_ok else 0,
        "max_score": 5,
        "passed": cid_ok,
        "reason": f"值为 {entry.get('candidate_id')}" if has_cid else "字段缺失"
    })

    # 8. 包含 job_id 字段 (5分)
    has_jid = "job_id" in entry
    score += 5 if has_jid else 0
    details.append({
        "item": "包含 job_id 字段",
        "score": 5 if has_jid else 0,
        "max_score": 5,
        "passed": has_jid,
        "reason": "字段存在" if has_jid else "字段缺失"
    })

    # 9. job_id 正确 (5分)
    jid_ok = has_jid and entry["job_id"] == "J001"
    score += 5 if jid_ok else 0
    details.append({
        "item": "job_id 值为 'J001'",
        "score": 5 if jid_ok else 0,
        "max_score": 5,
        "passed": jid_ok,
        "reason": f"值为 {entry.get('job_id')}" if has_jid else "字段缺失"
    })

    # 10. 包含 interviewer 字段 (5分)
    has_int = "interviewer" in entry
    score += 5 if has_int else 0
    details.append({
        "item": "包含 interviewer 字段",
        "score": 5 if has_int else 0,
        "max_score": 5,
        "passed": has_int,
        "reason": "字段存在" if has_int else "字段缺失"
    })

    # 11. interviewer 正确 (5分)
    int_ok = has_int and entry["interviewer"] == "Alice"
    score += 5 if int_ok else 0
    details.append({
        "item": "interviewer 值为 'Alice'",
        "score": 5 if int_ok else 0,
        "max_score": 5,
        "passed": int_ok,
        "reason": f"值为 {entry.get('interviewer')}" if has_int else "字段缺失"
    })

    # 12. 包含 scheduled_time 字段 (5分)
    has_time = "scheduled_time" in entry
    score += 5 if has_time else 0
    details.append({
        "item": "包含 scheduled_time 字段",
        "score": 5 if has_time else 0,
        "max_score": 5,
        "passed": has_time,
        "reason": "字段存在" if has_time else "字段缺失"
    })

    # 13. scheduled_time 正确 (5分)
    expected_time = "2025-04-15T10:00:00"
    time_ok = has_time and entry["scheduled_time"] == expected_time
    score += 5 if time_ok else 0
    details.append({
        "item": f"scheduled_time 值为 '{expected_time}'",
        "score": 5 if time_ok else 0,
        "max_score": 5,
        "passed": time_ok,
        "reason": f"值为 {entry.get('scheduled_time')}" if has_time else "字段缺失"
    })

    # 14. 没有多余字段（可选，扣分项）满分10分，多余一个字段扣2分，最多扣10分
    expected_fields = {"candidate_id", "job_id", "interviewer", "scheduled_time"}
    actual_fields = set(entry.keys())
    extra = actual_fields - expected_fields
    extra_penalty = min(10, len(extra) * 2)
    score_extra = 10 - extra_penalty
    score += score_extra
    details.append({
        "item": "没有多余字段",
        "score": score_extra,
        "max_score": 10,
        "passed": len(extra) == 0,
        "reason": f"有多余字段 {extra}" if extra else "仅含必要字段"
    })

    # 总分写入
    total_score = min(score, max_score)
    return {"total_score": total_score, "details": details}


if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))
