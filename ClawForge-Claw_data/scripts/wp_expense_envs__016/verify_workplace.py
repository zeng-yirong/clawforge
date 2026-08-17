import sys
import json
import os
import glob
from collections import defaultdict

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

def read_json(filepath):
    if not os.path.exists(filepath):
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

score_details = []
total_score = 0
max_total = 100

# 1. 检查报告文件是否存在 (10分)
report_path = os.path.join(workspace, "ops/analysis_report.json")
if os.path.exists(report_path):
    score_details.append({"item": "报告文件存在", "score": 10, "max_score": 10, "passed": True, "reason": "ops/analysis_report.json 存在"})
    total_score += 10
else:
    score_details.append({"item": "报告文件存在", "score": 0, "max_score": 10, "passed": False, "reason": "ops/analysis_report.json 不存在"})
    # 后续检查全部跳过
    score_details.append({"item": "报告内容有效", "score": 0, "max_score": 10, "passed": False, "reason": "文件缺失"})
    score_details.append({"item": "关键字段完整", "score": 0, "max_score": 20, "passed": False, "reason": "文件缺失"})
    score_details.append({"item": "预算计算正确", "score": 0, "max_score": 30, "passed": False, "reason": "文件缺失"})
    score_details.append({"item": "超支项判断正确", "score": 0, "max_score": 20, "passed": False, "reason": "文件缺失"})
    score_details.append({"item": "数值精度准确", "score": 0, "max_score": 10, "passed": False, "reason": "文件缺失"})
    # 写入结果并退出
    result = {"total_score": total_score, "details": score_details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    sys.exit(0)

# 2. 解析报告并验证JSON格式 (10分)
try:
    report = read_json(report_path)
    if report is None:
        raise ValueError("无法读取")
    if not isinstance(report, dict):
        raise ValueError("不是JSON对象")
    score_details.append({"item": "报告内容有效", "score": 10, "max_score": 10, "passed": True, "reason": "JSON格式正确且为字典"})
    total_score += 10
except Exception as e:
    score_details.append({"item": "报告内容有效", "score": 0, "max_score": 10, "passed": False, "reason": str(e)})
    # 继续检查后续，但很多字段可能缺失，先给0分后续再判断
    report = {}

# 3. 检查关键字段 (20分)
required_fields = ["employee_name", "tier", "destination", "duration_days", "total_budget", "total_actual", "over_budget_items"]
missing_fields = [f for f in required_fields if f not in report]
if not missing_fields:
    score_details.append({"item": "关键字段完整", "score": 20, "max_score": 20, "passed": True, "reason": f"包含全部{len(required_fields)}个要求字段"})
    total_score += 20
else:
    score_details.append({"item": "关键字段完整", "score": 0, "max_score": 20, "passed": False, "reason": f"缺少字段: {missing_fields}"})

# 4. 验证预算计算（基于政策、天数） (30分)
# 从原始文件加载政策
trip_info_path = os.path.join(workspace, "ops/trip_info.json")
trip_info = read_json(trip_info_path)
policy_path = os.path.join(workspace, "data/travel_policies.json")
policies = read_json(policy_path)

budget_correct = False
budget_reason = ""
budget_score = 0

try:
    if trip_info and policies:
        tier = trip_info.get("tier", "")
        days = trip_info.get("duration_days", 0)
        dest = trip_info.get("destination", "")
        employee_name = trip_info.get("employee_name", "")
        policy = policies.get(tier)
        if policy:
            # 计算各分类预算
            budget_per_category = {}
            for cat, info in policy.items():
                daily = info.get("daily_budget", 0)
                budget_per_category[cat] = round(daily * days, 2)
            total_budget = round(sum(budget_per_category.values()), 2)

            # 从报告中提取数据
            report_total_budget = report.get("total_budget")
            report_total_actual = report.get("total_actual")
            report_over_items = report.get("over_budget_items", [])

            # 从消费记录中计算小张的实际消费（需要去重？没有重复记录，直接累加，排除脏数据）
            records_path = os.path.join(workspace, "data/consumption_records.json")
            all_records = read_json(records_path)
            actual_by_category = defaultdict(float)
            if all_records:
                emp_id = trip_info.get("employee_id")
                for r in all_records:
                    if not isinstance(r, dict):
                        continue
                    if r.get("employee_id") != emp_id:
                        continue
                    cat = r.get("category")
                    if not cat or cat == "":
                        continue
                    amount = r.get("amount")
                    if amount is None:
                        continue
                    try:
                        actual_by_category[cat] += float(amount)
                    except:
                        pass
            total_actual = round(sum(actual_by_category.values()), 2)

            # 检查总预算是否一致
            if abs(report_total_budget - total_budget) < 0.01:
                budget_correct = True
                budget_reason = f"总预算正确: {total_budget}"
                budget_score = 15
            else:
                budget_reason = f"总预算不一致: 报告={report_total_budget}, 期望={total_budget}"
                budget_score = 0

            # 检查总实际消费是否一致
            if abs(report_total_actual - total_actual) < 0.01:
                budget_score += 15
                budget_reason += f" 总实际正确: {total_actual}"
            else:
                budget_reason += f" 总实际不一致: 报告={report_total_actual}, 期望={total_actual}"
                budget_score += 0

            # 实际预算计算部分已经检查了总预算和总实际，共30分，各15分
            # 但还需要检查over_budget_items中的各分类预算和实际是否匹配，在下一部分

            # 暂时记录得分
            score_details.append({"item": "预算计算正确", "score": budget_score, "max_score": 30, "passed": (budget_score == 30), "reason": budget_reason})
            total_score += budget_score

            # 5. 检查超支项 (20分)
            over_check_score = 0
            over_reason = ""
            # 计算哪些分类实际超过预算
            over_categories = {}
            for cat, actual in actual_by_category.items():
                budget = budget_per_category.get(cat, 0)
                if actual > budget:
                    over_categories[cat] = {"category": cat, "budget": budget, "actual": actual, "over_amount": round(actual - budget, 2)}
            # 检查报告中的over_budget_items
            if isinstance(report_over_items, list):
                report_over_set = set()
                for item in report_over_items:
                    if isinstance(item, dict) and item.get("category") and item.get("budget") is not None and item.get("actual") is not None:
                        report_over_set.add(item["category"])
                expected_over_set = set(over_categories.keys())
                if report_over_set == expected_over_set:
                    # 再比较每个超支项的数值
                    all_match = True
                    for item in report_over_items:
                        cat = item.get("category")
                        expected = over_categories.get(cat)
                        if expected is None:
                            all_match = False
                            break
                        if abs(item.get("budget",0) - expected["budget"]) > 0.01 or \
                           abs(item.get("actual",0) - expected["actual"]) > 0.01 or \
                           abs(item.get("over_amount",0) - expected["over_amount"]) > 0.01:
                            all_match = False
                            break
                    if all_match:
                        over_check_score = 20
                        over_reason = f"超支项集合与数值完全正确: {expected_over_set}"
                    else:
                        over_reason = "超支项数值不匹配"
                        over_check_score = 10
                else:
                    over_reason = f"超支项集合不匹配: 报告有{report_over_set}, 期望{expected_over_set}"
                    over_check_score = 5
            else:
                over_reason = "over_budget_items不是列表或格式错误"
                over_check_score = 0

            score_details.append({"item": "超支项判断正确", "score": over_check_score, "max_score": 20, "passed": (over_check_score >= 18), "reason": over_reason})
            total_score += over_check_score

        else:
            score_details.append({"item": "预算计算正确", "score": 0, "max_score": 30, "passed": False, "reason": "找不到对应职等的政策"})
            score_details.append({"item": "超支项判断正确", "score": 0, "max_score": 20, "passed": False, "reason": "依赖预算计算"})
    else:
        score_details.append({"item": "预算计算正确", "score": 0, "max_score": 30, "passed": False, "reason": "无法读取trip_info或policies"})
        score_details.append({"item": "超支项判断正确", "score": 0, "max_score": 20, "passed": False, "reason": "依赖预算计算"})
except Exception as e:
    score_details.append({"item": "预算计算正确", "score": 0, "max_score": 30, "passed": False, "reason": f"异常: {e}"})
    score_details.append({"item": "超支项判断正确", "score": 0, "max_score": 20, "passed": False, "reason": f"异常: {e}"})

# 6. 数值精度（所有金额保留两位小数） (10分)
precision_score = 10
precision_reason = ""
try:
    def check_precision(val, path_str):
        if isinstance(val, float):
            s = f"{val:.2f}"
            if float(s) != val:
                return False
        return True
    all_precise = True
    for key in ["total_budget", "total_actual"]:
        if key in report:
            if not check_precision(report[key], key):
                all_precise = False
                break
    if "over_budget_items" in report and isinstance(report["over_budget_items"], list):
        for item in report["over_budget_items"]:
            for subkey in ["budget", "actual", "over_amount"]:
                if subkey in item:
                    if not check_precision(item[subkey], f"over_budget_items.{subkey}"):
                        all_precise = False
                        break
            if not all_precise:
                break
    if all_precise:
        precision_score = 10
        precision_reason = "所有金额保留两位小数"
    else:
        precision_score = 0
        precision_reason = "存在未保留两位小数的金额"
except Exception as e:
    precision_score = 0
    precision_reason = f"精度检查出错: {e}"
score_details.append({"item": "数值精度准确", "score": precision_score, "max_score": 10, "passed": (precision_score == 10), "reason": precision_reason})
total_score += precision_score

# 最终总分
final_score = min(total_score, 100)
result = {"total_score": final_score, "details": score_details}
with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)
