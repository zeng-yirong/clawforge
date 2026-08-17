import os
import json
import random

def build_env():
    # ---------- 基础目录 ----------
    os.makedirs("data/accounts", exist_ok=True)
    os.makedirs("data/attachments", exist_ok=True)
    os.makedirs("data/contacts", exist_ok=True)
    os.makedirs("data/pricing", exist_ok=True)
    os.makedirs("data/resources", exist_ok=True)
    os.makedirs("raw_logs", exist_ok=True)    # 干扰目录

    # ---------- 附件 ----------
    rules_content = """# Cloud Cost Accounting Rules (v2.1)

## Resource Category Mapping
| metric_code          | category | 
|----------------------|----------|
| vcpu                 | compute  |
| memory_gb            | compute  |
| gpu                  | compute  |
| block_storage_gb     | storage  |
| object_storage_gb    | storage  |

## Cost Calculation
For each **business** cluster (cluster_role == "business"):
1. Fetch all resource ledger entries for that cluster.
2. Exclude any entry where `quantity <= 0`.
3. For each entry, look up the corresponding `unit_price` from the **active** pricing catalog (status == "active") using the `metric_code`.
4. Compute `cost = quantity * unit_price`.
5. Sum costs by category (compute / storage).
6. Write output as a JSON array of objects, each containing:
   - `cluster_id`
   - `cluster_name`
   - `total_compute_cost` (float, 2 decimals)
   - `total_storage_cost` (float, 2 decimals)
   - `total_cost` (float, 2 decimals)

Output file: `monthly_cost_report.json` at workspace root.
"""
    with open("data/attachments/cost_accounting_rules.md", "w") as f:
        f.write(rules_content)

    # ---------- 集群 ----------
    clusters = [
        {"cluster_id": "c_ads", "cluster_name": "ads-ranking", "business_service": "Ads ranking and campaign inference", "domain": "marketing", "environment": "prod", "region": "us-east-1", "owner_team": "Growth Engineering", "cluster_role": "business", "service_tier": "tier_1", "workload_tags": ["ads", "ml"]},
        {"cluster_id": "c_lake", "cluster_name": "lakehouse-analytics", "business_service": "Lakehouse analytics and finance marts", "domain": "data", "environment": "prod", "region": "eu-west-1", "owner_team": "Data Platform", "cluster_role": "business", "service_tier": "tier_1", "workload_tags": ["analytics", "etl"]},
        {"cluster_id": "c_retail", "cluster_name": "retail-core", "business_service": "Storefront and order orchestration", "domain": "commerce", "environment": "prod", "region": "us-west-2", "owner_team": "Commerce Platform", "cluster_role": "business", "service_tier": "tier_2", "workload_tags": ["storefront", "order"]},
        {"cluster_id": "c_shared", "cluster_name": "shared-ops", "business_service": "Shared CI and platform tooling", "domain": "infrastructure", "environment": "prod", "region": "us-east-1", "owner_team": "Cloud Foundations", "cluster_role": "shared_platform", "service_tier": "tier_2", "workload_tags": ["ci", "tools"]},  # 干扰
    ]
    os.makedirs("data/resources", exist_ok=True)
    with open("data/resources/clusters.json", "w") as f:
        json.dump({"clusters": clusters}, f, indent=2)

    # ---------- 定价目录 ----------
    pricing_catalogs = [
        {
            "catalog_id": "pc_archive_202603",
            "version": "2026.03-archive",
            "status": "archived",
            "region": "global",
            "currency": "USD",
            "billing_month": "2026-03",
            "billing_hours": 744,
            "approved_for_reporting": False,
            "effective_from": "2026-03-01",
            "effective_to": "2026-03-31",
            "rates": [
                {"metric_code": "vcpu", "unit_price": 0.042},
                {"metric_code": "memory_gb", "unit_price": 0.012},
                {"metric_code": "gpu", "unit_price": 1.20},
                {"metric_code": "block_storage_gb", "unit_price": 0.10},
                {"metric_code": "object_storage_gb", "unit_price": 0.025},
            ]
        },
        {
            "catalog_id": "pc_live_202606",
            "version": "2026.06-live",
            "status": "active",
            "region": "global",
            "currency": "USD",
            "billing_month": "2026-06",
            "billing_hours": 720,
            "approved_for_reporting": True,
            "effective_from": "2026-06-01",
            "effective_to": "2026-06-30",
            "rates": [
                {"metric_code": "vcpu", "unit_price": 0.048},
                {"metric_code": "memory_gb", "unit_price": 0.015},
                {"metric_code": "gpu", "unit_price": 1.50},
                {"metric_code": "block_storage_gb", "unit_price": 0.12},
                {"metric_code": "object_storage_gb", "unit_price": 0.030},
            ]
        }
    ]
    os.makedirs("data/pricing", exist_ok=True)
    with open("data/pricing/pricing_catalogs.json", "w") as f:
        json.dump({"pricing_catalogs": pricing_catalogs}, f, indent=2)

    # ---------- 资源台账 ----------
    # 正确条目（三个business集群）
    entries = [
        # ads-ranking
        {"entry_id": "e001", "cluster_id": "c_ads", "cluster_name": "ads-ranking", "resource_name": "compute-node-1", "resource_family": "compute", "metric_code": "vcpu", "quantity": 32, "unit": "vcpu", "billing_model": "monthly"},
        {"entry_id": "e002", "cluster_id": "c_ads", "cluster_name": "ads-ranking", "resource_name": "compute-node-1", "resource_family": "compute", "metric_code": "memory_gb", "quantity": 128, "unit": "GiB", "billing_model": "monthly"},
        {"entry_id": "e003", "cluster_id": "c_ads", "cluster_name": "ads-ranking", "resource_name": "gpu-node-1", "resource_family": "compute", "metric_code": "gpu", "quantity": 4, "unit": "gpu", "billing_model": "monthly"},
        {"entry_id": "e004", "cluster_id": "c_ads", "cluster_name": "ads-ranking", "resource_name": "data-volume", "resource_family": "storage", "metric_code": "block_storage_gb", "quantity": 500, "unit": "GiB", "billing_model": "monthly"},
        # lakehouse-analytics
        {"entry_id": "e005", "cluster_id": "c_lake", "cluster_name": "lakehouse-analytics", "resource_name": "etl-node-1", "resource_family": "compute", "metric_code": "vcpu", "quantity": 64, "unit": "vcpu", "billing_model": "reserved"},
        {"entry_id": "e006", "cluster_id": "c_lake", "cluster_name": "lakehouse-analytics", "resource_name": "etl-node-1", "resource_family": "compute", "metric_code": "memory_gb", "quantity": 256, "unit": "GiB", "billing_model": "reserved"},
        {"entry_id": "e007", "cluster_id": "c_lake", "cluster_name": "lakehouse-analytics", "resource_name": "analytics-bucket", "resource_family": "storage", "metric_code": "object_storage_gb", "quantity": 2000, "unit": "GiB", "billing_model": "autoscale"},
        # retail-core
        {"entry_id": "e008", "cluster_id": "c_retail", "cluster_name": "retail-core", "resource_name": "web-node-1", "resource_family": "compute", "metric_code": "vcpu", "quantity": 8, "unit": "vcpu", "billing_model": "monthly"},
        {"entry_id": "e009", "cluster_id": "c_retail", "cluster_name": "retail-core", "resource_name": "web-node-1", "resource_family": "compute", "metric_code": "memory_gb", "quantity": 32, "unit": "GiB", "billing_model": "monthly"},
        {"entry_id": "e010", "cluster_id": "c_retail", "cluster_name": "retail-core", "resource_name": "order-store", "resource_family": "storage", "metric_code": "block_storage_gb", "quantity": 100, "unit": "GiB", "billing_model": "monthly"},
    ]

    # 干扰条目：shared-ops (shared_platform)
    entries.append({
        "entry_id": "e011", "cluster_id": "c_shared", "cluster_name": "shared-ops", "resource_name": "shared-worker", "resource_family": "compute", "metric_code": "vcpu", "quantity": 16, "unit": "vcpu", "billing_model": "monthly"
    })
    # 干扰条目：quantity <= 0
    entries.append({
        "entry_id": "e012", "cluster_id": "c_ads", "cluster_name": "ads-ranking", "resource_name": "old-volume", "resource_family": "storage", "metric_code": "block_storage_gb", "quantity": 0, "unit": "GiB", "billing_model": "monthly"
    })
    entries.append({
        "entry_id": "e013", "cluster_id": "c_lake", "cluster_name": "lakehouse-analytics", "resource_name": "expired-cache", "resource_family": "compute", "metric_code": "memory_gb", "quantity": -64, "unit": "GiB", "billing_model": "autoscale"
    })
    # 干扰条目：重复（不同entry_id但内容相同，应只算一条？规则没有去重，但理论上entry_id唯一，所以都算。为了避免歧义，我们再加一条正确集群的正常条目，加大计算量)
    entries.append({
        "entry_id": "e014", "cluster_id": "c_retail", "cluster_name": "retail-core", "resource_name": "cdn-cache", "resource_family": "storage", "metric_code": "object_storage_gb", "quantity": 50, "unit": "GiB", "billing_model": "autoscale"
    })

    # 随机打乱
    random.shuffle(entries)

    with open("data/resources/resource_ledger.json", "w") as f:
        json.dump({"resource_ledger": entries}, f, indent=2)

    # ---------- 其他干扰文件 ----------
    with open("raw_logs/old_audit.log", "w") as f:
        f.write("2026-06-01 00:00:00 INFO session started\n")
    with open("data/accounts/placeholder.json", "w") as f:
        json.dump({"accounts": []}, f)
    with open("data/contacts/contacts.json", "w") as f:
        json.dump({"contacts": []}, f)

if __name__ == "__main__":
    build_env()
