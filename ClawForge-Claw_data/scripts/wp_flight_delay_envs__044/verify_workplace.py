import sys
import json
import csv
import os
from pathlib import Path

def verify(workspace: str):
    workspace_path = Path(workspace).resolve()
    score_details = []
    total_score = 0

    # 1. Check ops directory exists
    ops_dir = workspace_path / "ops"
    dir_exists = ops_dir.is_dir()
    score_details.append({
        "item": "ops 目录存在",
        "score": 10 if dir_exists else 0,
        "max_score": 10,
        "passed": dir_exists,
        "reason": "目录存在" if dir_exists else "缺少 ops/ 目录"
    })
    if dir_exists:
        total_score += 10

    # 2. Check impacted_orders.json exists
    orders_file = ops_dir / "impacted_orders.json"
    orders_exists = orders_file.is_file()
    score_details.append({
        "item": "impacted_orders.json 文件存在",
        "score": 10 if orders_exists else 0,
        "max_score": 10,
        "passed": orders_exists,
        "reason": "文件存在" if orders_exists else "缺少 impacted_orders.json"
    })
    if orders_exists:
        total_score += 10

    # 3. Check notify_list.csv exists
    csv_file = ops_dir / "notify_list.csv"
    csv_exists = csv_file.is_file()
    score_details.append({
        "item": "notify_list.csv 文件存在",
        "score": 10 if csv_exists else 0,
        "max_score": 10,
        "passed": csv_exists,
        "reason": "文件存在" if csv_exists else "缺少 notify_list.csv"
    })
    if csv_exists:
        total_score += 10

    # 4. Validate impacted_orders.json content
    orders_valid = False
    orders_correct = False
    expected_ids = {"HB-003", "TB-003"}
    if orders_exists:
        try:
            with open(orders_file, "r") as f:
                data = json.load(f)
            if isinstance(data, list) and len(data) == 2:
                orders_valid = True
                total_score += 10
                score_details.append({
                    "item": "impacted_orders.json 格式合法且为包含2个元素的数组",
                    "score": 10,
                    "max_score": 10,
                    "passed": True,
                    "reason": "合法的JSON数组，长度正确"
                })
                # 检查内容 (集合比较)
                ids_set = set(data)
                if ids_set == expected_ids:
                    orders_correct = True
                    total_score += 20
                    score_details.append({
                        "item": "impacted_orders.json 内容完全正确 (HB-003, TB-003)",
                        "score": 20,
                        "max_score": 20,
                        "passed": True,
                        "reason": "ID 集合匹配"
                    })
                else:
                    score_details.append({
                        "item": "impacted_orders.json 内容正确",
                        "score": 0,
                        "max_score": 20,
                        "passed": False,
                        "reason": f"期望 {expected_ids}，实际 {ids_set}"
                    })
            else:
                score_details.append({
                    "item": "impacted_orders.json 格式合法且为包含2个元素的数组",
                    "score": 0,
                    "max_score": 10,
                    "passed": False,
                    "reason": f"类型或长度错误: {type(data)} 长度={len(data) if isinstance(data, list) else 'N/A'}"
                })
        except (json.JSONDecodeError, Exception) as e:
            score_details.append({
                "item": "impacted_orders.json 解析",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"JSON解析失败: {str(e)}"
            })
            score_details.append({
                "item": "impacted_orders.json 内容正确",
                "score": 0,
                "max_score": 20,
                "passed": False,
                "reason": "因格式错误无法验证内容"
            })
    else:
        score_details.append({
            "item": "impacted_orders.json 格式合法且为包含2个元素的数组",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件不存在"
        })
        score_details.append({
            "item": "impacted_orders.json 内容正确",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "文件不存在"
        })

    # 5. Validate notify_list.csv
    csv_valid = False
    csv_correct = False
    expected_emails = {"john.smith@example.com", "jane.doe@example.com"}
    if csv_exists:
        try:
            with open(csv_file, newline='') as f:
                reader = csv.reader(f)
                rows = list(reader)
            # 检查标题
            if len(rows) >= 1 and rows[0] == ["email"]:
                csv_valid = True
                total_score += 10
                score_details.append({
                    "item": "notify_list.csv 格式合法（标题行正确）",
                    "score": 10,
                    "max_score": 10,
                    "passed": True,
                    "reason": "标题行为 ['email']"
                })
                # 收集后续行的邮箱（跳过标题）
                email_rows = [row[0].strip() for row in rows[1:] if len(row) > 0]
                email_set = set(email_rows)
                if len(email_rows) == 2 and email_set == expected_emails:
                    csv_correct = True
                    total_score += 30
                    score_details.append({
                        "item": "notify_list.csv 邮箱内容正确（2个邮箱）",
                        "score": 30,
                        "max_score": 30,
                        "passed": True,
                        "reason": f"邮箱集合正确: {email_set}"
                    })
                else:
                    score_details.append({
                        "item": "notify_list.csv 邮箱内容正确（2个邮箱）",
                        "score": 0,
                        "max_score": 30,
                        "passed": False,
                        "reason": f"期望 {expected_emails} (2个)，实际 {email_set} (数量 {len(email_rows)})"
                    })
            else:
                score_details.append({
                    "item": "notify_list.csv 格式合法（标题行正确）",
                    "score": 0,
                    "max_score": 10,
                    "passed": False,
                    "reason": f"标题行错误: {rows[0] if rows else '空文件'}"
                })
                score_details.append({
                    "item": "notify_list.csv 邮箱内容正确（2个邮箱）",
                    "score": 0,
                    "max_score": 30,
                    "passed": False,
                    "reason": "因标题行错误无法验证内容"
                })
        except Exception as e:
            score_details.append({
                "item": "notify_list.csv 解析",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"CSV解析失败: {str(e)}"
            })
            score_details.append({
                "item": "notify_list.csv 邮箱内容正确（2个邮箱）",
                "score": 0,
                "max_score": 30,
                "passed": False,
                "reason": "因解析失败无法验证内容"
            })
    else:
        score_details.append({
            "item": "notify_list.csv 格式合法（标题行正确）",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件不存在"
        })
        score_details.append({
            "item": "notify_list.csv 邮箱内容正确（2个邮箱）",
            "score": 0,
            "max_score": 30,
            "passed": False,
            "reason": "文件不存在"
        })

    # 总分强制整数
    total_score = min(total_score, 100)
    result = {
        "total_score": total_score,
        "details": score_details
    }
    with open(workspace_path / "workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

    print(f"Verification complete. Total score: {total_score}/100")

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
