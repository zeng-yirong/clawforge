import json
import os
import sys

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    os.chdir(workspace)

    results = []
    total_score = 0

    # 1. 检查 ops/customer_tier_labels.json 是否存在 (10分)
    result_file = "ops/customer_tier_labels.json"
    if os.path.isfile(result_file):
        results.append({"item": "文件存在", "score": 10, "max_score": 10, "passed": True, "reason": "ops/customer_tier_labels.json 存在"})
        total_score += 10
    else:
        results.append({"item": "文件存在", "score": 0, "max_score": 10, "passed": False, "reason": "ops/customer_tier_labels.json 未找到"})
        print("最终得分: 0 (文件缺失)")
        write_score(total_score, results)
        sys.exit(0)

    # 2. 解析 JSON 并检查合法性 (10分)
    try:
        with open(result_file, "r") as f:
            data = json.load(f)
        results.append({"item": "JSON格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "JSON解析成功"})
        total_score += 10
    except Exception as e:
        results.append({"item": "JSON格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON解析失败: {e}"})
        write_score(total_score, results)
        sys.exit(0)

    # 3. 确保是列表，且包含两个客户 (20分, 每个10)
    if not isinstance(data, list):
        results.append({"item": "结果类型", "score": 0, "max_score": 20, "passed": False, "reason": "输出应为数组"})
        write_score(total_score, results)
        sys.exit(0)

    if len(data) != 2:
        results.append({"item": "客户数量正确", "score": 0, "max_score": 20, "passed": False, "reason": f"期望2个客户，实际{len(data)}个"})
        write_score(total_score, results)
        sys.exit(0)
    else:
        results.append({"item": "客户数量正确", "score": 20, "max_score": 20, "passed": True, "reason": "包含2个客户"})
        total_score += 20

    # 4. 定义预期答案
    expected = {
        "C001": {
            "labels": ["high_value", "growing"],
            "vip_score": 50  # 62 + (30-15)*0.1 = 63.5 > 50 -> 50
        },
        "C002": {
            "labels": ["churn_risk"],
            "vip_score": 18  # 18 + 0
        }
    }

    # 5. 逐客户检查 (每个客户: 标签正确10分 + VIP分数正确20分 = 30分, 两个共60分)
    for entry in data:
        cid = entry.get("customer_id")
        if cid not in expected:
            results.append({"item": f"客户{cid}存在", "score": 0, "max_score": 30, "passed": False, "reason": f"意外的客户ID: {cid}"})
            continue

        exp = expected[cid]
        item_label_score = 0
        item_label_max = 10
        item_vip_score = 0
        item_vip_max = 20

        # 检查 labels (忽略顺序)
        actual_labels = entry.get("labels", [])
        if set(actual_labels) == set(exp["labels"]):
            item_label_score = 10
            total_score += 10
            results.append({"item": f"客户{cid}标签", "score": 10, "max_score": 10, "passed": True, "reason": f"标签匹配: {actual_labels}"})
        else:
            results.append({"item": f"客户{cid}标签", "score": 0, "max_score": 10, "passed": False, "reason": f"期望{exp['labels']}，实际{actual_labels}"})

        # 检查 vip_score (整数或浮点数比较)
        actual_vip = entry.get("vip_score")
        if isinstance(actual_vip, (int, float)) and abs(actual_vip - exp["vip_score"]) < 0.001:
            item_vip_score = 20
            total_score += 20
            results.append({"item": f"客户{cid}VIP分数", "score": 20, "max_score": 20, "passed": True, "reason": f"vip_score={actual_vip}"})
        else:
            results.append({"item": f"客户{cid}VIP分数", "score": 0, "max_score": 20, "passed": False, "reason": f"期望{exp['vip_score']}，实际{actual_vip}"})

    # 总分 10+10+20+10+20+10+20 = 100 (实际看累加)
    write_score(total_score, results)

def write_score(total, details):
    output = {"total_score": total, "details": details}
    with open("workplace_score.json", "w") as f:
        json.dump(output, f, indent=2)
    print(f"总得分: {total}/100")

if __name__ == "__main__":
    main()
