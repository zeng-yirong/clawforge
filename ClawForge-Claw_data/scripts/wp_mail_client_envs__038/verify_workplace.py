import json
import os
import sys
from pathlib import Path

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    ws = Path(workspace)

    details = []
    total_score = 0
    max_total = 100

    # 1. result目录是否存在 (10分)
    result_dir = ws / "result"
    if result_dir.is_dir():
        details.append({"item": "result/ 目录存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录已创建"})
        total_score += 10
    else:
        details.append({"item": "result/ 目录存在", "score": 0, "max_score": 10, "passed": False, "reason": "目录不存在"})
        # 如果目录都不存在，后续检查无法进行，直接结束
        write_score(total_score, details)
        return

    # 2. urgent_ids.json 文件存在 (20分)
    target_file = result_dir / "urgent_ids.json"
    if target_file.is_file():
        details.append({"item": "result/urgent_ids.json 文件存在", "score": 20, "max_score": 20, "passed": True, "reason": "文件已创建"})
        total_score += 20
    else:
        details.append({"item": "result/urgent_ids.json 文件存在", "score": 0, "max_score": 20, "passed": False, "reason": "文件不存在"})
        write_score(total_score, details)
        return

    # 3. 文件是否为合法JSON (20分)
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        details.append({"item": "JSON格式合法", "score": 20, "max_score": 20, "passed": True, "reason": "解析成功"})
        total_score += 20
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        details.append({"item": "JSON格式合法", "score": 0, "max_score": 20, "passed": False, "reason": f"解析失败: {str(e)}"})
        write_score(total_score, details)
        return

    # 4. 包含ids字段且为list (20分)
    if isinstance(data, dict) and "ids" in data and isinstance(data["ids"], list):
        details.append({"item": "包含ids字段且为列表", "score": 20, "max_score": 20, "passed": True, "reason": "字段存在且类型正确"})
        total_score += 20
    else:
        details.append({"item": "包含ids字段且为列表", "score": 0, "max_score": 20, "passed": False, "reason": "缺失或类型错误"})
        write_score(total_score, details)
        return

    # 5. ids内容正确 (30分)
    expected_ids = ["e001", "e004"]
    actual_ids = sorted(data["ids"])
    expected_sorted = sorted(expected_ids)
    if actual_ids == expected_sorted:
        details.append({"item": "ids列表内容正确", "score": 30, "max_score": 30, "passed": True, "reason": f"匹配: {actual_ids}"})
        total_score += 30
    else:
        details.append({"item": "ids列表内容正确", "score": 0, "max_score": 30, "passed": False, "reason": f"预期 {expected_sorted}, 实际 {actual_ids}"})

    write_score(total_score, details)

def write_score(score, details):
    result = {"total_score": score, "details": details}
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
