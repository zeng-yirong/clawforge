import os
import sys
import json

def load_json(path):
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return None

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0

    # 1. Check directory structure (10 pts)
    required_dirs = ["data", "data/pricing", "ops"]
    dirs_ok = all(os.path.isdir(os.path.join(workspace, d)) for d in required_dirs)
    score_details.append({
        "item": "Directory structure (data, data/pricing, ops exist)",
        "score": 10 if dirs_ok else 0,
        "max_score": 10,
        "passed": dirs_ok,
        "reason": "Required directories present" if dirs_ok else "Missing one or more directories"
    })
    if dirs_ok:
        total_score += 10

    # 2. Check report file exists (15 pts)
    report_path = os.path.join(workspace, "ops", "cost_report.json")
    report_exists = os.path.isfile(report_path)
    score_details.append({
        "item": "ops/cost_report.json exists",
        "score": 15 if report_exists else 0,
        "max_score": 15,
        "passed": report_exists,
        "reason": "Report file found" if report_exists else "Report file missing"
    })
    if report_exists:
        total_score += 15

    # 3. Report is valid JSON (10 pts)
    report_data = load_json(report_path)
    valid_json = report_data is not None
    score_details.append({
        "item": "Report is valid JSON",
        "score": 10 if valid_json else 0,
        "max_score": 10,
        "passed": valid_json,
        "reason": "JSON parsed successfully" if valid_json else "Invalid JSON"
    })
    if valid_json:
        total_score += 10

    # 4. Report contains required fields (20 pts)
    required_fields = ["cluster_name", "billing_month", "compute_cost", "storage_cost", "total_cost"]
    if valid_json and isinstance(report_data, dict):
        fields_present = all(f in report_data for f in required_fields)
    else:
        fields_present = False
    score_details.append({
        "item": "Required fields present (cluster_name, billing_month, compute_cost, storage_cost, total_cost)",
        "score": 20 if fields_present else 0,
        "max_score": 20,
        "passed": fields_present,
        "reason": "All fields present" if fields_present else "Missing one or more required fields"
    })
    if fields_present:
        total_score += 20

    # 5. Numerical correctness (45 pts) – compute expected values
    # Expected: compute = 8*0.05 + 16*0.02 = 0.4 + 0.32 = 0.72
    # storage = 200*0.10 = 20.0
    # total = 20.72
    # Note: negative quantity entry (-2 vcpu) must be ignored.
    if valid_json and fields_present:
        expected_compute = 8 * 0.05 + 16 * 0.02   # 0.4+0.32=0.72
        expected_storage = 200 * 0.10              # 20.0
        expected_total = expected_compute + expected_storage  # 20.72

        actual = report_data
        # Use tolerance for floating point
        compute_ok = abs(actual.get("compute_cost", 0) - expected_compute) < 0.001
        storage_ok = abs(actual.get("storage_cost", 0) - expected_storage) < 0.001
        total_ok = abs(actual.get("total_cost", 0) - expected_total) < 0.001
        cluster_ok = actual.get("cluster_name") == "ads-ranking"
        month_ok = actual.get("billing_month") == "2026-06"

        num_correct = sum([compute_ok, storage_ok, total_ok, cluster_ok, month_ok])
        # Score per correct element: 9 pts each (5*9=45)
        numerical_score = num_correct * 9
        score_details.append({
            "item": "Numerical and metadata correctness",
            "score": numerical_score,
            "max_score": 45,
            "passed": num_correct == 5,
            "reason": f"Correct fields: {num_correct}/5. Expected compute={expected_compute:.2f}, storage={expected_storage:.2f}, total={expected_total:.2f}, cluster=ads-ranking, month=2026-06"
        })
        total_score += numerical_score
    else:
        score_details.append({
            "item": "Numerical correctness (skipped due to previous failures)",
            "score": 0,
            "max_score": 45,
            "passed": False,
            "reason": "Report not available or invalid fields"
        })

    # Finalize
    total_score = min(total_score, 100)
    result = {
        "total_score": total_score,
        "details": score_details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score: {total_score}/100")
    sys.exit(0 if total_score >= 60 else 1)

if __name__ == "__main__":
    main()
