import sys
import json
import os
from pathlib import Path

def verify(workspace: str):
    """
    验证 agent 产出的 ops/price_comparison.json 是否满足任务要求。
    评分细则：
    - 目录存在（ops/）: 10分
    - JSON 合法: 10分
    - 字段完整性（lumina_avg, derm_avg, gap）: 10分（每个缺失扣10）
    - 数值计算正确:
        * lumina_avg 正确: 20分
        * derm_avg 正确: 20分
        * gap 正确（差值）: 20分
    - 排除干扰（未混入 discontinued SKU 或无关品牌）: 10分（如果数值正确自动得满分，否则检查是否因包含干扰导致错误）
    总分 100。
    """
    details = []
    total = 0

    ws = Path(workspace)

    # 1. 检查 ops/ 目录是否存在
    ops_dir = ws / "ops"
    if ops_dir.is_dir():
        details.append({
            "item": "ops/ directory exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Found ops/ directory"
        })
        total += 10
    else:
        details.append({
            "item": "ops/ directory exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Missing ops/ directory"
        })

    # 2. 检查 JSON 文件存在且合法
    result_file = ops_dir / "price_comparison.json"
    if not result_file.is_file():
        details.append({
            "item": "price_comparison.json file exists and is valid JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not found"
        })
        # 后续无法继续，直接结束
        _write_score(total, details)
        return

    try:
        with open(result_file, "r") as f:
            data = json.load(f)
        details.append({
            "item": "price_comparison.json file exists and is valid JSON",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Valid JSON file"
        })
        total += 10
    except (json.JSONDecodeError, Exception) as e:
        details.append({
            "item": "price_comparison.json file exists and is valid JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Invalid JSON: {e}"
        })
        _write_score(total, details)
        return

    # 3. 字段完整性
    expected_keys = {"lumina_avg", "derm_avg", "gap"}
    provided_keys = set(data.keys())
    missing = expected_keys - provided_keys
    extra = provided_keys - expected_keys
    if missing:
        details.append({
            "item": "Required fields present",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Missing fields: {missing}"
        })
        # 字段不全，后续计算无意义，但继续尝试
    elif extra:
        details.append({
            "item": "Required fields present",
            "score": 5,
            "max_score": 10,
            "passed": False,
            "reason": f"Extra fields found: {extra} (not penalized further, but incomplete)"
        })
        total += 5
    else:
        details.append({
            "item": "Required fields present",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "All three fields exist"
        })
        total += 10

    if missing:
        # 如果缺少字段，无法进一步计算，给0分
        details.append({
            "item": "Numerical accuracy (lumina_avg)",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "Skipped due to missing fields"
        })
        details.append({
            "item": "Numerical accuracy (derm_avg)",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "Skipped due to missing fields"
        })
        details.append({
            "item": "Numerical accuracy (gap)",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "Skipped due to missing fields"
        })
        details.append({
            "item": "Exclusion of interference (discontinued/other brands)",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Cannot verify without all fields"
        })
        _write_score(total, details)
        return

    # 计算期望值（根据env_builder中的数据）
    # LuminaSkin active Hydration Serum SKUs (from skus.json):
    # sku_lum_hs01: 2999 cents = 29.99 USD
    # sku_lum_hs02: 3450 cents = 34.50 USD
    # sku_lum_hs03: 2499 cents = 24.99 USD
    lumina_prices_dol = [29.99, 34.50, 24.99]
    expected_lumina_avg = round(sum(lumina_prices_dol) / len(lumina_prices_dol), 2)  # 29.83

    # DermVeil active Hydration Serum SKUs:
    # sku_der_hs01: 2750 cents = 27.50 USD
    # sku_der_hs02: 3100 cents = 31.00 USD
    derm_prices_dol = [27.50, 31.00]
    expected_derm_avg = round(sum(derm_prices_dol) / len(derm_prices_dol), 2)  # 29.25
    expected_gap = round(expected_lumina_avg - expected_derm_avg, 2)  # 0.58

    # 允许误差 0.005 (因为四舍五入)
    tol = 0.005

    # 检查 lumina_avg
    lumina_ok = abs(data.get("lumina_avg") - expected_lumina_avg) < tol
    details.append({
        "item": "Numerical accuracy (lumina_avg)",
        "score": 20 if lumina_ok else 0,
        "max_score": 20,
        "passed": lumina_ok,
        "reason": f"Expected {expected_lumina_avg}, got {data.get('lumina_avg')}"
    })
    if lumina_ok: total += 20

    # 检查 derm_avg
    derm_ok = abs(data.get("derm_avg") - expected_derm_avg) < tol
    details.append({
        "item": "Numerical accuracy (derm_avg)",
        "score": 20 if derm_ok else 0,
        "max_score": 20,
        "passed": derm_ok,
        "reason": f"Expected {expected_derm_avg}, got {data.get('derm_avg')}"
    })
    if derm_ok: total += 20

    # 检查 gap
    gap_ok = abs(data.get("gap") - expected_gap) < tol
    details.append({
        "item": "Numerical accuracy (gap)",
        "score": 20 if gap_ok else 0,
        "max_score": 20,
        "passed": gap_ok,
        "reason": f"Expected {expected_gap}, got {data.get('gap')}"
    })
    if gap_ok: total += 20

    # 排除干扰（如果数值都正确，则自动说明排除干扰正确；否则检查是否因为包含discontinued导致）
    # 但我们增加一个单独项：确保未使用discontinued SKU（sku_der_hs03 2000美分）
    interference_ok = True
    # 如果 gap 正确，我们认为没有问题；否则检查是否因为包括了 discontinued SKU 导致数值偏离
    if not (lumina_ok and derm_ok and gap_ok):
        # 尝试推断：如果 derm_avg 比期望高很多，可能包括了 discontinued 的 20.00（实际2000美分=20.00美元）
        # 但这里不详细推理，简单给0分
        interference_ok = False

    details.append({
        "item": "Exclusion of interference (discontinued/other brands)",
        "score": 10 if interference_ok else 0,
        "max_score": 10,
        "passed": interference_ok,
        "reason": "No interference detected" if interference_ok else "Values indicate possible use of discontinued or irrelevant SKUs"
    })
    if interference_ok: total += 10

    _write_score(total, details)

def _write_score(total, details):
    score = {"total_score": total, "details": details}
    with open("workplace_score.json", "w") as f:
        json.dump(score, f, indent=2)
    print(json.dumps(score, indent=2))

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
