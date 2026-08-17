import sys
import os
import json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0

    data_dir = os.path.join(workspace, "data", "onboarding")
    output_dir = os.path.join(workspace, "output")

    if not os.path.isdir(data_dir):
        score_details.append({"item": "Initial data directory exists", "score": 0, "max_score": 5, "passed": False, "reason": "Missing data/onboarding directory"})
    else:
        score_details.append({"item": "Initial data directory exists", "score": 5, "max_score": 5, "passed": True, "reason": "Found data/onboarding"})

    if not os.path.isdir(output_dir):
        score_details.append({"item": "Output directory exists", "score": 0, "max_score": 5, "passed": False, "reason": "Missing output directory"})
    else:
        score_details.append({"item": "Output directory exists", "score": 5, "max_score": 5, "passed": True, "reason": "Found output"})

    output_file = os.path.join(output_dir, "onboarding_summary.json")
    if not os.path.isfile(output_file):
        score_details.append({"item": "Output file exists", "score": 0, "max_score": 10, "passed": False, "reason": "Missing output/onboarding_summary.json"})
        total_score = sum(d["score"] for d in score_details)
        write_score(total_score, score_details)
        return

    try:
        with open(output_file, "r") as f:
            result = json.load(f)
        score_details.append({"item": "Output file is valid JSON", "score": 10, "max_score": 10, "passed": True, "reason": "JSON parse OK"})
    except (json.JSONDecodeError, Exception) as e:
        score_details.append({"item": "Output file is valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"Invalid JSON: {str(e)}"})
        total_score = sum(d["score"] for d in score_details)
        write_score(total_score, score_details)
        return

    contracts_path = os.path.join(data_dir, "contracts.json")
    equipment_path = os.path.join(data_dir, "equipment_inventory.json")
    packs_path = os.path.join(data_dir, "permission_packs.json")

    with open(contracts_path) as f:
        contracts_data = json.load(f)
    with open(equipment_path) as f:
        equipment_data = json.load(f)
    with open(packs_path) as f:
        packs_data = json.load(f)

    contracts = contracts_data.get("contracts", [])
    equipment_list = equipment_data.get("equipment_inventory", [])
    packs = packs_data.get("permission_packs", [])

    signed_contracts = [c for c in contracts if c.get("status") == "signed" and c.get("employee_name") == "张三"]
    expected_contract = signed_contracts[0] if len(signed_contracts) == 1 else None

    available_laptops = [e for e in equipment_list if e.get("asset_type") == "laptop" and e.get("status") == "available"]
    expected_equipment = available_laptops[0] if len(available_laptops) == 1 else None

    if expected_contract:
        dept = expected_contract.get("department")
        matched_packs = [p for p in packs if p.get("department") == dept]
        expected_pack = matched_packs[0] if len(matched_packs) == 1 else None
    else:
        expected_pack = None

    if expected_contract and expected_equipment and expected_pack:
        expected = {
            "employee_id": expected_contract["employee_id"],
            "employee_name": expected_contract["employee_name"],
            "email": expected_contract["email"],
            "equipment": {
                "asset_tag": expected_equipment["asset_tag"],
                "asset_type": expected_equipment["asset_type"]
            },
            "permissions": {
                "pack_id": expected_pack["pack_id"],
                "systems": expected_pack["systems"]
            }
        }
    else:
        expected = None

    if expected is None:
        score_details.append({"item": "Consistency", "score": 0, "max_score": 80, "passed": False, "reason": "Initial data not consistent - cannot determine expected result"})
        total_score = sum(d["score"] for d in score_details)
        write_score(total_score, score_details)
        return

    expected_keys = set(expected.keys())
    actual_keys = set(result.keys())
    if expected_keys != actual_keys:
        score_details.append({"item": "Top-level keys match", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected keys {expected_keys}, got {actual_keys}"})
    else:
        score_details.append({"item": "Top-level keys match", "score": 10, "max_score": 10, "passed": True, "reason": "Keys match"})

    items_check = [
        ("employee_id", "employee_id", 10),
        ("employee_name", "employee_name", 10),
        ("email", "email", 10),
        ("equipment", "equipment", 20),
        ("permissions", "permissions", 20)
    ]
    for display, key, max_s in items_check:
        if result.get(key) == expected.get(key):
            score_details.append({"item": f"Field '{key}' correct", "score": max_s, "max_score": max_s, "passed": True, "reason": "Value matches expected"})
        else:
            score_details.append({"item": f"Field '{key}' correct", "score": 0, "max_score": max_s, "passed": False, "reason": f"Expected {expected.get(key)}, got {result.get(key)}"})

    total_score = sum(d["score"] for d in score_details)
    write_score(total_score, score_details)

def write_score(total, details):
    output = {
        "total_score": total,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(output, f, indent=2)

if __name__ == "__main__":
    main()
