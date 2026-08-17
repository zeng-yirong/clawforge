import json
import os
import sys

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0

    # Target file
    target_path = os.path.join(workspace, "ops", "kill_target.json")

    # 1. File exists
    exists = os.path.isfile(target_path)
    details.append({
        "item": "File ops/kill_target.json exists",
        "score": 10 if exists else 0,
        "max_score": 10,
        "passed": exists,
        "reason": "Found" if exists else "Not found"
    })
    if exists:
        total_score += 10

    # 2. JSON valid
    valid_json = False
    data = None
    if exists:
        try:
            with open(target_path, "r") as f:
                data = json.load(f)
            valid_json = True
        except (json.JSONDecodeError, Exception):
            valid_json = False
    details.append({
        "item": "Valid JSON",
        "score": 10 if valid_json else 0,
        "max_score": 10,
        "passed": valid_json,
        "reason": "JSON parsed" if valid_json else "Invalid JSON"
    })
    if valid_json:
        total_score += 10

    # 3. Contains transaction_id field (string)
    has_field = False
    field_type_ok = False
    if valid_json and isinstance(data, dict):
        has_field = "transaction_id" in data
        if has_field:
            field_type_ok = isinstance(data["transaction_id"], str) and len(data["transaction_id"]) > 0
    details.append({
        "item": "Field 'transaction_id' present and non-empty string",
        "score": 15 if (has_field and field_type_ok) else 0,
        "max_score": 15,
        "passed": has_field and field_type_ok,
        "reason": f"Field 'transaction_id' found and type valid" if (has_field and field_type_ok) else "Missing or invalid field"
    })
    if has_field and field_type_ok:
        total_score += 15

    # 4. Value matches expected transaction ID
    expected_id = "tx_dl_payment_001"
    correct_value = False
    if valid_json and has_field and field_type_ok:
        correct_value = data["transaction_id"] == expected_id
    details.append({
        "item": f"transaction_id equals correct deadlock transaction ID (expected: {expected_id})",
        "score": 65 if correct_value else 0,
        "max_score": 65,
        "passed": correct_value,
        "reason": f"Got {data.get('transaction_id')!r}" if has_field else "Field missing"
    })
    if correct_value:
        total_score += 65

    # Optional: ensure no extra fields (penalty if extra, but not mandatory)
    extra_fields = []
    if valid_json and isinstance(data, dict):
        extra_fields = [k for k in data if k not in ("transaction_id",)]
    if extra_fields:
        penalty = -min(10, len(extra_fields) * 2)
        details.append({
            "item": "No extra fields beyond 'transaction_id'",
            "score": max(0, 0 + penalty),
            "max_score": 0,
            "passed": False,
            "reason": f"Extra fields found: {extra_fields}"
        })
    else:
        details.append({
            "item": "No extra fields beyond 'transaction_id'",
            "score": 0,
            "max_score": 0,
            "passed": True,
            "reason": "No extra fields"
        })

    # Cap total at 100
    final_score = min(total_score, 100)
    result = {
        "total_score": final_score,
        "details": details
    }
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written: {final_score}/100")

if __name__ == "__main__":
    main()
