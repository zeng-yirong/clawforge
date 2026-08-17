import sys
import json
import os
from pathlib import Path

def check_password_strength(password, policy):
    """Return True if password meets all policy requirements"""
    if len(password) < policy["min_length"]:
        return False
    if policy["require_uppercase"] and not any(c.isupper() for c in password):
        return False
    if policy["require_lowercase"] and not any(c.islower() for c in password):
        return False
    if policy["require_digit"] and not any(c.isdigit() for c in password):
        return False
    # special char not required in this policy
    return True

def expected_category_for_site(site):
    """Heuristic mapping from site domain to expected category"""
    domain = site.lower().split(".")[-2] if "." in site else site
    # Common mappings
    work_domains = {"gmail", "outlook", "yahoo", "corp", "work"}
    ecom_domains = {"amazon", "ebay", "shopify", "alibaba"}
    social_domains = {"facebook", "twitter", "linkedin", "instagram"}
    bank_domains = {"bankofamerica", "chase", "citi", "wellsfargo"}

    # Extract main domain part (e.g., 'gmail' from 'gmail.com')
    parts = site.lower().split(".")
    if len(parts) >= 2:
        main = parts[-2]   # second-level domain
    else:
        main = site.lower()

    if main in work_domains:
        return "work_email"
    if main in ecom_domains:
        return "ecommerce"
    if main in social_domains:
        return "social_media"
    if main in bank_domains:
        return "banking"
    # fallback: use the site itself as unknown – we'll treat as correct if no mapping
    return None

def verify(workspace):
    workspace = Path(workspace)
    results = []
    total_score = 0

    # ---------- 1. Check required directories ----------
    item = {"item": "Directory `ops` exists", "score": 0, "max_score": 10, "passed": False, "reason": ""}
    if (workspace / "ops").is_dir():
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "ops directory found"
    else:
        item["reason"] = "ops directory missing"
    results.append(item)

    # ---------- 2. Check result file exists ----------
    result_path = workspace / "ops" / "security_audit.json"
    item = {"item": "Result file `ops/security_audit.json` exists", "score": 0, "max_score": 10, "passed": False, "reason": ""}
    if result_path.is_file():
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "file exists"
    else:
        item["reason"] = "file missing"
        # Cannot proceed with content checks
        item["score"] = 0
        results.append(item)
        # Still try to load data for detailed scoring? No, skip rest.
        # We'll fill remaining items as 0
        for name, max_s in [("JSON validity", 10), ("weak_password_ids correct", 35), ("misclassified_ids correct", 35)]:
            results.append({
                "item": name,
                "score": 0,
                "max_score": max_s,
                "passed": False,
                "reason": "result file missing"
            })
        total_score = sum(r["score"] for r in results)
        final = {"total_score": total_score, "details": results}
        with open(workspace / "workplace_score.json", "w") as f:
            json.dump(final, f, indent=2)
        return

    # ---------- 3. Validate JSON structure ----------
    item = {"item": "JSON format valid and has required keys", "score": 0, "max_score": 10, "passed": False, "reason": ""}
    try:
        with open(result_path, "r") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError("Top-level must be a dict")
        if "weak_password_ids" not in data or "misclassified_ids" not in data:
            raise ValueError("Missing required keys")
        if not isinstance(data["weak_password_ids"], list) or not isinstance(data["misclassified_ids"], list):
            raise ValueError("Both fields must be lists")
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "valid JSON with required keys"
    except Exception as e:
        item["reason"] = f"Invalid: {e}"
    results.append(item)

    # ---------- 4. Compute expected answers ----------
    # Load policy
    with open(workspace / "policy.json", "r") as f:
        policy = json.load(f)
    # Load vault records
    with open(workspace / "vault_export.json", "r") as f:
        records = json.load(f)

    expected_weak = []
    expected_mis = []
    for rec in records:
        # weak password check
        if not check_password_strength(rec["password"], policy):
            expected_weak.append(rec["id"])
        # misclassification check
        expected_cat = expected_category_for_site(rec["site"])
        if expected_cat is not None and rec["category"] != expected_cat:
            expected_mis.append(rec["id"])

    # Sort both for deterministic comparison
    expected_weak.sort()
    expected_mis.sort()

    # Agent's lists
    agent_weak = data.get("weak_password_ids", [])
    agent_mis = data.get("misclassified_ids", [])
    # Normalize: ensure strings, sort
    agent_weak = sorted([str(x) for x in agent_weak])
    agent_mis  = sorted([str(x) for x in agent_mis])

    # ---------- 5. Score weak_password_ids ----------
    item_w = {"item": "weak_password_ids correct", "score": 0, "max_score": 35, "passed": False, "reason": ""}
    if agent_weak == expected_weak:
        item_w["score"] = 35
        item_w["passed"] = True
        item_w["reason"] = f"Exact match: {expected_weak}"
    else:
        # Partial credit: count mismatches
        set_agent = set(agent_weak)
        set_exp = set(expected_weak)
        common = set_agent & set_exp
        precision = len(common) / len(set_agent) if set_agent else 0
        recall = len(common) / len(set_exp) if set_exp else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        points = int(round(f1 * 35))
        item_w["score"] = points
        item_w["passed"] = points == 35
        missed = set_exp - set_agent
        extra = set_agent - set_exp
        reasons = []
        if missed:
            reasons.append(f"missing: {sorted(missed)}")
        if extra:
            reasons.append(f"extra: {sorted(extra)}")
        item_w["reason"] = "; ".join(reasons) if reasons else "partial match"
    results.append(item_w)

    # ---------- 6. Score misclassified_ids ----------
    item_m = {"item": "misclassified_ids correct", "score": 0, "max_score": 35, "passed": False, "reason": ""}
    if agent_mis == expected_mis:
        item_m["score"] = 35
        item_m["passed"] = True
        item_m["reason"] = f"Exact match: {expected_mis}"
    else:
        set_agent = set(agent_mis)
        set_exp = set(expected_mis)
        common = set_agent & set_exp
        precision = len(common) / len(set_agent) if set_agent else 0
        recall = len(common) / len(set_exp) if set_exp else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        points = int(round(f1 * 35))
        item_m["score"] = points
        item_m["passed"] = points == 35
        missed = set_exp - set_agent
        extra = set_agent - set_exp
        reasons = []
        if missed:
            reasons.append(f"missing: {sorted(missed)}")
        if extra:
            reasons.append(f"extra: {sorted(extra)}")
        item_m["reason"] = "; ".join(reasons) if reasons else "partial match"
    results.append(item_m)

    # Final score
    total_score = sum(r["score"] for r in results)
    final = {
        "total_score": total_score,
        "details": results
    }
    with open(workspace / "workplace_score.json", "w") as f:
        json.dump(final, f, indent=2)


if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
