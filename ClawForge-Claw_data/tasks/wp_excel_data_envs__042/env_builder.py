import os
import csv

def build_env():
    # accounts.csv
    accounts = [
        ["customer_id", "customer_name"],
        ["C001", "Alice"],
        ["C002", "Bob"],
        ["C003", "Charlie"]
    ]
    with open("accounts.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(accounts)

    # raw_data/ directory
    os.makedirs("raw_data", exist_ok=True)
    os.makedirs("old_data", exist_ok=True)  # distractor

    # sales_jan.csv
    jan = [
        ["transaction_id","date","product_id","product_name","customer_id","customer_name","sales_amount","quantity"],
        ["T001","2024-01-01","P001","Product A","C001","Alice","100.0","2"],
        ["T002","2024-01-02","P001","Product A","C002","","150.0","3"],
        ["T003","2024-01-03","P002","Product B","C003","Charlie","200.0","1"],
        ["T004","2024-01-04","P003","Product C","C001","Alice","50.0","0"],
        ["T005","2024-01-05","P001","Product A","C003","Charlie","80.0","4"]
    ]
    with open("raw_data/sales_jan.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(jan)

    # sales_feb.csv
    feb = [
        ["transaction_id","date","product_id","product_name","customer_id","customer_name","sales_amount","quantity"],
        ["T001","2024-02-01","P001","Product A","C001","Alice","100.0","2"],
        ["T006","2024-02-02","P002","Product B","C002","Bob","300.0","2"],
        ["T007","2024-02-03","P001","Product A","C001","Alice","120.0","-5"],
        ["T008","2024-02-04","P003","Product C","C003","Charlie","250.0","1"]
    ]
    with open("raw_data/sales_feb.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(feb)

    # sales_mar.csv
    mar = [
        ["transaction_id","date","product_id","product_name","customer_id","customer_name","sales_amount","quantity"],
        ["T009","2024-03-01","P001","Product A","C004","","90.0","2"],
        ["T010","2024-03-02","P002","Product B","C002","Bob","400.0","3"],
        ["T011","2024-03-03","P003","Product C","C001","Alice","60.0","1"],
        ["T012","2024-03-04","P001","Product A","C003","Charlie","110.0","2"]
    ]
    with open("raw_data/sales_mar.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(mar)

    # distractor: old_data/backup.csv (different format, should be ignored)
    old = [
        ["id","name","value"],
        ["1","xxx","100"]
    ]
    with open("old_data/backup.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(old)

if __name__ == "__main__":
    build_env()
