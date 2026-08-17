import os
import csv
import random
from datetime import datetime, timedelta

def build_env():
    # Clean data functions
    def write_csv(filename, rows):
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(rows)

    # 1. products.csv (product catalog)
    products = [
        ['product_id', 'product_name', 'category', 'subcategory'],
        ['P001', 'Widget Alpha', 'Widgets', 'Basic'],
        ['P002', 'Widget Beta', 'Widgets', 'Pro'],
        ['P003', 'Gizmo X', 'Gizmos', 'Standard'],
        ['P004', 'Gizmo Y', 'Gizmos', 'Deluxe'],
        ['P005', 'Thingamajig', 'Thingamajigs', 'Classic'],
    ]
    write_csv('products.csv', products)

    # 2. city_region.csv
    city_region = [
        ['city', 'region'],
        ['New York', 'East'],
        ['Los Angeles', 'West'],
        ['Chicago', 'Midwest'],
        ['Houston', 'South'],
        ['Phoenix', 'West'],
        ['Philadelphia', 'East'],
        ['San Antonio', 'South'],
        ['San Diego', 'West'],
        ['Dallas', 'South'],
        ['San Jose', 'West'],
    ]
    write_csv('city_region.csv', city_region)

    # 3. sales_raw.csv – with duplicates, missing values, and a tricky case
    base_date = datetime(2024, 1, 1)
    rows = [
        ['transaction_id','date','product_id','product_name','category','subcategory','region','city','customer_id','customer_name','sales_amount','quantity','discount','payment_method','salesperson_id','salesperson_name','channel'],
        # 完全重复的行（第1行和第2行完全一样）
        ['T001', '2024-01-15', 'P001', 'Widget Alpha', 'Widgets', 'Basic', 'East', 'New York', 'C001', 'John Doe', '120.50', '2', '10', 'Credit', 'SP01', 'Alice', 'Online'],
        ['T001', '2024-01-15', 'P001', 'Widget Alpha', 'Widgets', 'Basic', 'East', 'New York', 'C001', 'John Doe', '120.50', '2', '10', 'Credit', 'SP01', 'Alice', 'Online'],
        # 相同 transaction_id 但日期不同（保留最新）
        ['T002', '2024-02-10', 'P002', 'Widget Beta', 'Widgets', 'Pro', 'West', 'Los Angeles', 'C002', 'Jane Smith', '230.00', '1', '0', 'Debit', 'SP02', 'Bob', 'Store'],
        ['T002', '2024-02-12', 'P002', 'Widget Beta', 'Widgets', 'Pro', 'West', 'Los Angeles', 'C002', 'Jane Smith', '235.00', '1', '5', 'Debit', 'SP02', 'Bob', 'Store'],
        # 缺失 product_name（需从 products.csv 补全 P003 -> Gizmo X）
        ['T003', '2024-03-05', 'P003', '', 'Gizmos', 'Standard', 'South', 'Houston', 'C003', 'Carlos Brown', '88.75', '3', '15', 'Cash', 'SP03', 'Carol', 'Online'],
        # 缺失 region（需从 city_region.csv 补全 Chicago -> Midwest）
        ['T004', '2024-04-20', 'P004', 'Gizmo Y', 'Gizmos', 'Deluxe', '', 'Chicago', 'C004', 'Diana Lee', '450.00', '1', '20', 'Credit', 'SP04', 'Dave', 'Store'],
        # 完全正常的一行
        ['T005', '2024-05-01', 'P005', 'Thingamajig', 'Thingamajigs', 'Classic', 'West', 'San Diego', 'C005', 'Eve Kim', '320.00', '2', '10', 'Debit', 'SP05', 'Eva', 'Online'],
        # 另一组重复：完全相同行
        ['T006', '2024-06-15', 'P001', 'Widget Alpha', 'Widgets', 'Basic', 'East', 'Philadelphia', 'C006', 'Frank Moore', '140.00', '1', '0', 'Credit', 'SP01', 'Alice', 'Store'],
        ['T006', '2024-06-15', 'P001', 'Widget Alpha', 'Widgets', 'Basic', 'East', 'Philadelphia', 'C006', 'Frank Moore', '140.00', '1', '0', 'Credit', 'SP01', 'Alice', 'Store'],
        # 缺失 product_name 且 city 不在 city_region.csv 中？为了唯一答案，我们不制造完全无法填充的。所有缺失都能填充。
        # 改为缺失 product_name（P002 在表中）和 region（Phoenix 对应 West）
        ['T007', '2024-07-10', 'P002', '', 'Widgets', 'Pro', '', 'Phoenix', 'C007', 'Grace Park', '275.50', '2', '10', 'Cash', 'SP02', 'Bob', 'Online'],
    ]
    # 故意追加一个诱惑行：相同的 transaction_id 但日期比 T002 更新，但只保留一个，这里确保 T002 最新是 2024-02-12
    # 已存在 T002 两条，最后数据应只有一条 T002（日期最新 2024-02-12）
    # 追加一个 T008 正常
    rows.append(['T008', '2024-08-25', 'P003', 'Gizmo X', 'Gizmos', 'Standard', 'South', 'San Antonio', 'C008', 'Henry Zhao', '190.00', '3', '5', 'Debit', 'SP03', 'Carol', 'Store'])
    write_csv('sales_raw.csv', rows)

    # 4. 干扰项：备份目录，无关文件
    os.makedirs('backup', exist_ok=True)
    write_csv('backup/sales_raw_old.csv', [
        ['transaction_id','date','product_id','product_name','category','subcategory','region','city','customer_id','customer_name','sales_amount','quantity','discount','payment_method','salesperson_id','salesperson_name','channel'],
        ['T001', '2023-12-01', 'P001', 'Widget Alpha', 'Widgets', 'Basic', 'East', 'New York', 'C001', 'John Doe', '110.00', '1', '5', 'Credit', 'SP01', 'Alice', 'Online'],
    ])

    # 无关的日志文件
    with open('logs/processing.log', 'w') as f:
        f.write("2024-01-01 12:00:00 INFO Job started\n2024-01-01 12:00:05 WARN Duplicate detected\n")

    # 无关的 notes
    with open('notes.txt', 'w') as f:
        f.write("Remember to update product catalog regularly.\n")

if __name__ == '__main__':
    build_env()
