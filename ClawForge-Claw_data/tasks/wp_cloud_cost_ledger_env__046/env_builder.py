import os
import json
import random

def build_env():
    # 确保目录存在
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/pricing", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # 干扰目录
    os.makedirs("logs", exist_ok=True) # 干扰目录

    # 1. clusters.json
    clusters = [
        {
            "cluster_id": "c-ads-ranking",
            "cluster_name": "ads-ranking",
            "business_service": "Ads ranking and campaign inference",
            "domain": "marketing",
            "environment": "prod",
            "region": "us-east-1",
            "owner_team": "Growth Engineering",
            "cluster_role": "business",
            "service_tier": "tier_1",
            "workload_tags": ["ml", "inference"]
        },
        {
            "cluster_id": "c-lakehouse-analytics",
            "cluster_name": "lakehouse-analytics",
            "business_service": "Lakehouse analytics and finance marts",
            "domain": "data",
            "environment": "prod",
            "region": "us-east-1",
            "owner_team": "Data Platform",
            "cluster_role": "business",
            "service_tier": "tier_1",
            "workload_tags": ["analytics", "spark"]
        },
        {
            "cluster_id": "c-retail-core",
            "cluster_name": "retail-core",
            "business_service": "Storefront and order orchestration",
            "domain": "commerce",
            "environment": "prod",
            "region": "us-west-2",
            "owner_team": "Commerce Platform",
            "cluster_role": "business",
            "service_tier": "tier_1",
            "workload_tags": ["web", "api"]
        },
        {
            "cluster_id": "c-shared-ops",
            "cluster_name": "shared-ops",
            "business_service": "Shared CI and platform tooling",
            "domain": "infrastructure",
            "environment": "prod",
            "region": "eu-west-1",
            "owner_team": "Cloud Foundations",
            "cluster_role": "shared_platform",
            "service_tier": "tier_2",
            "workload_tags": ["ci", "monitoring"]
        }
    ]
    with open("data/clusters.json", "w") as f:
        json.dump({"clusters": clusters}, f, indent=2)

    # 2. pricing_catalogs.json (活跃和存档)
    pricing_catalogs = [
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
                {"resource_family": "compute", "metric_code": "vcpu", "unit_price": 0.08},
                {"resource_family": "compute", "metric_code": "memory_gb", "unit_price": 0.02},
                {"resource_family": "compute", "metric_code": "gpu", "unit_price": 2.00},
                {"resource_family": "storage", "metric_code": "block_storage_gb", "unit_price": 0.15},
                {"resource_family": "storage", "metric_code": "object_storage_gb", "unit_price": 0.04}
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
                {"resource_family": "compute", "metric_code": "vcpu", "unit_price": 0.05},
                {"resource_family": "compute", "metric_code": "memory_gb", "unit_price": 0.01},
                {"resource_family": "compute", "metric_code": "gpu", "unit_price": 1.50},
                {"resource_family": "storage", "metric_code": "block_storage_gb", "unit_price": 0.10},
                {"resource_family": "storage", "metric_code": "object_storage_gb", "unit_price": 0.02}
            ]
        }
    ]
    with open("data/pricing/pricing_catalogs.json", "w") as f:
        json.dump({"pricing_catalogs": pricing_catalogs}, f, indent=2)

    # 3. resource_ledger.json (包含正常、脏数据、非业务集群条目)
    ledger = [
        # ads-ranking 正常条目
        {"entry_id": "e-001", "cluster_id": "c-ads-ranking", "cluster_name": "ads-ranking", "resource_name": "ad-vcpu-pool", "resource_family": "compute", "metric_code": "vcpu", "quantity": 100, "unit": "vcpu", "billing_model": "monthly"},
        {"entry_id": "e-002", "cluster_id": "c-ads-ranking", "cluster_name": "ads-ranking", "resource_name": "ad-memory-pool", "resource_family": "compute", "metric_code": "memory_gb", "quantity": 200, "unit": "GiB", "billing_model": "monthly"},
        {"entry_id": "e-003", "cluster_id": "c-ads-ranking", "cluster_name": "ads-ranking", "resource_name": "ad-gpu-pool", "resource_family": "compute", "metric_code": "gpu", "quantity": 10, "unit": "gpu", "billing_model": "reserved"},
        {"entry_id": "e-004", "cluster_id": "c-ads-ranking", "cluster_name": "ads-ranking", "resource_name": "ad-block-storage", "resource_family": "storage", "metric_code": "block_storage_gb", "quantity": 500, "unit": "GiB", "billing_model": "monthly"},
        # ads-ranking 脏数据：quantity=0
        {"entry_id": "e-005", "cluster_id": "c-ads-ranking", "cluster_name": "ads-ranking", "resource_name": "ad-zero-storage", "resource_family": "storage", "metric_code": "block_storage_gb", "quantity": 0, "unit": "GiB", "billing_model": "monthly"},
        # lakehouse-analytics 正常条目
        {"entry_id": "e-006", "cluster_id": "c-lakehouse-analytics", "cluster_name": "lakehouse-analytics", "resource_name": "lake-vcpu-pool", "resource_family": "compute", "metric_code": "vcpu", "quantity": 80, "unit": "vcpu", "billing_model": "monthly"},
        {"entry_id": "e-007", "cluster_id": "c-lakehouse-analytics", "cluster_name": "lakehouse-analytics", "resource_name": "lake-memory-pool", "resource_family": "compute", "metric_code": "memory_gb", "quantity": 150, "unit": "GiB", "billing_model": "monthly"},
        {"entry_id": "e-008", "cluster_id": "c-lakehouse-analytics", "cluster_name": "lakehouse-analytics", "resource_name": "lake-gpu-pool", "resource_family": "compute", "metric_code": "gpu", "quantity": 5, "unit": "gpu", "billing_model": "reserved"},
        {"entry_id": "e-009", "cluster_id": "c-lakehouse-analytics", "cluster_name": "lakehouse-analytics", "resource_name": "lake-block-storage", "resource_family": "storage", "metric_code": "block_storage_gb", "quantity": 300, "unit": "GiB", "billing_model": "monthly"},
        # lakehouse-analytics 脏数据：quantity=-5
        {"entry_id": "e-010", "cluster_id": "c-lakehouse-analytics", "cluster_name": "lakehouse-analytics", "resource_name": "lake-negative-vcpu", "resource_family": "compute", "metric_code": "vcpu", "quantity": -5, "unit": "vcpu", "billing_model": "monthly"},
        # retail-core 正常条目
        {"entry_id": "e-011", "cluster_id": "c-retail-core", "cluster_name": "retail-core", "resource_name": "retail-vcpu-pool", "resource_family": "compute", "metric_code": "vcpu", "quantity": 120, "unit": "vcpu", "billing_model": "monthly"},
        {"entry_id": "e-012", "cluster_id": "c-retail-core", "cluster_name": "retail-core", "resource_name": "retail-memory-pool", "resource_family": "compute", "metric_code": "memory_gb", "quantity": 250, "unit": "GiB", "billing_model": "monthly"},
        {"entry_id": "e-013", "cluster_id": "c-retail-core", "cluster_name": "retail-core", "resource_name": "retail-block-storage", "resource_family": "storage", "metric_code": "block_storage_gb", "quantity": 200, "unit": "GiB", "billing_model": "monthly"},
        # retail-core 脏数据：缺少 metric_code（设为null）
        {"entry_id": "e-014", "cluster_id": "c-retail-core", "cluster_name": "retail-core", "resource_name": "retail-bad-entry", "resource_family": "compute", "metric_code": None, "quantity": 30, "unit": "vcpu", "billing_model": "monthly"},
        # shared-ops 非业务集群 (不应计入)
        {"entry_id": "e-015", "cluster_id": "c-shared-ops", "cluster_name": "shared-ops", "resource_name": "shared-vcpu-pool", "resource_family": "compute", "metric_code": "vcpu", "quantity": 20, "unit": "vcpu", "billing_model": "monthly"},
        {"entry_id": "e-016", "cluster_id": "c-shared-ops", "cluster_name": "shared-ops", "resource_name": "shared-memory-pool", "resource_family": "compute", "metric_code": "memory_gb", "quantity": 50, "unit": "GiB", "billing_model": "monthly"},
    ]
    with open("data/resource_ledger.json", "w") as f:
        json.dump({"resource_ledger": ledger}, f, indent=2)

    # 4. 干扰文件
    os.makedirs("data/accounts", exist_ok=True)
    with open("data/accounts/some_accounts.json", "w") as f:
        json.dump({"dummy": "data"}, f)
    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": []}, f)
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": []}, f)
    with open("README.md", "w") as f:
        f.write("# Cloud Cost Ledger Environment\nSome docs here...")
    with open("ops/monthly_cost_report_2026_03.json", "w") as f:
        json.dump({"month": "2026-03", "clusters": []}, f)
    print("Environment built successfully.")

if __name__ == "__main__":
    build_env()
