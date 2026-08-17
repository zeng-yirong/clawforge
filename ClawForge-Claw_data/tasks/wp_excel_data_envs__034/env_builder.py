import os
import csv
import random
import math

def build_env():
    # Create raw_data directory
    os.makedirs("raw_data", exist_ok=True)
    os.makedirs("raw_data/backup", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # Define fieldnames matching the schema
    fields = [
        "transaction_id", "date", "product_id", "product_name", "category",
        "subcategory", "region", "city", "customer_id", "customer_name",
        "sales_amount", "quantity", "discount", "payment_method",
        "salesperson_id", "salesperson_name", "channel"
    ]

    # ---------- Build clean base data (2024 + 2025) ----------
    # We'll create 50 unique transactions with realistic values.
    base_rows = []
    for i in range(1, 51):
        tid = f"TXN{i:04d}"
        year = 2024 if i <= 30 else 2025
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        date_str = f"{year}-{month:02d}-{day:02d}"
        product_id = f"P{random.randint(100,999)}"
        product_name = random.choice(["Widget A", "Gadget B", "Thingamajig C", "Doodad D", "Contraption E"])
        category = random.choice(["Electronics", "Home", "Sports", "Books", "Clothing"])
        subcategory = random.choice(["Accessories", "Parts", "Full Set"])
        region = random.choice(["North", "South", "East", "West"])
        city = random.choice(["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"])
        customer_id = f"C{random.randint(1000,9999)}"
        customer_name = random.choice(["Alice Brown", "Bob Smith", "Charlie Davis", "Diana Lee", "Eve Wang"])
        sales_amount = round(random.uniform(20.0, 500.0), 2)
        quantity = random.randint(1, 10)
        discount = random.choice([0, 5, 10, 15, 20])
        payment_method = random.choice(["Credit Card", "PayPal", "Bank Transfer", "Cash"])
        salesperson_id = f"SP{random.randint(1,20):02d}"
        salesperson_name = random.choice(["John", "Jane", "Mike", "Lisa", "Tom"])
        channel = random.choice(["Online", "Retail", "Wholesale"])
        base_rows.append({
            "transaction_id": tid,
            "date": date_str,
            "product_id": product_id,
            "product_name": product_name,
            "category": category,
            "subcategory": subcategory,
            "region": region,
            "city": city,
            "customer_id": customer_id,
            "customer_name": customer_name,
            "sales_amount": str(sales_amount),
            "quantity": str(quantity),
            "discount": str(discount),
            "payment_method": payment_method,
            "salesperson_id": salesperson_id,
            "salesperson_name": salesperson_name,
            "channel": channel
        })

    # Write 2024 file (first 30 transactions)
    with open("raw_data/orders_2024.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in base_rows[:30]:
            writer.writerow(row)

    # Write 2025 file (remaining 20 transactions)
    with open("raw_data/orders_2025.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in base_rows[30:]:
            writer.writerow(row)

    # ---------- Inject duplicates and dirty data ----------
    # We'll modify the 2025 file in-place to add:
    # - Duplicate rows with same transaction_id but different amounts (some valid, some invalid)
    # - Missing sales_amount on some duplicates
    # - A few rows with negative or zero amounts (test entries)
    # - One row with invalid date

    # Read existing 2025 rows
    rows_2025 = []
    with open("raw_data/orders_2025.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows_2025.append(row)

    # Add duplicates: pick last 4 transactions (TXN0031, TXN0032, TXN0033, TXN0034) 
    # and create duplicate rows with slightly different amounts (one valid, one invalid)
    for i in range(1, 5):
        tid = f"TXN{30+i:04d}"
        # Find index of original row
        orig_index = None
        for idx, row in enumerate(rows_2025):
            if row["transaction_id"] == tid:
                orig_index = idx
                break
        if orig_index is not None:
            orig = rows_2025[orig_index]
            # Duplicate 1: valid amount (same as original) – exactly the same row
            rows_2025.append(orig.copy())
            # Duplicate 2: invalid amount (negative)
            dup_invalid = orig.copy()
            dup_invalid["sales_amount"] = str(-random.uniform(10.0, 100.0))
            rows_2025.append(dup_invalid)
            # Duplicate 3: missing sales_amount (empty string)
            dup_missing = orig.copy()
            dup_missing["sales_amount"] = ""
            rows_2025.append(dup_missing)

    # Add a few pure junk rows (bogus transaction IDs, negative amounts, invalid date)
    junk_rows = [
        {
            "transaction_id": "TEST001",
            "date": "2025-01-01",
            "product_id": "P999",
            "product_name": "Test Product",
            "category": "Test",
            "subcategory": "Test",
            "region": "Test",
            "city": "Test",
            "customer_id": "C0000",
            "customer_name": "Test User",
            "sales_amount": "-100.00",
            "quantity": "0",
            "discount": "0",
            "payment_method": "Cash",
            "salesperson_id": "SP99",
            "salesperson_name": "Test",
            "channel": "Test"
        },
        {
            "transaction_id": "TXN0000",
            "date": "2025-13-01",  # invalid month
            "product_id": "P777",
            "product_name": "Bogus",
            "category": "Bogus",
            "subcategory": "Bogus",
            "region": "Bogus",
            "city": "Bogus",
            "customer_id": "C9876",
            "customer_name": "Bogus",
            "sales_amount": "0.00",
            "quantity": "5",
            "discount": "0",
            "payment_method": "Cash",
            "salesperson_id": "SP99",
            "salesperson_name": "Bogus",
            "channel": "Bogus"
        }
    ]
    rows_2025.extend(junk_rows)

    # Shuffle rows to mix duplicates
    random.shuffle(rows_2025)

    # Write back modified 2025 file
    with open("raw_data/orders_2025.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows_2025)

    # ---------- Create backup folder with old data (interference) ----------
    # a few rows with different amounts (outdated)
    backup_rows = []
    for i in range(1, 11):
        tid = f"TXN{i:04d}"
        backup_rows.append({
            "transaction_id": tid,
            "date": "2023-06-15",
            "product_id": "P000",
            "product_name": "Legacy Widget",
            "category": "Old",
            "subcategory": "Discontinued",
            "region": "Central",
            "city": "Dallas",
            "customer_id": "C0001",
            "customer_name": "Old Customer",
            "sales_amount": str(random.uniform(10.0, 200.0)),
            "quantity": "1",
            "discount": "0",
            "payment_method": "Check",
            "salesperson_id": "SP00",
            "salesperson_name": "Legacy",
            "channel": "Mail"
        })
    with open("raw_data/backup/orders_2024_old.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(backup_rows)

if __name__ == "__main__":
    build_env()
