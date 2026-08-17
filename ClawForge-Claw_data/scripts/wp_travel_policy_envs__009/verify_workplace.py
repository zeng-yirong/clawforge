import sys
import os
import json
import csv
from decimal import Decimal

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    os.chdir(workspace)

    score_details = []
    total_score = 0

    # 1. Check that outputs directory exists (5 points)
    if os.path.isdir("outputs"):
        score_details.append({
            "item": "outputs directory exists",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "outputs/ found"
        })
        total_score += 5
    else:
        score_details.append({
            "item": "outputs directory exists",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "outputs/ missing"
        })

    # 2. Check that outputs/best_booking.json exists (10 points)
    output_path = "outputs/best_booking.json"
    if os.path.isfile(output_path):
        score_details.append({
            "item": "best_booking.json exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "file found"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "best_booking.json exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "file missing"
        })
        # No point continuing if file missing
        write_score(score_details, total_score)
        return

    # 3. Validate JSON is parseable (10 points)
    try:
        with open(output_path, "r") as f:
            data = json.load(f)
        score_details.append({
            "item": "valid JSON",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "JSON parsed successfully"
        })
        total_score += 10
    except Exception as e:
        score_details.append({
            "item": "valid JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON parse error: {e}"
        })
        write_score(score_details, total_score)
        return

    # 4. Check required fields (10 points)
    required_fields = ["flight_id", "platform", "cabin_class", "price"]
    missing_fields = [f for f in required_fields if f not in data]
    if not missing_fields:
        score_details.append({
            "item": "required fields present",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"all fields found: {required_fields}"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "required fields present",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"missing fields: {missing_fields}"
        })
        # Still check value correctness even if fields missing? we can't compute.
        write_score(score_details, total_score)
        return

    # 5. Validate price is a number (not string) (10 points)
    price = data.get("price")
    if isinstance(price, (int, float)) and not isinstance(price, bool):
        score_details.append({
            "item": "price is numeric",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"price = {price} (type {type(price).__name__})"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "price is numeric",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"price is not a number: {repr(price)}"
        })
        write_score(score_details, total_score)
        return

    # 6. Core logic: compute expected best flight from raw data (40 points)
    # We'll re-read the original CSV, apply same business rules as expected.
    # The agent should have done: remove rows with missing destination, empty cabin, non-numeric price, duplicate flight_id or identical row content,
    # then filter by policy (cabin_class in ["economy","premium_economy"] and price <= 1200),
    # then pick the minimum price (with tie-breaking: earliest flight_id alphabetically).
    csv_path = "raw_data/flight_offers.csv"
    if not os.path.isfile(csv_path):
        # If missing, we can't verify. Give 0 and partial.
        score_details.append({
            "item": "best flight selection (logic)",
            "score": 0,
            "max_score": 40,
            "passed": False,
            "reason": "raw_data/flight_offers.csv not found, cannot verify"
        })
        write_score(score_details, total_score)
        return

    # Parse CSV rows
    rows = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    # Apply cleaning and policy rules (mimicking expected agent behavior)
    valid_rows = []
    seen_ids = set()
    seen_signatures = set()  # (flight_id, price, cabin_class) for exact duplicate detection

    for row in rows:
        # Skip rows with missing critical fields
        if not row.get("destination") or not row.get("cabin_class") or not row.get("price"):
            continue
        # Skip non-numeric price
        try:
            price_val = float(row["price"])
        except (ValueError, TypeError):
            continue
        # Skip duplicate flight_id (first occurrence kept)
        fid = row["flight_id"]
        if fid in seen_ids:
            continue
        seen_ids.add(fid)
        # Skip exact duplicate row content (same flight_id, price, cabin_class)
        sig = (fid, price_val, row["cabin_class"])
        if sig in seen_signatures:
            continue
        seen_signatures.add(sig)
        # Policy filter
        cabin = row["cabin_class"].strip().lower()
        if cabin not in ["economy", "premium_economy"]:
            continue
        if price_val > 1200:
            continue
        valid_rows.append({
            "flight_id": fid,
            "platform": row["platform"],
            "cabin_class": cabin,
            "price": price_val
        })

    # Find mini price with tie-break (first alphabetically by flight_id)
    if not valid_rows:
        expected = None
    else:
        min_price = min(r["price"] for r in valid_rows)
        candidates = [r for r in valid_rows if r["price"] == min_price]
        candidates.sort(key=lambda x: x["flight_id"])
        expected = candidates[0]

    # Compare with agent output
    agent_flight_id = data["flight_id"]
    agent_platform = data["platform"]
    agent_cabin = data["cabin_class"]
    agent_price = price

    # Convert expected to same types
    if expected is None:
        score_details.append({
            "item": "best flight selection (logic)",
            "score": 0,
            "max_score": 40,
            "passed": False,
            "reason": "No valid flights in source data (unexpected error)"
        })
        write_score(score_details, total_score)
        return

    correct = True
    reasons = []
    if agent_flight_id != expected["flight_id"]:
        correct = False
        reasons.append(f"flight_id: got {agent_flight_id}, expected {expected['flight_id']}")
    if agent_platform != expected["platform"]:
        correct = False
        reasons.append(f"platform: got {agent_platform}, expected {expected['platform']}")
    if agent_cabin != expected["cabin_class"]:
        correct = False
        reasons.append(f"cabin_class: got {agent_cabin}, expected {expected['cabin_class']}")
    if agent_price != expected["price"]:
        correct = False
        reasons.append(f"price: got {agent_price}, expected {expected['price']}")

    if correct:
        score_details.append({
            "item": "best flight selection (logic)",
            "score": 40,
            "max_score": 40,
            "passed": True,
            "reason": f"Correct flight {expected['flight_id']} at ${expected['price']:.2f}"
        })
        total_score += 40
    else:
        # Partial credit: each of 4 fields = 10 points each? We'll give 10 per correct field, max 40.
        field_scores = {
            "flight_id": 10,
            "platform": 10,
            "cabin_class": 10,
            "price": 10
        }
        score_earned = 0
        if agent_flight_id == expected["flight_id"]:
            score_earned += 10
        if agent_platform == expected["platform"]:
            score_earned += 10
        if agent_cabin == expected["cabin_class"]:
            score_earned += 10
        if agent_price == expected["price"]:
            score_earned += 10
        reason_str = "; ".join(reasons) if reasons else "partial match"
        score_details.append({
            "item": "best flight selection (logic)",
            "score": score_earned,
            "max_score": 40,
            "passed": False,
            "reason": reason_str
        })
        total_score += score_earned

    # 7. Bonus: check that no extra unexpected fields exist? Not required, but we can deduct if extra fields mislead.
    # Actually we only check required fields. Optional: penalize extra fields? Not needed.

    # Also check if output file is not empty (implicit)
    # Write final score
    write_score(score_details, total_score)

def write_score(details, total):
    result = {
        "total_score": total,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    # Print to stdout for visibility
    print(f"Total score: {total}/100")
    for d in details:
        status = "PASS" if d["passed"] else "FAIL"
        print(f"  [{status}] {d['item']}: {d['score']}/{d['max_score']} - {d['reason']}")

if __name__ == "__main__":
    main()
