import os
import csv
import random

def build_env():
    # Ensure necessary directories
    os.makedirs("data/raw_data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # will be empty, agent creates file inside
    os.makedirs("old_data", exist_ok=True)  # decoy

    # --- Main sales data with duplicates ---
    rows = [
        ["transaction_id", "date", "product_id", "product_name", "category", "subcategory", "region", "city", "customer_id", "customer_name", "sales_amount", "quantity", "discount", "payment_method", "salesperson_id", "salesperson_name", "channel"],
        # Duplicate TX001 (2 times)
        ["TX001", "2024-03-01", "P100", "Widget A", "Electronics", "Accessories", "East", "New York", "C001", "Alice", 120.0, 2, 10, "Credit", "S001", "John", "Online"],
        ["TX001", "2024-03-02", "P100", "Widget A", "Electronics", "Accessories", "East", "New York", "C001", "Alice", 120.0, 2, 10, "Credit", "S001", "John", "Online"],
        # Duplicate TX002 (3 times)
        ["TX002", "2024-03-01", "P200", "Gadget B", "Electronics", "Gadgets", "West", "Los Angeles", "C002", "Bob", 250.0, 1, 5, "Cash", "S002", "Jane", "Retail"],
        ["TX002", "2024-03-03", "P200", "Gadget B", "Electronics", "Gadgets", "West", "Los Angeles", "C002", "Bob", 250.0, 1, 5, "Cash", "S002", "Jane", "Retail"],
        ["TX002", "2024-03-05", "P200", "Gadget B", "Electronics", "Gadgets", "West", "Los Angeles", "C002", "Bob", 250.0, 1, 5, "Cash", "S002", "Jane", "Retail"],
        # Single TX003 (no duplicate)
        ["TX003", "2024-03-02", "P300", "Doohickey C", "Home", "Kitchen", "North", "Chicago", "C003", "Carol", 80.0, 3, 0, "Debit", "S003", "Mike", "Online"],
        # Duplicate TX004 (2 times)
        ["TX004", "2024-03-04", "P400", "Thingamajig D", "Office", "Supplies", "South", "Houston", "C004", "Dave", 45.0, 5, 15, "Credit", "S004", "Lisa", "Retail"],
        ["TX004", "2024-03-06", "P400", "Thingamajig D", "Office", "Supplies", "South", "Houston", "C004", "Dave", 45.0, 5, 15, "Credit", "S004", "Lisa", "Retail"],
        # Single TX005 (no duplicate)
        ["TX005", "2024-03-07", "P500", "Widget E", "Electronics", "Accessories", "East", "Boston", "C005", "Eve", 200.0, 2, 20, "Cash", "S005", "Tom", "Online"],
    ]
    with open("data/raw_data/sales_raw.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    # --- Decoy: an older version of sales data (different duplicates to confuse) ---
    old_rows = [
        ["transaction_id", "date", "product_id", "product_name", "category", "subcategory", "region", "city", "customer_id", "customer_name", "sales_amount", "quantity", "discount", "payment_method", "salesperson_id", "salesperson_name", "channel"],
        ["TX001", "2023-12-01", "P100", "Widget A", "Electronics", "Accessories", "East", "New York", "C001", "Alice", 115.0, 2, 10, "Credit", "S001", "John", "Online"],
        ["TX006", "2023-12-02", "P600", "Gizmo F", "Home", "Tools", "West", "San Francisco", "C006", "Frank", 300.0, 1, 0, "Credit", "S006", "Sara", "Retail"],
    ]
    with open("old_data/sales_2023.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(old_rows)

    # --- Decoy: accounts.csv (irrelevant) ---
    accounts = [
        ["account_id", "display_name", "role", "email"],
        ["A001", "Alice", "Sales", "alice@co.com"],
        ["A002", "Bob", "Marketing", "bob@co.com"],
    ]
    with open("data/accounts.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(accounts)

if __name__ == "__main__":
    build_env()
