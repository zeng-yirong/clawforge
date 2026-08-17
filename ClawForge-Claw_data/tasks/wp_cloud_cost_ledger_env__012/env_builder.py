import os
import json
import shutil
from pathlib import Path

def build_env():
    # 清理残留
    if os.path.exists("data"):
        shutil.rmtree("data")
    if os.path.exists("reports"):
        shutil.rmtree("reports")
    if os.path.exists("raw_logs"):
        shutil.rmtree("raw_logs")
    if os.path.exists("backups"):
        shutil.rmtree("backups")

    # 1. accounts.json (干扰)
    accounts = [
        {"account_id": "acc-001", "display_name": "Prod-A", "department": "Engineering", "email": "eng@northstar.example.com", "permissions": ["admin"], "default_region": "us-east-1", "voice": ["en"]},
        {"account_id": "acc-002", "display_name": "Dev-B", "department": "Data", "email": "data@northstar.example.com", "permissions": ["read"], "default_region": "eu-west-1", "voice": ["en"]}
    ]
    os.makedirs("data", exist_ok=True)
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # 2. contacts.json (干扰)
    contacts = [
        {"contact_id": "c-01", "name": "Daniel Song", "role": "Cloud FinOps Lead", "email": "daniel.song@northstar.example.com"},
        {"contact_id": "c-02", "name": "Leah Kumar", "role": "Cloud Operations Manager", "email": "leah.kumar@northstar.example.com"},
        {"contact_id": "c-03", "name": "Tara Ng", "role": "Data Platform Director", "email": "tara.ng@northstar.example.com"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # 3. attachments.json + 两个附件文件
    attachments = [
        {"path": "cost_accounting_rules.md", "title": "Cloud Cost Accounting Rules", "kind": "accounting_policy", "description": "Rules for cost calculation: use active pricing catalog, exclude shared_platform clusters, deduplicate by entry_id (keep first occurrence), use billing_hours from catalog."},
        {"path": "report_schema.md", "title": "Monthly Cost Report Schema", "kind": "report_schema", "description": "Output JSON schema for the monthly cost report."}
    ]
    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

    # 写入附件内容
    os.makedirs("data", exist_ok=True)
    with open("cost_accounting_rules.md", "w") as f:
        f.write("""# Cloud Cost Accounting Rules
1. Only consider clusters with `cluster_role == "business"`.
2. Use the pricing catalog with `status == "active"` (there is exactly one active catalog).
3. For each resource entry in the ledger, compute cost = `quantity * rate_per_unit * billing_hours` where rate is taken from the active catalog's rates list matching `resource_family` and `metric_code`.
4. If there are duplicate `entry_id` values, keep only the first occurrence (the one with the smallest index in the file).
5. Ignore entries where `quantity == 0` or `unit` does not match the catalog unit (treat as missing rate → skip).
6. Sum costs per cluster and overall.
""")
    with open("report_schema.md", "w") as f:
        f.write("""# Monthly Cost Report Schema
Output file: `reports/cost_report_q2_2026.json`
Expected JSON structure:
{
  "report_id": "Q2-2026-cost-report",
  "generated_at": "<ISO timestamp>",
  "billing_month": "2026-06",
  "clusters": [
    {
      "cluster_id": "<id>",
      "cluster_name": "<name>",
      "total_cost": <float>,
      "resources": [
        {
          "resource_name": "<name>",
          "metric_code": "<code>",
          "quantity": <int>,
          "rate_per_unit": <float>,
          "billing_hours": <int>,
          "cost": <float>
        }
      ]
    }
  ],
  "total_cost": <float>
}
""")

    # 4. pricing catalogs
    os.makedirs("data/pricing", exist_ok=True)
    pricing_catalogs = [
        {
            "catalog_id": "cat-2026-03",
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
                {"resource_family": "compute", "metric_code": "vcpu", "unit": "vcpu", "rate_per_unit": 0.04},
                {"resource_family": "compute", "metric_code": "memory_gb", "unit": "GiB", "rate_per_unit": 0.008}
            ]
        },
        {
            "catalog_id": "cat-2026-06",
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
                {"resource_family": "compute", "metric_code": "vcpu", "unit": "vcpu", "rate_per_unit": 0.05},
                {"resource_family": "compute", "metric_code": "memory_gb", "unit": "GiB", "rate_per_unit": 0.01},
                {"resource_family": "storage", "metric_code": "block_storage_gb", "unit": "GiB", "rate_per_unit": 0.001},
                {"resource_family": "storage", "metric_code": "object_storage_gb", "unit": "GiB", "rate_per_unit": 0.0001}
            ]
        }
    ]
    with open("data/pricing/pricing_catalogs.json", "w") as f:
        json.dump({"pricing_catalogs": pricing_catalogs}, f, indent=2)

    # 5. clusters
    clusters = [
        {"cluster_id": "c-ads", "cluster_name": "ads-ranking", "business_service": "Ads ranking and campaign inference", "domain": "marketing", "environment": "prod", "region": "us-east-1", "owner_team": "Growth Engineering", "cluster_role": "business", "service_tier": "tier_1", "workload_tags": ["ads", "ml"]},
        {"cluster_id": "c-lake", "cluster_name": "lakehouse-analytics", "business_service": "Lakehouse analytics and finance marts", "domain": "data", "environment": "prod", "region": "us-east-1", "owner_team": "Data Platform", "cluster_role": "business", "service_tier": "tier_1", "workload_tags": ["analytics", "spark"]},
        {"cluster_id": "c-retail", "cluster_name": "retail-core", "business_service": "Storefront and order orchestration", "domain": "commerce", "environment": "prod", "region": "eu-west-1", "owner_team": "Commerce Platform", "cluster_role": "business", "service_tier": "tier_1", "workload_tags": ["storefront", "orders"]},
        {"cluster_id": "c-shared", "cluster_name": "shared-ops", "business_service": "Shared CI and platform tooling", "domain": "infrastructure", "environment": "prod", "region": "us-east-1", "owner_team": "Cloud Foundations", "cluster_role": "shared_platform", "service_tier": "tier_2", "workload_tags": ["ci", "monitoring"]}
    ]
    os.makedirs("data/resources", exist_ok=True)
    with open("data/resources/clusters.json", "w") as f:
        json.dump({"clusters": clusters}, f, indent=2)

    # 6. resource_ledger (包含脏数据：重复entry_id、无效单位、quantity=0、shared_platform条目)
    ledger = [
        # ads-ranking (business)
        {"entry_id": "e-001", "cluster_id": "c-ads", "cluster_name": "ads-ranking", "resource_name": "compute-pool-a", "resource_family": "compute", "metric_code": "vcpu", "quantity": 48, "unit": "vcpu", "billing_model": "reserved"},
        {"entry_id": "e-002", "cluster_id": "c-ads", "cluster_name": "ads-ranking", "resource_name": "compute-pool-a", "resource_family": "compute", "metric_code": "memory_gb", "quantity": 256, "unit": "GiB", "billing_model": "reserved"},
        # 重复 entry_id (故意复制第一行，但第二条quantity不同)
        {"entry_id": "e-001", "cluster_id": "c-ads", "cluster_name": "ads-ranking", "resource_name": "compute-pool-a", "resource_family": "compute", "metric_code": "vcpu", "quantity": 96, "unit": "vcpu", "billing_model": "reserved", "note": "duplicate"},
        # lakehouse-analytics (business)
        {"entry_id": "e-003", "cluster_id": "c-lake", "cluster_name": "lakehouse-analytics", "resource_name": "analytics-pool", "resource_family": "compute", "metric_code": "vcpu", "quantity": 96, "unit": "vcpu", "billing_model": "monthly"},
        {"entry_id": "e-004", "cluster_id": "c-lake", "cluster_name": "lakehouse-analytics", "resource_name": "analytics-pool", "resource_family": "compute", "metric_code": "memory_gb", "quantity": 512, "unit": "GiB", "billing_model": "monthly"},
        {"entry_id": "e-005", "cluster_id": "c-lake", "cluster_name": "lakehouse-analytics", "resource_name": "data-volume", "resource_family": "storage", "metric_code": "block_storage_gb", "quantity": 1000, "unit": "GiB", "billing_model": "monthly"},
        # retail-core (business)
        {"entry_id": "e-006", "cluster_id": "c-retail", "cluster_name": "retail-core", "resource_name": "storefront-vm", "resource_family": "compute", "metric_code": "vcpu", "quantity": 24, "unit": "vcpu", "billing_model": "monthly"},
        {"entry_id": "e-007", "cluster_id": "c-retail", "cluster_name": "retail-core", "resource_name": "storefront-vm", "resource_family": "compute", "metric_code": "memory_gb", "quantity": 128, "unit": "GiB", "billing_model": "monthly"},
        {"entry_id": "e-008", "cluster_id": "c-retail", "cluster_name": "retail-core", "resource_name": "static-assets", "resource_family": "storage", "metric_code": "object_storage_gb", "quantity": 5000, "unit": "GiB", "billing_model": "monthly"},
        # shared-ops (shared_platform – 不应计入)
        {"entry_id": "e-009", "cluster_id": "c-shared", "cluster_name": "shared-ops", "resource_name": "ci-pool", "resource_family": "compute", "metric_code": "vcpu", "quantity": 16, "unit": "vcpu", "billing_model": "monthly"},
        {"entry_id": "e-010", "cluster_id": "c-shared", "cluster_name": "shared-ops", "resource_name": "ci-pool", "resource_family": "compute", "metric_code": "memory_gb", "quantity": 64, "unit": "GiB", "billing_model": "monthly"},
        # 脏数据：数量为0
        {"entry_id": "e-011", "cluster_id": "c-ads", "cluster_name": "ads-ranking", "resource_name": "zero-usage", "resource_family": "compute", "metric_code": "vcpu", "quantity": 0, "unit": "vcpu", "billing_model": "monthly"},
        # 脏数据：单位不匹配（catalog中memory_gb单位是GiB，这里写GB）
        {"entry_id": "e-012", "cluster_id": "c-lake", "cluster_name": "lakehouse-analytics", "resource_name": "extra-mem", "resource_family": "compute", "metric_code": "memory_gb", "quantity": 100, "unit": "GB", "billing_model": "monthly", "note": "unit mismatch"},
    ]
    with open("data/resources/resource_ledger.json", "w") as f:
        json.dump({"resource_ledger": ledger}, f, indent=2)

    # 7. 干扰目录 raw_logs 和 backups
    os.makedirs("raw_logs", exist_ok=True)
    with open("raw_logs/monitor.log", "w") as f:
        f.write("2026-06-15 03:12:34 WARN cpu usage 95%\n")
    os.makedirs("backups", exist_ok=True)
    with open("backups/ledger_2026_05.json", "w") as f:
        f.write("{}")

if __name__ == "__main__":
    build_env()
    print("Environment built successfully.")
