import json
import csv
import sys
import os
from collections import OrderedDict

def load_rows(filepath):
    """读取CSV，返回行列表（字典列表）"""
    rows = []
    with open(filepath, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for line in reader:
            # 将行转换为字典，并去除空白键（空行可能导致部分键为空）
            row = {k.strip(): v.strip() if v else "" for k, v in line.items()}
            # 跳过完全空的行（所有值都为空串）
            if all(val == "" for val in row.values()):
                continue
            rows.append(row)
    return rows

def compute_expected(workspace):
    """根据工作区中的原始数据计算预期结果"""
    raw_path = os.path.join(workspace, "data/raw_sales_2024.csv")
    if not os.path.isfile(raw_path):
        return None

    rows = load_rows(raw_path)

    # 清洗规则
    valid = []
    seen_ids = set()
    for row in rows:
        # 跳过缺少必要字段的行
        tid = row.get("transaction_id", "").strip()
        amt_str = row.get("sales_amount", "").strip()
        qty_str = row.get("quantity", "").strip()
        pname = row.get("product_name", "").strip()
        cid = row.get("customer_id", "").strip()

        # 跳过任何关键字段为空的行
        if not tid or not amt_str or not qty_str or not pname or not cid:
            continue
        try:
            amt = float(amt_str)
            qty = int(qty_str)
        except ValueError:
            continue
        # 负金额、零数量
        if amt <= 0 or qty <= 0:
            continue
        # 去重（基于 transaction_id 首次出现）
        if tid in seen_ids:
            continue
        seen_ids.add(tid)
        valid.append(row)

    if not valid:
        return {"total_revenue": 0.0, "average_order_value": 0.0, "unique_customers": 0, "top_product": ""}

    total_revenue = sum(float(r["sales_amount"]) for r in valid)
    order_count = len(valid)
    avg_order = total_revenue / order_count
    customers = set(r["customer_id"] for r in valid)
    unique_cust = len(customers)

    # 按 product_name 分组求和
    prod_rev = {}
    for r in valid:
        pn = r["product_name"]
        amt = float(r["sales_amount"])
        prod_rev[pn] = prod_rev.get(pn, 0.0) + amt
    top_product = max(prod_rev, key=prod_rev.get) if prod_rev else ""

    return {
        "total_revenue": round(total_revenue, 2),
        "average_order_value": round(avg_order, 2),
        "unique_customers": unique_cust,
        "top_product": top_product
    }

def verify(workspace="."):
    results = []
    # 1. 检查 ops/report.json 是否存在
    report_path = os.path.join(workspace, "ops", "report.json")
    if not os.path.isfile(report_path):
        results.append({
            "item": "产物文件存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "missing ops/report.json"
        })
        # 后续检查无法进行，提前返回总分
        total = 0
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": results}, f, indent=2)
        return total

    results.append({
        "item": "产物文件存在",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "ops/report.json found"
    })

    # 2. 检查是否为合法 JSON
    try:
        with open(report_path, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        results.append({
            "item": "JSON 格式合法",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"invalid JSON: {str(e)}"
        })
        total = sum(r["score"] for r in results)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": results}, f, indent=2)
        return total

    results.append({
        "item": "JSON 格式合法",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "valid JSON"
    })

    # 3. 检查必需字段
    required_keys = ["total_revenue", "average_order_value", "unique_customers", "top_product"]
    missing = [k for k in required_keys if k not in data]
    if missing:
        results.append({
            "item": "包含必需字段",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"missing keys: {missing}"
        })
        total = sum(r["score"] for r in results)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": results}, f, indent=2)
        return total
    results.append({
        "item": "包含必需字段",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "all required keys present"
    })

    # 4. 数值类型检查
    type_errors = []
    if not isinstance(data["total_revenue"], (int, float)):
        type_errors.append("total_revenue not numeric")
    if not isinstance(data["average_order_value"], (int, float)):
        type_errors.append("average_order_value not numeric")
    if not isinstance(data["unique_customers"], int):
        type_errors.append("unique_customers not int")
    if not isinstance(data["top_product"], str):
        type_errors.append("top_product not str")
    if type_errors:
        results.append({
            "item": "字段类型正确",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "; ".join(type_errors)
        })
    else:
        results.append({
            "item": "字段类型正确",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "all types correct"
        })

    # 5. 计算预期值
    expected = compute_expected(workspace)
    if expected is None:
        results.append({
            "item": "原始数据可读",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "cannot read data/raw_sales_2024.csv"
        })
        total = sum(r["score"] for r in results)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": results}, f, indent=2)
        return total

    # 6. total_revenue
    if abs(data["total_revenue"] - expected["total_revenue"]) < 0.005:
        results.append({
            "item": "total_revenue 正确",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": f"revenue={expected['total_revenue']}"
        })
    else:
        results.append({
            "item": "total_revenue 正确",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"expected {expected['total_revenue']}, got {data['total_revenue']}"
        })

    # 7. average_order_value
    if abs(data["average_order_value"] - expected["average_order_value"]) < 0.005:
        results.append({
            "item": "average_order_value 正确",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": f"avg={expected['average_order_value']}"
        })
    else:
        results.append({
            "item": "average_order_value 正确",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": f"expected {expected['average_order_value']}, got {data['average_order_value']}"
        })

    # 8. unique_customers
    if data["unique_customers"] == expected["unique_customers"]:
        results.append({
            "item": "unique_customers 正确",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": f"customers={expected['unique_customers']}"
        })
    else:
        results.append({
            "item": "unique_customers 正确",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": f"expected {expected['unique_customers']}, got {data['unique_customers']}"
        })

    # 9. top_product
    if data["top_product"] == expected["top_product"]:
        results.append({
            "item": "top_product 正确",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": f"top product={expected['top_product']}"
        })
    else:
        results.append({
            "item": "top_product 正确",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": f"expected {expected['top_product']}, got {data['top_product']}"
        })

    total = sum(r["score"] for r in results)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total, "details": results}, f, indent=2)
    return total

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
