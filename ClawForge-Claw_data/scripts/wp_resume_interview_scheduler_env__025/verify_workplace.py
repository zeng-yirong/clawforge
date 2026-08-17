import json
import os
import sys
from pathlib import Path

def verify(workspace: str) -> dict:
    result = {
        "total_score": 0,
        "details": []
    }
    workspace_path = Path(workspace)

    # -------------------- 1. 目录结构检查 (10分) --------------------
    dirs_ok = True
    ops_dir = workspace_path / "ops"
    if not ops_dir.is_dir():
        result["details"].append({
            "item": "ops目录存在",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "ops/ 目录不存在"
        })
        dirs_ok = False
    else:
        result["details"].append({
            "item": "ops目录存在",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "ops/ 目录已创建"
        })

    output_file = ops_dir / "interviews.json"
    if not output_file.is_file():
        result["details"].append({
            "item": "interviews.json文件存在",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "ops/interviews.json 文件不存在"
        })
        dirs_ok = False
    else:
        result["details"].append({
            "item": "interviews.json文件存在",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "ops/interviews.json 文件已创建"
        })

    if not dirs_ok:
        result["total_score"] = sum(d["score"] for d in result["details"])
        return result

    # -------------------- 2. 格式合法性与字段完整性 (30分) --------------------
    try:
        with open(output_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        result["details"].append({
            "item": "JSON格式正确",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON解析失败: {str(e)}"
        })
        result["total_score"] = sum(d["score"] for d in result["details"])
        return result

    if not isinstance(data, list):
        result["details"].append({
            "item": "顶层数据结构为列表",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "顶层不是列表，可能为对象或其他类型"
        })
        result["total_score"] = sum(d["score"] for d in result["details"])
        return result

    result["details"].append({
        "item": "顶层数据结构为列表",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "顶层是JSON数组"
    })

    # 检查元素个数
    if len(data) != 2:
        result["details"].append({
            "item": "数组元素个数为2",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"数组元素个数为 {len(data)}，应为2"
        })
        # 继续检查其他项不至于跳过
    else:
        result["details"].append({
            "item": "数组元素个数为2",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "数组包含2个元素"
        })

    # 检查每个对象的字段完整性（20分，每个对象10分）
    field_score = 0
    field_issues = []
    for i, entry in enumerate(data):
        if not isinstance(entry, dict):
            field_issues.append(f"元素{i}不是对象")
            continue
        has_job = "job_id" in entry
        has_candidate = "candidate_id" in entry
        has_time = "interview_time" in entry
        if not (has_job and has_candidate and has_time):
            missing = [f for f, flag in [("job_id", has_job), ("candidate_id", has_candidate), ("interview_time", has_time)] if not flag]
            field_issues.append(f"元素{i}缺少字段: {', '.join(missing)}")
        else:
            field_score += 10
    if field_score == 20:
        result["details"].append({
            "item": "每个对象字段完整（job_id, candidate_id, interview_time）",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "所有对象都包含所需字段"
        })
    else:
        result["details"].append({
            "item": "每个对象字段完整",
            "score": field_score,
            "max_score": 20,
            "passed": False,
            "reason": f"问题: {'; '.join(field_issues)}"
        })

    # -------------------- 3. 关键值正确性 (40分) --------------------
    # 构建对照表
    expected = {
        "J001": {"candidate_id": "C001", "interview_time": "2025-03-10T09:30"},
        "J002": {"candidate_id": "C006", "interview_time": "2025-03-10T10:00"}
    }
    # 将data转为字典方便查找
    got = {}
    for entry in data:
        if isinstance(entry, dict) and "job_id" in entry:
            got[entry["job_id"]] = entry

    correct_score = 0
    max_correct = 40  # 每个职位20分
    errors = []
    for jid, exp in expected.items():
        if jid not in got:
            errors.append(f"职位 {jid} 缺失")
            continue
        entry = got[jid]
        part_score = 0
        cid_ok = entry.get("candidate_id") == exp["candidate_id"]
        time_ok = entry.get("interview_time") == exp["interview_time"]
        if cid_ok and time_ok:
            part_score = 20
        elif cid_ok or time_ok:
            part_score = 10
        correct_score += part_score
        if not cid_ok:
            errors.append(f"职位 {jid}: 期望candidate_id={exp['candidate_id']}, 实际={entry.get('candidate_id')}")
        if not time_ok:
            errors.append(f"职位 {jid}: 期望interview_time={exp['interview_time']}, 实际={entry.get('interview_time')}")

    result["details"].append({
        "item": "关键值正确性（候选人ID和面试时间）",
        "score": correct_score,
        "max_score": max_correct,
        "passed": correct_score == max_correct,
        "reason": "全部正确" if correct_score == max_correct else f"部分错误: {'; '.join(errors)}"
    })

    # 总分计算
    total = sum(d["score"] for d in result["details"])
    result["total_score"] = total
    return result

if __name__ == "__main__":
    ws = sys.argv[1] if len(sys.argv) > 1 else "."
    res = verify(ws)
    print(json.dumps(res, indent=2))
    # 写入评分文件（仅当脚本被作为主程序运行时）
    with open(os.path.join(ws, "workplace_score.json"), "w") as f:
        json.dump(res, f, indent=2)
