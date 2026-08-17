import sys
import json
import os
import math

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."

    details = []
    total_score = 0

    # ---------- 1. 检查 cost_report.json 是否存在 ----------
    report_path = os.path.join(workspace, "cost_report.json")
    if not os.path.isfile(report_path):
        details.append({
            "item": "cost_report.json exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "cost_report.json not found in workspace root"
        })
        # 若文件不存在，后续检查无意义，直接输出
        write_score(report_path, details, total_score)
        return

    details.append({
        "item": "cost_report.json exists",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "file found"
    })
    total_score += 10

    # ---------- 2. 解析 JSON 并检查格式合法性 ----------
    try:
        with open(report_path, "r") as f:
            report = json.load(f)
    except json.JSONDecodeError as e:
        details.append({
            "item": "valid JSON syntax",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON decode error: {e}"
        })
        write_score(report_path, details, total_score)
        return

    if not isinstance(report, dict):
        details.append({
            "item": "valid JSON syntax",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "root is not a JSON object"
        })
        write_score(report_path, details, total_score)
        return

    details.append({
        "item": "valid JSON syntax",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "valid JSON object"
    })
    total_score += 10

    # ---------- 3. 检查必需字段 ----------
    required_fields = ["cluster_id", "month", "currency", "items", "total_cost"]
    missing = [f for f in required_fields if f not in report]
    if missing:
        details.append({
            "item": "required fields present",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"missing fields: {missing}"
        })
        write_score(report_path, details, total_score)
        return

    details.append({
        "item": "required fields present",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "all required fields exist"
    })
    total_score += 10

    # ---------- 4. 检查 cluster_id 和 month 正确性 ----------
    if report["cluster_id"] != "cl-retail-001":
        details.append({
            "item": "cluster_id value",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"expected 'cl-retail-001', got '{report['cluster_id']}'"
        })
    else:
        details.append({
            "item": "cluster_id value",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "correct"
        })
        total_score += 10

    if report["month"] != "2026-06":
        details.append({
            "item": "month value",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"expected '2026-06', got '{report['month']}'"
        })
    else:
        details.append({
            "item": "month value",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "correct"
        })
        total_score += 10

    # ---------- 5. 检查 currency ----------
    if report["currency"] != "USD":
        details.append({
            "item": "currency value",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": f"expected 'USD', got '{report['currency']}'"
        })
    else:
        details.append({
            "item": "currency value",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "correct"
        })
        total_score += 5

    # ---------- 6. 检查 items 结构 ----------
    items = report.get("items", [])
    if not isinstance(items, list) or len(items) == 0:
        details.append({
            "item": "items is non-empty list",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "items missing or empty"
        })
        write_score(report_path, details, total_score)
        return

    # 验证每个 item 包含所需字段
    item_fields_ok = True
    for idx, it in enumerate(items):
        for field in ["resource_family", "quantity", "unit_price", "cost"]:
            if field not in it:
                item_fields_ok = False
                break
        if not isinstance(it.get("quantity"), (int, float)):
            item_fields_ok = False
            break
        if not isinstance(it.get("unit_price"), (int, float)):
            item_fields_ok = False
            break
        if not isinstance(it.get("cost"), (int, float)):
            item_fields_ok = False
            break
    if not item_fields_ok:
        details.append({
            "item": "items field structure",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "one or more items missing or invalid fields (resource_family, quantity, unit_price, cost)"
        })
        write_score(report_path, details, total_score)
        return

    details.append({
        "item": "items field structure",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "all items have correct fields with numeric types"
    })
    total_score += 10

    # ---------- 7. 计算预期结果 ----------
    # 加载原始数据计算期望值
    # 注意：env_builder 创建的文件在 workspace 的子文件夹 data/ 下，但 verify 在 workspace 根目录执行
    ledger_path = os.path.join(workspace, "data/resources/resource_ledger.json")
    pricing_path = os.path.join(workspace, "data/pricing/pricing_catalogs.json")

    try:
        with open(ledger_path) as f:
            ledger_data = json.load(f)["resource_ledger"]
        with open(pricing_path) as f:
            pricing_data = json.load(f)["pricing_catalogs"]
    except Exception as e:
        details.append({
            "item": "reference data load",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"failed to load reference data: {e}"
        })
        write_score(report_path, details, total_score)
        return

    # 找到 retail-core 的条目 (cluster_id = cl-retail-001)
    retail_entries = [e for e in ledger_data if e["cluster_id"] == "cl-retail-001"]
    # 找到活跃定价 (status = active, billing_month = 2026-06)
    active_pricing = None
    for p in pricing_data:
        if p["status"] == "active" and p["billing_month"] == "2026-06":
            active_pricing = p
            break
    if active_pricing is None:
        details.append({
            "item": "expected cost calculation",
            "score": 0,
            "max_score": 25,
            "passed": False,
            "reason": "no active pricing catalog for 2026-06 found in reference data"
        })
        write_score(report_path, details, total_score)
        return

    # 构建 rate 映射: (resource_family, metric_code) -> unit_price
    rate_map = {}
    for r in active_pricing["rates"]:
        rate_map[(r["resource_family"], r["metric_code"])] = r["unit_price"]

    # 按 resource_family 聚合 quantity（注意：同一 resource_family 可能不同 metric，但实际我们按 family 聚合单价？
    # 但 report_schema.md 要求每个 item 有 resource_family 和 quantity/unit_price/cost。
    # 从业务看，相同 resource_family 可能有不同 metric，但定价表中 resource_family + metric_code 决定单价。
    # 为简化，我们允许 agent 按 (resource_family, metric_code) 作为 item 粒度，或者按 resource_family 聚合（取加权平均等）。
    # 但正确的做法：因每个 metric 单价不同，应拆分条目。我们验证时需兼容两种合理做法。
    # 但为了唯一性，我们设计时故意让 retail-core 有 5 个条目，分别对应不同的 (resource_family, metric_code) 组合。
    # 预期计算：分别计算每个条目成本，然后汇总。agent 输出 items 应包含每个 metric_code 一行，或者聚合 resource_family？
    # 我们预期 agent 会按 resource_family 聚合（因为 report 只要求 resource_family），但单价怎么取？实际上不同 metric 单价不同，
    # 如果按 family 聚合，需要加权平均。但 schema 示例中 items 有 resource_family, quantity, unit_price, cost。
    # 如果 agent 按 family 聚合，则 unit_price 应为加权平均或单独列出？为了明确，我们设计定价表中每个 metric 单价不同，
    # 并且 agent 应该每个 metric 一个 item（因为命名 resource_family 可以重复）。但 schema 要求 resource_family 字段，
    # 可以重复。我们检查时允许两种：要么每个 metric 一个 item，要么按 family 聚合（这时 unit_price 用加权平均）。但加权平均是合理的。
    # 为了简化验证，我们设定期望：agent 应该按 metric_code 拆开，因为 report_schema 没有禁止重复的 resource_family。
    # 实际上，常见做法是每个 resource_family 一行，但这里 metric 不同导致单价不同，所以必须按 metric 拆。
    # 我们强制期望为按 (family, metric) 拆分。这样验证简单。
    # 从 env_builder 数据计算预期 items 和 total_cost。

    # 构建预期 items
    expected_items = []
    for entry in retail_entries:
        key = (entry["resource_family"], entry["metric_code"])
        if key not in rate_map:
            # 忽略未匹配的（例如没有定价项，但我们的数据都有）
            continue
        unit_price = rate_map[key]
        qty = entry["quantity"]
        cost = round(qty * unit_price, 2)  # 保留两位小数
        # 查找是否已有相同 family+metric 的条目（但每个 entry 都是唯一的，所以不需要合并）
        expected_items.append({
            "resource_family": entry["resource_family"],
            "quantity": qty,
            "unit_price": unit_price,
            "cost": cost
        })

    expected_total = round(sum(it["cost"] for it in expected_items), 2)

    # 现在验证 agent 的 items 和 total_cost
    # 排序比较：按 (resource_family, unit_price) 排序
    def sort_key(it):
        return (it["resource_family"], it["unit_price"])
    agent_items_sorted = sorted(items, key=sort_key)
    expected_items_sorted = sorted(expected_items, key=sort_key)

    items_match = True
    if len(agent_items_sorted) != len(expected_items_sorted):
        items_match = False
    else:
        for a, e in zip(agent_items_sorted, expected_items_sorted):
            if (a["resource_family"] != e["resource_family"] or
                not math.isclose(a["quantity"], e["quantity"], rel_tol=1e-9) or
                not math.isclose(a["unit_price"], e["unit_price"], rel_tol=1e-9) or
                not math.isclose(a["cost"], e["cost"], rel_tol=1e-9)):
                items_match = False
                break

    if not items_match:
        details.append({
            "item": "items content (quantities, unit prices, costs)",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": f"expected 5 items, got {len(items)}; or values mismatch. expected: {expected_items_sorted}, got: {agent_items_sorted}"
        })
    else:
        details.append({
            "item": "items content (quantities, unit prices, costs)",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": "all 5 items match expected"
        })
        total_score += 15

    # ---------- 8. 检查 total_cost ----------
    agent_total = report.get("total_cost")
    if not isinstance(agent_total, (int, float)) or not math.isclose(agent_total, expected_total, rel_tol=1e-9):
        details.append({
            "item": "total_cost value",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"expected {expected_total}, got {agent_total}"
        })
    else:
        details.append({
            "item": "total_cost value",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "correct"
        })
        total_score += 10

    # ---------- 写出结果 ----------
    write_score(report_path, details, total_score)

def write_score(report_path, details, total_score):
    # 确保总分为整数
    total_score = int(total_score)
    score_obj = {
        "total_score": total_score,
        "details": details
    }
    score_path = os.path.join(os.path.dirname(report_path), "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(score_obj, f, indent=2)
    print(f"Score written: {total_score}/100")

if __name__ == "__main__":
    verify()
