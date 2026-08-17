import os
import json
import shutil

def build_env():
    # Clean slate
    if os.path.exists("data"):
        shutil.rmtree("data")
    if os.path.exists("pricing"):
        shutil.rmtree("pricing")
    if os.path.exists("ops"):
        shutil.rmtree("ops")

    # --- directories ---
    os.makedirs("data/resources", exist_ok=True)
    os.makedirs("data/pricing", exist_ok=True)
    os.makedirs("data/reports", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # --- accounts.json (distraction, not used) ---
    accounts = [
        {"account_id": "acc-001", "display_name": "Northstar FinOps", "department": "Finance", "email": "daniel.song@northstar.example.com", "permissions": ["billing"], "default_region": "us-east-1", "voice": []},
        {"account_id": "acc-002", "display_name": "Platform Engineering", "department": "Engineering", "email": "ops@northstar.example.com", "permissions": ["admin"], "default_region": "us-west-2", "voice": []}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # --- contacts.json (distraction) ---
    contacts = [
        {"contact_id": "c001", "name": "Daniel Song", "role": "Cloud FinOps Lead", "email": "daniel.song@northstar.example.com"},
        {"contact_id": "c002", "name": "Leah Kumar", "role": "Cloud Operations Manager", "email": "leah.kumar@northstar.example.com"},
        {"contact_id": "c003", "name": "Tara Ng", "role": "Data Platform Director", "email": "tara.ng@northstar.example.com"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # --- attachments.json (distraction) ---
    attachments = [
        {"path": "cost_accounting_rules.md", "title": "Cloud Cost Accounting Rules", "kind": "accounting_policy", "description": "Do not use"},
        {"path": "report_schema.md", "title": "Monthly Cost Report Schema", "kind": "report_schema", "description": "Legacy schema"}
    ]
    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

    # --- clusters.json (with multiple clusters) ---
    clusters = [
        {"cluster_id": "cl-ads", "cluster_name": "ads-ranking", "business_service": "Ads ranking and campaign inference", "domain": "marketing", "environment": "production", "region": "us-east-1", "owner_team": "Growth Engineering", "cluster_role": "business", "service_tier": "tier_1", "workload_tags": ["ml", "real-time"]},
        {"cluster_id": "cl-lake", "cluster_name": "lakehouse-analytics", "business_service": "Lakehouse analytics and finance marts", "domain": "data", "environment": "production", "region": "us-east-1", "owner_team": "Data Platform", "cluster_role": "business", "service_tier": "tier_1", "workload_tags": ["analytics", "scheduled"]},
        {"cluster_id": "cl-retail", "cluster_name": "retail-core", "business_service": "Storefront and order orchestration", "domain": "commerce", "environment": "production", "region": "us-west-2", "owner_team": "Commerce Platform", "cluster_role": "business", "service_tier": "tier_1", "workload_tags": ["transactional"]},
        {"cluster_id": "cl-shared", "cluster_name": "shared-ops", "business_service": "Shared CI and platform tooling", "domain": "infrastructure", "environment": "production", "region": "us-east-1", "owner_team": "Cloud Foundations", "cluster_role": "shared_platform", "service_tier": "tier_2", "workload_tags": ["ci", "pipeline"]}
    ]
    with open("data/resources/clusters.json", "w") as f:
        json.dump({"clusters": clusters}, f, indent=2)

    # --- resource_ledger.json (with distractions: zero/negative qty, other clusters, extra columns) ---
    ledger_entries = [
        # ads‑ranking valid entries
        {"entry_id": "e-ads-001", "cluster_id": "cl-ads", "cluster_name": "ads-ranking", "resource_name": "compute-pool-a", "resource_family": "compute", "metric_code": "vcpu", "quantity": 24, "unit": "vcpu", "billing_model": "reserved"},
        {"entry_id": "e-ads-002", "cluster_id": "cl-ads", "cluster_name": "ads-ranking", "resource_name": "compute-pool-a", "resource_family": "compute", "metric_code": "memory_gb", "quantity": 256, "unit": "GiB", "billing_model": "reserved"},
        {"entry_id": "e-ads-003", "cluster_id": "cl-ads", "cluster_name": "ads-ranking", "resource_name": "data-store-1", "resource_family": "storage", "metric_code": "block_storage_gb", "quantity": 2000, "unit": "GiB", "billing_model": "monthly"},
        {"entry_id": "e-ads-004", "cluster_id": "cl-ads", "cluster_name": "ads-ranking", "resource_name": "archive-bucket", "resource_family": "storage", "metric_code": "object_storage_gb", "quantity": 5000, "unit": "GiB", "billing_model": "monthly"},
        # distraction: zero quantity for same cluster
        {"entry_id": "e-ads-005", "cluster_id": "cl-ads", "cluster_name": "ads-ranking", "resource_name": "compute-pool-b", "resource_family": "compute", "metric_code": "vcpu", "quantity": 0, "unit": "vcpu", "billing_model": "autoscale"},
        # distraction: negative quantity (should be filtered)
        {"entry_id": "e-ads-006", "cluster_id": "cl-ads", "cluster_name": "ads-ranking", "resource_name": "orphan-volume", "resource_family": "storage", "metric_code": "block_storage_gb", "quantity": -500, "unit": "GiB", "billing_model": "monthly"},
        # other clusters (should be ignored)
        {"entry_id": "e-lake-001", "cluster_id": "cl-lake", "cluster_name": "lakehouse-analytics", "resource_name": "analytics-pool", "resource_family": "compute", "metric_code": "vcpu", "quantity": 96, "unit": "vcpu", "billing_model": "reserved"},
        {"entry_id": "e-retail-001", "cluster_id": "cl-retail", "cluster_name": "retail-core", "resource_name": "web-servers", "resource_family": "compute", "metric_code": "vcpu", "quantity": 64, "unit": "vcpu", "billing_model": "monthly"},
        {"entry_id": "e-shared-001", "cluster_id": "cl-shared", "cluster_name": "shared-ops", "resource_name": "ci-agents", "resource_family": "compute", "metric_code": "vcpu", "quantity": 32, "unit": "vcpu", "billing_model": "monthly"}
    ]
    with open("data/resources/resource_ledger.json", "w") as f:
        json.dump({"resource_ledger": ledger_entries}, f, indent=2)

    # --- pricing catalogs ---
    # Archived March catalog (should not be used)
    archived_catalog = {
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
            {"resource_family": "compute", "metric_code": "vcpu", "unit_price": 0.045},
            {"resource_family": "compute", "metric_code": "memory_gb", "unit_price": 0.009},
            {"resource_family": "storage", "metric_code": "block_storage_gb", "unit_price": 0.00018},
            {"resource_family": "storage", "metric_code": "object_storage_gb", "unit_price": 0.00009}
        ]
    }
    # Active June catalog (correct one)
    active_catalog = {
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
            {"resource_family": "storage", "metric_code": "block_storage_gb", "unit_price": 0.0002},
            {"resource_family": "storage", "metric_code": "object_storage_gb", "unit_price": 0.0001}
        ]
    }
    with open("data/pricing/pricing_catalogs.json", "w") as f:
        json.dump({"pricing_catalogs": [archived_catalog, active_catalog]}, f, indent=2)

    # --- stale reports in data/reports (distraction) ---
    stale_report = {
        "report_id": "rep-2026-03",
        "month": "2026-03",
        "cluster": "ads-ranking",
        "total_cost": 2890.56,
        "breakdown": {"compute": 2100.0, "storage": 790.56}
    }
    with open("data/reports/old_q1_report.json", "w") as f:
        json.dump(stale_report, f, indent=2)

    # Also create an empty ops directory placeholder (will be overwritten by agent)
    # Just to ensure directory exists
    pass

if __name__ == "__main__":
    build_env()
