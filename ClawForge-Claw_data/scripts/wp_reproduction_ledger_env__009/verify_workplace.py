import sys
import os
import json
import csv
from pathlib import Path

def score_workplace(workspace: str):
    details = []
    total = 0
    max_total = 100

    # ---------- 1. 检查 ops/ledger.json 存在 ----------
    ledger_path = Path(workspace) / "ops" / "ledger.json"
    item = {"item": "产物文件存在", "max_score": 5, "score": 0, "passed": False, "reason": ""}
    if ledger_path.exists():
        item["score"] = 5
        item["passed"] = True
        item["reason"] = "ops/ledger.json 已创建"
    else:
        item["reason"] = "ops/ledger.json 不存在"
        details.append(item)
        # 直接返回总分 0
        total = 0
        write_score(total, details, workspace)
        return total
    details.append(item)
    total += 5

    # ---------- 2. 文件是合法 JSON ----------
    item = {"item": "JSON 合法性", "max_score": 10, "score": 0, "passed": False, "reason": ""}
    try:
        with open(ledger_path, "r") as f:
            data = json.load(f)
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "JSON 解析成功"
    except Exception as e:
        item["reason"] = f"JSON 解析失败: {str(e)}"
        details.append(item)
        total += 0
        write_score(total, details, workspace)
        return total
    details.append(item)
    total += 10

    # ---------- 3. 数据必须是列表 ----------
    item = {"item": "顶层数据结构为列表", "max_score": 5, "score": 0, "passed": False, "reason": ""}
    if isinstance(data, list):
        item["score"] = 5
        item["passed"] = True
        item["reason"] = "数据类型正确"
    else:
        item["reason"] = f"期望list，实际{type(data).__name__}"
    details.append(item)
    total += 5

    # ---------- 4. 列表元素个数 ----------
    item = {"item": "记录条目数 (应为2)", "max_score": 10, "score": 0, "passed": False, "reason": ""}
    if len(data) == 2:
        item["score"] = 10
        item["passed"] = True
        item["reason"] = f"得到 {len(data)} 条记录，正确"
    else:
        item["reason"] = f"期望2条，实际得到 {len(data)} 条"
    details.append(item)
    total += 10 if item["passed"] else 0

    # ---------- 5. 每个元素的字段完整性 ----------
    required_fields = {"project_id", "doc_title", "steps_summary", "outcome", "last_modified"}
    item = {"item": "每条记录包含所有必需字段", "max_score": 10, "score": 0, "passed": False, "reason": ""}
    all_ok = True
    missing_details = []
    for idx, rec in enumerate(data):
        fields = set(rec.keys())
        missing = required_fields - fields
        if missing:
            all_ok = False
            missing_details.append(f"记录{idx}缺失字段: {missing}")
    if all_ok:
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "所有字段完整"
    else:
        item["reason"] = "; ".join(missing_details)
    details.append(item)
    total += 10 if item["passed"] else 0

    # ---------- 6. 精确验证内容 ----------
    # 期望结果 (按任意顺序，我们标准化后比较)
    expected = [
        {
            "project_id": "projA",
            "doc_title": "Deployment Guide for ProjA",
            "steps_summary": "Update config; re-run regression suite",
            "outcome": "failure",
            "last_modified": "2025-04-18"
        },
        {
            "project_id": "projB",
            "doc_title": "API Integration Manual",
            "steps_summary": "Rollback to tag v1.2; redeploy",
            "outcome": "success",
            "last_modified": "2025-04-16"
        }
    ]
    # 将实际数据转为可比较的集合 (忽略顺序)
    actual_normalized = []
    for rec in data:
        norm = {
            "project_id": rec.get("project_id", ""),
            "doc_title": rec.get("doc_title", ""),
            "steps_summary": rec.get("steps_summary", ""),
            "outcome": rec.get("outcome", ""),
            "last_modified": rec.get("last_modified", "")
        }
        actual_normalized.append(norm)

    item = {"item": "内容精确匹配 (项目、标题、步骤、结果、时间)", "max_score": 60, "score": 0, "passed": False, "reason": ""}
    # 将期望和实际都按 project_id 排序后比较
    expected_sorted = sorted(expected, key=lambda x: x["project_id"])
    actual_sorted = sorted(actual_normalized, key=lambda x: x["project_id"])
    if actual_sorted == expected_sorted:
        item["score"] = 60
        item["passed"] = True
        item["reason"] = "所有记录内容完全正确"
    else:
        # 给出差异分析
        diff_reasons = []
        if len(actual_sorted) != len(expected_sorted):
            diff_reasons.append(f"条目数不同")
        else:
            for i in range(len(expected_sorted)):
                exp = expected_sorted[i]
                act = actual_sorted[i]
                for key in required_fields:
                    if act.get(key) != exp[key]:
                        diff_reasons.append(f"记录{i}的{key}: 期望'{exp[key]}', 实际'{act.get(key)}'")
        item["reason"] = "; ".join(diff_reasons) if diff_reasons else "内容不匹配"
        # 部分得分：每正确一个字段给 2 分，最多 60
        # 但为了简单，如果完全错误就给0
        # 我们可以计算匹配字段数
        total_correct_fields = 0
        total_possible_fields = len(expected_sorted) * 5  # 2条 * 5字段 = 10
        for exp in expected_sorted:
            for act in actual_sorted:
                if exp["project_id"] == act["project_id"]:
                    for key in required_fields:
                        if act.get(key) == exp[key]:
                            total_correct_fields += 1
        if total_correct_fields > 0:
            item["score"] = int(60 * total_correct_fields / total_possible_fields)
        else:
            item["score"] = 0
    details.append(item)
    total += item["score"]

    # ---------- 总分 ----------
    # 确保总分不超过100
    total = min(total, 100)
    write_score(total, details, workspace)
    return total

def write_score(total, details, workspace):
    score_file = Path(workspace) / "workplace_score.json"
    result = {
        "total_score": total,
        "details": details
    }
    with open(score_file, "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    ws = sys.argv[1] if len(sys.argv) > 1 else "."
    score_workplace(ws)
