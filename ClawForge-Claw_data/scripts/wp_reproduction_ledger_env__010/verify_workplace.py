import csv
import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Any

def load_json(path: str) -> Any:
    with open(path, "r") as f:
        return json.load(f)

def load_csv(path: str) -> List[Dict[str, str]]:
    rows = []
    with open(path, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows

def compute_expected(workspace: str) -> List[Dict[str, str]]:
    """
    根据工作区中的 project_docs.json 和 project_ledgers.csv 动态计算预期结果。
    """
    # 读取项目文档
    proj_docs_path = os.path.join(workspace, "data", "projects", "project_docs.json")
    proj_docs = load_json(proj_docs_path)["project_docs"]
    # 构建 project_id -> status 映射
    status_map = {doc["project_id"]: doc["status"] for doc in proj_docs}

    # 读取 CSV
    csv_path = os.path.join(workspace, "project_ledgers.csv")
    records = load_csv(csv_path)

    # 过滤: reproducibility == "yes" 且项目状态不为 "archived"
    valid_records = []
    for r in records:
        proj = r["project_name"]
        if r["reproducibility"] != "yes":
            continue
        if status_map.get(proj, "active") == "archived":
            continue
        valid_records.append(r)

    # 按项目分组，取日期最新的记录
    grouped: Dict[str, List[Dict]] = {}
    for r in valid_records:
        proj = r["project_name"]
        grouped.setdefault(proj, []).append(r)

    expected = []
    for proj, recs in grouped.items():
        # 按日期降序排序
        recs_sorted = sorted(recs, key=lambda x: x["reproduction_date"], reverse=True)
        best = recs_sorted[0]
        expected.append({
            "project_name": best["project_name"],
            "issue_id": best["issue_id"],
            "reproduction_date": best["reproduction_date"],
            "notes": best["notes"]
        })

    # 按 project_name 字母序升序
    expected.sort(key=lambda x: x["project_name"])
    return expected

def verify() -> Dict:
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    scores = []
    total = 0

    # 检查输出文件是否存在
    output_path = os.path.join(workspace, "ops", "reproduction_ledger_archive.json")
    if os.path.isfile(output_path):
        scores.append({"item": "Output file exists", "score": 10, "max_score": 10, "passed": True, "reason": "File found at ops/reproduction_ledger_archive.json"})
    else:
        scores.append({"item": "Output file exists", "score": 0, "max_score": 10, "passed": False, "reason": "File not found"})
        return {"total_score": total, "details": scores}

    # 加载并检查 JSON 合法性
    try:
        output = load_json(output_path)
        scores.append({"item": "Valid JSON", "score": 10, "max_score": 10, "passed": True, "reason": "JSON parse successful"})
    except Exception as e:
        scores.append({"item": "Valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON parse error: {e}"})
        return {"total_score": total, "details": scores}

    # 检查是否为列表
    if isinstance(output, list):
        scores.append({"item": "Output is a list", "score": 10, "max_score": 10, "passed": True, "reason": "Type is list"})
    else:
        scores.append({"item": "Output is a list", "score": 0, "max_score": 10, "passed": False, "reason": f"Got {type(output).__name__}"})
        return {"total_score": sum(s["score"] for s in scores), "details": scores}

    # 动态计算预期
    expected = compute_expected(workspace)

    # 检查长度
    if len(output) == len(expected):
        scores.append({"item": "Correct number of entries", "score": 10, "max_score": 10, "passed": True, "reason": f"Length {len(output)} matches expected {len(expected)}"})
    else:
        scores.append({"item": "Correct number of entries", "score": 0, "max_score": 10, "passed": False, "reason": f"Got {len(output)} entries, expected {len(expected)}"})
        # 仍然继续检查后续，但长度扣分

    # 检查每个条目是否包含所需字段
    required_fields = ["project_name", "issue_id", "reproduction_date", "notes"]
    field_ok = True
    for i, entry in enumerate(output):
        if not isinstance(entry, dict):
            field_ok = False
            break
        missing = [f for f in required_fields if f not in entry]
        if missing:
            field_ok = False
            break
    if field_ok:
        scores.append({"item": "All entries have required fields", "score": 10, "max_score": 10, "passed": True, "reason": "Every entry contains project_name, issue_id, reproduction_date, notes"})
    else:
        scores.append({"item": "All entries have required fields", "score": 0, "max_score": 10, "passed": False, "reason": "Missing required fields in some entries"})

    # 逐一比较内容（最多50分，每个正确条目20分，但总上限50）
    content_score = 0
    max_content = 50
    # 如果长度不一致，只比较共有部分
    common_len = min(len(output), len(expected))
    for i in range(common_len):
        if output[i] == expected[i]:
            content_score += 20
        else:
            # 部分正确也给予10分
            # 检查字段值是否匹配
            matched = all(output[i].get(f) == expected[i].get(f) for f in required_fields)
            if matched:
                content_score += 20  # 实际全匹配
            else:
                # 检查哪些字段匹配
                partial = sum(1 for f in required_fields if output[i].get(f) == expected[i].get(f))
                if partial >= 2:
                    content_score += 10
    # 限制最高50
    content_score = min(content_score, max_content)
    scores.append({"item": "Content match with expected", "score": content_score, "max_score": max_content, "passed": content_score == max_content, "reason": f"Partial score {content_score}/{max_content}"})

    # 额外：检查排序顺序（按 project_name 字母序）
    sort_ok = True
    for i in range(len(output) - 1):
        if output[i]["project_name"] > output[i+1]["project_name"]:
            sort_ok = False
            break
    if sort_ok:
        scores.append({"item": "Sorted alphabetically by project_name", "score": 10, "max_score": 10, "passed": True, "reason": "List is sorted ascending by project name"})
    else:
        scores.append({"item": "Sorted alphabetically by project_name", "score": 0, "max_score": 10, "passed": False, "reason": "List not sorted correctly"})

    total = sum(s["score"] for s in scores)
    return {"total_score": total, "details": scores}

if __name__ == "__main__":
    result = verify()
    # 写入 workplace_score.json
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    out_path = os.path.join(workspace, "workplace_score.json")
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    # 输出到 stderr 以便调试（可选）
    print(f"Score: {result['total_score']}/100", file=sys.stderr)
