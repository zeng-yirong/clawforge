import sys
import json
import os
import math

def verify(workspace):
    score_details = []
    total = 0

    # 1. ops 目录存在
    ops_dir = os.path.join(workspace, "ops")
    item = {"item": "ops directory exists", "max_score": 10}
    if os.path.isdir(ops_dir):
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "ops directory found"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = "ops directory missing"
    score_details.append(item)
    total += item["score"]

    # 2. brief_prep.json 存在
    result_file = os.path.join(ops_dir, "brief_prep.json")
    item = {"item": "brief_prep.json exists", "max_score": 10}
    if os.path.isfile(result_file):
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "file found"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = "file not found"
    score_details.append(item)
    total += item["score"]

    # 3. JSON 解析
    item = {"item": "JSON parseable", "max_score": 10}
    try:
        with open(result_file, "r") as f:
            data = json.load(f)
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "valid JSON"
    except Exception as e:
        data = None
        item["score"] = 0
        item["passed"] = False
        item["reason"] = f"JSON parse error: {e}"
    score_details.append(item)
    total += item["score"]

    if data is None:
        # 无法继续评分
        for name in ["required fields", "average_pe value", "top_growth_ticker value", "top_growth_value value"]:
            score_details.append({"item": name, "score": 0, "max_score": 20 if "value" in name else 15, "passed": False, "reason": "JSON not available"})
    else:
        # 4. 检查必需字段
        required_fields = {"average_pe", "top_growth_ticker", "top_growth_value"}
        fields = set(data.keys())
        item = {"item": "required fields present", "max_score": 15}
        if required_fields == fields:
            item["score"] = 15
            item["passed"] = True
            item["reason"] = "exactly required fields"
        elif required_fields.issubset(fields):
            item["score"] = 10
            item["passed"] = True
            item["reason"] = f"extra fields found: {fields - required_fields}"
        else:
            missing = required_fields - fields
            item["score"] = 0
            item["passed"] = False
            item["reason"] = f"missing fields: {missing}"
        score_details.append(item)
        total += item["score"]

        # 5. average_pe 值
        expected_pe = 22.5
        item = {"item": "average_pe value", "max_score": 20}
        if "average_pe" in data:
            pe = data["average_pe"]
            if math.isclose(pe, expected_pe, abs_tol=0.01):
                item["score"] = 20
                item["passed"] = True
                item["reason"] = f"average_pe is {pe}"
            else:
                item["score"] = 0
                item["passed"] = False
                item["reason"] = f"expected {expected_pe}, got {pe}"
        else:
            item["score"] = 0
            item["passed"] = False
            item["reason"] = "field missing"
        score_details.append(item)
        total += item["score"]

        # 6. top_growth_ticker 值
        expected_ticker = "NXTC"
        item = {"item": "top_growth_ticker value", "max_score": 15}
        ticker = data.get("top_growth_ticker")
        if ticker == expected_ticker:
            item["score"] = 15
            item["passed"] = True
            item["reason"] = f"ticker is {ticker}"
        else:
            item["score"] = 0
            item["passed"] = False
            item["reason"] = f"expected {expected_ticker}, got {ticker}"
        score_details.append(item)
        total += item["score"]

        # 7. top_growth_value 值
        expected_value = 22.0
        item = {"item": "top_growth_value value", "max_score": 20}
        growth = data.get("top_growth_value")
        if growth is not None and math.isclose(growth, expected_value, abs_tol=0.01):
            item["score"] = 20
            item["passed"] = True
            item["reason"] = f"growth value is {growth}"
        else:
            item["score"] = 0
            item["passed"] = False
            item["reason"] = f"expected {expected_value}, got {growth}"
        score_details.append(item)
        total += item["score"]

    total = min(total, 100)
    result = {
        "total_score": total,
        "details": score_details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

    return total

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
