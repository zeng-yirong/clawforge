import sys
import json
import os
import math

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

def load_json(rel_path):
    full_path = os.path.join(workspace, rel_path)
    with open(full_path, "r", encoding="utf-8") as f:
        return json.load(f)

def file_exists(rel_path):
    return os.path.isfile(os.path.join(workspace, rel_path))

def dir_exists(rel_path):
    return os.path.isdir(os.path.join(workspace, rel_path))

def main():
    details = []
    total_score = 0

    # 1. 检查 reports 目录是否存在 (5分)
    if dir_exists("reports"):
        details.append({"item": "reports directory exists", "score": 5, "max_score": 5, "passed": True, "reason": "Found reports/"})
        total_score += 5
    else:
        details.append({"item": "reports directory exists", "score": 0, "max_score": 5, "passed": False, "reason": "Missing reports/"})

    # 2. 检查报告文件是否存在 (10分)
    report_path = "reports/monthly_cost_report.json"
    if file_exists(report_path):
        details.append({"item": "report file exists", "score": 10, "max_score": 10, "passed": True, "reason": f"Found {report_path}"})
        total_score += 10
    else:
        details.append({"item": "report file exists", "score": 0, "max_score": 10, "passed": False, "reason": f"Missing {report_path}"})
        # 如果文件不存在，后续检查都无效，返回
        print(json.dumps({"total_score": total_score, "details": details}))
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f)
        return

    # 3. 文件内容合法 JSON (5分)
    try:
        report_data = load_json(report_path)
        details.append({"item": "report JSON is valid", "score": 5, "max_score": 5, "passed": True, "reason": "Valid JSON"})
        total_score += 5
    except Exception as e:
        details.append({"item": "report JSON is valid", "score": 0, "max_score": 5, "passed": False, "reason": f"Invalid JSON: {e}"})
        print(json.dumps({"total_score": total_score, "details": details}))
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f)
        return

    # 4. 检查报告结构：应该是一个列表，每个元素包含 cluster_id, cluster_name, compute_cost, storage_cost, total_cost
    if not isinstance(report_data, list):
        details.append({"item": "report structure", "score": 0, "max_score": 10, "passed": False, "reason": "Root should be a list"})
        print(json.dumps({"total_score": total_score, "details": details}))
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f)
        return

    required_fields = {"cluster_id", "cluster_name", "compute_cost", "storage_cost", "total_cost"}
    all_have_fields = True
    for entry in report_data:
        if not all(f in entry for f in required_fields):
            all_have_fields = False
            break
    if all_have_fields:
        details.append({"item": "report fields present", "score": 10, "max_score": 10, "passed": True, "reason": "All entries have required fields"})
        total_score += 10
    else:
        details.append({"item": "report fields present", "score": 0, "max_score": 10, "passed": False, "reason": "Missing required fields in some entries"})
        print(json.dumps({"total_score": total_score, "details": details}))
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f)
        return

    # 5. 检查是否包含非业务集群 (shared-ops 不应出现) (10分)
    cluster_names_in_report = {e["cluster_name"] for e in report_data}
    if "shared-ops" in cluster_names_in_report:
        details.append({"item": "exclude shared_platform clusters", "score": 0, "max_score": 10, "passed": False, "reason": "shared-ops should not be present"})
        total_score += 0
    else:
        details.append({"item": "exclude shared_platform clusters", "score": 10, "max_score": 10, "passed": True, "reason": "No shared-ops in report"})
        total_score += 10

    # 6. 检查是否包含所有三个业务集群 (ads-ranking, lakehouse-analytics, retail-core) (10分)
    expected_business = {"ads-ranking", "lakehouse-analytics", "retail-core"}
    present = cluster_names_in_report & expected_business
    if present == expected_business:
        details.append({"item": "all business clusters present", "score": 10, "max_score": 10, "passed": True, "reason": f"Found {sorted(present)}"})
        total_score += 10
    else:
        missing = expected_business - present
        details.append({"item": "all business clusters present", "score": 0, "max_score": 10, "passed": False, "reason": f"Missing clusters: {missing}"})
        total_score += 0

    # 7. 计算期望成本并比对 (40分, 细分为 compute 和 storage)
    # 加载定价目录，选择 active 且 approved_for_reporting 为 true 的
    try:
        catalogs = load_json("data/pricing/pricing_catalogs.json")
        active_catalog = None
        for cat in catalogs["pricing_catalogs"]:
            if cat.get("status") == "active" and cat.get("approved_for_reporting") is True:
                active_catalog = cat
                break
        if active_catalog is None:
            details.append({"item": "pricing catalog selection", "score": 0, "max_score": 40, "passed": False, "reason": "Could not find active approved catalog"})
            total_score += 0
            print(json.dumps({"total_score": total_score, "details": details}))
            with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
                json.dump({"total_score": total_score, "details": details}, f)
            return

        # 构建速率字典
        rates = {}
        for r in active_catalog["rates"]:
            key = (r["resource_family"], r["metric_code"])
            rates[key] = r["unit_price"]

        # 加载资源流水，忽略重复 entry_id (取第一个出现的)
        ledger = load_json("data/resources/resource_ledger.json")
        seen_entries = set()
        valid_ledger = []
        for entry in ledger["resource_ledger"]:
            eid = entry["entry_id"]
            if eid in seen_entries:
                continue
            seen_entries.add(eid)
            valid_ledger.append(entry)

        # 加载集群信息，确定 business 集群的 id 列表
        clusters_data = load_json("data/resources/clusters.json")
        business_cluster_ids = set()
        for cl in clusters_data["clusters"]:
            if cl["cluster_role"] == "business":
                business_cluster_ids.add(cl["cluster_id"])

        # 计算每个业务集群的成本
        expected_costs = {}
        for entry in valid_ledger:
            cid = entry["cluster_id"]
            if cid not in business_cluster_ids:
                continue  # 非业务集群忽略
            resource_family = entry["resource_family"]
            metric_code = entry["metric_code"]
            qty = entry["quantity"]
            # 只计算规则中指定的 metric_code
            if metric_code == "memory_gb":
                continue  # 根据规则忽略
            if (resource_family, metric_code) in rates:
                cost = qty * rates[(resource_family, metric_code)]
                if cid not in expected_costs:
                    expected_costs[cid] = {"compute": 0.0, "storage": 0.0}
                if resource_family == "compute":
                    expected_costs[cid]["compute"] += cost
                elif resource_family == "storage":
                    expected_costs[cid]["storage"] += cost
            # 其他 metric_code 忽略（不计算成本）

        # 构建集群名称映射
        cluster_id_to_name = {}
        for cl in clusters_data["clusters"]:
            cluster_id_to_name[cl["cluster_id"]] = cl["cluster_name"]

        # 检查报告中的每个条目是否匹配
        compute_correct = True
        storage_correct = True
        tolerance = 1e-6
        for entry in report_data:
            cid = entry["cluster_id"]
            cname = entry["cluster_name"]
            if cid not in expected_costs:
                # 不应该出现
                compute_correct = False
                storage_correct = False
                continue
            expected = expected_costs[cid]
            actual_compute = entry["compute_cost"]
            actual_storage = entry["storage_cost"]
            if abs(actual_compute - expected["compute"]) > tolerance:
                compute_correct = False
            if abs(actual_storage - expected["storage"]) > tolerance:
                storage_correct = False

        compute_score = 20 if compute_correct else 0
        storage_score = 20 if storage_correct else 0
        details.append({"item": "compute cost accuracy", "score": compute_score, "max_score": 20, "passed": compute_correct,
                        "reason": "Compute costs match expected" if compute_correct else "Compute costs mismatch"})
        details.append({"item": "storage cost accuracy", "score": storage_score, "max_score": 20, "passed": storage_correct,
                        "reason": "Storage costs match expected" if storage_correct else "Storage costs mismatch"})
        total_score += compute_score + storage_score

    except Exception as e:
        details.append({"item": "cost calculation verification", "score": 0, "max_score": 40, "passed": False, "reason": f"Error during verification: {e}"})

    # 写入结果
    result = {"total_score": total_score, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
