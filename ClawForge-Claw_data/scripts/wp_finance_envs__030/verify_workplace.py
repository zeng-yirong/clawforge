import json
import sys
import os
from pathlib import Path

def load_json(filepath):
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception:
        return None

def verify(workspace):
    score_details = []
    total_score = 0

    # 1. 检查文件是否存在 (10分)
    target_file = os.path.join(workspace, 'ops/top_analyst_pick.json')
    exists = os.path.isfile(target_file)
    score_details.append({
        "item": "ops/top_analyst_pick.json 是否存在",
        "score": 10 if exists else 0,
        "max_score": 10,
        "passed": exists,
        "reason": "文件存在" if exists else "未找到文件 ops/top_analyst_pick.json"
    })
    if not exists:
        total_score = 10  # 只给文件存在分
        # 写入结果并返回
        details = score_details
        with open(os.path.join(workspace, 'workplace_score.json'), 'w') as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # 2. JSON 格式合法性 (10分)
    data = load_json(target_file)
    json_ok = data is not None
    score_details.append({
        "item": "JSON 格式合法",
        "score": 10 if json_ok else 0,
        "max_score": 10,
        "passed": json_ok,
        "reason": "解析成功" if json_ok else "无法解析为 JSON"
    })
    if not json_ok:
        total_score = 10
        details = score_details
        with open(os.path.join(workspace, 'workplace_score.json'), 'w') as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # 3. 必要字段齐全 (10分)
    required_fields = ['ticker', 'company_name', 'analyst_name', 'eps_beat_pct', 'quarter']
    missing = [f for f in required_fields if f not in data]
    fields_ok = len(missing) == 0
    score_details.append({
        "item": "字段齐全",
        "score": 10 if fields_ok else 0,
        "max_score": 10,
        "passed": fields_ok,
        "reason": "所有必需字段存在" if fields_ok else f"缺失字段: {missing}"
    })

    # 4. 读取原始数据，计算期望值 (准备后续比较)
    # 从工作区读取原始文件
    analysts_path = os.path.join(workspace, 'data/analysts.json')
    earnings_path = os.path.join(workspace, 'data/earnings.json')
    stocks_path = os.path.join(workspace, 'data/stocks.json')

    analysts_data = load_json(analysts_path)
    earnings_data = load_json(earnings_path)
    stocks_data = load_json(stocks_path)

    # 防御性检查原始数据是否存在
    raw_ok = (analysts_data is not None and earnings_data is not None and stocks_data is not None)
    if not raw_ok:
        score_details.append({
            "item": "原始数据完整性",
            "score": 0,
            "max_score": 0,  # 不参与总分，只记录
            "passed": False,
            "reason": "工作区缺少必要的原始数据文件"
        })
        # 但继续评分，只扣字段分？ 这里我们只给字段分，但后面数值比较无法进行，所以把数值分设为0。
        expected = None
    else:
        # 寻找 Sarah Chen
        analyst = None
        for a in analysts_data.get('analysts', []):
            if a.get('name') == 'Sarah Chen':
                analyst = a
                break
        if analyst is None:
            expected = None
        else:
            coverage = analyst.get('coverage', [])
            # 过滤 earnings 中最新季度 (Q2 2026) 且 ticker 在 coverage 中，且包含 eps_beat_pct
            latest_quarter = "Q2 2026"
            candidates = []
            for e in earnings_data.get('earnings', []):
                if e.get('ticker') in coverage and e.get('quarter') == latest_quarter and 'eps_beat_pct' in e:
                    candidates.append(e)
            if not candidates:
                expected = None
            else:
                # 按 eps_beat_pct 降序，相同则按 ticker 升序
                candidates.sort(key=lambda x: (-x['eps_beat_pct'], x['ticker']))
                best = candidates[0]
                ticker = best['ticker']
                # 找公司名
                company_name = ''
                for s in stocks_data.get('stocks', []):
                    if s['ticker'] == ticker:
                        company_name = s['company_name']
                        break
                expected = {
                    'ticker': ticker,
                    'company_name': company_name,
                    'analyst_name': 'Sarah Chen',
                    'eps_beat_pct': best['eps_beat_pct'],
                    'quarter': latest_quarter
                }

    # 5. 逐字段比较 (每个字段 15 分，共 60 分；若 expected 为 None 则直接 0)
    field_weights = {
        'ticker': 15,
        'company_name': 15,
        'analyst_name': 15,
        'eps_beat_pct': 15,
        'quarter': 10   # 剩下10分给quarter，总分100
    }
    # 调整权重：缺失字段已扣10分，所以这里总分为 15+15+15+15+10=70，加上前面20分共90？不对，前面已经20分（存在10+格式10+字段10）=30分，再加上70=100。
    # 但字段齐全已经给了10分，所以字段值比较总分应为 70分。
    # 或者我们重新分配：存在10，格式10，字段10，ticker 15, company 15, analyst_name 15, eps_beat_pct 15, quarter 10 = 100。
    # 已经分配正确。
    if expected is None:
        # 无法计算期望值，给0分
        for fname in ['ticker', 'company_name', 'analyst_name', 'eps_beat_pct', 'quarter']:
            score_details.append({
                "item": f"字段 {fname} 值正确",
                "score": 0,
                "max_score": field_weights[fname],
                "passed": False,
                "reason": "无法从原始数据推导期望值（数据不完整或未找到Sarah Chen）"
            })
    else:
        for fname, weight in field_weights.items():
            agent_val = data.get(fname)
            expected_val = expected[fname]
            if fname == 'eps_beat_pct':
                # 浮点数允许微小误差 (0.01)
                passed = isinstance(agent_val, (int, float)) and abs(agent_val - expected_val) < 0.01
                reason = f"期望 {expected_val}，实际 {agent_val}" if not passed else "正确"
            else:
                passed = agent_val == expected_val
                reason = f"期望 '{expected_val}'，实际 '{agent_val}'" if not passed else "正确"
            score_details.append({
                "item": f"字段 {fname} 值正确",
                "score": weight if passed else 0,
                "max_score": weight,
                "passed": passed,
                "reason": reason
            })

    # 6. 额外检查：没有多余的关键错误字段（不扣分，仅记录）
    # 不强制

    # 计算总分
    total_score = sum(d['score'] for d in score_details)
    # 写入结果
    result = {
        "total_score": total_score,
        "details": score_details
    }
    with open(os.path.join(workspace, 'workplace_score.json'), 'w') as f:
        json.dump(result, f, indent=2)
    print(f"Verification completed. Total score: {total_score}")

if __name__ == '__main__':
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
