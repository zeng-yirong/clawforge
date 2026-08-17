import os

def build_env():
    # Create directories
    os.makedirs("raw_data", exist_ok=True)
    os.makedirs("archive", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    # Main sales data
    sales_lines = [
        "transaction_id,date,product_id,product_name,category,subcategory,region,city,customer_id,customer_name,sales_amount,quantity,discount,payment_method,salesperson_id,salesperson_name,channel",
        "T001,2024-01-05,P001,Widget A,Widgets,Small,North,NYC,C001,Alice,100.0,2,0,card,SP001,Bob,Online",
        "T001,2024-01-05,P001,Widget A,Widgets,Small,North,NYC,C001,Alice,100.0,2,0,card,SP001,Bob,Online",  # duplicate
        "T002,2024-01-10,P002,Gadget B,Gadgets,Large,South,LA,C002,Bob,250.0,1,10,cash,SP002,Charlie,Store",
        "T003,2024-01-15,P003,Widget C,Widgets,Medium,East,Boston,C003,Carol,,3,5,card,SP001,Bob,Online",  # missing sales_amount
        "T004,2024-01-20,P004,Gadget D,Gadgets,Small,West,Seattle,C001,Alice,150.0,4,0,paypal,SP002,Charlie,Online",
        "T005,2024-01-25,P005,Widget E,Widgets,Large,North,Chicago,C004,Dave,200.0,1,20,cash,SP003,Diana,Store",
        "T006,2024-02-01,P001,Widget A,Widgets,Small,North,NYC,C001,Alice,110.0,2,0,card,SP001,Bob,Online",
        "T007,2024-02-05,P002,Gadget B,Gadgets,Large,South,LA,C002,Bob,260.0,1,10,cash,SP002,Charlie,Store",
        "T008,2024-02-10,P003,Widget C,Widgets,Medium,East,Boston,C003,Carol,120.0,3,5,card,SP001,Bob,Online",
        "T009,2024-02-15,P004,Gadget D,Gadgets,Small,West,Seattle,C001,Alice,160.0,4,0,paypal,SP002,Charlie,Online",
        "T010,2024-02-20,P005,Widget E,Widgets,Large,North,Chicago,C004,Dave,210.0,1,20,cash,SP003,Diana,Store",
    ]
    with open("raw_data/sales_master.csv", "w") as f:
        f.write("\n".join(sales_lines))

    # Interference: old_data
    old_lines = [
        "id,value",
        "1,10",
        "2,20",
    ]
    with open("raw_data/old_sales.csv", "w") as f:
        f.write("\n".join(old_lines))

    # Archive placeholder
    with open("archive/backup.zip", "w") as f:
        f.write("dummy zip content")

    # Log file
    with open("logs/startup.log", "w") as f:
        f.write("2024-01-01 INFO started")

    # Readme
    with open("README.txt", "w") as f:
        f.write("This is the workspace for sales data processing.\n")

if __name__ == "__main__":
    build_env()
