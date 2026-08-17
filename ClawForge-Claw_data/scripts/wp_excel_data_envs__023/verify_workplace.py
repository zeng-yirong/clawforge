import sys
import json
import os

def load_json(filepath):
    with open(filepath, "r") as f:
        return json.load(f)

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results = []
    total_score = 0
    max_total = 100

    # 1. 文件存在检查 (10分)
    report_path = os.path.join(workspace, "report.json")
    if os.path.isfile(report_path):
        results.append({
            "item": "report.json 存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "文件存在"
        })
        total_score += 10
    else:
        results.append({
            "item": "report.json 存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件不存在"
        })
        # 后续无法检查，提前写结果
        final = {"total_score": total_score, "details": results}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(final, f, indent=2)
        return

    # 2. JSON格式合法 (10分)
    try:
        data = load_json(report_path)
        results.append({
            "item": "report.json JSON格式合法",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "格式正确"
        })
        total_score += 10
    except Exception as e:
        results.append({
            "item": "report.json JSON格式合法",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON解析失败: {e}"
        })
        final = {"total_score": total_score, "details": results}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(final, f, indent=2)
        return

    # 3. 包含 overall_avg (10分)
    if "overall_avg" in data:
        results.append({
            "item": "包含 overall_avg 字段",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "字段存在"
        })
        total_score += 10
    else:
        results.append({
            "item": "包含 overall_avg 字段",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "缺失字段"
        })

    # 4. overall_avg 数值正确 (20分)
    expected_avg = 563.33  # (1200+450+800+250+600+150+1100+320+200)/9 = 5070/9 ≈ 563.333...
    actual_avg = data.get("overall_avg")
    if actual_avg is not None and abs(actual_avg - expected_avg) < 0.01:
        results.append({
            "item": "整体平均订单金额 (overall_avg) 数值正确",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": f"值为 {actual_avg}"
        })
        total_score += 20
    else:
        results.append({
            "item": "整体平均订单金额 (overall_avg) 数值正确",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"期望 {expected_avg}, 实际 {actual_avg}"
        })

    # 5. 包含 summary 字段 (10分)
    if "summary" in data and isinstance(data["summary"], list):
        results.append({
            "item": "包含 summary 列表",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "字段存在且为列表"
        })
        total_score += 10
    else:
        results.append({
            "item": "包含 summary 列表",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "缺失或类型错误"
        })

    # 6. summary 条目数量及字段完整性 (10分)
    summary = data.get("summary", [])
    if len(summary) == 3:
        categories_ok = all(
            "category" in item and "total_sales" in item and "avg_order" in item
            for item in summary
        )
        if categories_ok:
            results.append({
                "item": "summary 包含3个类别且字段完整",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "结构正确"
            })
            total_score += 10
        else:
            results.append({
                "item": "summary 包含3个类别且字段完整",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": "字段缺失"
            })
    else:
        results.append({
            "item": "summary 包含3个类别且字段完整",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"条目数量为 {len(summary)}，期望3"
        })

    # 7. 类别汇总数值准确性 (30分，每个类别10分)
    expected_categories = {
        "Electronics": {"total_sales": 3100.0, "avg_order": 1033.33},
        "Clothing": {"total_sales": 1370.0, "avg_order": 456.67},
        "Food": {"total_sales": 600.0, "avg_order": 200.00}
    }
    for cat, expected in expected_categories.items():
        # 找到对应的条目
        match = [item for item in summary if item.get("category") == cat]
        if match:
            item = match[0]
            ts_ok = abs(item.get("total_sales", 0) - expected["total_sales"]) < 0.01
            ao_ok = abs(item.get("avg_order", 0) - expected["avg_order"]) < 0.01
            if ts_ok and ao_ok:
                results.append({
                    "item": f"类别 '{cat}' 的汇总数值正确",
                    "score": 10,
                    "max_score": 10,
                    "passed": True,
                    "reason": f"total_sales={item['total_sales']}, avg_order={item['avg_order']}"
                })
                total_score += 10
            else:
                results.append({
                    "item": f"类别 '{cat}' 的汇总数值正确",
                    "score": 0,
                    "max_score": 10,
                    "passed": False,
                    "reason": f"期望 total_sales={expected['total_sales']}, avg_order={expected['avg_order']}, 实际 total_sales={item.get('total_sales')}, avg_order={item.get('avg_order')}"
                })
        else:
            results.append({
                "item": f"类别 '{cat}' 的汇总数值正确",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": "未找到该类别条目"
            })

    # 写入最终评分
    final = {
        "total_score": total_score,
        "details": results
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(final, f, indent=2)

if __name__ == "__main__":
    main()
