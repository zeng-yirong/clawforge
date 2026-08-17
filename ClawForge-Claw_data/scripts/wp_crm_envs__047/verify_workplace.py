import os
import sys
import json

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

score_details = []
total_score = 0

def add_item(name, score, max_score, passed, reason):
    score_details.append({
        "item": name,
        "score": score,
        "max_score": max_score,
        "passed": passed,
        "reason": reason
    })
    return score

# 1. Check that ops/summary.json exists
summary_path = os.path.join(workspace, "ops", "summary.json")
if not os.path.isfile(summary_path):
    total_score += add_item("ops/summary.json exists", 0, 10, False, "File not found")
    # No point continuing if file missing
    final_score = {"total_score": total_score, "details": score_details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(final_score, f, indent=2)
    sys.exit(0)
else:
    total_score += add_item("ops/summary.json exists", 10, 10, True, "File present")

# 2. Check JSON is valid and is a list
try:
    with open(summary_path, "r") as f:
        content = json.load(f)
    if not isinstance(content, list):
        total_score += add_item("JSON is a list", 0, 10, False, "Root not a list")
        # Still continue for partial scoring
    else:
        total_score += add_item("JSON is a list", 10, 10, True, "Valid list")
except (json.JSONDecodeError, Exception) as e:
    total_score += add_item("JSON syntax", 0, 10, False, f"Invalid JSON: {e}")
    # cannot parse further
    final_score = {"total_score": total_score, "details": score_details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(final_score, f, indent=2)
    sys.exit(0)

if not isinstance(content, list):
    # still try to extract if possible? but we treat as failure
    total_score += add_item("List length = 3", 0, 10, False, "Root not a list, cannot check length")
    total_score += add_item("Entry fields valid", 0, 10, False, "Cannot check fields")
    total_score += add_item("Core mapping correct", 0, 30, False, "Cannot check mapping")
    total_score += add_item("No extra entries", 0, 10, False, "Cannot check extras")
    # write and exit
    final_score = {"total_score": total_score, "details": score_details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(final_score, f, indent=2)
    sys.exit(0)

# 3. Check list length (should be exactly 3)
expected_contacts = {"ct_001", "ct_003", "ct_005"}
if len(content) == 3:
    total_score += add_item("List length = 3", 10, 10, True, "Exactly 3 entries")
else:
    total_score += add_item("List length = 3", 0, 10, False, f"Expected 3, got {len(content)}")

# 4. Check that every entry has contact_id and action
all_have_fields = True
for entry in content:
    if not isinstance(entry, dict):
        all_have_fields = False
        break
    if "contact_id" not in entry or "action" not in entry:
        all_have_fields = False
        break
if all_have_fields:
    total_score += add_item("Each entry has contact_id & action", 10, 10, True, "All entries have required fields")
else:
    total_score += add_item("Each entry has contact_id & action", 0, 10, False, "Missing fields in some entries")

# 5. Core mapping: for each expected contact, check action
# Also ensure no unexpected contact_ids
expected_actions = {
    "ct_001": "skipped",
    "ct_003": "enable",
    "ct_005": "create"
}
entry_map = {}
for e in content:
    cid = e.get("contact_id")
    act = e.get("action")
    if cid:
        entry_map[cid] = act

# Check no extra contact_ids
extra_ids = set(entry_map.keys()) - expected_contacts
if extra_ids:
    total_score += add_item("No extra contacts in output", 0, 10, False, f"Unexpected contact_ids: {extra_ids}")
else:
    total_score += add_item("No extra contacts in output", 10, 10, True, "Only March birthday contacts present")

# Check mapping
mapping_correct = True
for cid, expected_act in expected_actions.items():
    if cid not in entry_map:
        mapping_correct = False
        break
    if entry_map[cid] != expected_act:
        mapping_correct = False
        break
if mapping_correct:
    total_score += add_item("Correct actions for each March birthday contact", 30, 30, True, "All actions match expected")
else:
    total_score += add_item("Correct actions for each March birthday contact", 0, 30, False, "Mismatch in actions")

# Ensure missing contact_ids are treated as missing
missing = expected_contacts - set(entry_map.keys())
if missing:
    total_score += add_item("All March birthdays present", 0, 10, False, f"Missing contacts: {missing}")
else:
    total_score += add_item("All March birthdays present", 10, 10, True, "All three March contacts present")

# Note: total score should now sum to 100 if all perfect. We have items allocated:
# exists 10, list 10, length 10, fields 10, no extra 10, mapping 30, all present 10 -> 10+10+10+10+10+30+10 = 90? Wait we have 7 items totaling 90. Let's adjust: we omitted a "JSON is list" separate? Actually we have "JSON is list" under item 2 (10). That makes 10+10+10+10+10+30+10+10? Let's recount:
# 1 exists 10
# 2 JSON is list 10
# 3 length 10
# 4 fields 10
# 5 no extra 10
# 6 mapping 30
# 7 all present 10
# That's 10+10+10+10+10+30+10 = 90. We need 100. So we need another 10 points. We can give 10 for "all actions valid strings" (skipped/enable/create) as a separate check, or incorporate it. Let's add an item "action values are valid" worth 10.
# We'll add after fields check.
# Actually we already have mapping check which validates actions, but we can split. Let's make a dedicated item for action value validity (skipped/enable/create). That adds 10 => 100.

# We'll insert after fields check:
valid_actions = {"skipped", "enable", "create"}
actions_valid = True
for e in content:
    act = e.get("action")
    if act not in valid_actions:
        actions_valid = False
        break
if actions_valid:
    total_score += add_item("All action values are valid (skipped/enable/create)", 10, 10, True, "Actions are valid")
else:
    total_score += add_item("All action values are valid (skipped/enable/create)", 0, 10, False, "Invalid action value found")

# Now total max = 10+10+10+10+10+10+30+10 = 100

# Finalize
final_score = {"total_score": total_score, "details": score_details}
with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
    json.dump(final_score, f, indent=2)
print(f"Verification complete. Total score: {total_score}/100")
