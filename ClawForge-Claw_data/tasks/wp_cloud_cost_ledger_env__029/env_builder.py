import os
import json

def build_env():
    # Ensure base directories
    for d in ["data", "data/pricing", "data/resources", "data/attachments", "reports"]:
        os.makedirs(d, exist_ok=True)

    # ------ accounts.json (minimal, for realism) ------
    accounts = [
        {"account_id": "acct-001", "display_name": "NorthStar Engineering", "department": "Engineering",
         "email": "eng@northstar.example.com", "permissions": ["read", "write"], "default_region": "us-east-1", "voice": []}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # ------ contacts.json ------
    contacts = [
        {"contact_id": "c-001", "name": "Daniel Song", "role": "Cloud FinOps Lead",
         "email": "daniel.song@northstar.example.com"},
        {"contact_id": "c-002", "name": "Leah Kumar", "role": "Cloud Operations Manager",
         "email": "leah.kumar@northstar.example.com"},
        {"contact_id": "c-003", "name": "Tara Ng", "role": "Data Platform Director",
         "email": "tara.ng@northstar.example.com"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # ------ attachments.json (metadata) and actual files ------
    attachments_meta = [
        {"path": "data/attachments/cost_accounting_rules.md", "title": "Cloud Cost Accounting Rules",
         "kind": "accounting_policy", "description": "Rules for attributing cloud costs."},
        {"path": "data/attachments/report_schema.md", "title": "Monthly Cost Report Schema",
         "kind": "report_schema", "description": "Expected JSON structure for cost reports."}
    ]
    with open("data/attachments.json", "w") as f:
        json.dump(attachments_meta, f, indent=2)

    with open("data/attachments/cost_accounting_rules.md", "w") as f:
        f.write("# Cost Accounting Rules\nOnly use active pricing catalogs. Exclude shared platform clusters.\n")

    with open("data/attachments/report_schema.md", "w") as f:
        f.write("""# Report Schema
The cost report must be a JSON object with:
- "report_month": string (e.g., "2026-06")
- "generated_at": string (ISO timestamp)
- "clusters": list of objects, each with:
  - "cluster_id": string
  - "cluster_name": string
  - "compute_cost": number
  - "storage_cost": number
  - "total_cost": number
- "total_cost": number
""")

    # ------ pricing catalogs ------
    pricing_catalogs = [
        {
            "catalog_id": "catalog-2026-03",
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
                {"resource_family": "compute", "metric_code": "vcpu", "unit_price": 0.20},
                {"resource_family": "compute", "metric_code": "memory_gb", "unit_price": 0.04},
                {"resource_family": "storage", "metric_code": "block_storage_gb", "unit_price": 0.08},
                {"resource_family": "storage", "metric_code": "object_storage_gb", "unit_price": 0.015}
            ]
        },
        {
            "catalog_id": "catalog-2026-06",
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
                {"resource_family": "compute", "metric_code": "vcpu", "unit_price": 0.25},
                {"resource_family": "compute", "metric_code": "memory_gb", "unit_price": 0.05},
                {"resource_family": "storage", "metric_code": "block_storage_gb", "unit_price": 0.10},
                {"resource_family": "storage", "metric_code": "object_storage_gb", "unit_price": 0.02}
            ]
        }
    ]
    with open("data/pricing/pricing_catalogs.json", "w") as f:
        json.dump(pricing_catalogs, f, indent=2)

    # ------ clusters ------
    clusters = [
        {"cluster_id": "cl-ads", "cluster_name": "ads-ranking", "business_service": "Ads ranking and campaign inference",
         "domain": "marketing", "environment": "production", "region": "us-east-1",
         "owner_team": "Growth Engineering", "cluster_role": "business", "service_tier": "tier_1",
         "workload_tags": ["ml-training", "real-time"]},
        {"cluster_id": "cl-lake", "cluster_name": "lakehouse-analytics",
         "business_service": "Lakehouse analytics and finance marts",
         "domain": "data", "environment": "production", "region": "us-east-1",
         "owner_team": "Data Platform", "cluster_role": "business", "service_tier": "tier_2",
         "workload_tags": ["etl", "reporting"]},
        {"cluster_id": "cl-retail", "cluster_name": "retail-core",
         "business_service": "Storefront and order orchestration",
         "domain": "commerce", "environment": "production", "region": "us-west-2",
         "owner_team": "Commerce Platform", "cluster_role": "business", "service_tier": "tier_1",
         "workload_tags": ["critical", "web"]},
        {"cluster_id": "cl-shared", "cluster_name": "shared-ops",
         "business_service": "Shared CI and platform tooling",
         "domain": "infrastructure", "environment": "production", "region": "eu-central-1",
         "owner_team": "Cloud Foundations", "cluster_role": "shared_platform", "service_tier": "tier_2",
         "workload_tags": ["ci/cd", "monitoring"]}
    ]
    with open("data/resources/clusters.json", "w") as f:
        json.dump(clusters, f, indent=2)

    # ------ resource_ledger (with deliberate duplicates, distractions) ------
    resource_ledger = [
        # ads-ranking — vcpu splits into two entries (sum = 120)
        {"entry_id": "entry-001", "cluster_id": "cl-ads", "cluster_name": "ads-ranking",
         "resource_name": "ml-gpu-vm", "resource_family": "compute", "metric_code": "vcpu",
         "quantity": 100, "unit": "vcpu", "billing_model": "reserved"},
        {"entry_id": "entry-002", "cluster_id": "cl-ads", "cluster_name": "ads-ranking",
         "resource_name": "spot-instance", "resource_family": "compute", "metric_code": "vcpu",
         "quantity": 20, "unit": "vcpu", "billing_model": "autoscale"},
        # memory_gb: 400 + 200 = 600
        {"entry_id": "entry-003", "cluster_id": "cl-ads", "cluster_name": "ads-ranking",
         "resource_name": "ml-gpu-vm", "resource_family": "compute", "metric_code": "memory_gb",
         "quantity": 400, "unit": "GiB", "billing_model": "reserved"},
        {"entry_id": "entry-004", "cluster_id": "cl-ads", "cluster_name": "ads-ranking",
         "resource_name": "spot-instance", "resource_family": "compute", "metric_code": "memory_gb",
         "quantity": 200, "unit": "GiB", "billing_model": "autoscale"},
        # block_storage: 1500 + 500 = 2000
        {"entry_id": "entry-005", "cluster_id": "cl-ads", "cluster_name": "ads-ranking",
         "resource_name": "persistent-disk", "resource_family": "storage", "metric_code": "block_storage_gb",
         "quantity": 1500, "unit": "GiB", "billing_model": "monthly"},
        {"entry_id": "entry-006", "cluster_id": "cl-ads", "cluster_name": "ads-ranking",
         "resource_name": "extra-volume", "resource_family": "storage", "metric_code": "block_storage_gb",
         "quantity": 500, "unit": "GiB", "billing_model": "monthly"},
        # object_storage: 3000 + 2000 = 5000
        {"entry_id": "entry-007", "cluster_id": "cl-ads", "cluster_name": "ads-ranking",
         "resource_name": "data-bucket", "resource_family": "storage", "metric_code": "object_storage_gb",
         "quantity": 3000, "unit": "GiB", "billing_model": "monthly"},
        {"entry_id": "entry-008", "cluster_id": "cl-ads", "cluster_name": "ads-ranking",
         "resource_name": "archive-bucket", "resource_family": "storage", "metric_code": "object_storage_gb",
         "quantity": 2000, "unit": "GiB", "billing_model": "monthly"},

        # lakehouse-analytics — single entries
        {"entry_id": "entry-009", "cluster_id": "cl-lake", "cluster_name": "lakehouse-analytics",
         "resource_name": "compute-pool", "resource_family": "compute", "metric_code": "vcpu",
         "quantity": 80, "unit": "vcpu", "billing_model": "autoscale"},
        {"entry_id": "entry-010", "cluster_id": "cl-lake", "cluster_name": "lakehouse-analytics",
         "resource_name": "compute-pool", "resource_family": "compute", "metric_code": "memory_gb",
         "quantity": 400, "unit": "GiB", "billing_model": "autoscale"},
        {"entry_id": "entry-011", "cluster_id": "cl-lake", "cluster_name": "lakehouse-analytics",
         "resource_name": "data-lake-storage", "resource_family": "storage", "metric_code": "block_storage_gb",
         "quantity": 1500, "unit": "GiB", "billing_model": "monthly"},
        {"entry_id": "entry-012", "cluster_id": "cl-lake", "cluster_name": "lakehouse-analytics",
         "resource_name": "data-lake-bucket", "resource_family": "storage", "metric_code": "object_storage_gb",
         "quantity": 3000, "unit": "GiB", "billing_model": "monthly"},

        # retail-core
        {"entry_id": "entry-013", "cluster_id": "cl-retail", "cluster_name": "retail-core",
         "resource_name": "web-server-pool", "resource_family": "compute", "metric_code": "vcpu",
         "quantity": 200, "unit": "vcpu", "billing_model": "reserved"},
        {"entry_id": "entry-014", "cluster_id": "cl-retail", "cluster_name": "retail-core",
         "resource_name": "web-server-pool", "resource_family": "compute", "metric_code": "memory_gb",
         "quantity": 800, "unit": "GiB", "billing_model": "reserved"},
        {"entry_id": "entry-015", "cluster_id": "cl-retail", "cluster_name": "retail-core",
         "resource_name": "transaction-db-storage", "resource_family": "storage", "metric_code": "block_storage_gb",
         "quantity": 3000, "unit": "GiB", "billing_model": "monthly"},
        {"entry_id": "entry-016", "cluster_id": "cl-retail", "cluster_name": "retail-core",
         "resource_name": "static-assets-bucket", "resource_family": "storage", "metric_code": "object_storage_gb",
         "quantity": 8000, "unit": "GiB", "billing_model": "monthly"},

        # shared-ops – should be excluded
        {"entry_id": "entry-017", "cluster_id": "cl-shared", "cluster_name": "shared-ops",
         "resource_name": "ci-runner-pool", "resource_family": "compute", "metric_code": "vcpu",
         "quantity": 50, "unit": "vcpu", "billing_model": "autoscale"},
        {"entry_id": "entry-018", "cluster_id": "cl-shared", "cluster_name": "shared-ops",
         "resource_name": "ci-runner-pool", "resource_family": "compute", "metric_code": "memory_gb",
         "quantity": 200, "unit": "GiB", "billing_model": "autoscale"},
        {"entry_id": "entry-019", "cluster_id": "cl-shared", "cluster_name": "shared-ops",
         "resource_name": "monitoring-storage", "resource_family": "storage", "metric_code": "block_storage_gb",
         "quantity": 500, "unit": "GiB", "billing_model": "monthly"},

        # distraction: nonexistent cluster
        {"entry_id": "entry-020", "cluster_id": "cl-nonexistent", "cluster_name": "orphan-cluster",
         "resource_name": "stale-resource", "resource_family": "compute", "metric_code": "vcpu",
         "quantity": 999, "unit": "vcpu", "billing_model": "monthly"},
        # distraction: zero quantity entry (should not affect)
        {"entry_id": "entry-021", "cluster_id": "cl-ads", "cluster_name": "ads-ranking",
         "resource_name": "zero-use", "resource_family": "compute", "metric_code": "vcpu",
         "quantity": 0, "unit": "vcpu", "billing_model": "autoscale"}
    ]
    with open("data/resources/resource_ledger.json", "w") as f:
        json.dump(resource_ledger, f, indent=2)

    # placeholder for agent output
    open("reports/.gitkeep", "w").close()

if __name__ == "__main__":
    build_env()
