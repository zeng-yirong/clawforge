import sys
import json
import os
import re
from pathlib import Path

def parse_date(birthday_str):
    """尝试解析 yyyy-mm-dd 格式，返回月份(1-12)，失败返回 None"""
    if not isinstance(birthday_str, str) or not birthday_str.strip():
        return None
    m = re.match(r'^(\d{4})-(\d{2})-(\d{2})$', birthday_str.strip())
    if m:
        return int(m.group(2))
    return None

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    workspace_path = Path(workspace)
    scores = []
    total_score = 0

    # 1. 检查 ops 目录 (10分)
    ops_dir = workspace_path / "ops"
    if ops_dir.is_dir():
        scores.append({
            "item": "ops 目录存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "ops/ 目录已创建"
        })
        total_score += 10
    else:
        scores.append({
            "item": "ops 目录存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ops/ 目录不存在"
        })
        # 如果目录不存在，后续检查无意义，输出结果
        result = {"total_score": total_score, "details": scores}
        with open(workspace_path / "workplace_score.json", "w") as f:
            json.dump(result, f, indent=2)
        return

    # 2. 检查目标文件存在 (10分)
    target_file = ops_dir / "april_birthdays.json"
    if target_file.is_file():
        scores.append({
            "item": "ops/april_birthdays.json 存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "文件已生成"
        })
        total_score += 10
    else:
        scores.append({
            "item": "ops/april_birthdays.json 存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件不存在"
        })
        # 写入结果并退出
        result = {"total_score": total_score, "details": scores}
        with open(workspace_path / "workplace_score.json", "w") as f:
            json.dump(result, f, indent=2)
        return

    # 3. 解析 JSON 合法性 (10分)
    try:
        with open(target_file, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        scores.append({
            "item": "JSON 合法性",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON 解析失败: {e}"
        })
        result = {"total_score": total_score, "details": scores}
        with open(workspace_path / "workplace_score.json", "w") as f:
            json.dump(result, f, indent=2)
        return

    if not isinstance(data, list):
        scores.append({
            "item": "JSON 合法性",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "顶层不是列表"
        })
        result = {"total_score": total_score, "details": scores}
        with open(workspace_path / "workplace_score.json", "w") as f:
            json.dump(result, f, indent=2)
        return
    scores.append({
        "item": "JSON 合法性",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "有效的列表结构"
    })
    total_score += 10

    # 4. 从原始 contacts.json 获取基准 (期望列表)
    contacts_file = workspace_path / "data" / "contacts.json"
    expected = {}
    try:
        with open(contacts_file, "r") as f:
            contacts = json.load(f)
    except:
        scores.append({
            "item": "基准数据读取",
            "score": 0,
            "max_score": 0,
            "passed": True,
            "reason": "无法读取 contacts.json，使用硬编码期望"
        })
        # 硬编码：Alice, Carol, Emma, Grace
        expected = {
            "ct_001": "Alice Johnson",
            "ct_003": "Carol Williams",
            "ct_005": "Emma Davis",
            "ct_007": "Grace Wilson"
        }
    else:
        for c in contacts:
            month = parse_date(c.get("birthday"))
            if month == 4:
                cid = c.get("contact_id")
                name = c.get("full_name")
                if cid and name:
                    expected[cid] = name

    # 5. 列表长度 (20分)
    if len(data) == len(expected):
        scores.append({
            "item": "列表长度正确",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": f"数量 {len(data)} 与期望 {len(expected)} 一致"
        })
        total_score += 20
    else:
        scores.append({
            "item": "列表长度正确",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"实际 {len(data)} 个，期望 {len(expected)} 个"
        })

    # 6. 字段完整性 (10分)
    field_ok = True
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            field_ok = False
            break
        if "contact_id" not in item or "full_name" not in item:
            field_ok = False
            break
        if not isinstance(item["contact_id"], str) or not isinstance(item["full_name"], str):
            field_ok = False
            break
    if field_ok:
        scores.append({
            "item": "字段完整性",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "每个元素包含正确的 contact_id 和 full_name (字符串)"
        })
        total_score += 10
    else:
        scores.append({
            "item": "字段完整性",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "存在缺少字段或类型错误"
        })

    # 7. 内容正确性 (30分)
    # 将实际列表转为 dict 方便比较
    actual_map = {}
    for item in data:
        cid = item.get("contact_id")
        name = item.get("full_name")
        if cid:
            actual_map[cid] = name

    correct_count = 0
    error_reasons = []
    for cid, name in expected.items():
        if cid in actual_map and actual_map[cid] == name:
            correct_count += 1
        else:
            error_reasons.append(f"缺失或不匹配: {cid} -> {actual_map.get(cid, 'N/A')}" )
    # 检查是否有不应出现的联系人
    extra = [cid for cid in actual_map if cid not in expected]
    if extra:
        error_reasons.append(f"多余的联系人: {extra}")
        correct_count = 0  # 有额外则内容部分全扣
    if correct_count == len(expected) and not extra:
        scores.append({
            "item": "内容正确性",
            "score": 30,
            "max_score": 30,
            "passed": True,
            "reason": "所有期望联系人均正确列出，无多余"
        })
        total_score += 30
    else:
        scores.append({
            "item": "内容正确性",
            "score": 0,
            "max_score": 30,
            "passed": False,
            "reason": "; ".join(error_reasons)
        })

    # 8. 处理无效记录 (10分) —— 确保没有把空生日或非4月的人加进来
    invalid_contact_ids = {"ct_008"}  # Henry Taylor 空生日
    invalid_found = False
    for item in data:
        cid = item.get("contact_id")
        if cid in invalid_contact_ids:
            invalid_found = True
            break
    if not invalid_found:
        scores.append({
            "item": "忽略无效记录",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "未包含无效生日联系人 (Henry Taylor)"
        })
        total_score += 10
    else:
        scores.append({
            "item": "忽略无效记录",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "包含了无效生日联系人 (Henry Taylor)"
        })

    # 汇总写入
    result = {
        "total_score": total_score,
        "details": scores
    }
    with open(workspace_path / "workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
