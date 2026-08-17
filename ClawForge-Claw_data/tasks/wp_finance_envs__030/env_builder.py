import os
import json
import shutil

def build_env():
    # 清理旧的干扰文件（如果有）
    for path in ['data', 'ops', 'raw_logs']:
        if os.path.exists(path):
            shutil.rmtree(path)

    # 创建必需的目录
    os.makedirs('data', exist_ok=True)
    os.makedirs('ops', exist_ok=True)   # 空目录，让agent自己创建文件

    # 1. stocks.json
    stocks = [
        {"ticker": "TECH", "company_name": "TechVentures Inc", "sector": "Technology"},
        {"ticker": "NXTC", "company_name": "Nexa Technologies", "sector": "Technology"},
        {"ticker": "MFST", "company_name": "MegaFast Shipping", "sector": "Industrials"},
        {"ticker": "HLTH", "company_name": "HealthLink Systems", "sector": "Healthcare"},
        {"ticker": "CONS", "company_name": "ConsumerFirst Brands", "sector": "Consumer Defensive"},
        {"ticker": "ENER", "company_name": "PowerGrid Energy", "sector": "Utilities"},
    ]
    with open('data/stocks.json', 'w') as f:
        json.dump({"stocks": stocks}, f, indent=2)

    # 2. earnings.json (包含正常数据、脏数据、旧季度)
    earnings = [
        # 正常 Q2 2026 数据
        {"earnings_id": "e001", "ticker": "TECH", "quarter": "Q2 2026", "report_date": "2026-07-15",
         "eps_actual": 2.45, "eps_estimate": 2.12, "eps_beat_pct": 15.2},
        {"earnings_id": "e002", "ticker": "NXTC", "quarter": "Q2 2026", "report_date": "2026-07-18",
         "eps_actual": 1.87, "eps_estimate": 1.72, "eps_beat_pct": 8.7},
        {"earnings_id": "e003", "ticker": "MFST", "quarter": "Q2 2026", "report_date": "2026-07-20",
         "eps_actual": 3.15, "eps_estimate": 3.00, "eps_beat_pct": 5.0},
        # 脏数据：缺少 eps_beat_pct
        {"earnings_id": "e004", "ticker": "HLTH", "quarter": "Q2 2026", "report_date": "2026-07-22",
         "eps_actual": 1.50, "eps_estimate": 1.45},
        # 旧季度数据 (干扰)
        {"earnings_id": "e005", "ticker": "TECH", "quarter": "Q1 2026", "report_date": "2026-04-15",
         "eps_actual": 2.10, "eps_estimate": 1.95, "eps_beat_pct": 7.7},
        {"earnings_id": "e006", "ticker": "NXTC", "quarter": "Q1 2026", "report_date": "2026-04-10",
         "eps_actual": 1.60, "eps_estimate": 1.55, "eps_beat_pct": 3.2},
    ]
    with open('data/earnings.json', 'w') as f:
        json.dump({"earnings": earnings}, f, indent=2)

    # 3. analysts.json
    analysts = [
        {"analyst_id": "a001", "name": "Sarah Chen", "firm": "InvestWise Research",
         "coverage": ["TECH", "NXTC"], "rating": "Senior"},
        {"analyst_id": "a002", "name": "Mike Johnson", "firm": "Capital Markets",
         "coverage": ["MFST", "HLTH"], "rating": "Analyst"},
        {"analyst_id": "a003", "name": "Tom Davis", "firm": "Global Equities",
         "coverage": ["CONS", "ENER"], "rating": "Associate"},
    ]
    with open('data/analysts.json', 'w') as f:
        json.dump({"analysts": analysts}, f, indent=2)

    # 4. 干扰文件：旧版本 earnings_old.json (格式相似, 但数据更早)
    old_earnings = [
        {"earnings_id": "e_old1", "ticker": "TECH", "quarter": "Q3 2025", "report_date": "2025-10-20",
         "eps_actual": 1.98, "eps_estimate": 1.90, "eps_beat_pct": 4.2},
    ]
    with open('data/earnings_old.json', 'w') as f:
        json.dump({"earnings": old_earnings}, f, indent=2)

    # 5. 干扰文件：一个非 JSON 的文本文件
    with open('data/notes.txt', 'w') as f:
        f.write("No critical info here.\n")

    print("Environment built successfully.")

if __name__ == '__main__':
    build_env()
