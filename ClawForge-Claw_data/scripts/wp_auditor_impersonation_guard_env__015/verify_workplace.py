import os
import sys
import json

def verify(workspace):
    # 预期结果：三个冒充请求ID（按字母排序）
    expected_ids = sorted(["REQ-008", "REQ-009", "REQ-010"])  # 与env_builder生成一致

    details = []
    total_score = 0

    # 1. 检查ops目录是否存在
    ops_dir = os.path.join(workspace, "ops")
    dir_exists = os.path.isdir(ops_dir)
    details.append({
        "item": "ops directory exists",
        "score": 10 if dir_exists else 0,
        "max_score": 10,
        "passed": dir_exists,
        "reason": "ops directory found" if dir_exists else "ops directory not found"
    })
    total_score += 10 if dir_exists else 0

    # 2. 检查deny_list.json文件是否存在
    deny_file = os.path.join(ops_dir, "deny_list.json") if dir_exists else None
    file_exists = deny_file and os.path.isfile(deny_file)
    details.append({
        "item": "ops/deny_list.json exists",
        "score": 20 if file_exists else 0,
        "max_score": 20,
        "passed": file_exists,
        "reason": "file found" if file_exists else "file not found"
    })
    total_score += 20 if file_exists else 0

    # 3. 解析文件内容
    if file_exists:
        try:
            with open(deny_file, "r") as f:
                content = json.load(f)
        except (json.JSONDecodeError, Exception) as e:
            details.append({
                "item": "deny_list.json is valid JSON",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"Invalid JSON: {e}"
            })
            total_score += 0
            # 无法继续检查内容
            content = None
        else:
            details.append({
                "item": "deny_list.json is valid JSON",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "JSON parsed successfully"
            })
            total_score += 10

            # 4. 检查内容格式：应为列表
            if isinstance(content, list):
                details.append({
                    "item": "content is a list",
                    "score": 10,
                    "max_score": 10,
                    "passed": True,
                    "reason": "list type"
                })
                total_score += 10

                # 5. 检查元素是否都是字符串且为请求ID格式
                all_strings = all(isinstance(item, str) for item in content)
                if all_strings:
                    details.append({
                        "item": "all elements are strings",
                        "score": 10,
                        "max_score": 10,
                        "passed": True,
                        "reason": "all string elements"
                    })
                    total_score += 10
                else:
                    details.append({
                        "item": "all elements are strings",
                        "score": 0,
                        "max_score": 10,
                        "passed": False,
                        "reason": "non-string elements found"
                    })

                # 6. 排序后与期望列表比较
                sorted_content = sorted(content)
                if sorted_content == expected_ids:
                    details.append({
                        "item": "denied request IDs match expected (sorted)",
                        "score": 40,
                        "max_score": 40,
                        "passed": True,
                        "reason": f"Exact match: {sorted_content}"
                    })
                    total_score += 40
                else:
                    # 计算部分得分：正确个数
                    matched = sum(1 for id_ in sorted_content if id_ in expected_ids)
                    extra = [id_ for id_ in sorted_content if id_ not in expected_ids]
                    missing = [id_ for id_ in expected_ids if id_ not in sorted_content]
                    # 扣分：每个错误扣10分，最多扣40
                    penalty = min(40, (len(extra) + len(missing)) * 10)
                    score = max(0, 40 - penalty)
                    details.append({
                        "item": "denied request IDs match expected (sorted)",
                        "score": score,
                        "max_score": 40,
                        "passed": sorted_content == expected_ids,
                        "reason": f"Matched {matched}/{len(expected_ids)}; extra={extra}, missing={missing}"
                    })
                    total_score += score
            else:
                details.append({
                    "item": "content is a list",
                    "score": 0,
                    "max_score": 10,
                    "passed": False,
                    "reason": f"Expected list, got {type(content).__name__}"
                })
                # 无法继续检查元素类型和比较
                details.append({
                    "item": "all elements are strings",
                    "score": 0,
                    "max_score": 10,
                    "passed": False,
                    "reason": "content not a list"
                })
                details.append({
                    "item": "denied request IDs match expected (sorted)",
                    "score": 0,
                    "max_score": 40,
                    "passed": False,
                    "reason": "content not a list"
                })
    else:
        # 文件不存在，剩余项目0分
        details.append({
            "item": "deny_list.json is valid JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "file not found"
        })
        details.append({
            "item": "content is a list",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "file not found"
        })
        details.append({
            "item": "all elements are strings",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "file not found"
        })
        details.append({
            "item": "denied request IDs match expected (sorted)",
            "score": 0,
            "max_score": 40,
            "passed": False,
            "reason": "file not found"
        })

    # 确保总分不超过100
    total_score = min(total_score, 100)
    result = {
        "total_score": total_score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

    print(f"Verification complete. Total score: {total_score}/100")

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
