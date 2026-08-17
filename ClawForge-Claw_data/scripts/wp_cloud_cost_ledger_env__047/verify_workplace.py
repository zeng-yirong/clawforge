import sys
import json
import os
import math

def load_json(path):
    with open(path) as f:
        return json.load(f)

def verify(workspace):
    details = []
    total_score = 0

    # 1. Check output file exists
    report_path = os.path.join(workspace, "monthly_cost_report.json")
    if not os.path.exists(report_path):
        details.append({"item": "输出文件存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件 monthly_cost_report.json 未找到"})
        total_score += 0
        # early exit because we can't proceed
        return total_score, details
    else:
        details.append({"item": "输出文件存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
        total_score += 10

    # 2. JSON validity
    try:
        with open(report_path) as f:
            report = json.load(f)
        details.append({"item": "JSON合法", "score": 10, "max_score": 10, "passed": True, "reason": "JSON解析成功"})
        total_score += 10
    except Exception as e:
        details.append({"item": "JSON合法", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON解析失败: {e}"})
        return total_score, details

    # 3. Structure check
    if not isinstance(report, dict):
        details.append({"item": "报告结构", "score": 0, "max_score": 10, "passed": False, "reason": "报告顶层不是字典"})
        total_score += 0
        return total_score, details
    if "report_month" not in report or "clusters" not in report:
        details.append({"item": "报告结构", "score": 0, "max_score": 10, "passed": False, "reason": "缺少 report_month 或 clusters 字段"})
        total_score += 0
    elif report["report_month"] != "2026-06":
        details.append({"item": "报告结构", "score": 0, "max_score": 10, "passed": False, "reason": f"report_month 应为 2026-06，实际为 {report['report_month']}"})
        total_score += 0
    else:
        details.append({"item": "报告结构", "score": 10, "max_score": 10, "passed": True, "reason": "报告包含所需字段且月份正确"})
        total_score += 10

    # 4. Load ground truth and compute expected costs
    try:
        clusters_data = load_json(os.path.join(workspace, "data/resources/clusters.json"))
        ledgers_data = load_json(os.path.join(workspace, "data/resources/resource_ledger.json"))
        catalogs_data = load_json(os.path.join(workspace, "data/pricing/pricing_catalogs.json"))
    except Exception as e:
        details.append({"item": "数据文件读取", "score": 0, "max_score": 0, "passed": False, "reason": f"无法读取源数据: {e}"})
        return total_score, details

    # build business cluster id set
    biz_cluster_ids = {c["cluster_id"] for c in clusters_data["clusters"] if c["cluster_role"] == "business"}
    # find active approved June catalog
    june_catalog = None
    for cat in catalogs_data["pricing_catalogs"]:
        if cat["billing_month"] == "2026-06" and cat["status"] == "active" and cat["approved_for_reporting"]:
            june_catalog = cat
            break
    if june_catalog is None:
        details.append({"item": "定价目录选择", "score": 0, "max_score": 20, "passed": False, "reason": "未找到符合条件的2026-06活跃批准目录"})
        total_score += 0
        return total_score, details
    # build rate map: (resource_family, metric_code) -> unit_price
    rate_map = {}
    for r in june_catalog["rates"]:
        rate_map[(r["resource_family"], r["metric_code"])] = r["unit_price"]

    # aggregate costs per cluster
    expected_costs = {}
    for entry in ledgers_data["resource_ledger"]:
        cid = entry["cluster_id"]
        if cid not in biz_cluster_ids:
            continue
        family = entry["resource_family"]
        metric = entry["metric_code"]
        qty = entry["quantity"]
        key = (family, metric)
        if key in rate_map:
            cost = qty * rate_map[key]
            expected_costs[cid] = expected_costs.get(cid, 0.0) + cost
    # map cluster_id to cluster_name
    id_to_name = {c["cluster_id"]: c["cluster_name"] for c in clusters_data["clusters"]}

    # now verify agent output clusters list
    agent_clusters = report.get("clusters", [])
    if not isinstance(agent_clusters, list):
        details.append({"item": "集群列表类型", "score": 0, "max_score": 20, "passed": False, "reason": "clusters 不是列表"})
        total_score += 0
        return total_score, details

    # check each expected cluster is present with correct cost
    cluster_passed = []
    for cid, exp_cost in expected_costs.items():
        cname = id_to_name[cid]
        found = None
        for ac in agent_clusters:
            if ac.get("cluster_name") == cname:
                found = ac
                break
        if found is None:
            cluster_passed.append({"cluster": cname, "score": 0, "max_score": 10, "passed": False, "reason": f"未找到集群 {cname}"})
            total_score += 0
        else:
            try:
                agent_cost = float(found.get("total_cost", 0))
            except:
                agent_cost = 0.0
            if math.isclose(agent_cost, exp_cost, rel_tol=1e-5):
                cluster_passed.append({"cluster": cname, "score": 10, "max_score": 10, "passed": True, "reason": f"成本 {agent_cost} 与预期 {exp_cost} 一致"})
                total_score += 10
            else:
                cluster_passed.append({"cluster": cname, "score": 0, "max_score": 10, "passed": False, "reason": f"成本 {agent_cost} 与预期 {exp_cost} 不符（相差 {abs(agent_cost-exp_cost):.2f})"})
                total_score += 0

    # check that no extra clusters are included (should be exactly 3 business clusters)
    expected_names = {id_to_name[cid] for cid in biz_cluster_ids}
    agent_names = {ac.get("cluster_name") for ac in agent_clusters if isinstance(ac, dict)}
    extras = agent_names - expected_names
    if extras:
        details.append({"item": "无多余集群", "score": 0, "max_score": 10, "passed": False, "reason": f"包含了不应出现的集群: {extras}"})
        total_score += 0
    else:
        details.append({"item": "无多余集群", "score": 10, "max_score": 10, "passed": True, "reason": "只包含业务集群"})
        total_score += 10

    # add cluster detail items
    for cp in cluster_passed:
        details.append({"item": f"集群 {cp['cluster']} 成本", "score": cp["score"], "max_score": cp["max_score"], "passed": cp["passed"], "reason": cp["reason"]})

    # total score already accumulated
    return min(total_score, 100), details

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    total_score, details = verify(workspace)
    result = {"total_score": total_score, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(f"Verification complete. Total score: {total_score}/100")

if __name__ == "__main__":
    main()
