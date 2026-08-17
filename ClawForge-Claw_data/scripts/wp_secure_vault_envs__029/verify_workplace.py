import sys
import os
import json
import csv
import math

def weak_password(password: str) -> bool:
    """
    Determine if a password is weak based on simple heuristics:
    - length < 8
    - all digits (even if length >=8, e.g. '12345678' is weak)
    - common weak literals (case-insensitive)
    """
    common_weak = {'password', '123456', '12345678', 'qwerty', 'abc123',
                   'letmein', '111111', 'sunshine', 'iloveyou', 'welcome',
                   'monkey', 'dragon', 'master', 'hello'}
    if len(password) < 8:
        return True
    if password.isdigit():
        return True
    if password.lower() in common_weak:
        return True
    return False

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    os.chdir(workspace)  # assume workspace is the asset root (包含 data/ 和 ops/)

    details = []
    total_score = 0

    # ---------- 1) Check required directory structure (10 pts) ----------
    dir_items = ["data", "ops"]
    dir_ok = True
    for d in dir_items:
        if not os.path.isdir(d):
            details.append({"item": f"Directory '{d}' exists", "score": 0, "max_score": 5, "passed": False, "reason": f"Missing directory '{d}'"})
            dir_ok = False
            total_score += 0
        else:
            details.append({"item": f"Directory '{d}' exists", "score": 5, "max_score": 5, "passed": True, "reason": "Found"})
            total_score += 5
    if not dir_ok:
        # If base dir missing, cannot proceed further
        score_data = {"total_score": total_score, "details": details}
        with open("workplace_score.json", "w") as f:
            json.dump(score_data, f, indent=2)
        print(f"Score: {total_score}/100 -> written to workplace_score.json")
        sys.exit(0)

    # ---------- 2) Check required input files (10 pts) ----------
    input_files = ["data/vault_schema.json", "data/credentials.csv", "data/autofill_rules.json"]
    for f in input_files:
        if os.path.isfile(f):
            details.append({"item": f"Input file '{f}' exists", "score": 3, "max_score": 3, "passed": True, "reason": "Found"})
            total_score += 3
        else:
            details.append({"item": f"Input file '{f}' exists", "score": 0, "max_score": 3, "passed": False, "reason": "Missing"})

    # ---------- 3) Check agent output file ops/weak_creds.json (10 pts) ----------
    output_path = "ops/weak_creds.json"
    if not os.path.isfile(output_path):
        details.append({"item": "Agent output file 'ops/weak_creds.json' exists", "score": 0, "max_score": 10, "passed": False, "reason": "File not found"})
        # Cannot grade further, write partial score
        score_data = {"total_score": total_score, "details": details}
        with open("workplace_score.json", "w") as f:
            json.dump(score_data, f, indent=2)
        print(f"Score: {total_score}/100 -> written to workplace_score.json")
        sys.exit(0)
    else:
        details.append({"item": "Agent output file 'ops/weak_creds.json' exists", "score": 10, "max_score": 10, "passed": True, "reason": "Found"})
        total_score += 10

    # ---------- 4) Validate output JSON format (10 pts) ----------
    try:
        with open(output_path, "r") as f:
            content = f.read().strip()
            if not content:
                raise ValueError("Empty file")
            output_data = json.loads(content)
    except (json.JSONDecodeError, ValueError) as e:
        details.append({"item": "output JSON is valid and non-empty", "score": 0, "max_score": 10, "passed": False, "reason": f"Invalid JSON: {e}"})
        score_data = {"total_score": total_score, "details": details}
        with open("workplace_score.json", "w") as f:
            json.dump(score_data, f, indent=2)
        print(f"Score: {total_score}/100 -> written to workplace_score.json")
        sys.exit(0)

    # Expect structure: {"weak_creds": [{"id": "...", "category_name": "..."}, ...]}
    if not isinstance(output_data, dict) or "weak_creds" not in output_data:
        details.append({"item": "Output JSON has key 'weak_creds' and value is list", "score": 0, "max_score": 10, "passed": False, "reason": "Missing 'weak_creds' key or wrong structure"})
        score_data = {"total_score": total_score, "details": details}
        with open("workplace_score.json", "w") as f:
            json.dump(score_data, f, indent=2)
        print(f"Score: {total_score}/100 -> written to workplace_score.json")
        sys.exit(0)
    creds_list = output_data["weak_creds"]
    if not isinstance(creds_list, list):
        details.append({"item": "'weak_creds' is a list", "score": 0, "max_score": 10, "passed": False, "reason": "Not a list"})
        total_score += 0
    else:
        # Check each element has required fields
        all_good = True
        for item in creds_list:
            if not isinstance(item, dict) or "id" not in item or "category_name" not in item:
                all_good = False
                break
        if all_good:
            details.append({"item": "Each entry has 'id' and 'category_name'", "score": 10, "max_score": 10, "passed": True, "reason": "Structure valid"})
            total_score += 10
        else:
            details.append({"item": "Each entry has 'id' and 'category_name'", "score": 0, "max_score": 10, "passed": False, "reason": "Missing required keys in some entries"})
            total_score += 0

    # ---------- 5) Extract ground truth (30 pts for correctness) ----------
    # Build ground truth from credentials.csv
    cred_path = "data/credentials.csv"
    if not os.path.isfile(cred_path):
        details.append({"item": "Ground truth extraction", "score": 0, "max_score": 30, "passed": False, "reason": "credentials.csv missing"})
        total_score += 0
    else:
        try:
            with open(cred_path, "r") as f:
                reader = csv.DictReader(f)
                true_weak_ids = set()
                id_to_cat_name = {}
                id_to_password = {}
                for row in reader:
                    cid = row["id"]
                    cat_id = row["category_id"]
                    password = row["password"]
                    id_to_password[cid] = password
                    # Map category
                    id_to_cat_name[cid] = cat_id  # placeholder, will resolve later
                # Load schema for category name mapping
                with open("data/vault_schema.json") as f:
                    schema = json.load(f)
                cat_id_to_name = {c["category_id"]: c["name"] for c in schema}
                # Now determine weak passwords
                for cid, pw in id_to_password.items():
                    if weak_password(pw):
                        true_weak_ids.add(cid)
                # Build ground truth list with category names
                true_weak_list = []
                for cid in sorted(true_weak_ids):
                    cat_id = id_to_cat_name[cid]  # this was the category_id from csv
                    cat_name = cat_id_to_name.get(cat_id, "unknown")
                    true_weak_list.append({"id": cid, "category_name": cat_name})
        except Exception as e:
            details.append({"item": "Ground truth extraction", "score": 0, "max_score": 30, "passed": False, "reason": f"Error reading CSV: {e}"})
            total_score += 0
            score_data = {"total_score": total_score, "details": details}
            with open("workplace_score.json", "w") as f:
                json.dump(score_data, f, indent=2)
            print(f"Score: {total_score}/100 -> written to workplace_score.json")
            sys.exit(0)

        # Compare agent's list with ground truth
        agent_set = {(item["id"], item["category_name"]) for item in creds_list}
        true_set = {(item["id"], item["category_name"]) for item in true_weak_list}

        if agent_set == true_set:
            details.append({"item": "Weak credentials correct (exact match)", "score": 30, "max_score": 30, "passed": True, "reason": "All expected weak credentials found with correct category names"})
            total_score += 30
        else:
            # Partial credit: count intersection
            overlap = agent_set & true_set
            missed = true_set - agent_set
            extra = agent_set - true_set
            # Grade: 1 point per correct entry, max 30
            correct_count = len(overlap)
            score_val = min(30, correct_count * (30 / len(true_set)))  # proportional
            reason = f"Overlap {len(overlap)} / {len(true_set)}; missed {len(missed)}; extra {len(extra)}"
            details.append({"item": "Weak credentials correctness", "score": round(score_val), "max_score": 30, "passed": False, "reason": reason})
            total_score += round(score_val)

    # ---------- 6) Check that agent did not include strong/tricky passwords (20 pts) ----------
    # We already checked intersection above; now penalize for including non-weak passwords
    # Determine which ids agent reported
    agent_ids = {item["id"] for item in creds_list}
    all_ids_from_csv = set()
    with open(cred_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            all_ids_from_csv.add(row["id"])
    true_weak_ids_set = {item["id"] for item in true_weak_list}
    false_positives = agent_ids - true_weak_ids_set
    if len(false_positives) == 0:
        details.append({"item": "No false positives (strong passwords included)", "score": 20, "max_score": 20, "passed": True, "reason": "All reported credentials are truly weak"})
        total_score += 20
    else:
        # Penalize: each false positive costs 20/ (max possible false positives) but cap at 20
        # Max possible false positives = total credentials - true weak count = 20 - 8 = 12
        max_fp = 12
        deduction = min(20, len(false_positives) * (20 / max_fp))
        score_gained = max(0, 20 - deduction)
        details.append({"item": "No false positives", "score": round(score_gained), "max_score": 20, "passed": False, "reason": f"Found {len(false_positives)} false positive(s): {false_positives}"})
        total_score += round(score_gained)

    # ---------- 7) Check category name correctness (10 pts) ----------
    # Already accounted in set comparison, but we can double-check each category name matches schema
    cat_name_errors = 0
    for item in creds_list:
        # Find the id's category_id from csv, then map to name
        pass   # we already did in set comparison; no extra score needed.

    # ---------- Finalize ----------
    total_score = min(100, total_score)
    details.append({"item": "Final composite", "score": total_score, "max_score": 100, "passed": total_score >= 60, "reason": "Total score based on all checks"})
    score_data = {"total_score": total_score, "details": details}
    with open("workplace_score.json", "w") as f:
        json.dump(score_data, f, indent=2)
    print(f"Score: {total_score}/100 -> written to workplace_score.json")

if __name__ == "__main__":
    main()
