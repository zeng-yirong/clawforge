import os
import json

def build_env():
    # Create data directories
    os.makedirs("data/experiments", exist_ok=True)
    
    # Write experiment results CSV with intentional dirty rows
    csv_lines = [
        "batch_id,group_id,accuracy,latency_ms,cost_usd",
        "batch_001,A,0.95,120,0.5",
        "batch_001,B,0.88,150,0.7",
        "batch_001,C,0.92,130,0.6",
        "batch_002,A,0.97,110,0.55",
        "batch_002,B,0.85,160,0.65",
        "batch_002,C,0.93,125,0.62",
        "batch_003,A,0.91,140,0.6",
        "batch_003,B,0.87,140,0.68",
        "batch_id,group_id,accuracy,latency_ms,cost_usd",   # duplicate header
        "batch_001,A,0.95,120"                               # missing cost column
    ]
    with open("data/experiments/experiment_results.csv", "w") as f:
        for line in csv_lines:
            f.write(line + "\n")
    
    # Distractors – unrelated but valid JSON files in the workspace
    accounts = {
        "accounts": [
            {"account_id": "a1", "display_name": "Alice", "department": "R&D", "email": "alice@x.com", "permissions": ["read"]},
            {"account_id": "a2", "display_name": "Bob", "department": "Ops", "email": "bob@x.com", "permissions": ["write"]}
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f)
    
    contacts = {
        "contacts": [
            {"contact_id": "c1", "name": "Charlie", "role": "Dev", "email": "charlie@x.com"},
            {"contact_id": "c2", "name": "Diana", "role": "QA", "email": "diana@x.com"}
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f)

if __name__ == "__main__":
    build_env()
