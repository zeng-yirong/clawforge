import sys
import os
import json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    os.chdir(workspace)

    details = []
    total_score = 0

    # 1. 检查 outputs 目录是否存在 (10分)
    exists_outputs = os.path.isdir("outputs")
    details.append({
        "item": "outputs目录是否存在",
        "score": 10 if exists_outputs else 0,
        "max_score": 10,
        "passed": exists_outputs,
        "reason": "outputs目录存在" if exists_outputs else "outputs目录缺失"
    })
    if exists_outputs:
        total_score += 10

    # 2. 检查目标文件是否存在 (10分)
    target = "outputs/customer_tier_labels.json"
    exists_file = os.path.isfile(target)
    details.append({
        "item": "目标文件是否存在",
        "score": 10 if exists_file else 0,
        "max_score": 10,
        "passed": exists_file,
        "reason": f"{target}存在" if exists_file else f"{target}不存在"
    })
    if exists_file:
        total_score += 10

    # 3. 文件格式合法性 (10分)
    valid_json = False
    data = None
    if exists_file:
        try:
            with open(target, "r") as f:
                data = json.load(f)
            valid_json = True
        except (json.JSONDecodeError, ValueError):
            pass
    details.append({
        "item": "JSON格式合法",
        "score": 10 if valid_json else 0,
        "max_score": 10,
        "passed": valid_json,
        "reason": "JSON解析成功" if valid_json else "JSON解析失败"
    })
    if valid_json:
        total_score += 10

    # 4. 数据结构：必须是list，且包含恰好3条记录 (20分)
    correct_list = False
    record_count = 0
    if valid_json and isinstance(data, list):
        record_count = len(data)
        if record_count == 3:
            correct_list = True
    details.append({
        "item": "数组包含3条记录",
        "score": 20 if correct_list else (record_count if record_count < 3 else 0),
        "max_score": 20,
        "passed": correct_list,
        "reason": f"包含{record_count}条记录" if record_count == 3 else f"期望3条，实际{record_count}条"
    })
    if correct_list:
        total_score += 20

    # 5. 每条记录字段检查及标签正确性 (每个客户20分，共60分)
    expected_records = {
        "cust_001": "VIP活跃",
        "cust_002": "普通活跃",
        "cust_003": "VIP沉睡"
    }
    if correct_list:
        # 构建customer_id到记录的映射
        record_map = {}
        for rec in data:
            cid = rec.get("customer_id")
            if cid:
                record_map[cid] = rec

        for cid, expected_label in expected_records.items():
            passed = False
            reason = ""
            if cid not in record_map:
                reason = f"缺少客户{cid}"
            else:
                rec = record_map[cid]
                # 检查字段是否只有customer_id和new_label
                keys = set(rec.keys())
                if keys != {"customer_id", "new_label"}:
                    reason = f"客户{cid}包含多余或缺失字段: {keys}"
                elif rec.get("new_label") != expected_label:
                    reason = f"客户{cid}标签应为'{expected_label}'，实际为'{rec.get('new_label')}'"
                else:
                    passed = True
                    reason = f"客户{cid}字段和标签正确"
            score = 20 if passed else 0
            details.append({
                "item": f"客户{cid}标签正确性",
                "score": score,
                "max_score": 20,
                "passed": passed,
                "reason": reason
            })
            total_score += score

    # 6. 总分上限100
    total_score = min(total_score, 100)
    result = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
