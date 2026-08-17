#!/usr/bin/env python3
"""
Verify that the agent produced the correct postmortem file in ops/postmortem_041.json.
Checks:
1. Directory structure (ops/ exists)
2. File exists and is valid JSON
3. Required fields present
4. fault_id matches expected
5. peak_connections and connection_limit match expected values
6. root_cause and repair_plan are non-empty strings (optional but good practice)
Score distribution: dir=10, file_exists=10, valid_json=10, fault_id=20, peak_connections=20, connection_limit=20, textual fields=10 (5+5)
Total 100.
"""

import sys
import json
import os

WORKSPACE = sys.argv[1] if len(sys.argv) > 1 else "."

def check(condition, score, max_score, reason):
    return {"score": score if condition else 0, "max_score": max_score, "passed": condition, "reason": reason}

def main():
    results = []
    total_score = 0
    max_total = 100
    
    # 1. Check ops directory exists
    ops_dir = os.path.join(WORKSPACE, "ops")
    dir_ok = os.path.isdir(ops_dir)
    results.append(check(dir_ok, 10, 10, "ops/ directory exists" if dir_ok else "ops/ directory missing"))
    total_score += 10 if dir_ok else 0
    
    # 2. Check result file exists
    result_path = os.path.join(ops_dir, "postmortem_041.json")
    file_ok = os.path.isfile(result_path)
    results.append(check(file_ok, 10, 10, "ops/postmortem_041.json exists" if file_ok else "File not found"))
    total_score += 10 if file_ok else 0
    
    if not file_ok:
        # cannot proceed, fill remaining scores as 0
        for item in ["valid_json", "fault_id", "peak_connections", "connection_limit", "textual_fields"]:
            results.append({"score": 0, "max_score": 20 if item != "textual_fields" else 10, "passed": False, "reason": "File not found"})
        total_score = 20  # only dir and file existence give 20
    else:
        # 3. Parse JSON
        with open(result_path, "r") as f:
            try:
                data = json.load(f)
                json_ok = True
                results.append(check(True, 10, 10, "Valid JSON"))
                total_score += 10
            except json.JSONDecodeError as e:
                json_ok = False
                results.append(check(False, 0, 10, f"Invalid JSON: {e}"))
                total_score += 0
                # cannot check further
                for item in ["fault_id", "peak_connections", "connection_limit", "textual_fields"]:
                    results.append({"score": 0, "max_score": 20 if item != "textual_fields" else 10, "passed": False, "reason": "JSON parse failed"})
                # write final score
                final = {"total_score": total_score, "details": results}
                with open(os.path.join(WORKSPACE, "workplace_score.json"), "w") as sf:
                    json.dump(final, sf)
                print(f"Score: {total_score}/100")
                return
        
        # 4. Check fault_id
        expected_fault_id = "fault_041"
        fid_ok = isinstance(data.get("fault_id"), str) and data["fault_id"] == expected_fault_id
        results.append(check(fid_ok, 20, 20, f"fault_id is '{expected_fault_id}'" if fid_ok else f"fault_id is {data.get('fault_id')}"))
        total_score += 20 if fid_ok else 0
        
        # 5. Check peak_connections
        expected_peak = 512
        peak_ok = isinstance(data.get("peak_connections"), (int, float)) and data["peak_connections"] == expected_peak
        results.append(check(peak_ok, 20, 20, f"peak_connections = {expected_peak}" if peak_ok else f"peak_connections = {data.get('peak_connections')}"))
        total_score += 20 if peak_ok else 0
        
        # 6. Check connection_limit
        expected_limit = 400
        limit_ok = isinstance(data.get("connection_limit"), (int, float)) and data["connection_limit"] == expected_limit
        results.append(check(limit_ok, 20, 20, f"connection_limit = {expected_limit}" if limit_ok else f"connection_limit = {data.get('connection_limit')}"))
        total_score += 20 if limit_ok else 0
        
        # 7. Check textual fields (root_cause and repair_plan) are non-empty strings
        rc_ok = isinstance(data.get("root_cause"), str) and len(data["root_cause"].strip()) > 0
        rp_ok = isinstance(data.get("repair_plan"), str) and len(data["repair_plan"].strip()) > 0
        textual_ok = rc_ok and rp_ok
        textual_reason = "Both root_cause and repair_plan are non-empty strings" if textual_ok else f"root_cause ok: {rc_ok}, repair_plan ok: {rp_ok}"
        results.append(check(textual_ok, 10, 10, textual_reason))
        total_score += 10 if textual_ok else 0
    
    # Build final score detail
    final = {"total_score": total_score, "details": results}
    score_path = os.path.join(WORKSPACE, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(final, f)
    print(f"Score: {total_score}/100")

if __name__ == "__main__":
    main()
