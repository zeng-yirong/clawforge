import os
import sys
import json
import math

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

score_details = []
total_score = 0
max_total = 100

def add_score(item, score, max_score, passed, reason):
    global total_score
    total_score += score
    score_details.append({
        "item": item,
        "score": score,
        "max_score": max_score,
        "passed": passed,
        "reason": reason
    })

# 1. 检查输出文件是否存在 (20 points)
report_path = os.path.join(workspace, "monthly_cost_report.json")
if os.path.isfile(report_path):
    add_score("Output file exists", 20, 20, True, "monthly_cost_report.json found")
else:
    add_score("Output file exists", 0, 20, False, "monthly_cost_report.json not found")
    # 终止，无法继续
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
    sys.exit(0)

# 2. JSON 合法性 (20 points)
try:
    with open(report_path, "r") as f:
        data = json.load(f)
    if isinstance(data, list):
        add_score("JSON is valid list", 20, 20, True, "Valid JSON array")
    else:
        add_score("JSON is valid list", 0, 20, False, "Root must be a JSON array")
except Exception as e:
    add_score("JSON is valid list", 0, 20, False, f"Invalid JSON: {str(e)}")
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
    sys.exit(0)

# 3. 集群集合正确 (20 points) - 必须恰好包含三个business集群
expected_cluster_ids = {"c_ads", "c_lake", "c_retail"}
expected_cluster_names = {"ads-ranking", "lakehouse-analytics", "retail-core"}
actual_ids = set()
actual_names = set()
for entry in data:
    if not isinstance(entry, dict):
        continue
    cid = entry.get("cluster_id")
    cname = entry.get("cluster_name")
    if cid:
        actual_ids.add(cid)
    if cname:
        actual_names.add(cname)

# 允许额外没有的集群应该扣分
if actual_ids == expected_cluster_ids and actual_names == expected_cluster_names:
    add_score("Correct cluster set", 20, 20, True, f"Clusters: {sorted(actual_ids)}")
else:
    missing_ids = expected_cluster_ids - actual_ids
    extra_ids = actual_ids - expected_cluster_ids
    reasons = []
    if missing_ids:
        reasons.append(f"Missing clusters: {missing_ids}")
    if extra_ids:
        reasons.append(f"Extra clusters (should be excluded): {extra_ids}")
    add_score("Correct cluster set", 0, 20, False, "; ".join(reasons))

# 4. 数值计算精确 (40 points)
# 先重新计算正确值（使用env_builder中的逻辑）
# 从工作区读取原始数据以获得正确基准（但verify脚本应该独立？更稳健是硬编码期望值，但需要与env_builder一致）
# 为了可维护，我们直接根据env_builder的数据重新计算。因为workplace中有原始文件。
# 但我们不能假定原始文件存在（agent可能删了），最佳做法是硬编码期望值（因为env_builder是确定性的）。
# 这里硬编码期望结果，避免依赖原始文件。
# 计算基于：active catalog rates = {vcpu:0.048, memory_gb:0.015, gpu:1.5, block_storage_gb:0.12, object_storage_gb:0.03}
# 有效条目（排除shared-ops, quantity<=0）:
# ads: e001 vcpu 32, e002 mem 128, e003 gpu 4, e004 block 500
# compute: 32*0.048 + 128*0.015 + 4*1.5 = 1.536 + 1.92 + 6 = 9.456
# storage: 500*0.12 = 60
# total: 69.456
# lake: e005 vcpu 64, e006 mem 256, e007 object 2000
# compute: 64*0.048 + 256*0.015 = 3.072 + 3.84 = 6.912
# storage: 2000*0.03 = 60
# total: 66.912
# retail: e008 vcpu 8, e009 mem 32, e010 block 100, e014 object 50
# compute: 8*0.048 + 32*0.015 = 0.384 + 0.48 = 0.864
# storage: 100*0.12 + 50*0.03 = 12 + 1.5 = 13.5
# total: 14.364

