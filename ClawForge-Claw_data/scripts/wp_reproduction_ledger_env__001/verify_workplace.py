import sys
import os
import json

EXPECTED_STEPS = "1. Install version 2.3; 2. Run `./start.sh --debug`; 3. Observe log line 'ERROR DB'."
EXPECTED_RESULT = "Database connection fails consistently."
EXPECTED_DOC_ID = "doc_alpha_002"
EXPECTED_TITLE = "Reproduction Steps v2 (Correct)"
EXPECTED_ARCHIVED_BY = "Alice"

def verify_workplace(workspace):
    score = 0
    details = []
    total_max = 100

    # 1. 目录结构 (10分)
    archive_dir = os.path.join(workspace, "archive")
    dir_ok = os.path.isdir(archive_dir)
    if dir_ok:
        score += 10
        details.append({"item": "archive 目录存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录已创建"})
    else:
        details.append({"item": "archive 目录存在", "score": 0, "max_score": 10, "passed": False, "reason": "目录未找到"})
        return  # 后续依赖此目录，直接结束

    # 2. 文件存在 (10分)
    ledger_path = os.path.join(archive_dir, "reproduction_ledger.json")
    file_ok = os.path.isfile(ledger_path)
    if file_ok:
        score += 10
        details.append({"item": "reproduction_ledger.json 存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件已创建"})
    else:
        score += 0
        details.append({"item": "reproduction_ledger.json 存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        return

    # 3. JSON 合法性 (10分)
    try:
        with open(ledger_path, "r") as f:
            data = json.load(f)
        if isinstance(data, dict):
            score += 10
            details.append({"item": "JSON 格式合法且为对象", "score": 10, "max_score": 10, "passed": True, "reason": "解析成功"})
        else:
            score += 0
            details.append({"item": "JSON 格式合法且为对象", "score": 0, "max_score": 10, "passed": False, "reason": "根元素不是字典"})
            return
    except Exception as e:
        score += 0
        details.append({"item": "JSON 格式合法且为对象", "score": 0, "max_score": 10, "passed": False, "reason": f"解析异常: {str(e)}"})
        return

    # 4. 字段完整性 (10分)
    required_fields = ["doc_id", "title", "steps", "result", "archived_by"]
    missing = [f for f in required_fields if f not in data]
    if not missing:
        score += 10
        details.append({"item": "包含所有必需字段", "score": 10, "max_score": 10, "passed": True, "reason": "字段齐全"})
    else:
        score += 0
        details.append({"item": "包含所有必需字段", "score": 0, "max_score": 10, "passed": False, "reason": f"缺失字段: {missing}"})
        # 继续检查已有字段，不返回

    # 5. doc_id 正确 (15分)
    doc_id_ok = data.get("doc_id") == EXPECTED_DOC_ID
    score += 15 if doc_id_ok else 0
    details.append({
        "item": "doc_id 正确",
        "score": 15 if doc_id_ok else 0,
        "max_score": 15,
        "passed": doc_id_ok,
        "reason": f"期望 '{EXPECTED_DOC_ID}'，得到 '{data.get('doc_id')}'"
    })

    # 6. title 正确 (10分)
    title_ok = data.get("title") == EXPECTED_TITLE
    score += 10 if title_ok else 0
    details.append({
        "item": "title 正确",
        "score": 10 if title_ok else 0,
        "max_score": 10,
        "passed": title_ok,
        "reason": f"期望 '{EXPECTED_TITLE}'，得到 '{data.get('title')}'"
    })

    # 7. steps 正确 (15分)
    steps_value = data.get("steps", "")
    steps_ok = steps_value.strip() == EXPECTED_STEPS
    score += 15 if steps_ok else 0
    details.append({
        "item": "steps 内容正确",
        "score": 15 if steps_ok else 0,
        "max_score": 15,
        "passed": steps_ok,
        "reason": f"期望内容与提供的一致" if steps_ok else f"期望 '{EXPECTED_STEPS}'，得到 '{steps_value.strip()}'"
    })

    # 8. result 正确 (15分)
    result_value = data.get("result", "")
    result_ok = result_value.strip() == EXPECTED_RESULT
    score += 15 if result_ok else 0
    details.append({
        "item": "result 内容正确",
        "score": 15 if result_ok else 0,
        "max_score": 15,
        "passed": result_ok,
        "reason": f"期望内容与提供的一致" if result_ok else f"期望 '{EXPECTED_RESULT}'，得到 '{result_value.strip()}'"
    })

    # 9. archived_by 正确 (5分)
    archived_ok = data.get("archived_by") == EXPECTED_ARCHIVED_BY
    score += 5 if archived_ok else 0
    details.append({
        "item": "archived_by 正确",
        "score": 5 if archived_ok else 0,
        "max_score": 5,
        "passed": archived_ok,
        "reason": f"期望 '{EXPECTED_ARCHIVED_BY}'，得到 '{data.get('archived_by')}'"
    })

    # 写入评分
    result = {
        "total_score": score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify_workplace(workspace)
