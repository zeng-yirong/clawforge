#!/usr/bin/env python3
"""
验证 output/interview_plan.json 是否符合任务要求。
评分维度：
  - 目录存在 (10)
  - 文件存在 (10)
  - JSON 合法 (10)
  - job_id 与 job_title 正确 (10)
  - interviews 数量正确 (10)
  - 每位候选人信息正确 (40, 每人10)
  - 候选人顺序正确 (10)
总分 100。
"""
import sys
import os
import json

def verify(workspace):
    details = []
    total_score = 0

    # 1. 检查 output 目录是否存在
    output_dir = os.path.join(workspace, 'output')
    if os.path.isdir(output_dir):
        details.append({"item": "output目录存在", "score": 10, "max_score": 10, "passed": True, "reason": "output/ 目录存在"})
        total_score += 10
    else:
        details.append({"item": "output目录存在", "score": 0, "max_score": 10, "passed": False, "reason": "output/ 目录不存在"})
        # 后续检查跳过
        _write_score(total_score, details)
        return

    # 2. 检查文件是否存在
    plan_path = os.path.join(output_dir, 'interview_plan.json')
    if not os.path.isfile(plan_path):
        details.append({"item": "interview_plan.json存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        _write_score(total_score, details)
        return
    details.append({"item": "interview_plan.json存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
    total_score += 10

    # 3. 解析 JSON
    try:
        with open(plan_path, 'r') as f:
            data = json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        details.append({"item": "JSON合法性", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON解析失败: {str(e)}"})
        _write_score(total_score, details)
        return
    details.append({"item": "JSON合法性", "score": 10, "max_score": 10, "passed": True, "reason": "JSON格式正确"})
    total_score += 10

    # 4. 检查 job_id 和 job_title
    if not isinstance(data, dict):
        details.append({"item": "根结构为对象", "score": 0, "max_score": 10, "passed": False, "reason": "根不是JSON对象"})
        _write_score(total_score, details)
        return
    if data.get("job_id") != "J001" or data.get("job_title") != "Senior Data Engineer":
        details.append({"item": "job_id和job_title正确", "score": 0, "max_score": 10, "passed": False,
                        "reason": f"得到 job_id={data.get('job_id')}, job_title={data.get('job_title')}"})
        total_score += 0
    else:
        details.append({"item": "job_id和job_title正确", "score": 10, "max_score": 10, "passed": True, "reason": "匹配"})
        total_score += 10

    # 5. 检查 interviews 数量
    interviews = data.get("interviews", [])
    if not isinstance(interviews, list):
        details.append({"item": "interviews是列表", "score": 0, "max_score": 10, "passed": False, "reason": "interviews不是列表"})
        _write_score(total_score, details)
        return
    if len(interviews) != 4:
        details.append({"item": "interviews数量为4", "score": 0, "max_score": 10, "passed": False,
                        "reason": f"实际数量 {len(interviews)}"})
        total_score += 0
    else:
        details.append({"item": "interviews数量为4", "score": 10, "max_score": 10, "passed": True, "reason": "正确4个候选人"})
        total_score += 10

    # 6. 逐个候选人检查（预期顺序：Alice Wang C001, Charlie Chen C003, Eva Liu C005, Grace Zhao C007）
    expected = [
        {"candidate_id": "C001", "candidate_name": "Alice Wang", "interviewer_email": "smith@example.com"},
        {"candidate_id": "C003", "candidate_name": "Charlie Chen", "interviewer_email": "smith@example.com"},
        {"candidate_id": "C005", "candidate_name": "Eva Liu", "interviewer_email": "smith@example.com"},
        {"candidate_id": "C007", "candidate_name": "Grace Zhao", "interviewer_email": "smith@example.com"}
    ]
    for idx, exp in enumerate(expected):
        if idx >= len(interviews):
            break
        actual = interviews[idx]
        # 检查必需字段
        ok = True
        reason_parts = []
        for key in ["candidate_id", "candidate_name", "interviewer_email"]:
            if key not in actual:
                ok = False
                reason_parts.append(f"缺少字段'{key}'")
            elif actual[key] != exp[key]:
                ok = False
                reason_parts.append(f"字段'{key}'值应为'{exp[key]}'，实际'{actual[key]}'")
        if ok:
            details.append({"item": f"候选人{idx+1}正确", "score": 10, "max_score": 10, "passed": True,
                            "reason": f"匹配 {exp['candidate_name']}"})
            total_score += 10
        else:
            details.append({"item": f"候选人{idx+1}正确", "score": 0, "max_score": 10, "passed": False,
                            "reason": "; ".join(reason_parts)})

    # 7. 顺序检查（已在上面逐项验证顺序，若都通过则顺序正确）
    all_passed = all(d["passed"] for d in details[-4:])  # 最后4项是候选人
    if all_passed:
        details.append({"item": "候选人顺序正确", "score": 10, "max_score": 10, "passed": True, "reason": "按姓名A-Z排列"})
        total_score += 10
    else:
        details.append({"item": "候选人顺序正确", "score": 0, "max_score": 10, "passed": False, "reason": "顺序错误或部分候选人缺失"})

    _write_score(total_score, details)

def _write_score(score, details):
    # 确保得分不超过100
    score = min(score, 100)
    result = {
        "total_score": score,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"Total score: {score}/100")

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
