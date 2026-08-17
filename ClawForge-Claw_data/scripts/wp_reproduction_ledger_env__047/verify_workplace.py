import os
import sys
import json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0

    # 1. 检查 ops 目录是否存在 (10分)
    ops_path = os.path.join(workspace, "ops")
    if os.path.isdir(ops_path):
        score_details.append({
            "item": "ops directory exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "ops/ directory found"
        })
    else:
        score_details.append({
            "item": "ops directory exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ops/ directory not found"
        })

    # 2. 检查 reproduction_ledger.json 是否存在 (15分)
    ledger_path = os.path.join(ops_path, "reproduction_ledger.json")
    if os.path.isfile(ledger_path):
        score_details.append({
            "item": "reproduction_ledger.json exists",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": "file exists at ops/reproduction_ledger.json"
        })
    else:
        score_details.append({
            "item": "reproduction_ledger.json exists",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": "file not found"
        })
        # 后续检查无法进行，提前返回
        _write_score(score_details, workspace)
        return

    # 3. 文件内容为合法 JSON (15分)
    try:
        with open(ledger_path, "r") as f:
            data = json.load(f)
        score_details.append({
            "item": "valid JSON format",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": "file parses as valid JSON"
        })
    except Exception as e:
        score_details.append({
            "item": "valid JSON format",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": f"JSON parse error: {str(e)}"
        })
        _write_score(score_details, workspace)
        return

    # 4. 包含 reproduction_id 字段 (20分)
    if isinstance(data, dict) and "reproduction_id" in data:
        score_details.append({
            "item": "reproduction_id field present",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": f"found reproduction_id: {data['reproduction_id']}"
        })
    else:
        score_details.append({
            "item": "reproduction_id field present",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "missing reproduction_id key or data is not a dict"
        })

    # 5. 包含 result 字段 (20分)
    if isinstance(data, dict) and "result" in data:
        score_details.append({
            "item": "result field present",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": f"found result: {data['result']}"
        })
    else:
        score_details.append({
            "item": "result field present",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "missing result key"
        })

    # 6. reproduction_id 值必须为 "RPT-047" (10分)
    if isinstance(data, dict):
        rid = data.get("reproduction_id", "")
        if rid == "RPT-047":
            score_details.append({
                "item": "reproduction_id value correct",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": f"value is 'RPT-047'"
            })
        else:
            score_details.append({
                "item": "reproduction_id value correct",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"expected 'RPT-047', got '{rid}'"
            })
    # 7. result 值必须为 "SUCCESS" (10分)
    if isinstance(data, dict):
        res = data.get("result", "")
        if res == "SUCCESS":
            score_details.append({
                "item": "result value correct",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": f"value is 'SUCCESS'"
            })
        else:
            score_details.append({
                "item": "result value correct",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"expected 'SUCCESS', got '{res}'"
            })
    # 8. 无多余字段 (bonus 不计分，但可以作为检查项，这里忽略)

    # 计算总分
    total_score = sum(item["score"] for item in score_details)
    _write_score(score_details, workspace)

def _write_score(details, workspace):
    total_score = sum(item["score"] for item in details)
    result = {
        "total_score": total_score,
        "details": details
    }
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Verification complete. Total score: {total_score}/100")

if __name__ == "__main__":
    main()
