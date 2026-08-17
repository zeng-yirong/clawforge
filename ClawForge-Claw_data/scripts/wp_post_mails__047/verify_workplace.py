#!/usr/bin/env python3
import json, os, sys, re

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

results = []
def add(item, score, max_score, passed, reason):
    results.append({"item": item, "score": score, "max_score": max_score, "passed": passed, "reason": reason})

# ---------- 1. Directory structure (10 pts) ----------
dirs_ok = True
for d in ["data/emails", "data/social", "ops"]:
    if not os.path.isdir(os.path.join(workspace, d)):
        dirs_ok = False
        add("Directory structure", 0, 10, False, f"Missing directory: {d}")
        break
if dirs_ok:
    add("Directory structure", 10, 10, True, "All required directories present")

# ---------- 2. Output file exists and valid JSON (10 pts) ----------
output_path = os.path.join(workspace, "ops/launch_pack.json")
if not os.path.isfile(output_path):
    add("Output file exists", 0, 10, False, "ops/launch_pack.json not found")
    # still continue to collect partial scores for other checks? we can skip later checks that require file.
    # But to be safe, we still run checks and they will fail gracefully.
else:
    try:
        with open(output_path, "r") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError("top-level must be dict")
        add("Output file valid JSON", 10, 10, True, "File exists and valid JSON")
    except Exception as e:
        add("Output file valid JSON", 0, 10, False, f"Invalid JSON: {e}")
        data = None

# ---------- 3. Correct source brief used (10 pts) ----------
if data:
    # check that the agent used the latest brief (em_009)
    # We can infer from the posted product name and launch date
    x_post = data.get("x_post", "")
    reddit_post = data.get("reddit_post", "")
    # The correct brief says "Launch Date: 2025-03-20" and "Product: Orbital Launch"
    # The old brief says March 22 and "Orbital Launch (old draft)"
    # Also the body includes "Real-time satellite tracking" etc.
    # We'll check that the posts mention the correct date and features, not the old ones.
    score = 0
    reasons = []
    if "March 20" in x_post or "2025-03-20" in x_post:
        score += 5
        reasons.append("X post references correct launch date")
    else:
        reasons.append("X post missing correct launch date")
    if "Real-time" in x_post or "real-time" in x_post:
        score += 2
        reasons.append("X post mentions real-time tracking")
    else:
        reasons.append("X post missing real-time tracking feature")
    if "Modular" in x_post or "modular" in x_post:
        score += 3
        reasons.append("X post mentions modular payload")
    else:
        reasons.append("X post missing modular payload")
    if "March 20" in reddit_post or "2025-03-20" in reddit_post:
        score += 2
        reasons.append("Reddit post references correct launch date")
    else:
        reasons.append("Reddit post missing correct launch date")
    if "Real-time" in reddit_post or "real-time" in reddit_post:
        score += 2
        reasons.append("Reddit post mentions real-time tracking")
    else:
        reasons.append("Reddit post missing real-time tracking")
    if "Modular" in reddit_post or "modular" in reddit_post:
        score += 1
        reasons.append("Reddit post mentions modular payload")
    else:
        reasons.append("Reddit post missing modular payload")
    add("Correct source brief used", score, 15, score >= 10, "; ".join(reasons))
else:
    add("Correct source brief used", 0, 15, False, "No data to check")

# ---------- 4. X post length + compliance (15 pts) ----------
if data:
    x = data.get("x_post", "")
    score = 0
    reasons = []
    if len(x) <= 280:
        score += 5
        reasons.append("Within 280 characters")
    else:
        reasons.append(f"Length {len(x)} > 280")
    # must not contain 'revolutionary' or 'disruptive'
    ban_words = ["revolutionary", "disruptive"]
    if not any(w in x.lower() for w in ban_words):
        score += 5
        reasons.append("No banned words")
    else:
        reasons.append("Contains banned words")
    # must contain CTA or something close
    if "waitlist" in x.lower() or "orbital.auroralabs.com" in x:
        score += 5
        reasons.append("CTA present")
    else:
        reasons.append("CTA missing")
    add("X post compliance & length", score, 15, score >= 10, "; ".join(reasons))
