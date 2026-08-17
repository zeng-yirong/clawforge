import sys
import json
import os
from pathlib import Path

def verify(workspace: str):
    base = Path(workspace)
    results = []
    total_score = 0

    # 1. cache 目录存在 (10分)
    cache_dir = base / "cache"
    item = {"item": "cache directory exists", "max_score": 10}
    if cache_dir.is_dir():
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "cache directory found"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = "cache directory not found"
    total_score += item["score"]
    results.append(item)

    # 2. cache/retention_email.json 存在 (10分)
    target = cache_dir / "retention_email.json"
    item = {"item": "cache/retention_email.json exists", "max_score": 10}
    if target.is_file():
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "file found"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = "file not found"
    total_score += item["score"]
    results.append(item)

    if not target.is_file():
        # 如果文件不存在，后续无法检查
        score = sum(r["score"] for r in results)
        with open(base / "workplace_score.json", "w") as f:
            json.dump({"total_score": score, "details": results}, f)
        return

    # 3. JSON 合法且是列表 (10分)
    item = {"item": "valid JSON and is a list", "max_score": 10}
    try:
        with open(target, "r") as f:
            data = json.load(f)
        if isinstance(data, list):
            item["score"] = 10
            item["passed"] = True
            item["reason"] = "valid list"
        else:
            item["score"] = 0
            item["passed"] = False
            item["reason"] = f"expected list, got {type(data).__name__}"
    except Exception as e:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = f"JSON parse error: {e}"
    total_score += item["score"]
    results.append(item)

    # 如果数据不是列表，停止检查
    if not isinstance(data, list):
        score = sum(r["score"] for r in results)
        with open(base / "workplace_score.json", "w") as f:
            json.dump({"total_score": score, "details": results}, f)
        return

    # 4. 列表长度应为 2 (10分)
    item = {"item": "list length is 2", "max_score": 10}
    if len(data) == 2:
        item["score"] = 10
        item["passed"] = True
        item["reason"] = f"length = {len(data)}"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = f"expected 2 items, got {len(data)}"
    total_score += item["score"]
    results.append(item)

    # 5. 每个条目包含必要字段 (10分)
    required_fields = ["customer_id", "customer_name", "industry", "news_headline"]
    item = {"item": "each item has required fields", "max_score": 10}
    all_have_fields = True
    missing = []
    for idx, entry in enumerate(data):
        if not isinstance(entry, dict):
            all_have_fields = False
            missing.append(f"item {idx} is not a dict")
            continue
        for field in required_fields:
            if field not in entry:
                all_have_fields = False
                missing.append(f"item {idx} missing field '{field}'")
    if all_have_fields:
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "all items have required fields"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = "; ".join(missing)
    total_score += item["score"]
    results.append(item)

    # 6. 内容正确性 - 客户 C001 (15分)
    item = {"item": "C001 (LedgerFlow) entry correct", "max_score": 15}
    c001 = next((e for e in data if e.get("customer_id") == "C001"), None)
    if c001:
        correct = (c001.get("customer_name") == "LedgerFlow" and
                   c001.get("industry") == "fintech" and
                   c001.get("news_headline") == "Fintech startups face funding winter")
        if correct:
            item["score"] = 15
            item["passed"] = True
            item["reason"] = "all fields match expected"
        else:
            item["score"] = 0
            item["passed"] = False
            item["reason"] = f"fields mismatch: {c001}"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = "C001 not found in list"
    total_score += item["score"]
    results.append(item)

    # 7. 内容正确性 - 客户 C002 (15分)
    item = {"item": "C002 (ShelfCloud) entry correct", "max_score": 15}
    c002 = next((e for e in data if e.get("customer_id") == "C002"), None)
    if c002:
        correct = (c002.get("customer_name") == "ShelfCloud" and
                   c002.get("industry") == "retail" and
                   c002.get("news_headline") == "Retail margins squeezed by inflation")
        if correct:
            item["score"] = 15
            item["passed"] = True
            item["reason"] = "all fields match expected"
        else:
            item["score"] = 0
            item["passed"] = False
            item["reason"] = f"fields mismatch: {c002}"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = "C002 not found in list"
    total_score += item["score"]
    results.append(item)

    # 8. 列表按 customer_id 升序排序 (5分)
    item = {"item": "list sorted by customer_id ascending", "max_score": 5}
    ids = [e.get("customer_id") for e in data if isinstance(e, dict)]
    if ids == sorted(ids):
        item["score"] = 5
        item["passed"] = True
        item["reason"] = "sorted"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = f"unsorted order: {ids}"
    total_score += item["score"]
    results.append(item)

    # 9. 没有包含不符合条件的客户 (10分)
    item = {"item": "no invalid customers (C003, C004)", "max_score": 10}
    invalid_ids = {"C003", "C004"}
    ids_in_data = {e.get("customer_id") for e in data if isinstance(e, dict)}
    if invalid_ids.isdisjoint(ids_in_data):
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "no invalid customers present"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = f"found invalid customer IDs: {ids_in_data & invalid_ids}"
    total_score += item["score"]
    results.append(item)

    # 写入评分
    with open(base / "workplace_score.json", "w") as f:
        json.dump({"total_score": total_score, "details": results}, f)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
