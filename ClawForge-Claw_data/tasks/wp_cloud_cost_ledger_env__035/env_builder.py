import os
import json
from decimal import Decimal

def build_env():
    # Create directory structure
    os.makedirs("data/resources", exist_ok=True)
    os.makedirs("data/pricing", exist_ok=True)
    os.makedirs("attachments", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    # ---------- clusters.json ----------
    clusters = [
        {"cluster_id": "cls-ads-rnk-01", "cluster_name": "ads-ranking", "business_service": "Ads ranking and campaign inference",
         "domain": "marketing", "environment": "production", "region": "us-east-1", "owner_team": "Growth Engineering",
         "cluster_role": "business", "service_tier": "tier_1", "workload_tags": ["ml", "realtime"]},
        {"cluster_id": "cls-lake-an-01", "cluster_name": "lakehouse-analytics", "business_service": "Lakehouse analytics and finance marts",
         "domain": "data", "environment": "production", "region": "us-east-1", "owner_team": "Data Platform",
         "cluster_role": "business", "service_tier": "tier_1", "workload_tags": ["batch", "etl"]},
        {"cluster_id": "cls-retail-c-01", "cluster_name": "retail-core", "business_service": "Storefront and order orchestration",
         "domain": "commerce", "environment": "production", "region": "eu-west-1", "owner_team": "Commerce Platform",
         "cluster_role": "business", "service_tier": "tier_2", "workload_tags": ["web", "api"]},
        {"cluster_id": "cls-shared-01", "cluster_name": "shared-ops", "business_service": "Shared CI and platform tooling",
         "domain": "infrastructure", "environment": "production", "region": "us-west-2", "owner_team": "Cloud Foundations",
         "cluster_role": "shared_platform", "service_tier": "tier_2", "workload_tags": ["ci", "observability"]},
        # 测试集群（干扰）
        {"cluster_id": "cls-test-99", "cluster_name": "test-sandbox", "business_service": "Internal testing",
         "domain": "infrastructure", "environment": "test", "region": "us-east-1", "owner_team": "Cloud Foundations",
         "cluster_role": "test", "service_tier": "tier_3", "workload_tags": ["test"]}
    ]
    with open("data/resources/clusters.json", "w") as f:
        json.dump({"clusters": clusters}, f, indent=2)

    # ---------- resource_ledger.json ----------
    ledger = [
        # ads-ranking
        {"entry_id": "led-001", "cluster_id": "cls-ads-rnk-01", "cluster_name": "ads-ranking", "resource_name": "inference-vcpu",
         "resource_family": "compute", "metric_code": "vcpu", "quantity": 120, "unit": "vcpu", "billing_model": "autoscale"},
        {"entry_id": "led-002", "cluster_id": "cls-ads-rnk-01", "cluster_name": "ads-ranking", "resource_name": "inference-mem",
         "resource_family": "compute", "metric_code": "memory_gb", "quantity": 480, "unit": "GiB", "billing_model": "autoscale"},
        # lakehouse-analytics
        {"entry_id": "led-003", "cluster_id": "cls-lake-an-01", "cluster_name": "lakehouse-analytics", "resource_name": "etl-vcpu",
         "resource_family": "compute", "metric_code": "vcpu", "quantity": 80, "unit": "vcpu", "billing_model": "reserved"},
        {"entry_id": "led-004", "cluster_id": "cls-lake-an-01", "cluster_name": "lakehouse-analytics", "resource_name": "etl-block",
         "resource_family": "storage", "metric_code": "block_storage_gb", "quantity": 2000, "unit": "GiB", "billing_model": "monthly"},
        # retail-core
        {"entry_id": "led-005", "cluster_id": "cls-retail-c-01", "cluster_name": "retail-core", "resource_name": "web-vcpu",
         "resource_family": "compute", "metric_code": "vcpu", "quantity": 64, "unit": "vcpu", "billing_model": "autoscale"},
        {"entry_id": "led-006", "cluster_id": "cls-retail-c-01", "cluster_name": "retail-core", "resource_name": "web-object",
         "resource_family": "storage", "metric_code": "object_storage_gb", "quantity": 15000, "unit": "GiB", "billing_model": "monthly"},
        # shared-ops (shared_platform 不应被纳入)
        {"entry_id": "led-007", "cluster_id": "cls-shared-01", "cluster_name": "shared-ops", "resource_name": "ci-vcpu",
         "resource_family": "compute", "metric_code": "vcpu", "quantity": 32, "unit": "vcpu", "billing_model": "monthly"},
        # 测试集群（干扰）
        {"entry_id": "led-008", "cluster_id": "cls-test-99", "cluster_name": "test-sandbox", "resource_name": "sandbox-vcpu",
         "resource_family": "compute", "metric_code": "vcpu", "quantity": 4, "unit": "vcpu", "billing_model": "monthly"},
        # 重复条目（不同 entry_id，相同 cluster/metric_code/quantity，应累加）
        {"entry_id": "led-009", "cluster_id": "cls-ads-rnk-01", "cluster_name": "ads-ranking", "resource_name": "inference-vcpu-add",
         "resource_family": "compute", "metric_code": "vcpu", "quantity": 30, "unit": "vcpu", "billing_model": "reserved"},
    ]
    with open("data/resources/resource_ledger.json", "w") as f:
        json.dump({"resource_ledger": ledger}, f, indent=2)

    # ---------- pricing_catalogs.json ----------
    pricing_catalogs = [
        {
            "catalog_id": "cat-2026-06",
            "version": "2026.06-live",
            "status": "active",
            "region": "global",
            "currency": "USD",
            "billing_month": "2026-06",
            "billing_hours": 730,
            "approved_for_reporting": True,
            "effective_from": "2026-06-01",
            "effective_to": "2026-06-30",
            "rates": [
                {"metric_code": "vcpu", "rate": 0.0416},
                {"metric_code": "memory_gb", "rate": 0.0093},
                {"metric_code": "block_storage_gb", "rate": 0.10},
                {"metric_code": "object_storage_gb", "rate": 0.02},
                {"metric_code": "gpu", "rate": 1.20}
            ]
        },
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
                {"metric_code": "vcpu", "rate": 0.0380},
                {"metric_code": "memory_gb", "rate": 0.0085},
                {"metric_code": "block_storage_gb", "rate": 0.08},
                {"metric_code": "object_storage_gb", "rate": 0.018},
                {"metric_code": "gpu", "rate": 1.00}
            ]
        }
    ]
    with open("data/pricing/pricing_catalogs.json", "w") as f:
        json.dump({"pricing_catalogs": pricing_catalogs}, f, indent=2)

    # ---------- attachment: report_schema.md ----------
    report_schema = """# Monthly Cost Report Schema

Generate a single JSON file with the following structure:

{
  "report_month": "2026-06",
  "currency": "USD",
  "clusters": [
    {
      "cluster_id": "string",
      "cluster_name": "string",
      "total_cost": number,
      "details": [
        {
          "resource_family": "string",
          "metric_code": "string",
          "quantity": integer,
          "rate": number,
          "cost": number
        }
      ]
    }
  ]
}
- `total_cost` must equal the sum of all `cost` values in `details` for that cluster.
- All costs should be rounded to two decimal places.
"""
    with open("attachments/report_schema.md", "w") as f:
        f.write(report_schema)


if __name__ == "__main__":
    build_env()
