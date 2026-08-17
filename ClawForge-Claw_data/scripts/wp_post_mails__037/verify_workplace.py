import sys
import json
import os

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    # ------------------------------------------------------------------
    # 1. Check target file exists
    target_path = os.path.join(workspace, "ops", "launch_plan.json")
    if not os.path.isfile(target_path):
        details.append({
            "item": "ops/launch_plan.json exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not found"
        })
        # early exit if no file
        total = 0
        write_score(total, details, workspace)
        return

    details.append({
        "item": "ops/launch_plan.json exists",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "File present"
    })
    score += 10

    # ------------------------------------------------------------------
    # 2. Validate JSON syntax
    try:
        with open(target_path, "r") as f:
            data = json.load(f)
        details.append({
            "item": "Valid JSON",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Parsed successfully"
        })
        score += 10
    except Exception as e:
        details.append({
            "item": "Valid JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON parse error: {e}"
        })
        total = score  # stop further checks
        write_score(total, details, workspace)
        return

    # ------------------------------------------------------------------
    # 3. Check product_name
    expected_product = "Nova-7"
    actual_product = data.get("product_name", "")
    if actual_product == expected_product:
        details.append({
            "item": "product_name is 'Nova-7'",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": f"Correct: {actual_product}"
        })
        score += 20
    else:
        details.append({
            "item": "product_name is 'Nova-7'",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"Got '{actual_product}', expected '{expected_product}'"
        })

    # 4. Check launch_date
    expected_date = "2025-06-20"
    actual_date = data.get("launch_date", "")
    if actual_date == expected_date:
        details.append({
            "item": "launch_date is '2025-06-20'",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": f"Correct: {actual_date}"
        })
        score += 20
    else:
        details.append({
            "item": "launch_date is '2025-06-20'",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"Got '{actual_date}', expected '{expected_date}'"
        })

    # 5. Check message_for_x
    expected_x = "Excited to announce Nova-7, the next-gen orbital platform! #Nova7"
    actual_x = data.get("message_for_x", "")
    if actual_x == expected_x:
        details.append({
            "item": "message_for_x matches approved content",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "Exact match"
        })
        score += 20
    else:
        details.append({
            "item": "message_for_x matches approved content",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"Got '{actual_x}', expected '{expected_x}'"
        })

    # 6. Check message_for_reddit
    expected_reddit = "We've been working hard on Nova-7. Check out the features! [link]"
    actual_reddit = data.get("message_for_reddit", "")
    if actual_reddit == expected_reddit:
        details.append({
            "item": "message_for_reddit matches approved content",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "Exact match"
        })
        score += 20
    else:
        details.append({
            "item": "message_for_reddit matches approved content",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"Got '{actual_reddit}', expected '{expected_reddit}'"
        })

    # ------------------------------------------------------------------
    total = score
    write_score(total, details, workspace)

def write_score(total, details, workspace):
    out_path = os.path.join(workspace, "workplace_score.json")
    result = {
        "total_score": total,
        "details": details
    }
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    verify()
