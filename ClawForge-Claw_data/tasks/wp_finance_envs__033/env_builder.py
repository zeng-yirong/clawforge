import os
import json
import shutil

def build_env():
    # ---- 清理并创建目录 ----
    for d in ["data/earnings", "data/stocks", "ops"]:
        os.makedirs(d, exist_ok=True)

    # ---- stocks.json —— 提供基础股票信息（部分用于干扰） ----
    stocks = [
        {"ticker": "CONS", "company_name": "ConsumerFirst Brands", "sector": "Consumer Cyclical", "current_price": 45.3},
        {"ticker": "ENGY", "company_name": "PowerGrid Energy", "sector": "Utilities", "current_price": 78.1},
        {"ticker": "FNS", "company_name": "FinServe Corp", "sector": "Financial Services", "current_price": 112.4},
        {"ticker": "GLBL", "company_name": "Global Retail Inc", "sector": "Consumer Defensive", "current_price": 33.2},
        {"ticker": "HLTH", "company_name": "HealthLink Systems", "sector": "Healthcare", "current_price": 95.6},
        {"ticker": "MFST", "company_name": "MegaFast Shipping", "sector": "Industrials", "current_price": 210.0},
        {"ticker": "NXTC", "company_name": "Nexa Technologies", "sector": "Technology", "current_price": 320.5},
        {"ticker": "TECH", "company_name": "TechVentures Inc", "sector": "Technology", "current_price": 505.2}
    ]
    with open("data/stocks/stocks.json", "w") as f:
        json.dump(stocks, f, indent=2)

    # ---- earnings.json —— 主数据，包含目标 Q2 条目和大量干扰 ----
    # 目标：Q2 2026 中同时 revenue_beat=True and eps_beat=True 的五个标的
    # 排序后为 TECH(12.5), NXTC(9.8), MFST(7.2), GLBL(5.1), HLTH(3.6)
    # 干扰：
    #   - CONS  Q2 2026 revenue_beat=False
    #   - ENGY  Q2 2026 eps_beat=False
    #   - FNS   Q1 2026 全部 beat（季度不对）
    #   - FNS   Q2 2026 全部 beat 但重复了？为了唯一，我们不重复 FNS，而是让他只有 Q1。
    #   - 重复 TECH: 另一个 Q2 2026 且 revenue_beat=False （干扰，但不会影响排序）
    #   - 一个不存在的 ticker "FAKE" 的 Q2 数据（干扰解析）
    earnings = [
        # ---- 有效目标（Q2 2026 beat=true）----
        {"earnings_id": "e001", "ticker": "TECH", "quarter": "Q2 2026", "report_date": "2026-07-20",
         "revenue_actual": 5200, "revenue_estimate": 4622, "revenue_beat": True, "revenue_beat_pct": 12.5,
         "eps_actual": 2.45, "eps_estimate": 2.20, "eps_beat": True, "eps_beat_pct": 11.36},
        {"earnings_id": "e002", "ticker": "NXTC", "quarter": "Q2 2026", "report_date": "2026-07-18",
         "revenue_actual": 1800, "revenue_estimate": 1639, "revenue_beat": True, "revenue_beat_pct": 9.8,
         "eps_actual": 3.10, "eps_estimate": 2.85, "eps_beat": True, "eps_beat_pct": 8.77},
        {"earnings_id": "e003", "ticker": "MFST", "quarter": "Q2 2026", "report_date": "2026-07-25",
         "revenue_actual": 8900, "revenue_estimate": 8302, "revenue_beat": True, "revenue_beat_pct": 7.2,
         "eps_actual": 1.88, "eps_estimate": 1.70, "eps_beat": True, "eps_beat_pct": 10.59},
        {"earnings_id": "e004", "ticker": "GLBL", "quarter": "Q2 2026", "report_date": "2026-07-15",
         "revenue_actual": 3200, "revenue_estimate": 3045, "revenue_beat": True, "revenue_beat_pct": 5.1,
         "eps_actual": 0.95, "eps_estimate": 0.88, "eps_beat": True, "eps_beat_pct": 7.95},
        {"earnings_id": "e005", "ticker": "HLTH", "quarter": "Q2 2026", "report_date": "2026-07-22",
         "revenue_actual": 4100, "revenue_estimate": 3958, "revenue_beat": True, "revenue_beat_pct": 3.6,
         "eps_actual": 1.52, "eps_estimate": 1.44, "eps_beat": True, "eps_beat_pct": 5.56},
        # ---- 干扰：Q2 但至少一个 beat=False ----
        {"earnings_id": "e006", "ticker": "CONS", "quarter": "Q2 2026", "report_date": "2026-07-19",
         "revenue_actual": 2600, "revenue_estimate": 2500, "revenue_beat": False, "revenue_beat_pct": 4.0,
         "eps_actual": 1.20, "eps_estimate": 1.15, "eps_beat": True, "eps_beat_pct": 4.35},
        {"earnings_id": "e007", "ticker": "ENGY", "quarter": "Q2 2026", "report_date": "2026-07-17",
         "revenue_actual": 5500, "revenue_estimate": 5238, "revenue_beat": True, "revenue_beat_pct": 5.0,
         "eps_actual": 2.10, "eps_estimate": 2.15, "eps_beat": False, "eps_beat_pct": -2.33},
        # ---- 干扰：Q1 数据，即使全部 beat 但季度不符 ----
        {"earnings_id": "e008", "ticker": "FNS", "quarter": "Q1 2026", "report_date": "2026-04-10",
         "revenue_actual": 1500, "revenue_estimate": 1420, "revenue_beat": True, "revenue_beat_pct": 5.6,
         "eps_actual": 0.88, "eps_estimate": 0.80, "eps_beat": True, "eps_beat_pct": 10.0},
        # ---- 干扰：重复的 TECH 条目，但 revenue_beat=False ----
        {"earnings_id": "e009", "ticker": "TECH", "quarter": "Q2 2026", "report_date": "2026-07-20",
         "revenue_actual": 4600, "revenue_estimate": 4622, "revenue_beat": False, "revenue_beat_pct": -0.5,
         "eps_actual": 2.30, "eps_estimate": 2.20, "eps_beat": True, "eps_beat_pct": 4.55},
        # ---- 干扰：不存在的 ticker ----
        {"earnings_id": "e010", "ticker": "FAKE", "quarter": "Q2 2026", "report_date": "2026-07-21",
         "revenue_actual": 100, "revenue_estimate": 90, "revenue_beat": True, "revenue_beat_pct": 11.1,
         "eps_actual": 0.50, "eps_estimate": 0.45, "eps_beat": True, "eps_beat_pct": 11.11}
    ]
    with open("data/earnings/earnings.json", "w") as f:
        json.dump(earnings, f, indent=2)

    # ---- 干扰：旧版本的 earnings_backup.json（不同数值） ----
    old_earnings = [
        {"earnings_id": "b001", "ticker": "TECH", "quarter": "Q2 2026", "revenue_beat_pct": 15.0, "eps_beat": True},
        {"earnings_id": "b002", "ticker": "MFST", "quarter": "Q2 2026", "revenue_beat_pct": 6.0, "eps_beat": False}
    ]
    with open("data/earnings/earnings_backup.json", "w") as f:
        json.dump(old_earnings, f, indent=2)

    # ---- 空 ops 目录（agent 将创建目标文件） ----
    # 已经创建

    # ---- 其他干扰文件 ----
    with open("notes.txt", "w") as f:
        f.write("Some random notes, irrelevant.")

    # ---- 确保 ops 目录干净 ----
    # 如果已有 ops 下的文件（例如之前评测遗留），则清除
    if os.path.exists("ops/top_performers.json"):
        os.remove("ops/top_performers.json")

if __name__ == "__main__":
    build_env()
