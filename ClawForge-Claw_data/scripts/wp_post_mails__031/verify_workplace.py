import sys
import json
import os
import pathlib

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    wp = pathlib.Path(workspace)

    score = 0
    details = []

    # 1. output 目录存在 (10)
    out_dir = wp / "output"
    if out_dir.exists() and out_dir.is_dir():
        details.append({"item": "output directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "Found output/"})
        score += 10
    else:
        details.append({"item": "output directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "output/ directory missing"})

    # 2. launch_info.json 存在 (10)
    info_file = out_dir / "launch_info.json"
    if info_file.exists():
        details.append({"item": "launch_info.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "Found output/launch_info.json"})
        score += 10
    else:
        details.append({"item": "launch_info.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "File missing"})
        # 后续检查无法进行，直接写结果
        total = score
        write_result(total, details, workspace)
        return

    # 3. JSON 合法性 (10)
    try:
        with open(info_file, "r") as f:
            data = json.load(f)
        details.append({"item": "JSON is valid", "score": 10, "max_score": 10, "passed": True, "reason": "Parsed successfully"})
        score += 10
    except Exception as e:
        details.append({"item": "JSON is valid", "score": 0, "max_score": 10, "passed": False, "reason": f"Parse error: {e}"})
        total = score
        write_result(total, details, workspace)
        return

    # 4. product_name (15)
    if data.get("product_name") == "Aurora Orbital Launch":
        details.append({"item": "product_name correct", "score": 15, "max_score": 15, "passed": True, "reason": "Matches expected"})
        score += 15
    else:
        details.append({"item": "product_name correct", "score": 0, "max_score": 15, "passed": False, "reason": f"Got '{data.get('product_name')}', expected 'Aurora Orbital Launch'"})

    # 5. version_build (15)
    v = data.get("version_build")
    if isinstance(v, (int, float)) and v == 3.0:
        details.append({"item": "version_build correct", "score": 15, "max_score": 15, "passed": True, "reason": f"Got {v}"})
        score += 15
    else:
        details.append({"item": "version_build correct", "score": 0, "max_score": 15, "passed": False, "reason": f"Got {v}, expected 3.0"})

    # 6. launch_date (15)
    if data.get("launch_date") == "2026-07-15":
        details.append({"item": "launch_date correct", "score": 15, "max_score": 15, "passed": True, "reason": "Matches expected"})
        score += 15
    else:
        details.append({"item": "launch_date correct", "score": 0, "max_score": 15, "passed": False, "reason": f"Got '{data.get('launch_date')}', expected '2026-07-15'"})

    # 7. risk_flag (15)
    rf = data.get("risk_flag")
    if rf is False:
        details.append({"item": "risk_flag correct", "score": 15, "max_score": 15, "passed": True, "reason": "risk_flag is false"})
        score += 15
    else:
        details.append({"item": "risk_flag correct", "score": 0, "max_score": 15, "passed": False, "reason": f"Got {rf}, expected false"})

    # 8. 无多余字段 (10)
    expected_keys = {"product_name", "version_build", "launch_date", "risk_flag"}
    actual_keys = set(data.keys())
    if actual_keys == expected_keys:
        details.append({"item": "no extra fields", "score": 10, "max_score": 10, "passed": True, "reason": "Exactly the 4 required fields"})
        score += 10
    else:
        extra = actual_keys - expected_keys
        details.append({"item": "no extra fields", "score": 0, "max_score": 10, "passed": False, "reason": f"Extra fields: {extra}"})

    total = score
    write_result(total, details, workspace)

def write_result(total, details, workspace):
    result = {"total_score": total, "details": details}
    result_path = pathlib.Path(workspace) / "workplace_score.json"
    with open(result_path, "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
