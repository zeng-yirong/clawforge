import os
import csv

def build_env():
    # 创建目录
    os.makedirs("data", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    # 主销售数据（含重复和缺失）
    raw_data = [
        ["transaction_id","date","product_id","product_name","category","subcategory","region","city","customer_id","customer_name","sales_amount","quantity","discount","payment_method","salesperson_id","salesperson_name","channel"],
        ["T001","2024-01-05","P001","Widget A","Electronics","Gadgets","North","New York","C001","Alice","100.00","2","10","Credit","SP001","John","Online"],
        ["T001","2024-01-07","P001","Widget A","Electronics","Gadgets","North","New York","C001","Alice","120.00","2","10","Credit","SP001","John","Online"],  # 重复，保留此条
        ["T002","2024-01-12","P002","Widget B","Electronics","Gadgets","South","Dallas","C002","Bob","200.00","1","5","Debit","SP002","Jane","Store"],
        ["T003","2024-01-20","P003","Widget C","Home","Kitchen","East","Boston","C003","Charlie","150.00","3","0","Cash","SP003","Tom","Online"],
        ["T004","2024-02-03","P004","Widget D","Home","Kitchen","West","LA","C004","Diana","80.00","1","0","Debit","SP04","Lucy","Store"],
        ["T005","2024-02-15","P005","Widget E","Clothing","Shirts","North","Chicago","C005","Eve","250.00","5","15","Credit","SP005","Mark","Online"],
        ["T005","2024-02-10","P005","Widget E","Clothing","Shirts","North","Chicago","C005","Eve","240.00","5","15","Credit","SP005","Mark","Online"],  # 重复，保留2-15
        ["T006","2024-02-28","P006","Widget F","Clothing","Shirts","South","Houston","C006","Frank","90.00","1","0","Debit","SP006","Nina","Store"],
        ["T007","2024-03-01","P001","Widget A","Electronics","Gadgets","North","New York","C001","Alice","","1","0","Debit","SP001","John","Online"],  # 缺失金额
        ["T008","2024-03-05","P007","Widget G","Books","NonFic","East","Boston","C007","Grace","55.00","1","0","Cash","SP007","Oscar","Online"],
        ["T009","2024-03-10","P003","Widget C","Home","Kitchen","West","LA","C003","Charlie","","2","0","Credit","SP003","Tom","Online"],  # 缺失金额
        ["T010","2024-03-15","P008","Widget H","Books","NonFic","North","Chicago","C008","Henry","120.00","4","20","Credit","SP008","Paul","Store"],
    ]

    with open("data/sales_raw.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(raw_data)

    # 干扰文件：旧备份
    backup_data = [
        ["transaction_id","date","product_id","product_name","category","subcategory","region","city","customer_id","customer_name","sales_amount","quantity","discount","payment_method","salesperson_id","salesperson_name","channel"],
        ["T001","2023-12-20","P001","Widget A","Electronics","Gadgets","North","New York","C001","Alice","80.00","2","10","Credit","SP001","John","Online"],
        ["T002","2023-12-25","P002","Widget B","Electronics","Gadgets","South","Dallas","C002","Bob","190.00","1","5","Debit","SP002","Jane","Store"],
    ]
    with open("data/backup_2023.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(backup_data)

    # 干扰日志文件
    with open("logs/data_quality.log", "w") as f:
        f.write("2024-03-20 10:23:45 WARN  Found 2 duplicate transaction_ids in raw export.\n")
        f.write("2024-03-20 10:23:46 INFO  Null sales_amount detected for product P001, P003.\n")

if __name__ == "__main__":
    build_env()
