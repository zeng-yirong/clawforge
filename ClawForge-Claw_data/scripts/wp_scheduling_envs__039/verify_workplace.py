#!/usr/bin/env python
import sys
import json
import os

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total = 0

    # 1. 检查ops目录存在
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        details.append({"item": "ops目录存在", "score": 10, "max_score": 10, "passed": True, "reason": "ops目录已创建"})
        total += 10
    else:
        details.append({"item": "ops目录存在", "score": 0, "max_score": 10, "passed": False, "reason": "ops目录不存在"})

    # 2. 检查conflict_schedule.json文件存在
    file_path = os.path.join(ops_dir, "conflict_schedule.json")
    if os.path.isfile(file_path):
        details.append({"item": "文件conflict_schedule.json存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
        total += 10
    else:
        details.append({"item": "文件conflict_schedule.json存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        score = {"total_score": total, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(score, f, indent=2)
        return

    # 3. 解析JSON
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
        if isinstance(data, list):
            details.append({"item": "JSON格式合法且为数组", "score": 10, "max_score": 10, "passed": True, "reason": "JSON数组"})
            total += 10
        else:
            details.append({"item": "JSON格式合法且为数组", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON不是数组，而是{type(data).__name__}"})
            score = {"total_score": total, "details": details}
            with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
                json.dump(score, f, indent=2)
            return
    except Exception as e:
        details.append({"item": "JSON格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON解析失败: {e}"})
        score = {"total_score": total, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(score, f, indent=2)
        return

    # 4. 数组长度
    if len(data) == 2:
        details.append({"item": "数组长度为2", "score": 20, "max_score": 20, "passed": True, "reason": "长度正确"})
        total += 20
    else:
        details.append({"item": "数组长度为2", "score": 0, "max_score": 20, "passed": False, "reason": f"长度为{len(data)}"})

    # 5. 内容匹配
    expected_ids = {"sch_001", "sch_002"}
    actual_ids = set(data)
    if actual_ids == expected_ids:
        details.append({"item": "包含正确的冲突调度ID", "score": 40, "max_score": 40, "passed": True, "reason": f"包含{expected_ids}"})
        total += 40
    else:
        missing = expected_ids - actual_ids
        extra = actual_ids - expected_ids
        reason_parts = []
        if missing:
            reason_parts.append(f"缺少ID: {missing}")
        if extra:
            reason_parts.append(f"多余ID: {extra}")
        details.append({"item": "包含正确的冲突调度ID", "score": 0, "max_score": 40, "passed": False, "reason": "; ".join(reason_parts)})

    # 6. 所有元素均为字符串
    if all(isinstance(item, str) for item in data):
        details.append({"item": "所有元素均为字符串", "score": 10, "max_score": 10, "passed": True, "reason": "类型正确"})
        total += 10
    else:
        details.append({"item": "所有元素均为字符串", "score": 0, "max_score": 10, "passed": False, "reason": "存在非字符串元素"})

    # 写入结果
    score = {"total_score": total, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(score, f, indent=2)

if __name__ == "__main__":
    main()
