"""
verify_workplace.py for wp_post_mails__010.
Checks agent-produced files against expected values.
"""
import os
import sys
import json
import csv
from pathlib import Path

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    ws = Path(workspace)
    score = 0
    details = []
    total_max = 100

    # ---------- 1. 目录结构 (10分) ----------
    required_dirs = ["output"]
    for d in required_dirs:
        if (ws / d).is_dir():
            score += 5
            details.append({"item": f"目录 {d} 存在", "score": 5, "max_score": 5, "passed": True, "reason": ""})
        else:
            details.append({"item": f"目录 {d} 存在", "score": 0, "max_score": 5, "passed": False, "reason": f"缺少目录 {d}"})

    # ---------- 2. 输出文件结构 (10分) ----------
    required_files = ["output/x_post.json", "output/reddit_post.json", "output/replies.json"]
    for fname in required_files:
        fpath = ws / fname
        if fpath.is_file():
            score += 3   # 每个3分，共9，细调
            details.append({"item": f"文件 {fname} 存在", "score": 3, "max_score": 3, "passed": True, "reason": ""})
        else:
            details.append({"item": f"文件 {fname} 存在", "score": 0, "max_score": 3, "passed": False, "reason": f"文件缺失"})
    # 额外1分给output目录整体
    if all((ws / f).is_file() for f in required_files):
        score += 1
        details.append({"item": "三个输出文件齐全", "score": 1, "max_score": 1, "passed": True, "reason": ""})
    else:
        details.append({"item": "三个输出文件齐全", "score": 0, "max_score": 1, "passed": False, "reason": "文件不全"})

    # ---------- 3. x_post.json 正确性 (25分) ----------
    x_path = ws / "output/x_post.json"
    x_score = 0
    x_reason = ""
    try:
        with open(x_path, 'r') as f:
            x_data = json.load(f)
        # 检查必要字段
        if "platform" in x_data and x_data["platform"] == "x":
            x_score += 5
        else:
            x_reason = "platform 字段缺失或错误"
        if "content" in x_data and isinstance(x_data["content"], str):
            content = x_data["content"]
            # 必须包含任务名称 Aurora-7
            if "Aurora-7" in content:
                x_score += 10
            else:
                x_reason += " 缺少 Aurora-7"
            # 必须包含日期 2025-05-20 或 May 20
            if "2025-05-20" in content or "May 20" in content:
                x_score += 5
            else:
                x_reason += " 缺少日期"
            # 品牌CTA 或 语气检查 —— 是否包含 "🚀" 或 "liftoff"
            if "🚀" in content or "liftoff" in content.lower():
                x_score += 5
            else:
                x_reason += " 缺少品牌元素"
        else:
            x_reason = "content 字段缺失或非字符串"
    except Exception as e:
        x_reason = str(e)
        x_score = 0
    details.append({"item": "x_post.json 内容正确", "score": x_score, "max_score": 25, "passed": x_score == 25, "reason": x_reason})
    score += x_score

    # ---------- 4. reddit_post.json 正确性 (25分) ----------
    r_path = ws / "output/reddit_post.json"
    r_score = 0
    r_reason = ""
    try:
        with open(r_path, 'r') as f:
            r_data = json.load(f)
        if "platform" in r_data and r_data["platform"] == "reddit":
            r_score += 5
        else:
            r_reason = "platform 字段缺失或错误"
        # 需要包含 community 字段，且为 r/AuroraSpace
        if "community" in r_data and r_data["community"] == "r/AuroraSpace":
            r_score += 5
        else:
            r_reason += " 社区不对"
        if "content" in r_data and isinstance(r_data["content"], str):
            content = r_data["content"]
            if "Aurora-7" in content:
                r_score += 10
            else:
                r_reason += " 缺少 Aurora-7"
            if "2025-05-20" in content or "May 20" in content:
                r_score += 5
            else:
                r_reason += " 缺少日期"
        else:
            r_reason = "content 字段缺失或非字符串"
    except Exception as e:
        r_reason = str(e)
        r_score = 0
    details.append({"item": "reddit_post.json 内容正确", "score": r_score, "max_score": 25, "passed": r_score == 25, "reason": r_reason})
    score += r_score

    # ---------- 5. replies.json 正确性 (30分) ----------
    rep_path = ws / "output/replies.json"
    rep_score = 0
    rep_reason = ""
    try:
        with open(rep_path, 'r') as f:
            rep_data = json.load(f)
        if not isinstance(rep_data, list):
            rep_reason = "replies.json 必须是列表"
        else:
            # 应该恰好2条回复
            if len(rep_data) == 2:
                rep_score += 5
            else:
                rep_reason = f"预期2条回复，实际{len(rep_data)}条"
            # 检查每条回复的字段
            expected_post_ids = {"pst_001", "pst_002"}
            actual_ids = set()
            correct_content = "Confirmed! We're all set."
            for i, reply in enumerate(rep_data):
                if not isinstance(reply, dict):
                    rep_reason += f" 第{i+1}条不是对象"
                    continue
                if "post_id" not in reply:
                    rep_reason += f" 第{i+1}条缺少post_id"
                    continue
                actual_ids.add(reply["post_id"])
                if reply.get("content") == correct_content:
                    rep_score += 10  # 每条10分，共20
                else:
                    rep_reason += f" 第{i+1}条content不是'{correct_content}'"
            # 检查是否覆盖了需要的post_id
            if actual_ids == expected_post_ids:
                rep_score += 5
            else:
                rep_reason += " 回复的post_id不匹配预期"
    except Exception as e:
        rep_reason = str(e)
        rep_score = 0
    details.append({"item": "replies.json 内容正确", "score": rep_score, "max_score": 30, "passed": rep_score == 30, "reason": rep_reason})
    score += rep_score

    # 最终总分控制在0-100
    final_score = min(100, max(0, score))
    result = {
        "total_score": final_score,
        "details": details
    }
    with open(ws / "workplace_score.json", 'w') as f:
        json.dump(result, f, indent=2)
    print(f"Verification complete. Score: {final_score}/100")

if __name__ == "__main__":
    main()
