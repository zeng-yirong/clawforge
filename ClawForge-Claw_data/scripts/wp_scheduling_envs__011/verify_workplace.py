import json
import os
import sys

def verify(workspace):
    details = []
    total_score = 0
    max_total = 100

    # 1. 检查目录结构是否存在
    required_dirs = ["data", "ops", "logs"]
    for d in required_dirs:
        path = os.path.join(workspace, d)
        exists = os.path.isdir(path)
        details.append({
            "item": f"Directory '{d}' exists",
            "score": 10 if exists else 0,
            "max_score": 10,
            "passed": exists,
            "reason": "Found" if exists else "Not found"
        })
        if exists:
            total_score += 10

    # 2. 检查ops/conflict_schedules.json文件存在
    result_path = os.path.join(workspace, "ops", "conflict_schedules.json")
    file_exists = os.path.isfile(result_path)
    details.append({
        "item": "File 'ops/conflict_schedules.json' exists",
        "score": 20 if file_exists else 0,
        "max_score": 20,
        "passed": file_exists,
        "reason": "Found" if file_exists else "Not found"
    })
    if file_exists:
        total_score += 20

    # 3. 检查文件是否合法JSON
    if file_exists:
        try:
            with open(result_path, "r") as f:
                data = json.load(f)
            is_valid_json = True
            reason = "Valid JSON"
        except (json.JSONDecodeError, Exception) as e:
            data = None
            is_valid_json = False
            reason = f"Invalid JSON: {str(e)}"
        details.append({
            "item": "File is valid JSON",
            "score": 20 if is_valid_json else 0,
            "max_score": 20,
            "passed": is_valid_json,
            "reason": reason
        })
        if is_valid_json:
            total_score += 20
    else:
        details.append({
            "item": "File is valid JSON",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "File missing, cannot parse"
        })

    # 4. 检查内容是否为列表且包含正确ID
    if file_exists and is_valid_json:
        if not isinstance(data, list):
            details.append({
                "item": "Content is a list",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": "Content is not a list"
            })
            total_score += 0
        else:
            # 读取预期答案
            expected_path = os.path.join(workspace, "ops", ".expected.json")
            if os.path.exists(expected_path):
                with open(expected_path, "r") as f:
                    expected = json.load(f)
            else:
                # fallback: 硬编码（同builder）
                expected = ["sched_001","sched_002","sched_003","sched_009"]
            # 检查是否恰好是这些ID（顺序无关）
            actual_sorted = sorted(data)
            expected_sorted = sorted(expected)
            if actual_sorted == expected_sorted and len(actual_sorted) == len(expected_sorted):
                score = 30
                passed = True
                reason = f"Correct IDs: {actual_sorted}"
            elif set(actual_sorted) == set(expected_sorted) and len(actual_sorted) == len(expected_sorted):
                # 顺序不同但内容相同
                score = 25
                passed = True
                reason = f"Correct IDs but order differs: {actual_sorted}"
            else:
                # 部分正确：计算交集
                correct = set(actual_sorted) & set(expected_sorted)
                if len(correct) > 0:
                    score = max(5, int(30 * len(correct) / len(expected)))
                    passed = False
                    reason = f"Partial match. Found {sorted(correct)}, missing {sorted(set(expected)-set(actual_sorted))}, extra {sorted(set(actual_sorted)-set(expected))}"
                else:
                    score = 0
                    passed = False
                    reason = f"Completely wrong. Expected {expected_sorted}, got {actual_sorted}"
            details.append({
                "item": "Conflict schedule IDs correct",
                "score": score,
                "max_score": 30,
                "passed": passed,
                "reason": reason
            })
            total_score += score
    else:
        details.append({
            "item": "Conflict schedule IDs correct",
            "score": 0,
            "max_score": 30,
            "passed": False,
            "reason": "File not available"
        })

    # 5. 检查结果文件中没有多余字段（如对象等）
    if file_exists and is_valid_json and isinstance(data, list):
        # 检查每个元素是否为字符串
        all_strings = all(isinstance(x, str) for x in data)
        if all_strings:
            # 已包含在上面的正确性检查，这里给格式分
            score = 10
            passed = True
            reason = "All elements are strings"
        else:
            score = 0
            passed = False
            reason = f"Non-string elements found: {[x for x in data if not isinstance(x, str)]}"
        details.append({
            "item": "Result list contains only strings",
            "score": score,
            "max_score": 10,
            "passed": passed,
            "reason": reason
        })
        total_score += score
    else:
        details.append({
            "item": "Result list contains only strings",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Not applicable"
        })

    # 总分上限100
    total_score = min(total_score, 100)
    result = {
        "total_score": total_score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
