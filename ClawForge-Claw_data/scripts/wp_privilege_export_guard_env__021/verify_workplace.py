import json
import os
import sys
from pathlib import Path

def verify_workplace(workspace: str) -> dict:
    score = 0
    details = []
    base = Path(workspace)

    # 1. ops 目录是否存在 (10分)
    ops_dir = base / "ops"
    if ops_dir.is_dir():
        details.append({"item": "ops directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "ops/ directory found"})
        score += 10
    else:
        details.append({"item": "ops directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "ops/ directory missing"})

    # 2. ops/deny_list.json 是否存在 (10分)
    deny_path = ops_dir / "deny_list.json"
    if deny_path.is_file():
        details.append({"item": "deny_list.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "file found"})
        score += 10
    else:
        details.append({"item": "deny_list.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "file not found"})
        # 如果文件不存在，后续检查全部跳过
        return {"total_score": score, "details": details}

    # 3. JSON 格式是否合法 (10分)
    try:
        with open(deny_path, "r") as f:
            data = json.load(f)
        details.append({"item": "valid JSON", "score": 10, "max_score": 10, "passed": True, "reason": "JSON parsed successfully"})
        score += 10
    except Exception as e:
        details.append({"item": "valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON parse error: {str(e)}"})
        return {"total_score": score, "details": details}

    # 4. 内容是否为列表 (10分)
    if isinstance(data, list):
        details.append({"item": "content is a list", "score": 10, "max_score": 10, "passed": True, "reason": "top-level structure is a list"})
        score += 10
    else:
        details.append({"item": "content is a list", "score": 0, "max_score": 10, "passed": False, "reason": f"expected list, got {type(data).__name__}"})
        return {"total_score": score, "details": details}

    # 5. 列表长度 (10分) —— 应有且仅有一个元素
    if len(data) == 1:
        details.append({"item": "list length is 1", "score": 10, "max_score": 10, "passed": True, "reason": "length is 1"})
        score += 10
    else:
        details.append({"item": "list length is 1", "score": 0, "max_score": 10, "passed": False, "reason": f"expected length 1, got {len(data)}"})

    # 6. 唯一元素是否为 'req_002' (30分)
    correct_id = "req_002"
    if len(data) == 1 and data[0] == correct_id:
        details.append({"item": "correct request ID", "score": 30, "max_score": 30, "passed": True, "reason": f"contains exactly '{correct_id}'"})
        score += 30
    elif len(data) == 1 and data[0] != correct_id:
        details.append({"item": "correct request ID", "score": 0, "max_score": 30, "passed": False, "reason": f"expected '{correct_id}', got '{data[0]}'"})
    elif len(data) > 1:
        # 如果长度不对，检查是否包含正确ID
        if correct_id in data:
            details.append({"item": "correct request ID", "score": 15, "max_score": 30, "passed": False, "reason": f"ID found but list contains extra items"})
            score += 15
        else:
            details.append({"item": "correct request ID", "score": 0, "max_score": 30, "passed": False, "reason": f"list does not contain '{correct_id}'"})
    else:
        details.append({"item": "correct request ID", "score": 0, "max_score": 30, "passed": False, "reason": "list is empty"})

    # 7. 无多余元素 (20分) —— 如果长度正好为1且正确，给满分；否则根据多余元素数量扣分
    if len(data) == 1 and data[0] == correct_id:
        details.append({"item": "no extra elements", "score": 20, "max_score": 20, "passed": True, "reason": "list contains only the required ID"})
        score += 20
    elif len(data) == 1 and data[0] != correct_id:
        details.append({"item": "no extra elements", "score": 0, "max_score": 20, "passed": False, "reason": "wrong element present"})
    elif len(data) > 1:
        extras = [x for x in data if x != correct_id]
        if extras:
            details.append({"item": "no extra elements", "score": 0, "max_score": 20, "passed": False, "reason": f"extra elements found: {extras}"})
        else:
            # 多个正确ID? 这里不应有重复
            details.append({"item": "no extra elements", "score": 10, "max_score": 20, "passed": False, "reason": "list has duplicate entries"})
            score += 5 if score > 0 else 0  # 给一部分分
    else:
        details.append({"item": "no extra elements", "score": 0, "max_score": 20, "passed": False, "reason": "list is empty"})

    return {"total_score": score, "details": details}

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify_workplace(workspace)
    # 写入到工作区
    output_path = Path(workspace) / "workplace_score.json"
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written to {output_path}")
