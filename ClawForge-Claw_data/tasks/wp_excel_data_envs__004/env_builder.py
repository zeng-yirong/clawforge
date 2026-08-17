import os
import csv

def build_env():
    # 创建原始数据目录
    os.makedirs("raw_data", exist_ok=True)
    os.makedirs("results", exist_ok=True)  # 虽然 agent 会创建，但这里提前建好防止干扰

    # 写入 products.csv (价目表)
    products = [
        ["product_id","product_name","standard_price"],
        ["P001","Widget A","150.0"],
        ["P002","Widget B","180.0"],
        ["P003","Widget C","300.0"]
    ]
    with open("raw_data/products.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(products)

    # 写入 sales.csv (原始数据，包含重复行和缺失金额)
    sales = [
        ["transaction_id","date","product_id","product_name","category","subcategory","region","city","customer_id","customer_name","sales_amount","quantity","discount","payment_method","salesperson_id","salesperson_name","channel"],
        ["1","2023-01-01","P001","Widget A","Electronics","Gadgets","North","NYC","C001","John","100.0","2","0","Cash","S001","Alice","Online"],
        ["2","2023-01-01","P002","Widget B","Electronics","Gadgets","South","LA","C002","Jane","200.0","1","10","Card","S002","Bob","Retail"],
        ["2","2023-01-01","P002","Widget B","Electronics","Gadgets","South","LA","C002","Jane","200.0","1","10","Card","S002","Bob","Retail"],  # 完全重复行
        ["3","2023-01-02","P001","Widget A","Electronics","Gadgets","North","NYC","C001","John","","3","0","Cash","S001","Alice","Online"],  # 缺失金额
        ["4","2023-01-03","P003","Widget C","Electronics","Gadgets","East","Boston","C003","Jim","350.0","1","5","Card","S003","Eve","Retail"],  # 正常行，产品 P003
    ]
    with open("raw_data/sales.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(sales)

    # 干扰目录与文件
    os.makedirs("raw_data/backup", exist_ok=True)
    with open("raw_data/backup/old_sales.csv", "w", newline="") as f:
        f.write("transaction_id,date,product_id,sales_amount\n")
        f.write("9,2022-12-01,P001,90.0\n")  # 旧数据，不应该被使用

if __name__ == "__main__":
    build_env()
