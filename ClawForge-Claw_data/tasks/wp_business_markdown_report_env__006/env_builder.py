import os
import csv
import json

def build_env():
    # 创建目录结构
    os.makedirs("data/ledgers", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    
    # 客户台账 (customer_ledger.csv)
    # 2024-12 和 2024-11 的核心指标 + 干扰项
    customer_rows = [
        ['period', 'metric_code', 'metric_value'],
        ['2024-12', 'revenue', 450000],
        ['2024-12', 'active_customers', 1250],
        ['2024-12', 'churn_rate', 2.3],  # 干扰项：非核心
        ['2024-11', 'revenue', 420000],
        ['2024-11', 'active_customers', 1180],
        ['2024-11', 'avg_order_value', 85],  # 干扰项
        ['2024-10', 'revenue', 400000],  # 旧月份，不应包含在环比里（但prompt要求只看最新的三个csv，这里只有12和11是新表里的？实际上只有这个csv文件，但内部有多个月份数据，需要agent筛选12月和11月）
        ['2024-10', 'active_customers', 1100],
    ]
    with open("data/ledgers/customer_ledger.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(customer_rows)
    
    # 产品台账 (product_ledger.csv)
    product_rows = [
        ['period', 'metric_code', 'metric_value'],
        ['2024-12', 'units_sold', 3200],
        ['2024-12', 'avg_price', 149.5],
        ['2024-12', 'inventory_level', 500],  # 干扰
        ['2024-11', 'units_sold', 2800],
        ['2024-11', 'avg_price', 145.0],
        ['2024-11', 'defect_rate', 0.02],  # 干扰
        ['2024-10', 'units_sold', 2500],
        ['2024-10', 'avg_price', 140.0],
    ]
    with open("data/ledgers/product_ledger.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(product_rows)
    
    # 运营台账 (ops_ledger.csv)
    ops_rows = [
        ['period', 'metric_code', 'metric_value'],
        ['2024-12', 'uptime_pct', 99.8],
        ['2024-12', 'ticket_resolved', 430],
        ['2024-12', 'avg_response_time', 1.2],  # 干扰
        ['2024-11', 'uptime_pct', 99.5],
        ['2024-11', 'ticket_resolved', 390],
        ['2024-11', 'sla_breach', 5],  # 干扰
        ['2024-10', 'uptime_pct', 99.7],
        ['2024-10', 'ticket_resolved', 410],
    ]
    with open("data/ledgers/ops_ledger.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(ops_rows)
    
    # 创建旧的备份文件作为干扰项
    with open("data/ledgers/customer_ledger_2024-09.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows([["period","metric_code","metric_value"],["2024-09","revenue",380000]])
    with open("data/ledgers/old_ops_backup.csv", "w", newline="") as f:
        f.write("this is not a csv\n")
    
    # 创建一个 accounts.json 和 contacts.json 作为环境的额外数据（但prompt未要求使用，仅作为干扰氛围）
    accounts = [
        {"account_id":"acc1","display_name":"Alpha","department":"Customer","email":"alpha@co.com","permissions":["read"]},
        {"account_id":"acc2","display_name":"Beta","department":"Product","email":"beta@co.com","permissions":["read","write"]}
    ]
    with open("data/accounts.json","w") as f:
        json.dump(accounts, f)
    
    contacts = [
        {"contact_id":"c1","name":"Alice","role":"Manager","email":"alice@co.com"},
        {"contact_id":"c2","name":"Bob","role":"Engineer","email":"bob@co.com"}
    ]
    with open("data/contacts.json","w") as f:
        json.dump(contacts, f)
    
    # 在reports目录里放一个旧报告作为干扰
    with open("reports/old_report.md","w") as f:
        f.write("# Old report\nSome text")

if __name__ == "__main__":
    build_env()
