import sys
import json
import os
from pathlib import Path

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    ws = Path(workspace)
    details = []
    total_score = 0

    # 1. 检查 reports/ 目录是否存在 (10分)
    reports_dir = ws / "reports"
    if reports_dir.is_dir():
        details.append({"item": "Reports directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "reports/ directory found"})
        total_score += 10
    else:
        details.append({"item": "Reports directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "reports/ directory not found"})

    # 2. 检查报告文件是否存在 (10分)
    report_file = reports_dir / "cost_report_q2_2026.json"
    if report_file.is_file():
        details.append({"item": "Report file exists", "score": 10, "max_score": 10, "passed": True, "reason": "cost_report_q2_2026.json found"})
        total_score += 10
    else:
        details.append({"item": "Report file exists", "score": 0, "max_score": 10, "passed": False, "reason": "cost_report_q2_2026.json not found"})
        # 无法继续，提前返回
        write_score(details, total_score)
        return

    # 3. 检查 JSON 合法性 (10分)
    try:
        report = load_json(str(report_file))
        details.append({"item": "Report JSON is valid", "score": 10, "max_score": 10, "passed": True, "reason": "JSON parsed successfully"})
        total_score += 10
    except Exception as e:
        details.append({"item": "Report JSON is valid", "score": 0, "max_score": 10, "passed": False, "reason": f"Invalid JSON: {e}"})
        write_score(details, total_score)
        return

    # 4. 检查顶层字段 (5分)
    required_fields = ["report_id", "generated_at", "billing_month", "clusters", "total_cost"]
    missing = [f for f in required_fields if f not in report]
    if not missing:
        details.append({"item": "Top-level fields present", "score": 5, "max_score": 5, "passed": True, "reason": "All required fields exist"})
        total_score += 5
    else:
        details.append({"item": "Top-level fields present", "score": 0, "max_score": 5, "passed": False, "reason": f"Missing fields: {missing}"})

    # 5. 检查 billing_month 是否正确 (5分)
    if report.get("billing_month") == "2026-06":
        details.append({"item": "Billing month correct", "score": 5, "max_score": 5, "passed": True, "reason": "billing_month is 2026-06"})
        total_score += 5
    else:
        details.append({"item": "Billing month correct", "score": 0, "max_score": 5, "passed": False, "reason": f"Expected 2026-06, got {report.get('billing_month')}"})

    # 6. 检查 clusters 列表 (10分)
    clusters = report.get("clusters", [])
    expected_cluster_ids = {"c-ads", "c-lake", "c-retail"}
    actual_ids = {c.get("cluster_id") for c in clusters}
    if actual_ids == expected_cluster_ids:
        details.append({"item": "Clusters list correct", "score": 10, "max_score": 10, "passed": True, "reason": f"Contains exactly business clusters: {expected_cluster_ids}"})
        total_score += 10
    else:
        details.append({"item": "Clusters list correct", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected {expected_cluster_ids}, got {actual_ids}"})

    # 7. 检查每个集群的 cost 计算 (50分, 每个集群15分, 总cost 5分)
    # 预先加载原始数据重新计算
    try:
        clusters_data = load_json(str(ws / "data/resources/clusters.json"))["clusters"]
        ledger = load_json(str(ws / "data/resources/resource_ledger.json"))["resource_ledger"]
        catalogs = load_json(str(ws / "data/pricing/pricing_catalogs.json"))["pricing_catalogs"]
        attachments_data = load_json(str(ws / "data/attachments.json"))["attachments"]
    except Exception as e:
        details.append({"item": "Load source data", "score": 0, "max_score": 50, "passed": False, "reason": f"Cannot load source files: {e}"})
        write_score(details, total_score)
        return

    # 找到active catalog
    active_catalog = None
    for cat in catalogs:
        if cat["status"] == "active":
            active_catalog = cat
            break
    if not active_catalog:
        details.append({"item": "Active catalog found", "score": 0, "max_score": 50, "passed": False, "reason": "No active catalog"})
        write_score(details, total_score)
        return

    billing_hours = active_catalog["billing_hours"]
    rates = {}
    for r in active_catalog["rates"]:
        key = (r["resource_family"], r["metric_code"])
        rates[key] = r["rate_per_unit"]

    # 构建cluster_id -> cluster_role映射
    cluster_role_map = {c["cluster_id"]: c["cluster_role"] for c in clusters_data}

    # 处理ledger：去重(保留第一个entry_id), 排除shared_platform, 排除quantity=0, 排除单位不匹配(即unit与catalog中对应rate的unit不一致)
    seen_ids = set()
    filtered_entries = []
    for entry in ledger:
        eid = entry["entry_id"]
        if eid in seen_ids:
            continue
        seen_ids.add(eid)
        cid = entry["cluster_id"]
        if cluster_role_map.get(cid) != "business":
            continue
        if entry["quantity"] == 0:
            continue
        # 找到对应rate
        key = (entry["resource_family"], entry["metric_code"])
        if key not in rates:
            continue
        catalog_unit = None
        for r in active_catalog["rates"]:
            if r["resource_family"] == entry["resource_family"] and r["metric_code"] == entry["metric_code"]:
                catalog_unit = r["unit"]
                break
        if entry["unit"] != catalog_unit:
            continue
        filtered_entries.append(entry)

    # 计算每个cluster的cost
    expected_cluster_costs = {}
    for entry in filtered_entries:
        cid = entry["cluster_id"]
        key = (entry["resource_family"], entry["metric_code"])
        rate = rates[key]
        cost = entry["quantity"] * rate * billing_hours
        expected_cluster_costs.setdefault(cid, 0)
        expected_cluster_costs[cid] += cost

    # 转换为期望的cluster列表
    expected_clusters = []
    for cid in ["c-ads", "c-lake", "c-retail"]:
        cluster_obj = None
        for c in clusters_data:
            if c["cluster_id"] == cid:
                cluster_obj = c
                break
        total_cost = round(expected_cluster_costs.get(cid, 0), 2)
        resources = []
        for entry in filtered_entries:
            if entry["cluster_id"] == cid:
                key = (entry["resource_family"], entry["metric_code"])
                rate = rates[key]
                cost = round(entry["quantity"] * rate * billing_hours, 2)
                resources.append({
                    "resource_name": entry["resource_name"],
                    "metric_code": entry["metric_code"],
                    "quantity": entry["quantity"],
                    "rate_per_unit": rate,
                    "billing_hours": billing_hours,
                    "cost": cost
                })
        expected_clusters.append({
            "cluster_id": cid,
            "cluster_name": cluster_obj["cluster_name"],
            "total_cost": total_cost,
            "resources": resources
        })
    expected_total = round(sum(c["total_cost"] for c in expected_clusters), 2)

    # 比较每个集群
    cluster_score = 0
    max_cluster_score = 15 * 3 + 5  # 每个集群15，总cost 5 => 50
    cluster_issues = []
    for i, exp_cluster in enumerate(expected_clusters):
        act_cluster = None
        for ac in clusters:
            if ac.get("cluster_id") == exp_cluster["cluster_id"]:
                act_cluster = ac
                break
        if not act_cluster:
            cluster_issues.append(f"Missing cluster {exp_cluster['cluster_id']}")
            continue
        # 检查total_cost (精确到2位)
        if abs(act_cluster.get("total_cost", 0) - exp_cluster["total_cost"]) > 0.01:
            cluster_issues.append(f"Cluster {exp_cluster['cluster_id']} total_cost expected {exp_cluster['total_cost']}, got {act_cluster.get('total_cost')}")
            continue
        # 检查resources数量
        exp_res = exp_cluster["resources"]
        act_res = act_cluster.get("resources", [])
        if len(act_res) != len(exp_res):
            cluster_issues.append(f"Cluster {exp_cluster['cluster_id']} resources count expected {len(exp_res)}, got {len(act_res)}")
            continue
        # 检查每个resource
        for er in exp_res:
            found = False
            for ar in act_res:
                if ar.get("resource_name") == er["resource_name"] and ar.get("metric_code") == er["metric_code"]:
                    if abs(ar.get("cost", 0) - er["cost"]) > 0.01:
                        cluster_issues.append(f"Cluster {exp_cluster['cluster_id']} resource {er['resource_name']} cost expected {er['cost']}, got {ar.get('cost')}")
                    else:
                        found = True
                    break
            if not found:
                cluster_issues.append(f"Cluster {exp_cluster['cluster_id']} missing resource {er['resource_name']} / {er['metric_code']}")

    if not cluster_issues:
        cluster_score = max_cluster_score  # 50
        details.append({"item": "Cluster cost calculations", "score": 50, "max_score": 50, "passed": True, "reason": "All cluster costs and resources match expected"})
        total_score += 50
    else:
        # 部分得分：每个集群15，总cost 5
        per_cluster = 15
        total_cost_weight = 5
        earned = 0
        for i, exp_cluster in enumerate(expected_clusters):
            act_cluster = next((ac for ac in clusters if ac.get("cluster_id") == exp_cluster["cluster_id"]), None)
            if act_cluster and abs(act_cluster.get("total_cost", 0) - exp_cluster["total_cost"]) <= 0.01:
                earned += per_cluster
        # 总cost
        if abs(report.get("total_cost", 0) - expected_total) <= 0.01:
            earned += total_cost_weight
        details.append({"item": "Cluster cost calculations", "score": earned, "max_score": 50, "passed": earned >= 45, "reason": f"Issues: {cluster_issues[:3]}"})
        total_score += earned

    write_score(details, total_score)

def write_score(details, total_score):
    result = {
        "total_score": min(total_score, 100),
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    verify()
