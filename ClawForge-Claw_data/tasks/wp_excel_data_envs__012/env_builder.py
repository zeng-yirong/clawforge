import os

def build_env():
    # Ensure ops directory exists (empty, agent will write into it)
    os.makedirs("ops", exist_ok=True)

    # Product catalog – used for filling missing sale_amount
    products_content = "product_id,category,suggested_retail_price\n" \
                       "P001,Electronics,1500\n" \
                       "P002,Clothing,50\n" \
                       "P003,Food,10\n"
    with open("products.csv", "w") as f:
        f.write(products_content)

    # Raw sales data with duplicates, missing amounts, and a negative amount
    sales_content = "transaction_id,product_id,sale_amount,quantity,date\n" \
                    "T001,P001,1600,1,2024-03-01\n" \
                    "T001,P001,1600,1,2024-03-01\n" \
                    "T002,P001,,2,2024-03-02\n" \
                    "T003,P002,60,1,2024-03-03\n" \
                    "T004,P003,-5,1,2024-03-04\n" \
                    "T005,P003,12,1,2024-03-05\n" \
                    "T006,P002,55,2,2024-03-06\n"
    with open("raw_sales.csv", "w") as f:
        f.write(sales_content)

if __name__ == "__main__":
    build_env()
