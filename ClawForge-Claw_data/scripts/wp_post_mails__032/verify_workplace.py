import os
import sys
import json
import glob

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    os.chdir(workspace)

    score_details = []
    total_score = 0
    max_total = 100

    # ------------------------------------------------------------------
    # 1. Check that ops/ directory exists (10 points)
    # ------------------------------------------------------------------
    item_name = "ops directory exists"
    if os.path.isdir("ops"):
        score_details.append({
            "item": item_name,
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Directory ops/ found."
        })
        total_score += 10
    else:
        score_details.append({
            "item": item_name,
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Directory ops/ not found."
        })

    # ------------------------------------------------------------------
    # 2. Check ops/launch_details.json (10 points)
    # ------------------------------------------------------------------
    ld_path = "ops/launch_details.json"
    if os.path.isfile(ld_path):
        try:
            ld = load_json(ld_path)
            score_details.append({
                "item": "launch_details.json exists and is valid JSON",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": f"File exists and parses correctly."
            })
            total_score += 10
        except (json.JSONDecodeError, Exception) as e:
            score_details.append({
                "item": "launch_details.json exists and is valid JSON",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"File exists but is not valid JSON: {e}"
            })
    else:
        score_details.append({
            "item": "launch_details.json exists and is valid JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not found."
        })

    # ------------------------------------------------------------------
    # 3. Check ops/pending_posts.json (10 points)
    # ------------------------------------------------------------------
    pp_path = "ops/pending_posts.json"
    if os.path.isfile(pp_path):
        try:
            pp = load_json(pp_path)
            score_details.append({
                "item": "pending_posts.json exists and is valid JSON",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": f"File exists and parses correctly."
            })
            total_score += 10
        except (json.JSONDecodeError, Exception) as e:
            score_details.append({
                "item": "pending_posts.json exists and is valid JSON",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"File exists but is not valid JSON: {e}"
            })
    else:
        score_details.append({
            "item": "pending_posts.json exists and is valid JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not found."
        })

    # ------------------------------------------------------------------
    # 4. Verify launch_details content (35 points)
    # ------------------------------------------------------------------
    # Expected values derived from the environment:
    # - Find email in data/emails/ with labels containing "approved", importance "high",
    #   and max timestamp
    # - Get its attachment id, find that attachment in data/attachments/
    # - Expected product_name and launch_date from attachment content
    try:
        email_files = glob.glob("data/emails/*.json")
        approved_email = None
        max_ts = None
        for ef in email_files:
            try:
                em = load_json(ef)
            except:
                continue
            if not isinstance(em.get("labels"), list):
                continue
            if "approved" in em.get("labels", []) and em.get("importance") == "high":
                ts = em.get("timestamp", "")
                if max_ts is None or ts > max_ts:
                    max_ts = ts
                    approved_email = em
        if approved_email is None:
            raise ValueError("No approved+high email found in environment. (Corrupted?)")
        att_id = approved_email.get("attachments", [{}])[0].get("id", "")
        att_path = f"data/attachments/{att_id}.json"
        if not os.path.isfile(att_path):
            raise ValueError(f"Attachment file {att_path} not found.")
        att = load_json(att_path)
        content = att.get("content", {})
        expected_product = content.get("product_name")
        expected_date = content.get("launch_date")
    except Exception as e:
        # If environment is broken, we cannot judge; assume 0
        expected_product = None
        expected_date = None

    if expected_product and expected_date:
        # Check agent output
        if os.path.isfile(ld_path):
            try:
                ld = load_json(ld_path)
            except:
                ld = {}
            ld_product = ld.get("product_name")
            ld_date = ld.get("launch_date")
            product_ok = (ld_product == expected_product)
            date_ok = (ld_date == expected_date)
            if product_ok and date_ok:
                score_details.append({
                    "item": "launch_details content (product_name and launch_date)",
                    "score": 35,
                    "max_score": 35,
                    "passed": True,
                    "reason": f"product_name='{ld_product}' and launch_date='{ld_date}' match expected."
                })
                total_score += 35
            else:
                reason = ""
                if not product_ok:
                    reason += f"product_name expected '{expected_product}', got '{ld_product}'. "
                if not date_ok:
                    reason += f"launch_date expected '{expected_date}', got '{ld_date}'. "
                score_details.append({
                    "item": "launch_details content (product_name and launch_date)",
                    "score": 0,
                    "max_score": 35,
                    "passed": False,
                    "reason": reason.strip()
                })
        else:
            score_details.append({
                "item": "launch_details content (product_name and launch_date)",
                "score": 0,
                "max_score": 35,
                "passed": False,
                "reason": "launch_details.json not found, cannot verify content."
            })
    else:
        score_details.append({
            "item": "launch_details content (product_name and launch_date)",
            "score": 0,
            "max_score": 35,
            "passed": False,
            "reason": "Could not compute expected values from environment (possibly broken)."
        })

    # ------------------------------------------------------------------
    # 5. Verify pending_posts content (30 points)
    # ------------------------------------------------------------------
    # Expected: all social posts with needs_response == True, sorted by post_id
    try:
        post_files = glob.glob("data/social/*.json")
        expected_posts = []
        for pf in post_files:
            try:
                p = load_json(pf)
            except:
                continue
            if p.get("needs_response") is True:
                expected_posts.append(p.get("post_id"))
        expected_posts.sort()
    except Exception as e:
        expected_posts = []

    if expected_posts:
        if os.path.isfile(pp_path):
            try:
                pp = load_json(pp_path)
            except:
                pp = []
            if not isinstance(pp, list):
                pp = []
            agent_posts = sorted([str(x) for x in pp])  # ensure string list
            if agent_posts == expected_posts:
                score_details.append({
                    "item": "pending_posts list (needs_response post IDs)",
                    "score": 30,
                    "max_score": 30,
                    "passed": True,
                    "reason": f"Post IDs match expected: {expected_posts}."
                })
                total_score += 30
            else:
                score_details.append({
                    "item": "pending_posts list (needs_response post IDs)",
                    "score": 0,
                    "max_score": 30,
                    "passed": False,
                    "reason": f"Expected {expected_posts}, got {agent_posts}."
                })
        else:
            score_details.append({
                "item": "pending_posts list (needs_response post IDs)",
                "score": 0,
                "max_score": 30,
                "passed": False,
                "reason": "pending_posts.json not found."
            })
    else:
        score_details.append({
            "item": "pending_posts list (needs_response post IDs)",
            "score": 0,
            "max_score": 30,
            "passed": False,
            "reason": "Could not compute expected posts from environment."
        })

    # ------------------------------------------------------------------
    # 6. No extraneous fields in launch_details (5 points)
    # ------------------------------------------------------------------
    if os.path.isfile(ld_path):
        try:
            ld = load_json(ld_path)
            allowed_keys = {"product_name", "launch_date"}
            extra = set(ld.keys()) - allowed_keys
            if not extra:
                score_details.append({
                    "item": "No extra fields in launch_details.json",
                    "score": 5,
                    "max_score": 5,
                    "passed": True,
                    "reason": "Only product_name and launch_date present."
                })
                total_score += 5
            else:
                score_details.append({
                    "item": "No extra fields in launch_details.json",
                    "score": 0,
                    "max_score": 5,
                    "passed": False,
                    "reason": f"Unexpected keys: {extra}."
                })
        except:
            score_details.append({
                "item": "No extra fields in launch_details.json",
                "score": 0,
                "max_score": 5,
                "passed": False,
                "reason": "Cannot parse file."
            })
    else:
        score_details.append({
            "item": "No extra fields in launch_details.json",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "File not found."
        })

    # ------------------------------------------------------------------
    # Write final score
    # ------------------------------------------------------------------
    result = {
        "total_score": total_score,
        "details": score_details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

    print(f"Score: {total_score}/{max_total}")

if __name__ == "__main__":
    main()
