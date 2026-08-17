import sys
import os
import json

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

def read_correct_answer():
    meta_path = os.path.join(workspace, ".meta", "correct_error_id.txt")
    if not os.path.exists(meta_path):
        return None
    with open(meta_path) as f:
        return f.read().strip()

def verify():
    correct_id = read_correct_answer()
    if correct_id is None:
        return {"total_score": 0, "details": [{"item": "meta file missing", "score": 0, "max_score": 100, "passed": False, "reason": "Correct answer file not found."}]}

    score = 0
    details = []

    # 1. 检查目录结构 (10分)
    dirs_ok = True
    for d in ["reproductions", os.path.join("knowledge", "archive")]:
        if not os.path.isdir(os.path.join(workspace, d)):
            dirs_ok = False
    if dirs_ok:
        score += 10
        details.append({"item": "Directory structure", "score": 10, "max_score": 10, "passed": True, "reason": "reproductions/ and knowledge/archive/ exist."})
    else:
        details.append({"item": "Directory structure", "score": 0, "max_score": 10, "passed": False, "reason": "Missing required directories."})

    # 2. 检查 reproductions/segfault_v3.2.1.json (20分)
    json1_path = os.path.join(workspace, "reproductions", "segfault_v3.2.1.json")
    json1_ok = False
    json1_reason = ""
    if os.path.exists(json1_path):
        try:
            with open(json1_path) as f:
                data = json.load(f)
            if isinstance(data, dict) and "error_id" in data:
                if data["error_id"] == correct_id:
                    json1_ok = True
                    json1_reason = "File exists, valid JSON, error_id matches."
                else:
                    json1_reason = f"error_id is '{data['error_id']}' but expected '{correct_id}'."
            else:
                json1_reason = "JSON does not contain 'error_id' key or is not a dict."
        except Exception as e:
            json1_reason = f"JSON parse error: {e}"
    else:
        json1_reason = "File does not exist."

    if json1_ok:
        score += 20
        details.append({"item": "reproductions/segfault_v3.2.1.json content", "score": 20, "max_score": 20, "passed": True, "reason": json1_reason})
    else:
        details.append({"item": "reproductions/segfault_v3.2.1.json content", "score": 0, "max_score": 20, "passed": False, "reason": json1_reason})

    # 3. 检查 knowledge/archive/segfault_v3.2.1_ledger.json (20分)
    json2_path = os.path.join(workspace, "knowledge", "archive", "segfault_v3.2.1_ledger.json")
    json2_ok = False
    json2_reason = ""
    if os.path.exists(json2_path):
        try:
            with open(json2_path) as f:
                data = json.load(f)
            if isinstance(data, dict) and "error_id" in data:
                if data["error_id"] == correct_id:
                    json2_ok = True
                    json2_reason = "File exists, valid JSON, error_id matches."
                else:
                    json2_reason = f"error_id is '{data['error_id']}' but expected '{correct_id}'."
            else:
                json2_reason = "JSON does not contain 'error_id' key or is not a dict."
        except Exception as e:
            json2_reason = f"JSON parse error: {e}"
    else:
        json2_reason = "File does not exist."

    if json2_ok:
        score += 20
        details.append({"item": "knowledge/archive/segfault_v3.2.1_ledger.json content", "score": 20, "max_score": 20, "passed": True, "reason": json2_reason})
    else:
        details.append({"item": "knowledge/archive/segfault_v3.2.1_ledger.json content", "score": 0, "max_score": 20, "passed": False, "reason": json2_reason})

    # 4. JSON 格式合法性（已在上面检查，但单独给10分，如果两个文件都合法则给10分）
    format_ok = json1_ok and json2_ok
    if format_ok:
        score += 10
        details.append({"item": "JSON format validity", "score": 10, "max_score": 10, "passed": True, "reason": "Both files are valid JSON."})
    else:
        details.append({"item": "JSON format validity", "score": 0, "max_score": 10, "passed": False, "reason": "At least one file is invalid JSON."})

    # 5. 核心数据正确性 (40分) - 这里上面已经部分给了，再额外给40分确保 error_id 完全正确
    # 实际上最关键是 error_id 一致，我们给一个额外大项
    core_ok = json1_ok and json2_ok
    if core_ok:
        score += 40
        details.append({"item": "Core error_id correctness", "score": 40, "max_score": 40, "passed": True, "reason": "Both files contain the correct error_id."})
    else:
        details.append({"item": "Core error_id correctness", "score": 0, "max_score": 40, "passed": False, "reason": "error_id mismatch or missing."})

    # 总分限制100
    total = min(score, 100)
    result = {
        "total_score": total,
        "details": details
    }
    # 写入 workplace_score.json
    out_path = os.path.join(workspace, "workplace_score.json")
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    return result

if __name__ == "__main__":
    res = verify()
    print(json.dumps(res, indent=2))
