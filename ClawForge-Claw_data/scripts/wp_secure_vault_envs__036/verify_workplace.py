"""
Verify the agent's workplace for wp_secure_vault_envs__036.
Checks that the agent produced ops/secure_vault.json with correct
filtering and classification according to provided policies.
"""
import sys
import json
import os
import csv
from datetime import datetime, timezone
from pathlib import Path

def load_policy(workspace):
    policy_path = workspace / "vault_policy.json"
    with open(policy_path, "r") as f:
        return json.load(f)

def load_mapping(workspace):
    map_path = workspace / "category_mapping.json"
    with open(map_path, "r") as f:
        return json.load(f)

def load_expected_entries(workspace, policy, mapping):
    """Recompute which entries from credentials_dump.csv should be in vault."""
    csv_path = workspace / "credentials_dump.csv"
    ref_date = datetime.strptime(policy["valid_date"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
    min_len = policy["min_length"]
    req_upper = policy["require_uppercase"]
    req_lower = policy["require_lowercase"]
    req_digit = policy["require_digit"]
    req_special = policy["require_special"]

    def password_valid(pw):
        if len(pw) < min_len:
            return False
        if req_upper and not any(c.isupper() for c in pw):
            return False
        if req_lower and not any(c.islower() for c in pw):
            return False
        if req_digit and not any(c.isdigit() for c in pw):
            return False
        if req_special and not any(c in "!@#$%^&*()_+-=[]{};':\"\\|,.<>/?~`" for c in pw):
            return False
        return True

    expected = {}  # category: list of (username, password, expiry_date)
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            username = row["username"]
            password = row["password"]
            cat_raw = row["category_raw"]
            expiry_str = row["expiry_date"]
            if not expiry_str:
                continue
            expiry = datetime.strptime(expiry_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            if expiry < ref_date:
                continue
            if not password:
                continue
            if not password_valid(password):
                continue
            # map category
            mapped = mapping.get(cat_raw)
            if not mapped:
                continue
            expected.setdefault(mapped, []).append((username, password, expiry_str))
    return expected

def verify_vault(workspace, expected):
    vault_path = workspace / "ops" / "secure_vault.json"
    if not vault_path.exists():
        return 0, "ops/secure_vault.json not found"
    try:
        with open(vault_path, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        return 0, "Invalid JSON in secure_vault.json"
    if "vault" not in data or not isinstance(data["vault"], dict):
        return 18, "Missing or invalid 'vault' key"  # partial score
    vault = data["vault"]
    required_categories = list(expected.keys())
    # Check all expected categories present
    for cat in required_categories:
        if cat not in vault:
            return 18, f"Missing category '{cat}' in vault"
    # Check no extra categories
    extra_cats = set(vault.keys()) - set(required_categories)
    if extra_cats:
        return 18, f"Unexpected categories: {extra_cats}"
    # Compare entries
    total_score = 0
    reasons = []
    # Score structure: 10 for file+JSON +10 for categories +80 for entries (10 per entry, 8 entries? Actually we have 6 expected)
    base_score = 20  # file exists & JSON valid & categories ok
    entry_max = 80  # 6 entries -> 13.33 each, round to 13? We'll do per entry scoring
    # We'll allocate 13 per expected entry, total 78, extra 2 for overall structure
    # But we need to be flexible: total 100. Let's use: categories 10, entries 6*15=90.
    # Adjust: base 10 (file+JSON) + categories 10 + entries 80 =100.
    # For 6 entries, each entry max 13.33, but we'll give 14 each (84) and adjust.
    # Simpler: use point system:
    # 10 for file existence and valid JSON
    # 10 for correct category keys
    # 80 for correct entries: each expected entry 13 points (6 entries => 78) + 2 bonus for no extra entries.
    # We'll compute as:
    # - each expected entry present and correctly placed: +13
    # - extra entries (should not exist): -13 per extra
    # - missing entries: -13 per missing
    # - category mismatch: -5 per entry
    # Then clamp between 0 and 100.
    score = 20
    max_score = 100
    # Convert expected to sets for comparison
    expected_entries_set = {}
    for cat, entries in expected.items():
        expected_entries_set[cat] = set(entries)

    actual_entries_set = {}
    for cat, entries in vault.items():
        actual_list = []
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            username = entry.get("username", "")
            password = entry.get("password", "")
            expiry = entry.get("expiry_date", "")
            actual_list.append((username, password, expiry))
        actual_entries_set[cat] = set(actual_list)

    total_expected = sum(len(s) for s in expected_entries_set.values())
    total_actual = sum(len(s) for s in actual_entries_set.values())

    # Check for extra entries in actual
    extra_entries = []
    missing_entries = []
    for cat in expected_entries_set:
        exp_set = expected_entries_set[cat]
        act_set = actual_entries_set.get(cat, set())
        for entry in act_set - exp_set:
            extra_entries.append(entry)
        for entry in exp_set - act_set:
            missing_entries.append(entry)
    # Check for entries in categories not expected
    for cat in actual_entries_set:
        if cat not in expected_entries_set:
            for entry in actual_entries_set[cat]:
                extra_entries.append((cat, entry))

    per_entry_points = 13  # approx
    deduction = (len(missing_entries) + len(extra_entries)) * per_entry_points
    score -= deduction
    if score < 0:
        score = 0
    # If there are any category mismatches (entry in wrong category) we would have caught as extra/missing.
    # Also check each entry's fields: must have username, password, expiry_date
    for cat in actual_entries_set:
        for entry_tup in actual_entries_set[cat]:
            username, password, expiry = entry_tup
            if not username or not password or not expiry:
                score -= 5  # malformed entry
    # Round score to int
    score = max(0, min(100, int(round(score))))
    reasons = []
    if missing_entries:
        reasons.append(f"Missing {len(missing_entries)} entries: {missing_entries}")
    if extra_entries:
        reasons.append(f"Extra {len(extra_entries)} entries: {extra_entries}")
    if not reasons:
        reasons.append("All expected entries found correctly.")
    return score, "; ".join(reasons)

def main():
    workspace = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    if not workspace.exists():
        print("Workspace not found")
        sys.exit(1)
    policy = load_policy(workspace)
    mapping = load_mapping(workspace)
    expected = load_expected_entries(workspace, policy, mapping)
    score, reason = verify_vault(workspace, expected)
    # Details for scoring
    details = []
    # Itemize:
    # 1. ops/secure_vault.json exists and valid JSON (10)
    vault_path = workspace / "ops" / "secure_vault.json"
    file_exists = vault_path.exists()
    json_valid = False
    if file_exists:
        try:
            with open(vault_path) as f:
                json.load(f)
            json_valid = True
        except:
            pass
    if file_exists and json_valid:
        details.append({"item": "File exists and valid JSON", "score": 10, "max_score": 10, "passed": True, "reason": "OK"})
    else:
        details.append({"item": "File exists and valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": "Missing or invalid"})
    # 2. Correct categories present (10)
    cat_ok = "vault" in (json.load(open(vault_path)) if vault_path.exists() else {}) if file_exists and json_valid else False
    if cat_ok:
        details.append({"item": "Correct categories present", "score": 10, "max_score": 10, "passed": True, "reason": "OK"})
    else:
        details.append({"item": "Correct categories present", "score": 0, "max_score": 10, "passed": False, "reason": "Missing vault key or categories"})
    # 3. Filtering and classification (80)
    details.append({"item": "Accurate filtering and classification", "score": score - 20 if score >= 20 else 0, "max_score": 80, "passed": score >= 80, "reason": reason})
    total_score = details[0]["score"] + details[1]["score"] + details[2]["score"]
    with open(workspace / "workplace_score.json", "w") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2)
    print(f"Total score: {total_score}")

if __name__ == "__main__":
    main()
