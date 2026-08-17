import json
import os
import random

def build_env():
    # ------------------------------------------------------------------
    # 1. Clusters
    # ------------------------------------------------------------------
    clusters = [
        {
            "cluster_id": "cluster-ads-001",
            "cluster_name": "ads-ranking",
            "business_service": "Ads ranking and campaign inference",
            "domain": "marketing",
            "environment": "production",
            "region": "us-east-1",
            "owner_team": "Growth Engineering",
            "cluster_role": "business",
            "service_tier": "tier_1",
            "workload_tags": ["ads", "inference", "production"]
        },
        {
            "cluster_id": "cluster-lake-002",
            "cluster_name": "lakehouse-analytics",
            "business_service": "Lakehouse analytics and finance marts",
            "domain": "data",
            "environment": "production",
            "region": "eu-west-1",
            "owner_team": "Data Platform",
            "cluster_role": "business",
            "service_tier": "tier_2",
            "workload_tags": ["analytics", "spark"]
        },
        {
            "cluster_id": "cluster-retail-003",
            "cluster_name": "retail-core",
            "business_service": "Storefront and order orchestration",
            "domain": "commerce",
            "environment": "production",
            "region": "us-west-2",
            "owner_team": "Commerce Platform",
            "cluster_role": "business",
            "service_tier": "tier_1",
            "workload_tags": ["storefront", "orders"]
        },
        {
            "cluster_id": "cluster-shared-004",
            "cluster_name": "shared-ops",
            "business_service": "Shared CI and platform tooling",
            "domain": "infrastructure",
            "environment": "staging",
            "region": "us-east-1",
            "owner_team": "Cloud Foundations",
            "cluster_role": "shared_platform",
            "service_tier": "tier_2",
            "workload_tags": ["ci", "tooling"]
        }
    ]
    with open("clusters.json", "w") as f:
        json.dump({"clusters": clusters}, f, indent=2)

    # ------------------------------------------------------------------
    # 2. Resource ledger – many records, including dirt, for all clusters
    # ------------------------------------------------------------------
    ads_entries = [
        # clean records
        {"entry_id": "entry-ads-vcpu-01", "cluster_id": "cluster-ads-001", "cluster_name": "ads-ranking",
         "resource_name": "ml-inference-pool", "resource_family": "compute", "metric_code": "vcpu",
         "quantity": 50, "unit": "vcpu", "billing_model": "reserved"},
        {"entry_id": "entry-ads-mem-01", "cluster_id": "cluster-ads-001", "cluster_name": "ads-ranking",
         "resource_name": "ml-inference-pool", "resource_family": "compute", "metric_code": "memory_gb",
         "quantity": 200, "unit": "GiB", "billing_model": "reserved"},
        {"entry_id": "entry-ads-gpu-01", "cluster_id": "cluster-ads-001", "cluster_name": "ads-ranking",
         "resource_name": "training-node", "resource_family": "compute", "metric_code": "gpu",
         "quantity": 4, "unit": "gpu", "billing_model": "monthly"},
        {"entry_id": "entry-ads-block-01", "cluster_id": "cluster-ads-001", "cluster_name": "ads-ranking",
         "resource_name": "model-storage", "resource_family": "storage", "metric_code": "block_storage_gb",
         "quantity": 1000, "unit": "GiB", "billing_model": "monthly"},
        {"entry_id": "entry-ads-obj-01", "cluster_id": "cluster-ads-001", "cluster_name": "ads-ranking",
         "resource_name": "training-data", "resource_family": "storage", "metric_code": "object_storage_gb",
         "quantity": 500, "unit": "GiB", "billing_model": "monthly"},
        # dirty records (should be excluded)
        {"entry_id": "entry-ads-vcpu-dirty-zero", "cluster_id": "cluster-ads-001", "cluster_name": "ads-ranking",
         "resource_name": "test-pool", "resource_family": "compute", "metric_code": "vcpu",
         "quantity": 0, "unit": "vcpu", "billing_model": "autoscale"},  # zero quantity
        {"entry_id": "entry-ads-block-dirty-unit", "cluster_id": "cluster-ads-001", "cluster_name": "ads-ranking",
         "resource_name": "test-storage", "resource_family": "storage", "metric_code": "block_storage_gb",
         "quantity": 100, "unit": "GB", "billing_model": "monthly"},  # wrong unit "GB" instead of "GiB"
    ]

    # other clusters (non-ads) – clean records to distract
    lake_entries = [
        {"entry_id": "entry-lake-vcpu-01", "cluster_id": "cluster-lake-002", "cluster_name": "lakehouse-analytics",
         "resource_name": "spark-executor", "resource_family": "compute", "metric_code": "vcpu",
         "quantity": 80, "unit": "vcpu", "billing_model": "autoscale"},
        {"entry_id": "entry-lake-mem-01", "cluster_id": "cluster-lake-002", "cluster_name": "lakehouse-analytics",
         "resource_name": "spark-executor", "resource_family": "compute", "metric_code": "memory_gb",
         "quantity": 320, "unit": "GiB", "billing_model": "autoscale"},
        {"entry_id": "entry-lake-block-01", "cluster_id": "cluster-lake-002", "cluster_name": "lakehouse-analytics",
         "resource_name": "data-lake", "resource_family": "storage", "metric_code": "block_storage_gb",
         "quantity": 3000, "unit": "GiB", "billing_model": "monthly"},
    ]
    retail_entries = [
        {"entry_id": "entry-retail-vcpu-01", "cluster_id": "cluster-retail-003", "cluster_name": "retail-core",
         "resource_name": "web-server", "resource_family": "compute", "metric_code": "vcpu",
         "quantity": 30, "unit": "vcpu", "billing_model": "reserved"},
        {"entry_id": "entry-retail-mem-01", "cluster_id": "cluster-retail-003", "cluster_name": "retail-core",
         "resource_name": "web-server", "resource_family": "compute", "metric_code": "memory_gb",
         "quantity": 120, "unit": "GiB", "billing_model": "reserved"},
    ]
    shared_entries = [
        {"entry_id": "entry-shared-vcpu-01", "cluster_id": "cluster-shared-004", "cluster_name": "shared-ops",
         "resource_name": "ci-runner", "resource_family": "compute", "metric_code": "vcpu",
         "quantity": 10, "unit": "vcpu", "billing_model": "autoscale"},
    ]

    resource_ledger = ads_entries + lake_entries + retail_entries + shared_entries
    with open("resource_ledger.json", "w") as f:
        json.dump({"resource_ledger": resource_ledger}, f, indent=2)

    # ------------------------------------------------------------------
    # 3. Pricing catalogs – active June 2026 + archived March 2026
    # ------------------------------------------------------------------
    pricing_catalogs = [
        {
            "catalog_id": "catalog-2026-03",
            "version": "2026.03-archive",
            "status": "archived",
            "region": "us-east-1",
            "currency": "USD",
            "billing_month": "2026-03",
            "billing_hours": 744,
            "approved_for_reporting": False,
            "effective_from": "2026-03-01",
            "effective_to": "2026-03-31",
            "rates": {
                "vcpu": 0.04,
                "memory_gb": 0.008,
                "gpu": 0.45,
                "block_storage_gb": 0.08,
                "object_storage_gb": 0.015
            }
        },
        {
            "catalog_id": "catalog-2026-06",
            "version": "2026.06-live",
            "status": "active",
            "region": "us-east-1",
            "currency": "USD",
            "billing_month": "2026-06",
            "billing_hours": 720,
            "approved_for_reporting": True,
            "effective_from": "2026-06-01",
            "effective_to": "2026-06-30",
            "rates": {
                "vcpu": 0.05,
                "memory_gb": 0.01,
                "gpu": 0.50,
                "block_storage_gb": 0.10,
                "object_storage_gb": 0.02
            }
        }
    ]
    with open("pricing_catalogs.json", "w") as f:
        json.dump({"pricing_catalogs": pricing_catalogs}, f, indent=2)

    # ------------------------------------------------------------------
    # 4. Optional extra files to add realism (not used)
    # ------------------------------------------------------------------
    os.makedirs("logs", exist_ok=True)
    os.makedirs("cost_reports", exist_ok=True)  # agent should create cost_reports if needed, but we ensure dir exists for safety
    # Put a dummy placeholder so agent knows directory exists
    with open("cost_reports/.gitkeep", "w") as f:
        f.write("")

if __name__ == "__main__":
    build_env()
