#!/usr/bin/env python3
"""
验证工作区中 ops/deny_list.json 是否包含正确的拒绝列表。
评分维度：
  - 目录结构 (10分)：ops 目录存在，且 denylist 文件存在
  - JSON 合法性 (10分)：文件为合法 JSON 且为数组
  - 内容正确性 (80分)：数组内容与期望的请求 ID 完全一致（顺序无关）
    每个期望 ID 出现 1 次得 26.67 分（共80/3=26.666，取整后按比例），
    缺少一个扣 26.67，多出一个扣 10，直至 0 分。
"""

import json
import sys
import pathlib

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    ws = pathlib.Path(workspace).resolve()
    
    details = []
    total_score = 0
    
    # ---------- 1. 目录结构 (10分) ----------
    ops_dir = ws / "ops"
    denylist_path = ops_dir / "deny_list.json"
    
    dir_exists = ops_dir.is_dir()
    file_exists = denylist_path.is_file()
    
    if dir_exists and file_exists:
        score_dir = 10
        details.append({
            "item": "目录结构 (ops/deny_list.json 存在)",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "ops 目录和 deny_list.json 均存在"
        })
    elif dir_exists and not file_exists:
        score_dir = 0
        details.append({
            "item": "目录结构 (ops/deny_list.json 存在)",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ops 目录存在但 deny_list.json 文件缺失"
        })
    else:
        score_dir = 0
        details.append({
            "item": "目录结构 (ops/deny_list.json 存在)",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ops 目录或 deny_list.json 文件缺失"
        })
    total_score += score_dir
    
    # ---------- 2. JSON 合法性 (10分) ----------
    if file_exists:
        try:
            with open(denylist_path, 'r') as f:
                content = json.load(f)
            if isinstance(content, list):
                score_json = 10
                details.append({
                    "item": "JSON 合法性 (合法数组)",
                    "score": 10,
                    "max_score": 10,
                    "passed": True,
                    "reason": "文件为合法 JSON 且内容为数组"
                })
            else:
                score_json = 0
                details.append({
                    "item": "JSON 合法性 (合法数组)",
                    "score": 0,
                    "max_score": 10,
                    "passed": False,
                    "reason": f"JSON 不是数组，实际类型: {type(content).__name__}"
                })
        except (json.JSONDecodeError, IOError) as e:
            score_json = 0
            details.append({
                "item": "JSON 合法性 (合法数组)",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"文件无法解析为 JSON: {e}"
            })
    else:
        score_json = 0
        details.append({
            "item": "JSON 合法性 (合法数组)",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件不存在，无法检查 JSON 合法性"
        })
    total_score += score_json
    
    # ---------- 3. 内容正确性 (80分) ----------
    expected_ids = {"REQ-101", "REQ-102", "REQ-103"}
    max_content = 80
    
    if file_exists and isinstance(content, list):
        actual_ids = set(content)
        # 检查是否有重复项
        if len(actual_ids) != len(content):
            # 有重复项，扣分
            duplicates = len(content) - len(actual_ids)
            # 记过一次
            details.append({
                "item": "内容正确性 (无重复项)",
                "score": 0,
                "max_score": 0,  # 不单独占分，但影响正确性
                "passed": False,
                "reason": f"列表中存在重复项，数量: {duplicates}"
            })
            # 重复项导致不能信任集合，直接取实际列表去重后计算
            # 但我们依然用集合比较，只计不重复项
        # 计算得分
        correct = actual_ids & expected_ids
        extra = actual_ids - expected_ids
        missing = expected_ids - actual_ids
        
        # 每个正确项得分上限 80/3 ≈ 26.667，但为了整数可累加，我们按比例计算
        # 简单处理：正确项每个得 26，剩余的2分再分配
        # 实际用浮点数，最后四舍五入
        base_each = max_content / len(expected_ids)  # 26.66666...
        score_correct = len(correct) * base_each
        # 额外项扣分：每个额外项扣 base_each
        penalty_extra = len(extra) * base_each
        # 缺失项扣分：每个缺失项扣 base_each
        penalty_missing = len(missing) * base_each
        raw_score = max(0, score_correct - penalty_extra - penalty_missing)
        score_content = round(raw_score)
        # 封顶不超过 max_content
        score_content = min(score_content, max_content)
        
        reason_parts = []
        if correct:
            reason_parts.append(f"正确项: {sorted(correct)}")
        if missing:
            reason_parts.append(f"缺少: {sorted(missing)}")
        if extra:
            reason_parts.append(f"多余: {sorted(extra)}")
        reason = "; ".join(reason_parts) if reason_parts else "完全正确"
        
        details.append({
            "item": "内容正确性 (请求ID列表)",
            "score": score_content,
            "max_score": max_content,
            "passed": score_content == max_content,
            "reason": reason
        })
        total_score += score_content
    elif file_exists and not isinstance(content, list):
        # 已经记录过 JSON 类型错误，这里直接给0
        details.append({
            "item": "内容正确性 (请求ID列表)",
            "score": 0,
            "max_score": max_content,
            "passed": False,
            "reason": "不是数组，无法计算正确性"
        })
    else:
        details.append({
            "item": "内容正确性 (请求ID列表)",
            "score": 0,
            "max_score": max_content,
            "passed": False,
            "reason": "文件不存在或无法读取"
        })
    
    # 确保总分在0-100之间
    total_score = max(0, min(100, total_score))
    
    # 写入评分结果
    result = {
        "total_score": total_score,
        "details": details
    }
    with open(ws / "workplace_score.json", 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"验证完成，总分: {total_score}/100")
    sys.exit(0 if total_score >= 100 else 1)

if __name__ == "__main__":
    main()
