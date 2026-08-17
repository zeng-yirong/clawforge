import json
import os
import sys

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

score_details = []
total_score = 0

def check(condition, item, max_score, reason_pass, reason_fail):
    global total_score
    passed = bool(condition)
    score = max_score if passed else 0
    total_score += score
    score_details.append({
        "item": item,
        "score": score,
        "max_score": max_score,
        "passed": passed,
        "reason": reason_pass if passed else reason_fail
    })

# ---------- 1. ops/ directory exists ----------
ops_path = os.path.join(workspace, "ops")
check(os.path.isdir(ops_path),
      "ops/ directory exists", 5,
      "ops/ directory found",
      "ops/ directory missing")

# ---------- 2. clue_manifest.json exists ----------
manifest_path = os.path.join(workspace, "ops", "clue_manifest.json")
check(os.path.isfile(manifest_path),
      "ops/clue_manifest.json exists", 10,
      "File exists",
      "File not found")

if not os.path.isfile(manifest_path):
    # early exit if file missing – rest will fail
    score_details.append({
        "item": "total_score",
        "score": total_score,
        "max_score": 100,
        "passed": False,
        "reason": "Missing clue_manifest.json"
    })
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
    sys.exit(0)

# ---------- 3. File is valid JSON ----------
try:
    with open(manifest_path, "r") as f:
        data = json.load(f)
    check(True, "Valid JSON", 5, "File parsable as JSON", "File corrupt or not JSON")
except Exception as e:
    check(False, "Valid JSON", 5, "", f"JSON parse error: {e}")
    data = {}

# ---------- 4. Contains key 'clue_list' (or maybe top-level list?) ----------
# We allow either a dict with "clue_list" or a plain list.
if isinstance(data, list):
    clue_list = data
elif isinstance(data, dict) and "clue_list" in data:
    clue_list = data["clue_list"]
else:
    clue_list = None
    check(False, "clue_list key or top-level array", 10,
          "", "Expected 'clue_list' key (array) or top-level array")

if clue_list is None:
    # finalize early
    score_details.append({
        "item": "total_score",
        "score": total_score,
        "max_score": 100,
        "passed": False,
        "reason": "Could not extract clue list"
    })
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
    sys.exit(0)

check(True, "clue_list key or top-level array", 10, "Found clue list", "")

# ---------- 5. Check each element has required fields ----------
required_fields = ["doc_id", "doc_type", "summary"]
all_have_fields = all(
    isinstance(item, dict) and all(f in item for f in required_fields)
    for item in clue_list
)
check(all_have_fields, "All entries have doc_id, doc_type, summary", 10,
      "Every entry contains required fields",
      "One or more entries missing required fields")

# ---------- 6. Correct number of matches (4) ----------
expected_ids = {
    "RPT-001", "RPT-004",     # reports
    "PRES-101",               # presentation
    "MED-201"                 # media sample (MED-203 also matches? Actually MED-203 solution_aliases contains "HelioSync Edge Inference Fabric" as well.
    # Wait, MED-203 has ["HelioSync Edge Inference Fabric", "HelioSync"] so it matches too! That gives 5? Let's check env_builder: MED-203 alias includes exactly "HelioSync Edge Inference Fabric". Yes it does.
    # So expected matches: RPT-001, RPT-004, PRES-101, MED-201, MED-203 => 5 matches.
    # But we also have MED-203. Let's verify env_builder: I wrote samples: MED-201, MED-202, MED-203. MED-203 has solution_aliases: ["HelioSync Edge Inference Fabric", "HelioSync"]. So it matches. So total = 5.
    # Correct set = {"RPT-001","RPT-004","PRES-101","MED-201","MED-203"}.
    # Need to adjust expected in comment.
}
# Let's recomputed: 
# reports: RPT-001 (yes), RPT-002 (Lite - no), RPT-003 (Edge Inference Fabric - no full phrase), RPT-004 (yes). => 2
# presentations: PRES-101 (yes), PRES-102 (no), PRES-103 (no) =>1
# media_samples: MED-201 (yes), MED-202 (no), MED-203 (yes) =>2
# Total 5.
expected_ids = {"RPT-001", "RPT-004", "PRES-101", "MED-201", "MED-203"}
actual_ids = set()
for entry in clue_list:
    if isinstance(entry, dict) and "doc_id" in entry:
        actual_ids.add(entry["doc_id"])

check(actual_ids == expected_ids,
      "Correct doc_id set (5 matches: RPT-001, RPT-004, PRES-101, MED-201, MED-203)", 40,
      f"All expected IDs present: {sorted(expected_ids)}",
      f"Expected {sorted(expected_ids)}, got {sorted(actual_ids)}")

# ---------- 7. No extra entries ----------
check(len(clue_list) == len(expected_ids),
      "No extra entries beyond expected", 10,
      f"Exactly {len(expected_ids)} entries",
      f"Expected {len(expected_ids)} entries, got {len(clue_list)}")

# ---------- 8. Summary fields non-empty (basic sanity) ----------
summaries_nonempty = all(
    isinstance(entry, dict) and entry.get("summary", "").strip()
    for entry in clue_list
)
check(summaries_nonempty, "All summaries non-empty", 10,
      "Every entry has a non-empty summary",
      "One or more entries have empty or missing summary")

# ---------- Write score file ----------
final_score = min(total_score, 100)
with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
    json.dump({"total_score": final_score, "details": score_details}, f, indent=2)
