import sys
import json
import os
import math

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    scores_path = os.path.join(workspace, "performance", "scores_202501.json")
    details = []
    total_score = 0
    max_total = 100

    # 1. 检查 performance 目录存在 (10分)
    perf_dir = os.path.join(workspace, "performance")
    dir_exists = os.path.isdir(perf_dir)
    details.append({
        "item": "performance directory exists",
        "score": 10 if dir_exists else 0,
        "max_score": 10,
        "passed": dir_exists,
        "reason": "" if dir_exists else "performance/ directory not found"
    })
    if dir_exists:
        total_score += 10

    # 2. 检查 scores_202501.json 文件存在 (10分)
    file_exists = os.path.isfile(scores_path)
    details.append({
        "item": "scores_202501.json file exists",
        "score": 10 if file_exists else 0,
        "max_score": 10,
        "passed": file_exists,
        "reason": "" if file_exists else "File not found at performance/scores_202501.json"
    })
    if file_exists:
        total_score += 10

    # 3. 检查 JSON 语法合法 (10分)
    valid_json = False
    data = None
    if file_exists:
        try:
            with open(scores_path, "r") as f:
                data = json.load(f)
            valid_json = True
        except (json.JSONDecodeError, ValueError):
            valid_json = False
    details.append({
        "item": "JSON syntax valid",
        "score": 10 if valid_json else 0,
        "max_score": 10,
        "passed": valid_json,
        "reason": "" if valid_json else "Invalid JSON content"
    })
    if valid_json:
        total_score += 10

    # 4. 检查是否为数组 (10分)
    is_list = isinstance(data, list) if valid_json else False
    details.append({
        "item": "root element is an array",
        "score": 10 if is_list else 0,
        "max_score": 10,
        "passed": is_list,
        "reason": "" if is_list else "Root is not a list"
    })
    if is_list:
        total_score += 10

    # 5. 检查每条记录包含必要字段 (10分)
    all_fields_ok = False
    if is_list:
        required_fields = {"employee_id", "total_score"}
        all_fields_ok = all(
            isinstance(entry, dict) and required_fields.issubset(entry.keys())
            for entry in data
        )
        # 同时检查无多余字段（可选，但扣分？这里作为加分项，但为简单只检查必要字段）
        # 我们额外检查 extra fields for strictness
        if all_fields_ok:
            for entry in data:
                if set(entry.keys()) != required_fields:
                    all_fields_ok = False
                    break
    details.append({
        "item": "each entry has employee_id and total_score (no extra fields)",
        "score": 10 if all_fields_ok else 0,
        "max_score": 10,
        "passed": all_fields_ok,
        "reason": "" if all_fields_ok else "Missing required fields or extra fields present"
    })
    if all_fields_ok:
        total_score += 10

    # 6. 检查员工数量应为3 (20分)
    correct_count = False
    if is_list:
        correct_count = len(data) == 3
    details.append({
        "item": "number of entries (should be 3)",
        "score": 20 if correct_count else 0,
        "max_score": 20,
        "passed": correct_count,
        "reason": f"Found {len(data) if is_list else 'N/A'} entries, expected 3" if not correct_count else ""
    })
    if correct_count:
        total_score += 20

    # 7. 检查具体员工得分 (每个10分，共30分)
    # 预期结果 (手动计算)
    expected = {
        "emp001": 100 * 0.5 + 80 * 0.3 + 90 * 0.2,   # 50 + 24 + 18 = 92
        "emp002": 90 * 0.5 + 85 * 0.3 + 70 * 0.2,    # 45 + 25.5 + 14 = 84.5
        "emp003": 70 * 0.4 + 90 * 0.4 + 80 * 0.2,    # 28 + 36 + 16 = 80
    }
    scores_ok = True
    if correct_count and all_fields_ok:
        for entry in data:
            eid = entry["employee_id"]
            score = entry["total_score"]
            if eid in expected and math.isclose(score, expected[eid], rel_tol=1e-9):
                continue
            else:
                scores_ok = False
                break
    details.append({
        "item": "all employee scores match expected values",
        "score": 30 if scores_ok else 0,
        "max_score": 30,
        "passed": scores_ok,
        "reason": "" if scores_ok else "One or more scores are incorrect"
    })
    if scores_ok:
        total_score += 30

    # 汇总
    result = {
        "total_score": total_score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score: {total_score}/{max_total}")

if __name__ == "__main__":
    main()
