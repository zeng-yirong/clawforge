import sys
import json
import os
import pathlib

def verify(workspace):
    details = []
    total = 0
    max_total = 100

    # 1. 目录结构检查 (ops/ 存在)
    ops_dir = os.path.join(workspace, "ops")
    detail = {
        "item": "ops/ 目录存在",
        "score": 0,
        "max_score": 5,
        "passed": False,
        "reason": ""
    }
    if os.path.isdir(ops_dir):
        detail["score"] = 5
        detail["passed"] = True
        detail["reason"] = "ops/ 目录存在"
    else:
        detail["reason"] = "缺少 ops/ 目录"
    details.append(detail)
    total += detail["score"]

    # 2. 结果文件存在
    result_path = os.path.join(ops_dir, "competition_report.json")
    detail = {
        "item": "ops/competition_report.json 存在",
        "score": 0,
        "max_score": 10,
        "passed": False,
        "reason": ""
    }
    if os.path.isfile(result_path):
        detail["score"] = 10
        detail["passed"] = True
        detail["reason"] = "文件存在"
    else:
        detail["reason"] = "文件不存在"
    details.append(detail)
    total += detail["score"]

    # 3. JSON 合法性
    detail = {
        "item": "JSON 格式正确",
        "score": 0,
        "max_score": 10,
        "passed": False,
        "reason": ""
    }
    try:
        with open(result_path, "r") as f:
            data = json.load(f)
        if isinstance(data, list):
            detail["score"] = 10
            detail["passed"] = True
            detail["reason"] = "有效 JSON 数组"
        else:
            detail["reason"] = "根元素不是数组"
    except Exception as e:
        detail["reason"] = f"JSON 解析失败: {str(e)}"
    details.append(detail)
    total += detail["score"]

    if not os.path.isfile(result_path):
        # 无法继续，返回
        final = {"total_score": total, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(final, f, indent=2)
        return

    # 4. 只包含 LuminaSkin 的 SKU，且排除 discontinued
    detail = {
        "item": "仅包含 LuminaSkin 且在售 SKU",
        "score": 0,
        "max_score": 20,
        "passed": False,
        "reason": ""
    }
    # 先加载源数据验证（但评分只检查输出）
    # 我们检查输出的每个条目是否 brand 正确，status 隐含
    # 但我们需要确认是否混入其他品牌或已停产
    expected_skus = {
        "LS-UV-200", "LS-UV-100", "LS-HYDR-100", "LS-HYDR-200"
    }
    found_skus = set()
    for entry in data:
        sku_id = entry.get("sku_id")
        if sku_id:
            found_skus.add(sku_id)
    if found_skus == expected_skus:
        detail["score"] = 20
        detail["passed"] = True
        detail["reason"] = "正确包含 4 个在售 SKU，无多余或缺失"
    else:
        missing = expected_skus - found_skus
        extra = found_skus - expected_skus
        reasons = []
        if missing:
            reasons.append(f"缺少: {missing}")
        if extra:
            reasons.append(f"多余: {extra}")
        detail["reason"] = "; ".join(reasons)
    details.append(detail)
    total += detail["score"]

    # 5. 价格正确（来自 current pricebook）
    detail = {
        "item": "价格取自当前价格手册 (APAC-Q2-2026-LIVE)",
        "score": 0,
        "max_score": 25,
        "passed": False,
        "reason": ""
    }
    expected_prices = {
        "LS-HYDR-100": 45.00,
        "LS-HYDR-200": 58.00,
        "LS-UV-100": 35.00,
        "LS-UV-200": 28.00
    }
    entry_prices = {}
    for entry in data:
        sku_id = entry.get("sku_id")
        price = entry.get("price")
        if sku_id and price is not None:
            entry_prices[sku_id] = price
    if entry_prices == expected_prices:
        detail["score"] = 25
        detail["passed"] = True
        detail["reason"] = "价格与当前价格手册一致"
    else:
        mismatches = {}
        for sid, ep in expected_prices.items():
            if sid in entry_prices:
                if abs(entry_prices[sid] - ep) > 0.001:
                    mismatches[sid] = f"期望 {ep}, 实际 {entry_prices[sid]}"
            else:
                mismatches[sid] = "缺失"
        detail["reason"] = f"价格不匹配: {mismatches}" if mismatches else "部分缺失"
    details.append(detail)
    total += detail["score"]

    # 6. 排序按价格升序
    detail = {
        "item": "按价格升序排列",
        "score": 0,
        "max_score": 15,
        "passed": False,
        "reason": ""
    }
    prices = [entry.get("price") for entry in data if isinstance(entry.get("price"), (int, float))]
    if prices == sorted(prices):
        detail["score"] = 15
        detail["passed"] = True
        detail["reason"] = "价格升序正确"
    else:
        detail["reason"] = "价格未按升序排列"
    details.append(detail)
    total += detail["score"]

    # 7. 每个条目包含必要字段 (sku_id, sku_name, size, price)
    detail = {
        "item": "每个条目包含 sku_id, sku_name, size, price",
        "score": 0,
        "max_score": 15,
        "passed": False,
        "reason": ""
    }
    required_fields = {"sku_id", "sku_name", "size", "price"}
    all_ok = True
    for i, entry in enumerate(data):
        missing = required_fields - set(entry.keys())
        if missing:
            all_ok = False
            detail["reason"] = f"条目 {i} 缺少字段 {missing}"
            break
    if all_ok:
        detail["score"] = 15
        detail["passed"] = True
        detail["reason"] = "所有条目包含必要字段"
    else:
        pass  # reason set above
    details.append(detail)
    total += detail["score"]

    # 最终总分
    final = {
        "total_score": total,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(final, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
