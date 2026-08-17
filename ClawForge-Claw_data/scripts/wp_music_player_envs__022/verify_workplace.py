import os
import sys
import json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0

    # 1. 目录存在性 (ops目录)
    ops_dir = os.path.join(workspace, "ops")
    dir_pass = os.path.isdir(ops_dir)
    score_details.append({
        "item": "ops directory exists",
        "score": 10 if dir_pass else 0,
        "max_score": 10,
        "passed": dir_pass,
        "reason": "Directory ops/ found" if dir_pass else "Directory ops/ not found"
    })
    if dir_pass:
        total_score += 10

    # 2. 目标文件存在
    target_path = os.path.join(workspace, "ops", "valid_songs.json")
    file_pass = os.path.isfile(target_path)
    score_details.append({
        "item": "ops/valid_songs.json exists",
        "score": 10 if file_pass else 0,
        "max_score": 10,
        "passed": file_pass,
        "reason": "File ops/valid_songs.json found" if file_pass else "File ops/valid_songs.json not found"
    })
    if file_pass:
        total_score += 10

    # 如果文件不存在，直接返回
    if not file_pass:
        final_score = total_score
        save_score(workspace, final_score, score_details)
        return

    # 3. JSON合法性
    try:
        with open(target_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        json_pass = True
        reason_json = "Valid JSON"
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        json_pass = False
        reason_json = f"Invalid JSON: {e}"
    score_details.append({
        "item": "JSON parsing valid",
        "score": 10 if json_pass else 0,
        "max_score": 10,
        "passed": json_pass,
        "reason": reason_json
    })
    if json_pass:
        total_score += 10
    else:
        # JSON无效则停止后续检查
        final_score = total_score
        save_score(workspace, final_score, score_details)
        return

    # 4. 数据类型检查：必须是列表，且元素均为字符串
    type_pass = isinstance(data, list) and all(isinstance(x, str) for x in data)
    score_details.append({
        "item": "Data type is list of strings",
        "score": 10 if type_pass else 0,
        "max_score": 10,
        "passed": type_pass,
        "reason": "Result is a list of strings" if type_pass else f"Expected list of strings, got {type(data).__name__}"
    })
    if type_pass:
        total_score += 10

    # 如果类型不对，后续检查可能崩溃，跳过
    if not type_pass:
        final_score = total_score
        save_score(workspace, final_score, score_details)
        return

    # 5. 去重正确性：不能有重复元素
    unique_data = list(set(data))
    dedup_pass = len(unique_data) == len(data)
    score_details.append({
        "item": "No duplicate song IDs",
        "score": 20 if dedup_pass else 0,
        "max_score": 20,
        "passed": dedup_pass,
        "reason": f"No duplicates found (count={len(data)})" if dedup_pass else f"Duplicates detected: {len(data) - len(unique_data)} duplicates"
    })
    if dedup_pass:
        total_score += 20

    # 6. 过滤正确性：预期结果 ['s001','s002','s006']（去除无效时长和重复后）
    expected = ["s001", "s002", "s006"]
    filter_pass = sorted(data) == expected
    score_details.append({
        "item": "Filtered to valid songs only (duration>0, deduplicated)",
        "score": 30 if filter_pass else 0,
        "max_score": 30,
        "passed": filter_pass,
        "reason": f"Result matches expected {expected}" if filter_pass else f"Expected {expected}, got {sorted(data)}"
    })
    if filter_pass:
        total_score += 30

    # 7. 排序正确性：按字母顺序
    sort_pass = data == sorted(data)
    score_details.append({
        "item": "Sorted alphabetically",
        "score": 20 if sort_pass else 0,
        "max_score": 20,
        "passed": sort_pass,
        "reason": "List is sorted" if sort_pass else f"List is not sorted, order: {data}"
    })
    if sort_pass:
        total_score += 20

    # 写入最终评分
    final_score = total_score
    save_score(workspace, final_score, score_details)

def save_score(workspace, total, details):
    score_path = os.path.join(workspace, "workplace_score.json")
    score_data = {
        "total_score": total,
        "details": details
    }
    with open(score_path, "w", encoding="utf-8") as f:
        json.dump(score_data, f, ensure_ascii=False, indent=2)
    print(f"Score saved to {score_path}, total={total}")

if __name__ == "__main__":
    main()
