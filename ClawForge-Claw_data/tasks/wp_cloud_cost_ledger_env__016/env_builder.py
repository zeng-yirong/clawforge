import os
import json

def build_env():
    # Ensure directories exist
    os.makedirs("data/resources", exist_ok=True)
    os.makedirs("data/pricing", exist_ok=True)
    os.makedirs("attachments", exist_ok=True)
    # ops directory will be created by agent output, but we can create it empty for consistency
    os.makedirs("ops", exist_ok=True)

    # --- clusters.json ---
    clusters = {
        "collection": "clusters",
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
                "workload_tags": ["ml-inference", "real-time"]
            },
            {
                "cluster_id": "cluster_lake",
                "cluster_name": "lakehouse-analytics",
                "business_service": "Lakehouse analytics and finance marts",
                "domain": "data",
                "environment": "production",
                "region": "us-east-1",
                "owner_team": "Data Platform",
                "cluster_role": "business",
                "service_tier": "tier_1",
                "workload_tags": ["batch", "etl"]
            },
            {
                "cluster_id": "cluster_retail",
                "cluster_name": "retail-core",
                "business_service": "Storefront and order orchestration",
                "domain": "commerce",
                "environment": "production",
                "region": "us-west-2",
                "owner_team": "Commerce Platform",
                "cluster_role": "business",
                "service_tier": "tier_1",
                "workload_tags": ["transactional", "critical"]
            },
            {
                "cluster_id": "cluster_shared",
                "cluster_name": "shared-ops",
                "business_service": "Shared CI and platform tooling",
                "domain": "infrastructure",
                "environment": "production",
                "region": "eu-west-1",
                "owner_team": "Cloud Foundations",
                "cluster_role": "shared_platform",
                "service_tier": "tier_2",
                "workload_tags": ["ci", "monitoring"]
            }
        ]
    }
    with open("data/resources/clusters.json", "w") as f:
        json.dump(clusters, f, indent=2)

    # --- resource_ledger.json ---
    resource_ledger = {
        "collection": "resource_ledger",
        "resource_ledger": [
            # ads-ranking entries
            {"entry_id": "rle_001", "cluster_id": "cluster_ads", "cluster_name": "ads-ranking",
             "resource_name": "ml-compute-pool", "resource_family": "compute",
             "metric_code": "vcpu", "quantity": 120, "unit": "vcpu", "billing_model": "reserved"},
            {"entry_id": "rle_002", "cluster_id": "cluster_ads", "cluster_name": "ads-ranking",
             "resource_name": "ml-compute-pool", "resource_family": "compute",
             "metric_code": "memory_gb", "quantity": 512, "unit": "GiB", "billing_model": "reserved"},
            {"entry_id": "rle_003", "cluster_id": "cluster_ads", "cluster_name": "ads-ranking",
             "resource_name": "gpu-accelerator", "resource_family": "compute",
             "metric_code": "gpu", "quantity": 8, "unit": "gpu", "billing_model": "autoscale"},
            {"entry_id": "rle_004", "cluster_id": "cluster_ads", "cluster_name": "ads-ranking",
             "resource_name": "training-data-store", "resource_family": "storage",
             "metric_code": "block_storage_gb", "quantity": 2000, "unit": "GiB", "billing_model": "monthly"},
            {"entry_id": "rle_005", "cluster_id": "cluster_ads", "cluster_name": "ads-ranking",
             "resource_name": "model-artifacts-store", "resource_family": "storage",
             "metric_code": "object_storage_gb", "quantity": 5000, "unit": "GiB", "billing_model": "monthly"},
            # lakehouse-analytics (interference)
            {"entry_id": "rle_006", "cluster_id": "cluster_lake", "cluster_name": "lakehouse-analytics",
             "resource_name": "spark-pool", "resource_family": "compute",
             "metric_code": "vcpu", "quantity": 200, "unit": "vcpu", "billing_model": "reserved"},
            {"entry_id": "rle_007", "cluster_id": "cluster_lake", "cluster_name": "lakehouse-analytics",
             "resource_name": "spark-pool", "resource_family": "compute",
             "metric_code": "memory_gb", "quantity": 1024, "unit": "GiB", "billing_model": "reserved"},
            {"entry_id": "rle_008", "cluster_id": "cluster_lake", "cluster_name": "lakehouse-analytics",
             "resource_name": "data-lake", "resource_family": "storage",
             "metric_code": "object_storage_gb", "quantity": 15000, "unit": "GiB", "billing_model": "monthly"},
            # retail-core (interference)
            {"entry_id": "rle_009", "cluster_id": "cluster_retail", "cluster_name": "retail-core",
             "resource_name": "web-servers", "resource_family": "compute",
             "metric_code": "vcpu", "quantity": 64, "unit": "vcpu", "billing_model": "monthly"},
            {"entry_id": "rle_010", "cluster_id": "cluster_retail", "cluster_name": "retail-core",
             "resource_name": "db-storage", "resource_family": "storage",
             "metric_code": "block_storage_gb", "quantity": 800, "unit": "GiB", "billing_model": "monthly"},
            # shared-ops (interference, with zero quantity to test filtering)
            {"entry_id": "rle_011", "cluster_id": "cluster_shared", "cluster_name": "shared-ops",
             "resource_name": "bastion-hosts", "resource_family": "compute",
             "metric_code": "vcpu", "quantity": 0, "unit": "vcpu", "billing_model": "monthly"}
        ]
    }
    with open("data/resources/resource_ledger.json", "w") as f:
        json.dump(resource_ledger, f, indent=2)

    # --- pricing_catalogs.json ---
    pricing_catalogs = {
        "collection": "pricing_catalogs",
        "pricing_catalogs": [
            {
                "catalog_id": "cat_2026_03",
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
                    {"resource_family": "compute", "metric_code": "vcpu", "rate": 0.06},
                    {"resource_family": "compute", "metric_code": "memory_gb", "rate": 0.012},
                    {"resource_family": "compute", "metric_code": "gpu", "rate": 0.55},
                    {"resource_family": "storage", "metric_code": "block_storage_gb", "rate": 0.09},
                    {"resource_family": "storage", "metric_code": "object_storage_gb", "rate": 0.025}
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
                    {"resource_family": "compute", "metric_code": "vcpu", "rate": 0.05},
                    {"resource_family": "compute", "metric_code": "memory_gb", "rate": 0.01},
                    {"resource_family": "compute", "metric_code": "gpu", "rate": 0.5},
                    {"resource_family": "storage", "metric_code": "block_storage_gb", "rate": 0.08},
                    {"resource_family": "storage", "metric_code": "object_storage_gb", "rate": 0.02}
                ]
            }
        ]
    }
    with open("data/pricing/pricing_catalogs.json", "w") as f:
        json.dump(pricing_catalogs, f, indent=2)

    # --- accounts.json (required by schema, but not directly used) ---
    accounts = {
        "collection": "accounts",
        "accounts": [
            {"account_id": "acct_001", "display_name": "NorthStar Cloud", "department": "Engineering",
             "email": "cloud-ops@northstar.example.com", "permissions": ["admin", "billing"],
             "default_region": "us-east-1", "voice": []}
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # --- contacts.json (required by schema) ---
    contacts = {
        "collection": "contacts",
        "contacts": [
            {"contact_id": "ct_001", "name": "Daniel Song", "role": "Cloud FinOps Lead",
             "email": "daniel.song@northstar.example.com"},
            {"contact_id": "ct_002", "name": "Leah Kumar", "role": "Cloud Operations Manager",
             "email": "leah.kumar@northstar.example.com"},
            {"contact_id": "ct_003", "name": "Tara Ng", "role": "Data Platform Director",
             "email": "tara.ng@northstar.example.com"}
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # --- attachments.json ---
    attachments = {
        "collection": "attachments",
        "attachments": [
            {"path": "attachments/cost_accounting_rules.md", "title": "Cloud Cost Accounting Rules",
             "kind": "accounting_policy", "description": "Policy document describing cost allocation methodology."},
            {"path": "attachments/report_schema.md", "title": "Monthly Cost Report Schema",
             "kind": "report_schema", "description": "Expected JSON schema for monthly cost reports."}
        ]
    }
    with open("data/attachments.json", "w") as f:
        json.dump(attachments, f, indent=2)

    # --- attachment content (cost_accounting_rules.md) ---
    rules_md = """# Cloud Cost Accounting Rules

## General
- Costs are calculated by multiplying resource quantity by the applicable rate.
- The rate to use is from the **active** pricing catalog for the billing month.
- Archived catalogs must not be used unless explicitly approved.

## Compute
- vCPU: per vCPU-hour
- Memory (GiB): per GiB-hour
- GPU: per GPU-hour

## Storage
- Block Storage (GiB): per GiB-month
- Object Storage (GiB): per GiB-month

## Disclaimers
This document is a historical reference; the rates in the active catalog always take precedence.
"""
    with open("attachments/cost_accounting_rules.md", "w") as f:
        f.write(rules_md)

    # --- report_schema.md (optional) ---
    schema_md = """# Monthly Cost Report Schema
{
  "cluster_name": "string",
  "billing_month": "YYYY-MM",
  "currency": "USD",
  "total_cost": "number (float)"
}
"""
    with open("attachments/report_schema.md", "w") as f:
        f.write(schema_md)

if __name__ == "__main__":
    build_env()
