import os
import random
import csv
import json

random.seed(42)

def build_env():
    # Create data directories
    os.makedirs("data/experiments", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    
    # Generate experiment results CSV
    rows = []
    # batch_001: 3 groups with baseline values
    baseline = {
        "group_A": (0.72, 150, 0.35),
        "group_B": (0.85, 200, 0.42),
        "group_C": (0.63, 180, 0.28)
    }
    for group_id, (acc, lat, cost) in baseline.items():
        rows.append({
            "batch_id": "batch_001",
            "group_id": group_id,
            "accuracy": round(acc, 2),
            "latency_ms": lat,
            "cost_usd": round(cost, 2)
        })
    
    # batch_002: perturbed values
    perturb = {
        "group_A": (0.78, 140, 0.38),
        "group_B": (0.81, 210, 0.45),
        "group_C": (0.69, 175, 0.25)
    }
    for group_id, (acc, lat, cost) in perturb.items():
        rows.append({
            "batch_id": "batch_002",
            "group_id": group_id,
            "accuracy": round(acc, 2),
            "latency_ms": lat,
            "cost_usd": round(cost, 2)
        })
    
    # Interference: batch_003 (extra batch)
    rows.append({
        "batch_id": "batch_003",
        "group_id": "group_A",
        "accuracy": 0.90,
        "latency_ms": 160,
        "cost_usd": 0.40
    })
    # Interference: duplicate row with same batch+group (different value) -> agent should deduplicate or pick last
    rows.append({
        "batch_id": "batch_001",
        "group_id": "group_C",
        "accuracy": 0.65,
        "latency_ms": 175,
        "cost_usd": 0.29
    })
    # Interference: row with missing field (malformed)
    rows.append({
        "batch_id": "batch_001",
        "group_id": "group_D",
        "accuracy": 0.70,
        "latency_ms": 190
        # missing cost_usd
    })
    
    with open("data/experiments/experiment_results.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["batch_id","group_id","accuracy","latency_ms","cost_usd"])
        writer.writeheader()
        writer.writerows(rows)
    
    # Create interference files
    # accounts.json (unrelated)
    accounts = [
        {"account_id": "acc001", "display_name": "Alice", "department": "R&D", "email": "alice@example.com", "permissions": ["read","write"]},
        {"account_id": "acc002", "display_name": "Bob", "department": "QA", "email": "bob@example.com", "permissions": ["read"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f)
    
    # contacts.json (unrelated)
    contacts = [
        {"contact_id": "c001", "name": "Charlie", "role": "Engineer", "email": "charlie@example.com"},
        {"contact_id": "c002", "name": "Diana", "role": "Manager", "email": "diana@example.com"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f)
    
    # Old data folder
    os.makedirs("old_results", exist_ok=True)
    with open("old_results/batch_001_old.csv", "w") as f:
        f.write("batch_id,group_id,accuracy,latency_ms,cost_usd\nbatch_001,group_A,0.71,152,0.34\n")

if __name__ == "__main__":
    build_env()
