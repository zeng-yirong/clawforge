import os
import csv

def build_env():
    # 确保工作目录正确（cwd 已设为 ）
    os.makedirs("ledgers", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("cache", exist_ok=True)
    
    # 客户账本
    with open("ledgers/customer_ledger.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["period", "metric_code", "metric_value"])
        writer.writerow(["2024-Q4", "revenue", "300"])
        writer.writerow(["2025-Q1", "revenue", "100"])
        writer.writerow(["2025-Q1 ", "cost", "50"])   # 注意: period 尾部空格
        writer.writerow(["2024-Q4", "cost", "150"])
    
    # 产品账本
    with open("ledgers/product_ledger.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["period", "metric_code", "metric_value"])
        writer.writerow(["2025-Q1", "units", "30"])
        writer.writerow(["2024-Q4", "units", "40"])
        writer.writerow(["2025-Q1", "defective", "5"])
    
    # 运营账本（含干扰行）
    with open("ledgers/ops_ledger.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["period", "metric_code", "metric_value"])
        writer.writerow(["2025-Q1", "overhead", "20"])
        writer.writerow(["2024-Q4", "overhead", "25"])
        writer.writerow(["2025-Q1", "waste", "3"])
        writer.writerow(["", "discount", "10"])          # 空时期
        writer.writerow(["2025-Q1", "bonus", "N/A"])     # 非数值
    
    # 干扰文件（不重要，但增加环境复杂度）
    with open("accounts.json", "w") as f:
        f.write('{"dummy": true}')
    with open("contacts.json", "w") as f:
        f.write('{"dummy": true}')

if __name__ == "__main__":
    build_env()
