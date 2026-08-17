import sys
import os
import json
import re

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = {"total_score": 0, "details": []}
    total_max = 100

    # 检查目标文件
    review_path = os.path.join(workspace, "research", "review.md")
    if not os.path.isfile(review_path):
        result["details"].append({
            "item": "research/review.md 存在",
            "score": 0, "max_score": 10,
            "passed": False,
            "reason": "文件不存在"
        })
        result["total_score"] = 0
        _write_score(result, workspace)
        return
    else:
        result["details"].append({
            "item": "research/review.md 存在",
            "score": 10, "max_score": 10,
            "passed": True,
            "reason": "文件存在"
        })

    # 读取 review.md 内容
    with open(review_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 检查是否有非空文本内容（除 mermaid 代码块外）
    text_only = re.sub(r'```[a-zA-Z]*\n.*?```', '', content, flags=re.DOTALL)
    text_only = text_only.strip()
    if len(text_only) >= 100:
        result["details"].append({
            "item": "review.md 包含足够的综述文本（≥100字符）",
            "score": 10, "max_score": 10,
            "passed": True,
            "reason": f"文本长度 {len(text_only)}"
        })
    else:
        result["details"].append({
            "item": "review.md 包含足够的综述文本（≥100字符）",
            "score": 0, "max_score": 10,
            "passed": False,
            "reason": f"文本长度 {len(text_only)}，不足100"
        })

    # 提取 mermaid 代码块
    mermaid_blocks = re.findall(r'```mermaid\s*\n(.*?)\n\s*```', content, re.DOTALL)
    if not mermaid_blocks:
        result["details"].append({
            "item": "包含 Mermaid 代码块",
            "score": 0, "max_score": 10,
            "passed": False,
            "reason": "未找到 mermaid 代码块"
        })
    else:
        result["details"].append({
            "item": "包含 Mermaid 代码块",
            "score": 10, "max_score": 10,
            "passed": True,
            "reason": "找到 mermaid 代码块"
        })
        mermaid_code = mermaid_blocks[0]  # take first

        # 解析 timeline 节点
        timeline_nodes = re.findall(r'^\s*(\d{4})\s*:\s*(.+)', mermaid_code, re.MULTILINE)
        actual_list = [(int(year), title.strip()) for year, title in timeline_nodes]
    # 计算预期列表
    papers_path = os.path.join(workspace, "data", "papers", "papers.json")
    if not os.path.isfile(papers_path):
        result["details"].append({
            "item": "数据文件存在",
            "score": 0, "max_score": 0,  # 不扣分，因为数据是环境提供的，但缺失则无法验证
            "passed": False,
            "reason": "data/papers/papers.json 缺失"
        })
        _write_score(result, workspace)
        return
    with open(papers_path, "r") as f:
        data = json.load(f)
    all_papers = data.get("papers", [])
    expected = []
    for p in all_papers:
        if p.get("direction") == "tool_augmented_reasoning" and p.get("year", 0) >= 2020:
            expected.append((p["year"], p["title"]))
    # 按年份排序，同年按标题排序
    expected.sort(key=lambda x: (x[0], x[1]))
    expected_titles = [t for _, t in expected]
    expected_years = [y for y, _ in expected]

    # 检查论文匹配
    if not mermaid_blocks:
        match_score = 0
        reason = "无 mermaid 代码块，无法匹配"
    else:
        actual_titles = [t for _, t in actual_list]
        actual_years = [y for y, _ in actual_list]
        # 检查顺序和内容完全一致
        if actual_list == expected:
            match_score = 50
            reason = f"完全匹配预期论文列表：{expected}"
        else:
            # 计算匹配比例：检查每个位置是否都正确
            correct = 0
            for ae in expected:
                if ae in actual_list:
                    correct += 1
            match_score = int(50 * correct / len(expected)) if len(expected) > 0 else 0
            reason = f"部分匹配：实际 {actual_list}，预期 {expected}"
        # 额外检查顺序是否正确（如果长度一致且内容一致但顺序不同）
        if set(actual_list) == set(expected) and actual_list != expected:
            match_score = min(match_score, 40)  # 扣10分排序
            reason += "；但顺序不正确"
    result["details"].append({
        "item": "论文列表完全匹配（包含年份和标题）",
        "score": match_score,
        "max_score": 50,
        "passed": match_score == 50,
        "reason": reason
    })

    # 检查是否有多余的论文（出现在 mermaid 中但不在预期中）
    if mermaid_blocks:
        extra_found = False
        for node in actual_list:
            if node not in expected:
                extra_found = True
                break
        if extra_found:
            result["details"].append({
                "item": "无多余论文节点",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"发现多余节点：{actual_list}"
            })
        else:
            result["details"].append({
                "item": "无多余论文节点",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "所有 mermaid 节点均在预期中"
            })
    else:
        result["details"].append({
            "item": "无多余论文节点",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "无 mermaid 代码块"
        })

    # 检查排序（已包含在匹配中？但额外给出10分排序项）
    if mermaid_blocks and actual_list == expected:
        sort_score = 10
        sort_pass = True
        sort_reason = "年份升序，同年按标题字母序"
    else:
        sort_score = 0
        sort_pass = False
        sort_reason = "顺序不符合预期"
    result["details"].append({
        "item": "节点按年份升序排列（同一年按标题字母序）",
        "score": sort_score,
        "max_score": 10,
        "passed": sort_pass,
        "reason": sort_reason
    })

    # 计算总分
    total = sum(d["score"] for d in result["details"])
    result["total_score"] = total
    _write_score(result, workspace)

def _write_score(result, workspace):
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written to {score_path}: {result['total_score']}/100")

if __name__ == "__main__":
    main()
