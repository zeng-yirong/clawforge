import sys
import os
import csv
import json
import math

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    os.chdir(workspace)  # 切换到工作区目录

    score_details = []
    total_raw_score = 0
    max_score = 100

    # 1. 检查产物文件是否存在
    result_path = "report/summary.json"
    if os.path.isfile(result_path):
        score_details.append({"item": "产物文件存在", "score": 10, "max_score": 10, "passed": True, "reason": "report/summary.json 存在"})
        total_raw_score += 10
    else:
        score_details.append({"item": "产物文件存在", "score": 0, "max_score": 10, "passed": False, "reason": "report/summary.json 不存在"})
        # 后续检查无法进行，直接输出并退出
        _write_score(total_raw_score, score_details)
        return

    # 2. 读取并验证 JSON 格式
    try:
        with open(result_path, "r") as f:
            data = json.load(f)
        score_details.append({"item": "JSON 格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "正确解析 JSON"})
        total_raw_score += 10
    except (json.JSONDecodeError, Exception) as e:
        score_details.append({"item": "JSON 格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析失败: {e}"})
        _write_score(total_raw_score, score_details)
        return

    # 3. 检查 categories 字段
    if "categories" not in data or not isinstance(data["categories"], list):
        score_details.append({"item": "包含 categories 列表", "score": 0, "max_score": 10, "passed": False, "reason": "categories 字段缺失或不是列表"})
        _write_score(total_raw_score, score_details)
        return
    score_details.append({"item": "包含 categories 列表", "score": 10, "max_score": 10, "passed": True, "reason": "存在 categories 列表"})
    total_raw_score += 10

    # 4. 读取原始数据，按规则计算预期结果
    # 4.1 读取映射
    prod_map = {}
    with open("data/products.csv", "r") as f:
        for row in csv.DictReader(f):
            prod_map[row["product_id"]] = row  # 包含 product_name, category, subcategory

    cust_map = {}
    with open("data/customers.csv", "r") as f:
        for row in csv.DictReader(f):
            cust_map[row["customer_id"]] = row["customer_name"]

    # 4.2 读取销售数据，清洗
    clean_rows = []
    seen = set()  # 用于去重（整行去重）
    with open("data/raw_sales.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 转成可哈希元组（去掉空格，保留顺序）
            row_tuple = tuple(row.values())
            if row_tuple in seen:
                continue
            seen.add(row_tuple)

            # 剔除异常数值
            try:
                sales = float(row["sales_amount"])
                qty = int(row["quantity"])
            except (ValueError, KeyError):
                continue
            if sales <= 0 or qty <= 0:
                continue

            # 填充缺失名称
            pid = row.get("product_id", "")
            cid = row.get("customer_id", "")

            # 产品名填充
            pname = row.get("product_name", "").strip()
            if not pname and pid in prod_map:
                pname = prod_map[pid]["product_name"]
            # 如果仍然为空则剔除（但本数据集中所有 pid 都在映射中）
            if not pname:
                continue

            # 客户名填充
            cname = row.get("customer_name", "").strip()
            if not cname and cid in cust_map:
                cname = cust_map[cid]
            if not cname:
                continue

            # 获取 category（从映射中保证一致）
            if pid in prod_map:
                category = prod_map[pid]["category"]
            else:
                # 如果 product_id 不在映射中，使用行内 category（但本数据集中都在）
                category = row.get("category", "").strip()
                if not category:
                    continue

            # 计算实际收入
            discount = int(row.get("discount", 0))
            line_total = sales * qty * (1 - discount / 100.0)

            clean_rows.append({
                "category": category,
                "line_total": line_total
            })

    # 4.3 按类别汇总
    expected = {}
    for r in clean_rows:
        cat = r["category"]
        if cat not in expected:
            expected[cat] = {"total_sales": 0.0, "order_count": 0}
        expected[cat]["total_sales"] += r["line_total"]
        expected[cat]["order_count"] += 1

    # 计算平均
    for cat in expected:
        expected[cat]["average_order"] = round(expected[cat]["total_sales"] / expected[cat]["order_count"], 2)

    # 4.4 将预期结果转为与 agent 输出同结构
    expected_list = []
    for cat in sorted(expected.keys()):
        expected_list.append({
            "category": cat,
            "total_sales": round(expected[cat]["total_sales"], 2),
            "average_order": expected[cat]["average_order"],
            "order_count": expected[cat]["order_count"]
        })

    # 5. 比较 agent 输出
    agent_list = data["categories"]
    # 检查长度
    if len(agent_list) != len(expected_list):
        score_details.append({"item": "类别数量正确", "score": 0, "max_score": 10, "passed": False,
                              "reason": f"期望 {len(expected_list)} 个类别，实际 {len(agent_list)}"})
        _write_score(total_raw_score, score_details)
        return
    score_details.append({"item": "类别数量正确", "score": 10, "max_score": 10, "passed": True, "reason": f"包含 {len(expected_list)} 个类别"})
    total_raw_score += 10

    # 将 agent 输出转为字典方便比较
    agent_dict = {item["category"]: item for item in agent_list}
    for exp_item in expected_list:
        cat = exp_item["category"]
        if cat not in agent_dict:
            score_details.append({"item": f"类别 '{cat}' 存在", "score": 0, "max_score": 5, "passed": False, "reason": f"缺少类别 {cat}"})
            continue
        # 比较三个数值
        agent_item = agent_dict[cat]
        mismatches = []
        # total_sales
        try:
            if not math.isclose(agent_item["total_sales"], exp_item["total_sales"], rel_tol=1e-5):
                mismatches.append(f"total_sales 期望 {exp_item['total_sales']}，得到 {agent_item['total_sales']}")
        except (KeyError, TypeError):
            mismatches.append("total_sales 字段缺失或类型错误")
        # average_order
        try:
            if not math.isclose(agent_item["average_order"], exp_item["average_order"], rel_tol=1e-5):
                mismatches.append(f"average_order 期望 {exp_item['average_order']}，得到 {agent_item['average_order']}")
        except (KeyError, TypeError):
            mismatches.append("average_order 字段缺失或类型错误")
        # order_count
        try:
            if agent_item["order_count"] != exp_item["order_count"]:
                mismatches.append(f"order_count 期望 {exp_item['order_count']}，得到 {agent_item['order_count']}")
        except (KeyError, TypeError):
            mismatches.append("order_count 字段缺失或类型错误")

        if mismatches:
            score_details.append({"item": f"类别 '{cat}' 数值准确", "score": 0, "max_score": 35, "passed": False, "reason": "; ".join(mismatches)})
        else:
            score_details.append({"item": f"类别 '{cat}' 数值准确", "score": 35, "max_score": 35, "passed": True, "reason": "所有数值匹配"})
            total_raw_score += 35

    _write_score(total_raw_score, score_details)


def _write_score(score, details):
    total = max(100, score)  # 防止超分
    result = {
        "total_score": min(100, score),
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written: {result['total_score']}")

if __name__ == "__main__":
    main()
