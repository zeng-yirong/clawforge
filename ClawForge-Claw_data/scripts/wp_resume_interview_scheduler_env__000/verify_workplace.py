import json
import os
import sys
from collections import OrderedDict

def verify(workspace):
    result = {
        "total_score": 0,
        "details": []
    }

    # 检查目录结构
    score_item = lambda name, max_s: {"item": name, "score": 0, "max_score": max_s, "passed": False, "reason": ""}
    details = []

    # 1. 检查 ops 目录是否存在
    ops_dir = os.path.join(workspace, "ops")
    d = score_item("ops directory exists", 10)
    if os.path.isdir(ops_dir):
        d["score"] = 10
        d["passed"] = True
        d["reason"] = "ops/ directory found"
    else:
        d["reason"] = "ops/ directory missing"
    details.append(d)

    # 2. 检查 interview_schedule.json 是否存在
    schedule_path = os.path.join(workspace, "ops/interview_schedule.json")
    d = score_item("ops/interview_schedule.json exists", 10)
    if os.path.isfile(schedule_path):
        d["score"] = 10
        d["passed"] = True
        d["reason"] = "file found"
    else:
        d["reason"] = "file missing"
    details.append(d)

    # 3. 解析JSON并检查合法性
    d = score_item("valid JSON and correct structure", 20)
    try:
        with open(schedule_path, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        d["reason"] = f"JSON parse error: {e}"
        details.append(d)
        # 后续检查无法进行，直接返回
        result["details"] = details
        result["total_score"] = sum(item["score"] for item in details)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # 检查是否为列表，且每个元素包含必要字段
    if not isinstance(data, list):
        d["reason"] = "root must be a list"
        details.append(d)
        result["details"] = details
        result["total_score"] = sum(item["score"] for item in details)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    required_fields = {"candidate_id", "job_id", "interview_time", "reminder_time"}
    all_ok = True
    for i, entry in enumerate(data):
        if not isinstance(entry, dict):
            all_ok = False
            break
        missing = required_fields - set(entry.keys())
        if missing:
            all_ok = False
            break
    if all_ok and len(data) > 0:
        d["score"] = 20
        d["passed"] = True
        d["reason"] = f"valid list with {len(data)} entries, all required fields present"
    else:
        d["reason"] = "structure invalid or missing fields"
    details.append(d)

    if not all_ok:
        result["details"] = details
        result["total_score"] = sum(item["score"] for item in details)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # 4. 检查匹配正确性（关键部分，50分）
    d = score_item("correct candidate-job matching based on skill overlap", 50)

    # 读取原始候选人和职位数据以验证
    try:
        with open(os.path.join(workspace, "data/candidates/candidates.json")) as f:
            candidates_raw = json.load(f)["candidates"]
        with open(os.path.join(workspace, "data/jobs/jobs.json")) as f:
            jobs_raw = json.load(f)["jobs"]
    except:
        d["reason"] = "unable to read original data files"
        details.append(d)
        result["details"] = details
        result["total_score"] = sum(item["score"] for item in details)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # 预处理候选人：去重（保留第一次出现的candidate_id），过滤技能为空
    seen_ids = set()
    candidates_clean = []
    for c in candidates_raw:
        cid = c["candidate_id"]
        if cid in seen_ids:
            continue
        seen_ids.add(cid)
        if not c.get("skills"):
            continue
        candidates_clean.append(c)

    # 预处理职位：只保留open状态，去重（保留第一次出现的job_id）
    seen_jobs = set()
    jobs_clean = []
    for j in jobs_raw:
        jid = j["job_id"]
        if jid in seen_jobs:
            continue
        seen_jobs.add(jid)
        if j.get("status") != "open":
            continue
        jobs_clean.append(j)

    # 计算每个开放职位的最佳候选人
    def skill_overlap(cand_skills, job_skills):
        return len(set(cand_skills) & set(job_skills))

    expected_schedule = []
    for job in jobs_clean:
        best_candidate = None
        best_overlap = -1
        for cand in candidates_clean:
            ov = skill_overlap(cand["skills"], job["required_skills"])
            if ov > best_overlap:
                best_overlap = ov
                best_candidate = cand
            elif ov == best_overlap and best_candidate is not None:
                # 规则：字母序小者优先
                if cand["candidate_name"] < best_candidate["candidate_name"]:
                    best_candidate = cand
        if best_candidate:
            expected_schedule.append({
                "candidate_id": best_candidate["candidate_id"],
                "job_id": job["job_id"],
                "interview_time": "2025-04-15T10:00:00",
                "reminder_time": "2025-04-15T09:30:00"
            })

    # 比较实际结果与预期
    # 先构建索引比较集合，忽略顺序
    actual_set = {}
    for entry in data:
        key = (entry["candidate_id"], entry["job_id"])
        actual_set[key] = entry

    expected_set = {}
    for entry in expected_schedule:
        key = (entry["candidate_id"], entry["job_id"])
        expected_set[key] = entry

    # 检查数量
    if len(actual_set) != len(expected_set):
        d["reason"] = f"number of entries mismatch: expected {len(expected_set)}, got {len(actual_set)}"
        details.append(d)
        result["details"] = details
        result["total_score"] = sum(item["score"] for item in details)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # 检查每个键是否正确，以及时间字段
    score = 50
    mismatch = False
    for key, exp in expected_set.items():
        act = actual_set.get(key)
        if not act:
            mismatch = True
            break
        # 检查 interview_time 和 reminder_time
        if act.get("interview_time") != "2025-04-15T10:00:00":
            mismatch = True
            break
        if act.get("reminder_time") != "2025-04-15T09:30:00":
            mismatch = True
            break

    if not mismatch:
        d["score"] = 50
        d["passed"] = True
        d["reason"] = f"all {len(expected_schedule)} matches correct, times correct"
    else:
        d["reason"] = "match or time field incorrect"
    details.append(d)

    # 5. 检查字段完整性（额外5分，但总分为50+20+10+10+? 实际最大100，这里max 90，故意留10分给格式）
    # 但是我们已经检查了必需字段，再加一个时间格式验证
    d = score_item("datetime fields valid ISO format", 10)
    all_time_ok = True
    for entry in data:
        try:
            # 简单验证格式
            from datetime import datetime
            datetime.fromisoformat(entry.get("interview_time", ""))
            datetime.fromisoformat(entry.get("reminder_time", ""))
        except:
            all_time_ok = False
            break
    if all_time_ok:
        d["score"] = 10
        d["passed"] = True
        d["reason"] = "all datetime fields valid ISO format"
    else:
        d["reason"] = "invalid datetime format"
    details.append(d)

    # 总分汇总
    total = sum(item["score"] for item in details)
    result["total_score"] = total
    result["details"] = details

    # 写入结果
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
