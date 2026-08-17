import os
import json

def build_env():
    # Create main experiment data directory
    os.makedirs("data/experiments", exist_ok=True)

    # CSV header and rows (with deliberate duplicates, missing values, and distractors)
    csv_lines = [
        "batch_id,group_id,accuracy,latency_ms,cost_usd",
        # exp_v1 – valid rows
        "exp_v1,control,0.85,120.0,0.45",
        "exp_v1,control,0.85,120.0,0.45",          # duplicate
        "exp_v1,treatment_a,0.78,150.0,0.60",
        "exp_v1,treatment_b,0.92,95.0,0.35",
        "exp_v1,treatment_b,0.92,95.0,0.35",       # duplicate
        # exp_v2 – valid rows
        "exp_v2,control,0.88,115.0,0.48",
        "exp_v2,control,0.88,115.0,0.48",          # duplicate
        "exp_v2,treatment_a,0.81,145.0,0.62",
        "exp_v2,treatment_b,0.91,100.0,0.38",
        "exp_v2,treatment_b,0.91,100.0,0.38",      # duplicate
        # Distractor batch (exp_v0) – should be ignored
        "exp_v0,control,0.80,130.0,0.40",
        "exp_v0,treatment_a,0.75,160.0,0.55",
        # Incomplete rows (missing values)
        "exp_v1,control,,120.0,0.45",               # missing accuracy
        "exp_v2,treatment_a,0.81,,0.62",            # missing latency
        # Non-numeric field (should be dropped)
        "exp_v1,test,abc,120.0,0.5",
    ]
    csv_path = "data/experiments/experiment_results.csv"
    with open(csv_path, "w") as f:
        f.write("\n".join(csv_lines) + "\n")

    # Optional distracting JSON files (agents should not touch them)
    os.makedirs("data", exist_ok=True)
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": [{"account_id":"a1","display_name":"Alice","department":"R&D"}]}, f)
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": [{"contact_id":"c1","name":"Bob","role":"engineer"}]}, f)

if __name__ == "__main__":
    build_env()
