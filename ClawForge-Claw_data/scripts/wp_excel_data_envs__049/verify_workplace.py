import sys
import json
import csv
import os
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

def load_csv(path):
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

def round_to_two(value):
    d = Decimal(str(value))
    return float(d.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

def main():
    result = {"total_score": 0, "details": []}

    # 1. 检查report.json是否存在
    report_path = os.path.join(workspace, "report.json")
    if not os.path.isfile(report_path):
        result["details"].append({
            "item": "report.json 文件存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件不存在"
        })
        result["total_score"] = 0
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    result["details"].append({
        "item": "report.json 文件存在",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "文件已生成"
    })

    # 2. 检查JSON格式合法性
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            report = json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        result["details"].append({
            "item": "JSON格式合法",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON解析失败: {str(e)}"
        })
        result["total_score"] = sum(d["score"] for d in result["details"])
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    result["details"].append({
        "item": "JSON格式合法",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "解析成功"
    })

    # 3. 检查必需字段
    if not isinstance(report, dict):
        result["details"].append({
            "item": "报告结构为字典",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "report不是字典"
        })
        # 继续但不加更多分
    else:
        has_regions = "regions" in report
        has_duplicates = "duplicates_removed" in report
        if has_regions and has_duplicates:
            result["details"].append({
                "item": "包含regions和duplicates_removed字段",
                "score": 5,
                "max_score": 5,
                "passed": True,
                "reason": "结构完整"
            })
        else:
            missing = []
            if not has_regions:
                missing.append("regions")
            if not has_duplicates:
                missing.append("duplicates_removed")
            result["details"].append({
                "item": "包含regions和duplicates_removed字段",
                "score": 0,
                "max_score": 5,
                "passed": False,
                "reason": f"缺少字段: {', '.join(missing)}"
            })

    # 4. 计算期望值（基于env_builder生成的数据）
    # 加载原始CSV
    csv_path = os.path.join(workspace, "data", "sales_raw.csv")
    if not os.path.isfile(csv_path):
        result["details"].append({
            "item": "原始数据存在",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "data/sales_raw.csv 缺失，无法验证"
        })
        # 直接返回
        result["total_score"] = sum(d["score"] for d in result["details"])
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    rows = load_csv(csv_path)
    # 去重：保留每个transaction_id第一次出现的行
    seen = set()
    deduped = []
    for row in rows:
        tid = row["transaction_id"]
        if tid not in seen:
            seen.add(tid)
            deduped.append(row)
    expected_duplicates = len(rows) - len(deduped)

    # 按region统计
    region_stats = defaultdict(lambda: {"total_sales": 0.0, "order_count": 0})
    for row in deduped:
        region = row["region"]
        amount = float(row["sales_amount"])
        region_stats[region]["total_sales"] += amount
        region_stats[region]["order_count"] += 1

    expected_regions = []
    for region in sorted(region_stats.keys()):
        stats = region_stats[region]
        avg = round_to_two(stats["total_sales"] / stats["order_count"]) if stats["order_count"] > 0 else 0.0
        expected_regions.append({
            "region": region,
            "total_sales": round_to_two(stats["total_sales"]),
            "average_order": avg,
            "order_count": stats["order_count"]
        })

    # 5. 验证duplicates_removed
    actual_duplicates = report.get("duplicates_removed")
    if actual_duplicates == expected_duplicates:
        result["details"].append({
            "item": "duplicates_removed 值正确",
            "score": 30,
            "max_score": 30,
            "passed": True,
            "reason": f"预期 {expected_duplicates}，实际 {actual_duplicates}"
        })
    else:
        result["details"].append({
            "item": "duplicates_removed 值正确",
            "score": 0,
            "max_score": 30,
            "passed": False,
            "reason": f"预期 {expected_duplicates}，实际 {actual_duplicates}"
        })

    # 6. 验证regions统计
    actual_regions = report.get("regions", [])
    # 转换为字典方便比较
    actual_dict = {}
    for r in actual_regions:
        if "region" in r:
            actual_dict[r["region"]] = r

    score_each = (50 // len(expected_regions)) if expected_regions else 0  # 最多50分
    region_score = 0
    for er in expected_regions:
        region_name = er["region"]
        ar = actual_dict.get(region_name)
        if not ar:
            result["details"].append({
                "item": f"区域 {region_name} 统计",
                "score": 0,
                "max_score": score_each,
                "passed": False,
                "reason": "该区域缺失"
            })
            continue
        # 检查三个字段
        issues = []
        if ar.get("total_sales") != er["total_sales"]:
            issues.append(f"total_sales: 预期{er['total_sales']}, 实际{ar.get('total_sales')}")
        if ar.get("average_order") != er["average_order"]:
            issues.append(f"average_order: 预期{er['average_order']}, 实际{ar.get('average_order')}")
        if ar.get("order_count") != er["order_count"]:
            issues.append(f"order_count: 预期{er['order_count']}, 实际{ar.get('order_count')}")
        if issues:
            result["details"].append({
                "item": f"区域 {region_name} 统计",
                "score": 0,
                "max_score": score_each,
                "passed": False,
                "reason": "; ".join(issues)
            })
        else:
            region_score += score_each
            result["details"].append({
                "item": f"区域 {region_name} 统计",
                "score": score_each,
                "max_score": score_each,
                "passed": True,
                "reason": "全部正确"
            })

    # 处理未预期的区域（不扣分，但记录）
    for ar in actual_regions:
        if ar.get("region") not in region_stats:
            # 额外区域不惩罚，但提示
            result["details"].append({
                "item": f"额外区域 {ar.get('region')}",
                "score": 0,
                "max_score": 0,
                "passed": True,
                "reason": "未预期但允许"
            })

    # 汇总分数
    total = sum(d["score"] for d in result["details"])
    result["total_score"] = total

    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
