import os
import json
import random
import shutil

def build_env():
    # Create directory structure
    os.makedirs("data", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    # --- Clusters ---
    clusters = [
        {
            "cluster_id": "c001",
            "cluster_name": "ads-ranking",
            "business_service": "Ads ranking and campaign inference",
            "domain": "marketing",
            "environment": "production",
            "region": "us-east-1",
            "owner_team": "Growth Engineering",
            "cluster_role": "business",
            "service_tier": "tier_1",
            "workload_tags": ["ads", "ranking"]
        },
        {
            "cluster_id": "c002",
            "cluster_name": "lakehouse-analytics",
            "business_service": "Lakehouse analytics and finance marts",
            "domain": "data",
            "environment": "production",
            "region": "us-west-2",
            "owner_team": "Data Platform",
            "cluster_role": "business",
            "service_tier": "tier_1",
            "workload_tags": ["lakehouse", "analytics"]
        },
        {
            "cluster_id": "c003",
            "cluster_name": "retail-core",
            "business_service": "Storefront and order orchestration",
            "domain": "commerce",
            "environment": "production",
            "region": "eu-central-1",
            "owner_team": "Commerce Platform",
            "cluster_role": "business",
            "service_tier": "tier_1",
            "workload_tags": ["storefront", "orders"]
        },
        {
            "cluster_id": "c004",
            "cluster_name": "shared-ops",
            "business_service": "Shared CI and platform tooling",
            "domain": "infrastructure",
            "environment": "production",
            "region": "us-east-1",
            "owner_team": "Cloud Foundations",
            "cluster_role": "shared_platform",
            "service_tier": "tier_2",
            "workload_tags": ["ci", "platform"]
        }
    ]

    with open("data/clusters.json", "w") as f:
        json.dump({"clusters": clusters}, f, indent=2)

    # --- Pricing Catalogs ---
    # Active June 2026 catalog
    june_rates = [
        {"resource_family": "compute", "metric_code": "vcpu", "unit_price": 0.042},
        {"resource_family": "compute", "metric_code": "gpu", "unit_price": 0.80},
        {"resource_family": "compute", "metric_code": "memory_gb", "unit_price": 0.015},
        {"resource_family": "storage", "metric_code": "block_storage_gb", "unit_price": 0.10},
        {"resource_family": "storage", "metric_code": "object_storage_gb", "unit_price": 0.02}
    ]
    march_rates = [
        {"resource_family": "compute", "metric_code": "vcpu", "unit_price": 0.038},
        {"resource_family": "compute", "metric_code": "gpu", "unit_price": 0.75},
        {"resource_family": "compute", "metric_code": "memory_gb", "unit_price": 0.012},
        {"resource_family": "storage", "metric_code": "block_storage_gb", "unit_price": 0.09},
        {"resource_family": "storage", "metric_code": "object_storage_gb", "unit_price": 0.018}
    ]

    catalogs = [
        {
            "catalog_id": "cat_2026_03_archive",
            "version": "2026.03-archive",
            "status": "archived",
            "region": "all",
            "currency": "USD",
            "billing_month": "2026-03",
            "billing_hours": 744,
            "approved_for_reporting": False,
            "effective_from": "2026-03-01",
            "effective_to": "2026-03-31",
            "rates": march_rates
        },
        {
            "catalog_id": "cat_2026_06_live",
            "version": "2026.06-live",
            "status": "active",
            "region": "all",
            "currency": "USD",
            "billing_month": "2026-06",
            "billing_hours": 720,
            "approved_for_reporting": True,
            "effective_from": "2026-06-01",
            "effective_to": "2026-06-30",
            "rates": june_rates
        }
    ]

    with open("data/pricing_catalogs.json", "w") as f:
        json.dump({"pricing_catalogs": catalogs}, f, indent=2)

    # --- Resource Ledger (with deliberate traps) ---
    # Real entries for business clusters + shared + noise
    ledger = [
        # ads-ranking
        {"entry_id": "e001", "cluster_id": "c001", "cluster_name": "ads-ranking", "resource_name": "ads-vcpu-pool", "resource_family": "compute", "metric_code": "vcpu", "quantity": 120, "unit": "vcpu", "billing_model": "reserved"},
        {"entry_id": "e002", "cluster_id": "c001", "cluster_name": "ads-ranking", "resource_name": "ads-memory-pool", "resource_family": "compute", "metric_code": "memory_gb", "quantity": 480, "unit": "GiB", "billing_model": "reserved"},
        {"entry_id": "e003", "cluster_id": "c001", "cluster_name": "ads-ranking", "resource_name": "ads-block-store", "resource_family": "storage", "metric_code": "block_storage_gb", "quantity": 2000, "unit": "GiB", "billing_model": "monthly"},
        # lakehouse-analytics
        {"entry_id": "e004", "cluster_id": "c002", "cluster_name": "lakehouse-analytics", "resource_name": "lake-gpu-nodes", "resource_family": "compute", "metric_code": "gpu", "quantity": 16, "unit": "gpu", "billing_model": "autoscale"},
        {"entry_id": "e005", "cluster_id": "c002", "cluster_name": "lakehouse-analytics", "resource_name": "lake-vcpu-pool", "resource_family": "compute", "metric_code": "vcpu", "quantity": 320, "unit": "vcpu", "billing_model": "reserved"},
        {"entry_id": "e006", "cluster_id": "c002", "cluster_name": "lakehouse-analytics", "resource_name": "lake-memory-pool", "resource_family": "compute", "metric_code": "memory_gb", "quantity": 2048, "unit": "GiB", "billing_model": "reserved"},
        {"entry_id": "e007", "cluster_id": "c002", "cluster_name": "lakehouse-analytics", "resource_name": "lake-object-store", "resource_family": "storage", "metric_code": "object_storage_gb", "quantity": 15000, "unit": "GiB", "billing_model": "monthly"},
        # retail-core
        {"entry_id": "e008", "cluster_id": "c003", "cluster_name": "retail-core", "resource_name": "retail-vcpu-pool", "resource_family": "compute", "metric_code": "vcpu", "quantity": 80, "unit": "vcpu", "billing_model": "reserved"},
        {"entry_id": "e009", "cluster_id": "c003", "cluster_name": "retail-core", "resource_name": "retail-memory-pool", "resource_family": "compute", "metric_code": "memory_gb", "quantity": 320, "unit": "GiB", "billing_model": "reserved"},
        {"entry_id": "e010", "cluster_id": "c003", "cluster_name": "retail-core", "resource_name": "retail-block-store", "resource_family": "storage", "metric_code": "block_storage_gb", "quantity": 5000, "unit": "GiB", "billing_model": "monthly"},
        # shared-ops (should be excluded)
        {"entry_id": "e011", "cluster_id": "c004", "cluster_name": "shared-ops", "resource_name": "shared-vcpu-pool", "resource_family": "compute", "metric_code": "vcpu", "quantity": 40, "unit": "vcpu", "billing_model": "monthly"},
        {"entry_id": "e012", "cluster_id": "c004", "cluster_name": "shared-ops", "resource_name": "shared-block-store", "resource_family": "storage", "metric_code": "block_storage_gb", "quantity": 3000, "unit": "GiB", "billing_model": "monthly"},
        # Noise / traps
        # stale entry referencing a deleted cluster (no match in clusters.json)
        {"entry_id": "e013", "cluster_id": "c099", "cluster_name": "ghost-cluster", "resource_name": "phantom-vcpu", "resource_family": "compute", "metric_code": "vcpu", "quantity": 50, "unit": "vcpu", "billing_model": "reserved"},
        # duplicate? JSON allows but will overwrite – instead add a wrong metric code that doesn't exist in catalog
        {"entry_id": "e014", "cluster_id": "c002", "cluster_name": "lakehouse-analytics", "resource_name": "lake-unknown", "resource_family": "storage", "metric_code": "tape_storage_gb", "quantity": 100, "unit": "GiB", "billing_model": "monthly"},
        # zero quantity (should be included? we'll keep it – price * 0 = 0, no harm)
        {"entry_id": "e015", "cluster_id": "c001", "cluster_name": "ads-ranking", "resource_name": "ads-idle-gpu", "resource_family": "compute", "metric_code": "gpu", "quantity": 0, "unit": "gpu", "billing_model": "autoscale"},
    ]

    with open("data/resource_ledger.json", "w") as f:
        json.dump({"resource_ledger": ledger}, f, indent=2)

    # Additional distracting files
    open("data/accounts.json", "w").write("{}")
    open("data/contacts.json", "w").write("{}")
    open("data/attachments.json", "w").write("{}")

    # Pre-create an empty reports directory (already done)

if __name__ == "__main__":
    build_env()
