import os
import json

def build_env():
    # ---------- directories ----------
    os.makedirs("data/attachments", exist_ok=True)
    os.makedirs("data/pricing", exist_ok=True)
    os.makedirs("data/resources", exist_ok=True)
    os.makedirs("report", exist_ok=True)   # agent may need to write here

    # ---------- accounts.json (wrapper: accounts) ----------
    accounts = {"accounts": []}
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # ---------- contacts.json (wrapper: contacts) ----------
    contacts = {
        "contacts": [
            {"contact_id": "c001", "name": "Daniel Song", "role": "Cloud FinOps Lead", "email": "daniel.song@northstar.example.com"},
            {"contact_id": "c002", "name": "Leah Kumar", "role": "Cloud Operations Manager", "email": "leah.kumar@northstar.example.com"},
            {"contact_id": "c003", "name": "Tara Ng", "role": "Data Platform Director", "email": "tara.ng@northstar.example.com"}
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # ---------- attachments.json and attachment files ----------
    attachments = {
        "attachments": [
            {
                "path": "data/attachments/cost_accounting_rules.md",
                "title": "Cloud Cost Accounting Rules",
                "kind": "accounting_policy",
                "description": "Standard cost calculation methodology for monthly reports."
            },
            {
                "path": "data/attachments/report_schema.md",
                "title": "Monthly Cost Report Schema",
                "kind": "report_schema",
                "description": "Expected output schema for the cost detail report."
            }
        ]
    }
    with open("data/attachments.json", "w") as f:
        json.dump(attachments, f, indent=2)

    # cost accounting rules
    with open("data/attachments/cost_accounting_rules.md", "w") as f:
        f.write("""# Cloud Cost Accounting Rules
Effective from June 2026.

## Compute Cost
For each compute resource (vcpu, memory_gb, gpu):
cost = quantity × unit_price × billing_hours
where `unit_price` is taken from the approved pricing catalog's `rates` array for the matching `metric_code`,
and `billing_hours` is the `billing_hours` field of that pricing catalog.

## Storage Cost
Storage is calculated separately (not part of this compute report).
""")

    # report schema (optional, but we create it)
    with open("data/attachments/report_schema.md", "w") as f:
        f.write("""# Monthly Cost Report Schema
{
  "report_month": "YYYY-MM",
  "clusters": [
    {
      "cluster_id": "...",
      "resources": [
        {
          "metric_code": "vcpu",
          "total_quantity": <int>,
          "unit_price": <float>,
          "billing_hours": <int>,
          "total_cost": <float>
        }
      ]
    }
  ]
}
""")

    # ---------- pricing_catalogs.json (wrapper: pricing_catalogs) ----------
    pricing_catalogs = {
        "pricing_catalogs": [
            {
                "catalog_id": "catalog_2026_03",
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
                    {"metric_code": "vcpu", "unit_price": 0.04},
                    {"metric_code": "memory_gb", "unit_price": 0.008},
                    {"metric_code": "gpu", "unit_price": 0.4}
                ]
            },
            {
                "catalog_id": "catalog_2026_06",
                "version": "2026.06-live",
                "status": "active",
                "region": "us-east-1",
                "currency": "USD",
                "billing_month": "2026-06",
                "billing_hours": 730,
                "approved_for_reporting": True,
                "effective_from": "2026-06-01",
                "effective_to": "2026-06-30",
                "rates": [
                    {"metric_code": "vcpu", "unit_price": 0.05},
                    {"metric_code": "memory_gb", "unit_price": 0.01},
                    {"metric_code": "gpu", "unit_price": 0.5}
                ]
            }
        ]
    }
    with open("data/pricing/pricing_catalogs.json", "w") as f:
        json.dump(pricing_catalogs, f, indent=2)

    # ---------- clusters.json (wrapper: clusters) ----------
    clusters = {
        "clusters": [
            {
                "cluster_id": "cluster-ads",
                "cluster_name": "ads-ranking",
                "business_service": "Ads ranking and campaign inference",
                "domain": "marketing",
                "environment": "production",
                "region": "us-east-1",
                "owner_team": "Growth Engineering",
                "cluster_role": "business",
                "service_tier": "tier_1",
                "workload_tags": ["online", "ads"]
            },
            {
                "cluster_id": "cluster-lake",
                "cluster_name": "lakehouse-analytics",
                "business_service": "Lakehouse analytics and finance marts",
                "domain": "data",
                "environment": "production",
                "region": "us-east-1",
                "owner_team": "Data Platform",
                "cluster_role": "business",
                "service_tier": "tier_1",
                "workload_tags": ["analytics", "pipeline"]
            },
            {
                "cluster_id": "cluster-retail",
                "cluster_name": "retail-core",
                "business_service": "Storefront and order orchestration",
                "domain": "commerce",
                "environment": "production",
                "region": "us-east-1",
                "owner_team": "Commerce Platform",
                "cluster_role": "business",
                "service_tier": "tier_1",
                "workload_tags": ["storefront", "orders"]
            },
            {
                "cluster_id": "cluster-shared",
                "cluster_name": "shared-ops",
                "business_service": "Shared CI and platform tooling",
                "domain": "infrastructure",
                "environment": "production",
                "region": "us-east-1",
                "owner_team": "Cloud Foundations",
                "cluster_role": "shared_platform",
                "service_tier": "tier_1",
                "workload_tags": ["ci", "platform"]
            }
        ]
    }
    with open("data/resources/clusters.json", "w") as f:
        json.dump(clusters, f, indent=2)

    # ---------- resource_ledger.json (wrapper: resource_ledger) ----------
    resource_ledger = {
        "resource_ledger": [
            # --- valid business compute entries for June 2026 ---
            {
                "entry_id": "e-001",
                "cluster_id": "cluster-ads",
                "cluster_name": "ads-ranking",
                "resource_name": "ads-vcpu-pool",
                "resource_family": "compute",
                "metric_code": "vcpu",
                "quantity": 10,
                "unit": "vcpu",
                "billing_model": "reserved",
                "billing_month": "2026-06"
            },
            {
                "entry_id": "e-002",
                "cluster_id": "cluster-ads",
                "cluster_name": "ads-ranking",
                "resource_name": "ads-memory-pool",
                "resource_family": "compute",
                "metric_code": "memory_gb",
                "quantity": 64,
                "unit": "GiB",
                "billing_model": "reserved",
                "billing_month": "2026-06"
            },
            {
                "entry_id": "e-003",
                "cluster_id": "cluster-lake",
                "cluster_name": "lakehouse-analytics",
                "resource_name": "lake-vcpu-spot",
                "resource_family": "compute",
                "metric_code": "vcpu",
                "quantity": 20,
                "unit": "vcpu",
                "billing_model": "autoscale",
                "billing_month": "2026-06"
            },
            {
                "entry_id": "e-004",
                "cluster_id": "cluster-lake",
                "cluster_name": "lakehouse-analytics",
                "resource_name": "lake-memory-pool",
                "resource_family": "compute",
                "metric_code": "memory_gb",
                "quantity": 128,
                "unit": "GiB",
                "billing_model": "monthly",
                "billing_month": "2026-06"
            },
            {
                "entry_id": "e-005",
                "cluster_id": "cluster-retail",
                "cluster_name": "retail-core",
                "resource_name": "retail-vcpu-std",
                "resource_family": "compute",
                "metric_code": "vcpu",
                "quantity": 30,
                "unit": "vcpu",
                "billing_model": "reserved",
                "billing_month": "2026-06"
            },
            {
                "entry_id": "e-006",
                "cluster_id": "cluster-retail",
                "cluster_name": "retail-core",
                "resource_name": "retail-memory-std",
                "resource_family": "compute",
                "metric_code": "memory_gb",
                "quantity": 256,
                "unit": "GiB",
                "billing_model": "reserved",
                "billing_month": "2026-06"
            },
            # --- interference: shared-ops (should be excluded) ---
            {
                "entry_id": "e-007",
                "cluster_id": "cluster-shared",
                "cluster_name": "shared-ops",
                "resource_name": "shared-vcpu",
                "resource_family": "compute",
                "metric_code": "vcpu",
                "quantity": 100,
                "unit": "vcpu",
                "billing_model": "reserved",
                "billing_month": "2026-06"
            },
            # --- interference: old month (March 2026) ---
            {
                "entry_id": "e-008",
                "cluster_id": "cluster-ads",
                "cluster_name": "ads-ranking",
                "resource_name": "old-vcpu",
                "resource_family": "compute",
                "metric_code": "vcpu",
                "quantity": 5,
                "unit": "vcpu",
                "billing_model": "monthly",
                "billing_month": "2026-03"
            },
            # --- interference: storage entry (should be excluded) ---
            {
                "entry_id": "e-009",
                "cluster_id": "cluster-retail",
                "cluster_name": "retail-core",
                "resource_name": "retail-block-storage",
                "resource_family": "storage",
                "metric_code": "block_storage_gb",
                "quantity": 500,
                "unit": "GiB",
                "billing_model": "monthly",
                "billing_month": "2026-06"
            },
            # --- interference: zero-quantity entry (should not affect sum) ---
            {
                "entry_id": "e-010",
                "cluster_id": "cluster-lake",
                "cluster_name": "lakehouse-analytics",
                "resource_name": "lake-zero-pool",
                "resource_family": "compute",
                "metric_code": "memory_gb",
                "quantity": 0,
                "unit": "GiB",
                "billing_model": "monthly",
                "billing_month": "2026-06"
            }
        ]
    }
    with open("data/resources/resource_ledger.json", "w") as f:
        json.dump(resource_ledger, f, indent=2)

if __name__ == "__main__":
    build_env()