expected = {
    "c_ads": {"total_compute_cost": 9.46, "total_storage_cost": 60.0, "total_cost": 69.46},
    "c_lake": {"total_compute_cost": 6.91, "total_storage_cost": 60.0, "total_cost": 66.91},
    "c_retail": {"total_compute_cost": 0.86, "total_storage_cost": 13.5, "total_cost": 14.36}
}
# 注意四舍五入到两位小数：我们使用round(,2)计算期望值，然后比较差异<=0.005
def calc_exact():
    # 使用精确计算
    rates = {"vcpu": 0.048, "memory_gb": 0.015, "gpu": 1.5, "block_storage_gb": 0.12, "object_storage_gb": 0.03}
    # ads
    compute_ads = 32*rates["vcpu"] + 128*rates["memory_gb"] + 4*rates["gpu"]
    storage_ads = 500*rates["block_storage_gb"]
    total_ads = compute_ads + storage_ads
    # lake
    compute_lake = 64*rates["vcpu"] + 256*rates["memory_gb"]
    storage_lake = 2000*rates["object_storage_gb"]
    total_lake = compute_lake + storage_lake
    # retail
    compute_retail = 8*rates["vcpu"] + 32*rates["memory_gb"]
    storage_retail = 100*rates["block_storage_gb"] + 50*rates["object_storage_gb"]
    total_retail = compute_retail + storage_retail
    return {
        "c_ads": {"compute": round(compute_ads,2), "storage": round(storage_ads,2), "total": round(total_ads,2)},
        "c_lake": {"compute": round(compute_lake,2), "storage": round(storage_lake,2), "total": round(total_lake,2)},
        "c_retail": {"compute": round(compute_retail,2), "storage": round(storage_retail,2), "total": round(total_retail,2)}
    }
exact = calc_exact()
# 将期望值转换为expected格式
expected_exact = {
    "c_ads": {"total_compute_cost": exact["c_ads"]["compute"], "total_storage_cost": exact["c_ads"]["storage"], "total_cost": exact["c_ads"]["total"]},
    "c_lake": {"total_compute_cost": exact["c_lake"]["compute"], "total_storage_cost": exact["c_lake"]["storage"], "total_cost": exact["c_lake"]["total"]},
    "c_retail": {"total_compute_cost": exact["c_retail"]["compute"], "total_storage_cost": exact["c_retail"]["storage"], "total_cost": exact["c_retail"]["total"]}
}
# 为每个集群检查，每个集群10分（compute+storage正确5分，total正确5分？为了简化，每个集群整体10分）
cluster_items = 0
for cid, exp in expected_exact.items():
    actual_entry = None
    for entry in data:
        if entry.get("cluster_id") == cid:
            actual_entry = entry
            break
    if actual_entry is None:
        add_score(f"Cluster {cid} missing", 0, 10, False, "Entry not found in output")
        continue
    # 检查字段
    comp = actual_entry.get("total_compute_cost")
    stor = actual_entry.get("total_storage_cost")
    tot = actual_entry.get("total_cost")
    passed = True
    reasons = []
    if comp is None or not isinstance(comp, (int, float)):
        passed = False; reasons.append("total_compute_cost missing/non-numeric")
    if stor is None or not isinstance(stor, (int, float)):
        passed = False; reasons.append("total_storage_cost missing/non-numeric")
    if tot is None or not isinstance(tot, (int, float)):
        passed = False; reasons.append("total_cost missing/non-numeric")
    if not passed:
        add_score(f"Cluster {cid} costs", 0, 10, False, "; ".join(reasons))
        continue
    # 比较数值（允许0.01误差）
    if abs(comp - exp["total_compute_cost"]) > 0.01:
        passed = False; reasons.append(f"compute cost {comp} != expected {exp['total_compute_cost']}")
    if abs(stor - exp["total_storage_cost"]) > 0.01:
        passed = False; reasons.append(f"storage cost {stor} != expected {exp['total_storage_cost']}")
    if abs(tot - exp["total_cost"]) > 0.01:
        passed = False; reasons.append(f"total cost {tot} != expected {exp['total_cost']}")
    if passed:
        add_score(f"Cluster {cid} costs", 10, 10, True, "All costs correct")
    else:
        add_score(f"Cluster {cid} costs", 0, 10, False, "; ".join(reasons))

# 总分检查
actual_total = sum(entry.get("total_cost", 0) for entry in data if isinstance(entry, dict) and entry.get("cluster_id") in expected)
expected_total = sum(exp["total_cost"] for exp in expected_exact.values())
# 额外扣分项：如果包含shared-ops集群（已在上面的集合检查中覆盖，但可以单独加分惩罚）
# 这里我们已经在集合检查中扣了20分，所以不再重复。

# 写入结果
with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
    json.dump({"total_score": total_score, "details": score_details}, f, indent=2)

print(f"Total score: {total_score}/100")
