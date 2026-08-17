import json
import csv
import os
import sys
import math

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

score_details = []
total_score = 0

def add_score(item, score, max_score, passed, reason):
    score_details.append({
        "item": item,
        "score": score,
        "max_score": max_score,
        "passed": passed,
        "reason": reason
    })
    return score

# ===== 1. Check that ops/diff_report.json exists =====
report_path = os.path.join(workspace, "ops", "diff_report.json")
if os.path.isfile(report_path):
    total_score += add_score("ops/diff_report.json 存在", 10, 10, True, "文件存在")
else:
    total_score += add_score("ops/diff_report.json 存在", 0, 10, False, "文件不存在")
    # cannot proceed
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f)
    sys.exit(0)

# ===== 2. Check JSON validity =====
try:
    with open(report_path, "r") as f:
        report = json.load(f)
    total_score += add_score("JSON 格式合法", 10, 10, True, "JSON 解析成功")
except Exception as e:
    total_score += add_score("JSON 格式合法", 0, 10, False, f"JSON 解析失败: {str(e)}")
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f)
    sys.exit(0)

# ===== 3. Check required fields =====
required_fields = ["batch_a_id", "batch_b_id", "groups", "best_group"]
missing = [f for f in required_fields if f not in report]
if not missing:
    total_score += add_score("报告包含所有必需字段", 20, 20, True, f"字段齐备: {required_fields}")
else:
    total_score += add_score("报告包含所有必需字段", 0, 20, False, f"缺少字段: {missing}")
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f)
    sys.exit(0)

# ===== 4. Parse CSV and compute expected results =====
csv_path = os.path.join(workspace, "experiments", "batch_results.csv")
valid_rows = []
try:
    with open(csv_path, "r") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header is None:
            raise ValueError("Empty CSV")
        for row in reader:
            # skip rows that are not exactly 5 columns
            if len(row) != 5:
                continue
            # skip rows where any numeric field is not a number
            try:
                batch_id = row[0].strip()
                group_id = row[1].strip()
                accuracy = float(row[2])
                latency = float(row[3])
                cost = float(row[4])
            except (ValueError, IndexError):
                continue
            valid_rows.append((batch_id, group_id, accuracy, latency, cost))
except Exception as e:
    total_score += add_score("读取 CSV 数据", 0, 30, False, f"CSV 读取失败: {str(e)}")
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f)
    sys.exit(0)

# Filter required batches
batch_a = "batch_20250301"
batch_b = "batch_20250315"

def get_batch_data(batch_id):
    data = {}
    for bid, gid, acc, lat, cost in valid_rows:
        if bid == batch_id:
            data[gid] = {"accuracy": acc, "latency_ms": lat, "cost_usd": cost}
    return data

data_a = get_batch_data(batch_a)
data_b = get_batch_data(batch_b)

# Check all three groups exist in both batches
expected_groups = ["control", "variant_a", "variant_b"]
expected_diffs = {}
best_group = None
best_acc_improve = -float("inf")

for g in expected_groups:
    if g not in data_a or g not in data_b:
        add_score("各组数据完整性", 0, 0, False, f"组 {g} 在源数据中不完整")
        # continue but note
    else:
        acc_diff = data_b[g]["accuracy"] - data_a[g]["accuracy"]
        lat_diff = data_b[g]["latency_ms"] - data_a[g]["latency_ms"]
        cost_diff = data_b[g]["cost_usd"] - data_a[g]["cost_usd"]
        # latency increase percentage relative to original
        lat_orig = data_a[g]["latency_ms"]
        lat_change_pct = lat_diff / lat_orig  # can be negative
        # condition: latency not increase more than 10% of original
        if lat_change_pct <= 0.10:
            if acc_diff > best_acc_improve:
                best_acc_improve = acc_diff
                best_group = g

# Use math.isclose for floating comparison
def close_enough(a, b):
    return math.isclose(a, b, rel_tol=1e-5)

# ===== 4. Validate groups array =====
groups_from_report = report.get("groups", [])
if not isinstance(groups_from_report, list):
    total_score += add_score("groups 为数组", 0, 30, False, "groups 不是数组")
    # skip rest
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f)
    sys.exit(0)

# Build expected groups dict
expected_group_map = {}
for g in expected_groups:
    if g in data_a and g in data_b:
        acc_diff = data_b[g]["accuracy"] - data_a[g]["accuracy"]
        lat_diff = data_b[g]["latency_ms"] - data_a[g]["latency_ms"]
        cost_diff = data_b[g]["cost_usd"] - data_a[g]["cost_usd"]
        expected_group_map[g] = {
            "accuracy_diff": round(acc_diff, 4),
            "latency_diff": round(lat_diff, 4),
            "cost_diff": round(cost_diff, 4)
        }

group_ok = True
for g in expected_groups:
    found = None
    for entry in groups_from_report:
        if entry.get("group_id") == g:
            found = entry
            break
    if found is None:
        add_score(f"groups 中包含组 {g}", 0, 30, False, f"缺失组 {g}")
        group_ok = False
        continue
    # check numeric fields with rounding
    expected = expected_group_map[g]
    for key in ["accuracy_diff", "latency_diff", "cost_diff"]:
        if key not in found:
            add_score(f"组 {g} 的 {key} 字段", 0, 30, False, f"缺失字段 {key}")
            group_ok = False
        else:
            val = found[key]
            if not isinstance(val, (int, float)):
                add_score(f"组 {g} 的 {key} 为数值", 0, 30, False, f"类型错误: {type(val)}")
                group_ok = False
            elif not close_enough(val, expected[key]):
                add_score(f"组 {g} 的 {key} 正确", 0, 30, False, f"期望 {expected[key]}, 实际 {val}")
                group_ok = False

if group_ok:
    total_score += add_score("groups 数组完全正确", 30, 30, True, "所有组差异值计算正确")
else:
    total_score += add_score("groups 数组完全正确", 0, 30, False, "详见子项错误")

# ===== 5. Validate best_group =====
if best_group is None:
    # fallback: possibly no group meets condition
    best_group = ""  # should not happen given our data
expected_best = best_group
if report.get("best_group") == expected_best:
    total_score += add_score("best_group 正确", 30, 30, True, f"最佳组为 {expected_best}")
else:
    total_score += add_score("best_group 正确", 0, 30, False, f"期望 {expected_best}, 实际 {report.get('best_group')}")

# ===== Write final score =====
result = {
    "total_score": total_score,
    "details": score_details
}
with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
    json.dump(result, f, indent=2)

print(f"Total score: {total_score}/100")
