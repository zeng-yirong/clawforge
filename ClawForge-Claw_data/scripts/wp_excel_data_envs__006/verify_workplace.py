import os
import sys
import csv
import json

def load_accounts(workspace):
    path = os.path.join(workspace, "data", "accounts.csv")
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        reader = csv.DictReader(f)
        return {row["account_id"]: row["display_name"] for row in reader}

def load_raw_sales(workspace):
    path = os.path.join(workspace, "data", "sales_raw.csv")
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        reader = csv.DictReader(f)
        return list(reader)

def remove_duplicates(rows):
    seen = set()
    result = []
    for row in rows:
        # 用所有字段的tuple作为唯一标识
        key = tuple(row.values())
        if key not in seen:
            seen.add(key)
            result.append(row)
    return result

def fill_missing(rows, accounts):
    for row in rows:
        if not row["customer_name"].strip() and row["customer_id"] in accounts:
            row["customer_name"] = accounts[row["customer_id"]]
        # 处理 sales_amount 缺失
        if not row["sales_amount"].strip():
            row["sales_amount"] = "0.0"
        # 确保 numeric 字段可转 float
        try:
            float(row["sales_amount"])
        except ValueError:
            row["sales_amount"] = "0.0"
    return rows

def compute_region_monthly(rows):
    import datetime
    result = {}
    for row in rows:
        dt = datetime.datetime.strptime(row["date"], "%Y-%m-%d")
        month_name = dt.strftime("%B")  # e.g. "January"
        region = row["region"]
        key = (region, month_name)
        if key not in result:
            result[key] = {"sales": 0.0, "orders": 0}
        result[key]["sales"] += float(row["sales_amount"])
        result[key]["orders"] += 1
    # 转成列表排序后返回
    sorted_items = sorted(result.items(), key=lambda x: x[0])
    return [(r, m, v["sales"], v["orders"]) for (r, m), v in sorted_items]

