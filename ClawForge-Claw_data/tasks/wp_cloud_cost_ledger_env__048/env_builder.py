import os
import csv
import json

def build_env():
    # data/resource_ledger.csv
    os.makedirs("data", exist_ok=True)
    rows = [
        ["entry_id","cluster_id","cluster_name","resource_name","resource_family","metric_code","quantity","unit","billing_model"],
        ["e001","c001","ads-ranking","compute-a1","compute","vcpu","40","vcpu","monthly"],
        ["e002","c001","ads-ranking","compute-g1","compute","gpu","8","gpu","reserved"],
        ["e003","c001","ads-ranking","storage-s1","storage","block_storage_gb","5000","GiB","monthly"],
        ["e004","c002","lakehouse-analytics","compute-b1","compute","vcpu","120","vcpu","autoscale"],
        ["e005","c002","lakehouse-analytics","memory-m1","compute","memory_gb","512","GiB","monthly"],
        ["e006","c002","lakehouse-analytics","storage-o1","storage","object_storage_gb","20000","GiB","monthly"],
        ["e007","c003","retail-core","compute-c1","compute","vcpu","64","vcpu","reserved"],
        ["e008","c003","retail-core","storage-s2","storage","block_storage_gb","10000","GiB","monthly"],
        ["e009","c004","shared-ops","compute-d1","compute","vcpu","16","vcpu","monthly"],
        ["e010","c004","shared-ops","memory-m2","compute","memory_gb","64","GiB","monthly"]
    ]
    with open("data/resource_ledger.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    # data/pricing/
    os.makedirs("data/pricing", exist_ok=True)

    # 有效定价（6月份，已批准）
    valid_catalog = {
        "catalog_id": "catalog_june",
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
            {"metric_code": "vcpu", "resource_family": "compute", "unit_price": 30.0},
            {"metric_code": "gpu", "resource_family": "compute", "unit_price": 500.0},
            {"metric_code": "memory_gb", "resource_family": "compute", "unit_price": 5.0},
            {"metric_code": "block_storage_gb", "resource_family": "storage", "unit_price": 0.10},
            {"metric_code": "object_storage_gb", "resource_family": "storage", "unit_price": 0.05}
        ]
    }
    with open("data/pricing/pricing_catalog_2026_06.json", "w") as f:
        json.dump(valid_catalog, f, indent=2)

    # 过期的3月份定价（已归档）
    old_catalog = {
        "catalog_id": "catalog_march",
        "version": "2026.03-archive",
        "status": "archived",
        "region": "us-east-1",
        "currency": "USD",
        "billing_month": "2026-03",
        "billing_hours": 720,
        "approved_for_reporting": False,
        "effective_from": "2026-03-01",
        "effective_to": "2026-03-31",
        "rates": [
            {"metric_code": "vcpu", "resource_family": "compute", "unit_price": 25.0},
            {"metric_code": "gpu", "resource_family": "compute", "unit_price": 450.0},
            {"metric_code": "memory_gb", "resource_family": "compute", "unit_price": 4.0},
            {"metric_code": "block_storage_gb", "resource_family": "storage", "unit_price": 0.08},
            {"metric_code": "object_storage_gb", "resource_family": "storage", "unit_price": 0.04}
        ]
    }
    with open("data/pricing/pricing_catalog_2026_03.json", "w") as f:
        json.dump(old_catalog, f, indent=2)

    # 另一个干扰项：6月份但未批准
    unapproved_catalog = {
        "catalog_id": "catalog_june_alt",
        "version": "2026.06-live",
        "status": "active",
        "region": "us-west-2",
        "currency": "USD",
        "billing_month": "2026-06",
        "billing_hours": 720,
        "approved_for_reporting": False,
        "effective_from": "2026-06-01",
        "effective_to": "2026-06-30",
        "rates": [
            {"metric_code": "vcpu", "resource_family": "compute", "unit_price": 28.0},
            {"metric_code": "gpu", "resource_family": "compute", "unit_price": 480.0},
            {"metric_code": "memory_gb", "resource_family": "compute", "unit_price": 4.5},
            {"metric_code": "block_storage_gb", "resource_family": "storage", "unit_price": 0.09},
            {"metric_code": "object_storage_gb", "resource_family": "storage", "unit_price": 0.045}
        ]
    }
    with open("data/pricing/pricing_catalog_2026_06_unapproved.json", "w") as f:
        json.dump(unapproved_catalog, f, indent=2)

if __name__ == "__main__":
    build_env()