else:
    add("X post compliance & length", 0, 15, False, "No data")

# ---------- 5. Reddit post structure (15 pts) ----------
if data:
    r = data.get("reddit_post", "")
    score = 0
    reasons = []
    if len(r) > 100:
        score += 5
        reasons.append("Sufficient length (>100 chars)")
    else:
        reasons.append("Too short")
    # must contain some hashtags or community mention
    if "#" in r or "r/" in r:
        score += 3
        reasons.append("Contains tags/community reference")
    else:
        reasons.append("Missing tags/community")
    # must not contain banned words
    if not any(w in r.lower() for w in ["revolutionary", "disruptive"]):
        score += 3
        reasons.append("No banned words")
    else:
        reasons.append("Contains banned words")
    # CTA
    if "waitlist" in r.lower() or "orbital.auroralabs.com" in r:
        score += 4
        reasons.append("CTA present")
    else:
        reasons.append("CTA missing")
    add("Reddit post structure", score, 15, score >= 10, "; ".join(reasons))
else:
    add("Reddit post structure", 0, 15, False, "No data")

# ---------- 6. Replies correctness (20 pts) ----------
if data:
    replies = data.get("replies", [])
    score = 0
    reasons = []
    if len(replies) == 2:
        score += 5
        reasons.append("Exactly 2 replies provided")
    else:
        reasons.append(f"Expected 2 replies, got {len(replies)}")
    # We expect replies to p001 (reddit) and p005 (reddit) or p002 (x) etc.
    # The agent could pick any two that have needs_response=True (p001, p002, p005)
    # We'll check ids and content.
    reply_ids = [r.get("post_id", "") for r in replies]
    valid_ids = ["p001", "p002", "p005"]
    # check that all provided ids are valid (needs_response)
    if all(rid in valid_ids for rid in reply_ids):
        score += 5
        reasons.append("All reply post_ids are valid (needs_response)")
    else:
        invalid = [rid for rid in reply_ids if rid not in valid_ids]
        reasons.append(f"Invalid post_ids: {invalid}")
    # Check that reply content mentions only approved facts (no competitor comparison, no banned words)
    ban = ["revolutionary", "disruptive", "Starship", "SpaceX"]
    ok = True
    for rep in replies:
        content = rep.get("reply_content", "")
        for w in ban:
            if w.lower() in content.lower():
                ok = False
                reasons.append(f"Banned word '{w}' in reply to {rep['post_id']}")
                break
    if ok:
        score += 5
        reasons.append("No banned words in replies")
    else:
        pass  # already added reasons
    # Check that replies contain some info from brief (e.g., launch date, features)
    brief_keywords = ["March 20", "real-time", "modular", "Orbital Launch"]
    keyword_hits = 0
    for rep in replies:
        content = rep.get("reply_content", "")
        for kw in brief_keywords:
            if kw.lower() in content.lower():
                keyword_hits += 1
    if keyword_hits >= 3:
        score += 5
        reasons.append("Replies contain at least 3 brief-derived keywords")
    else:
        reasons.append(f"Only {keyword_hits} brief keywords found")
    add("Replies correctness", score, 25, score >= 15, "; ".join(reasons))
else:
    add("Replies correctness", 0, 25, False, "No data")

# ---------- 7. General format – extra fields check (10 pts) ----------
if data:
    expected_keys = {"x_post", "reddit_post", "replies"}
    actual_keys = set(data.keys())
    extra = actual_keys - expected_keys
    if extra:
        add("No extra top-level fields", 0, 10, False, f"Extra fields: {extra}")
    else:
        add("No extra top-level fields", 10, 10, True, "Only expected fields present")
else:
    add("No extra top-level fields", 0, 10, False, "No data")

# ---------- Compute total ----------
total_score = sum(r["score"] for r in results)
max_total = sum(r["max_score"] for r in results)
# ensure integer
total_score = min(total_score, 100)  # cap to 100
output = {
    "total_score": total_score,
    "details": results
}
with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
    json.dump(output, f, indent=2)
