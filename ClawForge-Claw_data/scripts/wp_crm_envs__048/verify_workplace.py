import json
import sys
import os
from pathlib import Path

def load_json_rel(path):
    """Load JSON relative to workspace, return None if not found or invalid."""
    full = Path(workspace) / path
    if not full.exists():
        return None
    try:
        with open(full, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, Exception):
        return None

def build_expected():
    """From original contacts and companies, compute the set of contacts that
    should have been modified and their expected tags."""
    # load original data (from the same workspace)
    companies_raw = load_json_rel("data/companies.json")
    contacts_raw = load_json_rel("data/contacts.json")

    if not companies_raw or not contacts_raw:
        return None, "Cannot load original data files"

    # map company name -> company_id
    name_to_id = {}
    for comp in companies_raw.get("companies", []):
        name = comp.get("name")
        cid = comp.get("company_id")
        if name and cid:
            name_to_id[name] = cid

    target_names = ["ClientCo Operations", "TechCorp Industries"]
    target_company_ids = {name_to_id.get(n) for n in target_names if name_to_id.get(n)}

    # mapping: company_id -> tag to add
    company_tag_map = {}
    if "comp_clientco" in target_company_ids:
        company_tag_map["comp_clientco"] = "vip_client"
    if "comp_techcorp" in target_company_ids:
        company_tag_map["comp_techcorp"] = "tech_partner"

    expected_contacts = []
    for c in contacts_raw.get("contacts", []):
        cid = c.get("company_id")
        if cid in company_tag_map:
            new_tag = company_tag_map[cid]
            old_tags = list(c.get("tags", []))
            if new_tag not in old_tags:
                new_tags = old_tags + [new_tag]
            else:
                new_tags = old_tags  # already has it
            # build the modified contact (keeping all other fields)
            modified = dict(c)
            modified["tags"] = new_tags
            expected_contacts.append(modified)

    expected_contacts.sort(key=lambda x: x.get("contact_id", ""))
    return expected_contacts, None

def main():
    global workspace
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."

    details = []
    total_score = 0
    max_total = 100

    # 1. check that ops/updated_contacts.json exists
    target_path = Path(workspace) / "ops" / "updated_contacts.json"
    if target_path.exists():
        details.append({
            "item": "Output file exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "ops/updated_contacts.json found"
        })
        total_score += 10
    else:
        details.append({
            "item": "Output file exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ops/updated_contacts.json not found"
        })
        # cannot proceed further
        _write_score(total_score, details)
        return

    # 2. check JSON validity and structure
    agent_data = load_json_rel("ops/updated_contacts.json")
    if agent_data is None:
        details.append({
            "item": "JSON validity",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Invalid JSON or cannot parse"
        })
        _write_score(total_score, details)
        return

    if not isinstance(agent_data, dict) or "contacts" not in agent_data:
        details.append({
            "item": "JSON structure has wrapper 'contacts'",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Missing top-level 'contacts' key or wrong format"
        })
        _write_score(total_score, details)
        return

    details.append({
        "item": "JSON structure",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "Valid JSON with 'contacts' wrapper"
    })
    total_score += 10

    # 3. build expected list
    expected, err_msg = build_expected()
    if err_msg:
        details.append({
            "item": "Build expected data",
            "score": 0,
            "max_score": 30,
            "passed": False,
            "reason": err_msg
        })
        _write_score(total_score, details)
        return

    agent_contacts = agent_data.get("contacts", [])

    # normalize for comparison (sort by contact_id)
    agent_sorted = sorted(agent_contacts, key=lambda x: x.get("contact_id", ""))
    expected_sorted = sorted(expected, key=lambda x: x.get("contact_id", ""))

    # 4. check contact count
    if len(agent_sorted) != len(expected_sorted):
        details.append({
            "item": "Number of modified contacts",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"Expected {len(expected_sorted)} contacts but got {len(agent_sorted)}"
        })
        total_score += 0
    else:
        details.append({
            "item": "Number of modified contacts",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": f"Correct count {len(expected_sorted)}"
        })
        total_score += 20

    # 5. detailed comparison (only if counts match, else still try to compare as much as possible)
    field_score = 0
    max_field = 50
    # compare each expected contact with agent's version
    # we need to find agent's version by contact_id
    agent_map = {c.get("contact_id"): c for c in agent_sorted}
    expected_map = {c.get("contact_id"): c for c in expected_sorted}

    common_ids = set(agent_map.keys()) & set(expected_map.keys())
    extra_ids = set(agent_map.keys()) - set(expected_map.keys())
    missing_ids = set(expected_map.keys()) - set(agent_map.keys())

    field_errors = []

    # missing contacts
    if missing_ids:
        field_errors.append(f"Missing contacts: {', '.join(sorted(missing_ids))}")
    if extra_ids:
        field_errors.append(f"Unexpected contacts: {', '.join(sorted(extra_ids))}")

    # for common ids, compare fields (especially tags)
    for cid in common_ids:
        exp = expected_map[cid]
        act = agent_map[cid]
        # compare tags (order does not matter)
        exp_tags = set(exp.get("tags", []))
        act_tags = set(act.get("tags", []))
        if exp_tags != act_tags:
            field_errors.append(
                f"Contact {cid}: expected tags {sorted(exp_tags)}, got {sorted(act_tags)}"
            )
        # also other fields should match the original (except tags)
        for key in ["contact_id", "first_name", "last_name", "full_name", "email",
                     "phone", "company_id", "job_title", "department", "contact_type", "folder"]:
            if exp.get(key) != act.get(key):
                field_errors.append(f"Contact {cid}: field '{key}' mismatch (expected '{exp.get(key)}', got '{act.get(key)}')")

    if not field_errors:
        field_score = max_field
        details.append({
            "item": "Correctness of modified contacts (fields and tags)",
            "score": max_field,
            "max_score": max_field,
            "passed": True,
            "reason": "All contacts match expected content"
        })
    else:
        # partial score: each error reduces by a portion, min 0
        deduction = len(field_errors) * 10
        field_score = max(0, max_field - deduction)
        details.append({
            "item": "Correctness of modified contacts (fields and tags)",
            "score": field_score,
            "max_score": max_field,
            "passed": False,
            "reason": "; ".join(field_errors[:5])  # show first few errors
        })
    total_score += field_score

    # write final score
    _write_score(total_score, details)

def _write_score(total_score, details):
    # cap to 100
    total_score = min(total_score, 100)
    result = {
        "total_score": total_score,
        "details": details
    }
    with open(Path(workspace) / "workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
