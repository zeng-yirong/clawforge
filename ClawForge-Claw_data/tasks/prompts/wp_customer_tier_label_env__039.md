Hi, 我是客户成功部的 Alice。

我们刚调整了客户分层策略，不再沿用旧的手动标签。我这边有最新的活动日志和消费日志放在 `raw_logs/` 下，客户清单在 `data/customers/customers.json`。

新规则是这样的：
- 季度消费 >= 5000 且最近活跃天数 <= 30 的客户 → 标为 `gold`
- 季度消费 >= 2000 且最近活跃天数 <= 60 的客户 → 标为 `silver`
- 其他客户 → 标为 `bronze`

请帮我把所有客户的新标签算出来，结果写到 `ops/label_updates.json` 里。每条记录包含 `customer_id` 和 `new_tier` 字段。搞完后我直接拿这个文件去更新系统。

多谢！
