import os
import csv

def build_env():
    os.makedirs("data/raw_data", exist_ok=True)
    # 创建干扰目录，但不创建结果目录（由agent创建）
    
    headers = ["transaction_id","date","product_id","product_name","category","subcategory","region","city","customer_id","customer_name","sales_amount","quantity","discount","payment_method","salesperson_id","salesperson_name","channel"]
    
    rows = [
        ["T001","2023-01-15","P001","Widget A","Electronics","Gadgets","North","New York","C001","Alice","120.00","2","0","Credit","S001","John","Online"],
        ["T001","2023-01-15","P001","Widget A","Electronics","Gadgets","North","New York","C001","Alice","120.00","2","0","Credit","S001","John","Online"],  # duplicate
        ["T002","2023-01-16","P002","Shirt B","Clothing","Apparel","South","Dallas","C002","Bob","45.00","1","0","Cash","S002","Jane","Store"],
        ["T002","2023-01-16","P002","Shirt B","Clothing","Apparel","South","Dallas","C002","Bob","45.00","1","0","Cash","S002","Jane","Store"],  # duplicate
        ["T003","2023-01-17","P003","Shoes C","Footwear","Sneakers","East","Boston","C003","Carol","90.00","1","10","Debit","S003","Mike","Online"],
        ["T004","2023-01-18","P004","Hat D","Clothing","Accessories","West","Seattle","C004","Dave","24.00","3","5","Credit","S004","Lucy","Store"],
        ["T004","2023-01-18","P004","Hat D","Clothing","Accessories","West","Seattle","C004","Dave","24.00","3","5","Credit","S004","Lucy","Store"],  # duplicate
        ["T004","2023-01-18","P004","Hat D","Clothing","Accessories","West","Seattle","C004","Dave","24.00","3","5","Credit","S004","Lucy","Store"],  # duplicate
        ["T005","2023-01-19","P005","Phone E","Electronics","Phones","North","Chicago","C005","Eve","480.00","1","0","Credit","S001","John","Online"],
        ["T005","2023-01-19","P005","Phone E","Electronics","Phones","North","Chicago","C005","Eve","480.00","1","0","Credit","S001","John","Online"],  # duplicate
        ["T006","2023-01-20","P006","Socks F","Clothing","Socks","South","Miami","C006","Frank","12.00","10","0","Cash","S002","Jane","Store"],
        ["T007","2023-01-21","P007","Boots G","Footwear","Boots","East","Philadelphia","C007","Grace","150.00","1","15","Credit","S003","Mike","Online"],
        ["T007","2023-01-21","P007","Boots G","Footwear","Boots","East","Philadelphia","C007","Grace","150.00","1","15","Credit","S003","Mike","Online"],  # duplicate
    ]
    
    with open("data/raw_data/sales_raw.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    
    # 干扰文件
    old_headers = headers
    old_rows = [
        ["O001","2022-06-15","P001","Widget A","Electronics","Gadgets","North","New York","C001","Alice","100.00","2","0","Credit","S001","John","Online"],
        ["O002","2022-07-20","P002","Shirt B","Clothing","Apparel","South","Dallas","C002","Bob","40.00","1","0","Cash","S002","Jane","Store"],
    ]
    with open("data/old_sales.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(old_headers)
        writer.writerows(old_rows)
    
    # 额外干扰文件
    accounts_headers = ["account_id","display_name","role","email"]
    accounts_rows = [
        ["ACC001","Alice","Analyst","alice@example.com"],
        ["ACC002","Bob","Manager","bob@example.com"],
    ]
    os.makedirs("data", exist_ok=True)
    with open("data/accounts.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(accounts_headers)
        writer.writerows(accounts_rows)

if __name__ == "__main__":
    build_env()
