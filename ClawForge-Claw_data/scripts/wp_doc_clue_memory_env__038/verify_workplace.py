"""
Verify the agent's clue list output for wp_doc_clue_memory_env__038.
Checks existence, JSON validity, structure, completeness, and snippet accuracy.
"""

import sys
import json
from pathlib import Path

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    ws = Path(workspace)
    details = []
    total_score = 0

    # ---------- 1. 输出文件是否存在 ----------
    output_path = ws / "ops" / "collected_clues.json"
    if not output_path.exists():
        details.append({"item": "output file exists", "score": 0, "max_score": 10, "passed": False, "reason": "ops/collected_clues.json not found"})
        _write_score(details, 0)
        return
    details.append({"item": "output file exists", "score": 10, "max_score": 10, "passed": True, "reason": "file found"})

    # ---------- 2. JSON 合法性 ----------
    try:
        data = json.loads(output_path.read_text())
    except Exception as e:
        details.append({"item": "valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON parse error: {e}"})
        _write_score(details, 0)
        return

    if not isinstance(data, dict) or "clues" not in data:
        details.append({"item": "JSON structure", "score": 0, "max_score": 10, "passed": False, "reason": "missing top-level 'clues' key"})
        _write_score(details, 0)
        return

    clues = data["clues"]
    if not isinstance(clues, list):
        details.append({"item": "JSON structure", "score": 0, "max_score": 10, "passed": False, "reason": "'clues' is not a list"})
        _write_score(details, 0)
        return

    # 检查每个线索对象的结构
    valid_sources = {"report", "presentation", "media_sample"}
    structure_ok = True
    for i, clue in enumerate(clues):
        if not isinstance(clue, dict):
            structure_ok = False
            break
        if not all(k in clue for k in ("source", "id", "snippet")):
            structure_ok = False
            break
        if clue["source"] not in valid_sources:
            structure_ok = False
            break

    if not structure_ok:
        details.append({"item": "clue object structure", "score": 0, "max_score": 10, "passed": False, "reason": "one or more clues missing required fields or have invalid source"})
        _write_score(details, 0)
        return
    details.append({"item": "JSON structure", "score": 10, "max_score": 10, "passed": True, "reason": "all clues have correct fields"})

    # ---------- 3. 计算预期答案 ----------
    expected = []

    # 报告
    rpath = ws / "data" / "reports" / "reports.json"
    if rpath.exists():
        rdata = json.loads(rpath.read_text())
        for rec in rdata.get("reports", []):
            aliases = rec.get("solution_aliases")
            if isinstance(aliases, list) and "HelioSync Edge Inference Fabric" in aliases:
                expected.append({"source": "report", "id": rec["report_id"], "snippet": rec.get("summary", "")})

    # 演示文稿
    ppath = ws / "data" / "presentations" / "presentations.json"
    if ppath.exists():
        pdata = json.loads(ppath.read_text())
        for rec in pdata.get("presentations", []):
            aliases = rec.get("solution_aliases")
            if isinstance(aliases, list) and "HelioSync Edge Inference Fabric" in aliases:
                expected.append({"source": "presentation", "id": rec["presentation_id"], "snippet": rec.get("summary", "")})

    # 媒体样本
    mpath = ws / "data" / "media_samples" / "media_samples.json"
    if mpath.exists():
        mdata = json.loads(mpath.read_text())
        for rec in mdata.get("media_samples", []):
            aliases = rec.get("solution_aliases")
            if isinstance(aliases, list) and "HelioSync Edge Inference Fabric" in aliases:
                expected.append({"source": "media_sample", "id": rec["sample_id"], "snippet": rec.get("summary", "")})

    # 构建 agent 提供的映射
    agent_map = {}
    seen = set()
    duplicate_flag = False
    for clue in clues:
        key = (clue["source"], clue["id"])
        if key in seen:
            duplicate_flag = True
        seen.add(key)
        agent_map[key] = clue["snippet"]

    # duplicate 检查 10分
    if duplicate_flag:
        details.append({"item": "no duplicate clues", "score": 0, "max_score": 10, "passed": False, "reason": "duplicate clue entries found"})
    else:
        details.append({"item": "no duplicate clues", "score": 10, "max_score": 10, "passed": True, "reason": "no duplicates"})

    # ---------- 4. 线索集合完整性 ----------
    missing = []
    extra = []
    expected_set = {(e["source"], e["id"]) for e in expected}
    for exp in expected:
        key = (exp["source"], exp["id"])
        if key not in agent_map:
            missing.append(key)

    for key in agent_map:
        if key not in expected_set:
            extra.append(key)

    correct_set_score = 30
    if missing:
        correct_set_score -= 10 * len(missing)
    if extra:
        correct_set_score -= 10 * len(extra)
    correct_set_score = max(0, correct_set_score)
    details.append({
        "item": "correct clue set",
        "score": correct_set_score,
        "max_score": 30,
        "passed": not missing and not extra,
        "reason": f"missing {missing}, extra {extra}" if missing or extra else "all expected clues present, no extra"
    })

    # ---------- 5. snippet 准确性 ----------
    snippet_max = 30
    snippet_correct = 0
    for exp in expected:
        key = (exp["source"], exp["id"])
        if key in agent_map:
            if agent_map[key] == exp["snippet"]:
                snippet_correct += 1
    snippet_score = snippet_correct * (snippet_max // len(expected)) if expected else 0
    details.append({
        "item": "snippet correctness",
        "score": snippet_score,
        "max_score": snippet_max,
        "passed": snippet_score == snippet_max,
        "reason": f"{snippet_correct}/{len(expected)} snippets matched exactly"
    })

    # ---------- 总分 ----------
    total_score = sum(d["score"] for d in details)
    _write_score(details, total_score)

def _write_score(details, total):
    result = {"total_score": total, "details": details}
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score: {total}")

if __name__ == "__main__":
    main()
