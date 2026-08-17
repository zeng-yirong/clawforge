import os
import csv
import random
import json

def build_env():
    # Create directories
    os.makedirs("data/raw_sales", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # Write a dummy placeholder in ops to verify agent overwrites later (optional)
    with open("ops/channel_avg.json", "w") as f:
        json.dump({"status": "not_done"}, f)

    # Define base clean data (10 unique transactions across channels)
    # We'll embed some known average values: 
    # Channel A: amounts [1200.0, 850.0, 1500.0, None] -> after clean: [1200.0, 850.0, 1500.0] avg = 1183.33
    # Channel B: amounts [340.0, 210.0, 560.0, 400.0] -> avg = 377.50
    # Channel C: amounts [2000.0, 1750.0, 2200.0, 1950.0] -> avg = 1975.00
    # Also add duplicates, missing, bad format records

    base_rows = [
        {"transaction_id": "TXN-000001", "date": "2023-07-01", "product_id": "P-001", "product_name": "Widget A", "category": "Widgets", "subcategory": "Basic", "region": "North", "city": "NYC", "customer_id": "C-100", "customer_name": "Alice", "sales_amount": 1200.0, "quantity": 2, "discount": 0, "payment_method": "Credit", "salesperson_id": "S-01", "salesperson_name": "Tom", "channel": "Online"},
        {"transaction_id": "TXN-000002", "date": "2023-07-02", "product_id": "P-002", "product_name": "Widget B", "category": "Widgets", "subcategory": "Pro", "region": "South", "city": "ATL", "customer_id": "C-101", "customer_name": "Bob", "sales_amount": 850.0, "quantity": 1, "discount": 5, "payment_method": "Debit", "salesperson_id": "S-02", "salesperson_name": "Jerry", "channel": "Online"},
        {"transaction_id": "TXN-000003", "date": "2023-07-03", "product_id": "P-003", "product_name": "Gadget X", "category": "Gadgets", "subcategory": "Standard", "region": "East", "city": "BOS", "customer_id": "C-102", "customer_name": "Carol", "sales_amount": 1500.0, "quantity": 3, "discount": 10, "payment_method": "Cash", "salesperson_id": "S-03", "salesperson_name": "Kate", "channel": "In-Store"},
        {"transaction_id": "TXN-000004", "date": "2023-07-04", "product_id": "P-004", "product_name": "Gadget Y", "category": "Gadgets", "subcategory": "Pro", "region": "West", "city": "LA", "customer_id": "C-103", "customer_name": "Dave", "sales_amount": 340.0, "quantity": 2, "discount": 0, "payment_method": "Credit", "salesperson_id": "S-04", "salesperson_name": "Lisa", "channel": "Wholesale"},
        {"transaction_id": "TXN-000005", "date": "2023-07-05", "product_id": "P-005", "product_name": "Gadget Z", "category": "Gadgets", "subcategory": "Basic", "region": "North", "city": "CHI", "customer_id": "C-104", "customer_name": "Eve", "sales_amount": 210.0, "quantity": 1, "discount": 0, "payment_method": "Debit", "salesperson_id": "S-05", "salesperson_name": "Mike", "channel": "Wholesale"},
        {"transaction_id": "TXN-000006", "date": "2023-07-06", "product_id": "P-001", "product_name": "Widget A", "category": "Widgets", "subcategory": "Basic", "region": "South", "city": "HOU", "customer_id": "C-105", "customer_name": "Frank", "sales_amount": 560.0, "quantity": 2, "discount": 5, "payment_method": "Cash", "salesperson_id": "S-06", "salesperson_name": "Nina", "channel": "Wholesale"},
        {"transaction_id": "TXN-000007", "date": "2023-07-07", "product_id": "P-002", "product_name": "Widget B", "category": "Widgets", "subcategory": "Pro", "region": "East", "city": "PHI", "customer_id": "C-106", "customer_name": "Grace", "sales_amount": 400.0, "quantity": 1, "discount": 0, "payment_method": "Credit", "salesperson_id": "S-07", "salesperson_name": "Oscar", "channel": "Wholesale"},
        {"transaction_id": "TXN-000008", "date": "2023-07-08", "product_id": "P-006", "product_name": "Super Tool", "category": "Tools", "subcategory": "Premium", "region": "West", "city": "SF", "customer_id": "C-107", "customer_name": "Heidi", "sales_amount": 2000.0, "quantity": 1, "discount": 0, "payment_method": "Debit", "salesperson_id": "S-08", "salesperson_name": "Paul", "channel": "In-Store"},
        {"transaction_id": "TXN-000009", "date": "2023-07-09", "product_id": "P-007", "product_name": "Super Tool Pro", "category": "Tools", "subcategory": "Pro", "region": "North", "city": "SEA", "customer_id": "C-108", "customer_name": "Ivan", "sales_amount": 1750.0, "quantity": 2, "discount": 10, "payment_method": "Credit", "salesperson_id": "S-09", "salesperson_name": "Quinn", "channel": "In-Store"},
        {"transaction_id": "TXN-000010", "date": "2023-07-10", "product_id": "P-008", "product_name": "Mega Gadget", "category": "Gadgets", "subcategory": "Ultra", "region": "South", "city": "MIA", "customer_id": "C-109", "customer_name": "Judy", "sales_amount": 2200.0, "quantity": 1, "discount": 0, "payment_method": "Cash", "salesperson_id": "S-10", "salesperson_name": "Ray", "channel": "In-Store"},
    ]
    # Add row 11 for channel In-Store to have avg=1975? Actually we have 3 In-Store: TXN-000008,000009,000010 -> amounts 2000,1750,2200 -> avg=1983.33? Wait prompt says avg per channel. Let's recalc clean avg:
    # Online: TXN-000001(1200), TXN-000002(850) -> avg = 1025.0
    # In-Store: TXN-000003(1500), TXN-000008(2000), TXN-000009(1750), TXN-000010(2200) -> that's 4 records -> avg = (1500+2000+1750+2200)/4 = 1862.5
    # Wholesale: TXN-000004(340), TXN-000005(210), TXN-000006(560), TXN-000007(400) -> avg = (340+210+560+400)/4 = 377.5

    # Add duplicates of some rows
    duplicate_rows = [
        # exact duplicate of TXN-000001
        {"transaction_id": "TXN-000001", "date": "2023-07-01", "product_id": "P-001", "product_name": "Widget A", "category": "Widgets", "subcategory": "Basic", "region": "North", "city": "NYC", "customer_id": "C-100", "customer_name": "Alice", "sales_amount": 1200.0, "quantity": 2, "discount": 0, "payment_method": "Credit", "salesperson_id": "S-01", "salesperson_name": "Tom", "channel": "Online"},
        # duplicate with different case? Not needed, but add another duplicate with same transaction_id but slightly different amount? That would be ambiguous. Instead add duplicate with same data but different transaction_id? Not good. Let's add duplicate rows that are exact copies of TXN-000003 and TXN-000007.
        {"transaction_id": "TXN-000003", "date": "2023-07-03", "product_id": "P-003", "product_name": "Gadget X", "category": "Gadgets", "subcategory": "Standard", "region": "East", "city": "BOS", "customer_id": "C-102", "customer_name": "Carol", "sales_amount": 1500.0, "quantity": 3, "discount": 10, "payment_method": "Cash", "salesperson_id": "S-03", "salesperson_name": "Kate", "channel": "In-Store"},
        {"transaction_id": "TXN-000007", "date": "2023-07-07", "product_id": "P-002", "product_name": "Widget B", "category": "Widgets", "subcategory": "Pro", "region": "East", "city": "PHI", "customer_id": "C-106", "customer_name": "Grace", "sales_amount": 400.0, "quantity": 1, "discount": 0, "payment_method": "Credit", "salesperson_id": "S-07", "salesperson_name": "Oscar", "channel": "Wholesale"},
    ]

    # Add rows with missing sales_amount
    missing_amount_rows = [
        {"transaction_id": "TXN-000011", "date": "2023-07-11", "product_id": "P-009", "product_name": "Cheap Widget", "category": "Widgets", "subcategory": "Basic", "region": "North", "city": "DET", "customer_id": "C-110", "customer_name": "Kevin", "sales_amount": "", "quantity": 2, "discount": 0, "payment_method": "Cash", "salesperson_id": "S-11", "salesperson_name": "Steve", "channel": "Online"},
        {"transaction_id": "TXN-000012", "date": "2023-07-12", "product_id": "P-010", "product_name": "Fake Product", "category": "Tools", "subcategory": "Basic", "region": "South", "city": "DAL", "customer_id": "C-111", "customer_name": "Wendy", "sales_amount": "N/A", "quantity": 1, "discount": 0, "payment_method": "Debit", "salesperson_id": "S-12", "salesperson_name": "Vera", "channel": "In-Store"},
    ]

    # Add rows with bad transaction_id format
    bad_txn_rows = [
        {"transaction_id": "TXN-abc123", "date": "2023-07-13", "product_id": "P-011", "product_name": "Rogue Item", "category": "Gadgets", "subcategory": "Basic", "region": "East", "city": "WAS", "customer_id": "C-112", "customer_name": "Xavier", "sales_amount": 999.0, "quantity": 1, "discount": 0, "payment_method": "Credit", "salesperson_id": "S-13", "salesperson_name": "Uma", "channel": "Online"},
        {"transaction_id": "123456", "date": "2023-07-14", "product_id": "P-012", "product_name": "Mystery", "category": "Tools", "subcategory": "Premium", "region": "West", "city": "PDX", "customer_id": "C-113", "customer_name": "Yvonne", "sales_amount": 500.0, "quantity": 2, "discount": 0, "payment_method": "Cash", "salesperson_id": "S-14", "salesperson_name": "Zack", "channel": "Wholesale"},
    ]

    # Add row with missing quantity (but amount present) - quantity not required by prompt, but sales_amount is. Prompt says sales_amount or quantity empty/non-numeric -> discard. So include a row with quantity "abc".
    bad_qty_row = [
        {"transaction_id": "TXN-000013", "date": "2023-07-15", "product_id": "P-013", "product_name": "Quantityless", "category": "Gadgets", "subcategory": "Basic", "region": "North", "city": "MIN", "customer_id": "C-114", "customer_name": "Zoe", "sales_amount": 750.0, "quantity": "abc", "discount": 0, "payment_method": "Debit", "salesperson_id": "S-15", "salesperson_name": "Alex", "channel": "In-Store"},
    ]

    # Combine all rows
    all_rows = base_rows + duplicate_rows + missing_amount_rows + bad_txn_rows + bad_qty_row

    # Write "v1" file (cleaner version but missing some rows, just to distract)
    v1_rows = base_rows[:6]  # only first 6, no duplicates
    with open("data/raw_sales/sales_v1.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(base_rows[0].keys()))
        writer.writeheader()
        writer.writerows(v1_rows)

    # Write "v2" file (full messy version)
    with open("data/raw_sales/sales_v2.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(base_rows[0].keys()))
        writer.writeheader()
        writer.writerows(all_rows)

    # Write a "backup" file that is identical to v2 but older
    with open("data/raw_sales/sales_backup.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(base_rows[0].keys()))
        writer.writeheader()
        writer.writerows(all_rows)

    # Write a decoy file with different schema
    with open("data/raw_sales/inventory.txt", "w") as f:
        f.write("SKU,Qty,Location\nA,10,WH1\nB,20,WH2\n")

if __name__ == "__main__":
    build_env()
