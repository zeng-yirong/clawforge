import sys, json, os, pathlib

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    ws = pathlib.Path(workspace)
    details = []
    total_score = 0
    max_total = 100

    # ---------- 1. 检查 archive 目录存在 (10分) ----------
    archive_dir = ws / "archive"
    item = {"item": "archive directory exists", "score": 0, "max_score": 10, "passed": False, "reason": ""}
    if archive_dir.is_dir():
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "archive 目录存在"
    else:
        item["reason"] = "archive 目录不存在"
    details.append(item)
    total_score += item["score"]

    # ---------- 2. 检查 reproduction_ledger.json 文件存在且合法 JSON (10分) ----------
    ledger_file = archive_dir / "reproduction_ledger.json"
    item = {"item": "reproduction_ledger.json exists and is valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": ""}
    if not ledger_file.is_file():
        item["reason"] = "文件不存在"
        details.append(item)
        total_score += 0
        # 如果文件不存在，后续检查无法进行，直接输出结果
        _write_score(details, total_score, max_total, workspace)
        return
    try:
        with open(ledger_file, "r") as f:
            agent_data = json.load(f)
        if not isinstance(agent_data, dict) or "documents" not in agent_data:
            raise ValueError("Missing 'documents' key")
        if not isinstance(agent_data["documents"], list):
            raise ValueError("'documents' is not a list")
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "文件存在且为合法 JSON，包含 documents 列表"
    except Exception as e:
        item["reason"] = f"JSON 解析失败或结构错误: {e}"
    details.append(item)
    total_score += item["score"]

    # ---------- 加载源数据计算预期结果 ----------
    try:
        with open(ws / "data/contacts.json", "r") as f:
            contacts = json.load(f)
        contact_map = {}
        for c in contacts:
            contact_map[c["contact_id"]] = c["name"]
    except:
        contact_map = {}

    try:
        with open(ws / "data/projects/project_docs.json", "r") as f:
            all_docs = json.load(f)
    except:
        all_docs = []

    expected_docs = []
    for doc in all_docs:
        # 条件：status == 'active', title 存在且为字符串且非空
        if doc.get("status") != "active":
            continue
        title = doc.get("title")
        if not isinstance(title, str) or title.strip() == "":
            continue
        cid = doc.get("contact_id", "")
        contact_name = contact_map.get(cid, "Unknown")
        expected_docs.append({
            "doc_id": doc["doc_id"],
            "title": title,
            "contact_name": contact_name
        })

    # ---------- 3. 检查字段完整性 (20分) ----------
    item = {"item": "each document has correct fields (doc_id, title, contact_name) and no extra", "score": 0, "max_score": 20, "passed": False, "reason": ""}
    agent_docs = agent_data["documents"]
    field_errors = 0
    required_keys = {"doc_id", "title", "contact_name"}
    for i, d in enumerate(agent_docs):
        if not isinstance(d, dict):
            field_errors += 1
            continue
        keys = set(d.keys())
        if keys != required_keys:
            field_errors += 1
    if field_errors == 0:
        item["score"] = 20
        item["passed"] = True
        item["reason"] = "所有条目均包含正确字段，无多余字段"
    else:
        item["score"] = max(0, 20 - field_errors * 5)  # 每错一个扣5分
        item["reason"] = f"有 {field_errors} 个条目字段不符合要求"
    details.append(item)
    total_score += item["score"]

    # ---------- 4. 筛选正确性 (30分) ----------
    item = {"item": "only active documents with valid title are included", "score": 0, "max_score": 30, "passed": False, "reason": ""}
    # 转换为可比较的 set（每个转为 sorted tuple）
    def doc_to_tuple(d):
        return (d["doc_id"], d["title"], d["contact_name"])
    agent_set = set()
    for d in agent_docs:
        try:
            agent_set.add(doc_to_tuple(d))
        except:
            pass
    expected_set = set()
    for d in expected_docs:
        expected_set.add(doc_to_tuple(d))

    # 多余条目
    extra = agent_set - expected_set
    # 缺失条目
    missing = expected_set - agent_set

    if len(extra) == 0 and len(missing) == 0 and len(agent_set) == len(expected_set):
        item["score"] = 30
        item["passed"] = True
        item["reason"] = "筛选完全正确，无多余/缺失条目"
    else:
        score = 30
        score -= len(extra) * 6   # 每个多余扣6分
        score -= len(missing) * 6 # 每个缺失扣6分
        score = max(0, score)
        item["score"] = score
        item["reason"] = f"余 {len(extra)} 个多余条目，缺 {len(missing)} 个条目"
    details.append(item)
    total_score += item["score"]

    # ---------- 5. 联系人匹配正确性 (30分) ----------
    item = {"item": "contact_name matches expected per document", "score": 0, "max_score": 30, "passed": False, "reason": ""}
    match_errors = 0
    for d in agent_docs:
        try:
            key = doc_to_tuple(d)
        except:
            match_errors += 1
            continue
        if key not in expected_set:
            match_errors += 1  # 已经作为多余扣分，这里不再重复扣，但可以标记
            continue
        # 验证 contact_name 正确（已经在 expected_set 中）
    # 由于我们已经用集合比较过，这里只需要检查所有 agent 条目是否在 expected_set 中，但接触点已经在筛选正确性中扣过分。
    # 因此这里只检查那些在 expected_set 中的条目其 contact_name 是否正确（实际已包含，因为 expected_set 保证正确）
    # 所以我们直接给满分，除非有 agent 条目在 expected_set 中但 contact_name 不同（不可能，因为集合相同）
    # 但为了处理极端情况，我们再次遍历 agent 并检查 contact_name
    wrong_contact = 0
    for d in agent_docs:
        if d.get("doc_id") in {e["doc_id"] for e in expected_docs}:
            exp_contact = next((e["contact_name"] for e in expected_docs if e["doc_id"] == d.get("doc_id")), None)
            if exp_contact is not None and d.get("contact_name") != exp_contact:
                wrong_contact += 1
    if wrong_contact == 0:
        item["score"] = 30
        item["passed"] = True
        item["reason"] = "所有联系人姓名正确"
    else:
        score = max(0, 30 - wrong_contact * 10)
        item["score"] = score
        item["reason"] = f"有 {wrong_contact} 个条目联系人姓名错误"
    details.append(item)
    total_score += item["score"]

    # ---------- 输出总分 ----------
    _write_score(details, total_score, max_total, workspace)

def _write_score(details, total, max_total, workspace):
    result = {
        "total_score": total,
        "details": details
    }
    score_path = pathlib.Path(workspace) / "workplace_score.json"
    with open(score_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Verification complete. Score: {total}/{max_total}")

if __name__ == "__main__":
    main()
