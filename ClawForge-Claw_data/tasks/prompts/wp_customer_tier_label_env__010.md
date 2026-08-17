嗨，小张（或者当前负责的同事），

市场部这边马上要做一个客户分级推送，我需要你帮忙把每个客户的等级标签更新一下。数据都在工作区的 `data/` 下面：

- 客户基本信息在 `data/customers/customers.json`，每个客户有一个 `customer_id` 和空的 `labels` 字段。
- 最新一季度的消费数据在 `data/logs/consumption_logs.json`，记录了每个客户的 `quarter_spend_usd`。
- 同一季度的活跃度数据在 `data/logs/activity_logs.json`，包含风险等级 `risk_level`、最近活跃天数 `last_active_days` 和用量趋势 `usage_trend`。

分级规则很简单（公司内部一直这么用）：
- **黄金客户（gold）**：季度消费 ≥ 50,000 美元，风险等级为 low，最近 30 天内活跃，且用量趋势为 up。
- **白银客户（silver）**：季度消费 ≥ 20,000 美元，风险等级为 low，最近 60 天内活跃，且用量趋势不是 down（up 或 stable 都行）。
- **青铜客户（bronze）**：不满足以上两个条件的，统统归为青铜。

每个客户只属于一个等级，你把计算出的等级标签（比如 "gold"、"silver"、"bronze"）写入该客户的 `labels` 数组中。注意：如果某个客户同时在两个文件中都有记录，就按上述规则算；如果某个客户只有消费数据没有活跃度，或者反过来，那这条数据就跳过，不要处理。

处理好之后，把更新后的客户列表（只需包含你实际更新了标签的客户，每个客户一个对象，包括 `customer_id` 和更新后的 `labels` 数组）保存成一个 JSON 文件，放到 `ops/customer_tier_update.json`。里面不需要额外字段，顺序无所谓。

公司急着用，尽快搞定，谢啦！

—— 市场部主管 老李
