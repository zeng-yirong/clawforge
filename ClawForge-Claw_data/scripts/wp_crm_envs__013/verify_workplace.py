import os
import sys
import json

def verify(workspace: str):
    details = []
    total_score = 0
    max_total = 100

    # 1. 检查结果文件是否存在
    result_path = os.path.join(workspace, "ops/vip_task_result.json")
    if not os.path.isfile(result_path):
        details.append({"item": "结果文件存在", "score": 0, "max_score": 10, "passed": False,
                        "reason": "ops/vip_task_result.json 不存在"})
        # 缺失核心文件，剩余检查无法进行，直接返回
        return {"total_score": 0, "details": details}

    with open(result_path, "r") as f:
        content = f.read()
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        details.append({"item": "结果文件 JSON 合法性", "score": 0, "max_score": 10, "passed": False,
                        "reason": "文件不是合法 JSON"})
        return {"total_score": 0, "details": details}

    details.append({"item": "结果文件存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在且可读"})
    total_score += 10
    details.append({"item": "结果文件 JSON 合法性", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 格式正确"})
    total_score += 10

    # 2. 检查字段存在
    required_keys = ["contact_id", "tag_id"]
    for key in required_keys:
        if key not in data:
            details.append({"item": f"结果文件包含字段 {key}", "score": 0, "max_score": 10, "passed": False,
                            "reason": f"缺少字段 {key}"})
        else:
            details.append({"item": f"结果文件包含字段 {key}", "score": 10, "max_score": 10, "passed": True,
                            "reason": f"字段 {key} 存在"})
            total_score += 10

    if len(details) < 4:  # 前面结构不全时返回
        return {"total_score": total_score, "details": details}

    # 3. contact_id 正确性
    if data.get("contact_id") != "ct_007":
        details.append({"item": "contact_id 正确", "score": 0, "max_score": 20, "passed": False,
                        "reason": f"期望 ct_007，实际 {data.get('contact_id')}"})
    else:
        details.append({"item": "contact_id 正确", "score": 20, "max_score": 20, "passed": True,
                        "reason": "contact_id = ct_007"})
        total_score += 20

    # 4. tag_id 正确性
    expected_tag_id = "tag_vip_1"
    if data.get("tag_id") != expected_tag_id:
        details.append({"item": "tag_id 正确", "score": 0, "max_score": 30, "passed": False,
                        "reason": f"期望 {expected_tag_id}，实际 {data.get('tag_id')}"})
    else:
        details.append({"item": "tag_id 正确", "score": 30, "max_score": 30, "passed": True,
                        "reason": f"tag_id = {expected_tag_id}"})
        total_score += 30

    # 5. 验证 contacts.json 中 Grace Wilson 的 tags 是否已更新
    contacts_path = os.path.join(workspace, "data/contacts.json")
    if not os.path.isfile(contacts_path):
        details.append({"item": "联系人文件存在", "score": 0, "max_score": 10, "passed": False,
                        "reason": "data/contacts.json 不存在"})
    else:
        with open(contacts_path, "r") as f:
            contacts_data = json.load(f)
        contacts_list = contacts_data.get("contacts", [])
        grace = None
        for c in contacts_list:
            if c.get("contact_id") == "ct_007":
                grace = c
                break
        if grace is None:
            details.append({"item": "Grace Wilson 存在", "score": 0, "max_score": 10, "passed": False,
                            "reason": "未找到 contact_id=ct_007 的联系人"})
        else:
            tags = grace.get("tags", [])
            if expected_tag_id not in tags:
                details.append({"item": "Grace Wilson 已添加 VIP 标签", "score": 0, "max_score": 10, "passed": False,
                                "reason": f"tags 中不包含 {expected_tag_id}，实际 tags={tags}"})
            else:
                details.append({"item": "Grace Wilson 已添加 VIP 标签", "score": 10, "max_score": 10, "passed": True,
                                "reason": f"tags 包含 {expected_tag_id}"})
                total_score += 10

    # 总分上限控制
    total_score = min(total_score, max_total)
    return {"total_score": total_score, "details": details}

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score: {result['total_score']}/100")
