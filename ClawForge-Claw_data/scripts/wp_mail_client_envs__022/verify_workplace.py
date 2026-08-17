import json
import os
import sys

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def check_exists(path):
    return os.path.exists(os.path.join(workspace, path))

def check_file(path):
    full = os.path.join(workspace, path)
    if not os.path.isfile(full):
        return None
    with open(full, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return None

def run_verification():
    details = []
    total = 0

    # 1) Directory existence (10 points)
    dirs_ok = True
    for d in ["ops", "drafts"]:
        if not os.path.isdir(os.path.join(workspace, d)):
            details.append({"item": f"Directory '{d}' exists", "score": 0, "max_score": 5, "passed": False, "reason": f"Directory '{d}' not found"})
            dirs_ok = False
        else:
            details.append({"item": f"Directory '{d}' exists", "score": 5, "max_score": 5, "passed": True, "reason": "OK"})
            total += 5
    if not dirs_ok:
        # still continue to check files (they will fail)
        pass

    # 2) ops/cert_alert.json (40 points total)
    cert_data = check_file("ops/cert_alert.json")
    if cert_data is None:
        details.append({"item": "ops/cert_alert.json valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": "File missing or invalid JSON"})
        cert_ok = False
    else:
        details.append({"item": "ops/cert_alert.json valid JSON", "score": 10, "max_score": 10, "passed": True, "reason": "Valid JSON"})
        total += 10
        cert_ok = True

    if cert_ok:
        # Expected: list of dicts, each with id, subject, sender, timestamp
        if not isinstance(cert_data, list):
            details.append({"item": "cert_alert.json is a list", "score": 0, "max_score": 10, "passed": False, "reason": "Expected list, got " + type(cert_data).__name__})
            cert_ok = False
        else:
            details.append({"item": "cert_alert.json is a list", "score": 10, "max_score": 10, "passed": True, "reason": "Is a list"})
            total += 10

        if cert_ok:
            # Must contain exactly 2 entries (email_001 and email_002)
            expected_ids = {"email_001", "email_002"}
            actual_ids = set()
            for entry in cert_data:
                if not isinstance(entry, dict):
                    continue
                if "id" in entry:
                    actual_ids.add(entry["id"])
            if actual_ids == expected_ids:
                details.append({"item": "cert_alert contains correct email IDs", "score": 20, "max_score": 20, "passed": True, "reason": "IDs match exactly"})
                total += 20
            else:
                missing = expected_ids - actual_ids
                extra = actual_ids - expected_ids
                reason = f"Missing: {missing}, Extra: {extra}"
                details.append({"item": "cert_alert contains correct email IDs", "score": 0, "max_score": 20, "passed": False, "reason": reason})

    # 3) drafts/reply.json (25 points)
    reply_data = check_file("drafts/reply.json")
    if reply_data is None:
        details.append({"item": "drafts/reply.json valid JSON", "score": 0, "max_score": 5, "passed": False, "reason": "File missing or invalid JSON"})
        reply_ok = False
    else:
        details.append({"item": "drafts/reply.json valid JSON", "score": 5, "max_score": 5, "passed": True, "reason": "Valid JSON"})
        total += 5
        reply_ok = True

    if reply_ok:
        if not isinstance(reply_data, dict) or "to" not in reply_data or "subject" not in reply_data or "body" not in reply_data:
            details.append({"item": "reply.json has required fields (to, subject, body)", "score": 0, "max_score": 5, "passed": False, "reason": "Missing required fields"})
        else:
            details.append({"item": "reply.json has required fields", "score": 5, "max_score": 5, "passed": True, "reason": "Fields present"})
            total += 5
            # Check to field
            to_ok = reply_data["to"] == "bob@vendor-services.com"
            details.append({"item": "reply to correct recipient", "score": 5 if to_ok else 0, "max_score": 5, "passed": to_ok, "reason": f"to = {reply_data.get('to')}"})
            if to_ok: total += 5
            # Check subject contains "Re: URGENT: SSL certificate"
            subj_ok = "SSL certificate" in reply_data.get("subject", "") and "Re:" in reply_data.get("subject", "")
            details.append({"item": "reply subject references SSL certificate", "score": 5 if subj_ok else 0, "max_score": 5, "passed": subj_ok, "reason": f"subject = {reply_data.get('subject')}"})
            if subj_ok: total += 5
            # Check body contains "handle" and "certificate" (case insensitive)
            body = reply_data.get("body", "")
            body_ok = "handle" in body.lower() and "certificate" in body.lower()
            details.append({"item": "reply body contains 'handle' and 'certificate'", "score": 5 if body_ok else 0, "max_score": 5, "passed": body_ok, "reason": f"body synopsis: {body[:60]}..."})
            if body_ok: total += 5

    # 4) ops/archive_list.json (25 points)
    archive_data = check_file("ops/archive_list.json")
    if archive_data is None:
        details.append({"item": "ops/archive_list.json valid JSON", "score": 0, "max_score": 5, "passed": False, "reason": "File missing or invalid JSON"})
        archive_ok = False
    else:
        details.append({"item": "ops/archive_list.json valid JSON", "score": 5, "max_score": 5, "passed": True, "reason": "Valid JSON"})
        total += 5
        archive_ok = True

    if archive_ok:
        if not isinstance(archive_data, list):
            details.append({"item": "archive_list.json is a list", "score": 0, "max_score": 5, "passed": False, "reason": "Expected list"})
        else:
            details.append({"item": "archive_list.json is a list", "score": 5, "max_score": 5, "passed": True, "reason": "Is list"})
            total += 5
            expected = {"email_004", "email_005"}
            actual = set(archive_data)
            if actual == expected:
                details.append({"item": "archive_list contains correct IDs", "score": 15, "max_score": 15, "passed": True, "reason": "IDs match"})
                total += 15
            else:
                missing = expected - actual
                extra = actual - expected
                details.append({"item": "archive_list contains correct IDs", "score": 0, "max_score": 15, "passed": False, "reason": f"Missing: {missing}, Extra: {extra}"})

    # final score
    result = {
        "total_score": total,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(f"Total score: {total}/100")

if __name__ == "__main__":
    run_verification()
