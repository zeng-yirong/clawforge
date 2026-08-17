import csv
import os
import random

random.seed(42)

def build_env():
    # Create directories
    os.makedirs("data/raw_data", exist_ok=True)
    os.makedirs("data/archive", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # Define column headers
    headers = [
        "transaction_id", "date", "product_id", "product_name", "category",
        "subcategory", "region", "city", "customer_id", "customer_name",
        "sales_amount", "quantity", "discount", "payment_method",
        "salesperson_id", "salesperson_name", "channel"
    ]

    # Generate base data with categories and some duplicates / missing values
    categories = ["Electronics", "Clothing", "Home", "Sports", "Books"]
    base_rows = []
    for cat in categories:
        for i in range(3):  # 3 base rows per category
            tid = f"TXN-{cat[:2].upper()}-{i+100}"
            row = [
                tid,
                "2024-01-15",
                f"PROD-{cat[:2].upper()}-{random.randint(100,999)}",
                f"{cat} Item {i+1}",
                cat,
                f"{cat} Sub",
                "North",
                "NYC",
                f"CUST-{random.randint(1000,9999)}",
                f"Customer {random.randint(1,99)}",
                str(round(random.uniform(10.0, 500.0), 2)),
                str(random.randint(1,5)),
                str(random.randint(0,20)),
                random.choice(["Credit Card", "Cash", "PayPal"]),
                f"SP-{random.randint(10,99)}",
                f"Salesperson {random.randint(1,20)}",
                "Online"
            ]
            base_rows.append(row)

    # Add duplicate row: repeat first Electronics row
    dup_row = base_rows[0].copy()
    base_rows.append(dup_row)

    # Add another duplicate: repeat third Clothing row
    dup_row2 = base_rows[3+1].copy()  # Clothing second row? index: 3*1? Actually Clothing start at index 3 (0-based), third Clothing is index 5? Let's compute
    # base_rows indices: 0-2 Electronics, 3-5 Clothing, 6-8 Home, 9-11 Sports, 12-14 Books. So third Clothing is index 5
    dup_row2 = base_rows[5].copy()
    base_rows.append(dup_row2)

    # Add a row with missing sales_amount (empty string)
    missing_row = base_rows[3].copy()  # first Clothing row
    missing_row[10] = ""  # sales_amount
    base_rows.append(missing_row)

    # Write main CSV
    with open("data/raw_data/sales_raw.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(base_rows)

    # Create a distracting old data file (with different content)
    old_rows = [
        ["OLD-001", "2023-12-01", "PROD-OLD-1", "Old Widget", "Electronics",
         "Old Sub", "East", "Boston", "CUST-OLD-1", "Old Customer",
         "99.99", "2", "10", "Check", "SP-99", "Old Sales", "Retail"],
        ["OLD-002", "2023-12-02", "PROD-OLD-2", "Old Gadget", "Clothing",
         "Old Sub", "West", "LA", "CUST-OLD-2", "Old Customer2",
         "49.99", "1", "0", "Cash", "SP-88", "Old Sales2", "Online"],
    ]
    with open("data/archive/sales_old.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(old_rows)

    # Create an empty placeholder (interference)
    with open("data/raw_data/.gitkeep", "w") as f:
        pass

if __name__ == "__main__":
    build_env()
