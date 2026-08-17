import os
import json

def build_env():
    # data/resources
    os.makedirs("data/resources", exist_ok=True)
    resource_ledger = [
        {
            "entry_id": "ledger-001",
            "cluster_id": "ads-ranking",
            "cluster_name": "ads-ranking",
            "resource_name": "ml-gpu-node",
            "resource_family": "compute",
            "metric_code": "gpu",
            "quantity": 4,
            "unit": "gpu",
            "billing_model": "reserved"
        },
        {
            "entry_id": "ledger-002",
            "cluster_id": "ads-ranking",
            "cluster_name": "ads-ranking",
            "resource_name": "ads-data-lake",
            "resource_family": "storage",
            "metric_code": "object_storage_gb",
            "quantity": 2000,
            "unit": "GiB",
            "billing_model": "monthly"
        },
        {
            "entry_id": "ledger-101",
            "cluster_id": "retail-core",
            "cluster_name": "retail-core",
            "resource_name": "app-vm-pool",
            "resource_family": "compute",
            "metric_code": "vcpu",
            "quantity": 16,
            "unit": "vcpu",
            "billing_model": "reserved"
        },
        {
            "entry_id": "ledger-102",
            "cluster_id": "retail-core",
            "cluster_name": "retail-core",
            "resource_name": "db-block-storage",
            "resource_family": "storage",
            "metric_code": "block_storage_gb",
            "quantity": 500,
            "unit": "GiB",
            "billing_model": "monthly"
        },
        {
            "entry_id": "ledger-103",
            "cluster_id": "retail-core",
            "cluster_name": "retail-core",
            "resource_name": "ml-inference-gpu",
            "resource_family": "compute",
            "metric_code": "gpu",
            "quantity": 2,
            "unit": "gpu",
            "billing_model": "reserved"
        },
        {
            "entry_id": "ledger-201",
            "cluster_id": "lakehouse-analytics",
            "cluster_name": "lakehouse-analytics",
            "resource_name": "spark-worker",
            "resource_family": "compute",
            "metric_code": "vcpu",
            "quantity": 32,
            "unit": "vcpu",
            "billing_model": "autoscale"
        },
        {
            "entry_id": "ledger-202",
            "cluster_id": "lakehouse-analytics",
            "cluster_name": "lakehouse-analytics",
            "resource_name": "lakehouse-archive",
            "resource_family": "storage",
            "metric_code": "block_storage_gb",
            "quantity": 800,
            "unit": "GiB",
            "billing_model": "monthly"
        },
        {
            "entry_id": "ledger-301",
            "cluster_id": "shared-ops",
            "cluster_name": "shared-ops",
            "resource_name": "ci-runner",
            "resource_family": "compute",
            "metric_code": "vcpu",
            "quantity": 8,
            "unit": "vcpu",
            "billing_model": "monthly"
        }
    ]
    with open("data/resources/resource_ledger.json", "w") as f:
        json.dump({"resource_ledger": resource_ledger}, f, indent=2)

    # data/pricing
    os.makedirs("data/pricing", exist_ok=True)
    pricing_catalogs = [
        {
            "catalog_id": "cp-2026-03-archive",
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
                {"resource_family": "compute", "metric_code": "vcpu", "unit_price": 0.10},
                {"resource_family": "compute", "metric_code": "gpu", "unit_price": 0.45},
                {"resource_family": "storage", "metric_code": "block_storage_gb", "unit_price": 0.07},
                {"resource_family": "storage", "metric_code": "object_storage_gb", "unit_price": 0.015}
            ]
        },
        {
            "catalog_id": "cp-2026-06",
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
                {"resource_family": "compute", "metric_code": "vcpu", "unit_price": 0.12},
                {"resource_family": "compute", "metric_code": "gpu", "unit_price": 0.50},
                {"resource_family": "storage", "metric_code": "block_storage_gb", "unit_price": 0.08},
                {"resource_family": "storage", "metric_code": "object_storage_gb", "unit_price": 0.02}
            ]
        }
    ]
    with open("data/pricing/pricing_catalogs.json", "w") as f:
        json.dump({"pricing_catalogs": pricing_catalogs}, f, indent=2)

    # optional decoy files (not required by task)
    os.makedirs("data", exist_ok=True)
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": []}, f)

if __name__ == "__main__":
    build_env()
