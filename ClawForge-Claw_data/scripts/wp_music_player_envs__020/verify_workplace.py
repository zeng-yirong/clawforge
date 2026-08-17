import sys
import json
import os
import csv
from pathlib import Path

def main(workspace):
    workspace = Path(workspace)
    score_details = []
    total_score = 0

    # 1. Check output directory exists
    output_dir = workspace / "output"
    if output_dir.is_dir():
        score_details.append({"item": "Output directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "output/ directory found"})
        total_score += 10
    else:
        score_details.append({"item": "Output directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "output/ directory missing"})

    # 2. Check report.json exists and is valid JSON
    report_path = output_dir / "report.json"
    report_data = None
    if report_path.is_file():
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                report_data = json.load(f)
            score_details.append({"item": "report.json exists and valid JSON", "score": 10, "max_score": 10, "passed": True, "reason": "File found and JSON parseable"})
            total_score += 10
        except (json.JSONDecodeError, UnicodeDecodeError):
            score_details.append({"item": "report.json exists and valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": "Invalid JSON or encoding"})
    else:
        score_details.append({"item": "report.json exists and valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": "report.json not found"})

    if report_data is None:
        # Cannot continue with detailed checks, finalize
        final_score = total_score
        write_score(workspace, final_score, score_details)
        return

    # 3. Check that report contains a "count" field (or equivalent numeric field)
    #    We allow any numeric field, but prefer "count". We'll check for "count" first, then fallback to any numeric.
    count_field = None
    count_value = None
    if isinstance(report_data, dict):
        if "count" in report_data:
            count_field = "count"
            count_value = report_data["count"]
        else:
            # search for any numeric field
            for key, val in report_data.items():
                if isinstance(val, (int, float)):
                    count_field = key
                    count_value = val
                    break
    if count_field is not None and isinstance(count_value, (int, float)):
        score_details.append({"item": "Report contains a numeric count field", "score": 10, "max_score": 10, "passed": True, "reason": f"Found field '{count_field}' with value {count_value}"})
        total_score += 10
    else:
        score_details.append({"item": "Report contains a numeric count field", "score": 0, "max_score": 10, "passed": False, "reason": "No numeric count field found in report"})
        # Still continue to try exact value check? No point, but we can.

    # 4. Verify the exact count value (correct answer is 5)
    #    Ground truth: in playlist "speed_and_fury" (id speed_and_fury), song_ids = s001,s002,s003,s004,s005,s006,s007
    #    Among those, songs with language exactly "英文" (standard, excluding "English") : s001, s002, s004, s006, s007 -> 5
    #    Also note s005 has language "English" (non-standard) should be excluded. s003 is Chinese.
    expected_count = 5
    if count_value is not None and count_value == expected_count:
        score_details.append({"item": "Correct count of English songs in target playlist", "score": 50, "max_score": 50, "passed": True, "reason": f"Count is exactly {expected_count}"})
        total_score += 50
    elif count_value is not None:
        score_details.append({"item": "Correct count of English songs in target playlist", "score": 0, "max_score": 50, "passed": False, "reason": f"Expected {expected_count}, got {count_value}"})
    else:
        score_details.append({"item": "Correct count of English songs in target playlist", "score": 0, "max_score": 50, "passed": False, "reason": "Cannot evaluate count because no numeric field found"})

    # 5. Check that agent correctly handled dirty data (optional bonus? but we already penalize if count wrong)
    #    We can check if the reported value is integer (not float) and within plausible range? Not necessary.
    #    Add a small bonus for integer result (if applicable)
    if count_field and isinstance(count_value, int):
        score_details.append({"item": "Count value is an integer (clean handling)", "score": 10, "max_score": 10, "passed": True, "reason": "Value is integer type"})
        total_score += 10
    else:
        score_details.append({"item": "Count value is an integer (clean handling)", "score": 0, "max_score": 10, "passed": False, "reason": "Value is not integer or field missing"})

    # 6. Check that no extra unexpected fields appear in report (optional)
    #    We can check that report has only 'count' (or a few reasonable fields). Not scoring, just info.

    # Cap total at 100
    final_score = min(total_score, 100)
    write_score(workspace, final_score, score_details)

def write_score(workspace, score, details):
    score_path = workspace / "workplace_score.json"
    data = {
        "total_score": score,
        "details": details
    }
    with open(score_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Score written: {score}/100")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        workspace = sys.argv[1]
    else:
        workspace = "."
    main(workspace)
