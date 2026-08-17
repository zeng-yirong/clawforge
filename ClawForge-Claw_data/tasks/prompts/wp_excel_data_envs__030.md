嗨！我是销售部的老李，这季度数据真是让我头疼死。你打开工作区看看，`data/raw_sales.csv` 里面有一堆混乱的订单记录——重复的单子、缺失的产品名称和客户姓名，甚至还有负的金额和数量！我这边没法直接分析。

我们需要一份干净的数据，并按照产品类别汇总出实际收入。原始字段说明：`sales_amount` 是商品标价（单价），`quantity` 是件数，`discount` 是折扣百分比（比如10就表示打9折）。请你帮我做下面这几件事：

- 剔除掉所有异常的记录（金额或数量为负数的直接扔掉）。
- 完全重复的行（整行一模一样）只保留一条。
- 如果产品名称或客户姓名缺失，到 `data/products.csv` 和 `data/customers.csv` 里根据 `product_id` 或 `customer_id` 查一下补全；如果查不到，那条记录也丢掉。
- 然后按 `category`（产品类别）分组，算出每个类别下的：
  - 总实际收入（单价×数量×(1-折扣/100) 再求和）
  - 平均每单实际收入（总实际收入 / 订单数）
  - 订单数量

最后把结果输出到 `report/summary.json`，格式类似这样：
{
  "categories": [
    { "category": "Electronics", "total_sales": 1005.0, "average_order": 251.25, "order_count": 4 },
    { "category": "Clothing", "total_sales": 274.0, "average_order": 91.33, "order_count": 3 }
  ]
}
数字精确到两位小数就行。麻烦了，我明天汇报要用！
