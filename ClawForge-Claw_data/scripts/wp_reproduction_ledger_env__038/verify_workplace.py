import os
import sys
import json
import pathlib

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    workspace = pathlib.Path(workspace)

    results = []
    total_score = 0

    # 1. 检查 output 目录是否存在 (10分)
    output_dir = workspace / "output"
    item = {"item": "output directory exists", "max_score": 10}
    if output_dir.is_dir():
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "output directory found"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = "output directory missing"
    results.append(item)
    total_score += item["score"]

    # 2. 检查 reproduction_ledger.json 是否存在 (10分)
    ledger_path = output_dir / "reproduction_ledger.json"
    item = {"item": "reproduction_ledger.json exists", "max_score": 10}
    if ledger_path.is_file():
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "file found"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = "file missing"
    results.append(item)
    total_score += item["score"]

    # 3. JSON 格式合法性 (10分)
    item = {"item": "valid JSON", "max_score": 10}
    try:
        with open(ledger_path, "r") as f:
            data = json.load(f)
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "JSON valid"
    except Exception as e:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = f"JSON error: {e}"
    results.append(item)
    total_score += item["score"]

    # 如果JSON无效，后续检查跳过（记零分）
    if not item["passed"]:
        # 后续项计0分
        for label in ["ledger_id", "project_id", "title", "scenarios array", "scenario contents", "status", "no extra projects", "final indicator"]:
            results.append({
                "item": label,
                "max_score": 10,
                "score": 0,
                "passed": False,
                "reason": "previous JSON parse failed"
            })
        write_score(results, total_score)
        return

    # 4. 检查 ledger_id (10分)
    item = {"item": "ledger_id == 'ledger_038'", "max_score": 10}
    if data.get("ledger_id") == "ledger_038":
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "correct ledger_id"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = f"got '{data.get('ledger_id')}'"
    results.append(item)
    total_score += item["score"]

    # 5. 检查 project_id (10分)
    item = {"item": "project_id == 'proj_038'", "max_score": 10}
    if data.get("project_id") == "proj_038":
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "correct project_id"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = f"got '{data.get('project_id')}'"
    results.append(item)
    total_score += item["score"]

    # 6. 检查 title (10分)
    item = {"item": "title derived from document", "max_score": 10}
    # 文档title是 "Bug Fix v2.1"，但prompt说“从文档里提取的标题”，agent可能原样或加前缀
    acceptable_titles = ["Bug Fix v2.1", "Reproduction Ledger for Bug Fix v2.1", "Ledger for Bug Fix v2.1"]
    title = data.get("title", "")
    if title in acceptable_titles or title.startswith("Bug Fix v2.1"):
        item["score"] = 10
        item["passed"] = True
        item["reason"] = f"title '{title}' is acceptable"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = f"unexpected title '{title}'"
    results.append(item)
    total_score += item["score"]

    # 7. 检查 scenarios 数组存在且包含正确数目 (10分)
    scenarios = data.get("scenarios", [])
    item = {"item": "scenarios array has exactly 2 entries", "max_score": 10}
    if isinstance(scenarios, list) and len(scenarios) == 2:
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "found 2 scenarios (sc_01 and sc_02)"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = f"found {len(scenarios)} entries, expected 2"
    results.append(item)
    total_score += item["score"]

    # 8. 检查每个场景的内容 (15分)
    item = {"item": "scenario entries contain correct id, title, status", "max_score": 15}
    required_scenarios = {
        "sc_01": {"title": "Login crash", "status": "failed"},
        "sc_02": {"title": "Data not saved", "status": "failed"}
    }
    score = 0
    reason = ""
    if isinstance(scenarios, list):
        for sc in scenarios:
            sid = sc.get("scenario_id")
            if sid in required_scenarios:
                expected = required_scenarios[sid]
                if sc.get("title") == expected["title"] and sc.get("status") == expected["status"]:
                    score += 7.5  # 每个正确7.5
                else:
                    reason += f"mismatch for {sid}; "
            else:
                reason += f"unexpected scenario {sid}; "
    else:
        reason = "scenarios is not a list"
    if score == 15:
        reason = "both scenarios correct"
    item["score"] = int(score)
    item["passed"] = score == 15
    item["reason"] = reason
    results.append(item)
    total_score += int(score)

    # 9. 检查 status 字段 (10分)
    item = {"item": "status is 'final'", "max_score": 10}
    if data.get("status") == "final":
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "correct status"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = f"got '{data.get('status')}'"
    results.append(item)
    total_score += item["score"]

    # 10. 检查没有混入其他项目场景 (5分)
    item = {"item": "no scenarios from other projects", "max_score": 5}
    if isinstance(scenarios, list):
        foreign = [s for s in scenarios if s.get("scenario_id") not in ["sc_01","sc_02"]]
        if not foreign:
            item["score"] = 5
            item["passed"] = True
            item["reason"] = "only proj_038 scenarios"
        else:
            item["score"] = 0
            item["passed"] = False
            item["reason"] = f"extra scenarios: {[s.get('scenario_id') for s in foreign]}"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = "scenarios not list"
    results.append(item)
    total_score += item["score"]

    # 写出结果
    write_score(results, total_score)

def write_score(results, total):
    total = min(total, 100)  # 上限100
    out = {
        "total_score": total,
        "details": results
    }
    with open("workplace_score.json", "w") as f:
        json.dump(out, f, indent=2)
    print(f"Verification complete. Total score: {total}/100")

if __name__ == "__main__":
    main()
