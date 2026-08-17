import sys, os, json, glob

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    max_score = 100
    details = []

    # 1. Check ops directory exists
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        details.append({"item": "ops directory exists", "score": 5, "max_score": 5, "passed": True, "reason": "ops/ found"})
        score += 5
    else:
        details.append({"item": "ops directory exists", "score": 0, "max_score": 5, "passed": False, "reason": "ops/ not found"})

    # 2. Check recommendation.json exists
    rec_path = os.path.join(workspace, "ops", "recommendation.json")
    if os.path.isfile(rec_path):
        details.append({"item": "recommendation.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "file found"})
        score += 10
    else:
        details.append({"item": "recommendation.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "file missing"})
        write_score(score, details, workspace)
        return

    # 3. Parse JSON
    try:
        with open(rec_path, 'r') as f:
            rec = json.load(f)
        details.append({"item": "JSON valid", "score": 10, "max_score": 10, "passed": True, "reason": "valid JSON"})
        score += 10
    except Exception as e:
        details.append({"item": "JSON valid", "score": 0, "max_score": 10, "passed": False, "reason": str(e)})
        write_score(score, details, workspace)
        return

    # 4. Load policy (latest version)
    policy_dir = os.path.join(workspace, "data", "policies")
    policy = None
    if os.path.isdir(policy_dir):
        policy_files = glob.glob(os.path.join(policy_dir, "*.json"))
        best_version = None
        for pf in policy_files:
            try:
                with open(pf) as f:
                    p = json.load(f)
                ver = p.get("version", "")
                if best_version is None or ver > best_version:
                    best_version = ver
                    policy = p
            except:
                pass
    if policy is None:
        details.append({"item": "Policy loading", "score": 0, "max_score": 5, "passed": False, "reason": "no valid policy found"})
        write_score(score, details, workspace)
        return
    else:
        details.append({"item": "Policy loaded", "score": 5, "max_score": 5, "passed": True, "reason": f"found version {policy.get('version')}"})
        score += 5

    # 5. Load active platforms and compute expected
    platform_dir = os.path.join(workspace, "data", "platforms")
    active_platforms = []
    if os.path.isdir(platform_dir):
        platform_files = glob.glob(os.path.join(platform_dir, "*.json"))
        for pf in platform_files:
            try:
                with open(pf) as f:
                    plat = json.load(f)
                if plat.get("is_active") == True:
                    active_platforms.append(plat)
            except:
                pass
    details.append({"item": "Active platforms found", "score": 5, "max_score": 5, "passed": True, "reason": f"found {len(active_platforms)} active platforms"})
    score += 5

    # Compute expected recommendation
    max_single = policy.get("max_single_booking_cost", 0)
    max_per_booking = policy.get("max_cost_per_booking", 0)
    expected_best_platform = None
    expected_best_cost = float('inf')
    expected_all_options = []
    for plat in active_platforms:
        base = plat.get("current_offer", {}).get("base_fare", 0)
        tax = plat.get("current_offer", {}).get("taxes", 0)
        tx_fee = plat.get("transaction_fee", 0)
        svc_fee = plat.get("service_fee", 0)
        total = base + tax + tx_fee + svc_fee
        compliant = (total <= max_single) and (total <= max_per_booking)
        if compliant and total < expected_best_cost:
            expected_best_cost = total
            expected_best_platform = plat["platform_id"]
        expected_all_options.append({
            "platform": plat["platform_id"],
            "total": total,
            "compliant": compliant
        })

    # Check agent output
    rec_platform = rec.get("recommended_platform") or rec.get("recommendation")
    rec_cost = rec.get("total_cost") or rec.get("total")
    rec_compliant = rec.get("compliant")

    # Recommended platform
    if rec_platform == expected_best_platform:
        details.append({"item": "Recommended platform correct", "score": 20, "max_score": 20, "passed": True, "reason": f"expected {expected_best_platform}, got {rec_platform}"})
        score += 20
    else:
        details.append({"item": "Recommended platform correct", "score": 0, "max_score": 20, "passed": False, "reason": f"expected {expected_best_platform}, got {rec_platform}"})

    # Total cost
    if rec_cost == expected_best_cost:
        details.append({"item": "Total cost correct", "score": 20, "max_score": 20, "passed": True, "reason": f"expected {expected_best_cost}, got {rec_cost}"})
        score += 20
    else:
        details.append({"item": "Total cost correct", "score": 0, "max_score": 20, "passed": False, "reason": f"expected {expected_best_cost}, got {rec_cost}"})

    # Compliant flag
    if rec_compliant == True:
        details.append({"item": "Compliant flag correct", "score": 10, "max_score": 10, "passed": True, "reason": "compliant=True"})
        score += 10
    else:
        details.append({"item": "Compliant flag correct", "score": 0, "max_score": 10, "passed": False, "reason": f"expected True, got {rec_compliant}"})

    # Options array (bonus)
    options = rec.get("options") or rec.get("all_options") or rec.get("details")
    if options and isinstance(options, list) and len(options) > 0:
        expected_dict = {o["platform"]: o for o in expected_all_options}
        match_count = 0
        for opt in options:
            pid = opt.get("platform") or opt.get("platform_id")
            if pid in expected_dict:
                exp = expected_dict[pid]
                if opt.get("total") == exp["total"] and opt.get("compliant") == exp["compliant"]:
                    match_count += 1
        if match_count == len(expected_all_options):
            details.append({"item": "Options array accurate", "score": 10, "max_score": 10, "passed": True, "reason": "all options match"})
            score += 10
        else:
            details.append({"item": "Options array accurate", "score": 5, "max_score": 10, "passed": False, "reason": f"matched {match_count}/{len(expected_all_options)}"})
    else:
        details.append({"item": "Options array present", "score": 0, "max_score": 10, "passed": False, "reason": "no options array"})

    write_score(score, details, workspace)

def write_score(score, details, workspace):
    result = {"total_score": min(score, 100), "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score: {score}/100")

if __name__ == "__main__":
    main()
