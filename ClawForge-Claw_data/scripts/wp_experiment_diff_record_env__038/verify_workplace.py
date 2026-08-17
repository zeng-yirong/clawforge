import sys
import os
import json
import csv
from decimal import Decimal, getcontext

getcontext().prec = 10

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []
    result_path = os.path.join(workspace, "ops", "diff_record.json")

    # 1. 检查文件是否存在
    if not os.path.isfile(result_path):
        details.append({
            "item": "ops/diff_record.json 存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件未找到"
        })
        # 其他项自动0分
        for item in ["JSON格式合法", "batch_a 和 batch_b 字段", "records数组长度", "记录字段完整", "数值精确匹配"]:
            details.append({
                "item": item,
                "score": 0,
                "max_score": (10 if item != "数值精确匹配" else 40),
                "passed": False,
                "reason": "前置检查未通过"
            })
        total = sum(d["score"] for d in details)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": details}, f, indent=2)
        return

    details.append({
        "item": "ops/diff_record.json 存在",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "文件存在"
    })

    # 2. 检查 JSON 格式
    try:
        with open(result_path, "r") as f:
            data = json.load(f)
        details.append({
            "item": "JSON格式合法",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "JSON解析成功"
        })
    except Exception as e:
        details.append({
            "item": "JSON格式合法",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON解析失败: {str(e)}"
        })
        # 跳过后续检查
        for item in ["batch_a 和 batch_b 字段", "records数组长度", "记录字段完整", "数值精确匹配"]:
            details.append({
                "item": item,
                "score": 0,
                "max_score": (10 if item != "数值精确匹配" else 40),
                "passed": False,
                "reason": "前置检查未通过"
            })
        total = sum(d["score"] for d in details)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": details}, f, indent=2)
        return

    # 3. 检查 batch_a 和 batch_b
    if "batch_a" in data and "batch_b" in data and data["batch_a"] == "exp_v2" and data["batch_b"] == "exp_v3":
        details.append({
            "item": "batch_a 和 batch_b 字段",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"batch_a={data.get('batch_a')}, batch_b={data.get('batch_b')}"
        })
    else:
        details.append({
            "item": "batch_a 和 batch_b 字段",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"期望 batch_a='exp_v2', batch_b='exp_v3'，实际 batch_a={data.get('batch_a')}, batch_b={data.get('batch_b')}"
        })

    # 4. 检查 records 数组长度
    records = data.get("records", [])
    if isinstance(records, list) and len(records) == 3:
        details.append({
            "item": "records数组长度",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"records 长度为 {len(records)}"
        })
    else:
        details.append({
            "item": "records数组长度",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"期望长度为3，实际长度为 {len(records)}"
        })

    # 5. 检查每个记录字段完整性
    required_fields = {"group_id", "accuracy_diff", "latency_diff", "cost_diff"}
    all_records_complete = True
    for i, rec in enumerate(records):
        if not isinstance(rec, dict):
            all_records_complete = False
            break
        if not required_fields.issubset(rec.keys()):
            all_records_complete = False
            break
    if all_records_complete:
        details.append({
            "item": "记录字段完整",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "每个记录包含 group_id, accuracy_diff, latency_diff, cost_diff"
        })
    else:
        details.append({
            "item": "记录字段完整",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "部分记录缺少必要字段"
        })

    # 6. 数值精确匹配（最重头）
    # 预期值（基于 builder 中清理后的干净数据计算）
    expected = [
        {"group_id": "control",      "accuracy_diff": 0.01,  "latency_diff": 5,    "cost_diff": 0.003},
        {"group_id": "treatment_small", "accuracy_diff": 0.01,  "latency_diff": 3,    "cost_diff": 0.003},
        {"group_id": "treatment_large", "accuracy_diff": 0.01,  "latency_diff": -2,   "cost_diff": 0.005},
    ]
    # 为了方便检查，建立 group_id -> expected dict
    expect_by_group = {e["group_id"]: e for e in expected}
    numeric_score = 0
    numeric_max = 40
    if all_records_complete and len(records) == 3:
        # 检查每个组的差值
        all_match = True
        for rec in records:
            gid = rec.get("group_id")
            exp = expect_by_group.get(gid)
            if exp is None:
                all_match = False
                break
            for key in ["accuracy_diff", "latency_diff", "cost_diff"]:
                val = rec.get(key)
                exp_val = exp[key]
                # 使用 Decimal 避免浮点误差
                try:
                    d_val = Decimal(str(val))
                    d_exp = Decimal(str(exp_val))
                except:
                    all_match = False
                    break
                if abs(d_val - d_exp) > Decimal("1e-9"):
                    all_match = False
                    break
            if not all_match:
                break
        if all_match:
            numeric_score = 40
            details.append({
                "item": "数值精确匹配",
                "score": 40,
                "max_score": 40,
                "passed": True,
                "reason": "所有组的差值均与预期一致"
            })
        else:
            details.append({
                "item": "数值精确匹配",
                "score": 0,
                "max_score": 40,
                "passed": False,
                "reason": "至少一个组的差值不符合预期"
            })
    else:
        details.append({
            "item": "数值精确匹配",
            "score": 0,
            "max_score": 40,
            "passed": False,
            "reason": "前置条件（records长度/字段完整性）未满足"
        })

    total_score = sum(d["score"] for d in details)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2)

if __name__ == "__main__":
    main()
