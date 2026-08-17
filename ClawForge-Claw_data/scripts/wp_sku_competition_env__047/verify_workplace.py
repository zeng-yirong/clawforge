import os
import sys
import json
import math

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_file = os.path.join(workspace, "workplace_score.json")
    details = []
    total_score = 0

    # 1. 目录结构检查 (10分)
    ops_dir = os.path.join(workspace, "ops")
    data_dir = os.path.join(workspace, "data")
    if os.path.isdir(ops_dir) and os.path.isdir(data_dir):
        details.append({
            "item": "ops/ and data/ directories exist",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Required directories present"
        })
        total_score += 10
    else:
        missing = []
        if not os.path.isdir(ops_dir):
            missing.append("ops/")
        if not os.path.isdir(data_dir):
            missing.append("data/")
        details.append({
            "item": "ops/ and data/ directories exist",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Missing: {', '.join(missing)}"
        })

    # 2. 产物文件存在 (10分)
    report_path = os.path.join(workspace, "ops", "competition_analysis.json")
    if os.path.isfile(report_path):
        details.append({
            "item": "ops/competition_analysis.json exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Report file found"
        })
        total_score += 10
    else:
        details.append({
            "item": "ops/competition_analysis.json exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not found"
        })
        # 后续检查无法进行，直接写结果并返回
        write_score(score_file, total_score, details)
        return

    # 3. 加载产物并检查字段完整性 (20分)
    try:
        with open(report_path, "r") as f:
            report = json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        details.append({
            "item": "Report JSON is valid",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"Invalid JSON: {str(e)}"
        })
        write_score(score_file, total_score, details)
        return

    required_fields = [
        "lumina_sku", "lumina_price",
        "dermveil_sku", "dermveil_price",
        "aquapulse_sku", "aquapulse_price",
        "competitor_avg_price", "premium_pct",
        "currency"
    ]
    missing_fields = [f for f in required_fields if f not in report]
    if missing_fields:
        details.append({
            "item": "Report contains all required fields",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"Missing fields: {', '.join(missing_fields)}"
        })
        # 后续依赖这些字段，无法继续，直接结束
        write_score(score_file, total_score, details)
        return
    else:
        details.append({
            "item": "Report contains all required fields",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "All required fields present"
        })
        total_score += 20

    # 4. 从原始数据中获取真实值 (准备评分)
    price_books_path = os.path.join(workspace, "data", "pricing", "price_books.json")
    skus_path = os.path.join(workspace, "data", "skus", "skus.json")

    # 加载原始数据
    try:
        with open(price_books_path, "r") as f:
            pb_data = json.load(f)
        with open(skus_path, "r") as f:
            skus_data = json.load(f)
    except Exception as e:
        details.append({
            "item": "Original data files readable",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": f"Failed to read original data: {str(e)}"
        })
        write_score(score_file, total_score, details)
        return

    # 找到当前价格本
    current_pb = None
    for pb in pb_data.get("price_books", []):
        if pb.get("is_current") is True:
            current_pb = pb
            break
    if current_pb is None:
        details.append({
            "item": "Current price book exists",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "No price book with is_current=True found"
        })
        write_score(score_file, total_score, details)
        return
    else:
        # 构建价格映射
        price_map = {}
        for entry in current_pb.get("entries", []):
            price_map[entry["sku_id"]] = entry["price"]
        # 获取三个SKU的真实价格
        lum_sku = report.get("lumina_sku")
        derm_sku = report.get("dermveil_sku")
        aqua_sku = report.get("aquapulse_sku")

        # 检查这三个sku_id是否在价格本中
        sku_ids_in_pb = [lum_sku, derm_sku, aqua_sku]
        missing_in_pb = [sid for sid in sku_ids_in_pb if sid not in price_map]
        if missing_in_pb:
            details.append({
                "item": "All three SKU IDs exist in current price book",
                "score": 0,
                "max_score": 5,
                "passed": False,
                "reason": f"SKU IDs not in current price book: {missing_in_pb}"
            })
            write_score(score_file, total_score, details)
            return

        true_lum_price = round(price_map[lum_sku], 2)
        true_derm_price = round(price_map[derm_sku], 2)
        true_aqua_price = round(price_map[aqua_sku], 2)

        # 比较价格 (每个SKU 5分，共15分，平均值5分，百分比30分)
        price_score = 0
        price_items = [
            ("lumina_price", true_lum_price, report.get("lumina_price")),
            ("dermveil_price", true_derm_price, report.get("dermveil_price")),
            ("aquapulse_price", true_aqua_price, report.get("aquapulse_price"))
        ]
        for field, true_val, report_val in price_items:
            if isinstance(report_val, (int, float)) and round(report_val, 2) == true_val:
                price_score += 5
                details.append({
                    "item": f"{field} matches",
                    "score": 5,
                    "max_score": 5,
                    "passed": True,
                    "reason": f"Expected {true_val}, got {report_val}"
                })
            else:
                details.append({
                    "item": f"{field} matches",
                    "score": 0,
                    "max_score": 5,
                    "passed": False,
                    "reason": f"Expected {true_val}, got {report_val}"
                })

        # 计算期望平均值和百分比
        expected_avg = round((true_derm_price + true_aqua_price) / 2, 2)
        if expected_avg == 0:
            expected_pct = 0.0
        else:
            expected_pct = round((true_lum_price - expected_avg) / expected_avg * 100, 2)

        # 检查平均值
        if isinstance(report.get("competitor_avg_price"), (int, float)) and \
           round(report["competitor_avg_price"], 2) == expected_avg:
            price_score += 5
            details.append({
                "item": "competitor_avg_price matches",
                "score": 5,
                "max_score": 5,
                "passed": True,
                "reason": f"Expected {expected_avg}, got {report['competitor_avg_price']}"
            })
        else:
            details.append({
                "item": "competitor_avg_price matches",
                "score": 0,
                "max_score": 5,
                "passed": False,
                "reason": f"Expected {expected_avg}, got {report.get('competitor_avg_price')}"
            })

        # 检查百分比
        if isinstance(report.get("premium_pct"), (int, float)) and \
           round(report["premium_pct"], 2) == expected_pct:
            price_score += 30
            details.append({
                "item": "premium_pct matches",
                "score": 30,
                "max_score": 30,
                "passed": True,
                "reason": f"Expected {expected_pct}%, got {report['premium_pct']}%"
            })
        else:
            details.append({
                "item": "premium_pct matches",
                "score": 0,
                "max_score": 30,
                "passed": False,
                "reason": f"Expected {expected_pct}%, got {report.get('premium_pct')}%"
            })

        # 检查currency (额外0分，但可以提示)
        if report.get("currency") == "USD":
            pass  # 不扣分
        else:
            # 轻微提示，不加分也不减分
            details.append({
                "item": "currency is USD",
                "score": 0,
                "max_score": 0,
                "passed": True,
                "reason": "Currency check passed or not scored"
            })

        total_score += price_score

    # 最终写入
    total_score = min(total_score, 100)  # 确保不超过100
    write_score(score_file, total_score, details)

def write_score(path, total, details):
    result = {
        "total_score": total,
        "details": details
    }
    with open(path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written to {path}: {total}/100")

if __name__ == "__main__":
    main()
