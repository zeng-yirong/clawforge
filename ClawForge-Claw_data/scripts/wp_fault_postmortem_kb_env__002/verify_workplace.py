import sys
import json
from pathlib import Path

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    base = Path(workspace)
    details = []
    total = 0

    # 1. ops 目录是否存在
    ops_dir = base / "ops"
    item1 = {"item": "ops 目录存在", "max_score": 10}
    if ops_dir.is_dir():
        item1["score"] = 10
        item1["passed"] = True
        item1["reason"] = "ops 目录存在"
    else:
        item1["score"] = 0
        item1["passed"] = False
        item1["reason"] = "ops 目录不存在"
    details.append(item1)
    total += item1["score"]

    # 2. ops/postmortem.json 文件存在
    pm_file = ops_dir / "postmortem.json"
    item2 = {"item": "postmortem JSON 文件存在", "max_score": 10}
    if pm_file.is_file():
        item2["score"] = 10
        item2["passed"] = True
        item2["reason"] = "postmortem.json 文件存在"
    else:
        item2["score"] = 0
        item2["passed"] = False
        item2["reason"] = "postmortem.json 不存在"
    details.append(item2)
    total += item2["score"]

    # 3. 文件是合法的 JSON
    item3 = {"item": "合法 JSON 语法", "max_score": 10}
    data = None
    if pm_file.is_file():
        try:
            with open(pm_file, "r") as f:
                data = json.load(f)
            item3["score"] = 10
            item3["passed"] = True
            item3["reason"] = "JSON 解析成功"
        except json.JSONDecodeError as e:
            item3["score"] = 0
            item3["passed"] = False
            item3["reason"] = f"JSON 解码错误: {str(e)}"
    else:
        item3["score"] = 0
        item3["passed"] = False
        item3["reason"] = "文件不存在，无法检查 JSON"
    details.append(item3)
    total += item3["score"]

    # 4. 包含 root_cause 字段
    item4 = {"item": "包含 root_cause 字段", "max_score": 10}
    if data is not None and isinstance(data, dict) and "root_cause" in data:
        item4["score"] = 10
        item4["passed"] = True
        item4["reason"] = f"root_cause 字段存在，值: {data['root_cause'][:50]}..."
    else:
        item4["score"] = 0
        item4["passed"] = False
        item4["reason"] = "root_cause 字段缺失"
    details.append(item4)
    total += item4["score"]

    # 5. 包含 repair_plan 字段
    item5 = {"item": "包含 repair_plan 字段", "max_score": 10}
    if data is not None and isinstance(data, dict) and "repair_plan" in data:
        item5["score"] = 10
        item5["passed"] = True
        item5["reason"] = f"repair_plan 字段存在，值: {data['repair_plan'][:50]}..."
    else:
        item5["score"] = 0
        item5["passed"] = False
        item5["reason"] = "repair_plan 字段缺失"
    details.append(item5)
    total += item5["score"]

    # 6. root_cause 值正确
    expected_root = "Missing index on account_transaction.transaction_date leads to table-level lock."
    item6 = {"item": "root_cause 值正确", "max_score": 25}
    if data is not None and isinstance(data, dict) and "root_cause" in data:
        if data["root_cause"] == expected_root:
            item6["score"] = 25
            item6["passed"] = True
            item6["reason"] = "与预期一致"
        else:
            item6["score"] = 0
            item6["passed"] = False
            item6["reason"] = f"预期: '{expected_root}', 实际: '{data['root_cause']}'"
    else:
        item6["score"] = 0
        item6["passed"] = False
        item6["reason"] = "无法检查，root_cause 字段缺失"
    details.append(item6)
    total += item6["score"]

    # 7. repair_plan 值正确
    expected_repair = "Add index on account_transaction.transaction_date."
    item7 = {"item": "repair_plan 值正确", "max_score": 25}
    if data is not None and isinstance(data, dict) and "repair_plan" in data:
        if data["repair_plan"] == expected_repair:
            item7["score"] = 25
            item7["passed"] = True
            item7["reason"] = "与预期一致"
        else:
            item7["score"] = 0
            item7["passed"] = False
            item7["reason"] = f"预期: '{expected_repair}', 实际: '{data['repair_plan']}'"
    else:
        item7["score"] = 0
        item7["passed"] = False
        item7["reason"] = "无法检查，repair_plan 字段缺失"
    details.append(item7)
    total += item7["score"]

    # 写入评分文件
    result = {"total_score": total, "details": details}
    score_file = base / "workplace_score.json"
    with open(score_file, "w") as f:
        json.dump(result, f, indent=2)
    print(f"评分完成: {total}/100")

if __name__ == "__main__":
    main()
