import sys
import json
import csv
import os
from pathlib import Path

def load_csv(path):
    with open(path, newline='') as f:
        reader = csv.DictReader(f)
        return [row for row in reader]

def compute_expected_labels():
    # 从实际工作区加载数据（注意工作区路径已由 sys.argv[1] 传入）
    workspace = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    # 加载规则
    rules = []
    with open(workspace / "raw_data/segmentation_rules.csv", newline='') as f:
        reader = csv.DictReader(f)
        for r in reader:
            r['min_spend'] = int(r['min_spend'])
            r['max_spend'] = int(r['max_spend'])
            r['min_active_days'] = int(r['min_active_days'])
            r['max_active_days'] = int(r['max_active_days'])
            rules.append(r)

    # 加载客户（清洗：去重、过滤 inactive、过滤缺失 industry、只保留第一个有效记录）
    raw_customers = load_csv(workspace / "raw_data/customers.csv")
    seen = set()
    valid_customers = []
    for c in raw_customers:
        if c['customer_id'] in seen:
            continue
        seen.add(c['customer_id'])
        if c.get('status') == 'inactive':
            continue
        if not c.get('customer_id') or not c.get('industry') or c['industry'] == '':
            continue
        valid_customers.append(c)

    # 加载活动日志（去重，过滤负天数、缺失 risk_level）
    raw_activities = load_csv(workspace / "raw_data/activity_logs.csv")
    seen_act = set()
    activity_map = {}
    for a in raw_activities:
        cid = a.get('customer_id')
        if not cid or cid in seen_act:
            continue
        seen_act.add(cid)
        try:
            days = int(a['last_active_days'])
        except (ValueError, TypeError):
            continue
        if days < 0:
            continue
        if not a.get('risk_level') or a['risk_level'] == '':
            continue
        activity_map[cid] = {'risk_level': a['risk_level'], 'last_active_days': days}

    # 加载消费日志（去重，过滤负消费、缺失 customer_id）
    raw_consumption = load_csv(workspace / "raw_data/consumption_logs.csv")
    seen_cons = set()
    consumption_map = {}
    for c in raw_consumption:
        cid = c.get('customer_id')
        if not cid or cid in seen_cons:
            continue
        seen_cons.add(cid)
        try:
            spend = int(c['quarter_spend_usd'])
        except (ValueError, TypeError):
            continue
        if spend < 0:
            continue
        consumption_map[cid] = spend

    # 计算每个客户的标签
    expected = {}
    for c in valid_customers:
        cid = c['customer_id']
        act = activity_map.get(cid)
        spend = consumption_map.get(cid)
        if not act or spend is None:
            # 缺少必要数据，按规则 fallback 到 basic
            label = 'basic'
        else:
            risk = act['risk_level']
            days = act['last_active_days']
            # 按顺序匹配规则
            label = 'basic'
            for rule in rules:
                if rule['min_spend'] <= spend <= rule['max_spend'] and \
                   rule['min_active_days'] <= days <= rule['max_active_days']:
                    if rule['risk_level'] == 'any' or rule['risk_level'] == risk:
                        label = rule['tier']
                        break
        expected[cid] = label

    return expected

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    base = Path(workspace)
    details = []
    total_score = 0
    max_total = 100

    # 1. 目录结构检查 (10分)
    req_dirs = ["raw_data", "ops"]
    dir_ok = all((base / d).is_dir() for d in req_dirs)
    if dir_ok:
        details.append({"item": "目录结构存在", "score": 10, "max_score": 10, "passed": True, "reason": "raw_data 和 ops 目录均存在"})
    else:
        details.append({"item": "目录结构存在", "score": 0, "max_score": 10, "passed": False, "reason": "缺少必要目录"})

    # 2. 结果文件存在性 (10分)
    result_path = base / "ops/latest_tier_labels.json"
    if result_path.is_file():
        details.append({"item": "结果文件存在", "score": 10, "max_score": 10, "passed": True, "reason": "ops/latest_tier_labels.json 存在"})
    else:
        details.append({"item": "结果文件存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件缺失"})
        # 得分汇总
        total_score = sum(d['score'] for d in details)
        with open(base / "workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": details}, f)
        print(f"总得分: {total_score}/100")
        return

    # 3. 文件合法性 (10分)
    try:
        with open(result_path) as f:
            data = json.load(f)
        if isinstance(data, dict) or isinstance(data, list):
            details.append({"item": "JSON 格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "是合法 JSON"})
        else:
            details.append({"item": "JSON 格式合法", "score": 0, "max_score": 10, "passed": False, "reason": "不是合法 JSON 结构"})
    except Exception as e:
        details.append({"item": "JSON 格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {e}"})

    # 如果格式不合法则提前结束
    if details[-1]['score'] == 0:
        total_score = sum(d['score'] for d in details)
        with open(base / "workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": details}, f)
        print(f"总得分: {total_score}/100")
        return

    # 4. 内容校验 (70分)
    # 转换成 {customer_id: label} 字典处理
    if isinstance(data, dict):
        result_map = data
    elif isinstance(data, list):
        result_map = {}
        for item in data:
            if isinstance(item, dict) and 'customer_id' in item and 'label' in item:
                result_map[item['customer_id']] = item['label']
    else:
        result_map = {}

    # 计算预期标签
    try:
        expected = compute_expected_labels()
    except Exception as e:
        details.append({"item": "预期计算错误", "score": 0, "max_score": 70, "passed": False, "reason": f"内部错误: {e}"})
        total_score = sum(d['score'] for d in details)
        with open(base / "workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": details}, f)
        return

    # 检查每个预期客户
    correct = 0
    wrong = []
    missing = []
    extra = []
    # 预期客户：C001, C002 (C003 inactive 忽略，C004 缺字段忽略，C005/006 无有效消费/活动记录也算basic)
    expected_active = {k: v for k, v in expected.items()}
    for cid, label in expected_active.items():
        if cid not in result_map:
            missing.append(cid)
        elif result_map[cid] == label:
            correct += 1
        else:
            wrong.append((cid, result_map[cid], label))

    # 额外出现的客户（不在预期里）
    result_ids = set(result_map.keys())
    extra = list(result_ids - set(expected_active.keys()))

    # 打分：每个正确客户得 70/len(expected) 约 70/2 = 35 分，如果缺失或错误则扣分
    expected_count = len(expected_active)
    if expected_count > 0:
        per = 70 / expected_count
        score_content = int(correct * per)
    else:
        score_content = 0

    # 如果有额外记录，每个扣 5 分（最多扣到0）
    extra_penalty = min(len(extra) * 5, score_content)
    final_content = max(0, score_content - extra_penalty)

    reason_parts = []
    if correct > 0:
        reason_parts.append(f"正确标签数: {correct}/{expected_count}")
    if wrong:
        reason_parts.append(f"错误标签: {wrong}")
    if missing:
        reason_parts.append(f"缺失客户: {missing}")
    if extra:
        reason_parts.append(f"多余客户: {extra}")
    details.append({
        "item": "标签内容准确",
        "score": final_content,
        "max_score": 70,
        "passed": final_content == 70,
        "reason": "; ".join(reason_parts) if reason_parts else "完全正确"
    })

    # 总分
    total_score = sum(d['score'] for d in details)
    output = {
        "total_score": total_score,
        "details": details
    }
    with open(base / "workplace_score.json", "w") as f:
        json.dump(output, f, indent=2)
    print(f"总得分: {total_score}/100")

if __name__ == "__main__":
    verify()
