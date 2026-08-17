import sys
import os
import csv
import json

# --- Expected correct result (derived from the original CSV + modifications) ---
EXPECTED_ROWS = [
    {"vendor_id": "VEND-001", "name": "Alice Corp", "payment_method": "check", "bank_account": "12345", "status": "active"},
    {"vendor_id": "VEND-003", "name": "Bob Ltd", "payment_method": "wire_transfer", "bank_account": "67890", "status": "active"},
    {"vendor_id": "VEND-005", "name": "Charlie Inc", "payment_method": "wire_transfer", "bank_account": "11111", "status": "active"},
    {"vendor_id": "VEND-009", "name": "Eve LLC", "payment_method": "wire_transfer", "bank_account": "33333", "status": "active"},
]

# Expected field order
EXPECTED_FIELDS = ["vendor_id", "name", "payment_method", "bank_account", "status"]

def verify(workspace):
    details = []
    total_score = 0

    # Helper to add a score item
    def add_item(name, score, max_score, passed, reason):
        details.append({
            "item": name,
            "score": score,
            "max_score": max_score,
            "passed": passed,
            "reason": reason
        })
        return score

    # 1. Check ops directory exists (10 points)
    ops_path = os.path.join(workspace, "ops")
    if os.path.isdir(ops_path):
        total_score += add_item("ops directory exists", 10, 10, True, "ops/ directory found")
    else:
        total_score += add_item("ops directory exists", 0, 10, False, "ops/ directory not found")

    # 2. Check updated_payments.csv exists (10 points)
    csv_path = os.path.join(ops_path, "updated_payments.csv")
    if os.path.isfile(csv_path):
        total_score += add_item("updated_payments.csv exists", 10, 10, True, "File found")
    else:
        # if no file, return early with remaining items as 0
        total_score += add_item("updated_payments.csv exists", 0, 10, False, "File not found")
        # fill remaining items with 0
        for item_name, max_s in [("CSV format valid", 10), ("Row count correct", 20), ("VEND-003 payment method", 20), ("VEND-007 removed", 15), ("Other rows intact", 15)]:
            total_score += add_item(item_name, 0, max_s, False, "File missing, cannot verify")
        return total_score, details

    # 3. Check CSV format (10 points)
    try:
        with open(csv_path, "r", newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        # Verify fields
        if reader.fieldnames == EXPECTED_FIELDS:
            total_score += add_item("CSV format valid", 10, 10, True, "Headers match expected")
        else:
            total_score += add_item("CSV format valid", 0, 10, False, f"Headers mismatched: got {reader.fieldnames}")
            # skip further checks if format wrong
            for item_name, max_s in [("Row count correct", 20), ("VEND-003 payment method", 20), ("VEND-007 removed", 15), ("Other rows intact", 15)]:
                total_score += add_item(item_name, 0, max_s, False, "CSV header invalid, cannot parse rows")
            return total_score, details
    except Exception as e:
        total_score += add_item("CSV format valid", 0, 10, False, f"CSV parse error: {str(e)}")
        for item_name, max_s in [("Row count correct", 20), ("VEND-003 payment method", 20), ("VEND-007 removed", 15), ("Other rows intact", 15)]:
            total_score += add_item(item_name, 0, max_s, False, "CSV unreadable")
        return total_score, details

    # 4. Row count correct (20 points)
    expected_count = len(EXPECTED_ROWS)
    actual_count = len(rows)
    if actual_count == expected_count:
        total_score += add_item("Row count correct", 20, 20, True, f"Exactly {expected_count} rows found")
    else:
        total_score += add_item("Row count correct", 0, 20, False, f"Expected {expected_count} rows, got {actual_count}")

    # 5. VEND-003 payment method (20 points)
    vend003 = [r for r in rows if r.get("vendor_id") == "VEND-003"]
    if len(vend003) == 1 and vend003[0].get("payment_method") == "wire_transfer":
        total_score += add_item("VEND-003 payment method", 20, 20, True, "VEND-003 payment_method = wire_transfer")
    else:
        if len(vend003) != 1:
            total_score += add_item("VEND-003 payment method", 0, 20, False, f"VEND-003 appears {len(vend003)} times (expected 1)")
        else:
            total_score += add_item("VEND-003 payment method", 0, 20, False, f"VEND-003 payment_method = {vend003[0].get('payment_method')} (expected wire_transfer)")

    # 6. VEND-007 removed (15 points)
    vend007 = [r for r in rows if r.get("vendor_id") == "VEND-007"]
    if len(vend007) == 0:
        total_score += add_item("VEND-007 removed", 15, 15, True, "VEND-007 not found, correctly removed")
    else:
        total_score += add_item("VEND-007 removed", 0, 15, False, f"VEND-007 still present ({len(vend007)} row(s))")

    # 7. Other rows intact – spot check VEND-001 bank_account (15 points)
    vend001 = [r for r in rows if r.get("vendor_id") == "VEND-001"]
    if len(vend001) == 1 and vend001[0].get("bank_account") == "12345":
        total_score += add_item("Other rows intact", 15, 15, True, "VEND-001 bank_account still 12345 (intact)")
    else:
        reason = "VEND-001 missing or bank_account changed"
        if len(vend001) != 1:
            reason = f"VEND-001 appears {len(vend001)} times"
        else:
            reason = f"VEND-001 bank_account = {vend001[0].get('bank_account')} (expected 12345)"
        total_score += add_item("Other rows intact", 0, 15, False, reason)

    return total_score, details


if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    total_score, details = verify(workspace)

    # Ensure total_score is integer
    total_score = round(total_score)

    result = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

    print(f"Score: {total_score}/100")
    for d in details:
        status = "PASS" if d["passed"] else "FAIL"
        print(f"  {status} {d['item']}: {d['score']}/{d['max_score']} – {d['reason']}")
