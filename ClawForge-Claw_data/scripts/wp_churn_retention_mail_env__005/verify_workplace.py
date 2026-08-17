import os
import sys
import json

def verify(workspace):
    details = []
    total_score = 0

    # 1. Ops 目录存在 (10分)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        details.append({"item": "ops directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "ops/ found"})
        total_score += 10
    else:
        details.append({"item": "ops directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "ops/ not found"})

    # 2. 缓存文件存在 (10分)
    cache_path = os.path.join(workspace, "ops", "retention_email_cache.json")
    if os.path.isfile(cache_path):
        details.append({"item": "retention_email_cache.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "file found"})
        total_score += 10
    else:
        details.append({"item": "retention_email_cache.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "file missing"})
        # 后续检查无法进行，直接输出
        return {"total_score": total_score, "details": details}

    # 3. JSON 格式合法 (10分)
    try:
        with open(cache_path, "r") as f:
            data = json.load(f)
        details.append({"item": "valid JSON", "score": 10, "max_score": 10, "passed": True, "reason": "JSON parsed successfully"})
        total_score += 10
    except Exception as e:
        details.append({"item": "valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"parse error: {e}"})
        return {"total_score": total_score, "details": details}

    # 4. 必须包含 customer_id 字段 (20分)
    cid = data.get("customer_id")
    if cid == "C001":
        details.append({"item": "correct customer_id = C001", "score": 20, "max_score": 20, "passed": True, "reason": "C001 found"})
        total_score += 20
    else:
        details.append({"item": "correct customer_id = C001", "score": 0, "max_score": 20, "passed": False, "reason": f"got {cid}"})

    # 5. 必须包含 news_id 字段 (20分)
    nid = data.get("news_id")
    if nid == "N001":
        details.append({"item": "correct news_id = N001", "score": 20, "max_score": 20, "passed": True, "reason": "N001 found"})
        total_score += 20
    else:
        details.append({"item": "correct news_id = N001", "score": 0, "max_score": 20, "passed": False, "reason": f"got {nid}"})

    # 6. 邮件正文必须包含客户名称 LedgerFlow (10分)
    body = data.get("email_body", "")
    if "LedgerFlow" in body:
        details.append({"item": "email_body contains customer name", "score": 10, "max_score": 10, "passed": True, "reason": "LedgerFlow found"})
        total_score += 10
    else:
        details.append({"item": "email_body contains customer name", "score": 0, "max_score": 10, "passed": False, "reason": "missing LedgerFlow"})

    # 7. 邮件正文必须包含新闻标题的关键部分 (10分)
    if "New Fintech Opportunities" in body:
        details.append({"item": "email_body contains news headline snippet", "score": 10, "max_score": 10, "passed": True, "reason": "headline snippet found"})
        total_score += 10
    else:
        details.append({"item": "email_body contains news headline snippet", "score": 0, "max_score": 10, "passed": False, "reason": "missing headline snippet"})

    # 8. 邮件正文长度 > 50 字符 (10分)
    if len(body) > 50:
        details.append({"item": "email_body length > 50", "score": 10, "max_score": 10, "passed": True, "reason": f"length = {len(body)}"})
        total_score += 10
    else:
        details.append({"item": "email_body length > 50", "score": 0, "max_score": 10, "passed": False, "reason": f"too short ({len(body)})"})

    return {"total_score": total_score, "details": details}

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    # 写入文件
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score: {result['total_score']}/100")
