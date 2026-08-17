import os
import json
import shutil

def build_env():
    # Clean slate
    if os.path.exists("data"):
        shutil.rmtree("data")
    if os.path.exists("reports"):
        shutil.rmtree("reports")

    # ---- data/attachments ----
    os.makedirs("data/attachments")
    cost_accounting_rules = """# Cloud Cost Accounting Rules
## Billing computation
- For compute resources (metric_code in [vcpu, memory_gb, gpu]): cost = quantity × hourly_rate × billing_hours
- For storage resources (metric_code in [block_storage_gb, object_storage_gb]): cost = quantity × unit_rate (per GB-month)
- Billing hours are defined in the pricing catalog field 'billing_hours'.
- Only entries belonging to clusters with cluster_role = 'business' are included.
- Exclude any entry where cluster_id is not present in clusters.json.
"""
    with open("data/attachments/cost_accounting_rules.md", "w") as f:
        f.write(cost_accounting_rules)

    # ---- data/pricing ----
    os.makedirs("data/pricing")
    pricing_catalogs = {
        "pricing_catalogs": [
            {
                "catalog_id": "cat-2026-03",
                "version": "2026.03-archive",
                "status": "archived",
                "region": "us-east-1",
                "currency": "USD",
                "billing_month": "2026-03",
                "billing_hours": 744,
                "approved_for_reporting": False,
                "effective_from": "2026-03-01",
                "effective_to": "2026-03-31",
                "rates": [
                    {"resource_family": "compute", "metric_code": "vcpu", "unit": "vcpu", "hourly_rate": 0.04},
                    {"resource_family": "compute", "metric_code": "memory_gb", "unit": "GiB", "hourly_rate": 0.008},
                    {"resource_family": "compute", "metric_code": "gpu", "unit": "gpu", "hourly_rate": 0.4},
                    {"resource_family": "storage", "metric_code": "block_storage_gb", "unit": "GiB", "gb_month_rate": 0.08},
                    {"resource_family": "storage", "metric_code": "object_storage_gb", "unit": "GiB", "gb_month_rate": 0.015}
                ]
            },
            {
                "catalog_id": "cat-2026-06",
                "version": "2026.06-live",
                "status": "active",
                "region": "us-east-1",
                "currency": "USD",
                "billing_month": "2026-06",
                "billing_hours": 720,
                "approved_for_reporting": True,
                "effective_from": "2026-06-01",
                "effective_to": "2026-06-30",
                "rates": [
                    {"resource_family": "compute", "metric_code": "vcpu", "unit": "vcpu", "hourly_rate": 0.05},
                    {"resource_family": "compute", "metric_code": "memory_gb", "unit": "GiB", "hourly_rate": 0.01},
                    {"resource_family": "compute", "metric_code": "gpu", "unit": "gpu", "hourly_rate": 0.5},
                    {"resource_family": "storage", "metric_code": "block_storage_gb", "unit": "GiB", "gb_month_rate": 0.10},
                    {"resource_family": "storage", "metric_code": "object_storage_gb", "unit": "GiB", "gb_month_rate": 0.02}
                ]
            }
        ]
    }
    with open("data/pricing/pricing_catalogs.json", "w") as f:
        json.dump(pricing_catalogs, f, indent=2)

    # ---- data/resources ----
    os.makedirs("data/resources")
    clusters = {
        "clusters": [
            {
                "cluster_id": "c-ads",
                "cluster_name": "ads-ranking",
                "business_service": "Ads ranking and campaign inference",
                "domain": "marketing",
                "environment": "production",
                "region": "us-east-1",
                "owner_team": "Growth Engineering",
                "cluster_role": "business",
                "service_tier": "tier_1",
                "workload_tags": ["ml", "real-time"]
            },
            {
                "cluster_id": "c-lake",
                "cluster_name": "lakehouse-analytics",
                "business_service": "Lakehouse analytics and finance marts",
                "domain": "data",
                "environment": "production",
                "region": "us-east-1",
                "owner_team": "Data Platform",
                "cluster_role": "business",
                "service_tier": "tier_1",
                "workload_tags": ["analytics", "etl"]
            },
            {
                "cluster_id": "c-retail",
                "cluster_name": "retail-core",
                "business_service": "Storefront and order orchestration",
                "domain": "commerce",
                "environment": "production",
                "region": "us-east-1",
                "owner_team": "Commerce Platform",
                "cluster_role": "business",
                "service_tier": "tier_1",
                "workload_tags": ["web", "transactional"]
            },
            {
                "cluster_id": "c-shared",
                "cluster_name": "shared-ops",
                "business_service": "Shared CI and platform tooling",
                "domain": "infrastructure",
                "environment": "production",
                "region": "us-east-1",
                "owner_team": "Cloud Foundations",
                "cluster_role": "shared_platform",
                "service_tier": "tier_2",
                "workload_tags": ["ci", "monitoring"]
            }
        ]
    }
    with open("data/resources/clusters.json", "w") as f:
        json.dump(clusters, f, indent=2)

    # Resource ledger with business entries + interference
    resource_ledger = {
        "resource_ledger": [
            # ads-ranking entries
            {"entry_id": "e-001", "cluster_id": "c-ads", "cluster_name": "ads-ranking", "resource_name": "ml-node-vcpu", "resource_family": "compute", "metric_code": "vcpu", "quantity": 100, "unit": "vcpu", "billing_model": "monthly"},
            {"entry_id": "e-002", "cluster_id": "c-ads", "cluster_name": "ads-ranking", "resource_name": "ml-node-mem", "resource_family": "compute", "metric_code": "memory_gb", "quantity": 256, "unit": "GiB", "billing_model": "monthly"},
            {"entry_id": "e-003", "cluster_id": "c-ads", "cluster_name": "ads-ranking", "resource_name": "ml-node-block", "resource_family": "storage", "metric_code": "block_storage_gb", "quantity": 500, "unit": "GiB", "billing_model": "monthly"},
            # lakehouse-analytics entries
            {"entry_id": "e-004", "cluster_id": "c-lake", "cluster_name": "lakehouse-analytics", "resource_name": "data-node-vcpu", "resource_family": "compute", "metric_code": "vcpu", "quantity": 200, "unit": "vcpu", "billing_model": "monthly"},
            {"entry_id": "e-005", "cluster_id": "c-lake", "cluster_name": "lakehouse-analytics", "resource_name": "data-node-mem", "resource_family": "compute", "metric_code": "memory_gb", "quantity": 512, "unit": "GiB", "billing_model": "monthly"},
            {"entry_id": "e-006", "cluster_id": "c-lake", "cluster_name": "lakehouse-analytics", "resource_name": "data-obj-store", "resource_family": "storage", "metric_code": "object_storage_gb", "quantity": 2000, "unit": "GiB", "billing_model": "monthly"},
            # retail-core entries
            {"entry_id": "e-007", "cluster_id": "c-retail", "cluster_name": "retail-core", "resource_name": "web-node-vcpu", "resource_family": "compute", "metric_code": "vcpu", "quantity": 150, "unit": "vcpu", "billing_model": "monthly"},
            {"entry_id": "e-008", "cluster_id": "c-retail", "cluster_name": "retail-core", "resource_name": "web-node-gpu", "resource_family": "compute", "metric_code": "gpu", "quantity": 4, "unit": "gpu", "billing_model": "monthly"},
            {"entry_id": "e-009", "cluster_id": "c-retail", "cluster_name": "retail-core", "resource_name": "web-node-mem", "resource_family": "compute", "metric_code": "memory_gb", "quantity": 128, "unit": "GiB", "billing_model": "monthly"},
            # Interference: test cluster (should be excluded)
            {"entry_id": "e-010", "cluster_id": "c-test", "cluster_name": "test-cluster", "resource_name": "test-vcpu", "resource_family": "compute", "metric_code": "vcpu", "quantity": 10, "unit": "vcpu", "billing_model": "monthly"},
            # Interference: shared-ops (shared_platform, not business)
            {"entry_id": "e-011", "cluster_id": "c-shared", "cluster_name": "shared-ops", "resource_name": "ci-node-vcpu", "resource_family": "compute", "metric_code": "vcpu", "quantity": 50, "unit": "vcpu", "billing_model": "monthly"},
            # Interference: nonexistent cluster
            {"entry_id": "e-012", "cluster_id": "c-nonexistent", "cluster_name": "no-such-cluster", "resource_name": "ghost-block", "resource_family": "storage", "metric_code": "block_storage_gb", "quantity": 100, "unit": "GiB", "billing_model": "monthly"},
        ]
    }
    with open("data/resources/resource_ledger.json", "w") as f:
        json.dump(resource_ledger, f, indent=2)

    # ---- other data files (interference / realism) ----
    os.makedirs("data/logs")
    with open("data/logs/access.log", "w") as f:
        f.write("192.168.1.1 - - [01/Jul/2026:00:00:00 +0000] GET /api/cost HTTP/1.1 200 123\n")
    os.makedirs("data/backups")
    with open("data/backups/ledger_2026_05.json", "w") as f:
        f.write("{\"old\": true}\n")

    # Ensure reports directory exists (empty)
    os.makedirs("reports", exist_ok=True)

if __name__ == "__main__":
    build_env()
