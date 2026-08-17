import sys
import os
import csv
import json
import math
from collections import defaultdict

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

score_details = []
def add_detail(item, score, max_score, passed, reason):
    score_details.append({
        "item": item,
        "score": score,
        "max_score": max_score,
        "passed": passed,
        "reason": reason
    })

# 1. 检查 output 目录是否存在 (10分)
output_dir = os.path.join(workspace, "output")
if os.path.isdir(output_dir):
    add_detail("output目录存在", 10, 10, True, "output目录已创建")
else:
    add_detail("output目录存在", 0, 10, False, "output目录未找到")

# 2. 检查 output/monthly_revenue.json 是否存在 (10分)
target_file = os.path.join(output_dir, "monthly_revenue.json")
if os.path.isfile(target_file):
    add_detail("monthly_revenue.json存在", 10, 10, True, "文件存在")
else:
    add_detail("monthly_revenue.json存在", 0, 10, False, "文件未找到")
    # 如果文件不存在，后续检查无法进行，但继续给出0分
    add_detail("JSON格式合法", 0, 10, False, "文件不存在")
    add_detail("月份键正确", 0, 10, False, "文件不存在")
    add_detail("各月份金额正确", 0, 50, False, "文件不存在")
    add_detail("无多余键", 0, 10, False, "文件不存在")
    total = sum(d["score"] for d in score_details)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total, "details": score_details}, f, indent=2)
    sys.exit(0)

# 3. 检查 JSON 格式是否合法 (10分)
try:
    with open(target_file, "r") as f:
        agent_data = json.load(f)
    add_detail("JSON格式合法", 10, 10, True, "JSON解析成功")
except Exception as e:
    add_detail("JSON格式合法", 0, 10, False, f"解析失败: {str(e)}")
    total = sum(d["score"] for d in score_details)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total, "details": score_details}, f, indent=2)
    sys.exit(0)

# 4. 根据原始数据计算标准答案
def parse_discount(val):
    """将折扣字段转为整数百分比，空或非数字视为0"""
    if val is None or val.strip() == "":
        return 0
    try:
        return int(val.strip())
    except ValueError:
        return 0

def compute_expected():
    csv_path = os.path.join(workspace, "data/sales_data.csv")
    if not os.path.isfile(csv_path):
        return None, "原始数据文件 data/sales_data.csv 不存在"
    seen = set()
    monthly = defaultdict(float)
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 去重：transaction_id + date + product + category + quantity + sales_amount + discount
            key = (row["transaction_id"], row["date"], row["product"], row["category"],
                   row["quantity"], row["sales_amount"], row.get("discount", ""))
            if key in seen:
                continue
            seen.add(key)
            qty = float(row["quantity"])
            amt = float(row["sales_amount"])
            dsc = parse_discount(row.get("discount", ""))
            revenue = amt * qty * (1 - dsc / 100.0)
            month = row["date"][:7]  # YYYY-MM
            monthly[month] += revenue
    # 四舍五入到两位小数
    expected = {k: round(v, 2) for k, v in monthly.items()}
    return expected, None

expected, err = compute_expected()
if err:
    add_detail("原始数据读取", 0, 0, False, err)  # 不占分，但记录问题
    total = sum(d["score"] for d in score_details)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total, "details": score_details}, f, indent=2)
    sys.exit(0)

# 5. 检查月份键是否正确 (10分)
agent_months = set(agent_data.keys())
expected_months = set(expected.keys())
if agent_months == expected_months:
    add_detail("月份键正确", 10, 10, True, f"键集合完全匹配: {sorted(expected_months)}")
else:
    missing = expected_months - agent_months
    extra = agent_months - expected_months
    msg_parts = []
    if missing:
        msg_parts.append(f"缺少月份: {sorted(missing)}")
    if extra:
        msg_parts.append(f"多余月份: {sorted(extra)}")
    add_detail("月份键正确", 0, 10, False, "; ".join(msg_parts))

# 6. 检查各月份金额是否在允许误差内 (50分)
amount_ok = True
for month in expected_months:
    expected_val = expected[month]
    agent_val = agent_data.get(month)
    if agent_val is None:
        amount_ok = False
        continue
    if not isinstance(agent_val, (int, float)):
        amount_ok = False
        continue
    if abs(agent_val - expected_val) > 0.01:
        amount_ok = False
if amount_ok:
    add_detail("各月份金额正确", 50, 50, True, "所有月份金额误差均在0.01以内")
else:
    # 给出部分分（每个月份大约 50 / len(expected)）
    month_scores = 0
    for month in expected_months:
        expected_val = expected[month]
        agent_val = agent_data.get(month)
        if agent_val is None or not isinstance(agent_val, (int, float)):
            continue
        if abs(agent_val - expected_val) <= 0.01:
            month_scores += 50 / len(expected_months)
    add_detail("各月份金额正确", round(month_scores), 50, False,
               f"正确月份数: {int(round(month_scores/(50/len(expected_months))))} / {len(expected_months)}")

# 7. 检查无多余键 (10分)
extra_keys = [k for k in agent_data if k not in expected]
if not extra_keys:
    add_detail("无多余键", 10, 10, True, "没有出现预期之外的月份键")
else:
    add_detail("无多余键", 0, 10, False, f"存在多余键: {extra_keys}")

# 汇总分数
total_score = sum(d["score"] for d in score_details)
with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
    json.dump({"total_score": total_score, "details": score_details}, f, indent=2)

print(f"验证完成，总分: {total_score}")
