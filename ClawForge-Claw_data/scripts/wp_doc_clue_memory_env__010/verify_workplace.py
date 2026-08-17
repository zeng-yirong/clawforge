"""
verify_workplace.py – Pure code validation for wp_doc_clue_memory_env__010
No external imports, no LLM. Scored 0–100.
"""
import sys, os, json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    # 1. 目录结构存在 (10 points)
    dirs_required = ["ops", "data/reports", "data/presentations", "data/media_samples", "data/attachments"]
    all_dirs_exist = all(os.path.isdir(os.path.join(workspace, d)) for d in dirs_required)
    if all_dirs_exist:
        score += 10
        details.append({"item": "Required directories exist", "score": 10, "max_score": 10,
                        "passed": True, "reason": "ops, data/* subdirs found"})
    else:
        details.append({"item": "Required directories exist", "score": 0, "max_score": 10,
                        "passed": False, "reason": "Missing directories"})

    # 2. target_clues.json 存在 (10 points)
    clues_path = os.path.join(workspace, "ops/target_clues.json")
    if os.path.isfile(clues_path):
        score += 10
        details.append({"item": "target_clues.json exists", "score": 10, "max_score": 10,
                        "passed": True, "reason": "file found"})
    else:
        details.append({"item": "target_clues.json exists", "score": 0, "max_score": 10,
                        "passed": False, "reason": "file not found"})
        # 无法继续评分
        _write_score(score, details, workspace)
        return

    # 3. JSON 格式合法 (10 points)
    try:
        with open(clues_path, "r") as f:
            data = json.load(f)
        if isinstance(data, list):
            score += 10
            details.append({"item": "Valid JSON list", "score": 10, "max_score": 10,
                            "passed": True, "reason": "parsed as list"})
        else:
            score += 0
            details.append({"item": "Valid JSON list", "score": 0, "max_score": 10,
                            "passed": False, "reason": "not a list"})
            _write_score(score, details, workspace)
            return
    except (json.JSONDecodeError, Exception) as e:
        details.append({"item": "Valid JSON list", "score": 0, "max_score": 10,
                        "passed": False, "reason": str(e)})
        _write_score(score, details, workspace)
        return

    # 4. 每条记录包含必须字段 id, title, type (10 points)
    required_fields = {"id", "title", "type"}
    valid_types = {"report", "presentation", "media_sample"}
    all_have_fields = True
    for entry in data:
        if not isinstance(entry, dict):
            all_have_fields = False
            break
        if not required_fields.issubset(entry.keys()):
            all_have_fields = False
            break
        if entry.get("type") not in valid_types:
            all_have_fields = False
            break
    if all_have_fields and len(data) > 0:
        score += 10
        details.append({"item": "Required fields present", "score": 10, "max_score": 10,
                        "passed": True, "reason": f"all {len(data)} entries have id,title,type"})
    else:
        details.append({"item": "Required fields present", "score": 0, "max_score": 10,
                        "passed": False, "reason": "missing fields or invalid type"})
        _write_score(score, details, workspace)
        return

    # 5. 正确匹配的数量和记录 (30 points)
    # 预期正确的记录:
    expected = [
        {"id": "rpt_001", "title": "Industrial Edge Inference Landscape 2026", "type": "report"},
        {"id": "rpt_003", "title": "Logistics AI Summit Report", "type": "report"},
        {"id": "rpt_005", "title": "Inference Fabric for Autonomous Robots", "type": "report"},
        {"id": "pres_001", "title": "Partner Marketing Q2 Deck", "type": "presentation"},
        {"id": "pres_003", "title": "Inference Fabric Roadmap 2026", "type": "presentation"},
        {"id": "sample_002", "title": "Keynote: HelioSync Fabric Launch", "type": "media_sample"},
    ]
    # 构建集合比较
    actual_entries = {(e["id"], e["title"], e["type"]) for e in data}
    expected_entries = {(e["id"], e["title"], e["type"]) for e in expected}
    correct_hits = actual_entries.intersection(expected_entries)
    false_positives = actual_entries - expected_entries
    false_negatives = expected_entries - actual_entries

    if len(correct_hits) == len(expected) and len(false_positives) == 0:
        score += 30
        details.append({"item": "Accurate clue matching", "score": 30, "max_score": 30,
                        "passed": True, "reason": f"All {len(expected)} expected entries present, no extraneous"})
    else:
        # 部分得分
        per_entry = 5  # 每个正确的5分,最多30
        match_score = min(len(correct_hits) * 5, 30)
        if false_negatives:
            match_score = max(0, match_score - 2 * len(false_negatives))  # 每个缺少扣2分
        if false_positives:
            match_score = max(0, match_score - 2 * len(false_positives))
        score += match_score
        details.append({"item": "Accurate clue matching", "score": match_score, "max_score": 30,
                        "passed": match_score >= 20,
                        "reason": f"Correct: {len(correct_hits)}, Missing: {len(false_negatives)}, Extra: {len(false_positives)}"})

    # 6. 没有包含干扰记录 (20 points) 额外检查不包含干扰ID
    forbidden_ids = {"rpt_002", "rpt_004", "pres_002", "sample_001", "sample_003"}
    has_forbidden = any(e["id"] in forbidden_ids for e in data)
    if not has_forbidden:
        score += 20
        details.append({"item": "No distractor entries", "score": 20, "max_score": 20,
                        "passed": True, "reason": "No forbidden IDs found"})
    else:
        score += 0
        details.append({"item": "No distractor entries", "score": 0, "max_score": 20,
                        "passed": False, "reason": f"Contains distractor IDs"})

    # 7. 额外：不允许无关字段检查 (10 points) 可选，但作为奖励
    allowed_fields = {"id", "title", "type"}
    extra_fields_count = 0
    for e in data:
        extra = set(e.keys()) - allowed_fields
        if extra:
            extra_fields_count += 1
    if extra_fields_count == 0:
        score += 10
        details.append({"item": "No extraneous fields", "score": 10, "max_score": 10,
                        "passed": True, "reason": "Only id, title, type present"})
    else:
        score += 0
        details.append({"item": "No extraneous fields", "score": 0, "max_score": 10,
                        "passed": False, "reason": f"{extra_fields_count} entries have extra fields"})

    # 确保总分上限100
    score = min(score, 100)
    _write_score(score, details, workspace)

def _write_score(total, details, workspace):
    out_path = os.path.join(workspace, "workplace_score.json")
    with open(out_path, "w") as f:
        json.dump({"total_score": total, "details": details}, f, indent=2)
    print(f"Score written: {total}/100")

if __name__ == "__main__":
    main()
