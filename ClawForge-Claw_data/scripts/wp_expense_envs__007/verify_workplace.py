#!/usr/bin/env python3
"""
验证 Agent 是否在 ops/overbudget.json 中正确输出了最大超支类别和金额。
满分 100，细粒度评分。
"""
import sys
import os
import json
import math

WORKSPACE = sys.argv[1] if len(sys.argv) > 1 else "."

def load_json(rel_path):
    full = os.path.join(WORKSPACE, rel_path)
    if not os.path.isfile(full):
        return None
    with open(full, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return None

def main():
    details = []
    total = 0
    max_total = 100

    # 1. 目录结构检查 (10分)
    ops_dir = os.path.join(WORKSPACE, "ops")
    if os.path.isdir(ops_dir):
        details.append({"item": "ops目录存在", "score": 10, "max_score": 10, "passed": True, "reason": "ops 目录已创建"})
        total += 10
    else:
        details.append({"item": "ops目录存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 ops 目录"})
        # 如果目录都不存在，直接返回，因为后面无法检查文件
        write_score(total, details)
        return

    # 2. 目标文件存在 (15分)
    target_path = os.path.join(WORKSPACE, "ops", "overbudget.json")
    if os.path.isfile(target_path):
        details.append({"item": "overbudget.json 文件存在", "score": 15, "max_score": 15, "passed": True, "reason": "文件已生成"})
        total += 15
    else:
        details.append({"item": "overbudget.json 文件存在", "score": 0, "max_score": 15, "passed": False, "reason": f"文件 {target_path} 不存在"})
        write_score(total, details)
        return

    # 3. JSON 合法性 (15分)
    data = load_json("ops/overbudget.json")
    if data is None:
        details.append({"item": "JSON 格式合法", "score": 0, "max_score": 15, "passed": False, "reason": "文件不是合法的 JSON"})
        write_score(total, details)
        return
    else:
        details.append({"item": "JSON 格式合法", "score": 15, "max_score": 15, "passed": True, "reason": "JSON 解析成功"})
        total += 15

    # 4. 包含必要字段 (20分)
    errors = []
    if not isinstance(data, dict):
        errors.append("顶层应该是 JSON 对象")
    else:
        if "category" not in data:
            errors.append("缺少字段 'category'")
        if "over_amount" not in data:
            errors.append("缺少字段 'over_amount'")
    if errors:
        details.append({"item": "包含 category 和 over_amount 字段", "score": 0, "max_score": 20, "passed": False, "reason": "; ".join(errors)})
        write_score(total, details)
        return
    else:
        details.append({"item": "包含 category 和 over_amount 字段", "score": 20, "max_score": 20, "passed": True, "reason": "必要字段齐全"})
        total += 20

    # 5. 类别值正确 (25分)
    expected_category = "住宿"
    if data.get("category") == expected_category:
        details.append({"item": "类别应为 '住宿'", "score": 25, "max_score": 25, "passed": True, "reason": f"category = '{data['category']}'"})
        total += 25
    else:
        details.append({"item": "类别应为 '住宿'", "score": 0, "max_score": 25, "passed": False, "reason": f"实际 category = '{data.get('category')}', 期望 '住宿'"})

    # 6. 超支金额精确正确 (15分)
    expected_amount = 300.0
    actual = data.get("over_amount")
    if isinstance(actual, (int, float)):
        if math.isclose(actual, expected_amount, rel_tol=1e-6):
            details.append({"item": "超支金额应为 300.0", "score": 15, "max_score": 15, "passed": True, "reason": f"over_amount = {actual}"})
            total += 15
        else:
            details.append({"item": "超支金额应为 300.0", "score": 0, "max_score": 15, "passed": False, "reason": f"实际 over_amount = {actual}, 期望 300.0"})
    else:
        details.append({"item": "超支金额应为 300.0", "score": 0, "max_score": 15, "passed": False, "reason": f"over_amount 类型或缺失"})

    # 最终
    write_score(total, details)

def write_score(score, details):
    result = {
        "total_score": score,
        "details": details
    }
    out_path = os.path.join(WORKSPACE, "workplace_score.json")
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score: {score}/100 written to {out_path}")

if __name__ == "__main__":
    main()
