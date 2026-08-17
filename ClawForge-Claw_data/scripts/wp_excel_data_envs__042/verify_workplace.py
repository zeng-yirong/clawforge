import sys
import os
import csv
import json
from collections import defaultdict

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    os.chdir(workspace)

    details = []
    total_score = 0
    max_total = 100

    # 1. directory structure (5 points)
    if os.path.isdir("analysis"):
        details.append({"item": "analysis directory exists", "score": 5, "max_score": 5, "passed": True, "reason": "analysis/ found"})
        total_score += 5
    else:
        details.append({"item": "analysis directory exists", "score": 0, "max_score": 5, "passed": False, "reason": "analysis/ not found"})

    # 2. cleaned_sales.csv exists and is valid CSV (15 points)
    csv_path = "analysis/cleaned_sales.csv"
    if os.path.isfile(csv_path):
        try:
            with open(csv_path, newline="") as f:
                reader = csv.DictReader(f)
                agent_rows = list(reader)
            details.append({"item": "cleaned_sales.csv readable", "score": 10, "max_score": 10, "passed": True, "reason": f"loaded {len(agent_rows)} rows"})
            total_score += 10
        except Exception as e:
            details.append({"item": "cleaned_sales.csv readable", "score": 0, "max_score": 10, "passed": False, "reason": f"parse error: {e}"})
    else:
        details.append({"item": "cleaned_sales.csv exists", "score": 0, "max_score": 10, "passed": False, "reason": "file not found"})
        # cannot check further
        _write_score(details, total_score, max_total)
        return

    # 3. product_sales_summary.json exists and valid JSON (15 points)
    json_path = "analysis/product_sales_summary.json"
    if os.path.isfile(json_path):
        try:
            with open(json_path) as f:
                agent_json = json.load(f)
            details.append({"item": "product_sales_summary.json valid JSON", "score": 10, "max_score": 10, "passed": True, "reason": "parsed JSON"})
            total_score += 10
        except Exception as e:
            details.append({"item": "product_sales_summary.json valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON error: {e}"})
            agent_json = None
    else:
        details.append({"item": "product_sales_summary.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "file not found"})
        agent_json = None

    # 4. Recompute expected from raw_data (all .csv in raw_data/ excluding distractor)
    # read accounts
    accounts = {}
    if os.path.isfile("accounts.csv"):
        with open("accounts.csv", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                accounts[row["customer_id"]] = row["customer_name"]

    # read all raw_data/*.csv
    raw_files = [f for f in os.listdir("raw_data") if f.endswith(".csv")]
    all_raw_rows = []
    expected_columns = None
    for rf in raw_files:
        with open(os.path.join("raw_data", rf), newline="") as f:
            reader = csv.DictReader(f)
            cols = reader.fieldnames
            if expected_columns is None:
                expected_columns = set(cols)
            for row in reader:
                all_raw_rows.append(row)

    # dedup by full row tuple (all fields)
    seen = set()
    deduped = []
    for row in all_raw_rows:
        # create tuple with consistent key order
        key = tuple(row.get(col, "") for col in sorted(expected_columns))
        if key not in seen:
            seen.add(key)
            deduped.append(row)

    # filter quantity <= 0
    filtered = []
    for row in deduped:
        try:
            qty = int(row.get("quantity", 0))
        except (ValueError, TypeError):
            qty = 0
        if qty > 0:
            filtered.append(row)

    # fill customer_name from accounts
    for row in filtered:
        if not row.get("customer_name", "").strip():
            cid = row.get("customer_id", "")
            if cid in accounts:
                row["customer_name"] = accounts[cid]
            else:
                row["customer_name"] = "Unknown"

    # sort expected rows by all columns for comparison
    def sort_key(row):
        return tuple(row.get(col, "") for col in sorted(expected_columns))
    expected_rows_sorted = sorted(filtered, key=sort_key)

    # sort agent rows by same key
    agent_cols = set(agent_rows[0].keys()) if agent_rows else set()
    missing_cols = expected_columns - agent_cols
    extra_cols = agent_cols - expected_columns
    if missing_cols or extra_cols:
        details.append({"item": "cleaned_sales.csv column match", "score": 0, "max_score": 10, "passed": False,
                        "reason": f"expected columns {expected_columns}, got {agent_cols}"})
    else:
        # compare content
        agent_sorted = sorted(agent_rows, key=lambda r: tuple(r.get(col, "") for col in sorted(expected_columns)))
        mismatch = False
        for i, (e, a) in enumerate(zip(expected_rows_sorted, agent_sorted)):
            for col in sorted(expected_columns):
                e_val = e.get(col, "").strip()
                a_val = a.get(col, "").strip()
                # special handling for numeric fields (sales_amount, quantity)
                if col in ("sales_amount", "quantity"):
                    try:
                        e_num = float(e_val)
                        a_num = float(a_val)
                        if abs(e_num - a_num) > 0.001:
                            mismatch = True
                            break
                    except:
                        mismatch = True
                        break
                else:
                    if e_val != a_val:
                        mismatch = True
                        break
            if mismatch:
                break
        if mismatch or len(agent_sorted) != len(expected_rows_sorted):
            details.append({"item": "cleaned_sales.csv content correct", "score": 0, "max_score": 20, "passed": False,
                            "reason": f"content mismatch (length expected {len(expected_rows_sorted)}, got {len(agent_sorted)})"})
        else:
            details.append({"item": "cleaned_sales.csv content correct", "score": 20, "max_score": 20, "passed": True, "reason": "all rows match after dedup, filter, fill"})
            total_score += 20

    # check column match if not already checked
    if not missing_cols and not extra_cols:
        total_score += 10  # column match score
        details.append({"item": "cleaned_sales.csv column match", "score": 10, "max_score": 10, "passed": True, "reason": "columns match expected"})

    # 5. Verify summary JSON (25 points)
    if agent_json is not None:
        # check structure: list of products with product_id, total_sales, total_quantity
        if not isinstance(agent_json, dict) or "products" not in agent_json:
            details.append({"item": "summary JSON structure", "score": 0, "max_score": 5, "passed": False, "reason": "missing 'products' key"})
        else:
            products = agent_json["products"]
            if not isinstance(products, list):
                details.append({"item": "summary JSON structure", "score": 0, "max_score": 5, "passed": False, "reason": "'products' not a list"})
            else:
                details.append({"item": "summary JSON structure", "score": 5, "max_score": 5, "passed": True, "reason": "valid structure"})
                total_score += 5

                # compute expected summary
                expected_summary = defaultdict(lambda: {"total_sales": 0.0, "total_quantity": 0})
                for row in filtered:
                    pid = row.get("product_id", "")
                    try:
                        sales = float(row.get("sales_amount", 0))
                        qty = int(row.get("quantity", 0))
                    except:
                        continue
                    expected_summary[pid]["total_sales"] += sales
                    expected_summary[pid]["total_quantity"] += qty

                # sort by product_id
                expected_list = sorted(
                    [{"product_id": pid, "total_sales": round(v["total_sales"], 2), "total_quantity": v["total_quantity"]}
                     for pid, v in expected_summary.items()],
                    key=lambda x: x["product_id"]
                )

                # sort agent list
                agent_list = sorted(products, key=lambda x: x.get("product_id", ""))
                mismatch = False
                for e, a in zip(expected_list, agent_list):
                    if (e["product_id"] != a.get("product_id") or
                        abs(e["total_sales"] - float(a.get("total_sales", 0))) > 0.01 or
                        e["total_quantity"] != int(a.get("total_quantity", 0))):
                        mismatch = True
                        break
                if mismatch or len(agent_list) != len(expected_list):
                    details.append({"item": "summary values correct", "score": 0, "max_score": 20, "passed": False,
                                    "reason": f"expected {expected_list}, got {agent_list}"})
                else:
                    details.append({"item": "summary values correct", "score": 20, "max_score": 20, "passed": True, "reason": "all product summaries match"})
                    total_score += 20
    else:
        details.append({"item": "summary JSON structure", "score": 0, "max_score": 5, "passed": False, "reason": "JSON not loadable"})
        details.append({"item": "summary values correct", "score": 0, "max_score": 20, "passed": False, "reason": "JSON not loadable"})

    _write_score(details, total_score, max_total)

def _write_score(details, total, max_total):
    # clamp total to [0, max_total]
    total = max(0, min(total, max_total))
    result = {
        "total_score": total,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
