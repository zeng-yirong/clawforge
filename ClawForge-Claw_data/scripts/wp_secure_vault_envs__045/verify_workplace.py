import json
import csv
import os
import sys
from pathlib import Path

def verify(workspace: Path) -> dict:
    details = []
    total_score = 0

    # 1. 检查 ops 目录是否存在 (10分)
    ops_dir = workspace / "ops"
    item = {"item": "ops directory exists", "score": 0, "max_score": 10, "passed": False, "reason": ""}
    if ops_dir.is_dir():
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "ops/ directory found"
    else:
        item["reason"] = "ops/ directory not found"
    details.append(item)
    total_score += item["score"]

    # 2. ops/weak_passwords.json 存在且合法 JSON (10分)
    weak_json_path = ops_dir / "weak_passwords.json"
    item = {"item": "weak_passwords.json exists and valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": ""}
    if weak_json_path.is_file():
        try:
            with open(weak_json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                item["score"] = 10
                item["passed"] = True
                item["reason"] = f"valid JSON array with {len(data)} elements"
            else:
                item["reason"] = "JSON root is not a list"
        except json.JSONDecodeError as e:
            item["reason"] = f"invalid JSON: {e}"
    else:
        item["reason"] = "file not found"
    details.append(item)
    total_score += item["score"]

    # 3. weak_passwords.json 内容正确 (40分)：必须包含且只包含 [id1, id2, id4, id5]
    item = {"item": "weak_passwords.json contains correct IDs", "score": 0, "max_score": 40, "passed": False, "reason": ""}
    if weak_json_path.is_file():
        try:
            with open(weak_json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except:
            item["reason"] = "could not parse JSON"
            details.append(item)
            total_score += 0
            # 继续后续检查
        else:
            expected_ids = ["id1", "id2", "id4", "id5"]
            if isinstance(data, list):
                # 忽略顺序，去重比较
                actual = sorted(data)
                expected = sorted(expected_ids)
                if actual == expected:
                    item["score"] = 40
                    item["passed"] = True
                    item["reason"] = "IDs match exactly"
                else:
                    missing = set(expected) - set(actual)
                    extra = set(actual) - set(expected)
                    item["reason"] = f"mismatch: missing={sorted(missing)}, extra={sorted(extra)}"
            else:
                item["reason"] = "not a list"
    else:
        item["reason"] = "file not found"
    details.append(item)
    total_score += item["score"]

    # 4. ops/category_report.csv 存在 (10分)
    csv_path = ops_dir / "category_report.csv"
    item = {"item": "category_report.csv exists", "score": 0, "max_score": 10, "passed": False, "reason": ""}
    if csv_path.is_file():
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "file found"
    else:
        item["reason"] = "file not found"
    details.append(item)
    total_score += item["score"]

    # 5. category_report.csv 内容正确 (30分)
    item = {"item": "category_report.csv content matches expected statistics", "score": 0, "max_score": 30, "passed": False, "reason": ""}
    if csv_path.is_file():
        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
        except Exception as e:
            item["reason"] = f"could not parse CSV: {e}"
        else:
            # 期望数据：按类别排序（工作邮箱、电商平台、社交媒体、银行账户）
            expected = [
                {"category": "工作邮箱", "total": "2", "non_compliant": "2"},
                {"category": "电商平台", "total": "2", "non_compliant": "1"},
                {"category": "社交媒体", "total": "1", "non_compliant": "0"},
                {"category": "银行账户", "total": "1", "non_compliant": "1"},
            ]
            # 检查表头
            if reader.fieldnames != ["category", "total", "non_compliant"]:
                item["reason"] = f"header mismatch: {reader.fieldnames}"
            elif len(rows) != len(expected):
                item["reason"] = f"row count mismatch: expected {len(expected)}, got {len(rows)}"
            else:
                # 比较内容（忽略顺序，先转化为字典集合）
                expected_set = set((r["category"], r["total"], r["non_compliant"]) for r in expected)
                actual_set = set((r["category"], r["total"], r["non_compliant"]) for r in rows)
                if expected_set == actual_set:
                    item["score"] = 30
                    item["passed"] = True
                    item["reason"] = "CSV content correct"
                else:
                    missing = expected_set - actual_set
                    extra = actual_set - expected_set
                    item["reason"] = f"mismatch: missing={missing}, extra={extra}"
    else:
        item["reason"] = "file not found"
    details.append(item)
    total_score += item["score"]

    # 最终总分
    result = {
        "total_score": total_score,
        "details": details
    }
    return result

if __name__ == "__main__":
    workspace = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    result = verify(workspace)
    output_path = workspace / "workplace_score.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(json.dumps(result, indent=2, ensure_ascii=False))
