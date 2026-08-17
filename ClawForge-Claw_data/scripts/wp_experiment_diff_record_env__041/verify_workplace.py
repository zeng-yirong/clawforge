import sys
import json
import os
import math

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

score_details = []

def check(condition, item, score, max_score, reason_if_fail=""):
    passed = bool(condition)
    score_details.append({
        "item": item,
        "score": score if passed else 0,
        "max_score": max_score,
        "passed": passed,
        "reason": "" if passed else reason_if_fail
    })

# 1. 目录 ops 是否存在 (10分)
ops_dir = os.path.join(workspace, "ops")
check(os.path.isdir(ops_dir), "ops/ directory exists", 10, 10, "ops directory not found")

# 2. diff_record.json 文件是否存在 (10分)
diff_path = os.path.join(ops_dir, "diff_record.json")
check(os.path.isfile(diff_path), "ops/diff_record.json exists", 10, 10, "diff_record.json not found")

# 3. JSON 合法 (10分)
valid_json = False
data = None
try:
    with open(diff_path, "r") as f:
        data = json.load(f)
    valid_json = True
except Exception:
    pass
check(valid_json, "diff_record.json is valid JSON", 10, 10, "File is not valid JSON or cannot be parsed")

# 4. 结构正确：必须是一个 dict，键为 group_id，值为 dict 包含三个 diff 字段 (10分)
struct_ok = False
if isinstance(data, dict):
    required_diffs = ["accuracy_diff", "latency_ms_diff", "cost_usd_diff"]
    if all(isinstance(v, dict) for v in data.values()):
        if all(all(k in v for k in required_diffs) for v in data.values()):
            struct_ok = True
check(struct_ok, "JSON structure: dict of {group_id: {accuracy_diff, latency_ms_diff, cost_usd_diff}}", 10, 10,
      "Expected JSON structure is a dict mapping group_id to an object with exactly three numeric fields: accuracy_diff, latency_ms_diff, cost_usd_diff")

# 5. 计算预期差异并与结果比较 (每个组20分，共3组=60分)
# 预期值基于 env_builder 生成的数据（去重后平均值）
expected = {
    "group_a": {"accuracy_diff": 0.03, "latency_ms_diff": -14.0, "cost_usd_diff": -0.01},
    "group_b": {"accuracy_diff": 0.03, "latency_ms_diff": -12.5, "cost_usd_diff": -0.015},
    "group_c": {"accuracy_diff": 0.02, "latency_ms_diff": -6.0, "cost_usd_diff": -0.01}
}

if struct_ok:
    for gid, exp_vals in expected.items():
        if gid not in data:
            check(False, f"{gid} present", 0, 20, f"Missing group '{gid}' in output")
            continue
        actual = data[gid]
        # accuracy_diff (7分)
        acc_ok = math.isclose(actual.get("accuracy_diff", None), exp_vals["accuracy_diff"], abs_tol=1e-9)
        check(acc_ok, f"{gid} accuracy_diff correct", 7, 7, f"Expected {exp_vals['accuracy_diff']}, got {actual.get('accuracy_diff')}")
        # latency_ms_diff (7分)
        lat_ok = math.isclose(actual.get("latency_ms_diff", None), exp_vals["latency_ms_diff"], abs_tol=1e-9)
        check(lat_ok, f"{gid} latency_ms_diff correct", 7, 7, f"Expected {exp_vals['latency_ms_diff']}, got {actual.get('latency_ms_diff')}")
        # cost_usd_diff (6分)
        cost_ok = math.isclose(actual.get("cost_usd_diff", None), exp_vals["cost_usd_diff"], abs_tol=1e-9)
        check(cost_ok, f"{gid} cost_usd_diff correct", 6, 6, f"Expected {exp_vals['cost_usd_diff']}, got {actual.get('cost_usd_diff')}")
else:
    # 结构不正确，记0分
    for gid in expected:
        check(False, f"{gid} accuracy_diff correct", 0, 7, "Structure invalid, cannot check values")
        check(False, f"{gid} latency_ms_diff correct", 0, 7, "Structure invalid, cannot check values")
        check(False, f"{gid} cost_usd_diff correct", 0, 6, "Structure invalid, cannot check values")

# 计算总分
total = sum(d["score"] for d in score_details)
result = {
    "total_score": total,
    "details": score_details
}

output_path = os.path.join(workspace, "workplace_score.json")
with open(output_path, "w") as f:
    json.dump(result, f, indent=2)

print(f"Total score: {total}/100")
