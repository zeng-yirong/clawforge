import sys, os, json, math

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

score_details = []
total_score = 0
max_possible = 100

def add_detail(item, score, max_score, passed, reason):
    global total_score
    score_details.append({
        "item": item,
        "score": score,
        "max_score": max_score,
        "passed": passed,
        "reason": reason
    })
    total_score += score

# --- 1. 目录结构检查 (5分) ---
ops_dir = os.path.join(workspace, "ops")
if os.path.isdir(ops_dir):
    add_detail("ops/ 目录存在", 5, 5, True, "ops 目录已创建")
else:
    add_detail("ops/ 目录存在", 0, 5, False, "缺少 ops/ 目录")
    total_score = 0
    # 如果目录都不存在，后续无法进行，直接结束
    result = {"total_score": total_score, "details": score_details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    sys.exit(0)

# --- 2. 报告文件存在 (10分) ---
report_path = os.path.join(ops_dir, "report.json")
if os.path.isfile(report_path):
    add_detail("ops/report.json 存在", 10, 10, True, "报告文件已生成")
else:
    add_detail("ops/report.json 存在", 0, 10, False, "未找到 ops/report.json")
    result = {"total_score": total_score, "details": score_details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    sys.exit(0)

# --- 3. 格式合法 (10分) ---
try:
    with open(report_path, "r", encoding="utf-8") as f:
        report = json.load(f)
    trip_id = report.get("trip_id")
    items = report.get("overspend_items", [])
    if not isinstance(items, list):
        raise ValueError("overspend_items 不是列表")
    add_detail("JSON 格式与结构正确", 10, 10, True, "解析成功，包含 trip_id 和 overspend_items 列表")
except Exception as e:
    add_detail("JSON 格式与结构正确", 0, 10, False, f"解析失败: {str(e)}")
    result = {"total_score": total_score, "details": score_details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    sys.exit(0)

# --- 4. trip_id 正确 (5分) ---
if trip_id == "TRIP-018":
    add_detail("trip_id 正确", 5, 5, True, "trip_id = TRIP-018")
else:
    add_detail("trip_id 正确", 0, 5, False, f"期望 TRIP-018，实际 {trip_id}")

# --- 5. 超支条目数量 (20分) ---
expected_categories = ["住宿", "餐饮"]  # 仅这两个超支
if len(items) == 2:
    add_detail("超支条目数量为2", 20, 20, True, f"共有 {len(items)} 个超支条目")
else:
    add_detail("超支条目数量为2", 0, 20, False, f"期望2个，实际 {len(items)} 个")

# --- 6. 每个条目结构和数值正确 (50分, 每个类别25分) ---
# 预期数值 (根据 env_builder 计算):
# 住宿: budget_total = 500 * 3 = 1500, actual_total = 800+800 = 1600, overspend = 100
# 餐饮: budget_total = 200 * 3 = 600, actual_total = 250+250+250 = 750, overspend = 150
expected = {
    "住宿": {"budget_total": 1500.0, "actual_total": 1600.0, "overspend": 100.0},
    "餐饮": {"budget_total": 600.0, "actual_total": 750.0, "overspend": 150.0}
}

def check_item(item_dict, exp):
    errors = []
    cat = item_dict.get("category")
    # 检查字段存在
    for field in ["category", "actual_total", "budget_total", "overspend"]:
        if field not in item_dict:
            errors.append(f"缺少字段 {field}")
            return False, errors
    # 数值类型
    for field in ["actual_total", "budget_total", "overspend"]:
        if not isinstance(item_dict[field], (int, float)):
            errors.append(f"{field} 不是数字")
            return False, errors
    # 比对
    for field in ["budget_total", "actual_total", "overspend"]:
        expected_val = exp[field]
        actual_val = item_dict[field]
        if not math.isclose(actual_val, expected_val, abs_tol=0.01):
            errors.append(f"{field} 期望 {expected_val}，实际 {actual_val}")
            return False, errors
    return True, errors

for cat_name, exp in expected.items():
    matched_item = next((it for it in items if it.get("category") == cat_name), None)
    if matched_item is None:
        add_detail(f"类别 '{cat_name}' 存在且数值正确", 0, 25, False, f"缺少 '{cat_name}' 条目")
        continue
    ok, errs = check_item(matched_item, exp)
    if ok:
        add_detail(f"类别 '{cat_name}' 存在且数值正确", 25, 25, True, f"所有字段匹配")
    else:
        add_detail(f"类别 '{cat_name}' 存在且数值正确", 0, 25, False, "; ".join(errs))

# 检查是否有多余超支条目 (例如不应该有 taxi, flight 等) - 额外扣分可集成在数量评分中，但这里为精确再加一条
extras = [it for it in items if it.get("category") not in expected]
if extras:
    # 从总分中扣减，但细节里记录
    extra_names = [it.get("category") for it in extras]
    add_detail("无多余超支条目", 0, 0, False, f"发现了不应有的超支类别: {extra_names}")
else:
    add_detail("无多余超支条目", 0, 0, True, "没有多余超支条目")

# 总分限制不超过100
total_score = min(total_score, 100)

# 写入结果
result = {
    "total_score": total_score,
    "details": score_details
}
with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print(f"总得分: {total_score}/100")
