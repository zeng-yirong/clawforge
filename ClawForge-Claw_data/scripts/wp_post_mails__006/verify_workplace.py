import json
import os
import sys
import glob

def verify(workspace):
    issues = []
    details = []
    total_score = 0
    max_total = 100

    # 1. 检查结果目录和文件存在 (10 分)
    result_dir = os.path.join(workspace, "reports")
    result_file = os.path.join(result_dir, "community_priority.json")
    if not os.path.isdir(result_dir):
        details.append({"item": "reports directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "reports/ 目录不存在"})
    elif not os.path.isfile(result_file):
        details.append({"item": "community_priority.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "reports/community_priority.json 文件不存在"})
    else:
        details.append({"item": "结果文件存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
        total_score += 10

    # 2. 解析结果文件格式 (10 分)
    if os.path.isfile(result_file):
        try:
            with open(result_file, "r") as f:
                result_data = json.load(f)
            if not isinstance(result_data, list):
                details.append({"item": "JSON 格式为数组", "score": 0, "max_score": 10, "passed": False, "reason": "根元素不是 list"})
            else:
                details.append({"item": "JSON 格式正确", "score": 10, "max_score": 10, "passed": True, "reason": "是合法的 JSON 数组"})
                total_score += 10
        except (json.JSONDecodeError, IOError) as e:
            details.append({"item": "JSON 可解析", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {e}"})
    else:
        details.append({"item": "JSON 解析", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在，跳过"})

    # 3. 计算标准答案（从 data/social 读取，模拟 agent 的正确操作）
    expected_result = None
    social_dir = os.path.join(workspace, "data", "social")
    if os.path.isdir(social_dir):
        community_counts = {}
        for fname in os.listdir(social_dir):
            if not fname.endswith(".json"):
                continue
            fpath = os.path.join(social_dir, fname)
            try:
                with open(fpath, "r") as f:
                    post = json.load(f)
                if post.get("needs_response") == True:
                    comm = post.get("community", "unknown")
                    community_counts[comm] = community_counts.get(comm, 0) + 1
            except:
                pass
        sorted_items = sorted(community_counts.items(), key=lambda x: (-x[1], x[0]))
        expected_result = [{"community": comm, "count": cnt} for comm, cnt in sorted_items]

    # 4. 内容准确性 (70 分)
    if expected_result is None:
        details.append({"item": "无法计算标准答案", "score": 0, "max_score": 70, "passed": False, "reason": "data/social 目录不存在或为空"})
    elif not os.path.isfile(result_file):
        details.append({"item": "结果内容匹配", "score": 0, "max_score": 70, "passed": False, "reason": "无结果文件"})
    else:
        # 比较长度
        if len(result_data) != len(expected_result):
            details.append({"item": "条目数量正确", "score": 0, "max_score": 10, "passed": False, "reason": f"条目数不符，期望 {len(expected_result)}，实际 {len(result_data)}"})
        else:
            details.append({"item": "条目数量正确", "score": 10, "max_score": 10, "passed": True, "reason": "条目数一致"})
            total_score += 10

        # 逐条比较社区和 count
        match_score = 0
        max_match = 60
        max_items = min(len(result_data), len(expected_result)) if isinstance(result_data, list) else 0
        matched = 0
        for i in range(max_items):
            er = expected_result[i]
            ar = result_data[i]
            if not isinstance(ar, dict):
                continue
            if ar.get("community") == er["community"] and ar.get("count") == er["count"]:
                matched += 1
        if matched == len(expected_result) and matched == len(result_data):
            match_score = max_match
        else:
            # 按匹配比例给分（至少需要匹配顺序正确）
            match_score = int(max_match * matched / len(expected_result)) if len(expected_result) > 0 else 0
        details.append({"item": "社区与计数按降序匹配", "score": match_score, "max_score": max_match, "passed": match_score == max_match, "reason": f"匹配 {matched}/{len(expected_result)} 条，排序需正确"})
        total_score += match_score

        # 额外扣分：如果结果中有其他字段
        extra_fields = False
        for item in result_data:
            if isinstance(item, dict):
                keys = set(item.keys())
                if keys != {"community", "count"}:
                    extra_fields = True
        if extra_fields:
            details.append({"item": "无多余字段", "score": 0, "max_score": 0, "passed": False, "reason": "结果中包含 community/count 之外的字段，扣减 10 分以示惩罚（不计入最大分）"})
            total_score = max(0, total_score - 10)  # 实际扣分
        else:
            details.append({"item": "无多余字段", "score": 0, "max_score": 0, "passed": True, "reason": "无额外字段"})

    # 5. 计算最终总分 (0-100)
    final_score = min(total_score, 100)
    # 确保分数为整数
    result = {
        "total_score": final_score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    return result

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
