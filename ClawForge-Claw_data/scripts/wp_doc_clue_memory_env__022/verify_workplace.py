import sys
import os
import json

def _write_score(total, details, workspace):
    result = {"total_score": total, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

def verify(workspace):
    score = 0
    details = []

    def add_item(name, sc, max_sc, passed, reason):
        details.append({"item": name, "score": sc, "max_score": max_sc, "passed": passed, "reason": reason})
        return sc

    # 1. 文件存在
    target_path = os.path.join(workspace, "ops", "target_clues.json")
    if not os.path.isfile(target_path):
        add_item("靶文件存在", 0, 5, False, "ops/target_clues.json 不存在")
        _write_score(score, details, workspace)
        return
    score += add_item("靶文件存在", 5, 5, True, "文件已创建")

    # 2. JSON合法且为列表
    try:
        with open(target_path, "r") as f:
            clues = json.load(f)
    except:
        add_item("JSON格式", 0, 5, False, "无法解析")
        _write_score(score, details, workspace)
        return
    if not isinstance(clues, list):
        add_item("JSON格式", 0, 5, False, "顶层不是列表")
        _write_score(score, details, workspace)
        return
    score += add_item("JSON格式", 5, 5, True, "合法JSON列表")

    # 3. 加载原始数据
    def load_json(rel):
        full = os.path.join(workspace, rel)
        with open(full, "r") as f:
            return json.load(f)
    try:
        reports_data = load_json("reports/reports.json")["reports"]
        presentations_data = load_json("presentations/presentations.json")["presentations"]
        media_data = load_json("media_samples/media_samples.json")["media_samples"]
    except Exception as e:
        add_item("原始数据加载", 0, 5, False, str(e))
        _write_score(score, details, workspace)
        return
    score += add_item("原始数据加载", 5, 5, True, "成功加载")

    # 4. 构建期望答案
    target = "HelioSync Edge Inference Fabric"
    expected = []
    for r in reports_data:
        if target in r.get("solution_aliases", []):
            expected.append({"type": "report", "id": r["id"], "title": r["title"], "clue": r["summary"]})
    for p in presentations_data:
        if target in p.get("solution_aliases", []):
            expected.append({"type": "presentation", "id": p["id"], "title": p["title"], "clue": p["summary"]})
    for m in media_data:
        if target in m.get("solution_aliases", []):
            expected.append({"type": "media_sample", "id": m["id"], "title": m["title"], "clue": m["summary"]})

    # 5. 条目数量
    if len(clues) == len(expected):
        score += add_item("条目数量", 10, 10, True, f"期望{len(expected)}条，实际{len(clues)}条")
    else:
        score += add_item("条目数量", 0, 10, False, f"期望{len(expected)}条，实际{len(clues)}条")

    # 6. 无多余/缺失
    exp_by_id = {e["id"]: e for e in expected}
    act_by_id = {c["id"]: c for c in clues if "id" in c}
    missing = set(exp_by_id.keys()) - set(act_by_id.keys())
    extra = set(act_by_id.keys()) - set(exp_by_id.keys())
    if not missing and not extra:
        score += add_item("无缺失无多余", 10, 10, True, "ID集合完全匹配")
    else:
        reason = ""
        if missing:
            reason += f"缺失ID: {missing}. "
        if extra:
            reason += f"多余ID: {extra}. "
        score += add_item("无缺失无多余", 0, 10, False, reason)

    # 7. 每个条目的字段正确性（type, title, clue）
    entry_ok = 0
    entry_total = 0
    for eid, exp in exp_by_id.items():
        act = act_by_id.get(eid)
        if not act:
            continue
        ok = True
        if act.get("type") != exp["type"]:
            ok = False
        if act.get("title") != exp["title"]:
            ok = False
        if act.get("clue") != exp["clue"]:
            ok = False
        if ok:
            entry_ok += 1
        entry_total += 1
    if entry_total > 0:
        entry_score = int(60 * entry_ok / entry_total)  # 60分满
        score += add_item("条目字段正确性", entry_score, 60, entry_ok == entry_total,
                          f"{entry_ok}/{entry_total} 个条目完全正确")
    else:
        add_item("条目字段正确性", 0, 60, False, "没有可检查的条目")

    # 8. 额外扣分项：如果存在不应包含的条目（干扰项）
    # 已通过extra ID检查，但还需检查那些ID在期望中但类型错误的情况（上面已覆盖）
    # 不再重复

    _write_score(score, details, workspace)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
