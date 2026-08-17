import json, sys, os
from pathlib import Path

def main():
    workspace = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    total_score = 0
    details = []

    # 预期答案 (唯一)
    expected_ids = {"req_evil_001", "req_suspicious_002"}

    # 1. 检查目录结构 (10分)
    dirs_ok = True
    for d in ["data", "ops"]:
        if not (workspace / d).is_dir():
            dirs_ok = False
            details.append({"item": f"Directory '{d}' exists", "score": 0, "max_score": 5, "passed": False,
                            "reason": f"Missing directory: {d}"})
        else:
            details.append({"item": f"Directory '{d}' exists", "score": 5, "max_score": 5, "passed": True,
                            "reason": f"Found {d}/"})
    if dirs_ok:
        total_score += 10

    # 2. 检查产物文件 ops/denied_ids.json 是否存在 (10分)
    result_file = workspace / "ops" / "denied_ids.json"
    if not result_file.is_file():
        details.append({"item": "File 'ops/denied_ids.json' exists", "score": 0, "max_score": 10, "passed": False,
                        "reason": "File not found"})
        # 无法继续，给剩余分数0
        finalize(total_score, details)
        return
    else:
        details.append({"item": "File 'ops/denied_ids.json' exists", "score": 10, "max_score": 10, "passed": True,
                        "reason": "Found file"})
        total_score += 10

    # 3. 解析JSON合法性 (15分)
    try:
        with open(result_file, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        details.append({"item": "JSON parsing", "score": 0, "max_score": 15, "passed": False,
                        "reason": f"Invalid JSON: {e}"})
        finalize(total_score, details)
        return

    if not isinstance(data, list):
        details.append({"item": "JSON is an array", "score": 0, "max_score": 15, "passed": False,
                        "reason": "Root element is not an array"})
        finalize(total_score, details)
        return

    details.append({"item": "JSON is a valid array", "score": 15, "max_score": 15, "passed": True,
                    "reason": "Parsed successfully as list"})
    total_score += 15

    # 4. 检查数组内容 (50分)
    actual_ids = set()
    for item in data:
        if isinstance(item, str):
            actual_ids.add(item)
        else:
            # 非字符串元素，扣分
            pass
    # 无重复检查
    if len(actual_ids) != len(data):
        details.append({"item": "No duplicates in array", "score": 0, "max_score": 10, "passed": False,
                        "reason": f"Array contains {len(data)} elements but {len(actual_ids)} unique strings"})
        total_score -= 0  # 暂不扣分，后面处理
    else:
        details.append({"item": "No duplicates in array", "score": 10, "max_score": 10, "passed": True,
                        "reason": "All elements are unique strings"})
        total_score += 10

    # 内容匹配
    missing = expected_ids - actual_ids
    extra = actual_ids - expected_ids
    base_score = 40
    if missing or extra:
        reason_parts = []
        if missing:
            reason_parts.append(f"Missing IDs: {missing}")
        if extra:
            reason_parts.append(f"Extra IDs: {extra}")
        details.append({"item": "Result IDs match expected set", "score": 0, "max_score": 40, "passed": False,
                        "reason": "; ".join(reason_parts)})
    else:
        details.append({"item": "Result IDs match expected set", "score": 40, "max_score": 40, "passed": True,
                        "reason": f"Both contain {sorted(expected_ids)}"})
        total_score += 40

    # 5. 格式完整性：没有多余字段 (15分)
    # 只检查数组内是否都是字符串 (已检查), 且没有额外嵌套
    if all(isinstance(x, str) for x in data):
        details.append({"item": "All elements are strings (no extra structure)", "score": 15, "max_score": 15, "passed": True,
                        "reason": "Clean JSON array of strings"})
        total_score += 15
    else:
        details.append({"item": "All elements are strings (no extra structure)", "score": 0, "max_score": 15, "passed": False,
                        "reason": "Some elements are non-string"})

    finalize(total_score, details)

def finalize(total, details):
    total = min(total, 100)
    result = {"total_score": total, "details": details}
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score: {total}/100")

if __name__ == "__main__":
    main()
