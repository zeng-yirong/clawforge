#!/usr/bin/env python3
import sys
import json
import os

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0
    max_total = 100

    ledger_path = os.path.join(workspace, "knowledge_base/reproduction_ledger.json")

    # 1. 文件存在 (10分)
    item1 = {"item": "reproduction ledger file exists", "max_score": 10, "score": 0, "passed": False, "reason": ""}
    if os.path.isfile(ledger_path):
        item1["score"] = 10
        item1["passed"] = True
        item1["reason"] = "File exists"
    else:
        item1["reason"] = "File not found"
    total_score += item1["score"]
    score_details.append(item1)

    if item1["passed"]:
        # 2. JSON 格式合法 (10分)
        item2 = {"item": "JSON format is valid", "max_score": 10, "score": 0, "passed": False, "reason": ""}
        try:
            with open(ledger_path, "r") as f:
                data = json.load(f)
            item2["score"] = 10
            item2["passed"] = True
            item2["reason"] = "Valid JSON"
        except Exception as e:
            item2["reason"] = f"Invalid JSON: {e}"
        total_score += item2["score"]
        score_details.append(item2)

        if item2["passed"]:
            # 3. project_id 正确 (20分)
            item3 = {"item": "project_id is correct", "max_score": 20, "score": 0, "passed": False, "reason": ""}
            if isinstance(data, dict) and data.get("project_id") == "project-alpha":
                item3["score"] = 20
                item3["passed"] = True
                item3["reason"] = "project_id = project-alpha"
            else:
                item3["reason"] = f"Expected project-alpha, got {data.get('project_id')}"
            total_score += item3["score"]
            score_details.append(item3)

            # 4. status 为 completed (20分)
            item4 = {"item": "status is completed", "max_score": 20, "score": 0, "passed": False, "reason": ""}
            if data.get("status") == "completed":
                item4["score"] = 20
                item4["passed"] = True
                item4["reason"] = "status = completed"
            else:
                item4["reason"] = f"Expected completed, got {data.get('status')}"
            total_score += item4["score"]
            score_details.append(item4)

            # 5. result 字段存在且为字典 (10分)
            item5 = {"item": "result field exists and is a dictionary", "max_score": 10, "score": 0, "passed": False, "reason": ""}
            result = data.get("result")
            if isinstance(result, dict):
                item5["score"] = 10
                item5["passed"] = True
                item5["reason"] = "result exists"
            else:
                item5["reason"] = f"Expected dict, got {type(result).__name__}"
            total_score += item5["score"]
            score_details.append(item5)

            # 6. avg_response_time 正确 (30分)
            item6 = {"item": "avg_response_time is correct (225)", "max_score": 30, "score": 0, "passed": False, "reason": ""}
            avg = result.get("avg_response_time") if isinstance(result, dict) else None
            if avg is not None and (avg == 225 or avg == 225.0):
                item6["score"] = 30
                item6["passed"] = True
                item6["reason"] = f"avg_response_time = {avg}"
            else:
                item6["reason"] = f"Expected 225, got {avg}"
            total_score += item6["score"]
            score_details.append(item6)

    total_score = min(total_score, max_total)

    output = {
        "total_score": total_score,
        "details": score_details
    }
    output_path = os.path.join(workspace, "workplace_score.json")
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"Score written to {output_path}: {total_score}/100")

if __name__ == "__main__":
    main()
