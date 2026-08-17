import sys
import os
import csv
import json
from decimal import Decimal, ROUND_HALF_UP

workspace = sys.argv[1] if len(sys.argv) > 1 else "."
score_details = []
total_score = 0

def add_score(item, score, max_score, passed, reason):
    global total_score
    score_details.append({
        "item": item,
        "score": score,
        "max_score": max_score,
        "passed": passed,
        "reason": reason
    })
    total_score += score

# 1. 检查 report 目录是否存在
report_dir = os.path.join(workspace, "report")
if os.path.isdir(report_dir):
    add_score("报告目录存在", 5, 5, True, "report/ 目录已创建")
else:
    add_score("报告目录存在", 0, 5, False, "report/ 目录缺失")
    # 如果目录不存在，后续无法继续
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
    sys.exit(0)

# 2. 检查结果文件是否存在
result_path = os.path.join(report_dir, "region_summary.csv")
if not os.path.isfile(result_path):
    add_score("结果文件存在", 0, 10, False, "report/region_summary.csv 未生成")
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
    sys.exit(0)
else:
    add_score("结果文件存在", 10, 10, True, "report/region_summary.csv 存在")

# 3. 读取结果文件并检查格式
try:
    with open(result_path, "r") as f:
        reader = csv.reader(f)
        rows = list(reader)
    if len(rows) < 2:
        add_score("结果文件至少包含表头+1行数据", 0, 5, False, "文件为空或仅有表头")
        # 继续检查表头
    else:
        add_score("结果文件至少包含表头+1行数据", 5, 5, True, "行数充足")
except Exception as e:
    add_score("结果文件可解析为CSV", 0, 5, False, f"解析失败: {e}")
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
    sys.exit(0)

# 4. 检查表头
if len(rows[0]) != 2:
    add_score("表头包含两列", 0, 5, False, f"实际列数: {len(rows[0])}")
else:
    header = [h.strip().lower() for h in rows[0]]
    if header == ["region", "net_sales"]:
        add_score("表头列名正确 (region, net_sales)", 5, 5, True, "符合要求")
    else:
        add_score("表头列名正确 (region, net_sales)", 0, 5, False, f"实际表头: {rows[0]}")

# 5. 读取原始数据并计算预期结果（清洗规则同 prompt）
def clean_and_compute(workspace):
    """读取 data/sales_raw.csv，按规则清洗并计算净销售额，返回 {region: net_sales}"""
    raw_path = os.path.join(workspace, "data", "sales_raw.csv")
    if not os.path.isfile(raw_path):
        return None
    valid_rows = []
    with open(raw_path, "r") as f:
        reader = csv.DictReader(f)
        seen = set()
        for row in reader:
            # 构建唯一标识（所有字段组合）
            record = tuple(row.values())
            if record in seen:
                continue  # 完全重复跳过
            seen.add(record)

            region = (row.get("region") or "").strip()
            if not region:
                continue  # 缺失 region

            try:
                amount = Decimal(row["sales_amount"])
                qty = int(row["quantity"])
                discount = int(row["discount"])
            except (KeyError, ValueError, TypeError):
                continue  # 数字字段异常

            if amount <= 0 or qty <= 0:
                continue  # 非正数值

            net = amount * qty * (1 - Decimal(discount) / 100)
            net = net.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            valid_rows.append((region, net))

    # 按地区汇总
    region_net = {}
    for region, net in valid_rows:
        region_net[region] = region_net.get(region, Decimal("0")) + net
    # 对每个地区保留两位小数
    for region in region_net:
        region_net[region] = region_net[region].quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return region_net

expected = clean_and_compute(workspace)
if expected is None:
    add_score("原始数据文件可读取", 0, 10, False, "data/sales_raw.csv 不存在或无法解析")
else:
    add_score("原始数据文件可读取", 10, 10, True, "成功读取")

# 6. 比较实际结果与预期
if expected:
    # 提取实际数据（跳过表头）
    actual = {}
    for row in rows[1:]:
        if len(row) != 2:
            continue
        region_key = row[0].strip()
        try:
            value = Decimal(row[1])
        except:
            value = None
        if value is not None:
            actual[region_key] = value

    # 检查地区集合是否一致
    expected_regions = set(expected.keys())
    actual_regions = set(actual.keys())
    if expected_regions != actual_regions:
        missing = expected_regions - actual_regions
        extra = actual_regions - expected_regions
        reason = ""
        if missing:
            reason += f"缺失地区: {missing}; "
        if extra:
            reason += f"多余地区: {extra}"
        add_score("地区集合完全一致", 0, 20, False, reason)
    else:
        add_score("地区集合完全一致", 20, 20, True, "所有必要地区都包含，无多余地区")

    # 检查每个地区的净销售额
    if expected_regions == actual_regions:
        all_correct = True
        for region in expected_regions:
            exp_val = expected[region]
            act_val = actual.get(region)
            if act_val is None or act_val != exp_val:
                all_correct = False
                add_score(f"地区 {region} 净销售额正确", 0, 10, False,
                          f"期望 {exp_val}, 实际 {act_val}")
                break
        if all_correct:
            add_score("所有地区净销售额正确", 30, 30, True, "每个地区数值均匹配")
    else:
        # 地区不一致时，对存在的地区逐个检查（最多给部分分数）
        matched_count = 0
        for region in expected_regions & actual_regions:
            if expected[region] == actual[region]:
                matched_count += 1
        if matched_count > 0:
            add_score(f"部分匹配地区（{matched_count}个）", matched_count * 5, 20, True,
                      f"正确地区数值个数: {matched_count}")
        else:
            add_score("至少有一个地区数值正确", 0, 10, False, "无任何地区数值匹配")

# 7. 额外检查：结果文件中是否有多余的行（例如空行）
if rows:
    non_empty_data_rows = [r for r in rows[1:] if any(field.strip() for field in r)]
    pass

# 写入评分文件
with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
    json.dump({"total_score": total_score, "details": score_details}, f, indent=2)

# 打印结果（可选）
print(f"Total score: {total_score}/100")
