import os
import csv
import random

random.seed(42)  # deterministic but unused here; all data hardcoded

def build_env():
    # Create directories
    os.makedirs("data_sources", exist_ok=True)
    os.makedirs("report", exist_ok=True)

    # city_region.csv (root)
    city_region = [
        ["city", "region"],
        ["New York", "East"],
        ["Los Angeles", "West"],
        ["Chicago", "Midwest"],
        ["Houston", "South"],
        ["San Francisco", "West"]
    ]
    with open("city_region.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(city_region)

    # sales_raw_2024.csv (the real data)
    raw_data = [
        ["transaction_id","date","product_id","product_name","category","region","city","customer_id","customer_name","sales_amount","quantity","discount","payment_method","salesperson_id","salesperson_name","channel"],
        ["T001","2024-01-15","P001","Widget A","Widgets","","New York","C001","Alice","100.0","2","10","Credit Card","S001","John","Online"],
        ["T002","2024-01-16","P002","Widget B","Widgets","","Los Angeles","C002","Bob","200.0","1","0","PayPal","S002","Jane","In-store"],
        ["T003","2024-01-17","P001","Widget A","Widgets","","Chicago","C003","Charlie","150.0","3","5","Debit Card","S001","John","Online"],
        ["T004","2024-01-18","P003","Gadget X","Gadgets","","Houston","C004","Diana","300.0","1","20","Credit Card","S003","Tom","Online"],
        ["T005","2024-01-18","P001","Widget A","Widgets","","New York","C001","Alice","100.0","2","10","Credit Card","S001","John","Online"],  # duplicate of T001
        ["T006","2024-01-19","P002","Widget B","Widgets","","Los Angeles","C002","Bob","250.0","1","0","PayPal","S002","Jane","In-store"],
        ["T007","2024-01-20","P004","Gadget Y","Gadgets","","San Francisco","C005","Eve","400.0","1","15","Cash","S003","Tom","Online"],
        ["T008","2024-01-21","P005","Widget C","Widgets","East","New York","C006","Frank","50.0","1","0","PayPal","S001","John","Online"]
    ]
    with open("data_sources/sales_raw_2024.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(raw_data)

    # sales_2023.csv (old year, different data)
    old_data = [
        ["transaction_id","date","product_id","product_name","category","region","city","customer_id","customer_name","sales_amount","quantity","discount","payment_method","salesperson_id","salesperson_name","channel"],
        ["O001","2023-06-01","P010","Old Widget","Widgets","East","New York","C100","Gary","120.0","2","0","Cash","S010","Mike","Online"],
        ["O002","2023-06-02","P011","Old Gadget","Gadgets","West","Los Angeles","C101","Hannah","80.0","1","10","Credit Card","S011","Nina","In-store"]
    ]
    with open("data_sources/sales_2023.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(old_data)

    # sales_old_backup.csv (backup with extra column, confusing)
    backup_data = [
        ["transaction_id","date","product_id","product_name","category","region","city","customer_id","customer_name","sales_amount","quantity","discount","payment_method","salesperson_id","salesperson_name","channel","backup_flag"],
        ["B001","2024-01-10","P020","Backup Item","Misc","","New York","C200","Ivan","90.0","1","0","PayPal","S020","Oscar","Online","Y"]
    ]
    with open("data_sources/sales_old_backup.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(backup_data)

    # Empty placeholder in report (to be overwritten by agent)
    open("report/avg_by_product_region.json", "w").close()

if __name__ == "__main__":
    build_env()
