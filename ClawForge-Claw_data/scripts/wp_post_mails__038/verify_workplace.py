import os
import json
import sys

def verify(workspace: str) -> dict:
    details = []
    total = 0
    max_total = 100

    # 1. 检查目标文件是否存在 (10分)
    target_path = os.path.join(workspace, "ops", "approved_brief.json")
    file_exists = os.path.isfile(target_path)
    if file_exists:
        details.append({"item": "ops/approved_brief.json 存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件已创建"})
        total += 10
    else:
        details.append({"item": "ops/approved_brief.json 存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        # 如果文件不存在，后续检查无意义，直接返回
        return {"total_score": total, "details": details}

    # 2. 文件是否为合法JSON (10分)
    try:
        with open(target_path, "r") as f:
            data = json.load(f)
        details.append({"item": "JSON 格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "解析成功"})
        total += 10
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        details.append({"item": "JSON 格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {e}"})
        return {"total_score": total, "details": details}

    # 3. 是否包含键 "brief_code" (20分)
    if isinstance(data, dict) and "brief_code" in data:
        details.append({"item": "包含键 brief_code", "score": 20, "max_score": 20, "passed": True, "reason": "键存在"})
        total += 20
    else:
        details.append({"item": "包含键 brief_code", "score": 0, "max_score": 20, "passed": False, "reason": f"缺失键或不是字典，内容: {data}"})
        # 没有需要的键，无法继续
        return {"total_score": total, "details": details}

    # 4. 值是否等于 "APPROVED_BRIEF_038" (60分)
    expected = "APPROVED_BRIEF_038"
    actual = data["brief_code"]
    if isinstance(actual, str) and actual == expected:
        details.append({"item": "brief_code 值正确", "score": 60, "max_score": 60, "passed": True, "reason": f"值为 {actual}"})
        total += 60
    else:
        details.append({"item": "brief_code 值正确", "score": 0, "max_score": 60, "passed": False, "reason": f"期望 {expected}，实际 {actual}"})

    return {"total_score": total, "details": details}

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    # 写入结果
    result_path = os.path.join(workspace, "workplace_score.json")
    with open(result_path, "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
