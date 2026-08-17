import sys
import os
import json

def verify(workspace: str) -> None:
    """验证 agent 产出的 ops/reproduction_ledger.json 是否正确"""
    details = []
    total_score = 0

    # 预期唯一答案
    EXPECTED_PROJECT_ID = "proj-success"
    EXPECTED_DATE = "2025-04-01"

    # 1. 检查文件是否存在
    ledger_path = os.path.join(workspace, "ops", "reproduction_ledger.json")
    if not os.path.exists(ledger_path):
        details.append({
            "item": "ops/reproduction_ledger.json exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not found"
        })
        # 后续检查跳过
        for item_name in ["JSON is valid", "project_id correct", "reproduction_date correct", "No extra fields"]:
            details.append({
                "item": item_name,
                "score": 0,
                "max_score": (10 if item_name == "JSON is valid" else (30 if "correct" in item_name else 10)),
                "passed": False,
                "reason": "Skipped because required file is missing"
            })
    else:
        details.append({
            "item": "ops/reproduction_ledger.json exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "File exists"
        })

        # 2. 尝试解析 JSON
        try:
            with open(ledger_path, "r") as f:
                data = json.load(f)
            details.append({
                "item": "JSON is valid",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "Valid JSON"
            })

            # 3. 检查 project_id
            actual_pid = data.get("project_id")
            if actual_pid == EXPECTED_PROJECT_ID:
                details.append({
                    "item": "project_id correct",
                    "score": 30,
                    "max_score": 30,
                    "passed": True,
                    "reason": f"project_id = {EXPECTED_PROJECT_ID}"
                })
            else:
                details.append({
                    "item": "project_id correct",
                    "score": 0,
                    "max_score": 30,
                    "passed": False,
                    "reason": f"Expected {EXPECTED_PROJECT_ID}, got {actual_pid!r}"
                })

            # 4. 检查 reproduction_date
            actual_date = data.get("reproduction_date")
            if actual_date == EXPECTED_DATE:
                details.append({
                    "item": "reproduction_date correct",
                    "score": 30,
                    "max_score": 30,
                    "passed": True,
                    "reason": f"reproduction_date = {EXPECTED_DATE}"
                })
            else:
                details.append({
                    "item": "reproduction_date correct",
                    "score": 0,
                    "max_score": 30,
                    "passed": False,
                    "reason": f"Expected {EXPECTED_DATE}, got {actual_date!r}"
                })

            # 5. 检查是否有额外字段
            allowed_keys = {"project_id", "reproduction_date"}
            extra_keys = [k for k in data if k not in allowed_keys]
            if extra_keys:
                details.append({
                    "item": "No extra fields",
                    "score": 0,
                    "max_score": 10,
                    "passed": False,
                    "reason": f"Unexpected keys: {extra_keys}"
                })
            else:
                details.append({
                    "item": "No extra fields",
                    "score": 10,
                    "max_score": 10,
                    "passed": True,
                    "reason": "Only expected keys present"
                })

        except json.JSONDecodeError as e:
            details.append({
                "item": "JSON is valid",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"Invalid JSON: {e}"
            })
            # 后续检查跳过
            for item_name in ["project_id correct", "reproduction_date correct", "No extra fields"]:
                details.append({
                    "item": item_name,
                    "score": 0,
                    "max_score": (30 if "correct" in item_name else 10),
                    "passed": False,
                    "reason": "Skipped due to invalid JSON"
                })

    # 汇总总分
    total_score = sum(d["score"] for d in details)

    # 写入 workplace_score.json
    result = {
        "total_score": total_score,
        "details": details
    }
    out_path = os.path.join(workspace, "workplace_score.json")
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)

    print(f"Total score: {total_score}/100")

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
