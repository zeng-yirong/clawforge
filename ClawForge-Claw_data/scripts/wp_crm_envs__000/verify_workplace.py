import sys
import json
import pathlib

def verify(workspace: str):
    ws = pathlib.Path(workspace)
    score_details = []
    total_score = 0

    # ---------- 1. ops 目录存在 (10分) ----------
    ops_dir = ws / "ops"
    item = {"item": "ops目录存在", "score": 0, "max_score": 10, "passed": False, "reason": ""}
    if ops_dir.is_dir():
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "ops/ 目录存在"
    else:
        item["reason"] = "缺少 ops/ 目录"
    score_details.append(item)
    total_score += item["score"]

    # ---------- 2. add_tags.json 文件存在 (10分) ----------
    out_file = ops_dir / "add_tags.json"
    item = {"item": "add_tags.json 文件存在", "score": 0, "max_score": 10, "passed": False, "reason": ""}
    if out_file.is_file():
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "ops/add_tags.json 存在"
    else:
        item["reason"] = "缺少 ops/add_tags.json"
    score_details.append(item)
    total_score += item["score"]

    # ---------- 3. JSON 格式合法 (10分) ----------
    item = {"item": "JSON 格式合法", "score": 0, "max_score": 10, "passed": False, "reason": ""}
    if out_file.is_file():
        try:
            with open(out_file, "r") as f:
                data = json.load(f)
            item["score"] = 10
            item["passed"] = True
            item["reason"] = "JSON 解析成功"
        except (json.JSONDecodeError, Exception) as e:
            item["reason"] = f"JSON 解析失败: {str(e)}"
    else:
        item["reason"] = "文件不存在，跳过格式检查"
    score_details.append(item)
    total_score += item["score"]

    # ---------- 4. 内容正确性 (70分) ----------
    # 首先读取原始联系人数据，确定理论上的正确结果
    contacts_file = ws / "data" / "contacts.json"
    companies_file = ws / "data" / "companies.json"
    correct_entries = []
    error_reason = ""

    if not contacts_file.is_file() or not companies_file.is_file():
        error_reason = "缺少原始数据文件 data/contacts.json 或 data/companies.json"
        item = {"item": "内容正确性", "score": 0, "max_score": 70, "passed": False, "reason": error_reason}
        score_details.append(item)
        total_score += 0
    else:
        with open(contacts_file, "r") as f:
            contacts = json.load(f)
        with open(companies_file, "r") as f:
            companies = json.load(f)
        # 查找 TechCorp Industries 的 company_id
        techcorp_id = None
        for c in companies:
            if c["name"] == "TechCorp Industries":
                techcorp_id = c["company_id"]
                break
        if techcorp_id is None:
            error_reason = "未找到 TechCorp Industries 公司"
        else:
            # 筛选属于 TechCorp 且 tags 中不包含 "tech_partner" 的联系人
            target_contacts = []
            for ct in contacts:
                if ct.get("company_id") == techcorp_id and "tech_partner" not in ct.get("tags", []):
                    target_contacts.append(ct["contact_id"])
            # 构造预期输出（按 ID 排序以忽略顺序）
            correct_entries = sorted([{"contact_id": cid, "tags_to_add": ["tech_partner"]} for cid in target_contacts], key=lambda x: x["contact_id"])

            # 读取 agent 的输出
            try:
                with open(out_file, "r") as f:
                    agent_data = json.load(f)
                # 验证是列表
                if not isinstance(agent_data, list):
                    raise ValueError("输出不是列表")
                # 验证每个元素含有 contact_id 和 tags_to_add
                for entry in agent_data:
                    if not isinstance(entry, dict) or "contact_id" not in entry or "tags_to_add" not in entry:
                        raise ValueError("条目缺少 contact_id 或 tags_to_add")
                # 对 agent 输出排序后比较
                agent_sorted = sorted(agent_data, key=lambda x: x["contact_id"])
                # 比较
                if agent_sorted == correct_entries:
                    item = {"item": "内容正确性", "score": 70, "max_score": 70, "passed": True, "reason": "精确匹配"}
                else:
                    item = {"item": "内容正确性", "score": 0, "max_score": 70, "passed": False,
                            "reason": f"预期 {correct_entries}，实际 {agent_sorted}"}
            except Exception as e:
                item = {"item": "内容正确性", "score": 0, "max_score": 70, "passed": False,
                        "reason": f"读取或验证输出时出错: {str(e)}"}
        score_details.append(item)
        total_score += item["score"]

    # 写入评分文件
    result = {
        "total_score": min(total_score, 100),  # 防止溢出
        "details": score_details
    }
    with open(ws / "workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

    print(f"评分完成：{result['total_score']}/100")

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
