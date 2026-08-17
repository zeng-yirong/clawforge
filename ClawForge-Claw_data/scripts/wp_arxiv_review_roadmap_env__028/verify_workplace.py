import json
import os
import sys
import re

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0
    max_total = 100

    # 辅助函数
    def read_file(path):
        full = os.path.join(workspace, path)
        if not os.path.isfile(full):
            return None
        with open(full, "r", encoding="utf-8", errors="replace") as f:
            return f.read()

    # 期望的论文标题（高效视觉方向）
    ev_titles = [
        "Efficient Vision Transformer",
        "MobileViT: Lightweight Vision Transformer",
        "FastViT: Speed-Optimized Vision Transformer"
    ]
    # 干扰论文标题
    distractor_titles = [
        "Tool-Augmented Reasoning with LLMs",
        "ReAct: Synergizing Reasoning and Acting"
    ]
    # 附件关键短语
    key_phrase = "Key insight: Vision Transformers achieve state-of-the-art on ImageNet."

    # ---------- 1. 文件存在性 (10分) ----------
    score_exist = 0
    max_exist = 10
    items_exist = []
    for fname in ["review.md", "roadmap.md"]:
        full_path = os.path.join(workspace, fname)
        exists = os.path.isfile(full_path)
        s = 5 if exists else 0
        items_exist.append({
            "item": f"File {fname} exists",
            "score": s,
            "max_score": 5,
            "passed": exists,
            "reason": "Found" if exists else "Not found"
        })
        score_exist += s
    details.extend(items_exist)
    total_score += score_exist

    # ---------- 2. review.md 内容 (50分) ----------
    score_review = 0
    max_review = 50
    review_content = read_file("review.md")
    if review_content is None:
        # 文件不存在时，剩余项直接0分
        details.append({"item": "review.md content checks", "score": 0, "max_score": 50, "passed": False, "reason": "review.md missing"})
        total_score += 0
    else:
        # 2a-c 包含每篇论文标题 (每篇10分)
        for idx, title in enumerate(ev_titles, 1):
            found = title in review_content
            s = 10 if found else 0
            score_review += s
            details.append({
                "item": f"review.md contains paper {idx} title: {title}",
                "score": s,
                "max_score": 10,
                "passed": found,
                "reason": "Found" if found else f"Title '{title}' not found"
            })
        # 2d 包含附件关键短语 (10分)
        phrase_found = key_phrase in review_content
        s_phrase = 10 if phrase_found else 0
        score_review += s_phrase
        details.append({
            "item": "review.md contains key phrase from attachment",
            "score": s_phrase,
            "max_score": 10,
            "passed": phrase_found,
            "reason": "Found" if phrase_found else "Key phrase missing"
        })
        # 2e 不包含任何干扰论文标题 (10分)
        has_distractor = any(t in review_content for t in distractor_titles)
        s_no_dist = 10 if not has_distractor else 0
        score_review += s_no_dist
        details.append({
            "item": "review.md contains no distractor paper titles",
            "score": s_no_dist,
            "max_score": 10,
            "passed": not has_distractor,
            "reason": "No distractor found" if not has_distractor else f"Found distractor title(s) in review"
        })
        total_score += score_review

    # ---------- 3. roadmap.md 内容 (40分) ----------
    score_roadmap = 0
    max_roadmap = 40
    roadmap_content = read_file("roadmap.md")
    if roadmap_content is None:
        details.append({"item": "roadmap.md content checks", "score": 0, "max_score": 40, "passed": False, "reason": "roadmap.md missing"})
        total_score += 0
    else:
        # 3a 包含 mermaid 代码块 (10分)
        has_mermaid = "```mermaid" in roadmap_content
        s_mermaid = 10 if has_mermaid else 0
        score_roadmap += s_mermaid
        details.append({
            "item": "roadmap.md contains ```mermaid code block",
            "score": s_mermaid,
            "max_score": 10,
            "passed": has_mermaid,
            "reason": "Found" if has_mermaid else "No mermaid code block"
        })
        # 3b-d 包含每篇论文标题 (每篇10分)
        for idx, title in enumerate(ev_titles, 1):
            found = title in roadmap_content
            s = 10 if found else 0
            score_roadmap += s
            details.append({
                "item": f"roadmap.md contains paper {idx} title: {title}",
                "score": s,
                "max_score": 10,
                "passed": found,
                "reason": "Found" if found else f"Title '{title}' not found in roadmap"
            })
        total_score += score_roadmap

    # 如果总分为整数，确保不超过100
    if total_score > max_total:
        total_score = max_total

    # 写出结果
    result = {
        "total_score": total_score,
        "details": details
    }
    out_path = os.path.join(workspace, "workplace_score.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"Score written to {out_path}: {total_score}/{max_total}")

if __name__ == "__main__":
    main()
