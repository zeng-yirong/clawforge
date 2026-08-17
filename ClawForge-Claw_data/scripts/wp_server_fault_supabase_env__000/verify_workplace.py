import sys
import json
import os

def verify(workspace: str) -> dict:
    details = []
    total_score = 0

    # 1. 目录 ops 存在
    ops_dir = os.path.join(workspace, "ops")
    path_ok = os.path.isdir(ops_dir)
    details.append({
        "item": "ops directory exists",
        "score": 10 if path_ok else 0,
        "max_score": 10,
        "passed": path_ok,
        "reason": "ops/ found" if path_ok else "ops/ not found"
    })
    if not path_ok:
        total_score = sum(d["score"] for d in details)
        return {"total_score": total_score, "details": details}

    # 2. ops/kill_target.json 存在
    target_path = os.path.join(ops_dir, "kill_target.json")
    file_ok = os.path.isfile(target_path)
    details.append({
        "item": "ops/kill_target.json exists",
        "score": 10 if file_ok else 0,
        "max_score": 10,
        "passed": file_ok,
        "reason": "file exists" if file_ok else "file missing"
    })
    if not file_ok:
        total_score = sum(d["score"] for d in details)
        return {"total_score": total_score, "details": details}

    # 3. 合法 JSON
    try:
        with open(target_path, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        details.append({
            "item": "valid JSON content",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Invalid JSON: {e}"
        })
        total_score = sum(d["score"] for d in details)
        return {"total_score": total_score, "details": details}

    details.append({
        "item": "valid JSON content",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "JSON parse OK"
    })

    # 4. 包含 transaction_id 键且值为整数
    if "transaction_id" not in data:
        details.append({
            "item": "key 'transaction_id' present",
            "score": 0,
            "max_score": 30,
            "passed": False,
            "reason": "transaction_id key missing"
        })
        total_score = sum(d["score"] for d in details)
        return {"total_score": total_score, "details": details}

    val = data["transaction_id"]
    if not isinstance(val, int):
        details.append({
            "item": "transaction_id is integer",
            "score": 0,
            "max_score": 30,
            "passed": False,
            "reason": f"type is {type(val).__name__}, expected int"
        })
        total_score = sum(d["score"] for d in details)
        return {"total_score": total_score, "details": details}

    details.append({
        "item": "transaction_id present and integer",
        "score": 30,
        "max_score": 30,
        "passed": True,
        "reason": f"transaction_id = {val}"
    })

    # 5. 值等于 77138（正确答案）
    if val == 77138:
        details.append({
            "item": "transaction_id correct value 77138",
            "score": 30,
            "max_score": 30,
            "passed": True,
            "reason": "Correct transaction ID"
        })
    else:
        details.append({
            "item": "transaction_id correct value 77138",
            "score": 0,
            "max_score": 30,
            "passed": False,
            "reason": f"Got {val}, expected 77138"
        })

    # 6. 无多余键（防止 contain garbage）
    if len(data) == 1:
        details.append({
            "item": "no extra keys in JSON",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Only transaction_id present"
        })
    else:
        extra = [k for k in data if k != "transaction_id"]
        details.append({
            "item": "no extra keys in JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Extra keys: {extra}"
        })

    total_score = sum(d["score"] for d in details)
    return {"total_score": total_score, "details": details}

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))
