import json, sys, os
from pathlib import Path

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    ws = Path(workspace)

    details = []
    total_score = 0
    max_total = 100

    # 1. 检查必要目录和文件是否存在（10分）
    dirs_files = [
        ("data/", True),
        ("data/skus.json", True),
        ("data/price_books.json", True),
        ("ops/", True),
        ("ops/competitor_analysis.json", False),  # agent 产物
    ]
    for path_str, must_exist in dirs_files:
        p = ws / path_str
        exists = p.exists()
        if must_exist and not exists:
            details.append({"item": f"缺失必要路径: {path_str}", "score": 0, "max_score": 5 if path_str.endswith('/') else 3, "passed": False, "reason": "文件/目录不存在"})
        elif not must_exist and not exists:
            details.append({"item": f"产物缺失: {path_str}", "score": 0, "max_score": 10, "passed": False, "reason": "未生成"})
        else:
            details.append({"item": f"路径存在: {path_str}", "score": 5 if path_str.endswith('/') else 3, "max_score": 5 if path_str.endswith('/') else 3, "passed": True, "reason": "存在"})
    # 初期总分累加（仅目录/文件存在的得分先加，后面再调整）
    # 先收集总得分，后面统一计算

    # 2. 尝试读取产物并验证
    result_path = ws / "ops/competitor_analysis.json"
    if not result_path.exists():
        # 已经记录了缺失，直接返回
        details.append({"item": "读取产物", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        _write_score(ws, details, 0)
        return

    try:
        with open(result_path, "r") as f:
            agent_result = json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        details.append({"item": "JSON解析", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON格式错误: {e}"})
        _write_score(ws, details, 0)
        return

    # 3. 准备预期结果
    try:
        with open(ws / "data/skus.json", "r") as f:
            all_skus = json.load(f)
        with open(ws / "data/price_books.json", "r") as f:
            all_pbs = json.load(f)
    except Exception as e:
        details.append({"item": "读取原始数据", "score": 0, "max_score": 5, "passed": False, "reason": f"无法读取原始数据: {e}"})
        _write_score(ws, details, 0)
        return

    # 找到当前有效价格书
    current_pb = None
    for pb in all_pbs:
        if pb.get("is_current") is True and pb.get("status") == "approved":
            current_pb = pb
            break
    if not current_pb:
        details.append({"item": "当前价格书查找", "score": 0, "max_score": 5, "passed": False, "reason": "未找到当前有效价格书"})
        _write_score(ws, details, 0)
        return

    # 构建价格映射
    price_map = {}
    for entry in current_pb.get("entries", []):
        sku_id = entry.get("sku_id")
        price = entry.get("price")
        if sku_id and price is not None:
            price_map[sku_id] = price

    # 过滤符合条件的 SKU
    expected_records = []
    for sku in all_skus:
        if sku.get("category_name") != "Hydration Serum":
            continue
        if sku.get("status") != "active":
            continue
        if sku.get("sku_id") not in price_map:
            continue
        expected_records.append({
            "brand_name": sku["brand_name"],
            "sku_name": sku["sku_name"],
            "price": price_map[sku["sku_id"]],
            "selling_points_count": len(sku.get("selling_points", []))
        })

    # 按要求排序: 先brand_name升序，再sku_name升序
    expected_records.sort(key=lambda x: (x["brand_name"].lower(), x["sku_name"].lower()))

    # 4. 验证 agent 结果
    # 4.1 检查是否为列表（5分）
    if not isinstance(agent_result, list):
        details.append({"item": "结果类型", "score": 0, "max_score": 5, "passed": False, "reason": "应为数组"})
        _write_score(ws, details, 0)
        return
    else:
        details.append({"item": "结果类型", "score": 5, "max_score": 5, "passed": True, "reason": "是数组"})

    # 4.2 检查记录数（10分）
    if len(agent_result) != len(expected_records):
        details.append({"item": "记录数量", "score": 0, "max_score": 10, "passed": False, "reason": f"期望{len(expected_records)}条，实际{len(agent_result)}条"})
    else:
        details.append({"item": "记录数量", "score": 10, "max_score": 10, "passed": True, "reason": "数量正确"})

    # 4.3 逐条检查字段存在性和数值（共70分，每错一条扣10分，最多扣到0）
    field_score_per_record = 70 / len(expected_records) if expected_records else 0
    correct_count = 0
    for i, (exp, act) in enumerate(zip(expected_records, agent_result)):
        # 检查必要字段
        if not isinstance(act, dict):
            continue
        missing_fields = []
        for f in ["brand_name", "sku_name", "price", "selling_points_count"]:
            if f not in act:
                missing_fields.append(f)
        if missing_fields:
            continue
        # 比较数值
        if (act.get("brand_name") == exp["brand_name"] and
            act.get("sku_name") == exp["sku_name"] and
            act.get("price") == exp["price"] and
            act.get("selling_points_count") == exp["selling_points_count"]):
            correct_count += 1
        else:
            # 记录错误原因
            pass

    if correct_count == len(expected_records):
        details.append({"item": "内容准确性", "score": 70, "max_score": 70, "passed": True, "reason": "全部匹配"})
    else:
        score_earned = int(correct_count / len(expected_records) * 70)
        details.append({"item": "内容准确性", "score": score_earned, "max_score": 70, "passed": False, "reason": f"正确{correct_count}/{len(expected_records)}条"})

    # 5. 额外检查：不允许有多余字段（5分）
    extra_fields_penalty = 0
    for rec in agent_result:
        if isinstance(rec, dict):
            extra = set(rec.keys()) - {"brand_name", "sku_name", "price", "selling_points_count"}
            if extra:
                extra_fields_penalty = 5
                break
    if extra_fields_penalty:
        details.append({"item": "字段纯洁性", "score": 0, "max_score": 5, "passed": False, "reason": "存在多余字段"})
    else:
        details.append({"item": "字段纯洁性", "score": 5, "max_score": 5, "passed": True, "reason": "无多余字段"})

    # 计算总分
    total_score = sum(d["score"] for d in details)
    _write_score(ws, details, total_score)

def _write_score(ws, details, total):
    score_data = {
        "total_score": total,
        "details": details
    }
    with open(ws / "workplace_score.json", "w") as f:
        json.dump(score_data, f, indent=2)

if __name__ == "__main__":
    main()
