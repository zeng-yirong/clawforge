"""
Verify the agent's output for task wp_doc_clue_memory_env__012.
Checks that ops/clue_list.json exists, is valid JSON, and contains all and only
the documents whose solution_aliases include "HelioSync Edge Inference Fabric".
Also verifies that the "quote" field is a substring of the corresponding source document.
"""
import json, os, sys, math

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

details = []
total_score = 0

# ------------------------------------------------------------------------------
# 1. Check that ops/clue_list.json exists (10 points)
path = os.path.join(workspace, "ops", "clue_list.json")
if os.path.isfile(path):
    details.append({
        "item": "ops/clue_list.json exists",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "File found."
    })
    total_score += 10
else:
    details.append({
        "item": "ops/clue_list.json exists",
        "score": 0,
        "max_score": 10,
        "passed": False,
        "reason": "File not found."
    })
    # Can't proceed with further checks
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2)
    sys.exit(0)

# ------------------------------------------------------------------------------
# 2. Validate JSON format (10 points)
try:
    with open(path, "r") as f:
        clue_list = json.load(f)
    if not isinstance(clue_list, list):
        raise ValueError("Root is not a list")
    details.append({
        "item": "JSON validity and list type",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "Valid JSON array."
    })
    total_score += 10
except Exception as e:
    details.append({
        "item": "JSON validity and list type",
        "score": 0,
        "max_score": 10,
        "passed": False,
        "reason": f"Invalid JSON or not a list: {str(e)}"
    })
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2)
    sys.exit(0)

# ------------------------------------------------------------------------------
# 3. Check each entry has required fields (20 points)
required_fields = {"document_id", "title", "type", "quote"}
field_errors = []
for i, entry in enumerate(clue_list):
    missing = required_fields - set(entry.keys())
    if missing:
        field_errors.append(f"Entry {i} missing {', '.join(sorted(missing))}")
    extra = set(entry.keys()) - required_fields
    if extra:
        field_errors.append(f"Entry {i} has extra fields: {', '.join(sorted(extra))}")
if field_errors:
    details.append({
        "item": "Each entry has exactly the required fields",
        "score": 0,
        "max_score": 20,
        "passed": False,
        "reason": "; ".join(field_errors)
    })
else:
    details.append({
        "item": "Each entry has exactly the required fields",
        "score": 20,
        "max_score": 20,
        "passed": True,
        "reason": "All entries have valid fields."
    })
    total_score += 20

# ------------------------------------------------------------------------------
# 4. Build expected set of documents (from env_builder data) (60 points)
#    Only documents whose solution_aliases contains "HelioSync Edge Inference Fabric"
expected_docs = set()
source_content = {}  # doc_id -> content string (from report content / deck_notes / media content)

# --- Reports ---
reports_path = os.path.join(workspace, "data", "reports.json")
if os.path.isfile(reports_path):
    with open(reports_path, "r") as f:
        reports = json.load(f)
    for r in reports:
        aliases = r.get("solution_aliases", [])
        if "HelioSync Edge Inference Fabric" in aliases:
            expected_docs.add(r["report_id"])
            source_content[r["report_id"]] = {
                "text": r.get("content", ""),
                "type": "report",
                "title": r.get("title", "")
            }

# --- Presentations ---
pres_path = os.path.join(workspace, "data", "presentations.json")
if os.path.isfile(pres_path):
    with open(pres_path, "r") as f:
        presentations = json.load(f)
    for p in presentations:
        aliases = p.get("solution_aliases", [])
        if "HelioSync Edge Inference Fabric" in aliases:
            expected_docs.add(p["presentation_id"])
            source_content[p["presentation_id"]] = {
                "text": p.get("deck_notes", ""),
                "type": "presentation",
                "title": p.get("title", "")
            }

# --- Media Samples ---
media_path = os.path.join(workspace, "data", "media_samples.json")
if os.path.isfile(media_path):
    with open(media_path, "r") as f:
        media_samples = json.load(f)
    for m in media_samples:
        aliases = m.get("solution_aliases", [])
        if "HelioSync Edge Inference Fabric" in aliases:
            expected_docs.add(m["sample_id"])
            source_content[m["sample_id"]] = {
                "text": m.get("content", ""),
                "type": "media",
                "title": m.get("title", "")
            }

# Collect actual IDs from clue_list
actual_ids = set()
actual_map = {}
for entry in clue_list:
    doc_id = entry.get("document_id", None)
    if doc_id:
        actual_ids.add(doc_id)
        actual_map[doc_id] = entry

# Compare sets
missing = expected_docs - actual_ids
extra = actual_ids - expected_docs
error_msgs = []
if missing:
    error_msgs.append(f"Missing documents: {', '.join(sorted(missing))}")
if extra:
    error_msgs.append(f"Unexpected documents: {', '.join(sorted(extra))}")

# Score: each correct document (intersection) gets 20/len(expected_docs) points
correct_count = len(expected_docs & actual_ids)
if expected_docs:
    per_doc_score = 60 / len(expected_docs)  # e.g., 20 each for 3 docs
else:
    per_doc_score = 0

score_docs = math.floor(correct_count * per_doc_score)  # floor to int
# But we want integer total within 60 cap
score_docs = min(score_docs, 60)

if not error_msgs:
    # all present and none extra
    score_docs = 60
    details.append({
        "item": "Correct document selection (all expected, no extras)",
        "score": 60,
        "max_score": 60,
        "passed": True,
        "reason": f"Exactly the {len(expected_docs)} expected documents."
    })
    total_score += 60
else:
    # partial credit
    # Also deduct for extras: -10 per extra doc, but min score 0
    extra_penalty = len(extra) * 10
    final_score = max(0, score_docs - extra_penalty)
    details.append({
        "item": "Correct document selection (all expected, no extras)",
        "score": final_score,
        "max_score": 60,
        "passed": False,
        "reason": "; ".join(error_msgs) + f" (partial document match gives {score_docs}, penalty {extra_penalty})"
    })
    total_score += final_score

# ------------------------------------------------------------------------------
# 5. Verify each quote is a substring of the corresponding source document (10 points)
quote_ok = True
quote_errors = []
for entry in clue_list:
    doc_id = entry.get("document_id", "")
    quote = entry.get("quote", "")
    src = source_content.get(doc_id)
    if src is None:
        quote_errors.append(f"Entry for {doc_id}: unknown document ID")
        quote_ok = False
        continue
    if quote not in src["text"]:
        quote_errors.append(f"Entry for {doc_id}: quote not found in source text")
        quote_ok = False
    # Also check type matches
    if entry.get("type") != src["type"]:
        quote_errors.append(f"Entry for {doc_id}: type mismatch (expected {src['type']})")
        quote_ok = False
    if entry.get("title") != src["title"]:
        quote_errors.append(f"Entry for {doc_id}: title mismatch (expected '{src['title']}')")
        quote_ok = False

if quote_ok:
    details.append({
        "item": "Each quote is present in source, type and title match",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "All quotes validated against source documents."
    })
    total_score += 10
else:
    details.append({
        "item": "Each quote is present in source, type and title match",
        "score": 0,
        "max_score": 10,
        "passed": False,
        "reason": "; ".join(quote_errors[:5])  # show first 5 errors
    })

# ------------------------------------------------------------------------------
# Write final score
with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
    json.dump({"total_score": total_score, "details": details}, f, indent=2)
