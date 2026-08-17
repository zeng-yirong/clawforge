import sys
import os
import json
import math
from decimal import Decimal, ROUND_HALF_UP

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def verify(workspace):
    details = []
    total_score = 0
    max_total = 100

    # 1. 检查必要目录和文件 (10分)
    items_dir = [
        ("ops/cost_report.json", "成本报告文件存在")
    ]
    dir_score = 0
    for rel, desc in items_dir:
        path = os.path.join(workspace, rel)
        if os.path.isfile(path):
            dir_score += 5
            details.append({"item": desc, "score": 5, "max_score": 5, "passed": True, "reason": f"文件 {rel} 存在"})
        else:
            details.append({"item": desc, "score": 0, "max_score": 5, "passed": False, "reason": f"文件 {rel} 不存在"})
    total_score += dir_score

    # 2. 解析 cost_report.json 并检查合法性 (10分)
    cost_report_path = os.path.join(workspace, "ops/cost_report.json")
    if not os.path.isfile(cost_report_path):
        details.append({"item": "JSON 格式合法", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在，无法解析"})
        # 后续步骤跳过
        write_score(workspace, 0, details)
        return

    try:
        report = load_json(cost_report_path)
        details.append({"item": "JSON 格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "成功解析 JSON"})
        total_score += 10
    except Exception as e:
        details.append({"item": "JSON 格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {e}"})
        write_score(workspace, total_score, details)
        return

    # 3. 检查报告结构 (10分)
    struct_score = 0
    if not isinstance(report, dict):
        details.append({"item": "报告是字典", "score": 0, "max_score": 5, "passed": False, "reason": "报告不是 JSON 对象"})
    else:
        if "total_cost" in report:
            details.append({"item": "报告包含 total_cost", "score": 5, "max_score": 5, "passed": True, "reason": "total_cost 字段存在"})
            struct_score += 5
        else:
            details.append({"item": "报告包含 total_cost", "score": 0, "max_score": 5, "passed": False, "reason": "缺少 total_cost"})
        if "items" in report and isinstance(report["items"], list):
            details.append({"item": "报告包含 items 列表", "score": 5, "max_score": 5, "passed": True, "reason": "items 字段存在且为列表"})
            struct_score += 5
        else:
            details.append({"item": "报告包含 items 列表", "score": 0, "max_score": 5, "passed": False, "reason": "items 缺失或不是列表"})
    total_score += struct_score

    # 4. 数据过滤正确性：只包含 ads-ranking 集群 (30分)
    filter_score = 0
    if "items" in report and isinstance(report["items"], list):
        items = report["items"]
        # 读取原始 ledger 获取 ads-ranking 的正确条目 ID
        ledger_path = os.path.join(workspace, "data/resources/resource_ledger.json")
        if not os.path.isfile(ledger_path):
            details.append({"item": "过滤：只包含 ads-ranking 条目", "score": 0, "max_score": 30, "passed": False, "reason": "无法读取 resource_ledger.json"})
        else:
            ledger = load_json(ledger_path)["resource_ledger"]
            expected_entries = [e for e in ledger if e["cluster_name"] == "ads-ranking" and e["quantity"] > 0]  # 排除 quantity=0 的干扰
            expected_names = [e["resource_name"] for e in expected_entries]
            actual_names = [item.get("resource_name", "") for item in items]
            # 检查是否包含所有期望的资源，且没有多余
            missing = [n for n in expected_names if n not in actual_names]
            extra = [n for n in actual_names if n not in expected_names]
            if not missing and not extra:
                details.append({"item": "过滤：只包含 ads-ranking 条目", "score": 30, "max_score": 30, "passed": True, "reason": "正确过滤，无多余或遗漏"})
                filter_score = 30
            else:
                reason_parts = []
                if missing:
                    reason_parts.append(f"缺少资源: {missing}")
                if extra:
                    reason_parts.append(f"多余资源: {extra}")
                details.append({"item": "过滤：只包含 ads-ranking 条目", "score": 0, "max_score": 30, "passed": False, "reason": "; ".join(reason_parts)})
    else:
        details.append({"item": "过滤：只包含 ads-ranking 条目", "score": 0, "max_score": 30, "passed": False, "reason": "items 不可用"})
    total_score += filter_score

    # 5. 定价目录使用正确性 (20分) —— 检查使用的价格是否来自 active 目录，并且不是 archived
    pricing_score = 0
    pricing_path = os.path.join(workspace, "data/pricing/pricing_catalogs.json")
    if not os.path.isfile(pricing_path):
        details.append({"item": "定价来源正确（active 目录）", "score": 0, "max_score": 20, "passed": False, "reason": "无法读取 pricing_catalogs.json"})
    else:
        catalogs = load_json(pricing_path)["pricing_catalogs"]
        active_catalog = None
        for cat in catalogs:
            if cat["status"] == "active":
                active_catalog = cat
                break
        if active_catalog is None:
            details.append({"item": "定价来源正确（active 目录）", "score": 0, "max_score": 20, "passed": False, "reason": "未找到 active 目录"})
        else:
            active_rates = active_catalog["rates"]
            # 验证 items 中的 unit_price 是否都能在 active_rates 中找到
            if "items" in report and isinstance(report["items"], list):
                price_ok = True
                for item in report["items"]:
                    rf = item.get("resource_family")
                    mc = item.get("metric_code")
                    up = item.get("unit_price")
                    # 在 active_rates 中找匹配
                    found = False
                    for rate in active_rates:
                        if rate["resource_family"] == rf and rate["metric_code"] == mc:
                            if abs(rate["unit_price"] - up) < 1e-9:
                                found = True
                            break
                    if not found:
                        price_ok = False
                        details.append({"item": "定价来源正确（active 目录）", "score": 0, "max_score": 20, "passed": False, "reason": f"资源 {item.get('resource_name')} 的 unit_price {up} 不匹配 active 目录中的价格"})
                        break
                if price_ok:
                    details.append({"item": "定价来源正确（active 目录）", "score": 20, "max_score": 20, "passed": True, "reason": "所有 unit_price 均来自 active 目录"})
                    pricing_score = 20
    total_score += pricing_score

    # 6. 成本计算准确性 (30分) —— 计算期望总成本并比较
    calc_score = 0
    if filter_score == 30 and pricing_score == 20:
        # 重新计算期望值
        ledger = load_json(os.path.join(workspace, "data/resources/resource_ledger.json"))["resource_ledger"]
        active_rates = active_catalog["rates"]
        expected_total = Decimal('0')
        expected_items = []
        for entry in ledger:
            if entry["cluster_name"] != "ads-ranking" or entry["quantity"] == 0:
                continue
            # 查找 rate
            rate_val = None
            for rate in active_rates:
                if rate["resource_family"] == entry["resource_family"] and rate["metric_code"] == entry["metric_code"]:
                    rate_val = Decimal(str(rate["unit_price"]))
                    break
            if rate_val is None:
                continue
            cost = Decimal(str(entry["quantity"])) * rate_val
            expected_total += cost
            expected_items.append({
                "resource_name": entry["resource_name"],
                "quantity": entry["quantity"],
                "unit_price": float(rate_val),
                "cost": float(cost.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
            })
        expected_total_rounded = float(expected_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

        actual_total = report.get("total_cost")
        if isinstance(actual_total, (int, float)):
            if math.isclose(actual_total, expected_total_rounded, rel_tol=1e-9):
                details.append({"item": "总成本计算正确", "score": 15, "max_score": 15, "passed": True, "reason": f"总成本 {actual_total} 与预期 {expected_total_rounded} 一致"})
                calc_score += 15
            else:
                details.append({"item": "总成本计算正确", "score": 0, "max_score": 15, "passed": False, "reason": f"总成本 {actual_total} 与预期 {expected_total_rounded} 不符"})
        else:
            details.append({"item": "总成本计算正确", "score": 0, "max_score": 15, "passed": False, "reason": "total_cost 不是数字"})

        # 检查每个 line item 的成本
        items_correct = True
        if "items" in report and isinstance(report["items"], list):
            for i, item in enumerate(expected_items):
                actual_item = None
                for ai in report["items"]:
                    if ai.get("resource_name") == item["resource_name"]:
                        actual_item = ai
                        break
                if actual_item is None:
                    items_correct = False
                    break
                # 检查 quantity, unit_price, cost
                if (actual_item.get("quantity") != item["quantity"] or
                    not math.isclose(actual_item.get("unit_price", 0), item["unit_price"], rel_tol=1e-9) or
                    not math.isclose(actual_item.get("cost", 0), item["cost"], rel_tol=1e-9)):
                    items_correct = False
                    break
            if items_correct:
                details.append({"item": "每个资源的成本行正确", "score": 15, "max_score": 15, "passed": True, "reason": "所有 line item 的 quantity, unit_price, cost 均匹配预期"})
                calc_score += 15
            else:
                details.append({"item": "每个资源的成本行正确", "score": 0, "max_score": 15, "passed": False, "reason": "line item 数据与预期不符"})
        else:
            details.append({"item": "每个资源的成本行正确", "score": 0, "max_score": 15, "passed": False, "reason": "items 不可用"})
    total_score += calc_score

    # 最终总分写入
    write_score(workspace, total_score, details)

def write_score(workspace, score, details):
    result = {
        "total_score": score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written: {score}")

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
