import sys
import json
import csv
import os
import math

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0

    # 1. 检查必需文件是否存在
    required_files = ["cleaned_sales.csv", "summary.json"]
    for fname in required_files:
        path = os.path.join(workspace, fname)
        exists = os.path.isfile(path)
        max_s = 10
        if exists:
            score_details.append({"item": f"文件 {fname} 存在", "score": max_s, "max_score": max_s, "passed": True, "reason": "ok"})
            total_score += max_s
        else:
            score_details.append({"item": f"文件 {fname} 存在", "score": 0, "max_score": max_s, "passed": False, "reason": f"未找到 {path}"})

    # 如果文件缺失，后续检查需要跳过，但继续收集分数
    cleaned_path = os.path.join(workspace, "cleaned_sales.csv")
    summary_path = os.path.join(workspace, "summary.json")
    cleaned_ok = os.path.isfile(cleaned_path)
    summary_ok = os.path.isfile(summary_path)

    # 2. 检查表头和基本格式 (10分)
    if cleaned_ok:
        try:
            with open(cleaned_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader)
            expected_header = ["transaction_id","date","product_id","product_name","category","subcategory","region","city","customer_id","customer_name","sales_amount","quantity","discount","payment_method","salesperson_id","salesperson_name","channel"]
            if header == expected_header:
                score_details.append({"item": "CSV 表头正确", "score": 10, "max_score": 10, "passed": True, "reason": "表头完全匹配"})
                total_score += 10
            else:
                score_details.append({"item": "CSV 表头正确", "score": 0, "max_score": 10, "passed": False, "reason": f"表头不一致: 收到 {header}"})
        except Exception as e:
            score_details.append({"item": "CSV 表头正确", "score": 0, "max_score": 10, "passed": False, "reason": f"读取表头失败: {e}"})
    else:
        score_details.append({"item": "CSV 表头正确", "score": 0, "max_score": 10, "passed": False, "reason": "cleaned_sales.csv 缺失"})

    # 3. 去重检查 (15分) - 确保无重复 transaction_id
    if cleaned_ok:
        try:
            with open(cleaned_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                ids = [row["transaction_id"] for row in reader]
            duplicates = [t for t in ids if ids.count(t) > 1]
            if not duplicates:
                score_details.append({"item": "去重：无重复 transaction_id", "score": 15, "max_score": 15, "passed": True, "reason": "所有交易ID唯一"})
                total_score += 15
            else:
                score_details.append({"item": "去重：无重复 transaction_id", "score": 0, "max_score": 15, "passed": False, "reason": f"发现重复ID: {set(duplicates)}"})
        except Exception as e:
            score_details.append({"item": "去重：无重复 transaction_id", "score": 0, "max_score": 15, "passed": False, "reason": f"读取CSV失败: {e}"})
    else:
        score_details.append({"item": "去重：无重复 transaction_id", "score": 0, "max_score": 15, "passed": False, "reason": "cleaned_sales.csv 缺失"})

    # 4. 负数金额检查 (15分) - 确保无负数
    if cleaned_ok:
        try:
            with open(cleaned_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                negatives = [row for row in reader if float(row["sales_amount"]) < 0]
            if not negatives:
                score_details.append({"item": "剔除负数金额", "score": 15, "max_score": 15, "passed": True, "reason": "无负数金额"})
                total_score += 15
            else:
                score_details.append({"item": "剔除负数金额", "score": 0, "max_score": 15, "passed": False, "reason": f"仍有负数行: {negatives}"})
        except Exception as e:
            score_details.append({"item": "剔除负数金额", "score": 0, "max_score": 15, "passed": False, "reason": f"读取CSV失败: {e}"})
    else:
        score_details.append({"item": "剔除负数金额", "score": 0, "max_score": 15, "passed": False, "reason": "cleaned_sales.csv 缺失"})

    # 5. 缺失填充检查 (10分) - salesperson_name 不应为空
    if cleaned_ok:
        try:
            with open(cleaned_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                empties = [row for row in reader if row["salesperson_name"].strip() == ""]
            if not empties:
                score_details.append({"item": "缺失销售人员填充", "score": 10, "max_score": 10, "passed": True, "reason": "无空销售人员姓名"})
                total_score += 10
            else:
                score_details.append({"item": "缺失销售人员填充", "score": 0, "max_score": 10, "passed": False, "reason": f"仍有空销售人员姓名行: {empties}"})
        except Exception as e:
            score_details.append({"item": "缺失销售人员填充", "score": 0, "max_score": 10, "passed": False, "reason": f"读取CSV失败: {e}"})
    else:
        score_details.append({"item": "缺失销售人员填充", "score": 0, "max_score": 10, "passed": False, "reason": "cleaned_sales.csv 缺失"})

    # 6. 行数正确性 (10分) 和 聚合值 (30分)
    # 先计算期望：基于原始数据逻辑
    # 原始数据有13行（包括表头？不，表头不计）。实际记录：raw_rows 有11行（见env_builder）? 仔细数：raw_rows列表的元素个数：从正常记录到T010共12行？我们重新数：T001,T002,T001重复,T003,T003重复,T004,T004重复,T005,T006,T007,T008,T009,T010 => 13行？注意列表里写了12条？实际上我写了13个元素？检查：从#正常记录开始：T001,T002,T001重复(3), T003(4),T003重复(5),T004(6),T004重复(7),T005(8),T006(9),T007(10),T008(11),T009(12),T010(13)。共13行。其中：
    #   - 完全重复：T001出现2行，保留1行 → 去掉1行
    #   - 重复按日期留最新：T003最新是2024-01-03；T004最新是2024-01-05 → 各去掉1行，共2行
    #   - 负数金额：T005(-20), T009(-5) → 去掉2行
    #   - 空销售员：T006,S006空；T008,S008空；另外T009销售员也空但已被负数去掉。所以填充不影响行数。
    # 去重+负数去重后保留的行数 = 13 - 1(完全重复) - 2(T003旧) - 2(T004旧) - 2(负数) = 6行？等等计算：13 - (1+2+2+2) = 13-7=6行。剩余：T002正常，T003最新，T004最新，T006（空但已填充），T007，T008（空填充），T010。共7行？T006、T007、T008、T010加上前面三个，共7？让我们列出所有原始行并标记保留：
    # 1 T001 2024-01-01 (重复) -> 保留？这个是最早的？T001有两个相同日期？它们完全一样，所以保留任意一条（但日期一样，所以去重保留第一条）。我们设计完全重复的两个T001日期相同，所以保留其中一个即可。我们按保留第一个。
    # 2 T002 正常 -> 保留
    # 3 T001 完全重复 -> 去掉
    # 4 T003 2024-01-02 -> 去掉（因为T003最新是2024-01-03）
    # 5 T003 2024-01-03 -> 保留
    # 6 T004 2024-01-04 -> 去掉
    # 7 T004 2024-01-05 -> 保留
    # 8 T005 -20 -> 去掉
    # 9 T006 空销售员 -> 保留（需填充）
    # 10 T007 正常 -> 保留
    # 11 T008 空销售员 -> 保留
    # 12 T009 -5 -> 去掉
    # 13 T010 正常 -> 保留
    # 保留：1(T001), 2(T002), 5(T003), 7(T004), 9(T006), 10(T007), 11(T008), 13(T010) => 8行。
    # 检查：1 T001 保留，2 T002 保留，5 T003 保留，7 T004 保留，9 T006 保留，10 T007 保留，11 T008 保留，13 T010 保留。共8行。
    # 总销售额 = 100(T001) + 200(T002) + 60(T003) + 180(T004) + 300(T006) + 45(T007) + 250(T008) + 120(T010) = 100+200=300; 300+60=360; 360+180=540; 540+300=840; 840+45=885; 885+250=1135; 1135+120=1255。
    # 平均订单 = 1255 / 8 = 156.875
    expected_count = 8
    expected_revenue = 1255.0
    expected_average = expected_revenue / expected_count  # 156.875

    # 检查行数
    if cleaned_ok:
        try:
            with open(cleaned_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            actual_count = len(rows)
            if actual_count == expected_count:
                score_details.append({"item": "清洗后行数正确", "score": 10, "max_score": 10, "passed": True, "reason": f"行数={actual_count}"})
                total_score += 10
            else:
                score_details.append({"item": "清洗后行数正确", "score": 0, "max_score": 10, "passed": False, "reason": f"期望{expected_count}行，实际{actual_count}行"})
        except Exception as e:
            score_details.append({"item": "清洗后行数正确", "score": 0, "max_score": 10, "passed": False, "reason": f"读取CSV失败: {e}"})
    else:
        score_details.append({"item": "清洗后行数正确", "score": 0, "max_score": 10, "passed": False, "reason": "cleaned_sales.csv 缺失"})

    # 检查 summary.json 三个字段 (各10分)
    if summary_ok:
        try:
            with open(summary_path, "r", encoding="utf-8") as f:
                summary = json.load(f)
            # total_records
            if summary.get("total_records") == expected_count:
                score_details.append({"item": "summary.total_records 正确", "score": 10, "max_score": 10, "passed": True, "reason": f"值为{expected_count}"})
                total_score += 10
            else:
                score_details.append({"item": "summary.total_records 正确", "score": 0, "max_score": 10, "passed": False, "reason": f"期望{expected_count}，收到{summary.get('total_records')}"})
            # total_revenue
            actual_rev = summary.get("total_revenue")
            if isinstance(actual_rev, (int, float)) and math.isclose(actual_rev, expected_revenue, rel_tol=1e-9):
                score_details.append({"item": "summary.total_revenue 正确", "score": 10, "max_score": 10, "passed": True, "reason": f"值为{actual_rev}"})
                total_score += 10
            else:
                score_details.append({"item": "summary.total_revenue 正确", "score": 0, "max_score": 10, "passed": False, "reason": f"期望{expected_revenue}，收到{actual_rev}"})
            # average_order
            actual_avg = summary.get("average_order")
            if isinstance(actual_avg, (int, float)) and math.isclose(actual_avg, expected_average, rel_tol=1e-9):
                score_details.append({"item": "summary.average_order 正确", "score": 10, "max_score": 10, "passed": True, "reason": f"值为{actual_avg}"})
                total_score += 10
            else:
                score_details.append({"item": "summary.average_order 正确", "score": 0, "max_score": 10, "passed": False, "reason": f"期望{expected_average}，收到{actual_avg}"})
        except Exception as e:
            score_details.append({"item": "summary.json 解析或字段检查", "score": 0, "max_score": 30, "passed": False, "reason": f"错误: {e}"})
    else:
        score_details.append({"item": "summary.json 存在", "score": 0, "max_score": 30, "passed": False, "reason": "summary.json 缺失"})

    # 输出结果
    result = {"total_score": min(total_score, 100), "details": score_details}
    out_path = os.path.join(workspace, "workplace_score.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
