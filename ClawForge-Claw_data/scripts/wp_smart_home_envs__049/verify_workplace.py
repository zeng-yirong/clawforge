"""
Verifier for wp_smart_home_envs__049: check conflict resolution file.
"""
import os
import sys
import json

workspace = sys.argv[1] if len(sys.argv) > 1 else "."
score_details = []
total_score = 0

# ---------- helper ----------
def add_item(name, score, max_score, passed, reason):
    score_details.append({
        "item": name,
        "score": score,
        "max_score": max_score,
        "passed": passed,
        "reason": reason
    })
    return score

# ---------- check file existence ----------
conflict_path = os.path.join(workspace, "ops/conflict_resolution.txt")
if not os.path.isfile(conflict_path):
    total_score += add_item("File exists: ops/conflict_resolution.txt", 0, 10, False,
                            "Missing: ops/conflict_resolution.txt")
else:
    total_score += add_item("File exists: ops/conflict_resolution.txt", 10, 10, True, "File found")

# ---------- parse file content ----------
expected_entries = {
    "Bedroom AC": 24,
    "Bedroom Humidifier": 55
}
found_entries = {}
errors = []

if os.path.isfile(conflict_path):
    with open(conflict_path, "r") as f:
        lines = f.read().strip().splitlines()

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if ":" not in line:
            errors.append(f"Invalid format (missing colon): {line}")
            continue
        parts = line.split(":", 1)
        name = parts[0].strip()
        try:
            value = int(parts[1].strip())
        except ValueError:
            errors.append(f"Non-integer value: {line}")
            continue
        # check duplication
        if name in found_entries:
            errors.append(f"Duplicate entry: {name}")
        else:
            found_entries[name] = value

    # check number of lines
    num_required = len(expected_entries)
    if len(errors) == 0 and len(found_entries) != num_required:
        errors.append(f"Expected {num_required} conflict devices, found {len(found_entries)}: {list(found_entries.keys())}")

    # check each expected entry
    all_correct = True
    for name, expected_val in expected_entries.items():
        if name not in found_entries:
            errors.append(f"Missing device: {name}")
            all_correct = False
        elif found_entries[name] != expected_val:
            errors.append(f"{name} has value {found_entries[name]}, expected {expected_val}")
            all_correct = False

    # check for extra entries (should not include non-conflict devices)
    allowed_names = set(expected_entries.keys())
    extra = {k for k in found_entries if k not in allowed_names}
    if extra:
        errors.append(f"Unexpected devices reported: {extra}")
        all_correct = False

    if errors:
        reason = "; ".join(errors[:3])
        total_score += add_item("Parsed content correctness", 0, 90, False, reason)
    else:
        total_score += add_item("Parsed content correctness", 90, 90, True,
                                "All expected devices found with correct values, no extras")
else:
    total_score += add_item("Parsed content correctness", 0, 90, False, "File not available for parsing")

# ensure total_score is integer between 0 and 100
total_score = min(max(total_score, 0), 100)

result = {
    "total_score": total_score,
    "details": score_details
}

result_path = os.path.join(workspace, "workplace_score.json")
with open(result_path, "w") as f:
    json.dump(result, f, indent=2)
