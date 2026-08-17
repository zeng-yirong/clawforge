import os
import json
import random

random.seed(42)

def build_env():
    # Ensure directory structure
    os.makedirs("data/resources", exist_ok=True)
    os.makedirs("data/pricing", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    # --- clusters.json ---
    clusters = [
        {"cluster_id": "c-ads", "cluster_name": "ads-ranking", "cluster_role": "business", "domain": "marketing", "environment": "prod", "region": "us-east-1", "owner_team": "Growth Engineering", "service_tier": "tier_1", "workload_tags": ["ads", "inference"], "business_service": "Ads ranking and campaign inference"},
        {"cluster_id": "c-lake", "cluster_name": "lakehouse-analytics", "cluster_role": "business", "domain": "data", "environment": "prod", "region": "us-west-2", "owner_team": "Data Platform", "service_tier": "tier_1", "workload_tags": ["analytics", "finance"], "business_service": "Lakehouse analytics and finance marts"},
        {"cluster_id": "c-retail", "cluster_name": "retail-core", "cluster_role": "business", "domain": "commerce", "environment": "prod", "region": "eu-west-1", "owner_team": "Commerce Platform", "service_tier": "tier_2", "workload_tags": ["storefront", "orders"], "business_service": "Storefront and order orchestration"},
        {"cluster_id": "c-shared", "cluster_name": "shared-ops", "cluster_role": "shared_platform", "domain": "infrastructure", "environment": "prod", "region": "us-east-1", "owner_team": "Cloud Foundations", "service_tier": "tier_2", "workload_tags": ["ci", "tooling"], "business_service": "Shared CI and platform tooling"}
    ]
    with open("data/resources/clusters.json", "w") as f:
        json.dump({"clusters": clusters}, f, indent=2)

    # --- resource_ledger.json ---
    # business cluster IDs
    biz_clusters = ["c-ads", "c-lake", "c-retail"]
    # define entries per cluster: (resource_name, resource_family, metric_code, quantity, unit, billing_model)
    entries = []
    entry_id = 0
    def add_entry(cluster_id, cluster_name, resource_name, family, metric, qty, unit, billing):
        nonlocal entry_id
        entries.append({
            "entry_id": f"e-{entry_id:04d}",
            "cluster_id": cluster_id,
            "cluster_name": cluster_name,
            "resource_name": resource_name,
            "resource_family": family,
            "metric_code": metric,
            "quantity": qty,
            "unit": unit,
            "billing_model": billing
        })
        entry_id += 1

    # ads-ranking
    add_entry("c-ads", "ads-ranking", "ads-vcpu-pool", "compute", "vcpu", 120, "vcpu", "monthly")
    add_entry("c-ads", "ads-ranking", "ads-memory-pool", "compute", "memory_gb", 512, "GiB", "monthly")
    add_entry("c-ads", "ads-ranking", "ads-block-store", "storage", "block_storage_gb", 2000, "GiB", "monthly")
    # lakehouse-analytics
    add_entry("c-lake", "lakehouse-analytics", "lake-vcpu-pool", "compute", "vcpu", 80, "vcpu", "reserved")
    add_entry("c-lake", "lakehouse-analytics", "lake-memory-pool", "compute", "memory_gb", 384, "GiB", "reserved")
    add_entry("c-lake", "lakehouse-analytics", "lake-object-store", "storage", "object_storage_gb", 5000, "GiB", "autoscale")
    # retail-core
    add_entry("c-retail", "retail-core", "retail-vcpu-pool", "compute", "vcpu", 200, "vcpu", "monthly")
    add_entry("c-retail", "retail-core", "retail-memory-pool", "compute", "memory_gb", 1024, "GiB", "monthly")
    add_entry("c-retail", "retail-core", "retail-block-store", "storage", "block_storage_gb", 4000, "GiB", "monthly")
    # --- dirty records ---
    # 1) entry belonging to shared-ops (should be excluded)
    add_entry("c-shared", "shared-ops", "shared-vcpu", "compute", "vcpu", 16, "vcpu", "monthly")
    # 2) entry with nonexistent cluster_id (should be excluded)
    add_entry("c-ghost", "ghost-cluster", "ghost-vcpu", "compute", "vcpu", 100, "vcpu", "reserved")

    with open("data/resources/resource_ledger.json", "w") as f:
        json.dump({"resource_ledger": entries}, f, indent=2)

    # --- pricing_catalogs.json ---
    catalogs = [
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
                {"resource_family": "compute", "metric_code": "vcpu", "unit_price": 0.042},
                {"resource_family": "compute", "metric_code": "memory_gb", "unit_price": 0.008},
                {"resource_family": "storage", "metric_code": "block_storage_gb", "unit_price": 0.10},
                {"resource_family": "storage", "metric_code": "object_storage_gb", "unit_price": 0.02}
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
                {"resource_family": "compute", "metric_code": "vcpu", "unit_price": 0.045},
                {"resource_family": "compute", "metric_code": "memory_gb", "unit_price": 0.009},
                {"resource_family": "storage", "metric_code": "block_storage_gb", "unit_price": 0.12},
                {"resource_family": "storage", "metric_code": "object_storage_gb", "unit_price": 0.025}
            ]
        }
    ]
    with open("data/pricing/pricing_catalogs.json", "w") as f:
        json.dump({"pricing_catalogs": catalogs}, f, indent=2)

if __name__ == "__main__":
    build_env()
