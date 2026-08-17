import json
import os
import sys

def verify_workplace(workspace):
    """
    Pure code verifier for wp_crm_envs__017.
    Checks that the agent produced ops/add_vendor_tags.json listing contact_ids
    of VendorCo Supplies (company_id=comp_006) contacts who do NOT already have
    the vendor tag (tag_id=tag_vendor_001).
    """
    result = {"total_score": 0, "details": []}

    # Paths
    tag_def_path = os.path.join(workspace, "data/tags/tag_definitions.json")
    contacts_path = os.path.join(workspace, "data/contacts.json")
    companies_path = os.path.join(workspace, "data/companies.json")
    output_path = os.path.join(workspace, "ops/add_vendor_tags.json")

    # 1. output file existence (10)
    if not os.path.isfile(output_path):
        result["details"].append({
            "item": "output file existence",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ops/add_vendor_tags.json not found"
        })
        result["total_score"] = 0
        _write_score(result, workspace)
        return
    else:
        result["details"].append({
            "item": "output file existence",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "File exists"
        })

    # 2. JSON parseable (10)
    try:
        with open(output_path, "r") as f:
            output_list = json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        result["details"].append({
            "item": "JSON parseable",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Failed to parse JSON: {str(e)}"
        })
        _write_score(result, workspace)
        return
    result["details"].append({
        "item": "JSON parseable",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "Valid JSON"
    })

    # 3. Output must be a list (10)
    if not isinstance(output_list, list):
        result["details"].append({
            "item": "output structure",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Expected a list, got " + type(output_list).__name__
        })
        _write_score(result, workspace)
        return
    # All elements must be strings
    for i, item in enumerate(output_list):
        if not isinstance(item, str):
            result["details"].append({
                "item": "output structure",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"Element at index {i} is not string, got {type(item).__name__}"
            })
            _write_score(result, workspace)
            return
    result["details"].append({
        "item": "output structure",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "Is a list of strings"
    })

    # 4. Determine expected contact_ids (70)
    # Load tag definitions to get vendor tag_id
    try:
        with open(tag_def_path, "r") as f:
            tag_data = json.load(f)
    except Exception as e:
        result["details"].append({
            "item": "determine expected set (tag_defs)",
            "score": 0,
            "max_score": 70,
            "passed": False,
            "reason": f"Cannot read tag_definitions.json: {str(e)}"
        })
        _write_score(result, workspace)
        return

    vendor_tag_id = None
    for tag in tag_data.get("tag_definitions", []):
        if tag.get("name") == "vendor":
            vendor_tag_id = tag.get("tag_id")
            break
    if not vendor_tag_id:
        result["details"].append({
            "item": "determine expected set (tag_defs)",
            "score": 0,
            "max_score": 70,
            "passed": False,
            "reason": "No tag with name 'vendor' found in tag_definitions"
        })
        _write_score(result, workspace)
        return

    # Load companies to get VendorCo company_id
    try:
        with open(companies_path, "r") as f:
            comp_data = json.load(f)
    except Exception as e:
        result["details"].append({
            "item": "determine expected set (companies)",
            "score": 0,
            "max_score": 70,
            "passed": False,
            "reason": f"Cannot read companies.json: {str(e)}"
        })
        _write_score(result, workspace)
        return

    vendor_company_id = None
    for comp in comp_data.get("companies", []):
        if comp.get("name") == "VendorCo Supplies":
            vendor_company_id = comp.get("company_id")
            break
    if not vendor_company_id:
        result["details"].append({
            "item": "determine expected set (companies)",
            "score": 0,
            "max_score": 70,
            "passed": False,
            "reason": "VendorCo Supplies not found in companies"
        })
        _write_score(result, workspace)
        return

    # Load contacts
    try:
        with open(contacts_path, "r") as f:
            contact_data = json.load(f)
    except Exception as e:
        result["details"].append({
            "item": "determine expected set (contacts)",
            "score": 0,
            "max_score": 70,
            "passed": False,
            "reason": f"Cannot read contacts.json: {str(e)}"
        })
        _write_score(result, workspace)
        return

    # Build expected set: contacts whose company_id == vendor_company_id AND who do NOT have vendor_tag_id in tags
    expected_ids = set()
    for c in contact_data.get("contacts", []):
        if c.get("company_id") == vendor_company_id:
            if vendor_tag_id not in c.get("tags", []):
                expected_ids.add(c["contact_id"])

    # Check for duplicate entries (shouldn't happen in clean data, but guard)
    # Ensure uniqueness of output list
    output_set = set(output_list)
    if len(output_set) != len(output_list):
        result["details"].append({
            "item": "correct contact set",
            "score": 0,
            "max_score": 70,
            "passed": False,
            "reason": f"Output list contains duplicates: {len(output_list)} items but {len(output_set)} unique"
        })
        _write_score(result, workspace)
        return

    # Compare
    missing = expected_ids - output_set
    extra = output_set - expected_ids
    penalty = 0
    max_penalty = 70
    reason_parts = []
    if missing:
        penalty += len(missing) * 15  # 15 points per missing contact
        reason_parts.append(f"Missing contacts: {sorted(missing)}")
    if extra:
        penalty += len(extra) * 15
        reason_parts.append(f"Extra contacts: {sorted(extra)}")

    score = max(0, 70 - penalty)
    passed = (penalty == 0)
    reason = "; ".join(reason_parts) if reason_parts else "Exactly matches expected set"
    result["details"].append({
        "item": "correct contact set",
        "score": score,
        "max_score": 70,
        "passed": passed,
        "reason": reason
    })

    # Total
    total = sum(d["score"] for d in result["details"])
    result["total_score"] = min(total, 100)

    # Write result
    _write_score(result, workspace)


def _write_score(result, workspace):
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(result, f, indent=2)


if __name__ == "__main__":
    ws = sys.argv[1] if len(sys.argv) > 1 else "."
    verify_workplace(ws)
