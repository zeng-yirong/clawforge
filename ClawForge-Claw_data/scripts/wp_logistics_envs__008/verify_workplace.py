import sys
import json
import os
from pathlib import Path

def score():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    ws = Path(workspace)

    # Scoring components
    total = 0
    details = []

    # --- 1. Directory structure (10 points) ---
    dirs_ok = True
    required_dirs = ["data/returns", "data/shipments", "data/inventory", "ops"]
    for d in required_dirs:
        if not (ws / d).is_dir():
            dirs_ok = False
            details.append({"item": f"Directory {d} exists", "score": 0, "max_score": 10, "passed": False, "reason": f"Missing directory: {d}"})
            break
    if dirs_ok:
        details.append({"item": "Directory structure", "score": 10, "max_score": 10, "passed": True, "reason": "All required directories present"})
        total += 10

    # --- 2. JSON validity (10 points) ---
    try:
        with open(ws / "data/returns/returns.json") as f:
            returns = json.load(f)
        with open(ws / "data/shipments/shipments.json") as f:
            shipments = json.load(f)
        with open(ws / "data/inventory/inventory.json") as f:
            inventory = json.load(f)
        details.append({"item": "JSON files valid", "score": 10, "max_score": 10, "passed": True, "reason": "All three JSON files parse successfully"})
        total += 10
    except Exception as e:
        details.append({"item": "JSON files valid", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON parse error: {e}"})
        print("Fatal: cannot parse JSON files. Exiting.")
        write_score(total, details, ws)
        sys.exit(1)

    # --- 3. Return ret_001 (20 points) ---
    ret001 = next((r for r in returns if r["return_id"] == "ret_001"), None)
    ret001_score = 0
    ret001_reason = []
    if ret001 is None:
        ret001_reason.append("ret_001 not found")
    else:
        if ret001.get("status") == "approved":
            ret001_score += 10
        else:
            ret001_reason.append(f"status is '{ret001.get('status')}', expected 'approved'")
        if "refund_approved" in ret001.get("resolution", ""):
            ret001_score += 10
        else:
            ret001_reason.append(f"resolution does not contain 'refund_approved'")
    details.append({"item": "Return ret_001 approved correctly", "score": ret001_score, "max_score": 20, "passed": ret001_score == 20, "reason": "; ".join(ret001_reason) if ret001_reason else "OK"})
    total += ret001_score

    # --- 4. Return ret_003 (20 points) ---
    ret003 = next((r for r in returns if r["return_id"] == "ret_003"), None)
    ret003_score = 0
    ret003_reason = []
    if ret003 is None:
        ret003_reason.append("ret_003 not found")
    else:
        notes = ret003.get("inspection_notes", "")
        if "wrong item" in notes and "exchange" in notes:
            ret003_score += 20
        else:
            ret003_reason.append(f"inspection_notes missing 'wrong item' or 'exchange': '{notes}'")
    details.append({"item": "Return ret_003 inspection notes correct", "score": ret003_score, "max_score": 20, "passed": ret003_score == 20, "reason": "; ".join(ret003_reason) if ret003_reason else "OK"})
    total += ret003_score

    # --- 5. Shipment ship_005 (20 points) ---
    ship005 = next((s for s in shipments if s["shipment_id"] == "ship_005"), None)
    ship005_score = 0
    ship005_reason = []
    if ship005 is None:
        ship005_reason.append("ship_005 not found")
    else:
        if ship005.get("status") == "shipped":
            ship005_score += 10
        else:
            ship005_reason.append(f"status is '{ship005.get('status')}', expected 'shipped'")
        if ship005.get("carrier") == "FedEx":
            ship005_score += 10
        else:
            ship005_reason.append(f"carrier is '{ship005.get('carrier')}', expected 'FedEx'")
    details.append({"item": "Shipment ship_005 updated correctly", "score": ship005_score, "max_score": 20, "passed": ship005_score == 20, "reason": "; ".join(ship005_reason) if ship005_reason else "OK"})
    total += ship005_score

    # --- 6. Inventory SKU-1002, wh_001 (20 points) ---
    inv_item = next((i for i in inventory if i["sku"] == "SKU-1002" and i["warehouse_id"] == "wh_001"), None)
    inv_score = 0
    inv_reason = []
    if inv_item is None:
        inv_reason.append("SKU-1002 in wh_001 not found")
    else:
        # expected stock_level = 100 - 5 = 95
        if inv_item.get("stock_level") == 95:
            inv_score += 15
        else:
            inv_reason.append(f"stock_level is {inv_item.get('stock_level')}, expected 95")
        # check damage tag – look for a field like 'adjustment_reason' or 'notes' containing 'damage'
        if inv_item.get("adjustment_reason") == "damage" or "damage" in inv_item.get("notes", ""):
            inv_score += 5
        else:
            inv_reason.append("missing damage indication (field 'adjustment_reason'='damage' or 'notes' containing 'damage')")
    details.append({"item": "Inventory SKU-1002 adjusted correctly", "score": inv_score, "max_score": 20, "passed": inv_score == 20, "reason": "; ".join(inv_reason) if inv_reason else "OK"})
    total += inv_score

    # --- 7. Reconciliation report (10 points) ---
    report_path = ws / "ops/reconciliation_report.json"
    report_score = 0
    report_reason = []
    if report_path.exists():
        try:
            with open(report_path) as f:
                report = json.load(f)
            # must contain fields 'reconciliation' and 'discrepancy' (as keys or values)
            if "reconciliation" in report or any("reconciliation" in str(v) for v in report.values()):
                report_score += 5
            else:
                report_reason.append("missing 'reconciliation' key or value")
            if "discrepancy" in report or any("discrepancy" in str(v) for v in report.values()):
                report_score += 5
            else:
                report_reason.append("missing 'discrepancy' key or value")
        except json.JSONDecodeError:
            report_reason.append("report is not valid JSON")
    else:
        report_reason.append("ops/reconciliation_report.json does not exist")
    details.append({"item": "Reconciliation report generated", "score": report_score, "max_score": 10, "passed": report_score == 10, "reason": "; ".join(report_reason) if report_reason else "OK"})
    total += report_score

    write_score(total, details, ws)

def write_score(total, details, workspace_path):
    result = {
        "total_score": total,
        "details": details
    }
    with open(workspace_path / "workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    score()
