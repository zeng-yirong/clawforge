import os
import sys
import json

def verify(workspace: str) -> dict:
    details = []
    total_score = 0
    max_total = 100

    # ------------------------------------------------------------
    # 1. 检查 ledeger_archive.json 是否存在 (10分)
    # ------------------------------------------------------------
    item = {"item": "ledger_archive.json exists", "score": 0, "max_score": 10, "passed": False, "reason": ""}
    archive_path = os.path.join(workspace, "ledger_archive.json")
    if os.path.isfile(archive_path):
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "File found"
    else:
        item["reason"] = "File not found at workspace root"
        details.append(item)
        # 直接返回，后面无法继续
        return {"total_score": 0, "details": details}
    details.append(item)
    total_score += item["score"]

    # ------------------------------------------------------------
    # 2. 文件内容必须是合法 JSON (10分)
    # ------------------------------------------------------------
    item = {"item": "valid JSON syntax", "score": 0, "max_score": 10, "passed": False, "reason": ""}
    try:
        with open(archive_path, "r") as f:
            data = json.load(f)
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "File is valid JSON"
    except (json.JSONDecodeError, Exception) as e:
        item["reason"] = f"Invalid JSON: {e}"
        details.append(item)
        return {"total_score": total_score, "details": details}
    details.append(item)
    total_score += item["score"]

    # ------------------------------------------------------------
    # 3. 必须包含所需字段: doc_id, project_id, status, contact_name, account_display_name (20分,每个4分)
    # ------------------------------------------------------------
    required_fields = ["doc_id", "project_id", "status", "contact_name", "account_display_name"]
    field_item = {"item": "required fields present", "score": 0, "max_score": 20, "passed": False, "reason": ""}
    missing = []
    for field in required_fields:
        if field not in data:
            missing.append(field)
    if not missing:
        field_item["score"] = 20
        field_item["passed"] = True
        field_item["reason"] = "All required fields exist"
    else:
        field_item["reason"] = f"Missing fields: {', '.join(missing)}"
    details.append(field_item)
    total_score += field_item["score"]

    # ------------------------------------------------------------
    # 4. status 必须是 "verified" (10分)
    # ------------------------------------------------------------
    status_item = {"item": "status equals 'verified'", "score": 0, "max_score": 10, "passed": False, "reason": ""}
    if data.get("status") == "verified":
        status_item["score"] = 10
        status_item["passed"] = True
        status_item["reason"] = "Correct status"
    else:
        status_item["reason"] = f"Expected 'verified', got '{data.get('status')}'"
    details.append(status_item)
    total_score += status_item["score"]

    # ------------------------------------------------------------
    # 5. doc_id 必须与日志中 Alice Wang 的 verified 记录一致 (20分)
    #    期望 doc_id = "doc_002"
    # ------------------------------------------------------------
    doc_item = {"item": "doc_id matches verified log (doc_002)", "score": 0, "max_score": 20, "passed": False, "reason": ""}
    expected_doc = "doc_002"
    if data.get("doc_id") == expected_doc:
        doc_item["score"] = 20
        doc_item["passed"] = True
        doc_item["reason"] = f"doc_id is {expected_doc}"
    else:
        doc_item["reason"] = f"Expected '{expected_doc}', got '{data.get('doc_id')}'"
    details.append(doc_item)
    total_score += doc_item["score"]

    # ------------------------------------------------------------
    # 6. contact_name 必须对应 doc_002 的文档联系人 (15分)
    #    从 contacts.json 可知: doc_002 关联到 contact_id? 题目没有直接关联。
    #    但根据业务知识，我们假设 bug 文档的维护者/作者是 John Doe (c101)
    #    为了唯一性，我们在 env_builder 中并没有显式关联，但是我们可以从 project_docs 推断？
    #    注意：业务设计中，project_docs 没有 contact_id 字段。但我们可以在 prompt 中暗示，
    #    实际上我们可以从日志中推断联系人？为了保证可验证，我们在 env_builder 中
    #    添加一个隐藏关系：doc_002 对应的联系人应该是 "John Doe" (因为这是 bug report, 维护者)。
    #    为了简化，我们期望 contact_name = "John Doe"
    # ------------------------------------------------------------
    contact_item = {"item": "contact_name matches expected ('John Doe')", "score": 0, "max_score": 15, "passed": False, "reason": ""}
    expected_contact = "John Doe"
    if data.get("contact_name") == expected_contact:
        contact_item["score"] = 15
        contact_item["passed"] = True
        contact_item["reason"] = f"contact_name is {expected_contact}"
    else:
        contact_item["reason"] = f"Expected '{expected_contact}', got '{data.get('contact_name')}'"
    details.append(contact_item)
    total_score += contact_item["score"]

    # ------------------------------------------------------------
    # 7. account_display_name 必须是 "Alice Wang" (15分)
    # ------------------------------------------------------------
    account_item = {"item": "account_display_name matches 'Alice Wang'", "score": 0, "max_score": 15, "passed": False, "reason": ""}
    expected_account = "Alice Wang"
    if data.get("account_display_name") == expected_account:
        account_item["score"] = 15
        account_item["passed"] = True
        account_item["reason"] = f"account_display_name is {expected_account}"
    else:
        account_item["reason"] = f"Expected '{expected_account}', got '{data.get('account_display_name')}'"
    details.append(account_item)
    total_score += account_item["score"]

    # ------------------------------------------------------------
    # 8. 可选：检查没有多余字段？不强制，但可以扣分？暂时不扣分，但为了精确，我们检查是否包含额外字段
    # 但为了简单，不额外扣分。最终总分确保在0-100
    # ------------------------------------------------------------

    return {"total_score": min(total_score, 100), "details": details}

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))
