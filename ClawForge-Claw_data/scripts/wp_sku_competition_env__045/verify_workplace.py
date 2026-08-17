import sys
import json
import os
import re

def verify(workspace: str) -> dict:
    details = []
    total_score = 0

    # 1. 检查 ops/report.json 是否存在 (10分)
    report_path = os.path.join(workspace, "ops", "report.json")
    if os.path.isfile(report_path):
        details.append({"item": "ops/report.json 存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
    else:
        details.append({"item": "ops/report.json 存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        # 若文件不存在，后续检查直接给0分
        return {"total_score": 0, "details": details}

    # 2. 解析 JSON，检查合法性 (10分)
    try:
        with open(report_path, "r") as f:
            report = json.load(f)
        if isinstance(report, list) and len(report) > 0:
            details.append({"item": "report.json 是合法 JSON 数组", "score": 10, "max_score": 10, "passed": True, "reason": f"数组长度 {len(report)}"})
        else:
            details.append({"item": "report.json 是合法 JSON 数组", "score": 0, "max_score": 10, "passed": False, "reason": "不是非空数组"})
            return {"total_score": 10, "details": details}
    except Exception as e:
        details.append({"item": "report.json 是合法 JSON 数组", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {str(e)}"})
        return {"total_score": 10, "details": details}

    # 3. 检查是否有且仅有4个条目（两个品牌各2个 active Hydration Serum SKU）(20分)
    #    允许顺序不同，但数量必须为4
    if len(report) == 4:
        details.append({"item": "报告条目数正确 (4)", "score": 20, "max_score": 20, "passed": True, "reason": "共4条"})
    else:
        details.append({"item": "报告条目数正确 (4)", "score": 0, "max_score": 20, "passed": False, "reason": f"实际 {len(report)} 条"})
        # 后续检查仍可继续，但会扣分

    # 4. 检查每个条目的结构：必须包含 brand_name, sku_id, sku_name, selling_points, ingredients, price (15分)
    required_fields = {"brand_name", "sku_id", "sku_name", "selling_points", "ingredients", "price"}
    field_ok = True
    for idx, entry in enumerate(report):
        missing = required_fields - set(entry.keys())
        if missing:
            field_ok = False
            details.append({"item": f"条目 {idx} 字段完整性", "score": 0, "max_score": 15, "passed": False, "reason": f"缺失字段: {missing}"})
            break
    if field_ok:
        details.append({"item": "所有条目拥有必需字段", "score": 15, "max_score": 15, "passed": True, "reason": "字段完整"})

    # 5. 检查包含的 SKU 集合必须为四个正确的 ID，且不包含干扰 SKU (20分)
    expected_sku_ids = {"lum-hs-001", "lum-hs-002", "aqu-hs-001", "aqu-hs-002"}
    actual_sku_ids = {e["sku_id"] for e in report if "sku_id" in e}
    if actual_sku_ids == expected_sku_ids:
        details.append({"item": "SKU ID 集合正确，无干扰", "score": 20, "max_score": 20, "passed": True, "reason": "仅包含预期的4个 SKU"})
    else:
        extra = actual_sku_ids - expected_sku_ids
        missing = expected_sku_ids - actual_sku_ids
        reason = f"多余: {extra}, 缺失: {missing}" if extra or missing else "集合不等"
        details.append({"item": "SKU ID 集合正确，无干扰", "score": 0, "max_score": 20, "passed": False, "reason": reason})

    # 6. 检查每个 SKU 的价格是否与当前 LIVE 价格本一致 (25分)
    expected_prices = {
        "lum-hs-001": 24.80,
        "lum-hs-002": 29.50,
        "aqu-hs-001": 19.90,
        "aqu-hs-002": 22.00
    }
    price_ok = True
    for entry in report:
        sid = entry.get("sku_id")
        actual_price = entry.get("price")
        exp = expected_prices.get(sid)
        if exp is None:
            price_ok = False
            details.append({"item": f"SKU {sid} 价格正确", "score": 0, "max_score": 25, "passed": False, "reason": "未知 SKU"})
            break
        if abs(actual_price - exp) > 0.001:
            price_ok = False
            details.append({"item": f"SKU {sid} 价格正确", "score": 0, "max_score": 25, "passed": False, "reason": f"预期 {exp}, 实际 {actual_price}"})
            break
    if price_ok:
        details.append({"item": "所有 SKU 价格与当前 LIVE 价格一致", "score": 25, "max_score": 25, "passed": True, "reason": "价格准确"})

    # 汇总得分
    for d in details:
        total_score += d["score"]
    # 确保不超过100
    total_score = min(total_score, 100)
    return {"total_score": total_score, "details": details}

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    # 写入 workplace_score.json
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written to {score_path}: total_score={result['total_score']}")
