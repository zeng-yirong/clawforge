import os
import json

def build_env():
    # Ensure directories exist
    os.makedirs("data/resources", exist_ok=True)
    os.makedirs("data/pricing", exist_ok=True)
    os.makedirs("output", exist_ok=True)  # empty, agent will place result here

    # clusters.json
    clusters = {
        "clusters": [
            {
                "cluster_id": "cluster_ads",
                "cluster_name": "ads-ranking",
                "business_service": "Ads ranking and campaign inference",
                "domain": "marketing",
                "environment": "production",
                "region": "us-east-1",
                "owner_team": "Growth Engineering",
                "cluster_role": "business",
                "service_tier": "tier_1",
                "workload_tags": ["ads", "ml"]
            },
            {
                "cluster_id": "cluster_lake",
                "cluster_name": "lakehouse-analytics",
                "business_service": "Lakehouse analytics and finance marts",
                "domain": "data",
                "region": "us-east-1",
                "owner_team": "Data Platform",
                "cluster_role": "business",
                "service_tier": "tier_2",
                "workload_tags": ["analytics", "data"]
            },
            {
                "cluster_id": "cluster_shared",
                "cluster_name": "shared-ops",
                "business_service": "Shared CI and platform tooling",
                "domain": "infrastructure",
                "region": "eu-west-1",
                "owner_team": "Cloud Foundations",
                "cluster_role": "shared_platform",
                "service_tier": "tier_2",
                "workload_tags": ["ci", "tools"]
            }
        ]
    }
    with open("data/resources/clusters.json", "w") as f:
        json.dump(clusters, f, indent=2)

    # pricing_catalogs.json
    pricing_catalogs = {
        "pricing_catalogs": [
            {
                "catalog_id": "cat_2026_03",
                "version": "2026.03-archive",
                "status": "archived",
                "region": "us-east-1",
                "currency": "USD",
                "billing_month": "2026-03",
                "billing_hours": 744,
                "approved_for_reporting": True,
                "effective_from": "2026-03-01",
                "effective_to": "2026-03-31",
                "rates": [
                    {"metric_code": "vcpu", "unit_price": 0.10},
                    {"metric_code": "memory_gb", "unit_price": 0.015},
                    {"metric_code": "gpu", "unit_price": 0.60},
                    {"metric_code": "block_storage_gb", "unit_price": 0.12},
                    {"metric_code": "object_storage_gb", "unit_price": 0.025}
                ]
            },
            {
                "catalog_id": "cat_2026_06",
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
                    {"metric_code": "vcpu", "unit_price": 0.08},
                    {"metric_code": "memory_gb", "unit_price": 0.01},
                    {"metric_code": "gpu", "unit_price": 0.50},
                    {"metric_code": "block_storage_gb", "unit_price": 0.10},
                    {"metric_code": "object_storage_gb", "unit_price": 0.02}
                ]
            },
            {
                "catalog_id": "cat_2026_06_eu",
                "version": "2026.06-live",
                "status": "active",
                "region": "eu-west-1",
                "currency": "USD",
                "billing_month": "2026-06",
                "billing_hours": 720,
                "approved_for_reporting": False,
                "effective_from": "2026-06-01",
                "effective_to": "2026-06-30",
                "rates": [
                    {"metric_code": "vcpu", "unit_price": 0.09},
                    {"metric_code": "memory_gb", "unit_price": 0.012},
                    {"metric_code": "gpu", "unit_price": 0.55},
                    {"metric_code": "block_storage_gb", "unit_price": 0.11},
                    {"metric_code": "object_storage_gb", "unit_price": 0.025}
                ]
            }
        ]
    }
    with open("data/pricing/pricing_catalogs.json", "w") as f:
        json.dump(pricing_catalogs, f, indent=2)

    # resource_ledger.json
    resource_ledger = {
        "resource_ledger": [
            # correct entries for ads-ranking
            {"entry_id": "e001", "cluster_id": "cluster_ads", "cluster_name": "ads-ranking", "resource_name": "compute-node-a", "resource_family": "compute", "metric_code": "vcpu", "quantity": 100, "unit": "vcpu", "billing_model": "monthly"},
            {"entry_id": "e002", "cluster_id": "cluster_ads", "cluster_name": "ads-ranking", "resource_name": "compute-node-a", "resource_family": "compute", "metric_code": "memory_gb", "quantity": 200, "unit": "GiB", "billing_model": "monthly"},
            {"entry_id": "e003", "cluster_id": "cluster_ads", "cluster_name": "ads-ranking", "resource_name": "gpu-node-b", "resource_family": "compute", "metric_code": "gpu", "quantity": 4, "unit": "gpu", "billing_model": "reserved"},
            {"entry_id": "e004", "cluster_id": "cluster_ads", "cluster_name": "ads-ranking", "resource_name": "storage-pool-1", "resource_family": "storage", "metric_code": "block_storage_gb", "quantity": 500, "unit": "GiB", "billing_model": "monthly"},
            {"entry_id": "e005", "cluster_id": "cluster_ads", "cluster_name": "ads-ranking", "resource_name": "storage-pool-2", "resource_family": "storage", "metric_code": "object_storage_gb", "quantity": 1000, "unit": "GiB", "billing_model": "monthly"},
            # decoy entries from other clusters
            {"entry_id": "e010", "cluster_id": "cluster_lake", "cluster_name": "lakehouse-analytics", "resource_name": "compute-node-x", "resource_family": "compute", "metric_code": "vcpu", "quantity": 50, "unit": "vcpu", "billing_model": "autoscale"},
            {"entry_id": "e011", "cluster_id": "cluster_lake", "cluster_name": "lakehouse-analytics", "resource_name": "storage-lake", "resource_family": "storage", "metric_code": "object_storage_gb", "quantity": 2000, "unit": "GiB", "billing_model": "monthly"},
            {"entry_id": "e020", "cluster_id": "cluster_shared", "cluster_name": "shared-ops", "resource_name": "shared-ci", "resource_family": "compute", "metric_code": "vcpu", "quantity": 20, "unit": "vcpu", "billing_model": "monthly"},
            # decoy entries with zero or negative quantity
            {"entry_id": "e030", "cluster_id": "cluster_ads", "cluster_name": "ads-ranking", "resource_name": "unused-resource", "resource_family": "compute", "metric_code": "memory_gb", "quantity": 0, "unit": "GiB", "billing_model": "monthly"},
            {"entry_id": "e031", "cluster_id": "cluster_ads", "cluster_name": "ads-ranking", "resource_name": "overdraw", "resource_family": "compute", "metric_code": "vcpu", "quantity": -10, "unit": "vcpu", "billing_model": "monthly"},
            # decoy entry with unknown metric_code
            {"entry_id": "e040", "cluster_id": "cluster_ads", "cluster_name": "ads-ranking", "resource_name": "custom-metric", "resource_family": "compute", "metric_code": "custom_metric", "quantity": 5, "unit": "units", "billing_model": "monthly"}
        ]
    }
    with open("data/resources/resource_ledger.json", "w") as f:
        json.dump(resource_ledger, f, indent=2)

if __name__ == "__main__":
    build_env()
