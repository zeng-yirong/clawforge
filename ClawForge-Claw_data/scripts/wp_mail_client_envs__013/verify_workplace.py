import sys
import os
import json

def score_detail(item, score, max_score, passed, reason):
    return {"item": item, "score": score, "max_score": max_score, "passed": passed, "reason": reason}

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result_path = os.path.join(workspace, "ops", "result.json")
    details = []
    total_max = 100
    score = 0

    # 1. Check file exists (10 points)
    if os.path.isfile(result_path):
        details.append(score_detail("result.json exists", 10, 10, True, "File found"))
        score += 10
    else:
        details.append(score_detail("result.json exists", 0, 10, False, "File not found at ops/result.json"))
        # If file missing, can't proceed with further checks
        final = {"total_score": score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(final, f, indent=2)
        return

    # 2. Parse JSON (10 points)
    try:
        with open(result_path, "r") as f:
            data = json.load(f)
        details.append(score_detail("JSON parse valid", 10, 10, True, "Valid JSON"))
        score += 10
    except (json.JSONDecodeError, Exception) as e:
        details.append(score_detail("JSON parse valid", 0, 10, False, f"Parse error: {e}"))
        final = {"total_score": score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(final, f, indent=2)
        return

    # 3. Check archived_spam_ids (15 points)
    expected_spam = {"e001", "e002"}
    actual_spam = set(data.get("archived_spam_ids", []))
    if actual_spam == expected_spam:
        details.append(score_detail("Spam IDs archived", 15, 15, True, f"Correct set: {expected_spam}"))
        score += 15
    else:
        details.append(score_detail("Spam IDs archived", 0, 15, False,
                                    f"Expected {expected_spam}, got {actual_spam}"))

    # 4. Check archived_newsletter_ids (15 points)
    expected_news = {"e003", "e004", "e005"}
    actual_news = set(data.get("archived_newsletter_ids", []))
    if actual_news == expected_news:
        details.append(score_detail("Newsletter IDs archived", 15, 15, True, f"Correct set: {expected_news}"))
        score += 15
    else:
        details.append(score_detail("Newsletter IDs archived", 0, 15, False,
                                    f"Expected {expected_news}, got {actual_news}"))

    # 5. Reply information (30 points)
    reply_info = data.get("reply", {})
    # 5a. Reply to (5)
    expected_to = "alice@clientcorp.com"
    actual_to = reply_info.get("to", "")
    if actual_to == expected_to:
        details.append(score_detail("Reply to address", 5, 5, True, "Correct recipient"))
        score += 5
    else:
        details.append(score_detail("Reply to address", 0, 5, False, f"Expected {expected_to}, got {actual_to}"))

    # 5b. Subject (5)
    expected_subject_prefix = "Re: Invoice discrepancy - urgent"
    actual_subject = reply_info.get("subject", "")
    if actual_subject.startswith(expected_subject_prefix):
        details.append(score_detail("Reply subject", 5, 5, True, f"Starts with '{expected_subject_prefix}'"))
        score += 5
    else:
        details.append(score_detail("Reply subject", 0, 5, False, f"Expected starting with '{expected_subject_prefix}', got '{actual_subject}'"))

    # 5c. Body contains total amount (20)
    expected_amount = "1245.67"
    body = reply_info.get("body", "")
    if expected_amount in body:
        details.append(score_detail("Reply body contains total amount", 20, 20, True, f"Amount {expected_amount} found"))
        score += 20
    else:
        details.append(score_detail("Reply body contains total amount", 0, 20, False, f"Expected to contain '{expected_amount}', body was: {body[:200]}"))

    # 6. TODO items (20 points)
    expected_todos = ["Verify quote total and confirm receipt"]
    actual_todos = data.get("todo_items", [])
    # Accept any list that contains the expected item (could be more, but must have this)
    if expected_todos[0] in actual_todos:
        details.append(score_detail("TODO items", 20, 20, True, f"Contains expected TODO: '{expected_todos[0]}'"))
        score += 20
    else:
        details.append(score_detail("TODO items", 0, 20, False, f"Expected TODO '{expected_todos[0]}' not in {actual_todos}"))

    # Final score
    final = {"total_score": score, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(final, f, indent=2)

if __name__ == "__main__":
    main()
