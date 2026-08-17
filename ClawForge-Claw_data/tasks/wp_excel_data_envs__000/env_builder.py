import os
import csv
import random

def build_env():
    # Create input data directory
    os.makedirs("data", exist_ok=True)

    # Define raw sales data with carefully crafted duplicates, missing names, and junk rows
    rows = [
        # Normal clean rows
        ["T001", "2024-01-10", "P100", "Widget A", "Widgets", "Sub-widget", "North", "NYC", "C001", "Alice", 120.50, 2, 10, "Card", "SP01", "Bob", "Retail"],
        ["T002", "2024-01-11", "P101", "Gadget B", "Gadgets", "Sub-gadget", "South", "Austin", "C002", "Bob", 250.00, 1, 5, "Cash", "SP02", "Carol", "Online"],
        ["T003", "2024-01-12", "P102", "Widget C", "Widgets", "Sub-widget", "East", "Boston", "C003", "Charlie", 99.99, 3, 0, "Card", "SP03", "Dave", "Retail"],
        # Duplicates of T001 (exact copy)
        ["T001", "2024-01-10", "P100", "Widget A", "Widgets", "Sub-widget", "North", "NYC", "C001", "Alice", 120.50, 2, 10, "Card", "SP01", "Bob", "Retail"],
        ["T001", "2024-01-10", "P100", "Widget A", "Widgets", "Sub-widget", "North", "NYC", "C001", "Alice", 120.50, 2, 10, "Card", "SP01", "Bob", "Retail"],
        # Duplicate of T002 with different quantity? We'll make it exact.
        ["T002", "2024-01-11", "P101", "Gadget B", "Gadgets", "Sub-gadget", "South", "Austin", "C002", "Bob", 250.00, 1, 5, "Cash", "SP02", "Carol", "Online"],
        # Missing product name but product ID P100 already has name "Widget A"
        ["T004", "2024-01-13", "P100", "", "Widgets", "Sub-widget", "North", "Chicago", "C004", "Diana", 300.00, 5, 15, "Transfer", "SP01", "Bob", "Retail"],
        ["T005", "2024-01-14", "P101", "", "Gadgets", "Sub-gadget", "West", "SF", "C005", "Eve", 175.25, 2, 8, "Card", "SP02", "Carol", "Online"],
        # Missing product name for a product ID that appears only once (P999) – cannot be filled → drop later
        ["T006", "2024-01-15", "P999", "", "Unknown", "Sub", "East", "Philadelphia", "C006", "Frank", 50.00, 1, 0, "Cash", "SP04", "Grace", "Retail"],
        # Junk rows (zero/negative amounts or quantities)
        ["T007", "2024-01-16", "P102", "Widget C", "Widgets", "Sub-widget", "West", "Seattle", "C007", "Grace", 0.00, 3, 10, "Card", "SP03", "Dave", "Online"],
        ["T008", "2024-01-17", "P103", "Gadget D", "Gadgets", "Sub-gadget", "South", "Miami", "C008", "Heidi", -50.00, 1, 5, "Cash", "SP02", "Carol", "Retail"],
        ["T009", "2024-01-18", "P104", "Widget E", "Widgets", "Sub-widget", "North", "Detroit", "C009", "Ivan", 100.00, 0, 20, "Card", "SP01", "Bob", "Retail"],
        # One more clean row
        ["T010", "2024-01-19", "P105", "Gadget F", "Gadgets", "Sub-gadget", "East", "NYC", "C010", "Judy", 500.00, 4, 12, "Transfer", "SP02", "Carol", "Online"],
    ]

    with open("data/sales_raw.csv", "w", newline="") as f:
        writer = csv.writer(f)
        # Header
        writer.writerow([
            "transaction_id", "date", "product_id", "product_name", "category",
            "subcategory", "region", "city", "customer_id", "customer_name",
            "sales_amount", "quantity", "discount", "payment_method",
            "salesperson_id", "salesperson_name", "channel"
        ])
        # Shuffle rows to avoid order bias (but we guarantee first occurrence rule)
        random.shuffle(rows)
        writer.writerows(rows)

    # Create some distracting files/directories
    os.makedirs("backup", exist_ok=True)
    with open("backup/old_sales_2023.csv", "w") as f:
        f.write("dummy,data\n")

    with open("notes.txt", "w") as f:
        f.write("Samantha's scratch notes – ignore\n")

    # Do NOT create report/ directory; agent must create it
    print("Environment built: data/sales_raw.csv and other files.")

if __name__ == "__main__":
    build_env()
