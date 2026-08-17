import json
import os
import sys
from datetime import datetime, date

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def check_password_compliant(password, policy):
    """Return list of reason strings if non-compliant; empty list if compliant."""
    reasons = []
    if len(password) < policy['min_length']:
        reasons.append("too short")
    if policy['require_uppercase'] and not any(c.isupper() for c in password):
        reasons.append("missing uppercase")
    if policy['require_digit'] and not any(c.isdigit() for c in password):
        reasons.append("missing digit")
    if policy['require_special'] and not any(c in "!@#$%^&*()_+-=[]{}|;:',.<>?/~`" for c in password):
        reasons.append("missing special char")
    return reasons

def compute_expected_report(creds, policies):
    # Build policy lookup
    policy_map = {p['policy_id']: p for p in policies}
    base_date = date(2025, 3, 1)  # must match builder's baseline
    report = []
    for cred in creds:
        # Skip invalid records
        if not isinstance(cred, dict):
            continue
        if 'password' not in cred or 'policy_id' not in cred:
            continue
        password = cred.get('password')
        if not password or password == "":
            continue
        pid = cred.get('policy_id')
        if pid not in policy_map:
            continue
        pol = policy_map[pid]
        reasons = []

        # Check strength
        strength_reasons = check_password_compliant(password, pol)
        reasons.extend(strength_reasons)

        # Check expiration
        created_str = cred.get('created_at')
        if created_str:
            try:
                created_date = datetime.strptime(created_str, "%Y-%m-%d").date()
                age_days = (base_date - created_date).days
                if age_days > pol['max_age_days']:
                    reasons.append("expired")
            except:
                reasons.append("invalid date")

        if reasons:
            report.append({
                "id": cred['id'],
                "name": cred.get('name', ''),
                "reasons": reasons
            })
    # Sort to have deterministic comparison (by id)
    report.sort(key=lambda x: x['id'])
    return report

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    os.chdir(workspace)

    details = []
    total_score = 0

    # 1. Check required directories exist (10 pts)
    dirs_ok = True
    for d in ["vault", "ops"]:
        if not os.path.isdir(d):
            details.append({"item": f"Directory '{d}' exists", "score": 0, "max_score": 5, "passed": False, "reason": f"Missing directory {d}"})
            dirs_ok = False
        else:
            details.append({"item": f"Directory '{d}' exists", "score": 5, "max_score": 5, "passed": True, "reason": ""})
    if dirs_ok:
        total_score += 10

    # 2. Check that agent output file exists (10 pts)
    report_path = "ops/compliance_report.json"
    if not os.path.isfile(report_path):
        details.append({"item": "Agent output file ops/compliance_report.json", "score": 0, "max_score": 10, "passed": False, "reason": "File not found"})
        total_score += 0
        # Cannot proceed further
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return
    else:
        details.append({"item": "Agent output file ops/compliance_report.json", "score": 10, "max_score": 10, "passed": True, "reason": ""})
        total_score += 10

    # 3. Load and validate output file (10 pts for valid JSON + correct structure)
    try:
        report = load_json(report_path)
        if not isinstance(report, list):
            raise ValueError("Report must be a list")
        for entry in report:
            if not isinstance(entry, dict):
                raise ValueError("Each entry must be an object")
            if "id" not in entry or "name" not in entry or "reasons" not in entry:
                raise ValueError("Each entry must have id, name, reasons")
            if not isinstance(entry["reasons"], list):
                raise ValueError("reasons must be a list")
        details.append({"item": "Output JSON structure", "score": 10, "max_score": 10, "passed": True, "reason": "Valid JSON and structure"})
        total_score += 10
    except Exception as e:
        details.append({"item": "Output JSON structure", "score": 0, "max_score": 10, "passed": False, "reason": str(e)})
        total_score += 0
        # Cannot proceed
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # 4. Load reference data and compute expected report (20 pts)
    try:
        creds = load_json("vault/credentials.json")
        policies = load_json("vault/policies.json")
    except Exception as e:
        details.append({"item": "Load vault data", "score": 0, "max_score": 20, "passed": False, "reason": str(e)})
        total_score += 0
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return
    details.append({"item": "Load vault data", "score": 20, "max_score": 20, "passed": True, "reason": ""})
    total_score += 20

    expected = compute_expected_report(creds, policies)

    # 5. Compare agent report with expected (50 pts)
    # Normalize both: sort by id
    agent_sorted = sorted(report, key=lambda x: x['id'])
    # Build dict for easy comparison
    expected_dict = {e['id']: e for e in expected}
    match_count = 0
    total_expected = len(expected)
    # We'll check each expected entry appears in agent with same reasons (order independent)
    expected_found = [False] * len(expected)
    agent_extra = []

    for a_entry in agent_sorted:
        eid = a_entry['id']
        if eid in expected_dict:
            e_entry = expected_dict[eid]
            # Compare reasons set (order independent)
            if set(a_entry['reasons']) == set(e_entry['reasons']) and a_entry['name'] == e_entry['name']:
                expected_found[list(expected_dict.keys()).index(eid)] = True
                match_count += 1
            else:
                agent_extra.append({"id": eid, "expected": e_entry, "got": a_entry})
        else:
            # Extra entry not in expected
            agent_extra.append({"id": eid, "expected": None, "got": a_entry})

    # Check if any expected missing
    missing_expected = [expected[i] for i, found in enumerate(expected_found) if not found]

    # Scoring: each correct match gives 50 / max(len(expected),1) points, capped at 50
    points_per = 50 / max(len(expected), 1) if len(expected) > 0 else 50
    correct_score = match_count * points_per
    # Deduct for extra or mismatched entries: each reduces by half of points_per
    penalty = len(agent_extra) * (points_per / 2)
    final_compliance_score = max(0, int(correct_score - penalty))
    final_compliance_score = min(final_compliance_score, 50)

    reason_str = f"Found {match_count}/{len(expected)} correct entries, {len(agent_extra)} extra/mismatched"
    details.append({"item": "Compliance report content", "score": final_compliance_score, "max_score": 50, "passed": final_compliance_score == 50, "reason": reason_str})
    total_score += final_compliance_score

    # Ensure total_score is integer between 0-100
    total_score = int(total_score)
    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2)

if __name__ == "__main__":
    main()
