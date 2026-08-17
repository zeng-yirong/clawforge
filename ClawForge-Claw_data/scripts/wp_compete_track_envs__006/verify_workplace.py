#!/usr/bin/env python3
import json
import os
import sys
import pathlib

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    wp = pathlib.Path(workspace)
    score_details = []

    # 1. 检查 ops/ 目录是否存在 (5分)
    ops_dir = wp / "ops"
    item = {"item": "ops 目录存在", "max_score": 5}
    if ops_dir.is_dir():
        item["score"] = 5
        item["passed"] = True
        item["reason"] = "ops 目录已创建"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = "ops 目录不存在"
    score_details.append(item)

    # 2. 检查 ops/priority_target.json 是否存在 (10分)
    target_file = ops_dir / "priority_target.json"
    item = {"item": "目标文件存在", "max_score": 10}
    if target_file.is_file():
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "priority_target.json 存在"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = "文件未找到"
    score_details.append(item)

    # 提前返回如果文件不存在，避免后续错误
    if not target_file.is_file():
        total = sum(it["score"] for it in score_details)
        result = {"total_score": total, "details": score_details}
        with open(wp / "workplace_score.json", "w") as f:
            json.dump(result, f, indent=2)
        print(f"总分: {total}/100")
        return

    # 3. 检查 JSON 是否合法 (10分)
    item = {"item": "JSON 格式合法", "max_score": 10}
    try:
        with open(target_file, "r") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError("top-level 不是 dict")
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "JSON 合法且为对象"
    except Exception as e:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = f"JSON 解析失败: {e}"
    score_details.append(item)

    if item["score"] != 10:
        # 如果 JSON 非法，后续字段无法检查，直接汇总
        total = sum(it["score"] for it in score_details)
        result = {"total_score": total, "details": score_details}
        with open(wp / "workplace_score.json", "w") as f:
            json.dump(result, f, indent=2)
        print(f"总分: {total}/100")
        return

    # 4. 检查必需字段存在 (competitor_id, name) (20分)
    item = {"item": "必需字段存在", "max_score": 20}
    missing = []
    if "competitor_id" not in data:
        missing.append("competitor_id")
    if "name" not in data:
        missing.append("name")
    if not missing:
        item["score"] = 20
        item["passed"] = True
        item["reason"] = "包含 competitor_id 和 name 字段"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = f"缺少字段: {', '.join(missing)}"
    score_details.append(item)

    if missing:
        total = sum(it["score"] for it in score_details)
        result = {"total_score": total, "details": score_details}
        with open(wp / "workplace_score.json", "w") as f:
            json.dump(result, f, indent=2)
        print(f"总分: {total}/100")
        return

    # 5. 检查 competitor_id 是否正确 (25分)
    expected_id = "comp_cloudmajor"
    item = {"item": "competitor_id 值正确", "max_score": 25}
    if data["competitor_id"] == expected_id:
        item["score"] = 25
        item["passed"] = True
        item["reason"] = f"competitor_id = '{expected_id}'"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = f"期望 '{expected_id}', 实际得到 '{data.get('competitor_id')}'"
    score_details.append(item)

    # 6. 检查 name 是否正确 (30分)
    expected_name = "CloudMajor"
    item = {"item": "name 值正确", "max_score": 30}
    if data["name"] == expected_name:
        item["score"] = 30
        item["passed"] = True
        item["reason"] = f"name = '{expected_name}'"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = f"期望 '{expected_name}', 实际得到 '{data.get('name')}'"
    score_details.append(item)

    # 计算总分
    total = sum(it["score"] for it in score_details)
    result = {"total_score": total, "details": score_details}
    with open(wp / "workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

    print(f"总分: {total}/100")
    for d in score_details:
        status = "✓" if d["passed"] else "✗"
        print(f"  {status} {d['item']}: {d['score']}/{d['max_score']} - {d['reason']}")

if __name__ == "__main__":
    main()
