import os
import sys
import json

def verify(workspace):
    results = []
    total_score = 0

    # 1. 目录结构检查 (10分)
    required_dirs = ["ops", "data", "data/pricing", "data/skus", "data/brands"]
    for d in required_dirs:
        path = os.path.join(workspace, d)
        if os.path.isdir(path):
            results.append({
                "item": f"目录 {d} 存在",
                "score": 10 // len(required_dirs),
                "max_score": 10 // len(required_dirs),
                "passed": True,
                "reason": ""
            })
            total_score += 10 // len(required_dirs)
        else:
            results.append({
                "item": f"目录 {d} 存在",
                "score": 0,
                "max_score": 10 // len(required_dirs),
                "passed": False,
                "reason": f"目录 {d} 未找到"
            })

    # 2. 产物文件是否存在 (10分)
    report_path = os.path.join(workspace, "ops", "competitive_report.json")
    if os.path.isfile(report_path):
        results.append({
            "item": "ops/competitive_report.json 存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": ""
        })
        total_score += 10
    else:
        results.append({
            "item": "ops/competitive_report.json 存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件未找到"
        })
        # 如果文件不存在，后续检查无法进行，直接返回
        final_score = total_score
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": final_score, "details": results}, f, indent=2)
        return

    # 3. JSON 合法性 (10分)
    try:
        with open(report_path, "r") as f:
            report = json.load(f)
        results.append({
            "item": "JSON 格式合法",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": ""
        })
        total_score += 10
    except Exception as e:
        results.append({
            "item": "JSON 格式合法",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"解析失败: {str(e)}"
        })
        final_score = total_score
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": final_score, "details": results}, f, indent=2)
        return

    # 4. 字段完整性 (20分) — 检查关键字段
    required_fields = ["report_id", "brand", "region", "price_book_version", "skus", "summary"]
    missing_fields = [f for f in required_fields if f not in report]
    if not missing_fields:
        results.append({
            "item": "报告包含全部必需字段",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": ""
        })
        total_score += 20
    else:
        results.append({
            "item": "报告包含全部必需字段",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"缺少字段: {', '.join(missing_fields)}"
        })

    # 5. 字段值正确性 (50分)
    # 5.1 report_id (5分)
    if report.get("report_id") == "CMP-APAC-LuminaSkin-020":
        results.append({
            "item": "report_id 正确",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": ""
        })
        total_score += 5
    else:
        results.append({
            "item": "report_id 正确",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": f"期望 CMP-APAC-LuminaSkin-020，得到 {report.get('report_id')}"
        })

    # 5.2 brand (5分)
    if report.get("brand") == "LuminaSkin":
        results.append({
            "item": "brand 正确",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": ""
        })
        total_score += 5
    else:
        results.append({
            "item": "brand 正确",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": f"期望 LuminaSkin，得到 {report.get('brand')}"
        })

    # 5.3 region (5分)
    if report.get("region") == "APAC":
        results.append({
            "item": "region 正确",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": ""
        })
        total_score += 5
    else:
        results.append({
            "item": "region 正确",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": f"期望 APAC，得到 {report.get('region')}"
        })

    # 5.4 price_book_version (5分)
    if report.get("price_book_version") == "APAC-Q2-2026-LIVE":
        results.append({
            "item": "price_book_version 正确",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": ""
        })
        total_score += 5
    else:
        results.append({
            "item": "price_book_version 正确",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": f"期望 APAC-Q2-2026-LIVE，得到 {report.get('price_book_version')}"
        })

    # 5.5 skus 内容 (25分)
    skus = report.get("skus", [])
    if not isinstance(skus, list):
        results.append({
            "item": "skus 是数组",
            "score": 0,
            "max_score": 25,
            "passed": False,
            "reason": "skus 字段不是数组"
        })
    else:
        # 期望3个 active LuminaSkin SKU
        expected_sku_ids = ["LS-001", "LS-002", "LS-003"]
        actual_sku_ids = sorted([s.get("sku_id") for s in skus if isinstance(s, dict)])
        if actual_sku_ids == expected_sku_ids:
            results.append({
                "item": "skus 包含正确的 SKU ID 列表（无重复、无干扰）",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": ""
            })
            total_score += 10
        else:
            results.append({
                "item": "skus 包含正确的 SKU ID 列表",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"期望 {expected_sku_ids}，实际 {actual_sku_ids}"
            })

        # 检查每个 SKU 的必填字段 (5分)
        all_fields_ok = True
        for sku in skus:
            if not all(k in sku for k in ["sku_id", "sku_name", "price", "selling_points", "ingredients"]):
                all_fields_ok = False
                break
        if all_fields_ok:
            results.append({
                "item": "每个 SKU 包含 sku_id, sku_name, price, selling_points, ingredients",
                "score": 5,
                "max_score": 5,
                "passed": True,
                "reason": ""
            })
            total_score += 5
        else:
            results.append({
                "item": "每个 SKU 包含所需字段",
                "score": 0,
                "max_score": 5,
                "passed": False,
                "reason": "部分 SKU 缺少字段"
            })

        # 检查价格是否正确 (10分)
        # 从 builder 中已知 live price 对应值
        expected_prices = {"LS-001": 25.50, "LS-002": 32.00, "LS-003": 18.75}
        price_errors = []
        for sku in skus:
            sid = sku.get("sku_id")
            actual_price = sku.get("price")
            expected = expected_prices.get(sid)
            if expected is None:
                price_errors.append(f"{sid}: 未知SKU")
            elif abs(actual_price - expected) > 0.01:
                price_errors.append(f"{sid}: 期望 {expected}，实际 {actual_price}")
        if not price_errors:
            results.append({
                "item": "每个 SKU 的价格与最新价格本一致",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": ""
            })
            total_score += 10
        else:
            results.append({
                "item": "每个 SKU 的价格正确",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": "; ".join(price_errors)
            })

    # 5.6 summary (5分)
    summary = report.get("summary", {})
    expected_summary = {
        "total_active_skus": 3,
        "average_price": 25.42,  # (25.50+32.00+18.75)/3 = 25.41666... ≈ 25.42
        "price_range": {"min": 18.75, "max": 32.00}
    }
    summary_ok = True
    if summary.get("total_active_skus") != expected_summary["total_active_skus"]:
        summary_ok = False
    if abs(summary.get("average_price", 0) - expected_summary["average_price"]) > 0.01:
        summary_ok = False
    pr = summary.get("price_range", {})
    if abs(pr.get("min", 0) - expected_summary["price_range"]["min"]) > 0.01:
        summary_ok = False
    if abs(pr.get("max", 0) - expected_summary["price_range"]["max"]) > 0.01:
        summary_ok = False
    if summary_ok:
        results.append({
            "item": "summary 数值正确",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": ""
        })
        total_score += 5
    else:
        results.append({
            "item": "summary 数值正确",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": f"期望 {expected_summary}，实际 {summary}"
        })

    # 汇总评分
    final_score = min(total_score, 100)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": final_score, "details": results}, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
