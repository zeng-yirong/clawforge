import json
import os
import sys

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."

    result_path = os.path.join(workspace, "ops", "interview_confirm.json")
    details = []
    total_score = 0

    # 1. 文件是否存在（10分）
    exists = os.path.isfile(result_path)
    details.append({
        "item": "文件 ops/interview_confirm.json 存在",
        "max_score": 10,
        "score": 10 if exists else 0,
        "passed": exists,
        "reason": "文件存在" if exists else "文件不存在"
    })
    if not exists:
        # 后续检查无意义，跳过
        _write_score(details, 0)
        return

    # 2. 文件是否为合法JSON（10分）
    try:
        with open(result_path, "r") as f:
            data = json.load(f)
        json_valid = True
        details.append({
            "item": "JSON 格式合法",
            "max_score": 10,
            "score": 10,
            "passed": True,
            "reason": "解析成功"
        })
    except Exception as e:
        json_valid = False
        details.append({
            "item": "JSON 格式合法",
            "max_score": 10,
            "score": 0,
            "passed": False,
            "reason": f"解析失败: {str(e)}"
        })
        _write_score(details, 10)  # 已得文件存在分10
        return

    # 3. 字段完整性：恰好包含 candidate_id, job_id, scheduled_time（10分）
    expected_keys = {"candidate_id", "job_id", "scheduled_time"}
    actual_keys = set(data.keys())
    keys_correct = actual_keys == expected_keys
    details.append({
        "item": "JSON 包含且仅包含要求的三个字段",
        "max_score": 10,
        "score": 10 if keys_correct else 0,
        "passed": keys_correct,
        "reason": f"实际字段: {actual_keys}" if not keys_correct else "字段正确"
    })

    # 4. candidate_id 正确（30分）
    cid_ok = data.get("candidate_id") == "cand_003"
    details.append({
        "item": "candidate_id 为 cand_003",
        "max_score": 30,
        "score": 30 if cid_ok else 0,
        "passed": cid_ok,
        "reason": f"实际值为 {data.get('candidate_id')}" if not cid_ok else "正确"
    })

    # 5. job_id 正确（20分）
    jid_ok = data.get("job_id") == "job_002"
    details.append({
        "item": "job_id 为 job_002",
        "max_score": 20,
        "score": 20 if jid_ok else 0,
        "passed": jid_ok,
        "reason": f"实际值为 {data.get('job_id')}" if not jid_ok else "正确"
    })

    # 6. scheduled_time 正确（30分）
    time_ok = data.get("scheduled_time") == "2025-04-11T10:00:00"
    details.append({
        "item": "scheduled_time 为 2025-04-11T10:00:00",
        "max_score": 30,
        "score": 30 if time_ok else 0,
        "passed": time_ok,
        "reason": f"实际值为 {data.get('scheduled_time')}" if not time_ok else "正确"
    })

    total_score = sum(d["score"] for d in details)
    _write_score(details, total_score)

def _write_score(details, total):
    output = {
        "total_score": total,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(output, f, indent=2)
    print(f"Score written: {total}/100")

if __name__ == "__main__":
    verify()
