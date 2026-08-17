import json
import os
import shutil

def build_env():
    # Clean slate
    base = os.getcwd()
    for d in ["data/resources", "data/pricing"]:
        os.makedirs(d, exist_ok=True)

    # ---- Clusters (4 clusters, 2 business, 2 shared_platform) ----
    clusters = {
        "clusters": [
            {
                "cluster_id": "c01",
                "cluster_name": "ads-ranking",
                "business_service": "Ads ranking and campaign inference",
                "domain": "marketing",
                "environment": "production",
                "region": "us-east-1",
                "owner_team": "Growth Engineering",
                "cluster_role": "business",
                "service_tier": "tier_1",
                "workload_tags": ["ad-serving", "real-time"]
            },
            {
                "cluster_id": "c02",
                "cluster_name": "lakehouse-analytics",
                "business_service": "Lakehouse analytics and finance marts",
                "domain": "data",
                "environment": "production",
                "region": "us-west-2",
                "owner_team": "Data Platform",
                "cluster_role": "business",
                "service_tier": "tier_1",
                "workload_tags": ["analytics", "etl"]
            },
            {
                "cluster_id": "c03",
                "cluster_name": "retail-core",
                "business_service": "Storefront and order orchestration",
                "domain": "commerce",
                "environment": "production",
                "region": "eu-west-1",
                "owner_team": "Commerce Platform",
                "cluster_role": "shared_platform",
                "service_tier": "tier_2",
                "workload_tags": ["checkout", "inventory"]
            },
            {
                "cluster_id": "c04",
                "cluster_name": "shared-ops",
                "business_service": "Shared CI and platform tooling",
                "domain": "infrastructure",
                "environment": "production",
                "region": "ap-southeast-1",
                "owner_team": "Cloud Foundations",
                "cluster_role": "shared_platform",
                "service_tier": "tier_2",
                "workload_tags": ["ci", "monitoring"]
            }
        ]
    }
    with open("data/resources/clusters.json", "w") as f:
        json.dump(clusters, f, indent=2)

    # ---- Resource Ledger (20 entries, 10 for business clusters, 10 distractors) ----
    resource_ledger = {
        "resource_ledger": [
            # Business cluster c01 – ads-ranking
            {"entry_id": "e001", "cluster_id": "c01", "cluster_name": "ads-ranking",
             "resource_name": "web-vcpu", "resource_family": "compute", "metric_code": "vcpu",
             "quantity": 100, "unit": "vcpu", "billing_model": "reserved"},
            {"entry_id": "e002", "cluster_id": "c01", "cluster_name": "ads-ranking",
             "resource_name": "web-mem", "resource_family": "compute", "metric_code": "memory_gb",
             "quantity": 200, "unit": "GiB", "billing_model": "reserved"},
            {"entry_id": "e003", "cluster_id": "c01", "cluster_name": "ads-ranking",
             "resource_name": "data-block", "resource_family": "storage", "metric_code": "block_storage_gb",
             "quantity": 500, "unit": "GiB", "billing_model": "monthly"},
            {"entry_id": "e004", "cluster_id": "c01", "cluster_name": "ads-ranking",
             "resource_name": "data-obj", "resource_family": "storage", "metric_code": "object_storage_gb",
             "quantity": 1000, "unit": "GiB", "billing_model": "monthly"},
            # Business cluster c02 – lakehouse-analytics
            {"entry_id": "e005", "cluster_id": "c02", "cluster_name": "lakehouse-analytics",
             "resource_name": "gpu-node", "resource_family": "compute", "metric_code": "gpu",
             "quantity": 8, "unit": "gpu", "billing_model": "reserved"},
            {"entry_id": "e006", "cluster_id": "c02", "cluster_name": "lakehouse-analytics",
             "resource_name": "analytics-cpu", "resource_family": "compute", "metric_code": "vcpu",
             "quantity": 300, "unit": "vcpu", "billing_model": "autoscale"},
            {"entry_id": "e007", "cluster_id": "c02", "cluster_name": "lakehouse-analytics",
             "resource_name": "analytics-mem", "resource_family": "compute", "metric_code": "memory_gb",
             "quantity": 1000, "unit": "GiB", "billing_model": "autoscale"},
            {"entry_id": "e008", "cluster_id": "c02", "cluster_name": "lakehouse-analytics",
             "resource_name": "lake-storage", "resource_family": "storage", "metric_code": "object_storage_gb",
             "quantity": 5000, "unit": "GiB", "billing_model": "monthly"},
            # Distractors: shared_platform clusters
            {"entry_id": "e009", "cluster_id": "c03", "cluster_name": "retail-core",
             "resource_name": "order-cpu", "resource_family": "compute", "metric_code": "vcpu",
             "quantity": 200, "unit": "vcpu", "billing_model": "reserved"},
            {"entry_id": "e010", "cluster_id": "c03", "cluster_name": "retail-core",
             "resource_name": "order-mem", "resource_family": "compute", "metric_code": "memory_gb",
             "quantity": 500, "unit": "GiB", "billing_model": "reserved"},
            {"entry_id": "e011", "cluster_id": "c03", "cluster_name": "retail-core",
             "resource_name": "order-db", "resource_family": "storage", "metric_code": "block_storage_gb",
             "quantity": 2000, "unit": "GiB", "billing_model": "monthly"},
            {"entry_id": "e012", "cluster_id": "c04", "cluster_name": "shared-ops",
             "resource_name": "ci-agent", "resource_family": "compute", "metric_code": "vcpu",
             "quantity": 50, "unit": "vcpu", "billing_model": "autoscale"},
            {"entry_id": "e013", "cluster_id": "c04", "cluster_name": "shared-ops",
             "resource_name": "ci-cache", "resource_family": "storage", "metric_code": "object_storage_gb",
             "quantity": 200, "unit": "GiB", "billing_model": "monthly"},
            # Extra distractors: archived entries (same cluster but duplicated? just extra)
            {"entry_id": "e014", "cluster_id": "c04", "cluster_name": "shared-ops",
             "resource_name": "backup-storage", "resource_family": "storage", "metric_code": "block_storage_gb",
             "quantity": 100, "unit": "GiB", "billing_model": "monthly"}
        ]
    }
    with open("data/resources/resource_ledger.json", "w") as f:
        json.dump(resource_ledger, f, indent=2)

    # ---- Pricing Catalogs (2 versions) ----
    pricing_catalogs = {
        "pricing_catalogs": [
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
                    {"resource_family": "compute", "metric_code": "vcpu", "rate": 0.10},
                    {"resource_family": "compute", "metric_code": "gpu", "rate": 1.50},
                    {"resource_family": "compute", "metric_code": "memory_gb", "rate": 0.05},
                    {"resource_family": "storage", "metric_code": "block_storage_gb", "rate": 0.08},
                    {"resource_family": "storage", "metric_code": "object_storage_gb", "rate": 0.02}
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
                    {"resource_family": "compute", "metric_code": "vcpu", "rate": 0.08},
                    {"resource_family": "compute", "metric_code": "gpu", "rate": 1.20},
                    {"resource_family": "compute", "metric_code": "memory_gb", "rate": 0.04},
                    {"resource_family": "storage", "metric_code": "block_storage_gb", "rate": 0.10},
                    {"resource_family": "storage", "metric_code": "object_storage_gb", "rate": 0.03}
                ]
            }
        ]
    }
    with open("data/pricing/pricing_catalogs.json", "w") as f:
        json.dump(pricing_catalogs, f, indent=2)

    # Optional: a dummy file to add noise
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": [{"account_id": "acc_dummy", "display_name": "Ignore me"}]}, f, indent=2)


if __name__ == "__main__":
    build_env()
