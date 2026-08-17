import sys
import os
import json

def verify(workspace):
    score_details = []
    total_score = 0
    max_total = 100

    result_path = os.path.join(workspace, "ops", "recommended_stocks.json")

    # 1. 文件存在性 (10分)
    if not os.path.isfile(result_path):
        result = {
            "total_score": 0,
            "details": [{"item": "file existence", "score": 0, "max_score": 10, "passed": False, "reason": "File ops/recommended_stocks.json not found"}]
        }
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return result
    else:
        score_details.append({"item": "file existence", "score": 10, "max_score": 10, "passed": True, "reason": "File exists"})
        total_score += 10

    # 2. JSON合法性 (10分)
    try:
        with open(result_path, "r") as f:
            data = json.load(f)
        score_details.append({"item": "valid JSON", "score": 10, "max_score": 10, "passed": True, "reason": "Valid JSON"})
        total_score += 10
    except Exception as e:
        result = {
            "total_score": total_score,
            "details": [{"item": "valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"Invalid JSON: {e}"}]
        }
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return result

    # 3. 必须是列表 (10分)
    if not isinstance(data, list):
        result = {
            "total_score": total_score,
            "details": [{"item": "result type", "score": 0, "max_score": 10, "passed": False, "reason": "Result is not a list"}]
        }
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return result
    else:
        score_details.append({"item": "result is list", "score": 10, "max_score": 10, "passed": True, "reason": "Result is a list"})
        total_score += 10

    # 4. 列表长度 (20分)
    if len(data) != 1:
        score_details.append({"item": "list length", "score": 0, "max_score": 20, "passed": False, "reason": f"Expected 1 item, got {len(data)}"})
        score_details.append({"item": "required fields", "score": 0, "max_score": 20, "passed": False, "reason": "Skipped due to incorrect length"})
        score_details.append({"item": "ticker value", "score": 0, "max_score": 15, "passed": False, "reason": "Skipped"})
        score_details.append({"item": "company_name value", "score": 0, "max_score": 15, "passed": False, "reason": "Skipped"})
        result = {"total_score": total_score, "details": score_details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return result
    else:
        score_details.append({"item": "list length", "score": 20, "max_score": 20, "passed": True, "reason": "Length is 1"})
        total_score += 20

    # 5. 字段存在性 (20分)
    item = data[0]
    has_ticker = "ticker" in item
    has_company = "company_name" in item
    if has_ticker and has_company:
        score_details.append({"item": "required fields", "score": 20, "max_score": 20, "passed": True, "reason": "Contains ticker and company_name"})
        total_score += 20
    else:
        missing = []
        if not has_ticker: missing.append("ticker")
        if not has_company: missing.append("company_name")
        score_details.append({"item": "required fields", "score": 0, "max_score": 20, "passed": False, "reason": f"Missing fields: {', '.join(missing)}"})
        # 字段缺失，后续无法检查，返回当前总分
        result = {"total_score": total_score, "details": score_details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return result

    # 6. ticker值 (15分)
    correct_ticker = "TECH"
    if item["ticker"] == correct_ticker:
        score_details.append({"item": "ticker value", "score": 15, "max_score": 15, "passed": True, "reason": "Correct ticker"})
        total_score += 15
    else:
        score_details.append({"item": "ticker value", "score": 0, "max_score": 15, "passed": False, "reason": f"Expected '{correct_ticker}', got '{item['ticker']}'"})

    # 7. company_name值 (15分)
    correct_company = "TechVentures Inc"
    if item["company_name"] == correct_company:
        score_details.append({"item": "company_name value", "score": 15, "max_score": 15, "passed": True, "reason": "Correct company_name"})
        total_score += 15
    else:
        score_details.append({"item": "company_name value", "score": 0, "max_score": 15, "passed": False, "reason": f"Expected '{correct_company}', got '{item['company_name']}'"})

    # 写入最终结果
    result = {"total_score": total_score, "details": score_details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    return result

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
