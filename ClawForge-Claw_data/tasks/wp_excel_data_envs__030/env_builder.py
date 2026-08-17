import os
import csv

def build_env():
    os.makedirs("data", exist_ok=True)
    os.makedirs("old_backup", exist_ok=True)
    os.makedirs("report", exist_ok=True)  # 预创建空目录，agent 可直接写入

    # 产品映射
    products = [
        {"product_id": "p1", "product_name": "手机", "category": "Electronics", "subcategory": "Mobile"},
        {"product_id": "p2", "product_name": "平板", "category": "Electronics", "subcategory": "Tablet"},
        {"product_id": "p3", "product_name": "笔记本", "category": "Electronics", "subcategory": "Laptop"},
        {"product_id": "p4", "product_name": "鼠标", "category": "Electronics", "subcategory": "Peripherals"},
        {"product_id": "p5", "product_name": "键盘", "category": "Electronics", "subcategory": "Peripherals"},
        {"product_id": "p6", "product_name": "T恤", "category": "Clothing", "subcategory": "Tops"},
        {"product_id": "p7", "product_name": "裤子", "category": "Clothing", "subcategory": "Pants"},
        {"product_id": "p8", "product_name": "帽子", "category": "Clothing", "subcategory": "Accessories"},
    ]
    with open("data/products.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["product_id", "product_name", "category", "subcategory"])
        w.writeheader()
        w.writerows(products)

    # 客户映射
    customers = [
        {"customer_id": "c1", "customer_name": "张三"},
        {"customer_id": "c2", "customer_name": "李四"},
        {"customer_id": "c3", "customer_name": "王五"},
        {"customer_id": "c4", "customer_name": "赵六"},
    ]
    with open("data/customers.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["customer_id", "customer_name"])
        w.writeheader()
        w.writerows(customers)

    # 原始销售数据（字段顺序与说明一致）
    fieldnames = [
        "transaction_id", "date", "product_id", "product_name",
        "category", "subcategory", "region", "city",
        "customer_id", "customer_name", "sales_amount",
        "quantity", "discount", "payment_method",
        "salesperson_id", "salesperson_name", "channel"
    ]
    rows = [
        # 正常记录
        {"transaction_id": "T001", "date": "2024-01-05", "product_id": "p1", "product_name": "手机",
         "category": "Electronics", "subcategory": "Mobile", "region": "North", "city": "Beijing",
         "customer_id": "c1", "customer_name": "张三", "sales_amount": "100", "quantity": "2",
         "discount": "10", "payment_method": "credit", "salesperson_id": "s1",
         "salesperson_name": "李销售", "channel": "online"},
        # 完全重复（整行相同）
        {"transaction_id": "T001", "date": "2024-01-05", "product_id": "p1", "product_name": "手机",
         "category": "Electronics", "subcategory": "Mobile", "region": "North", "city": "Beijing",
         "customer_id": "c1", "customer_name": "张三", "sales_amount": "100", "quantity": "2",
         "discount": "10", "payment_method": "credit", "salesperson_id": "s1",
         "salesperson_name": "李销售", "channel": "online"},
        # 缺失 product_name
        {"transaction_id": "T002", "date": "2024-01-06", "product_id": "p2", "product_name": "",
         "category": "Electronics", "subcategory": "Tablet", "region": "South", "city": "Shanghai",
         "customer_id": "c2", "customer_name": "李四", "sales_amount": "200", "quantity": "1",
         "discount": "0", "payment_method": "debit", "salesperson_id": "s2",
         "salesperson_name": "王销售", "channel": "store"},
        # 缺失 customer_name
        {"transaction_id": "T003", "date": "2024-01-07", "product_id": "p3", "product_name": "笔记本",
         "category": "Electronics", "subcategory": "Laptop", "region": "East", "city": "Hangzhou",
         "customer_id": "c3", "customer_name": "", "sales_amount": "500", "quantity": "1",
         "discount": "5", "payment_method": "credit", "salesperson_id": "s3",
         "salesperson_name": "赵销售", "channel": "online"},
        # 脏数据：负 sales_amount
        {"transaction_id": "T004", "date": "2024-01-08", "product_id": "p4", "product_name": "鼠标",
         "category": "Electronics", "subcategory": "Peripherals", "region": "West", "city": "Chengdu",
         "customer_id": "c4", "customer_name": "赵六", "sales_amount": "-20", "quantity": "3",
         "discount": "0", "payment_method": "cash", "salesperson_id": "s4",
         "salesperson_name": "刘销售", "channel": "store"},
        # 脏数据：负 quantity
        {"transaction_id": "T005", "date": "2024-01-09", "product_id": "p1", "product_name": "手机",
         "category": "Electronics", "subcategory": "Mobile", "region": "North", "city": "Beijing",
         "customer_id": "c1", "customer_name": "张三", "sales_amount": "100", "quantity": "-1",
         "discount": "10", "payment_method": "credit", "salesperson_id": "s1",
         "salesperson_name": "李销售", "channel": "online"},
        # 正常记录（Clothing 类别）
        {"transaction_id": "T006", "date": "2024-01-10", "product_id": "p6", "product_name": "T恤",
         "category": "Clothing", "subcategory": "Tops", "region": "South", "city": "Guangzhou",
         "customer_id": "c2", "customer_name": "李四", "sales_amount": "20", "quantity": "5",
         "discount": "0", "payment_method": "credit", "salesperson_id": "s2",
         "salesperson_name": "王销售", "channel": "online"},
        # 正常记录（Clothing 类别）
        {"transaction_id": "T007", "date": "2024-01-11", "product_id": "p7", "product_name": "裤子",
         "category": "Clothing", "subcategory": "Pants", "region": "East", "city": "Nanjing",
         "customer_id": "c3", "customer_name": "王五", "sales_amount": "50", "quantity": "3",
         "discount": "20", "payment_method": "debit", "salesperson_id": "s3",
         "salesperson_name": "赵销售", "channel": "store"},
        # 缺失 product_name 和 customer_name（可通过映射补全）
        {"transaction_id": "T008", "date": "2024-01-12", "product_id": "p8", "product_name": "",
         "category": "Clothing", "subcategory": "Accessories", "region": "North", "city": "Tianjin",
         "customer_id": "c1", "customer_name": "", "sales_amount": "30", "quantity": "2",
         "discount": "10", "payment_method": "cash", "salesperson_id": "s4",
         "salesperson_name": "刘销售", "channel": "store"},
        # 另一个正常记录（Electronics 类别）
        {"transaction_id": "T009", "date": "2024-02-01", "product_id": "p1", "product_name": "手机",
         "category": "Electronics", "subcategory": "Mobile", "region": "North", "city": "Beijing",
         "customer_id": "c1", "customer_name": "张三", "sales_amount": "150", "quantity": "1",
         "discount": "0", "payment_method": "credit", "salesperson_id": "s1",
         "salesperson_name": "李销售", "channel": "online"},
    ]

    with open("data/raw_sales.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    # 干扰文件
    with open("notes.txt", "w") as f:
        f.write("This is a note.\n")
    with open("old_backup/sales_2023.csv", "w") as f:
        f.write("transaction_id,date,product_id,sales_amount\n")
        f.write("O001,2023-12-01,p1,200\n")


if __name__ == "__main__":
    build_env()
