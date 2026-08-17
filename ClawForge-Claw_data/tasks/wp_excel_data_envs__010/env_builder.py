import os
import csv

def build_env():
    # Create sales_raw.csv
    sales_rows = [
        ["T001","2024-01-15","P001","Sales Widget A","Widgets","Small","North","NYC","C001","Alice","100.0","2","0","Card","S001","Bob","Retail"],
        ["T002","2024-01-15","P001","Sales Widget A","Widgets","Small","North","NYC","C001","Alice","100.0","2","0","Card","S001","Bob","Retail"],  # duplicate of T001
        ["T003","2024-01-20","P002","","Widgets","Medium","South","LA","C002","Charlie","200.0","1","10","Cash","S002","Dave","Online"],
        ["T004","2024-02-10","P003","Sales Gadget B","Gadgets","Large","East","NYC","C003","Eve","150.0","3","5","Card","S003","Frank","Retail"],
        ["T005","2024-02-10","P003","Sales Gadget B","Gadgets","Large","East","NYC","C003","Eve","150.0","3","5","Card","S003","Frank","Retail"],  # duplicate of T004
        ["T006","2024-02-15","P002","","Widgets","Medium","South","LA","C002","Charlie","300.0","1","0","Transfer","S002","Dave","Online"],
        ["T007","2024-03-05","P001","Sales Widget A","Widgets","Small","North","NYC","C004","Grace","500.0","5","0","Card","S001","Bob","Retail"],
        ["T008","2024-03-05","P004","Sales Gadget C","Gadgets","Small","West","SF","C005","Heidi","250.0","2","15","Card","S004","Ivan","Online"],
        ["T009","2024-01-25","P001","Sales Widget A","Widgets","Small","North","NYC","C001","Alice","120.0","1","0","Card","S001","Bob","Retail"],
        ["T010","2024-02-20","P003","Sales Gadget B","Gadgets","Large","East","NYC","C003","Eve","180.0","2","10","Card","S003","Frank","Retail"],
    ]
    headers = [
        "transaction_id","date","product_id","product_name","category","subcategory",
        "region","city","customer_id","customer_name","sales_amount","quantity",
        "discount","payment_method","salesperson_id","salesperson_name","channel"
    ]
    with open("sales_raw.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(sales_rows)

    # Create product_reference.csv
    ref_rows = [
        ["P001","Sales Widget A","Widgets","Small"],
        ["P002","Sales Widget B","Widgets","Medium"],
        ["P003","Sales Gadget B","Gadgets","Large"],
        ["P004","Sales Gadget C","Gadgets","Small"],
    ]
    ref_headers = ["product_id","product_name","category","subcategory"]
    with open("product_reference.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(ref_headers)
        writer.writerows(ref_rows)

    # Add some distracting files (interference)
    os.makedirs("backup", exist_ok=True)
    with open("backup/old_sales.csv", "w") as f:
        f.write("placeholder")
    with open("notes.txt", "w") as f:
        f.write("ignore me")

if __name__ == "__main__":
    build_env()
