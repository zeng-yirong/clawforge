import os
import csv
import json
import random

def build_env():
    # Create directories
    os.makedirs("data/experiments", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # Helper to write CSV with potential dirty rows
    def write_csv(path, rows, extra_dirty=True):
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["group_id", "accuracy", "latency_ms", "cost_usd"])
            for row in rows:
                writer.writerow(row)
            if extra_dirty:
                # Insert a blank line and a malformed row
                writer.writerow([])
                writer.writerow(["garbage", "abc", "xyz", ""])

    # 1) Batch b1 (clean + one dirty group3)
    b1_rows = [
        ["group1", 0.95, 100.0, 0.5],
        ["group2", 0.88, 150.0, 0.6],
        # group3 has a missing field (cost) – will be skipped
        # Actually we insert a row with missing field, but we also need a valid row? We'll insert a valid one and then a bad one.
    ]
    # Make group3 dirty: only 3 fields
    b1_rows.append(["group3", 0.91, 120.0])  # missing cost
    # Also add another valid group4 to increase complexity
    b1_rows.append(["group4", 0.72, 200.0, 0.4])
    # Add a row with extra comma
    b1_rows.append(["group5,0.83,130.0,0.55"])  # single string will cause error
    write_csv("data/experiments/batch_b1.csv", b1_rows)

    # 2) Batch b3 (valid rows for groups 1,2,4 only; group3 missing, group5 dirty)
    b3_rows = [
        ["group1", 0.93, 105.0, 0.55],
        ["group2", 0.85, 155.0, 0.58],
        # group3 not present intentionally
        ["group4", 0.79, 190.0, 0.42],
        # extra comma garbage
        ["group6", 0.88, 140.0, 0.5],  # group6 not in b1 → should be ignored during diff
    ]
    write_csv("data/experiments/batch_b3.csv", b3_rows)

    # 3) Interfering batch b2 (old experiment, not needed)
    b2_rows = [
        ["group_a", 0.91, 110.0, 0.52],
        ["group_b", 0.86, 145.0, 0.63],
    ]
    write_csv("data/experiments/batch_b2.csv", b2_rows)

    # 4) Extra interfering files
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": [{"account_id": "a1", "display_name": "Test", "department": "eng", "email": "t@x.com", "permissions": ["read"]}]}, f)
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": [{"contact_id": "c1", "name": "Alice", "role": "dev", "email": "a@x.com"}]}, f)
    with open("ops/old_diff.json", "w") as f:
        json.dump({"placeholder": True}, f)
    with open("README.txt", "w") as f:
        f.write("Experiment records here.\n")

if __name__ == "__main__":
    build_env()
