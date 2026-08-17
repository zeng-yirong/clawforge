import sys
import os
import json

def read_file_or_none(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception:
        return None

def check_json_structure(data):
    if not isinstance(data, dict):
        return False, "root is not a JSON object"
    if "doc_id" not in data:
        return False, "missing 'doc_id'"
    if "title" not in data:
        return False, "missing 'title'"
    if "reproduction_steps" not in data:
        return False, "missing 'reproduction_steps'"
    if not isinstance(data["reproduction_steps"], list):
        return False, "'reproduction_steps' is not a list"
    return True, ""

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total = 0

    # 1. 检查 ops 目录是否存在 (5分)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        details.append({"item": "ops directory exists", "score": 5, "max_score": 5, "passed": True, "reason": "Found ops/"})
        total += 5
    else:
        details.append({"item": "ops directory exists", "score": 0, "max_score": 5, "passed": False, "reason": "ops/ not found"})

    # 2. 检查 reproduction_ledger.json 是否存在 (10分)
    ledger_path = os.path.join(workspace, "ops", "reproduction_ledger.json")
    if os.path.isfile(ledger_path):
        details.append({"item": "reproduction_ledger.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "File found"})
        total += 10
    else:
        details.append({"item": "reproduction_ledger.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "File not found"})
        # 如果文件不存在，后面无法检查，直接写结果返回
        score_record = {"total_score": total, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(score_record, f, indent=2)
        return

    # 3. 读取并验证JSON合法性 (10分)
    content = read_file_or_none(ledger_path)
    if content is None:
        details.append({"item": "JSON is valid", "score": 0, "max_score": 10, "passed": False, "reason": "Cannot read file"})
        score_record = {"total_score": total, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(score_record, f, indent=2)
        return
    try:
        data = json.loads(content)
        details.append({"item": "JSON is valid", "score": 10, "max_score": 10, "passed": True, "reason": "Parsed successfully"})
        total += 10
    except json.JSONDecodeError as e:
        details.append({"item": "JSON is valid", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON decode error: {e}"})
        score_record = {"total_score": total, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(score_record, f, indent=2)
        return

    # 4. 检查必要字段 (各15分)
    ok, msg = check_json_structure(data)
    if not ok:
        details.append({"item": "doc_id field present and correct", "score": 0, "max_score": 15, "passed": False, "reason": msg})
        details.append({"item": "title field present and correct", "score": 0, "max_score": 15, "passed": False, "reason": msg})
        details.append({"item": "reproduction_steps field present and is array", "score": 0, "max_score": 10, "passed": False, "reason": msg})
    else:
        # doc_id
        if data["doc_id"] == "doc_007":
            details.append({"item": "doc_id field present and correct", "score": 15, "max_score": 15, "passed": True, "reason": "doc_id is doc_007"})
            total += 15
        else:
            details.append({"item": "doc_id field present and correct", "score": 0, "max_score": 15, "passed": False, "reason": f"Expected doc_007, got {data['doc_id']}"})

        # title
        if data["title"] == "Memory Leak in Cache Layer":
            details.append({"item": "title field present and correct", "score": 15, "max_score": 15, "passed": True, "reason": "title matches"})
            total += 15
        else:
            details.append({"item": "title field present and correct", "score": 0, "max_score": 15, "passed": False, "reason": f"Expected 'Memory Leak in Cache Layer', got {data['title']}"})

        # reproduction_steps 是一个数组 (10分)
        steps = data["reproduction_steps"]
        if isinstance(steps, list):
            details.append({"item": "reproduction_steps field present and is array", "score": 10, "max_score": 10, "passed": True, "reason": f"Array with {len(steps)} elements"})
            total += 10
        else:
            details.append({"item": "reproduction_steps field present and is array", "score": 0, "max_score": 10, "passed": False, "reason": "Not a list"})
            steps = []  # 继续，避免后续错误

        # 5. 检查 steps 内容精确匹配 (35分)
        expected_steps = [
            "Start the cache server with default config.",
            "Send 10000 requests with large payloads.",
            "Observe memory usage > 1GB.",
            "Stop the server and restart.",
            "Memory not released."
        ]
        # 去除空白后比较
        cleaned_steps = [s.strip() for s in steps]
        if cleaned_steps == expected_steps:
            details.append({"item": "reproduction_steps content matches expected", "score": 35, "max_score": 35, "passed": True, "reason": "All steps exactly correct"})
            total += 35
        else:
            # 部分正确可给部分分？ 但为了简单，这里完全匹配才给满分，否则0分。也可以按匹配数量给分
            # 为体现梯度，计算匹配数量比例
            matches = sum(1 for i in range(min(len(cleaned_steps), len(expected_steps))) if cleaned_steps[i] == expected_steps[i])
            score_35 = min(35, int(35 * matches / len(expected_steps)))
            if matches == len(expected_steps) and len(cleaned_steps) == len(expected_steps):
                reason = f"All {matches} steps match exactly"
            else:
                reason = f"{matches}/{len(expected_steps)} steps match; expected {expected_steps}, got {cleaned_steps}"
            details.append({"item": "reproduction_steps content matches expected", "score": score_35, "max_score": 35, "passed": score_35 == 35, "reason": reason})
            total += score_35

    # 写入结果
    score_record = {"total_score": total, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(score_record, f, indent=2)

if __name__ == "__main__":
    main()
