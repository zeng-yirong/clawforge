import sys
import os
import json
import math
import shutil

def verify(workspace: str):
    details = []
    total_score = 0
    max_total = 100

    # 1. 检查 reports 目录是否存在 (10分)
    reports_dir = os.path.join(workspace, "reports")
    if os.path.isdir(reports_dir):
        details.append({"item": "reports 目录存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录存在"})
        total_score += 10
    else:
        details.append({"item": "reports 目录存在", "score": 0, "max_score": 10, "passed": False, "reason": "reports 目录不存在"})
        # 如果目录都不存在，后续检查无法进行，直接返回
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    target_file = os.path.join(reports_dir, "dermveil_sku_pricing.json")
    if not os.path.isfile(target_file):
        details.append({"item": "目标文件存在", "score": 0, "max_score": 10, "passed": False, "reason": f"文件 {target_file} 不存在"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return
    else:
        details.append({"item": "目标文件存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
        total_score += 10

    # 2. JSON 合法性 (10分)
    try:
        with open(target_file, "r") as f:
            data = json.load(f)
        details.append({"item": "JSON 格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "可正常解析"})
        total_score += 10
    except Exception as e:
        details.append({"item": "JSON 格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {str(e)}"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # 3. 数据结构：必须是列表 (10分)
    if not isinstance(data, list):
        details.append({"item": "数据顶层为列表", "score": 0, "max_score": 10, "passed": False, "reason": f"类型为 {type(data).__name__}"})
        total_score += 0
    else:
        details.append({"item": "数据顶层为列表", "score": 10, "max_score": 10, "passed": True, "reason": "正确"})
        total_score += 10

    # 4. 字段完整性：每个条目必须有 sku_id, sku_name, unit_price, currency (10分)
    required_fields = {"sku_id", "sku_name", "unit_price", "currency"}
    fields_ok = True
    for idx, item in enumerate(data):
        if not isinstance(item, dict):
            fields_ok = False
            break
        if not required_fields.issubset(item.keys()):
            fields_ok = False
            break
    if fields_ok:
        details.append({"item": "字段完整性", "score": 10, "max_score": 10, "passed": True, "reason": "所有条目包含必需字段"})
        total_score += 10
    else:
        details.append({"item": "字段完整性", "score": 0, "max_score": 10, "passed": False, "reason": "存在缺失字段或条目非字典"})
        total_score += 0

    # 5. 正确过滤：只包含 DermVeil 品牌 active SKU，且按 unit_price 升序 (共60分，分成数量、排序、每个数值)
    # 预期结果：基于 env_builder 数据，DermVeil active SKU 在当前价格册中的条目：
    # DV-1001: 19.99 USD, DV-1002: 24.50 USD, DV-1003: 34.00 USD
    # 注意 DV-1004 虽然出现在 price_book 中，但 SKU 状态为 discontinued，应排除
    # 注意重复的 DV-1001 属于 LuminaSkin，应过滤掉
    expected = [
        {"sku_id": "DV-1001", "sku_name": "UV Shield SPF50", "unit_price": 19.99, "currency": "USD"},
        {"sku_id": "DV-1002", "sku_name": "Day Repair SPF30", "unit_price": 24.50, "currency": "USD"},
        {"sku_id": "DV-1003", "sku_name": "Night Renew Cream", "unit_price": 34.00, "currency": "USD"},
    ]

    # 5a. 条目数量 (15分)
    if len(data) == 3:
        details.append({"item": "条目数量正确", "score": 15, "max_score": 15, "passed": True, "reason": f"共 {len(data)} 条，预期 3 条"})
        total_score += 15
    else:
        details.append({"item": "条目数量正确", "score": 0, "max_score": 15, "passed": False, "reason": f"共 {len(data)} 条，预期 3 条"})
        total_score += 0

    # 5b. 排序正确 (15分)
    prices = [item["unit_price"] for item in data]
    if prices == sorted(prices):
        details.append({"item": "按 unit_price 升序排列", "score": 15, "max_score": 15, "passed": True, "reason": "价格升序"})
        total_score += 15
    else:
        details.append({"item": "按 unit_price 升序排列", "score": 0, "max_score": 15, "passed": False, "reason": f"当前顺序 prices={prices}"})
        total_score += 0

    # 5c. 每个条目的精确数值 (30分，每个条目10分)
    # 由于顺序已保证，我们对 data 和 expected 逐项比较
    score_per_item = 10
    for i, (actual, exp) in enumerate(zip(data, expected)):
        ok = True
        reasons = []
        if actual.get("sku_id") != exp["sku_id"]:
            ok = False
            reasons.append(f"sku_id 期望 {exp['sku_id']} 得到 {actual.get('sku_id')}")
        if actual.get("sku_name") != exp["sku_name"]:
            ok = False
            reasons.append(f"sku_name 期望 {exp['sku_name']} 得到 {actual.get('sku_name')}")
        # 允许价格浮点数微小误差，但这里精确相等
        if abs(actual.get("unit_price") - exp["unit_price"]) > 1e-6:
            ok = False
            reasons.append(f"unit_price 期望 {exp['unit_price']} 得到 {actual.get('unit_price')}")
        if actual.get("currency") != exp["currency"]:
            ok = False
            reasons.append(f"currency 期望 {exp['currency']} 得到 {actual.get('currency')}")
        if ok:
            details.append({"item": f"条目{i+1} ({exp['sku_id']}) 数值正确", "score": score_per_item, "max_score": score_per_item, "passed": True, "reason": "完全匹配"})
            total_score += score_per_item
        else:
            details.append({"item": f"条目{i+1} ({exp['sku_id']}) 数值正确", "score": 0, "max_score": score_per_item, "passed": False, "reason": "; ".join(reasons)})
            total_score += 0

    # 额外扣分项：如果存在多余条目（比如包含了 discontinued 或错误品牌），每多一条扣5分（从总数中扣，但不低于0）
    if len(data) > 3:
        extra = len(data) - 3
        # 扣分不单独记录，只在总得分体现，但为了清晰单独加一个 detail
        penalty = min(extra * 5, total_score)  # 最多扣到0
        details.append({"item": "无多余条目扣分", "score": 0, "max_score": 0, "passed": False, "reason": f"存在 {extra} 条多余条目, 扣 {penalty} 分"})
        total_score -= penalty
        if total_score < 0:
            total_score = 0

    # 汇总
    total_score = min(total_score, 100)
    result = {
        "total_score": total_score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
