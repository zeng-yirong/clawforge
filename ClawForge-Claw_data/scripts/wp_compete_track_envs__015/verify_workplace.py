import sys
import os
import json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_info = {
        "total_score": 0,
        "details": []
    }

    # 辅助函数：累加分数
    def add_detail(item, score, max_score, passed, reason):
        score_info["details"].append({
            "item": item,
            "score": score,
            "max_score": max_score,
            "passed": passed,
            "reason": reason
        })
        score_info["total_score"] += score

    # ---------- 1. 检查 ops 目录是否存在 ----------
    ops_path = os.path.join(workspace, "ops")
    if os.path.isdir(ops_path):
        add_detail("ops/ directory exists", 5, 5, True, "ops/ found")
    else:
        add_detail("ops/ directory exists", 0, 5, False, "ops/ not found")
        # 如果目录不存在，后续检查无法进行，直接结束
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(score_info, f, indent=2)
        return

    # ---------- 2. 检查输出文件是否存在 ----------
    output_path = os.path.join(ops_path, "top_growth_competitors.json")
    if not os.path.isfile(output_path):
        add_detail("top_growth_competitors.json exists", 0, 10, False, "file not found")
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(score_info, f, indent=2)
        return
    add_detail("top_growth_competitors.json exists", 10, 10, True, "file found")

    # ---------- 3. 解析 JSON ----------
    try:
        with open(output_path, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        add_detail("JSON is valid", 0, 10, False, f"parse error: {str(e)}")
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(score_info, f, indent=2)
        return
    add_detail("JSON is valid", 10, 10, True, "valid JSON")

    # ---------- 4. 检查是否为数组，长度是否为3 ----------
    if not isinstance(data, list):
        add_detail("Output is a JSON array", 0, 10, False, f"expected list, got {type(data).__name__}")
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(score_info, f, indent=2)
        return
    add_detail("Output is a JSON array", 5, 5, True, "is list")
    add_detail("List length", 0, 5, False, f"length = {len(data)}")  # 稍后重新赋值

    expected_length = 3
    if len(data) == expected_length:
        # 覆盖上面的未通过记录
        # 移除之前添加的 length 细节
        score_info["details"] = [d for d in score_info["details"] if d["item"] != "List length"]
        add_detail("List length is 3", 5, 5, True, f"length = {len(data)}")
    else:
        score_info["details"] = [d for d in score_info["details"] if d["item"] != "List length"]
        add_detail("List length is 3", 0, 5, False, f"length = {len(data)}, expected 3")
        # 后续检查仍可进行，但已失分

    # ---------- 5. 检查每个条目是否包含必需字段 ----------
    required_fields = ["competitor_id", "name", "growth_rate", "market_share"]
    for i, item in enumerate(data):
        missing = [f for f in required_fields if f not in item]
        if missing:
            add_detail(f"Entry {i} has all required fields", 0, 5, False,
                       f"missing: {', '.join(missing)}")
        else:
            add_detail(f"Entry {i} has all required fields", 5, 5, True, "all fields present")

    # ---------- 6. 验证排序：growth_rate 降序 ----------
    growth_rates = [item.get("growth_rate") for item in data if "growth_rate" in item]
    if len(growth_rates) >= 2:
        sorted_ok = all(growth_rates[i] >= growth_rates[i+1] for i in range(len(growth_rates)-1))
        if sorted_ok:
            add_detail("Sorted by growth_rate descending", 10, 10, True, "order correct")
        else:
            add_detail("Sorted by growth_rate descending", 0, 10, False, "not sorted descending")
    else:
        add_detail("Sorted by growth_rate descending", 0, 10, False, "insufficient entries to verify order")

    # ---------- 7. 精确数值验证 ----------
    # 预期结果（按 growth_rate 降序，排除 market_cap<1000 和无效记录）：
    # 有效记录：C002 (DataFlow AI, growth=0.35, share=0.10)
    #          C001 (CloudMajor v2, growth=0.30, share=0.18)
    #          C004 (TechCorp, growth=0.20, share=0.20)
    expected_entries = [
        {"competitor_id": "C002", "name": "DataFlow AI", "growth_rate": 0.35, "market_share": 0.10},
        {"competitor_id": "C001", "name": "CloudMajor", "growth_rate": 0.30, "market_share": 0.18},
        {"competitor_id": "C004", "name": "TechCorp", "growth_rate": 0.20, "market_share": 0.20},
    ]

    for i, expected in enumerate(expected_entries):
        if i >= len(data):
            add_detail(f"Entry {i} exact match (position {i})", 0, 10, False, "missing entry")
            continue
        item = data[i]
        match = True
        reason_parts = []
        for field in required_fields:
            if item.get(field) != expected[field]:
                match = False
                reason_parts.append(f"{field}: got {item.get(field)}, expected {expected[field]}")
        if match:
            add_detail(f"Entry {i} exact match", 10, 10, True, "values correct")
        else:
            add_detail(f"Entry {i} exact match", 0, 10, False, "; ".join(reason_parts))

    # ---------- 写入最终分数 ----------
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(score_info, f, indent=2)

if __name__ == "__main__":
    main()
