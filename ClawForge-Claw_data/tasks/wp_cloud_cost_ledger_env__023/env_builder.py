import os
import json

def build_env():
    # 创建必要的目录
    os.makedirs("data/pricing", exist_ok=True)
    os.makedirs("data/resources", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    # ---------- clusters.json ----------
    clusters = {
        "clusters": [
            {
                "cluster_id": "cluster-001",
                "cluster_name": "ads-ranking",
                "business_service": "Ads ranking and campaign inference",
                "domain": "marketing",
                "environment": "prod",
                "region": "us-east-1",
                "owner_team": "Growth Engineering",
                "cluster_role": "business",
                "service_tier": "tier_1",
                "workload_tags": ["ad-serving", "ml-inference"]
            },
            {
                "cluster_id": "cluster-002",
                "cluster_name": "lakehouse-analytics",
                "business_service": "Lakehouse analytics and finance marts",
                "domain": "data",
                "environment": "prod",
                "region": "us-west-2",
                "owner_team": "Data Platform",
                "cluster_role": "business",
                "service_tier": "tier_1",
                "workload_tags": ["spark", "etl"]
            },
            {
                "cluster_id": "cluster-003",
                "cluster_name": "shared-ops",
                "business_service": "Shared CI and platform tooling",
                "domain": "infrastructure",
                "environment": "prod",
                "region": "eu-west-1",
                "owner_team": "Cloud Foundations",
                "cluster_role": "shared_platform",
                "service_tier": "tier_2",
                "workload_tags": ["ci-cd", "monitoring"]
            }
        ]
    }
    with open("data/resources/clusters.json", "w") as f:
        json.dump(clusters, f, indent=2)

    # ---------- resource_ledger.json ----------
    resource_ledger = {
        "resource_ledger": [
            # ads-ranking
            {"entry_id": "entry-001", "cluster_id": "cluster-001", "cluster_name": "ads-ranking",
             "resource_name": "compute-vcpu", "resource_family": "compute", "metric_code": "vcpu",
             "quantity": 100, "unit": "vcpu", "billing_model": "monthly"},
            {"entry_id": "entry-002", "cluster_id": "cluster-001", "cluster_name": "ads-ranking",
             "resource_name": "compute-memory", "resource_family": "compute", "metric_code": "memory_gb",
             "quantity": 200, "unit": "GiB", "billing_model": "monthly"},
            {"entry_id": "entry-003", "cluster_id": "cluster-001", "cluster_name": "ads-ranking",
             "resource_name": "block-storage", "resource_family": "storage", "metric_code": "block_storage_gb",
             "quantity": 500, "unit": "GiB", "billing_model": "monthly"},
            # lakehouse-analytics
            {"entry_id": "entry-004", "cluster_id": "cluster-002", "cluster_name": "lakehouse-analytics",
             "resource_name": "compute-vcpu", "resource_family": "compute", "metric_code": "vcpu",
             "quantity": 150, "unit": "vcpu", "billing_model": "monthly"},
            {"entry_id": "entry-005", "cluster_id": "cluster-002", "cluster_name": "lakehouse-analytics",
             "resource_name": "gpu", "resource_family": "compute", "metric_code": "gpu",
             "quantity": 10, "unit": "gpu", "billing_model": "monthly"},
            {"entry_id": "entry-006", "cluster_id": "cluster-002", "cluster_name": "lakehouse-analytics",
             "resource_name": "object-storage", "resource_family": "storage", "metric_code": "object_storage_gb",
             "quantity": 1000, "unit": "GiB", "billing_model": "monthly"},
            # shared-ops (干扰)
            {"entry_id": "entry-007", "cluster_id": "cluster-003", "cluster_name": "shared-ops",
             "resource_name": "compute-vcpu", "resource_family": "compute", "metric_code": "vcpu",
             "quantity": 20, "unit": "vcpu", "billing_model": "monthly"},
            {"entry_id": "entry-008", "cluster_id": "cluster-003", "cluster_name": "shared-ops",
             "resource_name": "block-storage", "resource_family": "storage", "metric_code": "block_storage_gb",
             "quantity": 100, "unit": "GiB", "billing_model": "monthly"}
        ]
    }
    with open("data/resources/resource_ledger.json", "w") as f:
        json.dump(resource_ledger, f, indent=2)

    # ---------- pricing_catalogs.json ----------
    pricing_catalogs = {
        "pricing_catalogs": [
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
                "effective_to": "2026-04-01",
                "rates": [
                    {"resource_family": "compute", "metric_code": "vcpu", "unit_price": 0.06},
                    {"resource_family": "compute", "metric_code": "memory_gb", "unit_price": 0.015},
                    {"resource_family": "storage", "metric_code": "block_storage_gb", "unit_price": 0.08}
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
                "effective_to": "2026-07-01",
                "rates": [
                    {"resource_family": "compute", "metric_code": "vcpu", "unit_price": 0.08},
                    {"resource_family": "compute", "metric_code": "memory_gb", "unit_price": 0.02},
                    {"resource_family": "compute", "metric_code": "gpu", "unit_price": 0.50},
                    {"resource_family": "storage", "metric_code": "block_storage_gb", "unit_price": 0.10},
                    {"resource_family": "storage", "metric_code": "object_storage_gb", "unit_price": 0.05}
                ]
            }
        ]
    }
    with open("data/pricing/pricing_catalogs.json", "w") as f:
        json.dump(pricing_catalogs, f, indent=2)

    # 干扰文本文件
    with open("data/notes.txt", "w") as f:
        f.write("Remember to use the active pricing catalog for reporting.\n")

if __name__ == "__main__":
    build_env()
