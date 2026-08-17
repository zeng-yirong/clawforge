import json
import os
import sys

def verify(workspace: str) -> dict:
    """Score the agent's output against the expected truth."""
    details = []
    total_score = 0
    max_total = 100

    # Expected correct answers (sorted by (type, id) for easy comparison)
    expected = {
        ("report", "RPT-2026-001"): "Automated routing optimization for supply chains",
        ("presentation", "PRES-2026-001"): "Real-time fleet optimization for deliveries",
        ("media_sample", "MEDIA-2026-001"): "Edge deployment for manufacturing IoT",
    }

    # 1) Check temp_records directory exists
    dir_path = os.path.join(workspace, "temp_records")
    dir_exists = os.path.isdir(dir_path)
    details.append({
        "item": "temp_records directory exists",
        "score": 5 if dir_exists else 0,
        "max_score": 5,
        "passed": dir_exists,
        "reason": "Directory found" if dir_exists else "Missing directory"
    })
    if dir_exists:
        total_score += 5

    # 2) Check clue_list.json exists
    file_path = os.path.join(dir_path, "clue_list.json") if dir_exists else ""
    file_exists = os.path.isfile(file_path) if dir_exists else False
    details.append({
        "item": "clue_list.json exists",
        "score": 10 if file_exists else 0,
        "max_score": 10,
        "passed": file_exists,
        "reason": "File found" if file_exists else "File missing"
    })
    if file_exists:
        total_score += 10

    # 3) Parse JSON
    parsed = None
    json_valid = False
    if file_exists:
        try:
            with open(file_path, "r") as f:
                parsed = json.load(f)
            json_valid = isinstance(parsed, list)
            if not json_valid:
                details.append({
                    "item": "JSON is a list",
                    "score": 0,
                    "max_score": 10,
                    "passed": False,
                    "reason": "Root element is not a list"
                })
            else:
                details.append({
                    "item": "JSON is a list",
                    "score": 10,
                    "max_score": 10,
                    "passed": True,
                    "reason": "Valid list"
                })
                total_score += 10
        except (json.JSONDecodeError, Exception) as e:
            details.append({
                "item": "JSON is parseable",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"Parse error: {e}"
            })
    else:
        details.append({
            "item": "JSON is a list",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not present"
        })

    # 4) Check list length
    if json_valid and isinstance(parsed, list):
        length = len(parsed)
        length_ok = length == 3
        details.append({
            "item": "List length equals 3",
            "score": 15 if length_ok else 0,
            "max_score": 15,
            "passed": length_ok,
            "reason": f"Length = {length}" if length_ok else f"Expected 3, got {length}"
        })
        if length_ok:
            total_score += 15
        else:
            # If length wrong, skip finer checks
            pass
    else:
        details.append({
            "item": "List length equals 3",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": "Could not validate length (JSON not a list)"
        })

    # 5) Field presence and values (only if length=3 and all required fields exist)
    field_score = 0
    field_max = 45  # 3 entries * 3 fields * 5 each = 45
    if json_valid and isinstance(parsed, list) and len(parsed) == 3:
        # Build actual dictionary from the agent's list
        actual = {}
        all_fields_ok = True
        for i, entry in enumerate(parsed):
            if not isinstance(entry, dict):
                all_fields_ok = False
                continue
            s_type = entry.get("source_type")
            s_id = entry.get("source_id")
            clue = entry.get("clue")
            if None in (s_type, s_id, clue):
                all_fields_ok = False
                continue
            key = (s_type, s_id)
            if key in actual:
                all_fields_ok = False  # duplicate key
                continue
            actual[key] = clue

        if not all_fields_ok or len(actual) != 3:
            details.append({
                "item": "All 3 entries have required fields (source_type, source_id, clue) with no duplicates",
                "score": 0,
                "max_score": 15,
                "passed": False,
                "reason": "Missing fields or duplicates found"
            })
        else:
            details.append({
                "item": "All 3 entries have required fields (source_type, source_id, clue) with no duplicates",
                "score": 15,
                "max_score": 15,
                "passed": True,
                "reason": "Fields present and no duplicates"
            })
            total_score += 15

            # Compare with expected
            match_count = 0
            for key, expected_clue in expected.items():
                if key in actual and actual[key] == expected_clue:
                    match_count += 1
            if match_count == 3:
                item_name = "source_type and source_id match expected keys"
                details.append({
                    "item": item_name,
                    "score": 15,
                    "max_score": 15,
                    "passed": True,
                    "reason": "All keys correct"
                })
                total_score += 15
                item_name = "clue values match exactly"
                details.append({
                    "item": item_name,
                    "score": 15,
                    "max_score": 15,
                    "passed": True,
                    "reason": "All clues correct"
                })
                total_score += 15
            elif match_count > 0:
                # partial match
                details.append({
                    "item": "source_type/source_id match expected keys",
                    "score": 5,
                    "max_score": 15,
                    "passed": False,
                    "reason": f"Only {match_count} of 3 keys matched"
                })
                total_score += 5
                # check clues for those matched keys
                clue_score = 0
                for key in set(expected.keys()) & set(actual.keys()):
                    if expected[key] == actual[key]:
                        clue_score += 5
                details.append({
                    "item": "clue values match exactly",
                    "score": clue_score,
                    "max_score": 15,
                    "passed": clue_score == 15,
                    "reason": f"Clues correct for {clue_score//5} of 3 entries"
                })
                total_score += clue_score
            else:
                details.append({
                    "item": "source_type/source_id match expected keys",
                    "score": 0,
                    "max_score": 15,
                    "passed": False,
                    "reason": "No keys matched the expected ones"
                })
                details.append({
                    "item": "clue values match exactly",
                    "score": 0,
                    "max_score": 15,
                    "passed": False,
                    "reason": "No clues could be checked (keys mismatched)"
                })
    else:
        # If length wrong or JSON invalid, skip field checks
        pass

    # Ensure we have all details items (even if some wasn't appended)
    # The missing ones will be appended now with 0 score
    expected_items = [
        "temp_records directory exists",
        "clue_list.json exists",
        "JSON is a list",
        "List length equals 3",
        "All 3 entries have required fields (source_type, source_id, clue) with no duplicates",
        "source_type/source_id match expected keys",
        "clue values match exactly"
    ]
    item_titles = [d["item"] for d in details]
    for item in expected_items:
        if item not in item_titles:
            details.append({
                "item": item,
                "score": 0,
                "max_score": (5 if item == "temp_records directory exists" else
                              10 if item in ["clue_list.json exists", "JSON is a list"] else
                              15 if item == "List length equals 3" else
                              15 if item == "All 3 entries have required fields (source_type, source_id, clue) with no duplicates" else
                              15),
                "passed": False,
                "reason": "Not evaluated due to earlier failures"
            })

    total_score = min(total_score, max_total)
    result = {
        "total_score": total_score,
        "details": details
    }
    return result

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    output_path = os.path.join(workspace, "workplace_score.json")
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written to {output_path}")

if __name__ == "__main__":
    main()
