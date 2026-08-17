import sys
import os
import json
import csv
import re

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    os.chdir(workspace)

    score_details = []
    total_score = 0
    max_total = 100

    # ---------- 1. 目录结构检查 ----------
    item = {"item": "Directory structure exists", "max_score": 10}
    try:
        assert os.path.isdir("scheduling"), "scheduling directory missing"
        score_details.append({**item, "score": 10, "passed": True, "reason": "scheduling/ exists"})
        total_score += 10
    except AssertionError as e:
        score_details.append({**item, "score": 0, "passed": False, "reason": str(e)})

    # ---------- 2. 结果文件存在性 ----------
    item = {"item": "Result file exists", "max_score": 10}
    try:
        assert os.path.isfile("scheduling/interview_schedule.json"), "interview_schedule.json not found"
        score_details.append({**item, "score": 10, "passed": True, "reason": "File exists"})
        total_score += 10
    except AssertionError as e:
        score_details.append({**item, "score": 0, "passed": False, "reason": str(e)})
        # 如果文件不存在，后续检查全部0分，直接输出
        output_score(total_score, score_details)
        return

    # ---------- 3. JSON合法性 ----------
    item = {"item": "Valid JSON", "max_score": 10}
    try:
        with open("scheduling/interview_schedule.json") as f:
            data = json.load(f)
        assert isinstance(data, dict), "Root must be a JSON object"
        score_details.append({**item, "score": 10, "passed": True, "reason": "Valid JSON object"})
        total_score += 10
    except (json.JSONDecodeError, AssertionError) as e:
        score_details.append({**item, "score": 0, "passed": False, "reason": f"Invalid JSON: {e}"})
        output_score(total_score, score_details)
        return

    # ---------- 4. 必要字段检查 ----------
    item = {"item": "Contains required fields (schedule, candidate_id, interview_time, interviewer, job_id)", "max_score": 20}
    try:
        schedule = data.get("schedule", [])
        assert len(schedule) > 0, "schedule list is empty"
        for entry in schedule:
            assert "candidate_id" in entry, "Missing candidate_id"
            assert "interview_time" in entry, "Missing interview_time"
            assert "interviewer" in entry, "Missing interviewer"
            assert "job_id" in entry, "Missing job_id"
        score_details.append({**item, "score": 20, "passed": True, "reason": f"All {len(schedule)} entries have required fields"})
        total_score += 20
    except AssertionError as e:
        score_details.append({**item, "score": 0, "passed": False, "reason": str(e)})

    # ---------- 5. 匹配候选人数量精确性 ----------
    item = {"item": "Correct number of matched candidates (2)", "max_score": 15}
    try:
        candidate_ids = [e["candidate_id"] for e in schedule]
        expected_ids = {"cand_001", "cand_003"}  # 技能完全匹配的候选人
        actual_ids = set(candidate_ids)
        assert actual_ids == expected_ids, f"Expected {expected_ids}, got {actual_ids}"
        score_details.append({**item, "score": 15, "passed": True, "reason": f"Exactly candidates {expected_ids}"})
        total_score += 15
    except AssertionError as e:
        score_details.append({**item, "score": 0, "passed": False, "reason": str(e)})

    # ---------- 6. 面试时间正确性 ----------
    item = {"item": "Interview time format and value", "max_score": 15}
    try:
        for entry in schedule:
            time_val = entry["interview_time"]
            # 要求精确到分钟：2025-06-16T10:00:00
            assert re.match(r"2025-06-16T10:00:00", time_val), f"Unexpected time {time_val}"
        score_details.append({**item, "score": 15, "passed": True, "reason": "All times are 2025-06-16T10:00:00"})
        total_score += 15
    except AssertionError as e:
        score_details.append({**item, "score": 0, "passed": False, "reason": str(e)})

    # ---------- 7. 面试官姓名正确性 ----------
    item = {"item": "Interviewer is 'Alice'", "max_score": 10}
    try:
        for entry in schedule:
            assert entry["interviewer"] == "Alice", f"Expected Alice, got {entry['interviewer']}"
        score_details.append({**item, "score": 10, "passed": True, "reason": "Interviewer is Alice"})
        total_score += 10
    except AssertionError as e:
        score_details.append({**item, "score": 0, "passed": False, "reason": str(e)})

    # ---------- 8. job_id 正确性 ----------
    item = {"item": "job_id is 'job_001' (Backend Engineer)", "max_score": 10}
    try:
        for entry in schedule:
            assert entry["job_id"] == "job_001", f"Expected job_001, got {entry['job_id']}"
        score_details.append({**item, "score": 10, "passed": True, "reason": "All job_id are job_001"})
        total_score += 10
    except AssertionError as e:
        score_details.append({**item, "score": 0, "passed": False, "reason": str(e)})

    output_score(total_score, score_details)


def output_score(total, details):
    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": total, "details": details}, f, indent=2)
    print(f"Total score: {total}/100")

if __name__ == "__main__":
    verify()
