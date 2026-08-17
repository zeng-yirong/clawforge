import sys
import os
import json
import csv
import math

def load_csv(path):
    """加载CSV文件，返回列表字典，字段名小写化。如果文件不存在或解析失败返回None"""
    if not os.path.isfile(path):
        return None
    try:
        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = []
            for row in reader:
                # 键小写
                norm = {k.strip().lower(): v.strip() for k, v in row.items()}
                rows.append(norm)
            return rows
    except:
        return None

def verify(workspace):
    details = []
    total_score = 0
    max_total = 100

    # 1. 检查 report 目录是否存在 (10分)
    report_dir = os.path.join(workspace, "report")
    if os.path.isdir(report_dir):
        details.append({"item": "report目录存在", "score": 10, "max_score": 10, "passed": True, "reason": "report目录已创建"})
        total_score += 10
    else:
        details.append({"item": "report目录存在", "score": 0, "max_score": 10, "passed": False, "reason": "report目录未找到"})

    # 2. 检查 average_order.csv 文件是否存在 (10分)
    csv_path = os.path.join(report_dir, "average_order.csv") if os.path.isdir(report_dir) else os.path.join(workspace, "report", "average_order.csv")
    if os.path.isfile(csv_path):
        details.append({"item": "average_order.csv存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
        total_score += 10
    else:
        details.append({"item": "average_order.csv存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        # 后续检查如果文件不存在则直接返回
        final_score = total_score
        result = {"total_score": final_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # 3. 检查CSV文件格式合法性（表头、行数等）(10分)
    rows = load_csv(csv_path)
    if rows is None:
        details.append({"item": "CSV格式合法", "score": 0, "max_score": 10, "passed": False, "reason": "无法解析CSV"})
    else:
        expected_headers = {"product_id", "product_name", "avg_sales_amount"}
        actual_headers = set(rows[0].keys()) if rows else set()
        if expected_headers.issubset(actual_headers):
            details.append({"item": "CSV格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "表头正确，可解析"})
            total_score += 10
        else:
            details.append({"item": "CSV格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"缺少必要列：{expected_headers - actual_headers}"})

    # 4. 检查去重是否正确 (20分)
    # 读取原始销售数据，去重（定义：完全行重复），并填充缺失产品名
    raw_path = os.path.join(workspace, "data", "sales_raw.csv")
    raw_rows = load_csv(raw_path)
    if raw_rows is None:
        details.append({"item": "去重正确", "score": 0, "max_score": 20, "passed": False, "reason": "原始文件无法读取"})
    else:
        # 去重（基于所有字段的元组）
        seen = set()
        unique_rows = []
        for row in raw_rows:
            # 构建元组，注意字段顺序固定
            key = tuple(row.get(h, "") for h in ["transaction_id","date","product_id","product_name","category","subcategory","region","city","customer_id","customer_name","sales_amount","quantity","discount","payment_method","salesperson_id","salesperson_name","channel"])
            if key not in seen:
                seen.add(key)
                unique_rows.append(row)
        # 加载映射
        mapping_path = os.path.join(workspace, "data", "product_mapping.csv")
        mapping_rows = load_csv(mapping_path)
        mapping = {}
        if mapping_rows:
            for m in mapping_rows:
                mapping[m["product_id"]] = m["product_name"]
        # 填充缺失 product_name
        for row in unique_rows:
            if not row.get("product_name") and row.get("product_id") in mapping:
                row["product_name"] = mapping[row["product_id"]]
        # 计算期望的平均值（按 product_id, product_name 分组）
        product_groups = {}
        for row in unique_rows:
            pid = row.get("product_id", "")
            pname = row.get("product_name", "")
            try:
                amount = float(row.get("sales_amount", "0"))
            except:
                continue
            key = (pid, pname)
            if key not in product_groups:
                product_groups[key] = []
            product_groups[key].append(amount)
        expected_rows = []
        for (pid, pname), amounts in product_groups.items():
            avg = sum(amounts) / len(amounts)
            avg_rounded = round(avg, 2)
            expected_rows.append({"product_id": pid, "product_name": pname, "avg_sales_amount": avg_rounded})
        # 按product_id排序比较
        expected_sorted = sorted(expected_rows, key=lambda x: x["product_id"])
        # 读取agent输出
        agent_rows = load_csv(csv_path)
        if agent_rows is None:
            details.append({"item": "去重正确", "score": 0, "max_score": 20, "passed": False, "reason": "agent输出无法解析"})
        else:
            # 标准化agent输出：字段小写，avg_sales_amount转浮点
            agent_norm = []
            for r in agent_rows:
                pid = r.get("product_id", "").strip()
                pname = r.get("product_name", "").strip()
                try:
                    avg_val = float(r.get("avg_sales_amount", "").strip())
                except:
                    avg_val = None
                agent_norm.append({"product_id": pid, "product_name": pname, "avg_sales_amount": avg_val})
            agent_sorted = sorted(agent_norm, key=lambda x: x["product_id"])
            # 比较长度
            if len(agent_sorted) != len(expected_sorted):
                details.append({"item": "去重正确", "score": 0, "max_score": 20, "passed": False, "reason": f"记录数不匹配，期望{len(expected_sorted)}条，实际{len(agent_sorted)}条"})
            else:
                # 逐条比较
                mismatch = False
                for i in range(len(expected_sorted)):
                    e = expected_sorted[i]
                    a = agent_sorted[i]
                    if a["product_id"] != e["product_id"] or a["product_name"] != e["product_name"]:
                        mismatch = True
                        break
                    # 数值比较允许微小误差
                    if a["avg_sales_amount"] is None or abs(a["avg_sales_amount"] - e["avg_sales_amount"]) > 0.01:
                        mismatch = True
                        break
                if not mismatch:
                    details.append({"item": "去重正确", "score": 20, "max_score": 20, "passed": True, "reason": "去重及平均值计算完全正确"})
                    total_score += 20
                else:
                    details.append({"item": "去重正确", "score": 0, "max_score": 20, "passed": False, "reason": "数据内容与期望不一致"})

    # 5. 检查缺失填充 (20分)
    # 我们在上一步已经隐含检查了product_name，但为了专门评分，验证agent输出中是否包含P002的正确名称"Gadget Y"
    agent_rows = load_csv(csv_path) if 'agent_rows' not in locals() else agent_rows
    if agent_rows is None:
        details.append({"item": "缺失填充正确", "score": 0, "max_score": 20, "passed": False, "reason": "无法读取agent输出"})
    else:
        # 查找P002
        p002_row = None
        for r in agent_rows:
            if r.get("product_id", "").strip() == "P002":
                p002_row = r
                break
        if p002_row is None:
            details.append({"item": "缺失填充正确", "score": 0, "max_score": 20, "passed": False, "reason": "输出中缺少P002记录"})
        elif p002_row.get("product_name", "").strip() == "Gadget Y":
            details.append({"item": "缺失填充正确", "score": 20, "max_score": 20, "passed": True, "reason": "P002产品名填充正确"})
            total_score += 20
        else:
            details.append({"item": "缺失填充正确", "score": 0, "max_score": 20, "passed": False, "reason": f"P002产品名应为'Gadget Y'，实际为'{p002_row.get('product_name','')}'"})

    # 6. 计算平均值精确性 (30分) —— 实际已在去重中包含，但这里单独再验证一个关键点
    # 我们通过对P003的平均值计算来验证
    if agent_rows:
        p003_row = None
        for r in agent_rows:
            if r.get("product_id", "").strip() == "P003":
                p003_row = r
                break
        if p003_row:
            try:
                avg_val = float(p003_row.get("avg_sales_amount", "").strip())
                # 期望平均：(210.00 + 130.25)/2 = 170.125 四舍五入170.13
                expected_avg = round((210.00 + 130.25) / 2, 2)
                if abs(avg_val - expected_avg) < 0.01:
                    details.append({"item": "平均值精确计算", "score": 30, "max_score": 30, "passed": True, "reason": f"P003平均值{avg_val}正确"})
                    total_score += 30
                else:
                    details.append({"item": "平均值精确计算", "score": 0, "max_score": 30, "passed": False, "reason": f"P003期望{expected_avg}，实际{avg_val}"})
            except:
                details.append({"item": "平均值精确计算", "score": 0, "max_score": 30, "passed": False, "reason": "P003的avg_sales_amount格式无效"})
        else:
            details.append({"item": "平均值精确计算", "score": 0, "max_score": 30, "passed": False, "reason": "输出中缺少P003记录"})
    else:
        details.append({"item": "平均值精确计算", "score": 0, "max_score": 30, "passed": False, "reason": "无agent数据"})

    # 写入评分文件
    final_score = min(total_score, 100)
    result = {"total_score": final_score, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
