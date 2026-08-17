import json
import os
import sys

def verify(workspace: str) -> dict:
    details = []
    total_score = 0

    # 1) 检查结果文件是否存在 (10分)
    result_path = os.path.join(workspace, "industry_tags_applied.json")
    if os.path.isfile(result_path):
        details.append({"item": "结果文件存在", "score": 10, "max_score": 10, "passed": True, "reason": "industry_tags_applied.json 存在"})
        total_score += 10
    else:
        details.append({"item": "结果文件存在", "score": 0, "max_score": 10, "passed": False, "reason": "industry_tags_applied.json 不存在"})
        # 直接写分数并返回，后面检查无意义
        return {"total_score": total_score, "details": details}

    # 2) 解析JSON合法性 (10分)
    try:
        with open(result_path, "r") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ValueError("不是列表")
        details.append({"item": "JSON格式合法且为列表", "score": 10, "max_score": 10, "passed": True, "reason": "解析成功，类型为list"})
        total_score += 10
    except Exception as e:
        details.append({"item": "JSON格式合法且为列表", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {e}"})
        return {"total_score": total_score, "details": details}

    # 3) 每个条目必须有 contact_id 和 tag_name，且格式正确 (20分)
    valid_format = True
    for i, entry in enumerate(data):
        if not isinstance(entry, dict):
            valid_format = False
            break
        if "contact_id" not in entry or "tag_name" not in entry:
            valid_format = False
            break
        if not isinstance(entry["contact_id"], str) or not isinstance(entry["tag_name"], str):
            valid_format = False
            break
    if valid_format:
        details.append({"item": "条目字段格式正确", "score": 20, "max_score": 20, "passed": True, "reason": f"所有{len(data)}个条目均含contact_id和tag_name字符串字段"})
        total_score += 20
    else:
        details.append({"item": "条目字段格式正确", "score": 0, "max_score": 20, "passed": False, "reason": "存在条目缺少字段或类型错误"})
        return {"total_score": total_score, "details": details}

    # 4) 数量是否正确（应为3个需要添加的联系人：ct_102, ct_104, ct_106, ct_107 → 注意ct_106也是需要添加的，共4个？重新核对）
    # 从env_builder设计：需要添加的联系人：ct_102(Consulting), ct_104(Logistics), ct_106(Consulting), ct_107(Manufacturing) → 4个
    # 验证预期列表
    expected = {
        "ct_102": "Consulting",
        "ct_104": "Logistics",
        "ct_106": "Consulting",
        "ct_107": "Manufacturing"
    }
    if len(data) == len(expected):
        details.append({"item": "条目数量正确", "score": 20, "max_score": 20, "passed": True, "reason": f"条目数为{len(expected)}，与预期一致"})
        total_score += 20
    else:
        details.append({"item": "条目数量正确", "score": 0, "max_score": 20, "passed": False, "reason": f"期望{len(expected)}条，实际{len(data)}条"})
        # 不立即返回，继续检查可能部分正确

    # 5) 内容准确：每个contact_id对应的tag_name正确 (40分，每个10分)，考虑顺序无关
    # 先构建映射
    result_map = {}
    for entry in data:
        cid = entry["contact_id"]
        tag = entry["tag_name"]
        if cid in result_map:
            # 重复条目，扣分
            details.append({"item": "无重复contact_id", "score": 0, "max_score": 40, "passed": False, "reason": f"contact_id {cid} 出现多次"})
            return {"total_score": total_score, "details": details}
        result_map[cid] = tag

    correct_count = 0
    for cid, expected_tag in expected.items():
        if cid in result_map and result_map[cid] == expected_tag:
            correct_count += 1
        else:
            # 记录错误原因
            pass
    if correct_count == len(expected):
        details.append({"item": "内容准确", "score": 40, "max_score": 40, "passed": True, "reason": f"全部{len(expected)}个映射与预期一致"})
        total_score += 40
    else:
        details.append({"item": "内容准确", "score": 0, "max_score": 40, "passed": False, "reason": f"正确{correct_count}个，期望{len(expected)}个"})
        # 如果数量正确但内容不全对，扣分
        total_score += 0  # 不额外加分

    # 额外检查：有没有包含不应该存在的条目（如ct_101已有标签，ct_105已有，ct_108无有效公司）
    unexpected = [e for e in data if e["contact_id"] not in expected]
    if unexpected:
        details.append({"item": "无多余条目", "score": 0, "max_score": 0, "passed": False, "reason": f"发现不应出现的条目: {unexpected}"})
        # 不扣分，但记录

    # 确保分数不超过100
    total_score = min(total_score, 100)
    return {"total_score": total_score, "details": details}


if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))
