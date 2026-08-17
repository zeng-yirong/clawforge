import os
import sys
import json
import math

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    os.chdir(workspace)
    
    details = []
    total_score = 0
    max_total = 100
    
    # 1. Check reports directory exists
    reports_dir = os.path.join(".", "reports")
    dir_exists = os.path.isdir(reports_dir)
    if dir_exists:
        details.append({"item": "reports directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "Directory found"})
        total_score += 10
    else:
        details.append({"item": "reports directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "Directory not found"})
    
    # 2. Check output file exists
    output_path = os.path.join(reports_dir, "smartsaas_insight.json")
    file_exists = os.path.isfile(output_path)
    if file_exists:
        details.append({"item": "smartsaas_insight.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "File found"})
        total_score += 10
    else:
        details.append({"item": "smartsaas_insight.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "File not found"})
        # Stop further checks if file missing
        _write_score(total_score, max_total, details)
        return
    
    # 3. Parse JSON
    try:
        with open(output_path, "r") as f:
            data = json.load(f)
        details.append({"item": "Output is valid JSON", "score": 10, "max_score": 10, "passed": True, "reason": "JSON parsed successfully"})
        total_score += 10
    except Exception as e:
        details.append({"item": "Output is valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON parse error: {e}"})
        _write_score(total_score, max_total, details)
        return
    
    # 4. Check required fields exist
    required_fields = ["competitor_id", "total_users", "avg_acquisition_cost", "market_share"]
    fields_score = 0
    fields_max = 20  # 5 each, 4 fields = 20
    for field in required_fields:
        if field in data:
            fields_score += 5
            details.append({"item": f"Field '{field}' present", "score": 5, "max_score": 5, "passed": True, "reason": f"Field exists with value {data[field]}"})
        else:
            details.append({"item": f"Field '{field}' present", "score": 0, "max_score": 5, "passed": False, "reason": f"Field '{field}' missing"})
    total_score += fields_score
    
    # 5. Compute expected values from environment data
    expected = _compute_expected(workspace)
    if expected is None:
        # If compute failed (e.g., no SmartSaaS file), penalize heavily
        details.append({"item": "Environment data integrity", "score": 0, "max_score": 60, "passed": False, "reason": "Could not compute expected values from data files"})
        _write_score(total_score, max_total, details)
        return
    
    # 6. Compare numeric fields with tolerance
    numeric_checks = [
        ("total_users", int, expected["total_users"]),
        ("avg_acquisition_cost", float, expected["avg_acquisition_cost"]),
        ("market_share", float, expected["market_share"]),
    ]
    numeric_score = 0
    numeric_max = 60  # 20 each
    for field, ftype, exp_val in numeric_checks:
        if field not in data:
            details.append({"item": f"Numeric field '{field}' correct", "score": 0, "max_score": 20, "passed": False, "reason": "Field missing"})
            continue
        try:
            actual = ftype(data[field])
        except (ValueError, TypeError):
            details.append({"item": f"Numeric field '{field}' correct", "score": 0, "max_score": 20, "passed": False, "reason": f"Cannot convert to {ftype}"})
            continue
        
        if ftype == int:
            passed = (actual == exp_val)
        else:
            passed = math.isclose(actual, exp_val, rel_tol=1e-5, abs_tol=0.01)
        
        if passed:
            numeric_score += 20
            details.append({"item": f"Numeric field '{field}' correct", "score": 20, "max_score": 20, "passed": True, "reason": f"Expected {exp_val}, got {actual}"})
        else:
            details.append({"item": f"Numeric field '{field}' correct", "score": 0, "max_score": 20, "passed": False, "reason": f"Expected {exp_val}, got {actual}"})
    total_score += numeric_score
    
    _write_score(total_score, max_total, details)

def _compute_expected(workspace):
    """Traverse data/ to compute the correct answer"""
    # Find latest SmartSaaS competitor file
    comp_dir = os.path.join(workspace, "data", "competitors")
    best_comp = None
    best_version = -1
    if not os.path.isdir(comp_dir):
        return None
    for fname in os.listdir(comp_dir):
        if not fname.endswith(".json"):
            continue
        fpath = os.path.join(comp_dir, fname)
        with open(fpath, "r") as f:
            try:
                obj = json.load(f)
            except:
                continue
        if obj.get("competitor_id") != "SmartSaaS":
            continue
        ver = obj.get("version", 0)
        if ver > best_version:
            best_version = ver
            best_comp = obj
    if best_comp is None:
        return None
    
    market_share = best_comp.get("market_share")
    
    # Count active SmartSaaS users
    users_dir = os.path.join(workspace, "data", "users")
    active_users = []
    costs = []
    if os.path.isdir(users_dir):
        for fname in os.listdir(users_dir):
            if not fname.endswith(".json"):
                continue
            fpath = os.path.join(users_dir, fname)
            with open(fpath, "r") as f:
                try:
                    u = json.load(f)
                except:
                    continue
            if u.get("competitor_id") != "SmartSaaS":
                continue
            # Exclude archived users
            archived = u.get("archived", False)
            if archived:
                continue
            active_users.append(u)
            costs.append(u.get("acquisition_cost", 0))
    
    total_users = len(active_users)
    if total_users == 0:
        avg_cost = 0.0
    else:
        avg_cost = sum(costs) / total_users
    
    return {
        "total_users": total_users,
        "avg_acquisition_cost": avg_cost,
        "market_share": market_share
    }

def _write_score(total, max_total, details):
    final = {"total_score": total, "details": details}
    with open("workplace_score.json", "w") as f:
        json.dump(final, f, indent=2)

if __name__ == "__main__":
    main()
