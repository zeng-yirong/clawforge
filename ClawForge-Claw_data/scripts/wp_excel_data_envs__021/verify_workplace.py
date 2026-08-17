#!/usr/bin/env python3
"""
验证器：检查 agent 产出的 cleaned_sales.csv 和 customer_average_order.json
基于预先构造的原始数据（已知完全重复的条目和缺失的 customer_name）。
评分细则（总分100）：
  - 目录结构正确（10分）：cleaned_sales.csv 存在（5分），customer_average_order.json 存在（5分）
  - 格式合法（10分）：CSV 和 JSON 可正常解析（各5分）
  - 去重正确（30分）：结果行数应为原始唯一行数（15分），且每行均不重复（15分）
  - 客户名称填充正确（20分）：所有缺失的 customer_name 已根据 accounts.csv 填充（逐行检查）
  - 平均订单金额计算正确（30分）：每个客户的平均值、订单数、总销售额与期望一致（每个客户10分）
"""
import sys
import os
import json
import csv

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total = 0

    # ---------- 目录结构 ----------
    score_dir = 0
    # 检查 cleaned_sales.csv
    csv_path = os.path.join(workspace, "cleaned_sales.csv")
    json_path = os.path.join(workspace, "customer_average_order.json")
    csv_exists = os.path.isfile(csv_path)
    json_exists = os.path.isfile(json_path)
    item = {}
    if csv_exists:
        score_dir += 5
        details.append({"item": "cleaned_sales.csv 存在", "score": 5, "max_score": 5, "passed": True, "reason": "文件存在"})
    else:
        details.append({"item": "cleaned_sales.csv 存在", "score": 0, "max_score": 5, "passed": False, "reason": "文件不存在"})
    if json_exists:
        score_dir += 5
        details.append({"item": "customer_average_order.json 存在", "score": 5, "max_score": 5, "passed": True, "reason": "文件存在"})
    else:
        details.append({"item": "customer_average_order.json 存在", "score": 0, "max_score": 5, "passed": False, "reason": "文件不存在"})
    total += score_dir

    # ---------- 格式合法 ----------
    score_format = 0
    if csv_exists:
        try:
            with open(csv_path, newline="") as f:
                reader = csv.reader(f)
                rows = list(reader)
            if len(rows) == 0:
                raise ValueError("空文件")
            score_format += 5
            details.append({"item": "CSV 可解析", "score": 5, "max_score": 5, "passed": True, "reason": "合法CSV"})
        except Exception as e:
            details.append({"item": "CSV 可解析", "score": 0, "max_score": 5, "passed": False, "reason": str(e)})
    else:
        details.append({"item": "CSV 可解析", "score": 0, "max_score": 5, "passed": False, "reason": "文件缺失"})
    if json_exists:
        try:
            with open(json_path) as f:
                data = json.load(f)
            if not isinstance(data, dict):
                raise ValueError("JSON顶层应为字典")
            score_format += 5
            details.append({"item": "JSON 可解析", "score": 5, "max_score": 5, "passed": True, "reason": "合法JSON"})
        except Exception as e:
            details.append({"item": "JSON 可解析", "score": 0, "max_score": 5, "passed": False, "reason": str(e)})
    else:
        details.append({"item": "JSON 可解析", "score": 0, "max_score": 5, "passed": False, "reason": "文件缺失"})
    total += score_format

    # ---------- 去重正确 ----------
    score_dedup = 0
    if csv_exists and csv_exists:
        try:
            with open(csv_path, newline="") as f:
                reader = csv.reader(f)
                cleaned_rows = list(reader)
            # 原始数据已知：共14行（含重复行），唯一行11行（去掉3个完全重复）
            # 我们直接读取原始数据并去重来得到期望行数
            expected_unique = [
                ["t1","2024-01-01","p1","Widget","Electronics","Gadgets","East","NYC","1","Alice","100.0","2","10","Credit","s1","John","Online"],
                ["t2","2024-01-02","p2","Gizmo","Home","Kitchen","West","LA","2","","200.0","1","0","Cash","s2","Jane","Retail"],
                ["t3","2024-01-03","p1","Widget","Electronics","Gadgets","North","Chicago","1","Alice","150.0","3","5","Debit","s1","John","Online"],
                ["t4","2024-01-04","p3","Thingamajig","Home","Garden","South","Houston","3","Charlie","75.0","5","15","Credit","s3","Jake","Online"],
                ["t5","2024-01-05","p2","Gizmo","Home","Kitchen","West","LA","2","","120.0","2","10","Cash","s2","Jane","Retail"],
                ["t6","2024-01-06","p4","Doodad","Office","Supplies","East","Boston","1","Alice","80.0","1","0","Debit","s4","Mike","Retail"],
                ["t7","2024-01-07","p1","Widget","Electronics","Gadgets","East","NYC","4","Diana","200.0","4","20","Cash","s5","Emma","Online"],
                ["t8","2024-01-08","p3","Thingamajig","Home","Garden","South","Houston","3","Charlie","90.0","3","5","Credit","s3","Jake","Online"],
                ["t9","2024-01-09","p5","Whatchamacallit","Electronics","Accessories","West","SF","5","","50.0","1","0","Credit","s6","Liam","Retail"],
                ["t10","2024-01-10","p4","Doodad","Office","Supplies","East","Boston","1","Alice","110.0","2","10","Debit","s4","Mike","Online"],
                ["t11","2024-01-11","p6","Gadget","Electronics","Gadgets","North","Detroit","6","Frank","300.0","6","30","Credit","s7","Nina","Retail"],
            ]
            # 注意：原始数据中第3行和第12行是重复，第10行和第14行重复
            expected_count = len(expected_unique)
            # 检查行数（不包括表头）
            actual_count = len(cleaned_rows) - 1 if cleaned_rows else 0
            # 检查是否有表头，并确保表头与原始一致
            header_ok = len(cleaned_rows) > 1 and cleaned_rows[0] == ["transaction_id","date","product_id","product_name","category","subcategory","region","city","customer_id","customer_name","sales_amount","quantity","discount","payment_method","salesperson_id","salesperson_name","channel"]
            if header_ok and actual_count == expected_count:
                score_dedup += 15
                details.append({"item": "行数正确", "score": 15, "max_score": 15, "passed": True, "reason": f"期望 {expected_count} 行，实际 {actual_count} 行"})
            else:
                details.append({"item": "行数正确", "score": 0, "max_score": 15, "passed": False, "reason": f"期望 {expected_count} 行，实际 {actual_count} 行或表头错误"})
            # 检查无重复行（转化为元组集合，长度与行数一致）
            data_rows = cleaned_rows[1:]  # 跳过表头
            row_tuples = [tuple(r) for r in data_rows]
            if len(set(row_tuples)) == len(row_tuples):
                score_dedup += 15
                details.append({"item": "无重复行", "score": 15, "max_score": 15, "passed": True, "reason": "所有行唯一"})
            else:
                details.append({"item": "无重复行", "score": 0, "max_score": 15, "passed": False, "reason": "存在重复行"})
        except Exception as e:
            details.append({"item": "去重检查异常", "score": 0, "max_score": 30, "passed": False, "reason": str(e)})
    else:
        details.append({"item": "去重检查", "score": 0, "max_score": 30, "passed": False, "reason": "文件缺失"})
    total += score_dedup

    # ---------- 客户名称填充 ----------
    score_fill = 0
    if csv_exists:
        try:
            # 读取 accounts
            accounts_path = os.path.join(workspace, "data", "accounts.csv")
            if not os.path.isfile(accounts_path):
                # 如果agent删除了原始文件，我们用已知数据
                acc_map = {"1":"Alice","2":"Bob","3":"Charlie","4":"Diana","5":"Eve","6":"Frank"}
            else:
                acc_map = {}
                with open(accounts_path, newline="") as f:
                    reader = csv.reader(f)
                    next(reader)  # skip header
                    for row in reader:
                        acc_map[row[0]] = row[1]
            with open(csv_path, newline="") as f:
                reader = csv.reader(f)
                head = next(reader)
                # 找到 customer_id 和 customer_name 列索引
                try:
                    cid_idx = head.index("customer_id")
                    cname_idx = head.index("customer_name")
                except ValueError:
                    raise ValueError("表头缺少 customer_id 或 customer_name")
                filled_ok = True
                for row in reader:
                    cid = row[cid_idx]
                    cname = row[cname_idx]
                    if cid in acc_map:
                        expected_name = acc_map[cid]
                        if cname != expected_name:
                            filled_ok = False
                            break
                if filled_ok:
                    score_fill = 20
                    details.append({"item": "客户名称填充正确", "score": 20, "max_score": 20, "passed": True, "reason": "所有 customer_name 与 accounts 一致"})
                else:
                    details.append({"item": "客户名称填充正确", "score": 0, "max_score": 20, "passed": False, "reason": "存在未正确填充的客户名称"})
        except Exception as e:
            details.append({"item": "填充检查异常", "score": 0, "max_score": 20, "passed": False, "reason": str(e)})
    else:
        details.append({"item": "填充检查", "score": 0, "max_score": 20, "passed": False, "reason": "文件缺失"})
    total += score_fill

    # ---------- 平均订单金额计算 ----------
    score_avg = 0
    if json_exists and csv_exists:
        try:
            # 从 cleaned_sales.csv 中计算期望的汇总
            with open(csv_path, newline="") as f:
                reader = csv.reader(f)
                head = next(reader)
                cid_idx = head.index("customer_id")
                cname_idx = head.index("customer_name")
                amount_idx = head.index("sales_amount")
                sums = {}
                counts = {}
                names = {}
                for row in reader:
                    cid = row[cid_idx]
                    name = row[cname_idx]
                    amount = float(row[amount_idx])
                    sums[cid] = sums.get(cid, 0.0) + amount
                    counts[cid] = counts.get(cid, 0) + 1
                    names[cid] = name
            expected_summary = {}
            for cid in sums:
                expected_summary[cid] = {
                    "customer_name": names[cid],
                    "average_order": round(sums[cid] / counts[cid], 2),
                    "total_orders": counts[cid],
                    "total_sales": round(sums[cid], 2)
                }
            # 读取 agent 的 JSON
            with open(json_path) as f:
                agent_data = json.load(f)
            # 检查每个客户
            all_ok = True
            for cid, expect in expected_summary.items():
                if cid not in agent_data:
                    all_ok = False
                    break
                agent_entry = agent_data[cid]
                # 比较字段
                if (agent_entry.get("customer_name") != expect["customer_name"] or
                    agent_entry.get("average_order") != expect["average_order"] or
                    agent_entry.get("total_orders") != expect["total_orders"] or
                    agent_entry.get("total_sales") != expect["total_sales"]):
                    all_ok = False
                    break
            # 也检查 agent 是否有多余客户（不允许）
            if all_ok and len(agent_data) == len(expected_summary):
                score_avg = 30
                details.append({"item": "平均订单金额计算正确", "score": 30, "max_score": 30, "passed": True, "reason": f"所有 {len(expected_summary)} 个客户数据匹配"})
            else:
                details.append({"item": "平均订单金额计算正确", "score": 0, "max_score": 30, "passed": False, "reason": "数据不一致或有多余客户"})
        except Exception as e:
            details.append({"item": "平均计算异常", "score": 0, "max_score": 30, "passed": False, "reason": str(e)})
    else:
        details.append({"item": "平均计算检查", "score": 0, "max_score": 30, "passed": False, "reason": "必要文件缺失"})
    total += score_avg

    # 写入评分文件
    result = {
        "total_score": min(total, 100),
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score: {result['total_score']}/100 saved to workplace_score.json")

if __name__ == "__main__":
    main()
