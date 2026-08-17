import json
import os
import sys

def verify(workspace: str):
    score_details = []
    total = 0
    max_total = 100

    # ---------- 检查 ops/summary.json 是否存在且合法 ----------
    summary_path = os.path.join(workspace, "ops", "summary.json")
    if not os.path.isfile(summary_path):
        score_details.append({
            "item": "产物文件 ops/summary.json 存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件不存在"
        })
        # 后续无法检查，直接结束
        _write_score(workspace, 0, score_details)
        return

    try:
        with open(summary_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        score_details.append({
            "item": "产物文件 ops/summary.json 是合法 JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON 解析失败: {str(e)}"
        })
        _write_score(workspace, 0, score_details)
        return
    else:
        score_details.append({
            "item": "产物文件 ops/summary.json 是合法 JSON",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "JSON 格式正确"
        })
        total += 10

    # ---------- 检查字段结构 ----------
    required_fields = ["trip_id", "overbudget_items", "total_excess"]
    missing = [f for f in required_fields if f not in data]
    if missing:
        score_details.append({
            "item": "JSON 包含必要顶层字段 (trip_id, overbudget_items, total_excess)",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"缺少字段: {missing}"
        })
    else:
        score_details.append({
            "item": "JSON 包含必要顶层字段 (trip_id, overbudget_items, total_excess)",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "所有字段都存在"
        })
        total += 10

    # ---------- 检查 trip_id ----------
    if data.get("trip_id") != "TRIP-2024-011":
        score_details.append({
            "item": "trip_id 正确为 TRIP-2024-011",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"期望 'TRIP-2024-011'，实际 '{data.get('trip_id')}'"
        })
    else:
        score_details.append({
            "item": "trip_id 正确为 TRIP-2024-011",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "trip_id 匹配"
        })
        total += 10

    # ---------- 检查 overbudget_items ----------
    items = data.get("overbudget_items", [])
    if not isinstance(items, list):
        score_details.append({
            "item": "overbudget_items 是数组",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "overbudget_items 不是列表"
        })
        total += 0
        # 继续后续检查，但跳过 items 细节
    else:
        score_details.append({
            "item": "overbudget_items 是数组",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "类型正确"
        })
        total += 10

        # 预期超支项：accommodation (预算3200, 实际3400, 超200) 和 food (预算1000, 实际1200, 超200)
        expected_items = [
            {"category": "accommodation", "budget": 3200.0, "actual": 3400.0, "excess": 200.0},
            {"category": "food", "budget": 1000.0, "actual": 1200.0, "excess": 200.0}
        ]
        item_detail_score = 0
        item_detail_max = 30  # 每个项15分，共30分
        for idx, exp in enumerate(expected_items):
            found = None
            for act_item in items:
                if act_item.get("category") == exp["category"]:
                    found = act_item
                    break
            if found is None:
                score_details.append({
                    "item": f"超支项 {exp['category']} 存在",
                    "score": 0,
                    "max_score": 15,
                    "passed": False,
                    "reason": f"未找到 {exp['category']} 项"
                })
                continue

            # 检查 budget, actual, excess
            errors = []
            for key in ["budget", "actual", "excess"]:
                if abs(found.get(key, 0) - exp[key]) > 0.001:
                    errors.append(f"{key} 期望 {exp[key]}，实际 {found.get(key)}")
            if errors:
                score_details.append({
                    "item": f"超支项 {exp['category']} 数值正确",
                    "score": 0,
                    "max_score": 15,
                    "passed": False,
                    "reason": "; ".join(errors)
                })
            else:
                score_details.append({
                    "item": f"超支项 {exp['category']} 数值正确",
                    "score": 15,
                    "max_score": 15,
                    "passed": True,
                    "reason": f"{exp['category']} 各项数值匹配"
                })
                item_detail_score += 15
        total += item_detail_score

    # ---------- 检查 total_excess ----------
    expected_total_excess = 400.0
    if abs(data.get("total_excess", 0) - expected_total_excess) > 0.001:
        score_details.append({
            "item": "total_excess 正确为 400.0",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"期望 {expected_total_excess}，实际 {data.get('total_excess')}"
        })
    else:
        score_details.append({
            "item": "total_excess 正确为 400.0",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "total_excess 匹配"
        })
        total += 20

    # ---------- 总分 ----------
    _write_score(workspace, total, score_details)

def _write_score(workspace, total, details):
    score_path = os.path.join(workspace, "workplace_score.json")
    result = {
        "total_score": total,
        "details": details
    }
    with open(score_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
