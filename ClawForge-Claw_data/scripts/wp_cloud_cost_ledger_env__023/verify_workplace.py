"""
Pure-code verifier for wp_cloud_cost_ledger_env__023.
Checks that the agent has produced a correct monthly cost summary report.
"""
import sys
import os
import json
import math

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0
    max_total = 100

    # ---------- Helper to add score item ----------
    def add_item(name, score, max_score, passed, reason):
        score_details.append({
            "item": name,
            "score": score,
            "max_score": max_score,
            "passed": passed,
            "reason": reason
        })
        return score

    # ---------- 1. Directory existence (5 points) ----------
    reports_dir = os.path.join(workspace, "reports")
    dir_exists = os.path.isdir(reports_dir)
    total_score += add_item("reports directory exists",
                            5 if dir_exists else 0, 5, dir_exists,
                            "Found reports/ directory" if dir_exists else "Missing reports/ directory")

    # ---------- 2. File existence (5 points) ----------
    report_file = os.path.join(reports_dir, "2026-06_cost_summary.json")
    file_exists = os.path.isfile(report_file)
    total_score += add_item("report file exists",
                            5 if file_exists else 0, 5, file_exists,
                            "report file found" if file_exists else "report file missing")

    if not file_exists:
        # Can't continue without the file, write score and exit
        result = {"total_score": total_score, "details": score_details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        print(f"Final score: {total_score}/{max_total}")
        return

    # ---------- 3. JSON validity (10 points) ----------
    try:
        with open(report_file, "r") as f:
            data = json.load(f)
        json_valid = True
        total_score += add_item("JSON parse validity",
                                10, 10, True, "Valid JSON")
    except (json.JSONDecodeError, Exception) as e:
        json_valid = False
        total_score += add_item("JSON parse validity",
                                0, 10, False, f"Invalid JSON: {e}")
        # Write score and exit
        result = {"total_score": total_score, "details": score_details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        print(f"Final score: {total_score}/{max_total}")
        return

    # ---------- 4. Array with correct length (10 points) ----------
    is_list = isinstance(data, list)
    if not is_list:
        total_score += add_item("report structure",
                                0, 10, False, "Expected a JSON array, got non-list")
        result = {"total_score": total_score, "details": score_details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        print(f"Final score: {total_score}/{max_total}")
        return

    len_ok = len(data) == 2
    total_score += add_item("array length equals number of business clusters (2)",
                            10 if len_ok else 0, 10, len_ok,
                            f"Length is {len(data)} (expected 2)")

    # ---------- 5. No extra clusters (5 points) ----------
    expected_cluster_ids = {"cluster-001", "cluster-002"}
    actual_cluster_ids = {entry.get("cluster_id") for entry in data}
    extra = actual_cluster_ids - expected_cluster_ids
    no_extra = len(extra) == 0
    total_score += add_item("no extra clusters outside business set",
                            5 if no_extra else 0, 5, no_extra,
                            f"Extra cluster(s) found: {extra}" if extra else "OK")

    # ---------- 6. Required fields present (5 points) ----------
    required_fields = {"cluster_id", "cluster_name", "total_cost"}
    missing_fields = False
    for idx, entry in enumerate(data):
        missing = required_fields - set(entry.keys())
        if missing:
            missing_fields = True
            break
    fields_ok = not missing_fields
    total_score += add_item("all entries have required fields (cluster_id, cluster_name, total_cost)",
                            5 if fields_ok else 0, 5, fields_ok,
                            "All fields present" if fields_ok else "Some entries missing required fields")

    if missing_fields:
        # If fields missing, can't compute numerical scores reliably, stop further checks
        result = {"total_score": total_score, "details": score_details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        print(f"Final score: {total_score}/{max_total}")
        return

    # ---------- 7. Individual cluster correctness ----------
    # Build lookup from expected data
    expected = [
        {"cluster_id": "cluster-001", "cluster_name": "ads-ranking", "total_cost": 62.00},
        {"cluster_id": "cluster-002", "cluster_name": "lakehouse-analytics", "total_cost": 67.00}
    ]
    # Map actual entries by cluster_id
    actual_map = {}
    for entry in data:
        actual_map[entry["cluster_id"]] = entry

    for exp in expected:
        cid = exp["cluster_id"]
        # cluster_id and cluster_name checks (5 pts each)
        if cid in actual_map:
            act = actual_map[cid]
            id_ok = act["cluster_id"] == exp["cluster_id"]
            name_ok = act["cluster_name"] == exp["cluster_name"]
            # cluster_id correct (5 pts)
            total_score += add_item(f"cluster_id for {cid}",
                                    5 if id_ok else 0, 5, id_ok,
                                    f"actual {act['cluster_id']}" if id_ok else f"mismatch: expected {exp['cluster_id']}, got {act['cluster_id']}")
            # cluster_name correct (5 pts)
            total_score += add_item(f"cluster_name for {cid}",
                                    5 if name_ok else 0, 5, name_ok,
                                    f"actual {act['cluster_name']}" if name_ok else f"mismatch: expected {exp['cluster_name']}, got {act['cluster_name']}")
            # total_cost correct (20 pts each)
            cost_ok = abs(act["total_cost"] - exp["total_cost"]) < 0.01
            total_score += add_item(f"total_cost for {cid}",
                                    20 if cost_ok else 0, 20, cost_ok,
                                    f"actual {act['total_cost']}" if cost_ok else f"mismatch: expected {exp['total_cost']:.2f}, got {act['total_cost']:.2f}")
        else:
            # Missing cluster => zero for all sub-scores
            total_score += add_item(f"cluster_id for {cid}",
                                    0, 5, False, f"missing entry for {cid}")
            total_score += add_item(f"cluster_name for {cid}",
                                    0, 5, False, f"missing entry for {cid}")
            total_score += add_item(f"total_cost for {cid}",
                                    0, 20, False, f"missing entry for {cid}")

    # ---------- Finalize ----------
    result = {
        "total_score": total_score,
        "details": score_details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

    print(f"Final score: {total_score}/{max_total}")

if __name__ == "__main__":
    main()
