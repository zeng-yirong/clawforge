import os
import json
import random

def build_env():
    # Clean slate
    for p in ["data/earnings", "results"]:
        os.makedirs(p, exist_ok=True)

    # --- Define earnings data for each ticker ---
    # Only one stock (TECH) meets the condition in Q2 2026:
    #   revenue_beat=True AND eps_beat_pct is highest among all Q2 2026 records.
    # NXTC has revenue_beat=True but lower eps_beat_pct.
    # MFST has a high eps_beat_pct but revenue_beat=False.
    # HLTH has Q1 data only (no Q2).
    # Add some other quarters to create confusion.
    earnings_data = {
        "TECH": [
            {"quarter": "Q1 2026", "revenue_actual": 8500, "revenue_estimate": 8200, "revenue_beat": True, "revenue_beat_pct": 3.66, "eps_actual": 1.92, "eps_estimate": 1.80, "eps_beat": True, "eps_beat_pct": 6.67},
            {"quarter": "Q2 2026", "revenue_actual": 9150, "revenue_estimate": 8700, "revenue_beat": True, "revenue_beat_pct": 5.17, "eps_actual": 2.45, "eps_estimate": 2.10, "eps_beat": True, "eps_beat_pct": 16.67}
        ],
        "NXTC": [
            {"quarter": "Q2 2026", "revenue_actual": 3400, "revenue_estimate": 3200, "revenue_beat": True, "revenue_beat_pct": 6.25, "eps_actual": 0.87, "eps_estimate": 0.80, "eps_beat": True, "eps_beat_pct": 8.75}
        ],
        "MFST": [
            {"quarter": "Q2 2026", "revenue_actual": 12000, "revenue_estimate": 12500, "revenue_beat": False, "revenue_beat_pct": -4.00, "eps_actual": 3.10, "eps_estimate": 2.70, "eps_beat": True, "eps_beat_pct": 14.81}
        ],
        "HLTH": [
            {"quarter": "Q1 2026", "revenue_actual": 2200, "revenue_estimate": 2100, "revenue_beat": True, "revenue_beat_pct": 4.76, "eps_actual": 0.55, "eps_estimate": 0.50, "eps_beat": True, "eps_beat_pct": 10.00}
        ]
    }

    # Write each ticker's data to its own JSON file
    for ticker, records in earnings_data.items():
        # Add a couple of noisy fields to test robustness (extra keys)
        # but keep the core fields intact.
        enriched = []
        for rec in records:
            noisy = rec.copy()
            noisy["auditor"] = "PwC" if ticker == "TECH" else "Deloitte"
            enriched.append(noisy)
        filepath = f"data/earnings/{ticker}.json"
        with open(filepath, "w") as f:
            json.dump(enriched, f, indent=2)

    # Create a small distraction file in data/earnings (not a valid JSON array)
    with open("data/earnings/extra_info.txt", "w") as f:
        f.write("This file is irrelevant for the task.\n")

    # Create results directory (empty initially)
    # (already created above)

if __name__ == "__main__":
    build_env()
