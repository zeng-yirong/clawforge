#!/usr/bin/env python3
import sys
import json
from pathlib import Path

def load_json(path):
    with open(path) as f:
        return json.load(f)

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    ws = Path(workspace)

    details = []
    total = 0

    # 1. File existence (10 points)
    target = ws / "ops" / "updated_labels.json"
    if target.exists():
        details.append({"item": "产物文件存在", "score": 10, "max_score": 10, "passed": True, "reason": "ops/updated_labels.json 存在"})
        total += 10
    else:
        details.append({"item": "产物文件存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        _write_score(ws, total, details)
        return

    # 2. JSON validity (10 points)
    try:
        data = load_json(target)
        details.append({"item": "JSON合法", "score": 10, "max_score": 10, "passed": True, "reason": "JSON解析成功"})
        total += 10
    except Exception as e:
        details.append({"item": "JSON合法", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {e}"})
        _write_score(ws, total, details)
        return

    # 3. Structure correctness (10 points)
    if isinstance(data, dict) and "updated_labels" in data and isinstance(data["updated_labels"], list):
        details.append({"item": "结构正确（包含updated_labels列表）", "score": 10, "max_score": 10, "passed": True, "reason": "包含updated_labels"})
        total += 10
    else:
        details.append({"item": "结构正确", "score": 0, "max_score": 10, "passed": False, "reason": "缺少updated_labels或不是列表"})

    # 4. All required customers present (10 points)
    expected_ids = {"CP001", "LF001", "NT001"}
    actual_ids = set()
    for entry in data.get("updated_labels", []):
        if "customer_id" in entry:
            actual_ids.add(entry["customer_id"])
    if actual_ids == expected_ids:
        details.append({"item": "包含所有客户", "score": 10, "max_score": 10, "passed": True, "reason": "客户ID集合一致"})
        total += 10
    else:
        missing = expected_ids - actual_ids
        extra = actual_ids - expected_ids
        reason = f"缺失: {missing}, 多余: {extra}" if missing or extra else ""
        details.append({"item": "包含所有客户", "score": 0, "max_score": 10, "passed": False, "reason": reason})

    # 5. Load rules & source data
    try:
        rules = load_json(ws / "ops" / "tier_rules.json")
        activity = load_json(ws / "data" / "logs" / "activity_logs.json")["activity_logs"]
        consumption = load_json(ws / "data" / "logs" / "consumption_logs.json")["consumption_logs"]
    except Exception as e:
        details.append({"item": "读取规则和数据", "score": 0, "max_score": 0, "passed": False, "reason": f"读取失败: {e}"})
        _write_score(ws, total, details)
        return

    act_map = {a["customer_id"]: a for a in activity}
    cons_map = {c["customer_id"]: c for c in consumption}

    def compute_labels(cid):
        labels = []
        act = act_map.get(cid)
        cons = cons_map.get(cid)
        for rule in rules:
            if rule.get("default"):
                continue
            cond = rule["conditions"]
            ok = True
            if "quarter_spend_usd_ge" in cond:
                if cons is None or cons["quarter_spend_usd"] < cond["quarter_spend_usd_ge"]:
                    ok = False
            if "last_active_days_le" in cond:
                if act is None or act["last_active_days"] > cond["last_active_days_le"]:
                    ok = False
            if "quarter_spend_usd_lt" in cond:
                if cons is None or cons["quarter_spend_usd"] >= cond["quarter_spend_usd_lt"]:
                    ok = False
            if "last_active_days_gt" in cond:
                if act is None or act["last_active_days"] <= cond["last_active_days_gt"]:
                    ok = False
            if "risk_level" in cond:
                if act is None or act["risk_level"] != cond["risk_level"]:
                    ok = False
            if ok:
                labels.append(rule["label"])
        if not labels:
            for rule in rules:
                if rule.get("default"):
                    labels.append(rule["label"])
        return labels

    expected = {cid: compute_labels(cid) for cid in expected_ids}

    # 6-8. Per-customer label checks (20 points each, total 60)
    for cid in expected_ids:
        entry = next((e for e in data.get("updated_labels", []) if e.get("customer_id") == cid), None)
        if entry is None:
            details.append({"item": f"客户{cid}标签", "score": 0, "max_score": 20, "passed": False, "reason": "缺失"})
        else:
            actual = entry.get("labels", [])
            exp = expected[cid]
            if set(actual) == set(exp):
                details.append({"item": f"客户{cid}标签", "score": 20, "max_score": 20, "passed": True, "reason": f"标签正确: {exp}"})
                total += 20
            else:
                details.append({"item": f"客户{cid}标签", "score": 0, "max_score": 20, "passed": False, "reason": f"预期{exp}，实际{actual}"})

    # 9. No extra fields (10 points)
    has_extra = False
    for entry in data.get("updated_labels", []):
        for key in entry:
            if key not in ("customer_id", "labels"):
                has_extra = True
                break
        if has_extra:
            break
    if not has_extra:
        details.append({"item": "无多余字段", "score": 10, "max_score": 10, "passed": True, "reason": "仅包含customer_id和labels"})
        total += 10
    else:
        details.append({"item": "无多余字段", "score": 0, "max_score": 10, "passed": False, "reason": "包含额外字段"})

    # Write final score
    _write_score(ws, total, details)

def _write_score(ws, total, details):
    result = {"total_score": total, "details": details}
    with open(ws / "workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
