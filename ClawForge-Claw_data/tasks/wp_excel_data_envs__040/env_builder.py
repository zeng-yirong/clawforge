import os
import csv
import random

def build_env():
    # 确保目录存在
    os.makedirs("data", exist_ok=True)
    os.makedirs("backup", exist_ok=True)

    # 1. 主销售数据 sales_raw.csv（包含重复行、缺失 product_name）
    rows = []
    # 正常记录
    rows.append(["T001","2024-01-10","P001","Widget A","Electronics","Gadgets","North","New York","C001","Alice","120.50","2","0","Credit","S001","John","Online"])
    rows.append(["T002","2024-01-11","P002","","Electronics","Accessories","South","Atlanta","C002","Bob","45.00","3","10","Cash","S002","Jane","Retail"])
    rows.append(["T003","2024-01-12","P001","Widget A","Electronics","Gadgets","East","Boston","C003","Charlie","67.80","1","0","Debit","S001","John","Online"])
    rows.append(["T004","2024-01-13","P003","Gadget X","Home","Kitchen","West","Seattle","C004","Diana","210.00","5","5","Credit","S003","Tom","Retail"])
    rows.append(["T005","2024-01-14","P002","","Electronics","Accessories","North","Chicago","C005","Eve","89.90","2","0","Cash","S002","Jane","Online"])
    # 重复行（完全重复 T001）
    rows.append(["T001","2024-01-10","P001","Widget A","Electronics","Gadgets","North","New York","C001","Alice","120.50","2","0","Credit","S001","John","Online"])
    # 重复行（完全重复 T003）
    rows.append(["T003","2024-01-12","P001","Widget A","Electronics","Gadgets","East","Boston","C003","Charlie","67.80","1","0","Debit","S001","John","Online"])
    # 干扰脏数据：quantity 为负数（应视为无效，但 prompt 未要求剔除，我们不剔除，只要求去重和填充）
    rows.append(["T006","2024-01-15","P001","Widget A","Electronics","Gadgets","South","Miami","C006","Frank","55.00","-1","0","Credit","S001","John","Online"])
    # 干扰脏数据：sales_amount 为空字符串（视为缺失，保留但可能影响计算，我们保留以便 agent 处理？agent 需计算平均，空字符串会导致报错，最好让 agent 过滤或转换。但我们可设计为有效数字。为了简洁，不用空字符串，用正常值）
    # 改用另一个正常记录
    rows.append(["T007","2024-01-16","P003","Gadget X","Home","Kitchen","East","DC","C007","Grace","130.25","3","10","Debit","S003","Tom","Retail"])

    # 写文件
    header = ["transaction_id","date","product_id","product_name","category","subcategory","region","city","customer_id","customer_name","sales_amount","quantity","discount","payment_method","salesperson_id","salesperson_name","channel"]
    with open("data/sales_raw.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)

    # 2. 产品映射表 product_mapping.csv
    mapping = [
        ["P001","Widget A"],
        ["P002","Gadget Y"],
        ["P003","Gadget X"],
        ["P004","Premium Widget"]  # 这个不在主数据中出现，作为诱饵
    ]
    with open("data/product_mapping.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["product_id","product_name"])
        writer.writerows(mapping)

    # 3. 干扰文件：旧数据
    old_rows = [
        ["T001","2024-01-10","P001","Widget A","Electronics","Gadgets","North","New York","C001","Alice","120.50","2","0","Credit","S001","John","Online"],
        ["T002","2024-01-11","P002","","Electronics","Accessories","South","Atlanta","C002","Bob","45.00","3","10","Cash","S002","Jane","Retail"]
    ]
    with open("data/old_sales.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(old_rows)

    # 4. 备份目录下的干扰文件
    with open("backup/sales_backup.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows[:3])  # 仅前三条

    print("环境构建完成：data/sales_raw.csv, data/product_mapping.csv, 干扰文件已生成。")

if __name__ == "__main__":
    build_env()
