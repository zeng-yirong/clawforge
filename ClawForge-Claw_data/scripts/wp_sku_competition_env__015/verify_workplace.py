import sys
import json
import os
import re
from pathlib import Path

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total = 0
    max_total = 100

    # ---------- 1. 检查输出目录 ----------
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        score_details.append({
            "item": "ops 目录存在",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "ops/ 目录已创建"
        })
        total += 5
    else:
        score_details.append({
            "item": "ops 目录存在",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "ops/ 目录不存在"
        })

    # ---------- 2. 检查输出文件存在 ----------
    output_file = os.path.join(ops_dir, "price_discrepancies.json")
    if os.path.isfile(output_file):
        score_details.append({
            "item": "输出文件存在",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "ops/price_discrepancies.json 存在"
        })
        total += 5
    else:
        score_details.append({
            "item": "输出文件存在",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "文件不存在"
        })
        print(json.dumps({"total_score": total, "details": score_details}))
        sys.exit(0)

    # ---------- 3. 解析JSON ----------
    try:
        with open(output_file, "r") as f:
            data = json.load(f)
    except Exception as e:
        score_details.append({
            "item": "JSON 合法性",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON 解析失败: {e}"
        })
        # 提前结束，因为后面无法继续
        print(json.dumps({"total_score": total, "details": score_details}))
        sys.exit(0)

    if not isinstance(data, list):
        score_details.append({
            "item": "JSON 应为数组",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "顶层应为 list"
        })
        print(json.dumps({"total_score": total, "details": score_details}))
        sys.exit(0)

    score_details.append({
        "item": "JSON 格式正确",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "合法 JSON 数组"
    })
    total += 10

    # ---------- 4. 检查条目数量 ----------
    EXPECTED_COUNT = 2  # LUM-SK-001 和 LUM-SK-003 不一致，LUM-SK-004 一致不算
    actual_count = len(data)
    if actual_count == EXPECTED_COUNT:
        score_details.append({
            "item": "条目数量正确",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": f"共 {actual_count} 条，期望 {EXPECTED_COUNT}"
        })
        total += 20
    else:
        score_details.append({
            "item": "条目数量正确",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"实际 {actual_count} 条，期望 {EXPECTED_COUNT}"
        })

    # ---------- 5. 检查每个条目的字段和数值 ----------
    # 从通知中提取正确价格（再次解析确保一致性）
    notice_path = os.path.join(workspace, "data/attachments/current_pricebook_notice.md")
    expected_prices = {}
    if os.path.isfile(notice_path):
        with open(notice_path, "r") as f:
            content = f.read()
        # 解析 Markdown 表格
        table_pattern = r'\| (LUM-SK-\d+) \| ([\d.]+) \|'
        for match in re.finditer(table_pattern, content):
            sku = match.group(1)
            price = float(match.group(2))
            expected_prices[sku] = price

    # 只检查出现在 expected_prices 中的 SKU，且价格不一致的（我们已知只有两个）
    correct_discrepancies = {"LUM-SK-001": 24.50, "LUM-SK-003": 39.00}
    field_ok = True
    price_ok = True
    seen_skus = set()
    for idx, entry in enumerate(data):
        if not isinstance(entry, dict):
            field_ok = False
            continue
        if "sku_id" not in entry or "correct_price" not in entry:
            field_ok = False
            continue
        sku = entry["sku_id"]
        cp = entry["correct_price"]
        if sku in correct_discrepancies:
            # 检查价格是否匹配
            if abs(cp - correct_discrepancies[sku]) > 0.001:
                price_ok = False
        else:
            # 出现了非期望的 SKU
            price_ok = False
        seen_skus.add(sku)

    # 检查是否遗漏了正确的 SKU
    if set(correct_discrepancies.keys()) != seen_skus:
        price_ok = False

    # 字段检查评分
    if field_ok:
        score_details.append({
            "item": "字段结构 (sku_id, correct_price)",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "每个条目均包含所需字段"
        })
        total += 10
    else:
        score_details.append({
            "item": "字段结构 (sku_id, correct_price)",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "字段缺失或类型错误"
        })

    # 价格精确性评分（分两项：第一项 LUM-SK-001，第二项 LUM-SK-003）
    sku_001_ok = any(abs(entry.get("correct_price", 0) - 24.50) < 0.001
                     for entry in data if entry.get("sku_id") == "LUM-SK-001")
    sku_003_ok = any(abs(entry.get("correct_price", 0) - 39.00) < 0.001
                     for entry in data if entry.get("sku_id") == "LUM-SK-003")

    score_details.append({
        "item": "LUM-SK-001 价格正确",
        "score": 15 if sku_001_ok else 0,
        "max_score": 15,
        "passed": sku_001_ok,
        "reason": "24.50" if sku_001_ok else "缺失或数值错误"
    })
    if sku_001_ok:
        total += 15

    score_details.append({
        "item": "LUM-SK-003 价格正确",
        "score": 15 if sku_003_ok else 0,
        "max_score": 15,
        "passed": sku_003_ok,
        "reason": "39.00" if sku_003_ok else "缺失或数值错误"
    })
    if sku_003_ok:
        total += 15

    # ---------- 6. 检查有无多余条目（例如 LUM-SK-004 或其它品牌 SKU）----------
    extra_ok = True
    for entry in data:
        sku = entry.get("sku_id", "")
        if sku not in ["LUM-SK-001", "LUM-SK-003"]:
            extra_ok = False
            break
    if extra_ok:
        score_details.append({
            "item": "无多余条目",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "仅包含需要修正的 SKU"
        })
        total += 10
    else:
        score_details.append({
            "item": "无多余条目",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "包含不应出现的 SKU"
        })

    # ---------- 汇总 ----------
    final_score = min(total, max_total)
    result = {
        "total_score": final_score,
        "details": score_details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result))

if __name__ == "__main__":
    main()
