import os
import sys
import csv
import json

def verify(workspace):
    errors = []
    score = 0
    details = []

    # Check ops directory
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        score += 5
        details.append({"item": "ops directory exists", "score": 5, "max_score": 5, "passed": True, "reason": "Found ops/"})
    else:
        details.append({"item": "ops directory exists", "score": 0, "max_score": 5, "passed": False, "reason": "ops/ not found"})

    # Check cleaned_sales.csv
    csv_path = os.path.join(workspace, "cleaned_sales.csv")
    if os.path.isfile(csv_path):
        score += 5
        details.append({"item": "cleaned_sales.csv exists", "score": 5, "max_score": 5, "passed": True, "reason": "File found"})
    else:
        details.append({"item": "cleaned_sales.csv exists", "score": 0, "max_score": 5, "passed": False, "reason": "File not found"})

    # Check ops/result.json
    json_path = os.path.join(ops_dir, "result.json")
    if os.path.isfile(json_path):
        score += 5
        details.append({"item": "ops/result.json exists", "score": 5, "max_score": 5, "passed": True, "reason": "File found"})
    else:
        details.append({"item": "ops/result.json exists", "score": 0, "max_score": 5, "passed": False, "reason": "File not found"})

    # Validate CSV
    if os.path.isfile(csv_path):
        try:
            with open(csv_path, 'r') as f:
                reader = csv.reader(f)
                rows = list(reader)
            # Check header
            if len(rows) > 0 and rows[0] == ["transaction_id","date","product_id","product_name","category","subcategory","region","city","customer_id","customer_name","sales_amount","quantity","discount","payment_method","salesperson_id","salesperson_name","channel"]:
                score += 5
                details.append({"item": "CSV format and header correct", "score": 5, "max_score": 5, "passed": True, "reason": "Valid CSV with correct columns"})
            else:
                details.append({"item": "CSV format and header correct", "score": 0, "max_score": 5, "passed": False, "reason": "Missing or incorrect header"})
        except Exception as e:
            details.append({"item": "CSV format and header correct", "score": 0, "max_score": 5, "passed": False, "reason": f"CSV parse error: {e}"})
    else:
        details.append({"item": "CSV format and header correct", "score": 0, "max_score": 5, "passed": False, "reason": "File missing"})

    # Validate JSON
    if os.path.isfile(json_path):
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            # Check required keys
            required_keys = ["total_revenue", "total_transactions", "average_order_value", "top_customer_id", "top_customer_count"]
            if all(k in data for k in required_keys):
                score += 5
                details.append({"item": "JSON format and required keys", "score": 5, "max_score": 5, "passed": True, "reason": "Valid JSON with all keys"})
            else:
                missing = [k for k in required_keys if k not in data]
                details.append({"item": "JSON format and required keys", "score": 0, "max_score": 5, "passed": False, "reason": f"Missing keys: {missing}"})
        except Exception as e:
            details.append({"item": "JSON format and required keys", "score": 0, "max_score": 5, "passed": False, "reason": f"JSON parse error: {e}"})
    else:
        details.append({"item": "JSON format and required keys", "score": 0, "max_score": 5, "passed": False, "reason": "File missing"})

    # Numeric checks
    expected = {
        "total_revenue": 1708.0,
        "total_transactions": 10,
        "average_order_value": 170.8,
        "top_customer_id": "C001",
        "top_customer_count": 4
    }

    # Only if JSON is valid
    if os.path.isfile(json_path):
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            # total_revenue
            if data.get("total_revenue") == expected["total_revenue"]:
                score += 15
                details.append({"item": "total_revenue", "score": 15, "max_score": 15, "passed": True, "reason": f"Value {data['total_revenue']} matches expected"})
            else:
                details.append({"item": "total_revenue", "score": 0, "max_score": 15, "passed": False, "reason": f"Expected {expected['total_revenue']}, got {data.get('total_revenue')}"})
            # total_transactions
            if data.get("total_transactions") == expected["total_transactions"]:
                score += 15
                details.append({"item": "total_transactions", "score": 15, "max_score": 15, "passed": True, "reason": f"Value {data['total_transactions']} matches expected"})
            else:
                details.append({"item": "total_transactions", "score": 0, "max_score": 15, "passed": False, "reason": f"Expected {expected['total_transactions']}, got {data.get('total_transactions')}"})
            # average_order_value (allow small rounding)
            val_avg = data.get("average_order_value")
            if isinstance(val_avg, (int, float)) and round(val_avg, 1) == expected["average_order_value"]:
                score += 15
                details.append({"item": "average_order_value", "score": 15, "max_score": 15, "passed": True, "reason": f"Value {val_avg} matches expected"})
            else:
                details.append({"item": "average_order_value", "score": 0, "max_score": 15, "passed": False, "reason": f"Expected {expected['average_order_value']}, got {data.get('average_order_value')}"})
            # top_customer_id
            if data.get("top_customer_id") == expected["top_customer_id"]:
                score += 15
                details.append({"item": "top_customer_id", "score": 15, "max_score": 15, "passed": True, "reason": f"Value {data['top_customer_id']} matches expected"})
            else:
                details.append({"item": "top_customer_id", "score": 0, "max_score": 15, "passed": False, "reason": f"Expected {expected['top_customer_id']}, got {data.get('top_customer_id')}"})
            # top_customer_count
            if data.get("top_customer_count") == expected["top_customer_count"]:
                score += 15
                details.append({"item": "top_customer_count", "score": 15, "max_score": 15, "passed": True, "reason": f"Value {data['top_customer_count']} matches expected"})
            else:
                details.append({"item": "top_customer_count", "score": 0, "max_score": 15, "passed": False, "reason": f"Expected {expected['top_customer_count']}, got {data.get('top_customer_count')}"})
        except Exception:
            # Already scored JSON parse error, skip numeric
            pass

    # Write score
    result = {
        "total_score": score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score: {score}/100")

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