def compute_monthly_avg(rows):
    import datetime
    monthly = {}
    for row in rows:
        dt = datetime.datetime.strptime(row["date"], "%Y-%m-%d")
        month_name = dt.strftime("%B")
        if month_name not in monthly:
            monthly[month_name] = {"total_sales": 0.0, "order_count": 0}
        monthly[month_name]["total_sales"] += float(row["sales_amount"])
        monthly[month_name]["order_count"] += 1
    avg = {}
    for m, v in monthly.items():
        avg[m] = round(v["total_sales"] / v["order_count"], 2) if v["order_count"] > 0 else 0.0
    return avg

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."

    details = []
    total_score = 0

    # 1. 检查 output 目录
    output_dir = os.path.join(workspace, "output")
    dir_exists = os.path.isdir(output_dir)
    details.append({
        "item": "output directory exists",
        "score": 10 if dir_exists else 0,
        "max_score": 10,
        "passed": dir_exists,
        "reason": "Found output directory" if dir_exists else "output directory missing"
    })
    if dir_exists:
        total_score += 10

    # 2. 检查 cleaned_sales.csv 存在且合法
    cleaned_path = os.path.join(workspace, "output", "cleaned_sales.csv")
    cleaned_ok = os.path.isfile(cleaned_path)
    if cleaned_ok:
        try:
            with open(cleaned_path, "r") as f:
                csv.reader(f).__next__()
        except Exception:
            cleaned_ok = False
    details.append({
        "item": "cleaned_sales.csv exists and is valid CSV",
        "score": 10 if cleaned_ok else 0,
        "max_score": 10,
        "passed": cleaned_ok,
        "reason": "File exists and readable" if cleaned_ok else "Missing or malformed CSV"
    })
    if cleaned_ok:
        total_score += 10

    # 3. 检查 region_monthly_summary.csv
    summary_path = os.path.join(workspace, "output", "region_monthly_summary.csv")
    summary_ok = os.path.isfile(summary_path)
    if summary_ok:
        try:
            with open(summary_path, "r") as f:
                csv.reader(f).__next__()
        except Exception:
            summary_ok = False
    details.append({
        "item": "region_monthly_summary.csv exists and is valid CSV",
        "score": 10 if summary_ok else 0,
        "max_score": 10,
        "passed": summary_ok,
        "reason": "File exists and readable" if summary_ok else "Missing or malformed CSV"
    })
    if summary_ok:
        total_score += 10

    # 4. 检查 monthly_avg_order.json
    avg_path = os.path.join(workspace, "output", "monthly_avg_order.json")
    avg_ok = os.path.isfile(avg_path)
    if avg_ok:
        try:
            with open(avg_path, "r") as f:
                json.load(f)
        except Exception:
            avg_ok = False
    details.append({
        "item": "monthly_avg_order.json exists and is valid JSON",
        "score": 10 if avg_ok else 0,
        "max_score": 10,
        "passed": avg_ok,
        "reason": "File exists and valid JSON" if avg_ok else "Missing or malformed JSON"
    })
    if avg_ok:
        total_score += 10

    # 如果基础文件都缺失，后续比较无法进行，提前返回
    if not (cleaned_ok and summary_ok and avg_ok):
        # 但满分可能总分为0，直接写结果
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # 5. 验证 cleaned_sales.csv 内容
    accounts = load_accounts(workspace)
    raw_rows = load_raw_sales(workspace)
    if raw_rows is None:
        # 原始数据缺失，则无法验证（但不应该发生）
        details.append({
            "item": "cleaned_sales.csv content correctness",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "Original data missing"
        })
        total_score += 0
    else:
        # 计算预期清洗结果
        deduplicated = remove_duplicates(raw_rows)
        expected_clean = fill_missing(deduplicated, accounts)
        # 读取agent输出
        with open(cleaned_path, "r") as f:
            reader = csv.DictReader(f)
            agent_rows = list(reader)
        # 比较：按transaction_id排序后比较所有字段（忽略顺序）
        sort_key = lambda r: r["transaction_id"]
        expected_sorted = sorted(expected_clean, key=sort_key)
        agent_sorted = sorted(agent_rows, key=sort_key)
        content_ok = True
        reason = ""
        if len(expected_sorted) != len(agent_sorted):
            content_ok = False
            reason = f"Row count mismatch: expected {len(expected_sorted)}, got {len(agent_sorted)}"
        else:
            for e, a in zip(expected_sorted, agent_sorted):
                for key in e.keys():
                    if str(e[key]).strip() != str(a.get(key, "")).strip():
                        content_ok = False
                        reason = f"Mismatch in row {e['transaction_id']} field '{key}': expected '{e[key]}', got '{a.get(key,'')}'"
                        break
                if not content_ok:
                    break
            if content_ok:
                reason = "All fields match expected cleaned data"
        details.append({
            "item": "cleaned_sales.csv content correctness",
            "score": 20 if content_ok else 0,
            "max_score": 20,
            "passed": content_ok,
            "reason": reason
        })
        total_score += 20 if content_ok else 0

        # 6. 验证 region_monthly_summary.csv
        # 预期汇总
        expected_summary = compute_region_monthly(expected_clean)
        # 读取agent摘要
        with open(summary_path, "r") as f:
            reader = csv.DictReader(f)
            agent_summary = list(reader)
        # 将agent数据转为字典 (region, month) -> (sales, orders)
        agent_dict = {}
        for row in agent_summary:
            r = row.get("region", "").strip()
            m = row.get("month", "").strip()
            try:
                s = float(row.get("total_sales", 0))
                o = int(float(row.get("total_orders", 0)))  # 可能会有小数，但订单数应为整数
            except (ValueError, TypeError):
                s = 0.0; o = 0
            agent_dict[(r, m)] = (s, o)
        summary_ok = True
        reason = ""
        # 检查预期条目都在agent中且数值一致
        for (r, m, es, eo) in expected_summary:
            key = (r, m)
            if key not in agent_dict:
                summary_ok = False
                reason = f"Missing region={r}, month={m} in summary"
                break
            as_, ao = agent_dict[key]
            if abs(as_ - es) > 0.01 or ao != eo:
                summary_ok = False
                reason = f"Region={r}, month={m} expected sales={es}, orders={eo}; got sales={as_}, orders={ao}"
                break
        if summary_ok and len(agent_dict) != len(expected_summary):
            summary_ok = False
            reason = f"Extra rows in summary: expected {len(expected_summary)} rows, got {len(agent_dict)}"
        if summary_ok:
            reason = "All region-month aggregations match"
        details.append({
            "item": "region_monthly_summary.csv content correctness",
            "score": 20 if summary_ok else 0,
            "max_score": 20,
            "passed": summary_ok,
            "reason": reason
        })
        total_score += 20 if summary_ok else 0

        # 7. 验证 monthly_avg_order.json
        expected_avg = compute_monthly_avg(expected_clean)
        with open(avg_path, "r") as f:
            agent_avg = json.load(f)
        avg_ok = True
        reason = ""
        # agent输出可能是一个对象，我们期望键是月份名称，值是数字
        for month, exp_val in expected_avg.items():
            if month not in agent_avg:
                avg_ok = False
                reason = f"Missing month {month}"
                break
            act_val = agent_avg[month]
            if isinstance(act_val, str):
                try:
                    act_val = float(act_val)
                except:
                    avg_ok = False
                    reason = f"Month {month} value not numeric: {act_val}"
                    break
            if abs(act_val - exp_val) > 0.01:
                avg_ok = False
                reason = f"Month {month} expected {exp_val}, got {act_val}"
                break
        # 检查agent没有多余月份
        if avg_ok:
            extra = set(agent_avg.keys()) - set(expected_avg.keys())
            if extra:
                avg_ok = False
                reason = f"Extra months in output: {extra}"
        if avg_ok:
            reason = "All monthly averages correct"
        details.append({
            "item": "monthly_avg_order.json content correctness",
            "score": 20 if avg_ok else 0,
            "max_score": 20,
            "passed": avg_ok,
            "reason": reason
        })
        total_score += 20 if avg_ok else 0

    # 写入评分结果
    result = {"total_score": total_score, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
