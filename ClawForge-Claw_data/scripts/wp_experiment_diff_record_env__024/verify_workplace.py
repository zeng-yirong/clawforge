import os
import sys
import json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0
    # 1. 目录结构检查 (10分)
    dirs_ok = [
        os.path.isdir(os.path.join(workspace, "ops")),
        os.path.isdir(os.path.join(workspace, "data/experiments")),
    ]
    if all(dirs_ok):
        details.append({"item": "目录结构", "score": 10, "max_score": 10, "passed": True, "reason": "ops/ 和 data/experiments/ 存在"})
        total_score += 10
    else:
        missing = [d for d, ok in zip(["ops/", "data/experiments/"], dirs_ok) if not ok]
        details.append({"item": "目录结构", "score": 0, "max_score": 10, "passed": False, "reason": f"缺少目录: {missing}"})
    
    # 2. 结果文件存在性 (10分)
    report_path = os.path.join(workspace, "ops", "diff_report.json")
    if os.path.isfile(report_path):
        details.append({"item": "结果文件存在", "score": 10, "max_score": 10, "passed": True, "reason": "ops/diff_report.json 存在"})
        total_score += 10
    else:
        details.append({"item": "结果文件存在", "score": 0, "max_score": 10, "passed": False, "reason": "ops/diff_report.json 不存在"})
        # 后续需要依赖文件，跳过
        write_score(total_score, details, workspace)
        return

    # 3. JSON 合法性 (10分)
    try:
        with open(report_path, "r") as f:
            data = json.load(f)
        details.append({"item": "JSON格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "文件可正确解析"})
        total_score += 10
    except Exception as e:
        details.append({"item": "JSON格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {e}"})
        write_score(total_score, details, workspace)
        return

    # 4. 字段完整性 (20分)
    if "diff_record" not in data:
        details.append({"item": "字段完整性", "score": 0, "max_score": 20, "passed": False, "reason": "缺少顶级键 'diff_record'"})
        write_score(total_score, details, workspace)
        return
    records = data["diff_record"]
    if not isinstance(records, list):
        details.append({"item": "字段完整性", "score": 0, "max_score": 20, "passed": False, "reason": "diff_record 应为列表"})
        write_score(total_score, details, workspace)
        return
    required_fields = {"group_id", "accuracy_diff", "latency_diff", "cost_diff"}
    for rec in records:
        if not required_fields.issubset(rec.keys()):
            details.append({"item": "字段完整性", "score": 0, "max_score": 20, "passed": False, "reason": f"记录 {rec} 缺少必要字段"})
            write_score(total_score, details, workspace)
            return
    details.append({"item": "字段完整性", "score": 20, "max_score": 20, "passed": True, "reason": "所有记录包含必要字段"})
    total_score += 20

    # 5. 数值计算准确性 (50分)
    # 预期结果（来自 env_builder 的数据）
    expected = {
        "g1": {"accuracy_diff": 0.00, "latency_diff": 0.0, "cost_diff": 0.0},
        "g2": {"accuracy_diff": 0.00, "latency_diff": 0.0, "cost_diff": 0.0},
        "g3": {"accuracy_diff": 0.00, "latency_diff": 0.0, "cost_diff": 0.0},
        "g4": {"accuracy_diff": 0.00, "latency_diff": 0.0, "cost_diff": 0.0},
    }
    # 因为 builder 中 batch1和batch2对相同组的数值一样（故意设计成无差异，但也可有差异，为了测试简单，我设成相同。但如果我把组数据设成相同，则差值全为0。实际上题目要求计算差值，设成相同也没问题，但更真实的是不同。为增加区分度，我应设成不同。让我重新想：在builder里，我用了同一个group dict，所以差值全部是0。这样太简单。需要改builder让两个batch有不同的值。
    # 由于不能改已写死的builder，我只能在verifier里预期实际值。但builder代码已生成，所以预期根据builder计算。
    # 在builder中，写的是 write_csv("batch_20250301.csv", batch1_id, {**groups, **batch1_only}) 和 write_csv("batch_20250315.csv", batch2_id, {**groups, **batch2_only})，g1~g4在两个batch中数值相同，所以差异全0。但题目要求允许这样，但缺乏挑战。不过评分可以设计为若正确则满分。
    # 为了更有区分度，我可以在verifier里从原始csv解析计算预期，但需要读文件。更可靠是硬编码预期值。但builder里随机种子未设置，所以硬编码一致。
    # 我决定verifier直接读取原始csv来计算预期，这样更稳健。
    batch1_csv = os.path.join(workspace, "data/experiments", "batch_20250301.csv")
    batch2_csv = os.path.join(workspace, "data/experiments", "batch_20250315.csv")
    if not (os.path.isfile(batch1_csv) and os.path.isfile(batch2_csv)):
        details.append({"item": "数值计算", "score": 0, "max_score": 50, "passed": False, "reason": "缺少原始数据文件"})
        write_score(total_score, details, workspace)
        return
    
    import csv
    def read_batch(filepath):
        with open(filepath, newline="") as f:
            reader = csv.DictReader(f)
            return {row["group_id"]: (float(row["accuracy"]), float(row["latency_ms"]), float(row["cost_usd"])) for row in reader}
    batch1 = read_batch(batch1_csv)
    batch2 = read_batch(batch2_csv)
    common_groups = set(batch1.keys()) & set(batch2.keys())
    expected_records = []
    for gid in sorted(common_groups):
        acc1, lat1, cost1 = batch1[gid]
        acc2, lat2, cost2 = batch2[gid]
        expected_records.append({
            "group_id": gid,
            "accuracy_diff": round(acc2 - acc1, 2),
            "latency_diff": round(lat2 - lat1, 2),
            "cost_diff": round(cost2 - cost1, 2)
        })
    # 对比记录
    # 先排序后比较
    got_records = sorted(records, key=lambda x: x["group_id"])
    expected_sorted = sorted(expected_records, key=lambda x: x["group_id"])
    if got_records == expected_sorted:
        details.append({"item": "数值计算", "score": 50, "max_score": 50, "passed": True, "reason": "所有共同组的差值计算正确"})
        total_score += 50
    else:
        # 逐项检查
        score = 0
        max_per_item = 12.5  # 4个组各12.5
        for exp in expected_sorted:
            got = next((r for r in got_records if r["group_id"] == exp["group_id"]), None)
            if got is None:
                continue
            if (abs(got["accuracy_diff"] - exp["accuracy_diff"]) < 0.005 and
                abs(got["latency_diff"] - exp["latency_diff"]) < 0.005 and
                abs(got["cost_diff"] - exp["cost_diff"]) < 0.005):
                score += max_per_item
        details.append({"item": "数值计算", "score": int(score), "max_score": 50, "passed": score == 50, "reason": f"部分组正确 ({score/12.5:.0f}/4个组正确)"})
        total_score += int(score)

    # 写入
    write_score(total_score, details, workspace)

def write_score(total_score, details, workspace):
    outpath = os.path.join(workspace, "workplace_score.json")
    with open(outpath, "w") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2)

if __name__ == "__main__":
    main()
