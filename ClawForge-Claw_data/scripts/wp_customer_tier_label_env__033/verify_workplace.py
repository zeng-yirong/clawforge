"""
Verify that the agent produced the correct updated_customers.json.
"""

import json
import os
import sys

def verify(workspace: str) -> dict:
    details = []
    total = 0
    max_total = 100

    # 1. Check directory structure (ops/ exists)
    ops_dir = os.path.join(workspace, "ops")
    dir_ok = os.path.isdir(ops_dir)
    details.append({
        "item": "ops directory exists",
        "score": 10 if dir_ok else 0,
        "max_score": 10,
        "passed": dir_ok,
        "reason": "ops/ found" if dir_ok else "ops/ missing"
    })
    if dir_ok:
        total += 10

    # 2. Check output file exists
    out_path = os.path.join(workspace, "ops", "updated_customers.json")
    file_ok = os.path.isfile(out_path)
    details.append({
        "item": "updated_customers.json exists",
        "score": 10 if file_ok else 0,
        "max_score": 10,
        "passed": file_ok,
        "reason": "file found" if file_ok else "file missing"
    })
    if file_ok:
        total += 10

    # 3. JSON valid and correct structure
    if file_ok:
        try:
            with open(out_path, "r") as f:
                data = json.load(f)
        except (json.JSONDecodeError, Exception) as e:
            details.append({
                "item": "JSON format valid",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"invalid JSON: {e}"
            })
            total += 0  # subsequent checks skipped, but we still return what we have
            return {"total_score": total, "details": details}
        else:
            format_ok = isinstance(data, dict) and "customers" in data and isinstance(data["customers"], list)
            details.append({
                "item": "JSON structure (has customers array)",
                "score": 10 if format_ok else 0,
                "max_score": 10,
                "passed": format_ok,
                "reason": "correct structure" if format_ok else "missing customers key or not a list"
            })
            if format_ok:
                total += 10
            else:
                return {"total_score": total, "details": details}
    else:
        # file missing, can't check further
        return {"total_score": total, "details": details}

    # 4. Customer count (expect exactly 3)
    customers = data["customers"]
    count_ok = len(customers) == 3
    details.append({
        "item": "Customer count (expected 3)",
        "score": 10 if count_ok else 0,
        "max_score": 10,
        "passed": count_ok,
        "reason": f"found {len(customers)} customers" if count_ok else f"found {len(customers)} (expected 3)"
    })
    if count_ok:
        total += 10

    # 5. Labels for each customer
    # expected labels (as sets)
    expected_labels = {
        "cust_001": {"existing", "active", "high_value"},
        "cust_002": {"churn_risk", "low_spend", "declining"},
        "cust_003": {"vip", "active", "mid_value", "growing"}  # mid_value because spend 8000 >5000 but <10000, growing because trend up
    }
    # Note: for cust_003, spend=8000, trend=up => "growing"? But we didn't define growing in rule. Wait, rule says usage_trend down => declining, but no rule for up? We'll assume only down triggers 'declining'; up triggers nothing. So cust_003 should only have "active" (since last_active_days<30) and "mid_value" (spend between 5000 and 10000? Actually rule: >10000 => high_value; <5000 => low_spend; else nothing. So no "growing". Let's adjust: we need a rule for up? In prompt we only mentioned "declining" for down. So for cust_003, spend 8000 is not high_value, not low_spend, but trend up does not have a label. So only "active" + retain "vip". Also, what about "mid_value"? We didn't define that in prompt. To avoid confusion, let's keep the expected correct set as {"vip", "active"} only. But the prompt says "趋势下降加declining", no mention of up. So no label for up. So cust_003 expected = {"vip", "active"}. Wait, we need to be consistent with the truth we designed. Let's re-evaluate: In the initial design we thought "mid_value" and "growing", but prompt didn't include those. We must stick to the rules given in the prompt. The prompt says: 
# - 最近30天内有活跃的（last_active_days < 30） → 加 “active”
# - 超过90天没动弹、而且风险等级是 high 的 → 加 “churn_risk”
# - 季度消费超过 10000 并且使用趋势在上升 → 加 “high_value”
# - 季度消费不到 5000 的 → 加 “low_spend”
# - 使用趋势下降 → 加 “declining”
# So for cust_003: last_active_days=5 (<30) => "active"; spend=8000 (not <5000, not >10000) => no label; trend=up => no label. So final labels = ["vip", "active"].
# Also, for cust_001: spend 12000>10000 and trend up => "high_value"; active days<30 => "active"; risk low => no churn; existing kept. So {"existing", "active", "high_value"}.
# For cust_002: active days=120>90 and risk high => "churn_risk"; spend=3000<5000 => "low_spend"; trend down => "declining". So {"churn_risk", "low_spend", "declining"}.
# That is consistent. So expected_labels as above.

    # Actually need to adjust expected_labels for cust_003: {"vip", "active"}
    # Let's correct:
    expected_labels = {
        "cust_001": {"existing", "active", "high_value"},
        "cust_002": {"churn_risk", "low_spend", "declining"},
        "cust_003": {"vip", "active"}
    }

    # Build lookup by customer_id
    customer_map = {c["customer_id"]: c for c in customers}
    # Check each expected id
    all_ids_ok = True
    missing_ids = []
    for cid in expected_labels:
        if cid not in customer_map:
            all_ids_ok = False
            missing_ids.append(cid)
    if missing_ids:
        details.append({
            "item": "All expected customer_ids present",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"missing customer_ids: {missing_ids}"
        })
        total += 0
    else:
        details.append({
            "item": "All expected customer_ids present",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "cust_001, cust_002, cust_003 all found"
        })
        total += 10

    # Check labels for each
    labels_ok = True
    label_fail_reasons = []
    for cid, expected_set in expected_labels.items():
        actual = set(customer_map[cid].get("labels", []))
        if actual != expected_set:
            labels_ok = False
            label_fail_reasons.append(f"{cid}: got {sorted(actual)}, expected {sorted(expected_set)}")
    if labels_ok:
        details.append({
            "item": "Labels match expected for all customers",
            "score": 40,
            "max_score": 40,
            "passed": True,
            "reason": "all labels correct"
        })
        total += 40
    else:
        # Partial credit: 10 per correct customer
        correct_count = sum(1 for cid in expected_labels if set(customer_map[cid].get("labels", [])) == expected_labels[cid])
        score = correct_count * 10
        details.append({
            "item": "Labels match expected for all customers",
            "score": score,
            "max_score": 40,
            "passed": False,
            "reason": "; ".join(label_fail_reasons) if label_fail_reasons else "partial"
        })
        total += score

    # 6. No extra customers (decoy not included)
    extra_cids = [c["customer_id"] for c in customers if c["customer_id"] not in expected_labels]
    if extra_cids:
        details.append({
            "item": "No extra customers (decoy absent)",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"found extra customer_ids: {extra_cids}"
        })
    else:
        details.append({
            "item": "No extra customers (decoy absent)",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "no unexpected customers"
        })
        total += 10 if not extra_cids else 0

    return {"total_score": total, "details": details}

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    # Write score file
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))
