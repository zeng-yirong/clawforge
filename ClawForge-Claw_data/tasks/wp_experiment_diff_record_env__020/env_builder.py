import os
import csv

def build_env():
    # Create experiments directory
    os.makedirs("experiments", exist_ok=True)

    # Valid batch_alpha
    with open("experiments/batch_alpha.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["batch_id", "group_id", "accuracy", "latency_ms", "cost_usd"])
        writer.writerow(["alpha", "groupA", "0.95", "120", "0.5"])
        writer.writerow(["alpha", "groupB", "0.88", "150", "0.6"])

    # Valid batch_beta
    with open("experiments/batch_beta.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["batch_id", "group_id", "accuracy", "latency_ms", "cost_usd"])
        writer.writerow(["beta", "groupA", "0.92", "130", "0.55"])
        writer.writerow(["beta", "groupB", "0.90", "140", "0.58"])

    # Distractor: old batch missing groupB
    with open("experiments/batch_old.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["batch_id", "group_id", "accuracy", "latency_ms", "cost_usd"])
        writer.writerow(["old", "groupA", "0.80", "100", "0.40"])

    # Distractor: incomplete (no accuracy column)
    with open("experiments/batch_incomplete.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["batch_id", "group_id", "latency_ms", "cost_usd"])
        writer.writerow(["old2", "groupA", "110", "0.45"])

    # Distractor: corrupt file (not CSV)
    with open("experiments/batch_corrupt.txt", "w") as f:
        f.write("This is not a CSV file. Ignore me.")

    # Create empty diff_records directory to avoid confusion (agent must create file)
    os.makedirs("diff_records", exist_ok=True)

if __name__ == "__main__":
    build_env()
