import sys, os, json

workspace = sys.argv[1] if len(sys.argv) > 1 else "."
score = 0
details = []

def add_detail(item, score_val, max_val, passed, reason):
    details.append({
        "item": item,
        "score": score_val,
        "max_score": max_val,
        "passed": passed,
        "reason": reason
    })
    return score_val

# ---------- 1. 检查文件存在与格式 ----------
target_file = os.path.join(workspace, "ops", "tier_updates.json")
if not os.path.isfile(target_file):
    add_detail("ops/tier_updates.json 存在", 0, 10, False, "文件未找到")
    # 直接结束，后续无法进行
    print(json.dumps({"total_score": 0, "details": details}))
    sys.exit(0)
try:
    with open(target_file) as f:
        updates = json.load(f)
    add_detail("ops/tier_updates.json 合法JSON", 10, 10, True, "JSON解析成功")
except Exception as e:
    add_detail("ops/tier_updates.json 合法JSON", 0, 10, False, f"JSON解析失败: {e}")
    print(json.dumps({"total_score": 0, "details": details}))
    sys.exit(0)

# ---------- 2. 更新数据格式校验 ----------
if not isinstance(updates, list):
    add_detail("结果是一个列表", 0, 10, False, "根元素不是列表")
    print(json.dumps({"total_score": sum(d["score"] for d in details), "details": details}))
    sys.exit(0)

# 检查每个元素字段
fields_ok = True
for idx, entry in enumerate(updates):
    if not isinstance(entry, dict):
        fields_ok = False
        break
    if "customer_id" not in entry or "new_tier" not in entry:
        fields_ok = False
        break
    if len(entry) != 2:
        fields_ok = False
        break
if fields_ok:
    add_detail("每个条目包含且仅包含customer_id和new_tier", 10, 10, True, "字段结构符合要求")
else:
    add_detail("每个条目包含且仅包含customer_id和new_tier", 0, 10, False, "存在多余或缺失字段")

# ---------- 3. 读取原始数据，计算正确结果 ----------
def load_json(filepath):
    with open(filepath) as f:
        return json.load(f)

customers_file = os.path.join(workspace, "data/customers/customers.json")
consumption_file = os.path.join(workspace, "data/logs/consumption_logs.json")
activity_file = os.path.join(workspace, "data/logs/activity_logs.json")

try:
    cust_data = load_json(customers_file)["customers"]
    cons_data = load_json(consumption_file)["consumption_logs"]
    act_data = load_json(activity_file)["activity_logs"]
    add_detail("原始数据文件可读", 5, 5, True, "三个必要文件均存在且格式正确")
except Exception as e:
    add_detail("原始数据文件可读", 0, 5, False, f"读取失败: {e}")
    # 仍可继续只检查格式
    cust_data = []
    cons_data = []
    act_data = []

# 构建映射
cons_map = {x["customer_id"]: x["quarter_spend_usd"] for x in cons_data}
act_map = {x["customer_id"]: x["last_active_days"] for x in act_data}

correct_updates = []
for cust in cust_data:
    cid = cust["customer_id"]
    spend = cons_map.get(cid)
    days = act_map.get(cid)
    if spend is None or days is None:
        # 无数据则保持原等级
        new_tier = cust["tier"]
    else:
        if spend >= 10000 and days <= 30:
            new_tier = "VIP"
        elif spend >= 5000 and days <= 60:
            new_tier = "Premium"
        else:
            new_tier = "Standard"
    correct_updates.append({"customer_id": cid, "new_tier": new_tier})

# ---------- 4. 比对答案 ----------
# 首先按 customer_id 排序方便比较
actual_sorted = sorted(updates, key=lambda x: x["customer_id"])
correct_sorted = sorted(correct_updates, key=lambda x: x["customer_id"])

# 检查条目数量
score_item = 0
max_item = 20
if len(actual_sorted) != len(correct_sorted):
    score_item = add_detail("客户数量正确", 0, max_item, False,
                            f"实际{len(actual_sorted)}个, 正确{len(correct_sorted)}个")
else:
    # 逐个比对
    all_match = True
    for a, c in zip(actual_sorted, correct_sorted):
        if a["customer_id"] != c["customer_id"] or a["new_tier"] != c["new_tier"]:
            all_match = False
            break
    if all_match:
        score_item = add_detail("每条客户记录与正确结果一致", max_item, max_item, True, "全部匹配")
    else:
        # 找出差异
        mismatch = []
        for a in actual_sorted:
            found = next((c for c in correct_sorted if c["customer_id"] == a["customer_id"]), None)
            if found is None:
                mismatch.append(f"多余客户 {a['customer_id']}")
            elif a["new_tier"] != found["new_tier"]:
                mismatch.append(f"客户 {a['customer_id']} 预期 {found['new_tier']} 实际 {a['new_tier']}")
        for c in correct_sorted:
            if not any(a["customer_id"] == c["customer_id"] for a in actual_sorted):
                mismatch.append(f"缺失客户 {c['customer_id']}")
        reason = "; ".join(mismatch) if mismatch else "未知错误"
        score_item = add_detail("每条客户记录与正确结果一致", 0, max_item, False, reason)

# ---------- 5. 额外检查：没有多余字段 ----------
extra_field_penalty = 0
for entry in updates:
    for key in entry:
        if key not in ("customer_id", "new_tier"):
            extra_field_penalty -= 5
            break
if extra_field_penalty < 0:
    add_detail("无多余字段", 0, 0, False, f"发现多余字段，扣分已计入总分")

total_score = sum(d["score"] for d in details)
total_max = 10 + 10 + 10 + 5 + 20  # =55
# 实际上 max_score总和应为55，但我们可以再加一个权重调整让总分上限100
# 这里简单把上面分数按比例放大到100分制
scaled_score = min(100, int(total_score / 55 * 100 + 0.5))
# 为了更细粒度，我们增加一项“所有客户等级正确性”权重，但上面已经覆盖。
# 再补一个综合项“逻辑完全正确”占45分，如果上面完全正确则加45
if total_score == 55:
    add_detail("业务逻辑完全正确", 45, 45, True, "所有客户的等级与规则一致")
    total_score = 100
else:
    # 根据已得分比例给部分分
    logic_score = int(total_score / 55 * 45)
    add_detail("业务逻辑部分正确", logic_score, 45, total_score==55, f"得分比例 {total_score}/55")
    total_score = total_score + logic_score

# 写入结果
result = {
    "total_score": total_score,
    "details": details
}
with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
    json.dump(result, f, indent=2)

print(json.dumps(result))
