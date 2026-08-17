import json
import os
import sys

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

def compute_expected():
    """根据 env_builder 的逻辑计算预期产物"""
    # 读取 SKU
    with open(os.path.join(workspace, "data/skus/skus.json")) as f:
        skus_data = json.load(f)
    skus = skus_data["skus"]

    # 读取价目表
    with open(os.path.join(workspace, "data/pricing/price_books.json")) as f:
        pb_data = json.load(f)
    price_books = pb_data["price_books"]

    # 找到当前价目表
    current_pb = None
    for pb in price_books:
        if pb.get("is_current") is True:
            current_pb = pb
            break
    if current_pb is None:
        raise ValueError("No current price book found")

    # 构建价格映射
    price_map = {}
    for entry in current_pb["entries"]:
        price_map[entry["sku_id"]] = entry["price"]

    # 过滤 LuminaSkin 活跃SKU
    result = []
    for sku in skus:
        if sku["brand_name"] == "LuminaSkin" and sku["status"] == "active":
            sku_id = sku["sku_id"]
            if sku_id not in price_map:
                continue
            result.append({
                "sku_id": sku["sku_id"],
                "sku_name": sku["sku_name"],
                "category_name": sku["category_name"],
                "price": price_map[sku_id]
            })
    # 按 sku_id 排序保证确定性
    result.sort(key=lambda x: x["sku_id"])
    return result

expected = compute_expected()

def evaluate():
    details = []
    total_score = 0

    # 1. 目录结构（10分）
    report_path = os.path.join(workspace, "reports/competitor_report.json")
    dir_exists = os.path.isdir(os.path.join(workspace, "reports"))
    if dir_exists:
        details.append({"item": "reports directory created", "score": 5, "max_score": 5, "passed": True, "reason": "目录存在"})
        total_score += 5
    else:
        details.append({"item": "reports directory created", "score": 0, "max_score": 5, "passed": False, "reason": "目录不存在"})

    file_exists = os.path.isfile(report_path)
    if file_exists:
        details.append({"item": "competitor_report.json file exists", "score": 5, "max_score": 5, "passed": True, "reason": "文件存在"})
        total_score += 5
    else:
        details.append({"item": "competitor_report.json file exists", "score": 0, "max_score": 5, "passed": False, "reason": "文件不存在"})
        # 如果文件不存在，后续检查无法进行，直接返回
        score_dict = {"total_score": total_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(score_dict, f)
        return

    # 2. JSON格式合法（10分）
    try:
        with open(report_path) as f:
            agent_data = json.load(f)
        details.append({"item": "JSON格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "解析成功"})
        total_score += 10
    except Exception as e:
        details.append({"item": "JSON格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {str(e)}"})
        # 仍然可以继续检查，但后续可能出错
        agent_data = None

    if agent_data is None or not isinstance(agent_data, list):
        details.append({"item": "产物应为列表", "score": 0, "max_score": 10, "passed": False, "reason": "不是JSON数组"})
    else:
        details.append({"item": "产物是列表", "score": 10, "max_score": 10, "passed": True, "reason": "类型正确"})
        total_score += 10

    # 3. 过滤活跃SKU（20分）
    if agent_data is not None and isinstance(agent_data, list):
        # 检查是否包含了停产SKU LS-OLD-003
        has_discontinued = any(item["sku_id"] == "LS-OLD-003" for item in agent_data)
        if has_discontinued:
            details.append({"item": "过滤掉停产SKU", "score": 0, "max_score": 20, "passed": False, "reason": "包含已停产的LS-OLD-003"})
        else:
            details.append({"item": "过滤掉停产SKU", "score": 20, "max_score": 20, "passed": True, "reason": "未包含停产SKU"})
            total_score += 20

    # 4. 使用最新价目表（20分）
    if agent_data is not None and isinstance(agent_data, list):
        # 检查价格是否来自Q2（48.50和40.00），而不是Q1（45.00和38.00）
        price_errors = []
        for item in agent_data:
            if item["sku_id"] == "LS-HS-001" and item["price"] != 48.50:
                price_errors.append(f"LS-HS-001价格应为48.50，实际为{item['price']}")
            if item["sku_id"] == "LS-UV-002" and item["price"] != 40.00:
                price_errors.append(f"LS-UV-002价格应为40.00，实际为{item['price']}")
        if price_errors:
            details.append({"item": "使用当前价目表(APAC-Q2-2026)", "score": 0, "max_score": 20, "passed": False, "reason": "; ".join(price_errors)})
        else:
            details.append({"item": "使用当前价目表(APAC-Q2-2026)", "score": 20, "max_score": 20, "passed": True, "reason": "价格正确"})
            total_score += 20

    # 5. 价格数值精确（20分）
    # 已经包含在上一步，但这里单独检查数值是否准确
    if agent_data is not None and isinstance(agent_data, list):
        if len(agent_data) != len(expected):
            details.append({"item": "记录数量正确", "score": 0, "max_score": 10, "passed": False, "reason": f"期望{len(expected)}条，实际{len(agent_data)}条"})
        else:
            # 检查每条记录
            match = True
            for i, (exp, act) in enumerate(zip(expected, agent_data)):
                if exp["sku_id"] != act.get("sku_id") or exp["price"] != act.get("price"):
                    match = False
                    break
            if match:
                details.append({"item": "记录数量和价格完全匹配", "score": 20, "max_score": 20, "passed": True, "reason": "精确匹配"})
                total_score += 20
            else:
                details.append({"item": "记录数量和价格完全匹配", "score": 0, "max_score": 20, "passed": False, "reason": "与预期不完全一致"})

    # 6. 无多余字段（10分）
    if agent_data is not None and isinstance(agent_data, list):
        allowed_keys = {"sku_id", "sku_name", "category_name", "price"}
        extra_found = False
        for item in agent_data:
            if set(item.keys()) != allowed_keys:
                extra_found = True
                break
        if extra_found:
            details.append({"item": "无多余字段", "score": 0, "max_score": 10, "passed": False, "reason": "包含不允许的字段"})
        else:
            details.append({"item": "无多余字段", "score": 10, "max_score": 10, "passed": True, "reason": "字段集合正确"})
            total_score += 10

    # 7. 只含LuminaSkin品牌（10分）
    if agent_data is not None and isinstance(agent_data, list):
        wrong_brand = any(item.get("sku_id","").startswith("DV-") or item.get("sku_id","").startswith("AP-") for item in agent_data)
        if wrong_brand:
            details.append({"item": "只包含LuminaSkin品牌", "score": 0, "max_score": 10, "passed": False, "reason": "混入了其他品牌SKU"})
        else:
            details.append({"item": "只包含LuminaSkin品牌", "score": 10, "max_score": 10, "passed": True, "reason": "无一漏网"})
            total_score += 10

    # 生成最终分数
    score_dict = {"total_score": total_score, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(score_dict, f, indent=2)

if __name__ == "__main__":
    evaluate()
