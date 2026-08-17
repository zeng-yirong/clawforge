import os
import csv
import json
import math

def build_env():
    # 确保目录存在
    os.makedirs("data/raw_data", exist_ok=True)
    os.makedirs("data/backup", exist_ok=True)  # 干扰目录

    # 原始销售数据（含重复、缺失）
    sales_lines = [
        ["t1","2024-01-01","p1","Widget","Electronics","Gadgets","East","NYC","1","Alice","100.0","2","10","Credit","s1","John","Online"],
        ["t1","2024-01-01","p1","Widget","Electronics","Gadgets","East","NYC","1","Alice","100.0","2","10","Credit","s1","John","Online"],  # 完全重复
        ["t2","2024-01-02","p2","Gizmo","Home","Kitchen","West","LA","2","","200.0","1","0","Cash","s2","Jane","Retail"],  # 客户名称缺失
        ["t3","2024-01-03","p1","Widget","Electronics","Gadgets","North","Chicago","1","Alice","150.0","3","5","Debit","s1","John","Online"],
        ["t4","2024-01-04","p3","Thingamajig","Home","Garden","South","Houston","3","Charlie","75.0","5","15","Credit","s3","Jake","Online"],
        ["t5","2024-01-05","p2","Gizmo","Home","Kitchen","West","LA","2","","120.0","2","10","Cash","s2","Jane","Retail"],  # 客户名称缺失
        ["t6","2024-01-06","p4","Doodad","Office","Supplies","East","Boston","1","Alice","80.0","1","0","Debit","s4","Mike","Retail"],
        ["t7","2024-01-07","p1","Widget","Electronics","Gadgets","East","NYC","4","Diana","200.0","4","20","Cash","s5","Emma","Online"],
        ["t8","2024-01-08","p3","Thingamajig","Home","Garden","South","Houston","3","Charlie","90.0","3","5","Credit","s3","Jake","Online"],
        ["t9","2024-01-09","p5","Whatchamacallit","Electronics","Accessories","West","SF","5","","50.0","1","0","Credit","s6","Liam","Retail"],  # 客户名称缺失
        ["t10","2024-01-10","p4","Doodad","Office","Supplies","East","Boston","1","Alice","110.0","2","10","Debit","s4","Mike","Online"],
        ["t2","2024-01-02","p2","Gizmo","Home","Kitchen","West","LA","2","","200.0","1","0","Cash","s2","Jane","Retail"],  # 完全重复（与第3行相同）
        ["t11","2024-01-11","p6","Gadget","Electronics","Gadgets","North","Detroit","6","Frank","300.0","6","30","Credit","s7","Nina","Retail"],
        ["t10","2024-01-10","p4","Doodad","Office","Supplies","East","Boston","1","Alice","110.0","2","10","Debit","s4","Mike","Online"],  # 完全重复
    ]

    # 写 sales_raw.csv
    header = ["transaction_id","date","product_id","product_name","category","subcategory","region","city","customer_id","customer_name","sales_amount","quantity","discount","payment_method","salesperson_id","salesperson_name","channel"]
    with open("data/raw_data/sales_raw.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(sales_lines)

    # 写 accounts.csv
    accounts = [
        ["1","Alice","Manager","alice@company.com"],
        ["2","Bob","Sales","bob@company.com"],
        ["3","Charlie","Sales","charlie@company.com"],
        ["4","Diana","Manager","diana@company.com"],
        ["5","Eve","Sales","eve@company.com"],   # 注意 customer_id=5 对应 Eve（原始数据中 customer_name 缺失的客户 5）
        ["6","Frank","Sales","frank@company.com"],
    ]
    with open("data/accounts.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["account_id","display_name","role","email"])
        writer.writerows(accounts)

    # 干扰文件：旧版销售数据（格式不同）
    with open("data/backup/old_sales.csv", "w") as f:
        f.write("id,date,product,amount\n")
        f.write("a1,2023-12-01,Widget,120\n")
        f.write("a2,2023-12-15,Gizmo,60\n")

    # 干扰文件：一个空的汇总文件夹
    os.makedirs("reports", exist_ok=True)

if __name__ == "__main__":
    build_env()
