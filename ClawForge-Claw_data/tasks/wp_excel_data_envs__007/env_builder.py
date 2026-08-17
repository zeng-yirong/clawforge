import os
import csv
import json

def build_env():
    # Create required directories
    os.makedirs("data/backup", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    # Main sales data (raw_sales_2024.csv)
    header = [
        "transaction_id", "date", "product_id", "product_name", "category",
        "subcategory", "region", "city", "customer_id", "customer_name",
        "sales_amount", "quantity", "discount", "payment_method",
        "salesperson_id", "salesperson_name", "channel"
    ]

    # Valid rows (after dedup & cleaning)
    # P001: 100,200 -> avg=150
    # P002: 150,250,200 -> avg=200
    # P003: 500,400 -> avg=450
    rows = [
        ["TX2024-001","2024-01-15","P001","Product A","Cat1","Sub1","North","NY","C001","John","100.0","2","0","Credit","S001","Alice","Direct"],
        ["TX2024-002","2024-01-16","P001","Product A","Cat1","Sub1","North","NY","C002","Jane","200.0","3","5","Cash","S002","Bob","Online"],
        ["TX2024-003","2024-01-17","P002","Product B","Cat2","Sub2","South","TX","C003","Tom","150.0","1","0","Debit","S001","Alice","Direct"],
        ["TX2024-004","2024-01-18","P002","Product B","Cat2","Sub2","South","TX","C004","Lisa","250.0","2","10","Credit","S002","Bob","Online"],
        ["TX2024-005","2024-01-19","P003","Product C","Cat3","Sub3","East","MA","C005","Mike","500.0","5","0","Cash","S003","Charlie","Direct"],
        # Exact duplicate of TX2024-001
        ["TX2024-006","2024-01-20","P001","Product A","Cat1","Sub1","North","NY","C001","John","100.0","2","0","Credit","S001","Alice","Direct"],
        # Negative amount (invalid)
        ["TX2024-007","2024-01-21","P001","Product A","Cat1","Sub1","North","NY","C006","Sarah","-50.0","1","0","Debit","S002","Bob","Online"],
        # Blank amount (invalid)
        ["TX2024-008","2024-01-22","P002","Product B","Cat2","Sub2","South","TX","C007","David","","2","0","Cash","S003","Charlie","Direct"],
        # Additional valid row for P002
        ["TX2024-009","2024-01-23","P002","Product B","Cat2","Sub2","South","TX","C008","Emma","200.0","1","0","Credit","S001","Alice","Direct"],
        # Valid row for P003
        ["TX2024-010","2024-01-24","P003","Product C","Cat3","Sub3","East","MA","C009","Tom","400.0","3","5","Credit","S002","Bob","Online"],
    ]

    with open("data/raw_sales_2024.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)

    # Interference file: old year data (2023)
    old_rows = [
        ["TX2023-001","2023-06-10","P001","Product A","Cat1","Sub1","North","NY","C010","Alice","300.0","4","0","Credit","S004","Dave","Direct"],
        ["TX2023-002","2023-06-11","P002","Product B","Cat2","Sub2","South","TX","C011","Bob","180.0","2","5","Cash","S001","Alice","Online"],
    ]
    with open("data/raw_sales_2023.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(old_rows)

    # Backup file (partial copy, should not be used)
    backup_rows = [
        ["TX2024-001","2024-01-15","P001","Product A","Cat1","Sub1","North","NY","C001","John","100.0","2","0","Credit","S001","Alice","Direct"],
        ["TX2024-003","2024-01-17","P002","Product B","Cat2","Sub2","South","TX","C003","Tom","150.0","1","0","Debit","S001","Alice","Direct"],
        ["TX2024-011","2024-01-25","P003","Product C","Cat3","Sub3","East","MA","C010","Mark","600.0","2","0","Cash","S004","Dave","Online"],
    ]
    with open("data/backup/raw_sales_2024_backup.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(backup_rows)

    # Noise file
    with open("data/notes.txt", "w") as f:
        f.write("This is just a note, ignore it.\n")

if __name__ == "__main__":
    build_env()
