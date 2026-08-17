import sys
import os
import json
import re

WORKSPACE = sys.argv[1] if len(sys.argv) > 1 else "."

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def check_file_exists(filepath):
    return os.path.isfile(os.path.join(WORKSPACE, filepath))

def main():
    details = []
    total_score = 0
    max_total = 100

    # ----- 1. Social directory structure (5 pts) -----
    if not os.path.isdir(os.path.join(WORKSPACE, "social")):
        details.append({"item": "social directory exists", "score": 0, "max_score": 5, "passed": False, "reason": "social/ directory missing"})
    else:
        details.append({"item": "social directory exists", "score": 5, "max_score": 5, "passed": True, "reason": "social/ found"})

    # ----- 2. X launch post exists and valid JSON (10 pts) -----
    x_post_path = "social/x_launch.json"
    if not check_file_exists(x_post_path):
        details.append({"item": "X launch post file", "score": 0, "max_score": 10, "passed": False, "reason": "File not found"})
    else:
        try:
            x_post = load_json(os.path.join(WORKSPACE, x_post_path))
            if not isinstance(x_post, dict):
                raise ValueError("not a dict")
            details.append({"item": "X launch post file", "score": 10, "max_score": 10, "passed": True, "reason": "Valid JSON"})
        except Exception as e:
            details.append({"item": "X launch post file", "score": 0, "max_score": 10, "passed": False, "reason": f"Invalid JSON: {str(e)}"})

    # ----- 3. Reddit launch post exists and valid JSON (10 pts) -----
    reddit_post_path = "social/reddit_launch.json"
    if not check_file_exists(reddit_post_path):
        details.append({"item": "Reddit launch post file", "score": 0, "max_score": 10, "passed": False, "reason": "File not found"})
    else:
        try:
            reddit_post = load_json(os.path.join(WORKSPACE, reddit_post_path))
            if not isinstance(reddit_post, dict):
                raise ValueError("not a dict")
            details.append({"item": "Reddit launch post file", "score": 10, "max_score": 10, "passed": True, "reason": "Valid JSON"})
        except Exception as e:
            details.append({"item": "Reddit launch post file", "score": 0, "max_score": 10, "passed": False, "reason": f"Invalid JSON: {str(e)}"})

    # ----- 4. Content verification against approved brief (50 pts total) -----
    # Load the ground truth from the approved attachment
    brief_path = os.path.join(WORKSPACE, "attachments", "att_orion_brief_final.txt")
    if not os.path.isfile(brief_path):
        # fallback: embed ground truth
        truths = {
            "launch_date": "2025-09-20",
            "satellites": "12",
            "payloads": ["Communication", "Weather Imaging", "Earth Observation"],
            "partner": "European Space Agency (ESA)",
            "fact": "VISIR sensor"
        }
    else:
        with open(brief_path, 'r', encoding='utf-8') as f:
            content = f.read()
        # parse key facts
        truths = {}
        if m := re.search(r'Launch Date:\s*(\S+)', content):
            truths["launch_date"] = m.group(1)
        if m := re.search(r'Number of Satellites:\s*(\S+)', content):
            truths["satellites"] = m.group(1)
        if m := re.search(r'Primary Payload:\s*(.+)', content):
            truths["payloads"] = [p.strip() for p in m.group(1).split(',')]
        if m := re.search(r'Partner:\s*(.+)', content):
            truths["partner"] = m.group(1).strip()
        if m := re.search(r'Key Fact:\s*(.+)', content):
            truths["fact"] = m.group(1).strip()

    # Check X post
    x_score = 0
    x_max = 25
    x_reasons = []
    try:
        x_post = load_json(os.path.join(WORKSPACE, x_post_path))
        # Check that required fields exist
        has_required = all(k in x_post for k in ["platform", "content", "title"])
        if not has_required:
            x_reasons.append("Missing one of 'platform', 'content', 'title'")
        else:
            if x_post.get("platform", "").lower() != "x":
                x_reasons.append("platform should be 'x'")
            # Check content contains launch_date, satellite count, partner
            content_text = x_post.get("content", "")
            if truths.get("launch_date") and truths["launch_date"] not in content_text:
                x_reasons.append("launch date missing in content")
            if truths.get("satellites") and truths["satellites"] not in content_text:
                x_reasons.append("satellite count missing in content")
            if truths.get("partner") and truths["partner"] not in content_text:
                x_reasons.append("partner missing in content")
            if truths.get("fact") and truths["fact"] not in content_text:
                x_reasons.append("key fact missing in content")
        if not x_reasons:
            x_score = 25
            details.append({"item": "X post content accuracy", "score": 25, "max_score": 25, "passed": True, "reason": "All required facts present"})
        else:
            details.append({"item": "X post content accuracy", "score": 0, "max_score": 25, "passed": False, "reason": "; ".join(x_reasons)})
    except:
        details.append({"item": "X post content accuracy", "score": 0, "max_score": 25, "passed": False, "reason": "Could not read X post"})

    # Check Reddit post
    r_score = 0
    r_max = 25
    r_reasons = []
    try:
        reddit_post = load_json(os.path.join(WORKSPACE, reddit_post_path))
        has_required = all(k in reddit_post for k in ["platform", "content", "title", "community"])
        if not has_required:
            r_reasons.append("Missing one of 'platform', 'content', 'title', 'community'")
        else:
            if reddit_post.get("platform", "").lower() != "reddit":
                r_reasons.append("platform should be 'reddit'")
            if reddit_post.get("community", "") != "r/Aerospace":
                r_reasons.append("community must be r/Aerospace")
            content_text = reddit_post.get("content", "")
            if truths.get("launch_date") and truths["launch_date"] not in content_text:
                r_reasons.append("launch date missing in content")
            if truths.get("satellites") and truths["satellites"] not in content_text:
                r_reasons.append("satellite count missing in content")
            if truths.get("partner") and truths["partner"] not in content_text:
                r_reasons.append("partner missing in content")
            if truths.get("fact") and truths["fact"] not in content_text:
                r_reasons.append("key fact missing in content")
        if not r_reasons:
            r_score = 25
            details.append({"item": "Reddit post content accuracy", "score": 25, "max_score": 25, "passed": True, "reason": "All required facts present"})
        else:
            details.append({"item": "Reddit post content accuracy", "score": 0, "max_score": 25, "passed": False, "reason": "; ".join(r_reasons)})
    except:
        details.append({"item": "Reddit post content accuracy", "score": 0, "max_score": 25, "passed": False, "reason": "Could not read Reddit post"})

    # ----- 5. Reply to the question post (20 pts) -----
    reply_score = 0
    reply_max = 20
    reply_reason = ""
    try:
        original_post_path = os.path.join(WORKSPACE, "social/reddit_101.json")
        if not os.path.isfile(original_post_path):
            reply_reason = "Original post reddit_101.json not found"
        else:
            post = load_json(original_post_path)
            if "replies" not in post or not isinstance(post["replies"], list):
                reply_reason = "replies field missing or not a list"
            else:
                # Agent should have added a new reply (we expect at least 2 replies now, original had 1)
                if len(post["replies"]) < 2:
                    reply_reason = "No new reply added (expected at least 2 replies)"
                else:
                    # Find the reply that was added (the one with author of aurora official or Mira)
                    new_replies = [r for r in post["replies"] if r.get("author_id") in ("aurora_main", "c001")]
                    if not new_replies:
                        reply_reason = "New reply not from official account (aurora_main or c001)"
                    else:
                        # Check that reply content includes at least one fact from brief
                        reply = new_replies[-1]  # last one
                        content = reply.get("content", "")
                        checks = []
                        if truths.get("launch_date") and truths["launch_date"] not in content:
                            checks.append("launch date missing")
                        if truths.get("satellites") and truths["satellites"] not in content:
                            checks.append("satellites missing")
                        if truths.get("payloads"):
                            for p in truths["payloads"]:
                                if p.lower() in content.lower():
                                    break
                            else:
                                checks.append("payloads missing")
                        if not checks:
                            reply_score = 20
                            details.append({"item": "Reply to community question", "score": 20, "max_score": 20, "passed": True, "reason": "Correct reply added with facts"})
                        else:
                            reply_reason = "Content missing facts: " + "; ".join(checks)
    except Exception as e:
        reply_reason = f"Error processing reply: {str(e)}"

    if reply_score == 0:
        details.append({"item": "Reply to community question", "score": 0, "max_score": 20, "passed": False, "reason": reply_reason})

    # ----- 6. Ensure no extra files created? Not scored, but we can check for unwanted top-level mutations? Not required.-----

    # Calculate total
    total_score = sum(d["score"] for d in details)
    result = {
        "total_score": total_score,
        "details": details
    }
    out_path = os.path.join(WORKSPACE, "workplace_score.json")
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written to {out_path}: {total_score}/100")

if __name__ == "__main__":
    main()
