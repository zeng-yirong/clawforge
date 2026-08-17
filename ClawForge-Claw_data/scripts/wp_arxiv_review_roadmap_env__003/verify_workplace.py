import sys
import os
import json
import re
import csv
from pathlib import Path

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    ws = Path(workspace)
    score = 0
    details = []

    # ------------------------------------------------------------
    # 1. 检查最终产物存在 (每个10分)
    # ------------------------------------------------------------
    review_path = ws / "review.md"
    roadmap_path = ws / "roadmap.md"

    if review_path.exists():
        details.append({"item": "review.md 存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
        score += 10
    else:
        details.append({"item": "review.md 存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})

    if roadmap_path.exists():
        details.append({"item": "roadmap.md 存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
        score += 10
    else:
        details.append({"item": "roadmap.md 存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})

    if not review_path.exists():
        # 如果 review 不存在，后续无法检查，直接返回
        total = sum(d["score"] for d in details)
        result = {"total_score": total, "details": details}
        with open(ws / "workplace_score.json", "w") as f:
            json.dump(result, f, indent=2)
        return

    # ------------------------------------------------------------
    # 2. 解析 review.md 内容 (表格检查 50分)
    # ------------------------------------------------------------
    try:
        review_text = review_path.read_text(encoding="utf-8")
    except Exception as e:
        details.append({"item": "review.md 可读", "score": 0, "max_score": 5, "passed": False, "reason": f"读取失败: {e}"})
        # 仍然继续
        review_text = ""

    # 检查是否提到了 "Tool-Augmented Reasoning"
    has_direction = "Tool-Augmented Reasoning" in review_text or "tool_augmented_reasoning" in review_text
    if has_direction:
        details.append({"item": "提及研究方向", "score": 5, "max_score": 5, "passed": True, "reason": "包含方向名称"})
        score += 5
    else:
        details.append({"item": "提及研究方向", "score": 0, "max_score": 5, "passed": False, "reason": "未找到方向名称"})

    # 用正则提取所有 paper_id 模式 (假设表格中包含 paper_id 或论文ID)
    # 常见的表格写法：| paper_001 | ... |
    # 也可能在文本中直接提及 paper_001
    # 我们尝试提取所有符合 paper_三位数字 模式的 ID
    found_ids = set(re.findall(r'paper_\d{3}', review_text))
    # 正确的 ID 集合 (排除脏数据后的有效论文)
    expected_ids = {"paper_001", "paper_003", "paper_005", "paper_007", "paper_009"}

    # 判断是否包含了预期 ID 且没有多余
    missing = expected_ids - found_ids
    extra = found_ids - expected_ids

    id_correct = True
    reason_parts = []
    if missing:
        id_correct = False
        reason_parts.append(f"缺少ID: {sorted(missing)}")
    if extra:
        id_correct = False
        reason_parts.append(f"多余ID: {sorted(extra)}")
    if not found_ids:
        id_correct = False
        reason_parts.append("未找到任何论文ID")

    if id_correct:
        details.append({"item": "论文ID集合正确", "score": 30, "max_score": 30, "passed": True, "reason": "包含全部5个有效ID且无多余"})
        score += 30
    else:
        details.append({"item": "论文ID集合正确", "score": 0, "max_score": 30, "passed": False, "reason": "; ".join(reason_parts)})

    # 检查是否包含了脏数据中的ID (比如 paper_011, paper_013) 应该被剔除
    dirty_ids = {"paper_011", "paper_013"}
    if dirty_ids & found_ids:
        details.append({"item": "剔除脏数据", "score": 0, "max_score": 10, "passed": False, "reason": f"包含了脏数据ID: {sorted(dirty_ids & found_ids)}"})
    else:
        details.append({"item": "剔除脏数据", "score": 10, "max_score": 10, "passed": True, "reason": "未包含未来年份或缺失字段的论文"})
        score += 10

    # ------------------------------------------------------------
    # 3. 检查 roadmap.md 内容 (Mermaid 合法性 15分)
    # ------------------------------------------------------------
    if roadmap_path.exists():
        roadmap_text = roadmap_path.read_text(encoding="utf-8")
        # 检查是否包含 Mermaid 图声明 (graph TD / flowchart / timeline 等)
        has_mermaid = bool(re.search(r'```\s*mermaid|graph\s+\w+|timeline|flowchart', roadmap_text, re.IGNORECASE))
        if has_mermaid:
            details.append({"item": "Mermaid 图声明", "score": 10, "max_score": 10, "passed": True, "reason": "包含有效的Mermaid图表语法"})
            score += 10
        else:
            details.append({"item": "Mermaid 图声明", "score": 0, "max_score": 10, "passed": False, "reason": "未找到Mermaid图声明"})

        # 检查是否包含至少一个论文ID节点 (简单检查)
        node_ids = re.findall(r'paper_\d{3}', roadmap_text)
        if node_ids:
            details.append({"item": "Mermaid 包含论文节点", "score": 5, "max_score": 5, "passed": True, "reason": f"包含{len(node_ids)}个论文ID节点"})
            score += 5
        else:
            details.append({"item": "Mermaid 包含论文节点", "score": 0, "max_score": 5, "passed": False, "reason": "未找到论文ID节点"})
    else:
        details.append({"item": "Mermaid 内容检查", "score": 0, "max_score": 15, "passed": False, "reason": "roadmap.md 不存在"})

    # 附加小分：review.md 是否包含表格格式 (5分)
    if re.search(r'\|.*\|', review_text):
        details.append({"item": "review.md 表格格式", "score": 5, "max_score": 5, "passed": True, "reason": "包含Markdown表格"})
        score += 5
    else:
        details.append({"item": "review.md 表格格式", "score": 0, "max_score": 5, "passed": False, "reason": "未发现表格行"})

    # ------------------------------------------------------------
    # 总分 & 输出
    # ------------------------------------------------------------
    total_score = min(score, 100)  # 上限100
    result = {"total_score": total_score, "details": details}
    with open(ws / "workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == '__main__':
    verify()
