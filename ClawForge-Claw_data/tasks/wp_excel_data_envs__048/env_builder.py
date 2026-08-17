import os
import csv

def build_env():
    # 创建目录
    os.makedirs("data/raw_data", exist_ok=True)
    os.makedirs("data/archive", exist_ok=True)
    # 写入 sales_raw.csv
    rows = [
        ["transaction_id","date","product_id","product_name","category","subcategory","region","city","customer_id","customer_name","sales_amount","quantity","discount","payment_method","salesperson_id","salesperson_name","channel"],
        ["T001","2023-01-01","P001","Widget A","Electronics","Gadgets","North","NYC","C001","Alice","100.50","2","0","CC","S001","John","Online"],
        ["T002","2023-01-02","P002","Widget B","Electronics","Gadgets","South","LA","C002","Bob","200.00","1","10","CC","S002","Jane","Store"],
        ["T003","2023-01-03","P003","Widget C","Home","Kitchen","East","DC","C003","Charlie","50.00","5","0","Cash","S003","Jim","Online"],
        ["T004","2023-01-04","P004","Widget D","Electronics","Computers","West","SF","C004","Diana","-150.00","2","0","CC","S004","Jack","Online"],
        ["T001","2023-01-01","P001","Widget A","Electronics","Gadgets","North","NYC","C001","Alice","100.50","2","0","CC","S001","John","Online"],  # duplicate
        ["T005","2023-01-05","P005","Widget E","Home","Kitchen","North","Chi","C005","Eve","75.00","3","5","Cash","S005","Jill","Store"],
        ["T006","2023-01-06","P006","Widget F","Electronics","Computers","South","Austin","C006","Frank","","2","0","CC","S006","Tom","Online"],  # missing amount
        ["T007","2023-01-07","P007","Widget G","Books","Fiction","East","NYC","C007","Grace","30.00","1","0","Cash","S007","Amy","Online"],
        ["T008","2023-01-08","P008","Widget H","Books","NonFiction","West","LA","C008","Hank","45.00","1","0","Card","S008","Bob","Store"]
    ]
    with open("data/raw_data/sales_raw.csv","w",newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    # 写入 old_sales_backup.csv 干扰
    backup_rows = [
        ["transaction_id","date","product_id","product_name","category","subcategory","region","city","customer_id","customer_name","sales_amount","quantity","discount","payment_method","salesperson_id","salesperson_name","channel"],
        ["T001","2023-01-01","P001","Widget A","Electronics","Gadgets","North","NYC","C001","Alice","200.00","2","0","CC","S001","John","Online"], # different amount
        ["T009","2023-02-01","P009","Widget I","Office","Supplies","East","Boston","C009","Iris","120.00","4","10","CC","S009","Kim","Online"]
    ]
    with open("data/old_sales_backup.csv","w",newline="") as f:
        writer = csv.writer(f)
        writer.writerows(backup_rows)
    # 写入 accounts.csv 干扰
    accounts_rows = [
        ["account_id","display_name","role","email"],
        ["C001","Alice","Manager","alice@co.com"],
        ["C002","Bob","Staff","bob@co.com"]
    ]
    with open("data/accounts.csv","w",newline="") as f:
        writer = csv.writer(f)
        writer.writerows(accounts_rows)
    # 写入 archive/backup_2022.csv
    os.makedirs("data/archive", exist_ok=True)
    archive_rows = [
        ["transaction_id","amount"],
        ["X001","500"],
        ["X002","300"]
    ]
    with open("data/archive/backup_2022.csv","w",newline="") as f:
        writer = csv.writer(f)
        writer.writerows(archive_rows)

if __name__ == "__main__":
    build_env()
