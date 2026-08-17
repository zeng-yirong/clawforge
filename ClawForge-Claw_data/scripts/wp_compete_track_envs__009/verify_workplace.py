import os
import sys
import json
import math

def load_json(filepath):
    with open(filepath, "r") as f:
        return json.load(f)

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    total_score = 0
    details = []

    def add_detail(item, score, max_score, passed, reason):
        details.append({
            "item": item,
            "score": score,
            "max_score": max_score,
            "passed": passed,
            "reason": reason
        })
        return score

    # 1) ops/ directory exists (5 points)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        total_score += add_detail("ops/ directory exists", 5, 5, True, "Directory found.")
    else:
        total_score += add_detail("ops/ directory exists", 0, 5, False, "Missing ops/ directory.")

    # 2) campaign_analysis.json exists (5 points)
    report_path = os.path.join(ops_dir, "campaign_analysis.json")
    if os.path.isfile(report_path):
        total_score += add_detail("campaign_analysis.json exists", 5, 5, True, "File found.")
    else:
        total_score += add_detail("campaign_analysis.json exists", 0, 5, False, "File not found.")
        # If file missing, we cannot check further content; assign 0 for remaining
        add_detail("JSON format valid", 0, 10, False, "Skipped due to missing file.")
        add_detail("Correct keys in output", 0, 10, False, "Skipped.")
        add_detail("User count correct", 0, 15, False, "Skipped.")
        add_detail("Per-source cost correct", 0, 20, False, "Skipped.")
        add_detail("Per-source LTV correct", 0, 20, False, "Skipped.")
        add_detail("Dirty data excluded", 0, 15, False, "Skipped.")
        write_score(total_score, details)
        return

    # 3) JSON format valid (10 points)
    try:
        data = load_json(report_path)
        total_score += add_detail("JSON format valid", 10, 10, True, "Valid JSON.")
    except Exception as e:
        total_score += add_detail("JSON format valid", 0, 10, False, f"Invalid JSON: {e}")
        # skip remaining checks
        add_detail("Correct keys in output", 0, 10, False, "Skipped.")
        add_detail("User count correct", 0, 15, False, "Skipped.")
        add_detail("Per-source cost correct", 0, 20, False, "Skipped.")
        add_detail("Per-source LTV correct", 0, 20, False, "Skipped.")
        add_detail("Dirty data excluded", 0, 15, False, "Skipped.")
        write_score(total_score, details)
        return

    # 4) Expected structure: list of source entries
    if isinstance(data, list):
        sources = data
    elif isinstance(data, dict):
        # allow wrapping key like "sources" or "results"
        sources = data.get("sources") or data.get("results") or data.get("data")
        if sources is None:
            total_score += add_detail("Correct keys in output", 0, 10, False, "No list found inside JSON.")
            add_detail("User count correct", 0, 15, False, "Skipped.")
            add_detail("Per-source cost correct", 0, 20, False, "Skipped.")
            add_detail("Per-source LTV correct", 0, 20, False, "Skipped.")
            add_detail("Dirty data excluded", 0, 15, False, "Skipped.")
            write_score(total_score, details)
            return
    else:
        total_score += add_detail("Correct keys in output", 0, 10, False, "Output is not a list or dict with list.")
        add_detail("User count correct", 0, 15, False, "Skipped.")
        add_detail("Per-source cost correct", 0, 20, False, "Skipped.")
        add_detail("Per-source LTV correct", 0, 20, False, "Skipped.")
        add_detail("Dirty data excluded", 0, 15, False, "Skipped.")
        write_score(total_score, details)
        return

    # Check each source entry has required fields
    required_fields = {"source", "total_cost", "total_ltv", "user_count"}
    all_have_fields = True
    for entry in sources:
        if not isinstance(entry, dict):
            all_have_fields = False
            break
        if not required_fields.issubset(entry.keys()):
            all_have_fields = False
            break
    if all_have_fields and len(sources) > 0:
        total_score += add_detail("Correct keys in output", 10, 10, True,
                                  f"All {len(sources)} entries have source, total_cost, total_ltv, user_count.")
    else:
        total_score += add_detail("Correct keys in output", 0, 10, False,
                                  "Missing required fields or empty list.")

    # --- Compute expected values from raw data (same as builder logic) ---
    # Load all competitors
    comp_dir = os.path.join(workspace, "competitors")
    expected_sources = {}
    if os.path.isdir(comp_dir):
        for fname in os.listdir(comp_dir):
            if not fname.endswith(".json"):
                continue
            try:
                comp = load_json(os.path.join(comp_dir, fname))
            except:
                continue
            if comp.get("sector") != "Cloud Computing":
                continue
            competitor_id = comp.get("competitor_id")
            if not competitor_id:
                continue
            # Load all users
            users_dir = os.path.join(workspace, "users")
            if not os.path.isdir(users_dir):
                continue
            for ufname in os.listdir(users_dir):
                if not ufname.endswith(".json"):
                    continue
                try:
                    user = load_json(os.path.join(users_dir, ufname))
                except:
                    continue
                if user.get("competitor_id") != competitor_id:
                    continue
                # Cleanliness checks: acquisition_cost must be int > 0, source non-empty
                cost = user.get("acquisition_cost")
                source = user.get("acquisition_source")
                ltv = user.get("lifetime_value")
                if not isinstance(cost, int) or cost <= 0:
                    continue
                if not isinstance(source, str) or source.strip() == "":
                    continue
                if not isinstance(ltv, (int, float)):
                    continue
                # aggregate
                if source not in expected_sources:
                    expected_sources[source] = {"total_cost": 0, "total_ltv": 0, "user_count": 0}
                expected_sources[source]["total_cost"] += cost
                expected_sources[source]["total_ltv"] += ltv
                expected_sources[source]["user_count"] += 1
    # else no competitors directory -> expected empty

    # Compare
    # Build a dict from agent output for comparison
    agent_map = {}
    for entry in sources:
        src = entry.get("source")
        agent_map[src] = entry

    # Check user count total
    expected_total_users = sum(v["user_count"] for v in expected_sources.values())
    agent_total_users = sum(v.get("user_count", 0) for v in agent_map.values())
    if agent_total_users == expected_total_users:
        total_score += add_detail("User count correct", 15, 15, True,
                                  f"Total users: {agent_total_users} (expected {expected_total_users})")
    else:
        total_score += add_detail("User count correct", 0, 15, False,
                                  f"Total users: {agent_total_users} (expected {expected_total_users})")

    # Per-source cost (20 points, 5 each for up to 4 sources)
    source_cost_ok = 0
    source_ltv_ok = 0
    for src, exp in expected_sources.items():
        agent_entry = agent_map.get(src, {})
        # cost
        exp_cost = exp["total_cost"]
        agent_cost = agent_entry.get("total_cost")
        if agent_cost == exp_cost:
            source_cost_ok += 1
        # ltv
        exp_ltv = exp["total_ltv"]
        agent_ltv = agent_entry.get("total_ltv")
        if agent_ltv == exp_ltv:
            source_ltv_ok += 1
    # Also check that agent didn't include extra sources (dirty data)
    extra_sources = set(agent_map.keys()) - set(expected_sources.keys())
    if extra_sources:
        # penalize: each extra source could indicate dirty data included
        pass  # we handle dirty exclusion separately

    max_possible_sources = max(len(expected_sources), 1)  # avoid division by zero
    cost_max = 20 if len(expected_sources) >= 4 else (len(expected_sources) * 5)
    # but we award proportional
    cost_score = min(20, int(source_cost_ok * 20 / max_possible_sources)) if max_possible_sources > 0 else 0
    ltv_score = min(20, int(source_ltv_ok * 20 / max_possible_sources)) if max_possible_sources > 0 else 0
    total_score += add_detail("Per-source cost correct", cost_score, 20, cost_score == 20,
                              f"Cost: {source_cost_ok}/{max_possible_sources} sources correct.")
    total_score += add_detail("Per-source LTV correct", ltv_score, 20, ltv_score == 20,
                              f"LTV: {source_ltv_ok}/{max_possible_sources} sources correct.")

    # Dirty data exclusion (15 points)
    # Check that agent's sources do not contain data from dirty users
    # If agent included dirty source (e.g., "referral" from dirty user but with wrong cost) we can detect
    # Simpler: check that agent's total users equals expected clean count, and no extra source appears
    dirty_penalty = 0
    if extra_sources:
        dirty_penalty += 5  # each extra source may indicate dirty user inclusion
    if agent_total_users != expected_total_users:
        dirty_penalty += 10
    dirty_score = max(0, 15 - dirty_penalty)
    passed_dirty = (dirty_score == 15)
    total_score += add_detail("Dirty data excluded", dirty_score, 15, passed_dirty,
                              f"Expected {expected_total_users} clean users, agent had {agent_total_users}. Extra sources: {extra_sources}.")

    # Write final score
    write_score(total_score, details)

def write_score(total, details):
    result = {
        "total_score": total,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
