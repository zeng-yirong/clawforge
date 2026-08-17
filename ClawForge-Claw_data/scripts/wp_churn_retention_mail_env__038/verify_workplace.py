"""
Workplace verification script for wp_churn_retention_mail_env__038.
Pure Python, no external dependencies.
"""
import sys, os, json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    os.chdir(workspace)

    details = []
    total_score = 0

    # 1. 检查目录结构 (ops目录存在)
    if os.path.isdir("ops"):
        details.append({"item": "ops directory exists", "score": 5, "max_score": 5, "passed": True, "reason": "ops/ found"})
        total_score += 5
    else:
        details.append({"item": "ops directory exists", "score": 0, "max_score": 5, "passed": False, "reason": "ops/ missing"})

    # 2. 检查ops/retention_draft.json是否存在且合法JSON
    draft_path = "ops/retention_draft.json"
    if not os.path.isfile(draft_path):
        details.append({"item": "retention_draft.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "file not found"})
        details.append({"item": "JSON content is valid", "score": 0, "max_score": 10, "passed": False, "reason": "file missing"})
        # 后续检查跳过
        write_score(details)
        return

    try:
        with open(draft_path, "r") as f:
            data = json.load(f)
        details.append({"item": "retention_draft.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "file present and readable"})
        total_score += 10
        details.append({"item": "JSON content is valid", "score": 10, "max_score": 10, "passed": True, "reason": "valid JSON array"})
        total_score += 10
    except (json.JSONDecodeError, OSError) as e:
        details.append({"item": "retention_draft.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "file exists but invalid"})
        details.append({"item": "JSON content is valid", "score": 0, "max_score": 10, "passed": False, "reason": str(e)})
        write_score(details)
        return

    # 3. 确保是列表
    if not isinstance(data, list):
        details.append({"item": "Content is a list", "score": 0, "max_score": 5, "passed": False, "reason": "expected list, got " + type(data).__name__})
        write_score(details)
        return
    details.append({"item": "Content is a list", "score": 5, "max_score": 5, "passed": True, "reason": "root is list"})
    total_score += 5

    # 4. 数据准确性：预期唯一结果
    # 根据env_builder铺设的数据：
    # 活动日志：C001 high&45天，C002 high&10天（不满足>30），C003 low
    # 所以只有C001（LedgerFlow, fintech）符合条件。
    # 新闻：fintech中tone=opportunity只有N001。
    expected = [
        {
            "customer_id": "C001",
            "customer_name": "LedgerFlow",
            "headline": "Open Banking Regulation Boosts Fintech Innovation",
            "summary": "New regulatory framework opens doors for agile fintechs."
        }
    ]

    # 检查输出列表长度
    if len(data) != len(expected):
        details.append({"item": "Number of entries", "score": 0, "max_score": 15, "passed": False, "reason": f"expected {len(expected)} items, got {len(data)}"})
        total_score += 0
    else:
        details.append({"item": "Number of entries", "score": 15, "max_score": 15, "passed": True, "reason": f"exactly {len(expected)} items"})
        total_score += 15

    # 逐字段比较
    fields = ["customer_id", "customer_name", "headline", "summary"]
    field_score = 50  # 剩余50分分配给四个字段，每个12.5，取整12或13
    # 先检查字段齐全
    missing_fields = [f for f in fields if f not in data[0]] if data else []
    if data and not missing_fields:
        details.append({"item": "All required fields present", "score": 10, "max_score": 10, "passed": True, "reason": "fields: customer_id, customer_name, headline, summary"})
        total_score += 10
    else:
        details.append({"item": "All required fields present", "score": 0, "max_score": 10, "passed": False, "reason": f"missing fields: {missing_fields}" if missing_fields else "empty list"})
        total_score += 0

    # 值匹配
    if data and expected:
        match = True
        for idx, (field, exp_val) in enumerate([(f, expected[0][f]) for f in fields]):
            if data[0].get(field) != exp_val:
                details.append({"item": f"Field '{field}' value", "score": 0, "max_score": 10, "passed": False, "reason": f"expected '{exp_val}', got '{data[0].get(field)}'"})
                total_score += 0
                match = False
            else:
                details.append({"item": f"Field '{field}' value", "score": 10, "max_score": 10, "passed": True, "reason": f"correct value"})
                total_score += 10
        if match:
            pass  # 已加
    elif not data:
        for f in fields:
            details.append({"item": f"Field '{f}' value", "score": 0, "max_score": 10, "passed": False, "reason": "empty list"})

    # 确保没有多余字段（可选，不扣分但提示）
    if data:
        extra = set(data[0].keys()) - set(fields)
        if extra:
            # 不扣分，但记录在reason
            for d in details:
                if d["item"].startswith("All required fields"):
                    d["reason"] += f"; extra fields ignored: {extra}"

    write_score(details)

def write_score(details):
    total = sum(d["score"] for d in details)
    max_total = sum(d["max_score"] for d in details)
    result = {
        "total_score": total,
        "max_score": max_total,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written: {total}/{max_total}")

if __name__ == "__main__":
    main()
