import os
import csv

def build_env():
    # Ensure directories exist
    os.makedirs("data/ledgers", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # --- Helper to write CSV ---
    def write_csv(filename, rows):
        with open(os.path.join("data/ledgers", filename), "w", newline="") as f:
            writer = csv.writer(f)
            for row in rows:
                writer.writerow(row)

    # --- Primary ledgers (correct, 2024 Q1 focus) ---
    # customer_ledger.csv
    write_csv("customer_ledger.csv", [
        ["period", "metric_code", "metric_value"],
        ["2024Q1", "ARPU", 100],
        ["2024Q1", "ChurnRate", 20],
        ["2024Q1", "NPS", 80],
        ["2024Q2", "ARPU", 110],       # out-of-period, should be ignored
        ["2024Q1", "LTV", 150],        # extra metric
    ])

    # product_ledger.csv
    write_csv("product_ledger.csv", [
        ["period", "metric_code", "metric_value"],
        ["2024Q1", "Sales", 500],
        ["2024Q1", "Returns", 30],
        ["2023Q4", "Sales", 480],      # old period
    ])

    # ops_ledger.csv
    write_csv("ops_ledger.csv", [
        ["period", "metric_code", "metric_value"],
        ["2024Q1", "Uptime", 99],      # integer only
        ["2024Q1", "TicketsResolved", 150],
        ["2024Q1", "MTTR", 45],
        ["2024Q1", "Incidents", 5],
    ])

    # --- Interference files ---
    # Old version
    write_csv("customer_ledger_old.csv", [
        ["period", "metric_code", "metric_value"],
        ["2023Q4", "ARPU", 90],
        ["2023Q4", "ChurnRate", 25],
    ])

    # Backup with duplicate (would change total if mistakenly read)
    write_csv("product_ledger_backup.csv", [
        ["period", "metric_code", "metric_value"],
        ["2024Q1", "Sales", 500],      # duplicate value – would artificially raise total
        ["2024Q1", "Returns", 30],
        ["2024Q1", "ExtraMetric", 999],
    ])

    # Temp file with malformed header (missing period)
    write_csv("ops_ledger_temp.csv", [
        ["metric_code", "metric_value"],    # header missing period!
        ["Uptime", 100],
    ])

    # Non-CSV interference
    with open("data/ledgers/README.txt", "w") as f:
        f.write("This directory contains ledger exports. Use at your own risk.\n")

    # Compute ground truth total for 2024Q1 from primary files only
    # customer: ARPU 100 + ChurnRate 20 + NPS 80 + LTV 150 = 350
    # product:  Sales 500 + Returns 30 = 530
    # ops:      Uptime 99 + TicketsResolved 150 + MTTR 45 + Incidents 5 = 299
    # total = 350 + 530 + 299 = 1179
    # (save for later verification reference)
    ground_truth = 1179
    # We'll rely on the verifier to hardcode this.

if __name__ == "__main__":
    build_env()
