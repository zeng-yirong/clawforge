"""
Verify the agent's output for wp_crm_envs__019.

Checks that ops/techcorp_fix.json exists, is valid JSON, contains the expected
fixed contacts and the separate list of contacts that were already in the
business folder but missing the 'tech-partner' tag.

Scoring is purely code‑based using Python standard library.
"""
import json
import sys
import os

def verify(workspace: str) -> dict:
    result_path = os.path.join(workspace, "ops", "techcorp_fix.json")
    details = []
    total = 0

    # 1. File existence (10 pts)
    if os.path.isfile(result_path):
        details.append({
            "item": "output file exists",
            "score": 10, "max_score": 10, "passed": True,
            "reason": "ops/techcorp_fix.json found"
        })
        total += 10
    else:
        details.append({
            "item": "output file exists",
            "score": 0, "max_score": 10, "passed": False,
            "reason": "ops/techcorp_fix.json not found"
        })
        return {"total_score": total, "details": details}

    # 2. Valid JSON (10 pts)
    try:
        with open(result_path, "r") as f:
            data = json.load(f)
        details.append({
            "item": "valid JSON",
            "score": 10, "max_score": 10, "passed": True,
            "reason": "File parsed successfully"
        })
        total += 10
    except (json.JSONDecodeError, Exception) as e:
        details.append({
            "item": "valid JSON",
            "score": 0, "max_score": 10, "passed": False,
            "reason": f"Parse error: {e}"
        })
        return {"total_score": total, "details": details}

    # 3. Required top‑level keys (5+5 = 10 pts)
    has_fixed = "fixed_contacts" in data and isinstance(data["fixed_contacts"], list)
    has_missing = "already_business_missing_tag" in data and isinstance(data["already_business_missing_tag"], list)
    if has_fixed:
        details.append({
            "item": "top-level key 'fixed_contacts' exists and is a list",
            "score": 5, "max_score": 5, "passed": True,
            "reason": "fixed_contacts present"
        })
        total += 5
    else:
        details.append({
            "item": "top-level key 'fixed_contacts' exists and is a list",
            "score": 0, "max_score": 5, "passed": False,
            "reason": "fixed_contacts missing or not a list"
        })
    if has_missing:
        details.append({
            "item": "top-level key 'already_business_missing_tag' exists and is a list",
            "score": 5, "max_score": 5, "passed": True,
            "reason": "already_business_missing_tag present"
        })
        total += 5
    else:
        details.append({
            "item": "top-level key 'already_business_missing_tag' exists and is a list",
            "score": 0, "max_score": 5, "passed": False,
            "reason": "already_business_missing_tag missing or not a list"
        })

    fixed = data.get("fixed_contacts", [])
    missing = data.get("already_business_missing_tag", [])

    # 4. Length of fixed_contacts (10 pts)
    if len(fixed) == 2:
        details.append({
            "item": "fixed_contacts length = 2",
            "score": 10, "max_score": 10, "passed": True,
            "reason": "Exactly 2 contacts fixed"
        })
        total += 10
    else:
        details.append({
            "item": "fixed_contacts length = 2",
            "score": 0, "max_score": 10, "passed": False,
            "reason": f"Expected 2, got {len(fixed)}"
        })

    # 5. Length of already_business_missing_tag (10 pts)
    if len(missing) == 1:
        details.append({
            "item": "already_business_missing_tag length = 1",
            "score": 10, "max_score": 10, "passed": True,
            "reason": "Exactly 1 contact in that list"
        })
        total += 10
    else:
        details.append({
            "item": "already_business_missing_tag length = 1",
            "score": 0, "max_score": 10, "passed": False,
            "reason": f"Expected 1, got {len(missing)}"
        })

    # 6. Check fixed_contacts content (20 pts – 10 per contact)
    expected_fixed_ids = {"ct_001", "ct_002"}
    actual_fixed_ids = {c.get("contact_id") for c in fixed}
    score_fixed_ids = 0
    if actual_fixed_ids == expected_fixed_ids:
        score_fixed_ids = 10
        details.append({
            "item": "fixed_contacts contain exactly contact_ids ct_001 and ct_002",
            "score": 10, "max_score": 10, "passed": True,
            "reason": "Correct IDs"
        })
    else:
        details.append({
            "item": "fixed_contacts contain exactly contact_ids ct_001 and ct_002",
            "score": 0, "max_score": 10, "passed": False,
            "reason": f"Expected {{ct_001,ct_002}}, got {actual_fixed_ids}"
        })
    total += score_fixed_ids

    # 7. Check folder = "business" for each fixed contact (10 pts)
    all_folder_ok = all(c.get("folder") == "business" for c in fixed)
    if all_folder_ok and len(fixed) == 2:
        details.append({
            "item": "fixed_contacts all have folder = 'business'",
            "score": 10, "max_score": 10, "passed": True,
            "reason": "Folder corrected"
        })
        total += 10
    else:
        details.append({
            "item": "fixed_contacts all have folder = 'business'",
            "score": 0, "max_score": 10, "passed": False,
            "reason": f"Some contacts have incorrect folder"
        })

    # 8. Check tags for fixed contacts (20 pts – 10 each)
    tag_score = 0
    for c in fixed:
        cid = c.get("contact_id")
        tags = c.get("tags", [])
        tags_set = set(tags)
        if "tech-partner" in tags_set and "vip" in tags_set:
            tag_score += 10
        else:
            # partial
            pass
    if tag_score == 20:
        details.append({
            "item": "fixed_contacts tags include both 'tech-partner' and 'vip'",
            "score": 20, "max_score": 20, "passed": True,
            "reason": "Each contact has both required tags"
        })
    else:
        details.append({
            "item": "fixed_contacts tags include both 'tech-partner' and 'vip'",
            "score": tag_score, "max_score": 20, "passed": tag_score == 20,
            "reason": f"Got {tag_score} points (10 per contact)"
        })
    total += tag_score

    # 9. Check already_business_missing_tag content (10 pts)
    if len(missing) >= 1:
        m = missing[0]
        mid = m.get("contact_id")
        mfolder = m.get("folder")
        mtags = set(m.get("tags", []))
        sub_score = 0
        if mid == "ct_002":
            sub_score += 5
        if mfolder == "business":
            sub_score += 2
        if "tech-partner" in mtags and "vip" in mtags:
            sub_score += 3
        details.append({
            "item": "already_business_missing_tag entry is correct (ct_002, business, both tags)",
            "score": sub_score, "max_score": 10, "passed": sub_score == 10,
            "reason": f"Scored {sub_score}/10: id match={mid=='ct_002'}, folder={mfolder}, tags include required={('tech-partner' in mtags and 'vip' in mtags)}"
        })
        total += sub_score
    else:
        details.append({
            "item": "already_business_missing_tag entry is correct",
            "score": 0, "max_score": 10, "passed": False,
            "reason": "List empty, cannot check"
        })

    return {"total_score": total, "details": details}

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    output_path = os.path.join(workspace, "workplace_score.json")
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written to {output_path}")
