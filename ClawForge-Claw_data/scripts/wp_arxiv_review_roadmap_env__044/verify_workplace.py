import sys
import os
import json

def verify(workspace):
    # 工作区路径
    cwd = workspace if workspace != "." else os.getcwd()
    # 初始化得分明细
    details = []
    total_score = 0

    # ========== 1. 检查 docs/ 目录是否存在 (10分) ==========
    docs_path = os.path.join(cwd, "docs")
    if os.path.isdir(docs_path):
        details.append({
            "item": "docs directory exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "docs/ 目录存在"
        })
        total_score += 10
    else:
        details.append({
            "item": "docs directory exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "docs/ 目录不存在"
        })

    # ========== 2. 检查 filtered_papers.json 是否存在且合法JSON (10分) ==========
    filtered_path = os.path.join(docs_path, "filtered_papers.json")
    json_valid = False
    filtered_data = None
    if os.path.isfile(filtered_path):
        try:
            with open(filtered_path, "r") as f:
                filtered_data = json.load(f)
            json_valid = True
            details.append({
                "item": "filtered_papers.json exists and valid JSON",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "文件存在且为合法JSON"
            })
            total_score += 10
        except (json.JSONDecodeError, Exception) as e:
            details.append({
                "item": "filtered_papers.json exists and valid JSON",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"JSON解析失败: {str(e)}"
            })
    else:
        details.append({
            "item": "filtered_papers.json exists and valid JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件不存在"
        })

    # ========== 3. 检查 filtered_papers.json 内容正确性 (60分) ==========
    # 预期答案：所有 direction == "efficient_vision" 的论文ID按年份升序
    # 从原始 papers.json 读取真实数据（注意只读 data/papers/papers.json）
    papers_path = os.path.join(cwd, "data/papers/papers.json")
    expected_ids = []
    content_score = 0
    max_content = 60
    if os.path.isfile(papers_path) and json_valid:
        try:
            with open(papers_path, "r") as f:
                papers_data = json.load(f)
            all_papers = papers_data.get("papers", [])
            # 提取 direction 精确等于 "efficient_vision" 的论文
            target_papers = [p for p in all_papers if p.get("direction") == "efficient_vision"]
            # 按年份排序
            target_papers.sort(key=lambda x: x["year"])
            expected_ids = [p["paper_id"] for p in target_papers]

            # 检查 filtered_papers.json 的内容必须是列表
            if isinstance(filtered_data, list):
                actual_ids = filtered_data
                # 比较
                if actual_ids == expected_ids:
                    details.append({
                        "item": "filtered_papers.json content correct",
                        "score": 60,
                        "max_score": 60,
                        "passed": True,
                        "reason": f"论文ID列表与预期完全一致 ({len(expected_ids)}篇)"
                    })
                    content_score = 60
                    total_score += 60
                else:
                    # 部分正确但顺序或内容不同，给部分分
                    # 先检查是否是多出了或少了
                    extra = set(actual_ids) - set(expected_ids)
                    missing = set(expected_ids) - set(actual_ids)
                    # 检查顺序：如果ID集合一样但顺序不对，扣20分
                    if set(actual_ids) == set(expected_ids):
                        if actual_ids == expected_ids:
                            # 已经进入前面分支
                            pass
                        else:
                            # 集合相同但顺序错误
                            details.append({
                                "item": "filtered_papers.json content correct",
                                "score": 40,
                                "max_score": 60,
                                "passed": False,
                                "reason": "论文ID集合正确但未按年份升序排序"
                            })
                            content_score = 40
                            total_score += 40
                    else:
                        # 有缺失或多出
                        reason_parts = []
                        if missing:
                            reason_parts.append(f"缺少论文: {sorted(missing)}")
                        if extra:
                            reason_parts.append(f"多余的论文: {sorted(extra)}")
                        details.append({
                            "item": "filtered_papers.json content correct",
                            "score": 0,
                            "max_score": 60,
                            "passed": False,
                            "reason": "; ".join(reason_parts) if reason_parts else "内容不正确"
                        })
                    # 如果内容不是列表但JSON合法，给部分分？此处处理
            else:
                details.append({
                    "item": "filtered_papers.json content correct",
                    "score": 0,
                    "max_score": 60,
                    "passed": False,
                    "reason": "文件内容不是JSON列表"
                })
        except Exception as e:
            details.append({
                "item": "filtered_papers.json content correct",
                "score": 0,
                "max_score": 60,
                "passed": False,
                "reason": f"读取原始papers.json出错: {str(e)}"
            })
    else:
        details.append({
            "item": "filtered_papers.json content correct",
            "score": 0,
            "max_score": 60,
            "passed": False,
            "reason": "基础校验未通过（papers.json不存在或filtered_papers.json非法）"
        })

    # ========== 4. 检查 review.md 是否存在并包含研究方向关键字 (15分) ==========
    review_path = os.path.join(docs_path, "review.md")
    review_score = 0
    if os.path.isfile(review_path):
        try:
            with open(review_path, "r", encoding="utf-8") as f:
                content = f.read()
            if "efficient_vision" in content.lower():  # 不区分大小写
                details.append({
                    "item": "review.md exists and mentions research direction",
                    "score": 15,
                    "max_score": 15,
                    "passed": True,
                    "reason": "review.md存在且包含'efficient_vision'字样"
                })
                review_score = 15
                total_score += 15
            else:
                details.append({
                    "item": "review.md exists and mentions research direction",
                    "score": 5,
                    "max_score": 15,
                    "passed": False,
                    "reason": "review.md存在但未提及研究方向'efficient_vision'"
                })
                review_score = 5
                total_score += 5
        except Exception as e:
            details.append({
                "item": "review.md exists and mentions research direction",
                "score": 0,
                "max_score": 15,
                "passed": False,
                "reason": f"读取review.md出错: {str(e)}"
            })
    else:
        details.append({
            "item": "review.md exists and mentions research direction",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": "review.md文件不存在"
        })

    # ========== 5. 检查 roadmap.mermaid 是否存在并包含 Mermaid 标记 (15分) ==========
    roadmap_path = os.path.join(docs_path, "roadmap.mermaid")
    if os.path.isfile(roadmap_path):
        try:
            with open(roadmap_path, "r", encoding="utf-8") as f:
                content = f.read()
            # 检查是否包含常见的Mermaid图标记（如graph, flowchart, mindmap等）
            if "graph" in content.lower() or "flowchart" in content.lower() or "mermaid" in content.lower():
                details.append({
                    "item": "roadmap.mermaid exists and contains Mermaid graph syntax",
                    "score": 15,
                    "max_score": 15,
                    "passed": True,
                    "reason": "roadmap.mermaid存在且包含Mermaid图标记"
                })
                total_score += 15
            else:
                details.append({
                    "item": "roadmap.mermaid exists and contains Mermaid graph syntax",
                    "score": 5,
                    "max_score": 15,
                    "passed": False,
                    "reason": "roadmap.mermaid存在但未发现Mermaid图语法"
                })
                total_score += 5
        except Exception as e:
            details.append({
                "item": "roadmap.mermaid exists and contains Mermaid graph syntax",
                "score": 0,
                "max_score": 15,
                "passed": False,
                "reason": f"读取roadmap.mermaid出错: {str(e)}"
            })
    else:
        details.append({
            "item": "roadmap.mermaid exists and contains Mermaid graph syntax",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": "roadmap.mermaid文件不存在"
        })

    # 写入最终总分
    final_score = total_score  # 0-100
    result = {
        "total_score": final_score,
        "details": details
    }
    output_path = os.path.join(cwd, "workplace_score.json")
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
    
    return final_score

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
