import sys
import os
import json

def verify(workspace):
    details = []
    total_score = 0

    # 1. 目录和文件存在 (10分)
    ledger_dir = os.path.join(workspace, "reproduction_ledger")
    ledger_file = os.path.join(ledger_dir, "ledger.json")
    if os.path.isdir(ledger_dir):
        details.append({"item": "reproduction_ledger directory exists", "score": 5, "max_score": 5, "passed": True, "reason": "目录存在"})
        total_score += 5
    else:
        details.append({"item": "reproduction_ledger directory exists", "score": 0, "max_score": 5, "passed": False, "reason": "目录未创建"})

    if os.path.isfile(ledger_file):
        details.append({"item": "ledger.json file exists", "score": 5, "max_score": 5, "passed": True, "reason": "文件存在"})
        total_score += 5
    else:
        details.append({"item": "ledger.json file exists", "score": 0, "max_score": 5, "passed": False, "reason": "文件未找到"})
        # 如果文件不存在，后续无法检查，直接返回
        score = sum(d["score"] for d in details)
        return {"total_score": score, "details": details}

    # 2. JSON 格式合法 (10分)
    try:
        with open(ledger_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            details.append({"item": "JSON is a list", "score": 10, "max_score": 10, "passed": True, "reason": "解析成功且为列表"})
            total_score += 10
        else:
            details.append({"item": "JSON is a list", "score": 0, "max_score": 10, "passed": False, "reason": "根元素不是列表"})
            return {"total_score": total_score, "details": details}
    except Exception as e:
        details.append({"item": "JSON is valid", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {e}"})
        return {"total_score": total_score, "details": details}

    # 3. 条目数 (20分)
    expected_count = 2
    actual_count = len(data)
    if actual_count == expected_count:
        details.append({"item": "Number of ledger entries", "score": 20, "max_score": 20, "passed": True, "reason": f"正确: {actual_count} 条"})
        total_score += 20
    else:
        details.append({"item": "Number of ledger entries", "score": 0, "max_score": 20, "passed": False, "reason": f"期望 2 条, 实际 {actual_count} 条"})

    # 4. 每条记录字段完整性 (20分)
    required_fields = {"doc_id", "title", "step_description", "result", "reproducer"}
    all_fields_ok = True
    for i, entry in enumerate(data):
        missing = required_fields - set(entry.keys())
        if missing:
            all_fields_ok = False
            details.append({"item": f"Entry {i} field completeness", "score": 0, "max_score": 10, "passed": False, "reason": f"缺少字段: {missing}"})
            break
    if all_fields_ok and len(data) > 0:
        details.append({"item": "All entries have required fields", "score": 20, "max_score": 20, "passed": True, "reason": "字段完整"})
        total_score += 20
    elif not all_fields_ok:
        pass  # 上面已经加了一个失败的 detail，但分数扣完
    else:
        details.append({"item": "All entries have required fields", "score": 0, "max_score": 20, "passed": False, "reason": "列表为空"})

    # 5. 内容正确性 (30分)
    # 预期结果：两条记录，按照 doc_id 排序（或任意顺序，但内容要匹配）
    # doc_alpha 对应最新记录（2025-03-02 09:00:00），step="Clean install with minimal config"，result="Startup crash observed"，reproducer="Noah Chen"
    # doc_beta 对应最新记录（2025-03-02 10:00:00），step="Run parser with 200KB input"，result="Memory leak confirmed"，reproducer="Eve Lee"
    expected_entries = [
        {
            "doc_id": "doc_alpha",
            "title": "Alpha Project Crash on Startup",
            "step_description": "Clean install with minimal config",
            "result": "Startup crash observed",
            "reproducer": "Noah Chen"
        },
        {
            "doc_id": "doc_beta",
            "title": "Beta Memory Leak in Parser",
            "step_description": "Run parser with 200KB input",
            "result": "Memory leak confirmed",
            "reproducer": "Eve Lee"
        }
    ]
    # 构建一个字典方便比对
    result_by_doc = {e["doc_id"]: e for e in data}
    correct_count = 0
    for exp in expected_entries:
        act = result_by_doc.get(exp["doc_id"])
        if act is None:
            continue
        if all(act.get(k) == v for k, v in exp.items()):
            correct_count += 1
    if correct_count == 2:
        details.append({"item": "Content accuracy", "score": 30, "max_score": 30, "passed": True, "reason": "两条记录内容完全正确"})
        total_score += 30
    elif correct_count == 1:
        details.append({"item": "Content accuracy", "score": 15, "max_score": 30, "passed": False, "reason": "只有一条记录内容正确"})
    else:
        details.append({"item": "Content accuracy", "score": 0, "max_score": 30, "passed": False, "reason": "无正确记录"})

    final_score = min(total_score, 100)
    return {"total_score": final_score, "details": details}

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))
