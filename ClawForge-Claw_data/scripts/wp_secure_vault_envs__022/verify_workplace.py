"""
Verify workplace output for wp_secure_vault_envs__022.
Checks:
1. ops/ directory exists
2. ops/weak_creds.json exists and is valid JSON
3. ops/autofill_rules.json exists and is valid JSON
4. weak_creds.json contains exactly the 3 expected weak entries from target categories
5. autofill_rules.json contains exactly the 3 work email platforms with correct fields
"""
import sys
import os
import json
import csv

def score():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0
    max_total = 100
    
    # Helper to write score
    def record(item, score, max_score, passed, reason):
        details.append({
            "item": item,
            "score": score,
            "max_score": max_score,
            "passed": passed,
            "reason": reason
        })
        return score
    
    # 1. Check ops/ directory (10 pts)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        total_score += record("ops/ directory exists", 10, 10, True, "Directory found.")
    else:
        total_score += record("ops/ directory exists", 0, 10, False, "Directory 'ops/' not found.")
        # If ops missing, further checks impossible, finish early
        _write_score(total_score, details)
        return
    
    # 2. Check weak_creds.json (45 pts total)
    weak_path = os.path.join(ops_dir, "weak_creds.json")
    if not os.path.isfile(weak_path):
        total_score += record("weak_creds.json exists", 0, 45, False, "File not found.")
        # still check autofill
    else:
        try:
            with open(weak_path, "r") as f:
                weak_data = json.load(f)
        except (json.JSONDecodeError, ValueError):
            total_score += record("weak_creds.json format", 0, 45, False, "Invalid JSON.")
            weak_data = None
        
        if weak_data is not None:
            # Check it's a list of dicts
            if not isinstance(weak_data, list):
                total_score += record("weak_creds.json structure", 0, 5, False, "Should be a list.")
            else:
                total_score += record("weak_creds.json structure (list)", 5, 5, True, "Is a list.")
                
                # Expected weak creds (order doesn't matter)
                expected_weak = [
                    {"platform": "corpmail", "username": "admin@company.com", "category": "工作邮箱"},
                    {"platform": "bofa", "username": "jdoe", "category": "银行账户"},
                    {"platform": "outlook", "username": "user1", "category": "工作邮箱"}
                ]
                
                # Normalize: check each entry has required fields
                fieldset = {"platform", "username", "category"}
                valid_entries = [e for e in weak_data if isinstance(e, dict) and fieldset.issubset(e.keys())]
                if len(valid_entries) != 3:
                    total_score += record("weak_creds.json count", 0, 40, False, f"Expected 3 entries, got {len(valid_entries)}.")
                else:
                    # Compare by sorting by platform for deterministic check
                    sorted_valid = sorted(valid_entries, key=lambda x: x["platform"])
                    sorted_expected = sorted(expected_weak, key=lambda x: x["platform"])
                    match = True
                    for act, exp in zip(sorted_valid, sorted_expected):
                        if act["platform"] != exp["platform"] or act["username"] != exp["username"] or act["category"] != exp["category"]:
                            match = False
                            break
                    if match:
                        total_score += record("weak_creds.json exact match", 40, 40, True, "All 3 expected entries present and correct.")
                    else:
                        total_score += record("weak_creds.json exact match", 0, 40, False, f"Content mismatch. Expected {sorted_expected}, got {sorted_valid}.")
    
    # 3. Check autofill_rules.json (45 pts total)
    rules_path = os.path.join(ops_dir, "autofill_rules.json")
    if not os.path.isfile(rules_path):
        total_score += record("autofill_rules.json exists", 0, 45, False, "File not found.")
    else:
        try:
            with open(rules_path, "r") as f:
                rules_data = json.load(f)
        except (json.JSONDecodeError, ValueError):
            total_score += record("autofill_rules.json format", 0, 45, False, "Invalid JSON.")
            rules_data = None
        
        if rules_data is not None:
            if not isinstance(rules_data, list):
                total_score += record("autofill_rules.json structure", 0, 5, False, "Should be a list.")
            else:
                total_score += record("autofill_rules.json structure (list)", 5, 5, True, "Is a list.")
                
                # Expected rules (order doesn't matter)
                expected_rules = [
                    {"platform": "corpmail", "username": "admin@company.com", "auto_fill_enabled": True, "fill_interval": 30},
                    {"platform": "outlook", "username": "user1", "auto_fill_enabled": True, "fill_interval": 30},
                    {"platform": "gmail", "username": "boss@gmail.com", "auto_fill_enabled": True, "fill_interval": 30}
                ]
                # We also allow rule for yahoo? In data yahoo is 工作邮箱 with username info@corp.com. Actually row 60 is yahoo, category 工作邮箱. So 4 platforms? Let's count: corpmail, outlook, gmail, yahoo. That's 4. But we only have 3 in expected? Wait we need to check: In env_builder we have row 60: platform=yahoo, username=info@corp.com, category=工作邮箱. So there are 4 work email platforms. Prompt says "为工作邮箱下所有平台配置自动填充规则". So agent should include all: corpmail, outlook, gmail, yahoo. Let's adjust expected to 4.
                # We'll recompute expected from the real data by reading vault_entries.csv.
                # However, to keep verify self-contained, we can recompute from the env_builder logic by re-reading the CSV? But script only uses standard library and should not rely on env_builder running. We can embed the known list from env_builder:
                # Actually it's fine to hard-code the 4 platforms, but ensure consistency. Let's double-check:
                # rows: 10 corpmail (工作邮箱), 30 outlook (工作邮箱), 40 gmail (工作邮箱), 60 yahoo (工作邮箱). So 4.
                # Update expected_rules:
                expected_rules = [
                    {"platform": "corpmail", "username": "admin@company.com"},
                    {"platform": "outlook", "username": "user1"},
                    {"platform": "gmail", "username": "boss@gmail.com"},
                    {"platform": "yahoo", "username": "info@corp.com"}
                ]
                # Each rule must have auto_fill_enabled=true and fill_interval=30
                required_fields = {"platform", "username", "auto_fill_enabled", "fill_interval"}
                valid_rules = [r for r in rules_data if isinstance(r, dict) and required_fields.issubset(r.keys())]
                if len(valid_rules) != 4:
                    total_score += record("autofill_rules.json count", 0, 40, False, f"Expected 4 rules, got {len(valid_rules)}.")
                else:
                    # Check each expected rule exists (by platform)
                    match = True
                    for exp in expected_rules:
                        found = False
                        for act in valid_rules:
                            if act["platform"] == exp["platform"] and act["username"] == exp["username"]:
                                if act.get("auto_fill_enabled") is True and act.get("fill_interval") == 30:
                                    found = True
                                    break
                        if not found:
                            match = False
                            break
                    if match:
                        total_score += record("autofill_rules.json exact match", 40, 40, True, "All 4 platforms with correct fields.")
                    else:
                        total_score += record("autofill_rules.json exact match", 0, 40, False, "Rule content mismatch.")
    
    # Final score capped at 100
    final_score = min(total_score, 100)
    _write_score(final_score, details)

def _write_score(total_score, details):
    result = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"Score: {total_score}/100")

if __name__ == "__main__":
    score()
