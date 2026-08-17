import os
import json
import sys

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    total_score = 0
    max_total = 100
    details = []

    # 检查目录结构
    ops_dir = os.path.join(workspace, "ops")
    db_dumps_dir = os.path.join(workspace, "db_dumps")
    dirs_ok = os.path.isdir(ops_dir) and os.path.isdir(db_dumps_dir)
    if dirs_ok:
        details.append({
            "item": "目录结构完整性 (ops/, db_dumps/)",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "ops/ 和 db_dumps/ 均存在"
        })
        total_score += 10
    else:
        missing = []
        if not os.path.isdir(ops_dir):
            missing.append("ops/")
        if not os.path.isdir(db_dumps_dir):
            missing.append("db_dumps/")
        details.append({
            "item": "目录结构完整性 (ops/, db_dumps/)",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"缺少目录: {', '.join(missing)}"
        })

    # 检查产物文件 ops/kill_target.json
    target_path = os.path.join(workspace, "ops", "kill_target.json")
    if not os.path.isfile(target_path):
        details.append({
            "item": "产物文件 ops/kill_target.json 存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件不存在"
        })
        # 但是继续执行后续检查以输出完整报告，但后面会因为没有文件而失败
    else:
        details.append({
            "item": "产物文件 ops/kill_target.json 存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "文件存在"
        })
        total_score += 10

        # 检查 JSON 合法性
        try:
            with open(target_path, "r") as f:
                data = json.load(f)
            # 检查是否为对象
            if not isinstance(data, dict):
                details.append({
                    "item": "JSON 格式合法且为对象",
                    "score": 0,
                    "max_score": 10,
                    "passed": False,
                    "reason": "JSON 不是对象"
                })
            else:
                details.append({
                    "item": "JSON 格式合法且为对象",
                    "score": 10,
                    "max_score": 10,
                    "passed": True,
                    "reason": "合法 JSON 对象"
                })
                total_score += 10

                # 检查关键字段 transaction_id
                if "transaction_id" not in data:
                    details.append({
                        "item": "包含字段 transaction_id",
                        "score": 0,
                        "max_score": 20,
                        "passed": False,
                        "reason": "缺少 transaction_id 字段"
                    })
                else:
                    details.append({
                        "item": "包含字段 transaction_id",
                        "score": 20,
                        "max_score": 20,
                        "passed": True,
                        "reason": "字段存在"
                    })
                    total_score += 20

                    # 检查值是否为字符串且正确
                    tx_id = data["transaction_id"]
                    if not isinstance(tx_id, str):
                        details.append({
                            "item": "transaction_id 值为字符串",
                            "score": 0,
                            "max_score": 10,
                            "passed": False,
                            "reason": f"值类型为 {type(tx_id).__name__}，期望 str"
                        })
                    else:
                        if tx_id == "tx_2025032108":
                            details.append({
                                "item": "transaction_id 值正确",
                                "score": 30,
                                "max_score": 30,
                                "passed": True,
                                "reason": f"值为 {tx_id}"
                            })
                            total_score += 30
                        else:
                            details.append({
                                "item": "transaction_id 值正确",
                                "score": 0,
                                "max_score": 30,
                                "passed": False,
                                "reason": f"值为 {tx_id}，期望 tx_2025032108"
                            })

                # 检查是否有多余字段（只允许 transaction_id）
                allowed = ["transaction_id"]
                extra = [k for k in data if k not in allowed]
                if extra:
                    details.append({
                        "item": "无多余字段",
                        "score": 0,
                        "max_score": 10,
                        "passed": False,
                        "reason": f"多余字段: {extra}"
                    })
                else:
                    details.append({
                        "item": "无多余字段",
                        "score": 10,
                        "max_score": 10,
                        "passed": True,
                        "reason": "没有多余字段"
                    })
                    total_score += 10

        except json.JSONDecodeError as e:
            details.append({
                "item": "JSON 格式合法",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"JSON 解析失败: {e}"
            })
        except Exception as e:
            details.append({
                "item": "文件读取正常",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"读取异常: {e}"
            })

    # 确保总分不超过 100
    total_score = min(total_score, 100)
    result = {
        "total_score": total_score,
        "details": details
    }
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Verification complete. Total score: {total_score}/100")

if __name__ == "__main__":
    main()
