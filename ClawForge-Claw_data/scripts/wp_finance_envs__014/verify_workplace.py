import sys
import os
import json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    max_total = 100
    details = []

    # 1. 检查 reports/ 目录是否存在 (10)
    reports_dir = os.path.join(workspace, "reports")
    if os.path.isdir(reports_dir):
        details.append({"item": "reports/ directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "Directory found."})
        score += 10
    else:
        details.append({"item": "reports/ directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "Directory missing."})

    # 2. 检查 reports/tech_final_brief.json 是否存在 (10)
    brief_path = os.path.join(reports_dir, "tech_final_brief.json")
    if os.path.isfile(brief_path):
        details.append({"item": "reports/tech_final_brief.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "File found."})
        score += 10
    else:
        details.append({"item": "reports/tech_final_brief.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "File missing."})
        # 无法继续检查，直接输出结果
        write_score(score, details)
        return

    # 3. 解析 JSON 并检查格式合法 (10)
    try:
        with open(brief_path, "r") as f:
            brief = json.load(f)
        details.append({"item": "JSON is valid", "score": 10, "max_score": 10, "passed": True, "reason": "Parsed successfully."})
        score += 10
    except (json.JSONDecodeError, Exception) as e:
        details.append({"item": "JSON is valid", "score": 0, "max_score": 10, "passed": False, "reason": f"Invalid JSON: {e}"})
        write_score(score, details)
        return

    # 4. 检查 recommendations 数组存在且长度 >= 2 (10)
    recs = brief.get("recommendations")
    if isinstance(recs, list) and len(recs) >= 2:
        details.append({"item": "recommendations array with at least 2 entries", "score": 10, "max_score": 10, "passed": True, "reason": f"Found {len(recs)} recommendations."})
        score += 10
    else:
        details.append({"item": "recommendations array with at least 2 entries", "score": 0, "max_score": 10, "passed": False, "reason": "Missing or insufficient recommendations."})
        # 后续检查需要recs，跳到created_at
        recs = []

    # 5. 检查 NXTC 推荐为 Buy (20)
    nxtc_found = False
    tech_found = False
    nxtc_ok = False
    tech_ok = False
    for r in recs:
        if r.get("ticker") == "NXTC":
            nxtc_found = True
            if r.get("action") == "Buy":
                nxtc_ok = True
        if r.get("ticker") == "TECH":
            tech_found = True
            if r.get("action") == "Sell":
                tech_ok = True

    if nxtc_ok:
        details.append({"item": "NXTC action is 'Buy'", "score": 20, "max_score": 20, "passed": True, "reason": "Correct action for NXTC."})
        score += 20
    else:
        reason = "NXTC not found or action not 'Buy'"
        if not nxtc_found:
            reason = "NXTC ticker missing in recommendations."
        details.append({"item": "NXTC action is 'Buy'", "score": 0, "max_score": 20, "passed": False, "reason": reason})

    # 6. 检查 TECH 推荐为 Sell (20)
    if tech_ok:
        details.append({"item": "TECH action is 'Sell'", "score": 20, "max_score": 20, "passed": True, "reason": "Correct action for TECH."})
        score += 20
    else:
        reason = "TECH not found or action not 'Sell'"
        if not tech_found:
            reason = "TECH ticker missing in recommendations."
        details.append({"item": "TECH action is 'Sell'", "score": 0, "max_score": 20, "passed": False, "reason": reason})

    # 7. 检查 created_at 字段为 "2026-07-15" (20)
    cr = brief.get("created_at")
    if cr == "2026-07-15":
        details.append({"item": "created_at is '2026-07-15'", "score": 20, "max_score": 20, "passed": True, "reason": "Date matches."})
        score += 20
    else:
        details.append({"item": "created_at is '2026-07-15'", "score": 0, "max_score": 20, "passed": False, "reason": f"Got '{cr}', expected '2026-07-15'."})

    # 8. 检查 confidence 字段存在且合理 (bonus, 但总分不超过100) - 我们将其设为10分从其他地方扣? 已经满分100，跳过额外
    # 实际总分已经100，我们不再加额外项，但可以给予提示
    # 确保总分不超过100
    total = min(score, 100)

    write_score(total, details)

def write_score(total, details):
    result = {
        "total_score": total,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
