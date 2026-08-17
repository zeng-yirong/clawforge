import json
import os
import re
import sys

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

def parse_slow_query(log_text):
    """返回线程ID -> 查询时间的字典"""
    threads = {}
    lines = log_text.splitlines()
    current_thread = None
    current_time = None
    for line in lines:
        m = re.match(r'# Thread_id:\s*(\d+)', line)
        if m:
            current_thread = int(m.group(1))
            current_time = None
            continue
        m = re.match(r'# Query_time:\s*([\d.]+)', line)
        if m and current_thread is not None:
            current_time = float(m.group(1))
            threads[current_thread] = current_time
    return threads

def parse_innodb_status(text):
    """返回事务ID -> ACTIVE秒数"""
    trx = {}
    for line in text.splitlines():
        m = re.match(r'---TRANSACTION\s+(\d+),\s+ACTIVE\s+(\d+)\s+sec', line)
        if m:
            trx[int(m.group(1))] = int(m.group(2))
    return trx

def get_ground_truth():
    """从工作区文件计算正确的事务ID"""
    slow_path = os.path.join(workspace, "slow_logs/mysql-slow.log")
    innodb_path = os.path.join(workspace, "db_dumps/innodb_status.txt")
    if not os.path.exists(slow_path) or not os.path.exists(innodb_path):
        return None
    with open(slow_path) as f:
        slow_text = f.read()
    with open(innodb_path) as f:
        innodb_text = f.read()
    slow_threads = parse_slow_query(slow_text)
    innodb_trx = parse_innodb_status(innodb_text)
    # 找出慢查询中查询时间 > 500秒的线程ID
    long_threads = {tid for tid, t in slow_threads.items() if t > 500}
    # 找出InnoDB中活跃时间 > 500秒的事务ID
    long_trx = {tid for tid, sec in innodb_trx.items() if sec > 500}
    # 交集
    candidates = long_threads & long_trx
    # 应该只有一个
    if len(candidates) == 1:
        return list(candidates)[0]
    return None

def verify():
    results = []
    total = 0

    # 1-3: 目录存在性 (各5分)
    dirs = [
        ("slow_logs directory exists", "slow_logs", 5),
        ("db_dumps directory exists", "db_dumps", 5),
        ("ops directory exists", "ops", 5),
    ]
    for item, d, max_s in dirs:
        path = os.path.join(workspace, d)
        ok = os.path.isdir(path)
        score = max_s if ok else 0
        total += score
        results.append({"item": item, "score": score, "max_score": max_s, "passed": ok, "reason": f"目录{'存在' if ok else '不存在'}"})

    # 4: kill_target.json 存在 (10分)
    target_path = os.path.join(workspace, "ops/kill_target.json")
    ok = os.path.isfile(target_path)
    score = 10 if ok else 0
    total += score
    results.append({"item": "ops/kill_target.json exists", "score": score, "max_score": 10, "passed": ok, "reason": f"文件{'存在' if ok else '不存在'}"})

    if not ok:
        # 无法继续，直接输出
        results.append({"item": "kill_target.json is valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        results.append({"item": "contains key 'transaction_id'", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        results.append({"item": "transaction_id value is integer 123456", "score": 0, "max_score": 30, "passed": False, "reason": "文件不存在"})
        results.append({"item": "ID matches ground truth from files", "score": 0, "max_score": 20, "passed": False, "reason": "文件不存在"})
    else:
        # 5: JSON 合法 (10分)
        try:
            with open(target_path) as f:
                data = json.load(f)
            ok = True
        except Exception as e:
            ok = False
            data = None
        score = 10 if ok else 0
        total += score
        results.append({"item": "kill_target.json is valid JSON", "score": score, "max_score": 10, "passed": ok, "reason": f"JSON{'合法' if ok else '解析失败'}"})

        # 6-7: 字段存在及值 (40分)
        has_key = ok and isinstance(data, dict) and "transaction_id" in data
        score_key = 10 if has_key else 0
        total += score_key
        results.append({"item": "contains key 'transaction_id'", "score": score_key, "max_score": 10, "passed": has_key, "reason": f"键{'存在' if has_key else '不存在'}"})

        correct_value = False
        if has_key:
            val = data["transaction_id"]
            if isinstance(val, int) and val == 123456:
                correct_value = True
            # 允许字符串？不允许，必须整数
        score_val = 30 if correct_value else 0
        total += score_val
        results.append({"item": "transaction_id value is integer 123456", "score": score_val, "max_score": 30, "passed": correct_value, "reason": f"值{'正确' if correct_value else '错误'}"})

        # 8: 与文件推导的 ground truth 一致 (20分)
        gt = get_ground_truth()
        match = (gt is not None and has_key and isinstance(data.get("transaction_id"), int) and data["transaction_id"] == gt)
        score_match = 20 if match else 0
        total += score_match
        results.append({"item": "ID matches ground truth from files", "score": score_match, "max_score": 20, "passed": match, "reason": f"与文件推导的真相{'一致' if match else '不一致，正确ID为' + str(gt) if gt else '无法推导'}"})

    # 输出结果
    final = {"total_score": total, "details": results}
    output_path = os.path.join(workspace, "workplace_score.json")
    with open(output_path, "w") as f:
        json.dump(final, f, indent=2)
    print(f"Score written to {output_path}: {total}/100")

if __name__ == "__main__":
    verify()
