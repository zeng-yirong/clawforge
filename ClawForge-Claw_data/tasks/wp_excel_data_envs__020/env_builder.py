import os
import csv
import json

def build_env():
    # Create directories
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/backup", exist_ok=True)
    
    # Sales raw data with duplicates, missing values, and a suspicious record
    rows = [
        ["transaction_id","date","product_id","product_name","category","subcategory","region","city","customer_id","customer_name","sales_amount","quantity","discount","payment_method","salesperson_id","salesperson_name","channel"],
        ["TXN-001","2023-01-10","P001","Widget A","Electronics","Accessories","East","New York","C001","Alice","100.0","2","0","Credit","SP001","John","Online"],
        ["TXN-002","2023-01-11","P002","Widget B","Electronics","Accessories","West","Los Angeles","C002","Bob","200.0","1","10","Debit","SP002","Jane","Store"],
        ["TXN-003","2023-01-12","P003","Widget C","Home","Kitchen","North","Chicago","C003","Charlie","150.0","3","5","Cash","SP003","Jim","Online"],
        ["TXN-004","2023-01-13","P004","Widget D","Home","Kitchen","East","Boston","C004","Diana","300.0","1","0","Credit","SP004","Jill","Store"],
        ["TXN-005","2023-01-14","P005","Widget E","Electronics","Accessories","West","San Francisco","C005","Eve","250.0","2","20","Debit","SP005","Jack","Online"],
        # Duplicate of TXN-001 (all fields same)
        ["TXN-001","2023-01-10","P001","Widget A","Electronics","Accessories","East","New York","C001","Alice","100.0","2","0","Credit","SP001","John","Online"],
        # Missing sales_amount
        ["TXN-006","2023-01-15","P006","Widget F","Home","Kitchen","North","Detroit","C006","Frank","","1","0","Cash","SP006","Julia","Store"],
        ["TXN-007","2023-01-16","P007","Widget G","Electronics","Accessories","East","Philadelphia","C007","Grace","180.0","4","15","Credit","SP007","Ken","Online"],
        ["TXN-008","2023-01-17","P008","Widget H","Home","Kitchen","West","Phoenix","C008","Hank","","2","10","Debit","SP008","Lisa","Store"],
        ["TXN-009","2023-01-18","P009","Widget I","Electronics","Accessories","North","Minneapolis","C009","Ivy","220.0","1","5","Credit","SP009","Mark","Online"],
        # Suspicious record
        ["TXN-000999","2023-01-19","P999","Suspicious Item","Other","Unknown","East","Newark","C999","Zoe","1500.0","1","0","Credit","SP999","Admin","Online"],
    ]
    with open("data/raw/sales_raw.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    # Decoy file: old sales backup
    old_rows = [
        ["transaction_id","date","sales_amount"],
        ["TXN-001","2022-12-01","500"],
        ["TXN-003","2022-12-02","300"],
    ]
    with open("data/backup/sales_old.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(old_rows)

    # Decoy file: accounts
    accounts = [
        ["account_id","display_name","role","email"],
        ["C001","Alice Carr","buyer","alice@example.com"],
        ["C002","Bob Smith","buyer","bob@example.com"],
    ]
    with open("data/accounts.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(accounts)

if __name__ == "__main__":
    build_env()
