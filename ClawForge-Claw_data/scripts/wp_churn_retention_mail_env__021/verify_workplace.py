import sys
import os
import json

def verify(workspace):
    details = []
    total_score = 0

    # 1. 目录结构检查 (10分)
    path_ops = os.path.join(workspace, 'ops')
    path_file = os.path.join(path_ops, 'retention_emails.json')
    if os.path.isdir(path_ops):
        details.append({
            "item": "ops directory exists",
            "score": 5, "max_score": 5, "passed": True,
            "reason": "ops/ found"
        })
        total_score += 5
    else:
        details.append({
            "item": "ops directory exists",
            "score": 0, "max_score": 5, "passed": False,
            "reason": "ops/ directory missing"
        })

    if os.path.isfile(path_file):
        details.append({
            "item": "retention_emails.json exists",
            "score": 5, "max_score": 5, "passed": True,
            "reason": "file found"
        })
        total_score += 5
    else:
        details.append({
            "item": "retention_emails.json exists",
            "score": 0, "max_score": 5, "passed": False,
            "reason": "file not found"
        })
        # 如果文件不存在，直接返回，因为后续无法检查
        report = {"total_score": total_score, "details": details}
        with open(os.path.join(workspace, 'workplace_score.json'), 'w') as f:
            json.dump(report, f)
        return

    # 2. JSON合法性 (10分)
    try:
        with open(path_file, 'r') as f:
            data = json.load(f)
        details.append({
            "item": "valid JSON",
            "score": 10, "max_score": 10, "passed": True,
            "reason": "JSON parsed successfully"
        })
        total_score += 10
    except Exception as e:
        details.append({
            "item": "valid JSON",
            "score": 0, "max_score": 10, "passed": False,
            "reason": f"Invalid JSON: {str(e)}"
        })
        report = {"total_score": total_score, "details": details}
        with open(os.path.join(workspace, 'workplace_score.json'), 'w') as f:
            json.dump(report, f)
        return

    # 3. 数据结构合法性 (20分)
    if not isinstance(data, list):
        details.append({
            "item": "data is a list",
            "score": 0, "max_score": 10, "passed": False,
            "reason": "Expected a JSON array"
        })
        # 仍继续检查可能的其他结构
    else:
        details.append({
            "item": "data is a list",
            "score": 10, "max_score": 10, "passed": True,
            "reason": "proper array"
        })
        total_score += 10

        # 检查每个元素字段
        field_ok = True
        for i, entry in enumerate(data):
            if not isinstance(entry, dict) or 'customer_id' not in entry or 'news_id' not in entry:
                field_ok = False
                details.append({
                    "item": f"entry {i} has required fields",
                    "score": 0, "max_score": 10, "passed": False,
                    "reason": f"Missing customer_id or news_id in entry {i}"
                })
                break
        if field_ok and len(data) > 0:
            details.append({
                "item": "all entries have customer_id and news_id",
                "score": 10, "max_score": 10, "passed": True,
                "reason": "fields present"
            })
            total_score += 10
        elif field_ok and len(data) == 0:
            details.append({
                "item": "all entries have customer_id and news_id",
                "score": 0, "max_score": 10, "passed": False,
                "reason": "empty array"
            })
        else:
            # 已经在循环里加过detail了，这里不再重复
            pass

    # 4. 核心内容准确性 (60分，每个正确匹配30分)
    # 期望答案: [{"customer_id":"cust001","news_id":"n001"}, {"customer_id":"cust002","news_id":"n003"}]
    expected = [
        {"customer_id": "cust001", "news_id": "n001"},
        {"customer_id": "cust002", "news_id": "n003"}
    ]
    # 转换为可查找的映射
    expected_map = {e['customer_id']: e['news_id'] for e in expected}
    actual_map = {}
    for entry in data:
        if isinstance(entry, dict) and 'customer_id' in entry and 'news_id' in entry:
            actual_map[entry['customer_id']] = entry['news_id']

    score_cust1 = 0
    reason_cust1 = ""
    if 'cust001' in actual_map and actual_map['cust001'] == 'n001':
        score_cust1 = 30
        reason_cust1 = "cust001 maps to n001 correctly"
    else:
        reason_cust1 = f"cust001 not found or wrong news_id: {actual_map.get('cust001', 'missing')}"

    details.append({
        "item": "cust001 -> n001",
        "score": score_cust1, "max_score": 30, "passed": (score_cust1 == 30),
        "reason": reason_cust1
    })
    total_score += score_cust1

    score_cust2 = 0
    reason_cust2 = ""
    if 'cust002' in actual_map and actual_map['cust002'] == 'n003':
        score_cust2 = 30
        reason_cust2 = "cust002 maps to n003 correctly"
    else:
        reason_cust2 = f"cust002 not found or wrong news_id: {actual_map.get('cust002', 'missing')}"

    details.append({
        "item": "cust002 -> n003",
        "score": score_cust2, "max_score": 30, "passed": (score_cust2 == 30),
        "reason": reason_cust2
    })
    total_score += score_cust2

    # 额外扣分：如果包含了不应出现的客户（多出来的条目）
    extra_customers = set(actual_map.keys()) - {'cust001', 'cust002'}
    if extra_customers:
        # 每个额外客户扣10分（但确保总分不小于0）
        penalty = len(extra_customers) * 10
        details.append({
            "item": "no extra customers",
            "score": max(0, 10 - penalty), "max_score": 10, "passed": False,
            "reason": f"Extra customers found: {', '.join(extra_customers)}"
        })
        total_score = max(0, total_score - penalty)
    else:
        details.append({
            "item": "no extra customers",
            "score": 10, "max_score": 10, "passed": True,
            "reason": "only expected customers present"
        })
        total_score += 10

    # 汇总写入
    report = {
        "total_score": total_score,
        "details": details
    }
    with open(os.path.join(workspace, 'workplace_score.json'), 'w') as f:
        json.dump(report, f)

if __name__ == '__main__':
    workspace = sys.argv[1] if len(sys.argv) > 1 else '.'
    verify(workspace)
