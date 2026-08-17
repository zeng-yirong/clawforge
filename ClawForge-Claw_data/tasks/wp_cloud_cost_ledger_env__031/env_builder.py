import os
import json
import shutil

def build_env():
    # Clean slate
    if os.path.exists("data"):
        shutil.rmtree("data")
    if os.path.exists("output"):
        shutil.rmtree("output")
    if os.path.exists("attachments"):
        shutil.rmtree("attachments")

    # --- clusters.json ---
    clusters = [
        {
            "cluster_id": "c-ads",
            "cluster_name": "ads-ranking",
            "business_service": "Ads ranking and campaign inference",
            "domain": "marketing",
            "environment": "production",
            "region": "us-east-1",
            "owner_team": "Growth Engineering",
            "cluster_role": "business",
            "service_tier": "tier_1",
            "workload_tags": ["real-time", "ml"]
        },
        {
            "cluster_id": "c-lake",
            "cluster_name": "lakehouse-analytics",
            "business_service": "Lakehouse analytics and finance marts",
            "domain": "data",
            "environment": "production",
            "region": "us-west-2",
            "owner_team": "Data Platform",
            "cluster_role": "business",
            "service_tier": "tier_1",
            "workload_tags": ["batch", "etl"]
        },
        {
            "cluster_id": "c-retail",
            "cluster_name": "retail-core",
            "business_service": "Storefront and order orchestration",
            "domain": "commerce",
            "environment": "production",
            "region": "eu-west-1",
            "owner_team": "Commerce Platform",
            "cluster_role": "business",
            "service_tier": "tier_1",
            "workload_tags": ["web", "api"]
        },
        {
            "cluster_id": "c-shared",
            "cluster_name": "shared-ops",
            "business_service": "Shared CI and platform tooling",
            "domain": "infrastructure",
            "environment": "production",
            "region": "us-east-1",
            "owner_team": "Cloud Foundations",
            "cluster_role": "shared_platform",
            "service_tier": "tier_2",
            "workload_tags": ["ci", "monitoring"]
        }
    ]
    os.makedirs("data/resources", exist_ok=True)
    with open("data/resources/clusters.json", "w") as f:
        json.dump({"clusters": clusters}, f, indent=2)

    # --- resource_ledger.json ---
    ledger_entries = [
        # ads-ranking entries (positive)
        {"entry_id": "e-001", "cluster_id": "c-ads", "cluster_name": "ads-ranking", "resource_name": "ads-vcpu-pool", "resource_family": "compute", "metric_code": "vcpu", "quantity": 10, "unit": "vcpu", "billing_model": "monthly"},
        {"entry_id": "e-002", "cluster_id": "c-ads", "cluster_name": "ads-ranking", "resource_name": "ads-gpu-accelerators", "resource_family": "compute", "metric_code": "gpu", "quantity": 2, "unit": "gpu", "billing_model": "reserved"},
        {"entry_id": "e-003", "cluster_id": "c-ads", "cluster_name": "ads-ranking", "resource_name": "ads-block-storage", "resource_family": "storage", "metric_code": "block_storage_gb", "quantity": 100, "unit": "GiB", "billing_model": "monthly"},
        {"entry_id": "e-004", "cluster_id": "c-ads", "cluster_name": "ads-ranking", "resource_name": "ads-object-bucket", "resource_family": "storage", "metric_code": "object_storage_gb", "quantity": 500, "unit": "GiB", "billing_model": "autoscale"},
        # ads-ranking dirty entry (negative quantity – must be excluded)
        {"entry_id": "e-005", "cluster_id": "c-ads", "cluster_name": "ads-ranking", "resource_name": "ads-stale-vcpu", "resource_family": "compute", "metric_code": "vcpu", "quantity": -1, "unit": "vcpu", "billing_model": "monthly"},
        # shared-ops entries (should not be included in report)
        {"entry_id": "e-101", "cluster_id": "c-shared", "cluster_name": "shared-ops", "resource_name": "shared-ci-vcpu", "resource_family": "compute", "metric_code": "vcpu", "quantity": 4, "unit": "vcpu", "billing_model": "monthly"},
        {"entry_id": "e-102", "cluster_id": "c-shared", "cluster_name": "shared-ops", "resource_name": "shared-ci-storage", "resource_family": "storage", "metric_code": "block_storage_gb", "quantity": 50, "unit": "GiB", "billing_model": "monthly"},
        # other business clusters (not ads-ranking, should be ignored)
        {"entry_id": "e-201", "cluster_id": "c-lake", "cluster_name": "lakehouse-analytics", "resource_name": "lake-etl-vcpu", "resource_family": "compute", "metric_code": "vcpu", "quantity": 20, "unit": "vcpu", "billing_model": "monthly"},
        {"entry_id": "e-202", "cluster_id": "c-retail", "cluster_name": "retail-core", "resource_name": "retail-web-vcpu", "resource_family": "compute", "metric_code": "vcpu", "quantity": 8, "unit": "vcpu", "billing_model": "monthly"},
    ]
    with open("data/resources/resource_ledger.json", "w") as f:
        json.dump({"resource_ledger": ledger_entries}, f, indent=2)

    # --- pricing_catalogs.json ---
    active_rates = [
        {"metric_code": "vcpu", "resource_family": "compute", "unit": "vcpu", "unit_price": 0.12},
        {"metric_code": "gpu", "resource_family": "compute", "unit": "gpu", "unit_price": 0.50},
        {"metric_code": "block_storage_gb", "resource_family": "storage", "unit": "GiB", "unit_price": 0.02},
        {"metric_code": "object_storage_gb", "resource_family": "storage", "unit": "GiB", "unit_price": 0.01}
    ]
    archived_rates = [
        {"metric_code": "vcpu", "resource_family": "compute", "unit": "vcpu", "unit_price": 0.10},
        {"metric_code": "gpu", "resource_family": "compute", "unit": "gpu", "unit_price": 0.45},
        {"metric_code": "block_storage_gb", "resource_family": "storage", "unit": "GiB", "unit_price": 0.015},
        {"metric_code": "object_storage_gb", "resource_family": "storage", "unit": "GiB", "unit_price": 0.008}
    ]
    catalogs = [
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
            "rates": active_rates
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
            "rates": archived_rates
        }
    ]
    os.makedirs("data/pricing", exist_ok=True)
    with open("data/pricing/pricing_catalogs.json", "w") as f:
        json.dump({"pricing_catalogs": catalogs}, f, indent=2)

    # --- attachments (distractors) ---
    os.makedirs("data/attachments", exist_ok=True)
    with open("data/attachments/cost_accounting_rules.md", "w") as f:
        f.write("# Cost Accounting Rules\n\nAll compute costs are based on active monthly catalog.\n")
    with open("data/attachments/report_schema.md", "w") as f:
        f.write("# Report Schema\n\n```json\n{\n  \"report_month\": \"string\",\n  \"cluster_name\": \"string\",\n  \"total_cost\": number\n}\n```\n")

    # --- accounts.json (distractor) ---
    accounts = [
        {"account_id": "acc-001", "display_name": "Default", "department": "Engineering", "email": "eng@northstar.example.com", "permissions": ["admin"], "default_region": "us-east-1", "voice": ["en"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # --- contacts.json (distractor) ---
    contacts = [
        {"contact_id": "c-daniel", "name": "Daniel Song", "role": "Cloud FinOps Lead", "email": "daniel.song@northstar.example.com"},
        {"contact_id": "c-leah", "name": "Leah Kumar", "role": "Cloud Operations Manager", "email": "leah.kumar@northstar.example.com"},
        {"contact_id": "c-tara", "name": "Tara Ng", "role": "Data Platform Director", "email": "tara.ng@northstar.example.com"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # Ensure output directory exists (empty)
    os.makedirs("output", exist_ok=True)

    print("Environment built successfully.")

if __name__ == "__main__":
    build_env()
