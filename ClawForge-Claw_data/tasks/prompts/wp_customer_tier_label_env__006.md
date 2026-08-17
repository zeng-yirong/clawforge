嘿，小张，我是运营老李。这季度快结束了，系统里的客户等级标签还是一团糟！我刚把原始数据丢进了工作区，你帮我理一理。

你看一下 `data/customers/customers.json`，里面是所有客户的档案。然后去 `data/logs/` 目录下，有两条日志：`activity_logs.json` 记录最近活跃天数，`consumption_logs.json` 记录季度消费额。我这边业务规则很简单：

- 季度消费超过 5 万块，并且超过 30 天没在系统里冒泡的客户，那就是“高价值流失风险”——标成 `Churn Risk`。
- 季度消费不到 1 万块的，属于“低消费群体”——标成 `Low Spender`。
- 剩下的客户里，如果消费在 1 万到 5 万之间，并且使用趋势是向上的（`usage_trend` 为 `up`），说明有增长潜力，标 `Growth`；趋势向下的话，标 `Steady`。

注意！有几个测试客户（`customer_id` 以 `test_` 开头的）是之前做实验用的，别混进去。只处理正式客户。

你整理好后，给我生成一个文件放在 `ops/customer_tier_update.json`，里面每个正式客户的 `customer_id` 和对应的新标签。我等着用这个文件批量导入系统，千万别搞错格式——给我一个 JSON 数组就行，每个元素包含 `customer_id` 和 `label` 两个字段。

辛苦了，今晚之前搞定！
