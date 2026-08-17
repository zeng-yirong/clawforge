#!/usr/bin/env python3
import json
import os
import sys

def verify_workplace(workspace):
    details = []
    total_score = 0

    # 1. ops/ 目录是否存在 (10分)
    ops_dir = os.path.join(workspace, "ops")
    dir_exists = os.path.isdir(ops_dir)
    details.append({
        "item": "ops directory exists",
        "score": 10 if dir_exists else 0,
        "max_score": 10,
        "passed": dir_exists,
        "reason": "ops directory found" if dir_exists else "ops directory missing"
    })
    if dir_exists:
        total_score += 10

    # 2. competitive_report.json 文件存在 (10分)
    report_path = os.path.join(workspace, "ops", "competitive_report.json")
    file_exists = os.path.isfile(report_path)
    details.append({
        "item": "competitive_report.json exists",
        "score": 10 if file_exists else 0,
        "max_score": 10,
        "passed": file_exists,
        "reason": "File found" if file_exists else "File not found"
    })
    if file_exists:
        total_score += 10

    if not file_exists:
        # 如果文件不存在，后续无法验证，直接给总分20并返回
        details.append({
            "item": "Remaining checks skipped",
            "score": 0,
            "max_score": 80,
            "passed": False,
            "reason": "Required report file missing"
        })
        final_score = total_score
        output = {"total_score": final_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(output, f, indent=2)
        return

    # 3. JSON 格式合法 (10分)
    try:
        with open(report_path, "r") as f:
            report = json.load(f)
        json_ok = isinstance(report, list)
        details.append({
            "item": "JSON is a valid list",
            "score": 10 if json_ok else 0,
            "max_score": 10,
            "passed": json_ok,
            "reason": "Parsed as list" if json_ok else "Not a list"
        })
        if json_ok:
            total_score += 10
        else:
            # 如果不是列表，后续无法继续
            final_score = total_score
            output = {"total_score": final_score, "details": details}
            with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
                json.dump(output, f, indent=2)
            return
    except (json.JSONDecodeError, Exception) as e:
        details.append({
            "item": "JSON is valid",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Invalid JSON: {str(e)}"
        })
        final_score = total_score
        output = {"total_score": final_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(output, f, indent=2)
        return

    # 4. 记录数量正确 (应为4条竞品记录，不包含 LuminaSkin) (10分)
    expected_count = 4
    count_ok = len(report) == expected_count
    details.append({
        "item": "Report contains exactly 4 competitor records",
        "score": 10 if count_ok else 0,
        "max_score": 10,
        "passed": count_ok,
        "reason": f"Found {len(report)} records" if count_ok else f"Expected {expected_count}, got {len(report)}"
    })
    if count_ok:
        total_score += 10

    # 5. 每条记录包含四个必需字段 (10分)
    required_fields = {"brand", "sku", "price", "price_diff"}
    all_fields_ok = True
    missing_fields_records = []
    for idx, rec in enumerate(report):
        fields = set(rec.keys())
        if not required_fields.issubset(fields):
            all_fields_ok = False
            missing_fields_records.append((idx, required_fields - fields))
    if all_fields_ok:
        total_score += 10
    details.append({
        "item": "Each record has all 4 required fields (brand, sku, price, price_diff)",
        "score": 10 if all_fields_ok else 0,
        "max_score": 10,
        "passed": all_fields_ok,
        "reason": "All records complete" if all_fields_ok else f"Missing fields in records: {missing_fields_records}"
    })

    # 6. 没有多余字段 (每多一个字段扣5分，最多扣完10分) (10分)
    extra_penalty = 0
    for rec in report:
        extra = set(rec.keys()) - required_fields
        if extra:
            extra_penalty += 5 * len(extra)
    extra_score = max(0, 10 - extra_penalty)
    total_score += extra_score
    details.append({
        "item": "No extra fields beyond the 4 required",
        "score": extra_score,
        "max_score": 10,
        "passed": extra_score == 10,
        "reason": "No extra fields" if extra_score == 10 else f"Extra fields found, penalty {extra_penalty}"
    })

    # 7. 验证具体的价格和差价 (40分)
    # 期望数据（基于当前价格簿 active 的 30ml Hydration Serum 竞品）
    expected = {
        "AquaPulse": {"sku": "AquaPulse Hydra Boost 30ml", "price": 38.00, "diff": -7.00},
        "DermVeil":  {"sku": "DermVeil Pro Hydrate 30ml",  "price": 42.00, "diff": -3.00},
        "PureLattice":{"sku": "PureLattice Dew Serum 30ml", "price": 40.00, "diff": -5.00},
        "SolarOat":  {"sku": "SolarOat Light Serum 30ml",  "price": 35.00, "diff": -10.00}
    }
    correct_brands = 0
    correct_prices = 0
    correct_diffs = 0
    # 构建品牌到记录的映射
    rec_by_brand = {}
    for rec in report:
        if "brand" in rec:
            rec_by_brand[rec["brand"]] = rec
    for brand, exp in expected.items():
        if brand not in rec_by_brand:
            continue
        rec = rec_by_brand[brand]
        if rec.get("sku") == exp["sku"]:
            correct_brands += 1
        if abs(rec.get("price", 0) - exp["price"]) < 0.001:
            correct_prices += 1
        if abs(rec.get("price_diff", 0) - exp["diff"]) < 0.001:
            correct_diffs += 1
    # 每个正确项给 40/3 ≈ 13.33，简化: 12/14/14 分配
    # 总分40分: brand+sku 核对10分, price 15分, price_diff 15分
    brand_score = 10 * (correct_brands / len(expected))
    price_score = 15 * (correct_prices / len(expected))
    diff_score = 15 * (correct_diffs / len(expected))
    core_score = round(brand_score + price_score + diff_score)
    total_score += core_score
    details.append({
        "item": "Brand & SKU match expected competitors",
        "score": round(brand_score),
        "max_score": 10,
        "passed": brand_score >= 7.5,
        "reason": f"Correct brand/SKU: {correct_brands}/{len(expected)}"
    })
    details.append({
        "item": "Prices match expected values",
        "score": round(price_score),
        "max_score": 15,
        "passed": price_score >= 10,
        "reason": f"Correct prices: {correct_prices}/{len(expected)}"
    })
    details.append({
        "item": "Price differences match expected values",
        "score": round(diff_score),
        "max_score": 15,
        "passed": diff_score >= 10,
        "reason": f"Correct diffs: {correct_diffs}/{len(expected)}"
    })

    # 8. 确保没有包含 LuminaSkin 自身 (10分)
    lum_present = any(rec.get("brand") == "LuminaSkin" for rec in report)
    self_score = 0 if lum_present else 10
    total_score += self_score
    details.append({
        "item": "Report does not contain LuminaSkin itself",
        "score": self_score,
        "max_score": 10,
        "passed": not lum_present,
        "reason": "LuminaSkin excluded" if not lum_present else "LuminaSkin found in report"
    })

    # 总分截断到100
    total_score = min(total_score, 100)

    output = {"total_score": total_score, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(output, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify_workplace(workspace)
