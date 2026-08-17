import sys
import os
import json
import csv

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

details = []
total_score = 0

def add(item, score, max_score, passed, reason):
    details.append({
        "item": item,
        "score": score,
        "max_score": max_score,
        "passed": passed,
        "reason": reason
    })
    return score

# 1. Check that sales_summary.csv exists (10 pts)
path_summary = os.path.join(workspace, "sales_summary.csv")
if os.path.isfile(path_summary):
    add("sales_summary.csv exists", 10, 10, True, "File found")
    total_score += 10
else:
    add("sales_summary.csv exists", 0, 10, False, "File not found")

# 2. Check that average_order.txt exists (10 pts)
path_avg = os.path.join(workspace, "average_order.txt")
if os.path.isfile(path_avg):
    add("average_order.txt exists", 10, 10, True, "File found")
    total_score += 10
else:
    add("average_order.txt exists", 0, 10, False, "File not found")

# 3. Verify sales_summary.csv format (10 pts)
if os.path.isfile(path_summary):
    try:
        with open(path_summary, "r") as f:
            reader = csv.reader(f)
            rows = list(reader)
        if len(rows) >= 2:  # header + at least one data row
            header = rows[0]
            expected_header = ["year_month", "category", "total_sales"]
            if header == expected_header:
                add("sales_summary.csv header correct", 10, 10, True, f"Header: {header}")
                total_score += 10
            else:
                add("sales_summary.csv header correct", 0, 10, False, f"Got header {header}, expected {expected_header}")
        else:
            add("sales_summary.csv header correct", 0, 10, False, "No data rows found")
    except Exception as e:
        add("sales_summary.csv format", 0, 10, False, f"Read error: {e}")

# 4. Verify average_order.txt format and value (15 pts)
if os.path.isfile(path_avg):
    try:
        with open(path_avg, "r") as f:
            content = f.read().strip()
        avg = float(content)
        expected_avg = 225.0  # 1800 / 8
        if abs(avg - expected_avg) < 1e-6:
            add("average_order.txt value correct", 15, 15, True, f"Average = {avg}")
            total_score += 15
        else:
            add("average_order.txt value correct", 0, 15, False, f"Found {avg}, expected {expected_avg}")
    except Exception as e:
        add("average_order.txt format", 0, 15, False, f"Read error: {e}")

# 5. Verify sales_summary.csv data content (55 pts)
# Expected after dedup and fill:
# 2024-01,Widgets,420.0
# 2024-02,Widgets,300.0
# 2024-02,Gadgets,330.0
# 2024-03,Widgets,500.0
# 2024-03,Gadgets,250.0
if os.path.isfile(path_summary):
    try:
        with open(path_summary, "r") as f:
            reader = csv.reader(f)
            rows = list(reader)
        if len(rows) < 2:
            add("sales_summary.csv data rows", 0, 55, False, "No data rows")
        else:
            data_rows = rows[1:]
            # Build dictionary for easier lookup
            summary = {}
            for r in data_rows:
                if len(r) != 3:
                    continue
                key = (r[0], r[1])
                summary[key] = float(r[2])
            expected = {
                ("2024-01", "Widgets"): 420.0,
                ("2024-02", "Widgets"): 300.0,
                ("2024-02", "Gadgets"): 330.0,
                ("2024-03", "Widgets"): 500.0,
                ("2024-03", "Gadgets"): 250.0,
            }
            score_breakdown = 0
            max_data = 55
            # 5 entries, each worth 11 pts
            pts_per_entry = 11
            for key, val in expected.items():
                if key in summary:
                    if abs(summary[key] - val) < 1e-3:
                        score_breakdown += pts_per_entry
                    else:
                        # partial? we give 0 for this entry
                        pass
            # Also check no extra rows (penalise - but we already account)
            extra = len(data_rows) - len(expected)
            if extra > 0:
                score_breakdown = max(0, score_breakdown - 5 * extra)  # penalty
            add("sales_summary.csv data accuracy", score_breakdown, max_data,
                score_breakdown == max_data,
                f"Matched {score_breakdown}/{max_data} points on 5 expected records")
            total_score += score_breakdown
    except Exception as e:
        add("sales_summary.csv data", 0, 55, False, f"Parse error: {e}")

# Final score
total_score = min(total_score, 100)
out = {"total_score": total_score, "details": details}
with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
    json.dump(out, f, indent=2)
print(f"Score: {total_score}/100")
