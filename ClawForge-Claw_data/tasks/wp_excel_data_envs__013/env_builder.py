import os
import csv
import random

def build_env():
    # Ensure base directories exist
    os.makedirs("data/raw_data", exist_ok=True)
    os.makedirs("data/archived", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("temp", exist_ok=True)

    # --- product_categories.csv (lookup table) ---
    categories = [
        {"product_id": "P001", "product_name": "Alpha", "category": "Electronics"},
        {"product_id": "P002", "product_name": "Beta", "category": "Home"},
        {"product_id": "P003", "product_name": "Gamma", "category": "Office"},
        {"product_id": "P004", "product_name": "Delta", "category": "Sports"},
    ]
    with open("data/product_categories.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["product_id", "product_name", "category"])
        writer.writeheader()
        writer.writerows(categories)

    # --- sales_raw.csv (with duplicates, missing category, negative amounts) ---
    # Define 8 unique transactions (all amounts positive, each duplicated once = 16 rows)
    # T003 has empty category (will be filled from lookup)
    transactions = [
        ("T001", "2023-01-01", "P001", "Alpha", "Electronics", "SubA", "North", "NYC", "C001", "Cust1", 100.0, 1, 0, "credit", "SP1", "Alice", "online"),
        ("T002", "2023-01-02", "P002", "Beta", "Home", "SubB", "South", "LA", "C002", "Cust2", 200.0, 2, 0, "cash", "SP2", "Bob", "store"),
        ("T003", "2023-01-03", "P003", "Gamma", "", "SubC", "East", "CHI", "C003", "Cust3", 300.0, 3, 0, "credit", "SP3", "Charlie", "online"),
        ("T004", "2023-01-04", "P004", "Delta", "Sports", "SubD", "West", "SF", "C004", "Cust4", 400.0, 4, 0, "cash", "SP4", "Dave", "store"),
        ("T005", "2023-01-05", "P001", "Alpha", "Electronics", "SubA", "North", "NYC", "C005", "Cust5", 500.0, 1, 0, "credit", "SP1", "Alice", "online"),
        ("T006", "2023-01-06", "P002", "Beta", "Home", "SubB", "South", "LA", "C006", "Cust6", 600.0, 2, 0, "cash", "SP2", "Bob", "store"),
        ("T007", "2023-01-07", "P003", "Gamma", "Office", "SubC", "East", "CHI", "C007", "Cust7", 700.0, 3, 0, "credit", "SP3", "Charlie", "online"),
        ("T008", "2023-01-08", "P004", "Delta", "Sports", "SubD", "West", "SF", "C008", "Cust8", 800.0, 4, 0, "cash", "SP4", "Dave", "store"),
    ]
    # Add each transaction as written, then duplicate
    rows = []
    for t in transactions:
        rows.append(t)
        rows.append(t)  # exact duplicate

    # Add a few dirty rows with negative/zero amount (these are not in the 8 unique, but extra)
    dirty = [
        ("T009", "2023-01-09", "P001", "Alpha", "Electronics", "SubA", "North", "NYC", "C009", "Cust9", -100.0, 1, 0, "credit", "SP1", "Alice", "online"),
        ("T010", "2023-01-10", "P002", "Beta", "Home", "SubB", "South", "LA", "C010", "Cust10", 0.0, 1, 0, "cash", "SP2", "Bob", "store"),
    ]
    # Add each dirty row twice (also duplicates)
    for d in dirty:
        rows.append(d)
        rows.append(d)

    # Shuffle to make it realistic
    random.shuffle(rows)

    fieldnames = [
        "transaction_id", "date", "product_id", "product_name", "category",
        "subcategory", "region", "city", "customer_id", "customer_name",
        "sales_amount", "quantity", "discount", "payment_method",
        "salesperson_id", "salesperson_name", "channel"
    ]
    with open("data/raw_data/sales_raw.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(fieldnames)
        writer.writerows(rows)

    # --- Interference files ---
    # Old version of sales data (different numbers)
    old_rows = [
        ("T001", "2022-12-01", "P001", "Alpha", "Electronics", "SubA", "North", "NYC", "C001", "Cust1", 50.0, 1, 0, "credit", "SP1", "Alice", "online"),
        ("T002", "2022-12-02", "P002", "Beta", "Home", "SubB", "South", "LA", "C002", "Cust2", 70.0, 2, 0, "cash", "SP2", "Bob", "store"),
    ]
    with open("data/archived/sales_old.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(fieldnames)
        writer.writerows(old_rows)

    # Dummy log file
    with open("temp/process.log", "w") as f:
        f.write("INFO: Data loaded\nWARN: Duplicates detected\nINFO: Cleaning started\n")

if __name__ == "__main__":
    build_env()
