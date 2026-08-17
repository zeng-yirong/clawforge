#!/usr/bin/env python3
import json
import sys
import os

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

score_details = []
total_score = 0

def check(description, condition, max_score):
    global total_score
    passed = bool(condition)
    score = max_score if passed else 0
    total_score += score
    reason = "OK" if passed else f"FAIL: {description}"
    score_details.append({
        "item": description,
        "score": score,
        "max_score": max_score,
        "passed": passed,
        "reason": reason
    })

# 1. 检查结果文件是否存在 (10分)
result_path = os.path.join(workspace, "result", "customer_labels.json")
check("Result file exists", os.path.isfile(result_path), 10)

if os.path.isfile(result_path):
    # 2. 检查JSON合法性 (10分)
    try:
        with open(result_path, "r") as f:
            data = json.load(f)
        check("Result file is valid JSON", True, 10)
    except Exception as e:
        check("Result file is valid JSON", False, 10)
        # 如果JSON无效，后续检查跳过
        data = None

    if data is not None:
        # 3. 检查是否包含所有客户 (20分)
        expected_customers = {"c001", "c002", "c003"}
        actual_customers = set(data.keys())
        check("Contains all required customer IDs", actual_customers == expected_customers, 20)

        # 4. 检查c001标签 (20分)
        c001_labels = data.get("c001")
        check("c001 label is ['VIP']", c001_labels == ["VIP"], 20)

        # 5. 检查c002标签 (20分)
        c002_labels = data.get("c002")
        check("c002 label is ['churn_risk']", c002_labels == ["churn_risk"], 20)

        # 6. 检查c003标签 (20分)
        c003_labels = data.get("c003")
        check("c003 label is ['existing_label']", c003_labels == ["existing_label"], 20)

        # 7. 额外检查：没有多余的客户字段 (可选，可扣分但这里只给警告)
        # 为了简洁，不计分，但可以在details中体现
        extra = actual_customers - expected_customers
        if extra:
            score_details.append({
                "item": "No extra customers",
                "score": 0,
                "max_score": 0,
                "passed": False,
                "reason": f"Unexpected customers: {extra}"
            })
else:
    # 文件不存在，跳过后续检查，但要添加占位details使结构完整
    for desc in ["c001 label", "c002 label", "c003 label", "Contains all customers"]:
        score_details.append({
            "item": desc,
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "Result file missing"
        })

# 总分上限100，但当前设计总分110（10+10+20+20+20+20=100），修正
# 实际: 1(10)+2(10)+3(20)+4(20)+5(20)+6(20) = 100 正确

total_score = min(total_score, 100)  # 确保不超过100

result = {
    "total_score": total_score,
    "details": score_details
}

with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
    json.dump(result, f, indent=2)
