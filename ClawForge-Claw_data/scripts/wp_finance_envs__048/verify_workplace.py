import json
import os
import sys
import re

def check_recommendation(workspace):
    """验证 agent 产出的 recommendation.json"""
    details = []
    total_score = 0
    max_total = 100

    # 1. 检查文件是否存在 (10分)
    rec_path = os.path.join(workspace, "recommendation.json")
    if os.path.isfile(rec_path):
        details.append({
            "item": "recommendation.json 存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "文件已找到"
        })
        total_score += 10
    else:
        details.append({
            "item": "recommendation.json 存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"未在 {rec_path} 找到文件"
        })
        # 后续无法检查，直接返回
        return {"total_score": total_score, "details": details}

    # 2. JSON 合法性 (10分)
    try:
        with open(rec_path, "r") as f:
            rec = json.load(f)
        details.append({
            "item": "JSON 格式合法",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "可正常解析"
        })
        total_score += 10
    except Exception as e:
        details.append({
            "item": "JSON 格式合法",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON 解析失败: {str(e)}"
        })
        return {"total_score": total_score, "details": details}

    # 3. 检查结构：必须是一个对象，包含 tickers 数组 (10分)
    if not isinstance(rec, dict):
        details.append({
            "item": "顶层为 JSON 对象",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "顶层应为字典"
        })
        return {"total_score": total_score, "details": details}
    if "tickers" not in rec:
        details.append({
            "item": "包含 'tickers' 字段",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "缺少 tickers 数组"
        })
        return {"total_score": total_score, "details": details}
    tickers = rec["tickers"]
    if not isinstance(tickers, list) or len(tickers) == 0:
        details.append({
            "item": "'tickers' 为非空列表",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "tickers 应为非空列表"
        })
        return {"total_score": total_score, "details": details}
    details.append({
        "item": "JSON 结构正确",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": f"包含 tickers 数组，共 {len(tickers)} 个条目"
    })
    total_score += 10

    # 4. 检查每个条目是否包含 ticker 和 reason (15分)
    for i, entry in enumerate(tickers):
        if not isinstance(entry, dict):
            # 只要有一个不符合，扣分
            details.append({
                "item": f"tickers[{i}] 为对象",
                "score": 0,
                "max_score": 15,
                "passed": False,
                "reason": "条目不是字典"
            })
            return {"total_score": total_score, "details": details}
        if "ticker" not in entry or "reason" not in entry:
            details.append({
                "item": f"tickers[{i}] 包含 ticker 和 reason",
                "score": 0,
                "max_score": 15,
                "passed": False,
                "reason": f"缺少字段: {entry.keys()}"
            })
            return {"total_score": total_score, "details": details}
    else:
        details.append({
            "item": "每个条目含 ticker 和 reason",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": "所有条目字段完整"
        })
        total_score += 15

    # 5. 检查 ticker 是否只包含 TECH 和 NXTC (且必须包含这两个) (25分)
    ticker_set = set(entry["ticker"] for entry in tickers)
    expected = {"TECH", "NXTC"}
    if ticker_set == expected:
        details.append({
            "item": "仅包含目标 ticker (TECH, NXTC)",
            "score": 25,
            "max_score": 25,
            "passed": True,
            "reason": f"正确: {sorted(ticker_set)}"
        })
        total_score += 25
    elif ticker_set.issubset(expected) and len(ticker_set) == 2:
        # 包含了正确集合但可能有其他？但子集且大小为2只能是等于
        details.append({
            "item": "仅包含目标 ticker",
            "score": 25,
            "max_score": 25,
            "passed": True,
            "reason": "正确"
        })
        total_score += 25
    elif ticker_set == {"TECH"} or ticker_set == {"NXTC"}:
        details.append({
            "item": "仅包含目标 ticker",
            "score": 10,
            "max_score": 25,
            "passed": False,
            "reason": f"缺少一个目标股票，现有: {ticker_set}"
        })
        total_score += 10
    else:
        details.append({
            "item": "仅包含目标 ticker",
            "score": 0,
            "max_score": 25,
            "passed": False,
            "reason": f"包含错误股票: {ticker_set}"
        })
        total_score += 0

    # 6. 检查 reason 是否有实质内容（至少15个非空白字符）(15分)
    reason_ok = True
    for entry in tickers:
        reason = entry.get("reason", "")
        if len(reason.strip()) < 15:
            reason_ok = False
            break
    if reason_ok:
        details.append({
            "item": "每个理由有实质内容（>=15字符）",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": "所有理由长度足够"
        })
        total_score += 15
    else:
        details.append({
            "item": "每个理由有实质内容",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": "存在过短或无意义的理由"
        })

    # 7. 检查是否包含了重复的 ticker (5分)
    if len(ticker_set) == len(tickers):
        details.append({
            "item": "无重复 ticker",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "所有 ticker 唯一"
        })
        total_score += 5
    else:
        details.append({
            "item": "无重复 ticker",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "存在重复"
        })

    # 8. 检查 tickers 数组顺序 (可选，但我们可以要求字母序以便唯一确定) (10分)
    ticker_order = [entry["ticker"] for entry in tickers]
    if ticker_order == sorted(ticker_order):
        details.append({
            "item": "ticker 按字母序排列",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "顺序正确"
        })
        total_score += 10
    else:
        details.append({
            "item": "ticker 按字母序排列",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"顺序应为 {sorted(ticker_order)}，实际为 {ticker_order}"
        })

    # 总分封顶 100
    total_score = min(total_score, max_total)
    return {"total_score": total_score, "details": details}

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = check_recommendation(workspace)
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Scoring complete. Total: {result['total_score']}/100")

if __name__ == "__main__":
    main()
