import os
import json
import sys

def verify(workspace: str):
    details = []
    total_score = 0
    max_total = 100

    # Helper to add score item
    def add_item(name, score, max_score, passed, reason=""):
        details.append({
            "item": name,
            "score": score,
            "max_score": max_score,
            "passed": passed,
            "reason": reason
        })
        return score

    # =============================================
    # 1. Check ops directory exists (10 points)
    ops_path = os.path.join(workspace, "ops")
    if os.path.isdir(ops_path):
        total_score += add_item("ops directory exists", 10, 10, True)
    else:
        total_score += add_item("ops directory exists", 0, 10, False, "ops/ directory not found")

    # =============================================
    # 2. Check retention_cache.json exists (10 points)
    cache_path = os.path.join(ops_path, "retention_cache.json")
    if os.path.isfile(cache_path):
        total_score += add_item("retention_cache.json exists", 10, 10, True)
    else:
        total_score += add_item("retention_cache.json exists", 0, 10, False, "file not found")
        # If file is missing, we cannot continue meaningful checks; return partial
        result = {"total_score": total_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return result

    # =============================================
    # 3. JSON is valid (10 points)
    try:
        with open(cache_path, "r") as f:
            data = json.load(f)
        if isinstance(data, list):
            total_score += add_item("retention_cache.json is valid JSON array", 10, 10, True)
        else:
            total_score += add_item("retention_cache.json is valid JSON array", 0, 10, False, "not a list")
            data = []
    except Exception as e:
        total_score += add_item("retention_cache.json is valid JSON", 0, 10, False, f"parse error: {e}")
        data = []

    # =============================================
    # 4. Correct number of high-risk customers (20 points)
    # Expected: C001 (LedgerFlow, fintech), C002 (ShelfCloud, retail), C005 (DataVault, fintech)
    # Note: C003 appears twice in activity logs but one with stable usage -> not high risk.
    # C003 with high risk but stable usage (distractor) should not be included.
    expected_ids = {"C001", "C002", "C005"}
    actual_ids = {entry.get("customer_id") for entry in data if isinstance(entry, dict)}
    if actual_ids == expected_ids:
        total_score += add_item("Correct customer IDs (exactly C001, C002, C005)", 20, 20, True)
    else:
        missing = expected_ids - actual_ids
        extra = actual_ids - expected_ids
        reason_parts = []
        if missing:
            reason_parts.append(f"missing: {missing}")
        if extra:
            reason_parts.append(f"extra: {extra}")
        total_score += add_item("Correct customer IDs (exactly C001, C002, C005)", 0, 20, False, "; ".join(reason_parts))

    # =============================================
    # 5. Field checks for each expected customer (50 points total, 10 per customer per field group)
    # We'll validate for each expected customer: industry, selected_news_headline, retention_message
    # Predefine expected values based on env_builder and rules
    expected_customers = {
        "C001": {
            "customer_name": "LedgerFlow",
            "industry": "fintech",
            # For fintech, the first pain_point news (by news_id) is N001 (pain_point) -> note N005 also pain_point, but N001 comes first alphabetically? Actually N001 < N005, so N001.
            # news_samples order: N001 (pain_point fintech), N002 (opportunity retail), N003 (pain_point retail), N004 (opportunity fintech), N005 (pain_point fintech)
            # The first pain_point for fintech is N001.
            "selected_news_headline": "Fintech Regulation Tightens: New Compliance Costs Loom",
            "retention_message_prefix": "Retention note: New compliance rules expected to increase operational costs by 20% for small fintech firms."
        },
        "C002": {
            "customer_name": "ShelfCloud",
            "industry": "retail",
            # For retail, first pain_point is N003 (since N002 is opportunity)
            "selected_news_headline": "Supply Chain Disruptions Still Hitting Small Retailers Hard",
            "retention_message_prefix": "Retention note: Persistent logistics delays causing 15% revenue loss for mid-market retailers."
        },
        "C005": {
            "customer_name": "DataVault",
            "industry": "fintech",
            # Same as C001: first pain_point fintech is N001
            "selected_news_headline": "Fintech Regulation Tightens: New Compliance Costs Loom",
            "retention_message_prefix": "Retention note: New compliance rules expected to increase operational costs by 20% for small fintech firms."
        }
    }

    # Build lookup from actual data
    actual_by_id = {entry.get("customer_id"): entry for entry in data if isinstance(entry, dict)}

    for cust_id, expected in expected_customers.items():
        entry = actual_by_id.get(cust_id)
        if entry is None:
            total_score += add_item(f"Customer {cust_id} missing in output", 0, 10, False)
            continue
        # Check customer_name
        if entry.get("customer_name") == expected["customer_name"]:
            total_score += add_item(f"{cust_id}: customer_name correct", 2, 2, True)
        else:
            total_score += add_item(f"{cust_id}: customer_name correct", 0, 2, False, f"got {entry.get('customer_name')}")

        # Check industry
        if entry.get("industry") == expected["industry"]:
            total_score += add_item(f"{cust_id}: industry correct", 2, 2, True)
        else:
            total_score += add_item(f"{cust_id}: industry correct", 0, 2, False, f"got {entry.get('industry')}")

        # Check selected_news_headline
        if entry.get("selected_news_headline") == expected["selected_news_headline"]:
            total_score += add_item(f"{cust_id}: selected_news_headline correct", 3, 3, True)
        else:
            total_score += add_item(f"{cust_id}: selected_news_headline correct", 0, 3, False, f"got {entry.get('selected_news_headline')}")

        # Check retention_message (must start with the correct prefix)
        msg = entry.get("retention_message", "")
        if msg == expected["retention_message_prefix"]:
            total_score += add_item(f"{cust_id}: retention_message correct", 3, 3, True)
        else:
            total_score += add_item(f"{cust_id}: retention_message correct", 0, 3, False, f"expected '{expected['retention_message_prefix']}' got '{msg}'")

    # =============================================
    # Ensure no extra fields are introduced (optional, but can deduct if we want)
    # Not implemented, but verifier can check each entry has exactly 5 fields.
    for entry in data:
        if isinstance(entry, dict):
            keys = set(entry.keys())
            expected_keys = {"customer_id", "customer_name", "industry", "selected_news_headline", "retention_message"}
            if keys != expected_keys:
                extra_keys = keys - expected_keys
                missing_keys = expected_keys - keys
                if extra_keys or missing_keys:
                    # Deduct 5 points per entry but we already gave max for that customer? Let's add a deduction.
                    # Simpler: we already validated per field; extra keys are not penalized heavily.
                    pass

    # Cap total at 100
    total_score = min(total_score, 100)

    result = {"total_score": total_score, "details": details}
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(result, f, indent=2)
    return result

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
