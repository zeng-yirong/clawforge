import os
import json
import random
import math

def build_env():
    # --------------------
    # 1. Directories
    # --------------------
    os.makedirs("data/resources", exist_ok=True)
    os.makedirs("data/pricing", exist_ok=True)
    os.makedirs("data/attachments", exist_ok=True)
    os.makedirs("ops", exist_ok=True)          # empty, agent must create file here
    os.makedirs("raw_logs", exist_ok=True)    # decoy

    # --------------------
    # 2. Resource clusters (clusters.json)
    # --------------------
    clusters = {
        "clusters": [
            {"cluster_id": "c-ads-01", "cluster_name": "ads-ranking", "business_service": "Ads ranking and campaign inference", "domain": "marketing", "environment": "prod", "region": "us-east-1", "owner_team": "Growth Engineering", "cluster_role": "business", "service_tier": "tier_1", "workload_tags": ["ads", "ml"]},
            {"cluster_id": "c-lake-02", "cluster_name": "lakehouse-analytics", "business_service": "Lakehouse analytics and finance marts", "domain": "data", "environment": "prod", "region": "us-west-2", "owner_team": "Data Platform", "cluster_role": "business", "service_tier": "tier_1", "workload_tags": ["analytics", "finance"]},
            {"cluster_id": "c-retail-03", "cluster_name": "retail-core", "business_service": "Storefront and order orchestration", "domain": "commerce", "environment": "prod", "region": "eu-west-1", "owner_team": "Commerce Platform", "cluster_role": "business", "service_tier": "tier_1", "workload_tags": ["storefront", "orders"]},
            {"cluster_id": "c-shared-04", "cluster_name": "shared-ops", "business_service": "Shared CI and platform tooling", "domain": "infrastructure", "environment": "prod", "region": "us-east-1", "owner_team": "Cloud Foundations", "cluster_role": "shared_platform", "service_tier": "tier_2", "workload_tags": ["ci", "devtools"]}
        ]
    }
    with open("data/resources/clusters.json", "w") as f:
        json.dump(clusters, f, indent=2)

    # --------------------
    # 3. Resource ledger (resource_ledger.json) – includes target + decoys + dirty rows
    # --------------------
    entries = []

    # Helper to generate unique entry IDs
    def eid(prefix, n):
        return f"e-{prefix}-{n:04d}"

    # -- ads-ranking (target) – valid entries
    ads_entries = [
        {"entry_id": eid("ads",1), "cluster_id": "c-ads-01", "cluster_name": "ads-ranking", "resource_name": "compute-node-a", "resource_family": "compute", "metric_code": "vcpu", "quantity": 120, "unit": "vcpu", "billing_model": "monthly"},
        {"entry_id": eid("ads",2), "cluster_id": "c-ads-01", "cluster_name": "ads-ranking", "resource_name": "compute-node-a", "resource_family": "compute", "metric_code": "memory_gb", "quantity": 2560, "unit": "GiB", "billing_model": "monthly"},
        {"entry_id": eid("ads",3), "cluster_id": "c-ads-01", "cluster_name": "ads-ranking", "resource_name": "gpu-node-b", "resource_family": "compute", "metric_code": "gpu", "quantity": 8, "unit": "gpu", "billing_model": "reserved"},
        {"entry_id": eid("ads",4), "cluster_id": "c-ads-01", "cluster_name": "ads-ranking", "resource_name": "block-store-vol", "resource_family": "storage", "metric_code": "block_storage_gb", "quantity": 15000, "unit": "GiB", "billing_model": "monthly"},
        {"entry_id": eid("ads",5), "cluster_id": "c-ads-01", "cluster_name": "ads-ranking", "resource_name": "object-bucket", "resource_family": "storage", "metric_code": "object_storage_gb", "quantity": 50000, "unit": "GiB", "billing_model": "monthly"},
    ]
    entries.extend(ads_entries)

    # -- ads-ranking – dirty / invalid rows
    dirty_ads = [
        {"entry_id": eid("ads",6), "cluster_id": "c-ads-01", "cluster_name": "ads-ranking", "resource_name": "zero-vcpu", "resource_family": "compute", "metric_code": "vcpu", "quantity": 0, "unit": "vcpu", "billing_model": "monthly"},
        {"entry_id": eid("ads",7), "cluster_id": "c-ads-01", "cluster_name": "ads-ranking", "resource_name": "neg-mem", "resource_family": "compute", "metric_code": "memory_gb", "quantity": -512, "unit": "GiB", "billing_model": "monthly"},
        {"entry_id": eid("ads",8), "cluster_id": "c-ads-01", "cluster_name": "ads-ranking", "resource_name": "no-metric", "resource_family": "storage", "metric_code": "", "quantity": 100, "unit": "GiB", "billing_model": "monthly"},
        {"entry_id": eid("ads",9), "cluster_id": "c-ads-01", "cluster_name": "ads-ranking", "resource_name": "missing-family", "resource_family": "", "metric_code": "vcpu", "quantity": 10, "unit": "vcpu", "billing_model": "monthly"},
        {"entry_id": eid("ads",10), "cluster_id": "c-ads-01", "cluster_name": "ads-ranking", "resource_name": "dup-of-e1", "resource_family": "compute", "metric_code": "vcpu", "quantity": 120, "unit": "vcpu", "billing_model": "monthly"},  # duplicate quantity, but different entry_id – agent should still count both? we mark it as decoy because entry ids differ; the expected calculation already accounted for only 5 valid entries. To keep unique answer, we'll exclude this as it has a different entry_id but same quantity. Actually it would double vcpu cost if counted. So we must ensure it's flagged as invalid. Let's make its "cluster_name" slightly different to be safe? Let's change to "ads-rankung" (typo) so it's not counted. Better: use cluster_name = "ads-ranking" but resource_family empty? Already did. Let's keep this one with resource_family="compute", metric_code="vcpu", quantity=120, but set billing_model="invalid". The valid ones have "monthly" or "reserved". This one has "invalid". Agent should treat it as valid? Our schema doesn't restrict billing_model. So it would be considered valid and change answer. Let's make it clearly invalid: missing cluster_name field. We'll set cluster_name = None.
        {"entry_id": eid("ads",10), "cluster_id": "c-ads-01", "cluster_name": None, "resource_name": "noclustername", "resource_family": "compute", "metric_code": "vcpu", "quantity": 120, "unit": "vcpu", "billing_model": "monthly"},
    ]
    entries.extend(dirty_ads)

    # -- other clusters (decoys, valid)
    other_valid = [
        # lakehouse
        {"entry_id": eid("lk",1), "cluster_id": "c-lake-02", "cluster_name": "lakehouse-analytics", "resource_name": "spark-worker", "resource_family": "compute", "metric_code": "vcpu", "quantity": 400, "unit": "vcpu", "billing_model": "monthly"},
        {"entry_id": eid("lk",2), "cluster_id": "c-lake-02", "cluster_name": "lakehouse-analytics", "resource_name": "spark-worker", "resource_family": "compute", "metric_code": "memory_gb", "quantity": 8192, "unit": "GiB", "billing_model": "monthly"},
        # retail-core
        {"entry_id": eid("rt",1), "cluster_id": "c-retail-03", "cluster_name": "retail-core", "resource_name": "web-server", "resource_family": "compute", "metric_code": "vcpu", "quantity": 64, "unit": "vcpu", "billing_model": "monthly"},
        {"entry_id": eid("rt",2), "cluster_id": "c-retail-03", "cluster_name": "retail-core", "resource_name": "db-storage", "resource_family": "storage", "metric_code": "block_storage_gb", "quantity": 8000, "unit": "GiB", "billing_model": "monthly"},
        # shared-ops
        {"entry_id": eid("sh",1), "cluster_id": "c-shared-04", "cluster_name": "shared-ops", "resource_name": "ci-runner", "resource_family": "compute", "metric_code": "vcpu", "quantity": 32, "unit": "vcpu", "billing_model": "monthly"},
    ]
    entries.extend(other_valid)

    # -- random dirty rows (no cluster_name, empty metric_code, etc.)
    dirty_other = [
        {"entry_id": eid("dirty",1), "cluster_id": None, "cluster_name": "", "resource_name": "orphan-storage", "resource_family": "storage", "metric_code": "block_storage_gb", "quantity": 5000, "unit": "GiB", "billing_model": "monthly"},
        {"entry_id": eid("dirty",2), "cluster_id": "c-ads-01", "cluster_name": "ads-ranking", "resource_name": "negative-quantity", "resource_family": "storage", "metric_code": "object_storage_gb", "quantity": -100, "unit": "GiB", "billing_model": "monthly"},
        {"entry_id": eid("dirty",3), "cluster_id": "c-ads-01", "cluster_name": "ads-ranking", "resource_name": "null-metric", "resource_family": "compute", "metric_code": None, "quantity": 50, "unit": "vcpu", "billing_model": "monthly"},
    ]
    entries.extend(dirty_other)

    # Shuffle to avoid ordering clues
    random.shuffle(entries)

    with open("data/resources/resource_ledger.json", "w") as f:
        json.dump({"resource_ledger": entries}, f, indent=2)

    # --------------------
    # 4. Pricing catalogs (pricing_catalogs.json)
    # --------------------
    catalogs = {
        "pricing_catalogs": [
            {
                "catalog_id": "pc-2026-03",
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
                    {"metric_code": "vcpu", "unit_price": 0.038, "currency": "USD"},
                    {"metric_code": "memory_gb", "unit_price": 0.009, "currency": "USD"},
                    {"metric_code": "gpu", "unit_price": 0.75, "currency": "USD"},
                    {"metric_code": "block_storage_gb", "unit_price": 0.00010, "currency": "USD"},
                    {"metric_code": "object_storage_gb", "unit_price": 0.000015, "currency": "USD"}
                ]
            },
            {
                "catalog_id": "pc-2026-06",
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
                    {"metric_code": "vcpu", "unit_price": 0.042, "currency": "USD"},
                    {"metric_code": "memory_gb", "unit_price": 0.01, "currency": "USD"},
                    {"metric_code": "gpu", "unit_price": 0.80, "currency": "USD"},
                    {"metric_code": "block_storage_gb", "unit_price": 0.00012, "currency": "USD"},
                    {"metric_code": "object_storage_gb", "unit_price": 0.00002, "currency": "USD"}
                ]
            },
            {
                "catalog_id": "pc-2026-09",
                "version": "2026.09-draft",
                "status": "draft",
                "region": "us-east-1",
                "currency": "USD",
                "billing_month": "2026-09",
                "billing_hours": 720,
                "approved_for_reporting": False,
                "effective_from": "2026-09-01",
                "effective_to": "2026-09-30",
                "rates": [
                    {"metric_code": "vcpu", "unit_price": 0.045, "currency": "USD"},
                    {"metric_code": "memory_gb", "unit_price": 0.011, "currency": "USD"},
                    {"metric_code": "gpu", "unit_price": 0.85, "currency": "USD"},
                    {"metric_code": "block_storage_gb", "unit_price": 0.00013, "currency": "USD"},
                    {"metric_code": "object_storage_gb", "unit_price": 0.000025, "currency": "USD"}
                ]
            }
        ]
    }
    with open("data/pricing/pricing_catalogs.json", "w") as f:
        json.dump(catalogs, f, indent=2)

    # --------------------
    # 5. Attachments (report schema + decoy policy doc)
    # --------------------
    schema_content = """# Monthly Cost Report Schema
The output JSON must contain the following fields:
- cluster_name (string)
- billing_month (string, format YYYY-MM)
- currency (string)
- total_cost (number)
- breakdown (array of objects)
Each breakdown object:
- resource_family (string)
- cost (number)

Example:
{
  "cluster_name": "ads-ranking",
  "billing_month": "2026-06",
  "currency": "USD",
  "total_cost": 39.84,
  "breakdown": [
    {"resource_family": "compute", "cost": 37.04},
    {"resource_family": "storage", "cost": 2.80}
  ]
}"""
    with open("data/attachments/report_schema.md", "w") as f:
        f.write(schema_content)

    policy_content = """# Cloud Cost Accounting Rules (Decoy)
- Ignore any entry with quantity <= 0.
- Discard rows missing cluster_name or metric_code.
- Only use pricing catalogs with approved_for_reporting = true and status = 'active'.
- Round final cost to two decimal places."""
    with open("data/attachments/cost_accounting_rules.md", "w") as f:
        f.write(policy_content)

    # --------------------
    # 6. Decoy files in raw_logs/ and ops/
    # --------------------
    with open("raw_logs/old_audit.tar.gz", "w") as f:
        f.write("binary content placeholder")
    with open("ops/old_cost_report_2026_03.json", "w") as f:
        json.dump({"cluster_name":"ads-ranking","billing_month":"2026-03","total_cost":35.20}, f)

if __name__ == "__main__":
    build_env()
