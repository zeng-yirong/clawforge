import sys
import os
import json

def verify(workspace):
    details = []
    total_score = 0
    max_total = 100

    # 1. 检查 knowledge_base 目录存在 (10分)
    kb = os.path.join(workspace, "knowledge_base")
    if os.path.isdir(kb):
        details.append({"item": "knowledge_base directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "Directory found"})
        total_score += 10
    else:
        details.append({"item": "knowledge_base directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "Directory missing"})

    # 2. 检查 ledger.json 存在 (10分)
    ledger_path = os.path.join(workspace, "knowledge_base", "ledger.json")
    if os.path.isfile(ledger_path):
        details.append({"item": "ledger.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "File found"})
        total_score += 10
    else:
        details.append({"item": "ledger.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "File missing"})
        # 后续检查无意义，直接结束
        return write_score(total_score, details)

    # 3. 解析 JSON 合法性 (10分)
    try:
        with open(ledger_path, "r") as f:
            data = json.load(f)
        details.append({"item": "ledger.json is valid JSON", "score": 10, "max_score": 10, "passed": True, "reason": "Parse success"})
        total_score += 10
    except Exception as e:
        details.append({"item": "ledger.json is valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"Parse error: {e}"})
        return write_score(total_score, details)

    # 4. 检查 data 是否为列表 (5分)
    if isinstance(data, list):
        details.append({"item": "ledger.json root is a list", "score": 5, "max_score": 5, "passed": True, "reason": "Root is list"})
        total_score += 5
    else:
        details.append({"item": "ledger.json root is a list", "score": 0, "max_score": 5, "passed": False, "reason": f"Root is {type(data).__name__}"})

    # 5. 记录数应为 3 (只包含预期的失败场景) (20分)
    expected_ids = {"sc-001", "sc-004", "sc-007"}
    actual_ids = set()
    for rec in data:
        if isinstance(rec, dict) and "scenario_id" in rec:
            actual_ids.add(rec["scenario_id"])
    if actual_ids == expected_ids:
        details.append({"item": "Failed scenarios count and IDs correct", "score": 20, "max_score": 20, "passed": True, "reason": f"Got {actual_ids}"})
        total_score += 20
    elif len(actual_ids) == 0:
        details.append({"item": "Failed scenarios count and IDs correct", "score": 0, "max_score": 20, "passed": False, "reason": "Empty list"})
    else:
        # 部分正确，根据交集大小给分
        correct = len(actual_ids & expected_ids)
        extra = len(actual_ids - expected_ids)
        score = min(20, correct * 5)  # 每个正确ID给5分，最多20
        if extra > 0:
            score = max(0, score - extra * 2)  # 每个多余ID扣2分
        details.append({"item": "Failed scenarios count and IDs correct", "score": max(0, score), "max_score": 20, "passed": score == 20, "reason": f"Expected {expected_ids}, got {actual_ids}, extra {extra}"})
        total_score += max(0, score)

    # 6. 检查每个记录必含字段: scenario_id, project_id, error, doc_path (15分)
    required_fields = ["scenario_id", "project_id", "error", "doc_path"]
    field_ok = 0
    for i, rec in enumerate(data):
        if not isinstance(rec, dict):
            continue
        if all(f in rec for f in required_fields):
            field_ok += 1
    if field_ok == len(data):
        details.append({"item": "All records contain required fields", "score": 15, "max_score": 15, "passed": True, "reason": f"{len(data)} records all have fields"})
        total_score += 15
    else:
        details.append({"item": "All records contain required fields", "score": 0, "max_score": 15, "passed": False, "reason": f"Only {field_ok}/{len(data)} records have all fields"})

    # 7. 校验每个记录的数据是否与原始场景一致 (20分)
    # 读取原始场景 manifest.json 和 sc-020.yaml（但yaml我们用文本读取）
    manifest_path = os.path.join(workspace, "scenarios", "manifest.json")
    yaml_path = os.path.join(workspace, "scenarios", "sc-020.yaml")
    original = {}
    if os.path.isfile(manifest_path):
        with open(manifest_path) as f:
            manifest = json.load(f)
        for rec in manifest:
            sid = rec.get("scenario_id")
            if sid:
                original[sid] = rec
    # 读取 yaml 简单解析 (不依赖yaml库)
    if os.path.isfile(yaml_path):
        with open(yaml_path) as f:
            lines = f.read().splitlines()
        yaml_rec = {}
        for line in lines:
            if ":" in line:
                k, v = line.split(":", 1)
                yaml_rec[k.strip()] = v.strip()
        if "scenario_id" in yaml_rec:
            original[yaml_rec["scenario_id"]] = yaml_rec

    # 只检查预期ID的记录
    mismatch = False
    for rec in data:
        sid = rec.get("scenario_id")
        if sid in expected_ids:
            orig = original.get(sid, {})
            # 检查 project_id 和 doc_path 匹配
            if rec.get("project_id") != orig.get("project_id"):
                mismatch = True
            if rec.get("doc_path") != orig.get("doc_path"):
                mismatch = True
            # 检查 error 非空
            if not rec.get("error"):
                mismatch = True
    if not mismatch and len(data) == 3:
        details.append({"item": "Data accuracy verified against original scenarios", "score": 20, "max_score": 20, "passed": True, "reason": "All fields match"})
        total_score += 20
    else:
        details.append({"item": "Data accuracy verified against original scenarios", "score": 0, "max_score": 20, "passed": False, "reason": "Field mismatch or missing error"})

    # 8. 没有多余的错误场景（比如误包含SUCCESS或_old） (10分)
    extra_bad = 0
    for rec in data:
        sid = rec.get("scenario_id")
        if sid and ("_old" in sid or sid not in expected_ids):
            extra_bad += 1
    if extra_bad == 0:
        details.append({"item": "No old or non-failed scenarios included", "score": 10, "max_score": 10, "passed": True, "reason": "Clean data"})
        total_score += 10
    else:
        details.append({"item": "No old or non-failed scenarios included", "score": 0, "max_score": 10, "passed": False, "reason": f"Found {extra_bad} unwanted records"})

    return write_score(total_score, details)

def write_score(total, details):
    # 确保总分不超过100
    total = min(total, 100)
    result = {
        "total_score": total,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))
    return result

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    os.chdir(workspace)
    verify(workspace)
