import sys
import json
import os

def verify(workspace):
    details = []
    total_score = 0
    max_possible = 100

    # ---------- 1. Check required directories exist ----------
    dirs_ok = True
    for d in ["data", "ops"]:
        if not os.path.isdir(os.path.join(workspace, d)):
            details.append({
                "item": f"Directory '{d}' exists",
                "score": 0,
                "max_score": 5,
                "passed": False,
                "reason": f"Missing required directory: {d}"
            })
            dirs_ok = False
            total_score += 0
        else:
            details.append({
                "item": f"Directory '{d}' exists",
                "score": 5,
                "max_score": 5,
                "passed": True,
                "reason": "Found"
            })
            total_score += 5
    if not dirs_ok:
        # cannot proceed without basic structure
        details.append({"item": "Fatal: missing directories", "score": 0, "max_score": 0, "passed": False, "reason": "Abort"})
        return {"total_score": total_score, "details": details}

    max_possible = 100  # reset after adjusting scoring

    # ---------- 2. Check required input files (source of truth) ----------
    input_files = ["data/companies.json", "data/contacts.json"]
    for f in input_files:
        fp = os.path.join(workspace, f)
        if not os.path.isfile(fp):
            details.append({
                "item": f"Input file '{f}' exists",
                "score": 0,
                "max_score": 5,
                "passed": False,
                "reason": "Missing"
            })
            total_score += 0
        else:
            details.append({
                "item": f"Input file '{f}' exists",
                "score": 5,
                "max_score": 5,
                "passed": True,
                "reason": "Found"
            })
            total_score += 5

    # ---------- 3. Check agent output file exists ----------
    output_path = os.path.join(workspace, "ops/updated_contacts.json")
    if not os.path.isfile(output_path):
        details.append({
            "item": "Agent output 'ops/updated_contacts.json' exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not found"
        })
        total_score += 0
        # cannot proceed
        return {"total_score": total_score, "details": details}
    else:
        details.append({
            "item": "Agent output exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "File found"
        })
        total_score += 10

    # ---------- 4. Load original contacts and companies ----------
    with open(os.path.join(workspace, "data/companies.json")) as f:
        companies = json.load(f)
    with open(os.path.join(workspace, "data/contacts.json")) as f:
        original_contacts = json.load(f)
    with open(output_path) as f:
        try:
            updated_contacts = json.load(f)
        except json.JSONDecodeError:
            details.append({
                "item": "Output file is valid JSON",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": "Invalid JSON"
            })
            total_score += 10
            return {"total_score": total_score, "details": details}

    details.append({
        "item": "Output file is valid JSON",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "Valid"
    })
    total_score += 10

    # Build lookup: company_id -> industry
    company_industry = {c["company_id"]: c["industry"] for c in companies}

    # Determine expected modified contact IDs
    # Rule: contact_type == "business" AND company industry == "Technology"
    # For those contacts, folder must be "business" and tags must include "tech_client"
    expected_modify_ids = set()
    for c in original_contacts:
        comp_id = c["company_id"]
        if comp_id not in company_industry:
            continue
        if c["contact_type"] == "business" and company_industry[comp_id] == "Technology":
            expected_modify_ids.add(c["contact_id"])

    # Build map of original contacts by id
    orig_map = {c["contact_id"]: c for c in original_contacts}
    updated_map = {c["contact_id"]: c for c in updated_contacts}

    # ---------- 5. Check that all original contacts are present in output ----------
    score_contact_count = 0
    if set(orig_map.keys()) != set(updated_map.keys()):
        details.append({
            "item": "All original contact IDs present in output",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": f"Missing or extra IDs. Original: {set(orig_map.keys())}, Output: {set(updated_map.keys())}"
        })
        total_score += 0
    else:
        details.append({
            "item": "All original contact IDs present in output",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": "All IDs accounted for"
        })
        total_score += 15

    # ---------- 6. Verify modifications for target contacts ----------
    modification_score = 0
    max_mod = 30
    mod_issues = []
    for cid in expected_modify_ids:
        if cid not in updated_map:
            mod_issues.append(f"Missing {cid}")
            continue
        updated = updated_map[cid]
        original = orig_map[cid]
        # Check folder == "business"
        if updated.get("folder") != "business":
            mod_issues.append(f"{cid}: folder is '{updated.get('folder')}', expected 'business'")
        # Check tags contain "tech_client"
        if "tech_client" not in updated.get("tags", []):
            mod_issues.append(f"{cid}: tags missing 'tech_client' (tags={updated.get('tags')})")
        # Ensure other fields unchanged (except folder and tags)
        for field in ["first_name", "last_name", "email", "phone", "company_id", "job_title", "department", "contact_type"]:
            if updated.get(field) != original.get(field):
                mod_issues.append(f"{cid}: field '{field}' changed from '{original.get(field)}' to '{updated.get(field)}'")
                break
        # Ensure tags still contain original tags (unless removed intentionally, but allow additions)
        original_tags = set(original.get("tags", []))
        updated_tags = set(updated.get("tags", []))
        if not original_tags.issubset(updated_tags):
            mod_issues.append(f"{cid}: lost some original tags (original: {original_tags}, now: {updated_tags})")
    if not mod_issues:
        modification_score = max_mod
        details.append({
            "item": "Modifications for all target contacts correct",
            "score": max_mod,
            "max_score": max_mod,
            "passed": True,
            "reason": "All target contacts have folder='business' and tags contain 'tech_client', other fields unchanged"
        })
        total_score += max_mod
    else:
        details.append({
            "item": "Modifications for all target contacts correct",
            "score": 0,
            "max_score": max_mod,
            "passed": False,
            "reason": "; ".join(mod_issues)
        })
        total_score += 0

    # ---------- 7. Verify non-target contacts are unchanged ----------
    non_target_score = 0
    max_non = 20
    non_issues = []
    for cid, updated in updated_map.items():
        if cid in expected_modify_ids:
            continue
        original = orig_map[cid]
        if updated != original:
            non_issues.append(f"{cid}: non-target contact was modified")
    if not non_issues:
        non_target_score = max_non
        details.append({
            "item": "Non-target contacts not modified",
            "score": max_non,
            "max_score": max_non,
            "passed": True,
            "reason": "All non-target contacts identical to original"
        })
        total_score += max_non
    else:
        details.append({
            "item": "Non-target contacts not modified",
            "score": 0,
            "max_score": max_non,
            "passed": False,
            "reason": "; ".join(non_issues)
        })
        total_score += 0

    # ---------- 8. (Bonus) Check no extra file pollution ----------
    # Not required, but if agent created other files might indicate sloppiness? We ignore for simplicity.

    total_score = min(total_score, 100)  # cap
    return {"total_score": total_score, "details": details}

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))
